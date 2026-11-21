"""统一响应格式。

与 Node/Express 版本保持逐字一致的返回结构：
    { code: 200, data: ... }       业务成功
    { code: 400, message: '...' }  业务失败（HTTP 状态码仍是 200）
    { code: 401, message: '...' }  鉴权失败（HTTP 状态码也是 401）
"""


def ok(data=None, message=None):
    """成功响应。

    注意 data 即使是 None 也要按需出现：部分接口（如 /course/knowledge/:id）
    原本就返回 data.progress = null，缺失字段会让前端取值行为不一致。
    """
    body = {'code': 200}
    if message is not None:
        body['message'] = message
    if data is not None:
        body['data'] = data
    return body


def fail(code, message):
    """业务失败响应（HTTP 状态码仍为 200，靠 body.code 表达错误）。"""
    return {'code': code, 'message': message}
