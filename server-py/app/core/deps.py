"""路由依赖：登录态 / 管理员权限 / 可选登录态 / 防重放时间戳。"""

import time
from typing import Optional

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import COOKIE_NAME, TS_TOLERANCE
from app.core.errors import ApiError, Expired, Forbidden, Unauthorized
from app.core.security import verify_token
import jwt as pyjwt

bearer = HTTPBearer(auto_error=False)


def _token_from_request(request: Request):
    """取令牌：Authorization 头优先，其次 HttpOnly Cookie。

    前端正常走 Cookie（浏览器自动带，脚本读不到，XSS 偷不走）；
    Authorization 保留给 curl 调试和第三方调用，两条通道用同一个密钥签发，
    校验逻辑完全一致。
    """
    header = request.headers.get('authorization') or ''
    if header.startswith('Bearer '):
        return header[7:]
    return request.cookies.get(COOKIE_NAME) or ''


def _payload_from_request(request: Request):
    token = _token_from_request(request)
    if not token:
        return None, False
    try:
        return verify_token(token), True
    except pyjwt.ExpiredSignatureError:
        return None, True  # token 存在但已过期 → 需要区别于"没带 token"


def current_user(request: Request) -> dict:
    payload, present = _payload_from_request(request)
    if payload is None:
        if present:
            raise Expired()
        raise Unauthorized()
    return payload


def admin_user(user: dict = Depends(current_user)) -> dict:
    if user.get('role') != 'admin':
        raise Forbidden()
    return user


def optional_user(request: Request) -> Optional[dict]:
    """不强制登录：token 有效则返回用户，否则返回 None（用于公开接口带个性化字段）。"""
    payload, _ = _payload_from_request(request)
    return payload


def _unused(_credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer)):
    """让 OpenAPI 文档出现鉴权按钮；实际校验走 current_user（兼容自定义 header 形态）。"""
    return None


def check_timestamp(request: Request, tolerance: int = None):
    """防重放：校验 X-Timestamp（毫秒）。

    抓包重放的前提是请求能被原样再发一次。带上时间戳后，攻击者窗口被压到
    tolerance 秒内，且无法靠修改时间来延长（改了就超出容差）。
    它不能替代 HTTPS（传输中仍可能被中间人读取并立即重放），
    所以只在改密码 / 找回密码这类「改了凭据就接管账号」的接口上强制。

    缺失或不合法一律拒绝 —— 只对前端开放这些接口，前端 axios 拦截器统一加头。
    """
    # HTTP 状态码仍是 200、错误由 body.code 表达 —— 与项目其它业务失败响应保持一致
    # （只有鉴权类的 401/403 与限流的 429 才用真实 HTTP 状态码）。
    raw = request.headers.get('x-timestamp') or ''
    try:
        ts = int(raw)
    except (TypeError, ValueError):
        raise ApiError(200, 400, '请求缺少有效的时间戳，请刷新页面重试')
    limit = TS_TOLERANCE if tolerance is None else tolerance
    if abs(time.time() * 1000 - ts) > limit * 1000:
        raise ApiError(200, 400, '请求已过期，请刷新页面重试')
    return ts
