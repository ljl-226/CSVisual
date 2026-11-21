"""请求体解析中间件。

目的：让同步 def 的路由也能拿到解析好的 JSON body。
FastAPI 只有在 async def 里才能 `await request.json()`，而本项目的 DB 调用是同步阻塞的，
路由统一写成同步 def（跑在线程池里，不会卡住事件循环），因此 body 在中间件里一次性读完并缓存。
"""

import json


class JsonBodyMiddleware:
    """读取并缓存请求 body，避免下游重复消费 receive。"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get('type') != 'http':
            await self.app(scope, receive, send)
            return

        chunks = []
        more = True
        while more:
            message = await receive()
            if message.get('type') != 'http.request':
                break
            chunks.append(message.get('body') or b'')
            more = message.get('more_body', False)
        raw = b''.join(chunks)

        parsed = None
        text = raw.decode('utf-8', 'ignore').strip()
        if text[:1] in ('{', '['):
            try:
                parsed = json.loads(text)
            except ValueError:
                parsed = None

        state = dict(scope.get('state') or {})
        state['json_body'] = parsed if isinstance(parsed, dict) else {}
        state['raw_body'] = raw
        scope['state'] = state

        served = False

        async def cached_receive():
            """首次调用返回缓存的 body，之后交回真实 receive。

            不能无条件返回 http.request：starlette 的 StreamingResponse 会起一个
            listen_for_disconnect 协程，反复 await receive() 直到收到 http.disconnect
            才退出，而它与 stream_response 处在同一任务组内。若这里永远返回 http.request，
            该协程就变成一个不挂起的死循环，独占事件循环，stream_response 再也得不到
            调度（任务组的取消也就无从发生）—— 结果不是一个 SSE 请求卡住，而是
            **整个服务对所有请求失去响应**，且进程仍在、端口仍在 LISTENING，
            仅看端口完全看不出来。SSE 接口（/agent 与 /algorithm 的流式端点）必现。
            """
            nonlocal served
            if not served:
                served = True
                return {'type': 'http.request', 'body': raw, 'more_body': False}
            return await receive()

        await self.app(scope, cached_receive, send)


def body_of(request) -> dict:
    """取当前请求的 JSON body（非 dict 或解析失败一律返回空 dict）。"""
    return getattr(request.state, 'json_body', None) or {}
