"""流式（SSE）接口的两个回归守卫。

这里锁的是两个都曾真实发生、且**功能测试全绿也测不出来**的 bug：

1. **一次 SSE 请求把整个服务拖死**
   `app/core/body.py` 的 `JsonBodyMiddleware` 把 receive 换成了无条件返回
   `http.request` 的 `cached_receive`。而 starlette 的 `StreamingResponse` 会起一个
   `listen_for_disconnect` 反复 `await receive()` 直到收到 `http.disconnect` 才退出，
   它与 `stream_response` 处在同一任务组内 —— 于是变成一个**不挂起的死循环**占满事件
   循环，`stream_response` 再也得不到调度，任务组的取消也就无从发生。
   后果不是一个请求卡住，而是**整个服务对所有请求失去响应**：进程仍在、端口仍在
   LISTENING，只看端口或只看进程是否存在完全看不出来。

2. **没配大模型 Key 时流式问答静默返回空回答**
   `agent/chat/stream` 里整段大模型调用被 `if os.getenv('LLM_API_KEY')` 跳过，
   `mode` 仍停在初始的 `'llm'`、`acc` 仍是 `''`，而后面只按 `mode == 'fallback'`
   兜底 —— 于是一路走到 `done`，正文一个字都没有。前端 `AgentChat.vue` 走的正是
   这个接口，而「未配 Key 也能离线完整演示」是项目明确要保证的行为。

之所以用线程 + join(timeout) 包起来：bug 复现时请求会**永远不返回**，
不加超时保护的话整个测试套件会挂死，而不是失败。
"""

import json
import threading

import pytest


# bug 复现时请求永不返回，这个值决定「多久判定服务已被拖死」。
# 不能设太大：回归时三个用例会各卡满一次，60s 会让整套测试多花十几分钟。
# 也不能太小：配了真实 LLM 时流式问答本身可能要十几秒。
TIMEOUT = 20


def _run_in_thread(fn, timeout=TIMEOUT):
    """在守护线程里跑 fn，超时即判失败。返回 (是否完成, 结果或异常)。"""
    box = {}

    def target():
        try:
            box['value'] = fn()
        except BaseException as exc:  # noqa: BLE001 - 要原样带回主线程断言
            box['exc'] = exc

    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        return False, TimeoutError(f'操作超过 {timeout}s 未返回')
    return True, box.get('value', box.get('exc'))


def _consume_stream(client, auth, question):
    """消费一次 SSE 流，返回所有 data 行的内容。"""
    lines = []
    with client.stream(
        'POST',
        '/api/agent/chat/stream',
        json={'question': question},
        headers=auth,
    ) as resp:
        for line in resp.iter_lines():
            if line.startswith('data:'):
                lines.append(line[5:].strip())
    return lines


def test_sse_stream_returns_content_without_llm_key(client, auth, monkeypatch):
    """没配 LLM_API_KEY 时，流式问答必须走本地降级并真的吐出正文。

    这里必须自己把 LLM_API_KEY 摘掉：开发机上 server/.env 里通常配着真实 Key，
    不显式删除的话这条用例在「配了 Key」的机器上会变成另一个场景（走真实大模型，
    mode 是 llm），在「没配 Key」的机器上才是它要测的降级路径 —— 同一段代码
    在不同机器上测的不是同一件事，这类依赖外部环境的用例是不可靠的。
    """
    monkeypatch.delenv('LLM_API_KEY', raising=False)
    ok, payload = _run_in_thread(lambda: _consume_stream(client, auth, '简述 TCP 三次握手'))
    assert ok, f'流式请求未能正常结束：{payload}'
    assert not isinstance(payload, BaseException), f'流式请求抛错：{payload}'

    events = [json.loads(x) for x in payload if x]
    deltas = [e for e in events if e.get('type') == 'delta']

    assert payload, 'SSE 不应没有任何事件'
    assert deltas, '未配大模型 Key 时应走本地降级并产出正文，实际一个 delta 都没有'
    # delta 正文字段名：Python 侧与 Node 侧已统一成 content（前端 sse.js 两边都认，
    # 但契约只有一个，别再让两套后端各发一个名字）
    assert any(e.get('content') for e in deltas), 'delta 事件里的正文为空'
    # 未配 Key 时 mode 必须是 fallback，不能谎报 llm
    done = [e for e in events if e.get('type') == 'done']
    assert done and done[-1].get('mode') == 'fallback'


def test_sse_stream_does_not_deadlock_the_server(client, auth):
    """SSE 请求结束后，服务必须仍然能响应其它请求。

    这是本文件最重要的一条：它抓的是「整个后端对所有请求失去响应」。
    """
    ok, err = _run_in_thread(lambda: _consume_stream(client, auth, '栈和队列的区别'))
    assert ok, (
        '流式请求超时未返回 —— 极可能是 body.py 的 cached_receive 又无条件返回 '
        f'http.request，导致 listen_for_disconnect 死循环占满事件循环：{err}'
    )

    # 关键断言：流式请求之后，普通请求仍要能立刻应答
    def health():
        r = client.get('/api/health')
        return r.status_code, r.json()

    ok2, res = _run_in_thread(health, timeout=15)
    assert ok2, f'SSE 之后服务已失去响应（/api/health 超时）：{res}'

    status, body = res
    assert status == 200, f'/api/health 状态码异常: {status}'
    assert body.get('code') == 200 and body['data'].get('db') == 'connected', (
        f'SSE 之后服务状态异常: {body}'
    )


def test_algorithm_stream_also_keeps_server_alive(client, auth):
    """算法助手的流式接口同样不能拖死服务（同一个中间件，同一类风险）。"""
    def call():
        lines = []
        with client.stream(
            'POST',
            '/api/algorithm/assistant/stream',
            json={'question': '这段代码的时间复杂度是多少？', 'code': 'for i in range(n): pass'},
            headers=auth,
        ) as resp:
            for line in resp.iter_lines():
                if line.startswith('data:'):
                    lines.append(line[5:].strip())
        return lines

    ok, payload = _run_in_thread(call)
    assert ok, f'算法助手流式请求超时未返回：{payload}'

    ok2, res = _run_in_thread(lambda: client.get('/api/health').json(), timeout=15)
    assert ok2, f'算法助手 SSE 之后服务已失去响应：{res}'
    assert res.get('code') == 200
