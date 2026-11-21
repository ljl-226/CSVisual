"""错误体系。

Express 版用 res.status(401).json({code,message}) 与全局 error middleware 表达错误，
FastAPI 里改为抛异常 + 全局 handler，保证 HTTP 状态码与 body 结构和旧版完全一致。
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class ApiError(Exception):
    """带 HTTP 状态码的业务异常。"""

    def __init__(self, status_code: int, code: int = None, message: str = '', payload: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.code = code if code is not None else status_code
        self.message = message
        self.payload = payload or {}


class Unauthorized(ApiError):
    def __init__(self, message='未登录'):
        super().__init__(401, 401, message)


class Expired(ApiError):
    def __init__(self, message='登录已过期，请重新登录'):
        super().__init__(401, 401, message)


class Forbidden(ApiError):
    def __init__(self, message='无管理员权限'):
        super().__init__(403, 403, message)


def register_exception_handlers(app) -> None:
    @app.exception_handler(ApiError)
    async def _api_error(request: Request, exc: ApiError):
        body = {'code': exc.code, 'message': exc.message}
        body.update(exc.payload)
        return JSONResponse(status_code=exc.status_code, content=body)

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(request: Request, exc: StarletteHTTPException):
        # 保持 body 结构统一：{code, message} 而不是 FastAPI 默认的 {detail}
        if isinstance(exc.detail, dict):
            return JSONResponse(status_code=exc.status_code, content=exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={'code': exc.status_code, 'message': str(exc.detail)},
        )

    @app.exception_handler(Exception)
    async def _server_error(request: Request, exc: Exception):
        """兜底：任何异常都不让进程退出。

        这里**不能**把 str(exc) 回给前端。一次未捕获异常的文本里通常带着
        数据库表名字段、SQL 语句、本地文件路径甚至连接串 —— 等于把内部结构
        免费交给攻击者做下一步注入的地图。真实原因写服务端日志，
        响应里只给一个 requestId，用户报障时凭它在日志里定位。
        """
        import traceback
        import uuid

        rid = uuid.uuid4().hex[:12]
        print(f'[ERROR] requestId={rid} path={request.url.path} '
              f'{type(exc).__name__}: {exc}')
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={'code': 500, 'message': '服务器内部错误', 'requestId': rid},
        )
