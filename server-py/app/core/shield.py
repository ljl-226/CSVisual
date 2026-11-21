"""安全防护中间件：响应头 / CORS 白名单 / 限流 / 登录失败锁定。

一个 ASGI 中间件做完整套，是为了让「拒绝」发生在最外层 ——
限流与来源校验若排在 body 解析之后，攻击者仍能用超大 body 逼服务端先把请求读完再拒绝，
白白吃掉内存和 CPU。

执行顺序（Starlette 后添加的在外层）：
    SecurityMiddleware（最外层，本文件）
      └ JsonBodyMiddleware
          └ 路由

与 Node 版 server/src/middleware/security.js 是同一套规则的两个实现，
改任一边都要同步另一边，否则前端切后端时安全强度会莫名变化。
"""

import time
from collections import defaultdict, deque

from app.core import config as C

# ---- 安全响应头 ----
# frame-ancestors + X-Frame-Options 双写：前者现代浏览器认，后者老浏览器认，
# 少了任何一个都可能让页面被 iframe 套进去做点击劫持。
CSP = "default-src 'self'; img-src 'self' data: https:; script-src 'self' 'unsafe-inline' 'unsafe-eval'; " \
      "style-src 'self' 'unsafe-inline'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"

BASE_HEADERS = [
    (b'x-frame-options', b'DENY'),
    (b'x-content-type-options', b'nosniff'),
    (b'referrer-policy', b'strict-origin-when-cross-origin'),
    (b'permissions-policy', b'geolocation=(), microphone=(), camera=()'),
    (b'cross-origin-opener-policy', b'same-origin'),
    (b'content-security-policy', CSP.encode()),
    (b'x-permitted-cross-domain-policies', b'none'),
]

# HTTPS 下才发 HSTS：http 环境发它会让浏览器在有效期内强制跳 https，本地开发直接连不上
HSTS = (b'strict-transport-security', b'max-age=31536000; includeSubDomains')

# 允许跨域时暴露给前端 JS 的响应头（默认只有简单响应头可读）
EXPOSE_HEADERS = 'X-Request-Id'

DEV_ORIGIN_SUFFIX = ('http://localhost', 'http://127.0.0.1', 'http://[::1]')


def client_ip(scope) -> str:
    """取客户端 IP。

    只有显式配置 TRUST_PROXY=1 才认 X-Forwarded-For ——
    否则任何人伪造一个 XFF 头就能绕过所有基于 IP 的限流和锁定。
    """
    headers = dict(scope.get('headers') or [])
    if C.env('TRUST_PROXY', '0') in ('1', 'true', 'yes'):
        forwarded = headers.get(b'x-forwarded-for', b'').decode('latin-1')
        if forwarded:
            return forwarded.split(',')[0].strip()
    client = scope.get('client')
    return client[0] if client else 'unknown'


def ip_of(request) -> str:
    """路由里取客户端 IP（路由拿到的是 Request，中间件拿到的是 scope）。"""
    return client_ip(getattr(request, 'scope', {}) or {})


def _origin_allowed(origin: str) -> bool:
    """白名单判断。

    白名单为空时：生产态只允许同源（不带 Origin 的请求按服务端调用放行），
    开发态放通本机常见端口，免得每次换端口都要改配置。
    """
    if not origin:
        return True
    if C.ALLOWED_ORIGINS:
        return origin in C.ALLOWED_ORIGINS
    if C.IS_PROD:
        return False
    return origin.startswith(DEV_ORIGIN_SUFFIX)


class _Bucket:
    """滑动窗口计数。"""

    def __init__(self):
        self.hits = defaultdict(deque)

    def allow(self, key: str, limit: int, window: int) -> bool:
        if limit <= 0:
            return True
        now = time.time()
        q = self.hits[key]
        while q and now - q[0] > window:
            q.popleft()
        if len(q) >= limit:
            return False
        q.append(now)
        self._gc(now)
        return True

    def _gc(self, now):
        """顺手清掉空桶：长期运行下 key 会随 IP 数量无限增长。"""
        if len(self.hits) > 5000:
            for k in [k for k, v in self.hits.items() if not v]:
                del self.hits[k]


bucket = _Bucket()

# 登录失败计数：key -> [失败次数, 锁定截止时间戳]
# key 用「账号 + IP」而不是只按账号 —— 只按账号的话，任何人都能把别人的账号试锁死；
# 只按 IP 的话，同一 NAT 出口下一个人输错会连累所有人。
_login_fail: dict = {}


def login_fail_key(username: str, ip: str) -> str:
    return f'{ip}|{str(username).lower()}'


def login_locked(username: str, ip: str):
    """返回剩余锁定秒数（0 = 未锁定）。"""
    rec = _login_fail.get(login_fail_key(username, ip))
    if not rec:
        return 0
    count, until = rec
    left = until - time.time()
    return int(left) if left > 0 else 0


def note_login_fail(username: str, ip: str) -> int:
    """记一次失败，返回「达到上限后需要锁定的分钟数」（未达上限返回 0）。

    达到 LOGIN_MAX_FAIL 后锁定并清零计数，锁定期满后再从 0 开始累计。
    """
    key = login_fail_key(username, ip)
    count, until = _login_fail.get(key, (0, 0.0))
    now = time.time()
    if now < until:
        return 0
    count += 1
    if count >= C.LOGIN_MAX_FAIL:
        _login_fail[key] = (0, now + C.LOGIN_LOCK_MINUTES * 60)
        return C.LOGIN_LOCK_MINUTES
    _login_fail[key] = (count, 0.0)
    return 0


def clear_login_fail(username: str, ip: str):
    _login_fail.pop(login_fail_key(username, ip), None)


def _is_heavy(path: str) -> bool:
    """重资源接口：在线编译运行与大模型调用，配额单独收紧。"""
    return path.startswith('/api/code/run') or path.startswith('/api/agent/') \
        or path.endswith('/assistant')


def _is_auth(path: str) -> bool:
    return path.startswith('/api/auth/login') or path.startswith('/api/auth/register') \
        or path.startswith('/api/auth/forgot')


class SecurityMiddleware:
    """纯 ASGI 中间件：来源校验 → 限流 → 注入安全响应头。"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get('type') != 'http':
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get('headers') or [])
        origin = headers.get(b'origin', b'').decode('latin-1')
        path = scope.get('path') or '/'
        ip = client_ip(scope)

        # ---- 1. 来源校验 ----
        # 校验 Origin 而不是 Referer：Referer 可被策略省略、也更容易被中间设备改写，
        # 而浏览器跨域请求一定带 Origin。
        if not _origin_allowed(origin):
            await self._reject(send, 403, '请求来源不被允许', cors=False)
            return

        # ---- 2. 限流 ----
        if _is_auth(path):
            if not bucket.allow(f'auth:{ip}', C.RATE_AUTH_MAX, C.RATE_AUTH_WINDOW):
                await self._reject(send, 429, '操作过于频繁，请稍后再试', origin)
                return
        elif _is_heavy(path):
            if not bucket.allow(f'heavy:{ip}', C.RATE_HEAVY_MAX, C.RATE_WINDOW):
                await self._reject(send, 429, '请求过于频繁，请稍后再试', origin)
                return
        elif not bucket.allow(f'g:{ip}', C.RATE_MAX, C.RATE_WINDOW):
            await self._reject(send, 429, '请求过于频繁，请稍后再试', origin)
            return

        # ---- 3. 注入响应头 ----
        extra = list(BASE_HEADERS)
        if C.IS_PROD or C.COOKIE_SECURE:
            extra.append(HSTS)
        if origin and _origin_allowed(origin):
            extra += [
                (b'access-control-allow-origin', origin.encode()),
                (b'access-control-allow-credentials', b'true'),
                (b'vary', b'Origin'),
                (b'access-control-expose-headers', EXPOSE_HEADERS.encode()),
            ]

        async def send_with_headers(message):
            if message.get('type') == 'http.response.start':
                heads = message.setdefault('headers', [])
                heads.extend(extra)
            await send(message)

        # 预检请求直接在这里结束，不进路由（路由里没有 OPTIONS 处理器）
        if scope.get('method') == 'OPTIONS':
            await send({
                'type': 'http.response.start', 'status': 204,
                'headers': [
                    (b'access-control-allow-methods', b'GET, POST, PUT, DELETE, OPTIONS'),
                    (b'access-control-allow-headers', b'Content-Type, Authorization, X-Timestamp'),
                    (b'access-control-max-age', b'86400'),
                    (b'content-length', b'0'),
                ] + extra,
            })
            await send({'type': 'http.response.body', 'body': b''})
            return

        await self.app(scope, receive, send_with_headers)

    @staticmethod
    async def _reject(send, status: int, message: str, cors):
        body = ('{"code":%d,"message":"%s"}' % (status, message)).encode()
        heads = [(b'content-type', b'application/json; charset=utf-8'),
                 (b'content-length', str(len(body)).encode())] + BASE_HEADERS
        if cors:
            heads.append((b'access-control-allow-origin', cors.encode()))
        await send({'type': 'http.response.start', 'status': status, 'headers': heads})
        await send({'type': 'http.response.body', 'body': body})
