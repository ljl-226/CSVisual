"""配置加载。

项目已收敛为「只有 Python 后端」，配置文件固定为 server-py/.env。
首次部署请执行：cp .env.example .env（Windows: copy .env.example .env）
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# server-py/（config.py → core → app → server-py）
BASE_DIR = Path(__file__).resolve().parents[2]


def _bootstrap() -> None:
    local = BASE_DIR / '.env'
    if local.exists():
        load_dotenv(local)
        return
    # 项目根目录下也放一份（便于部署时统一配置），优先级低于 server-py/.env
    root = BASE_DIR.parent / '.env'
    if root.exists():
        load_dotenv(root)
        return
    print('[提示] 未找到 server-py/.env，全部配置走默认值。'
          '请执行 copy .env.example .env 后填写 DB_PASSWORD 等本机配置。')


_bootstrap()


def env(key: str, default: str = '') -> str:
    v = os.getenv(key)
    return v if v is not None and v != '' else default


def int_env(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, '') or default)
    except ValueError:
        return default


PORT = int_env('PORT', 3000)

# ---- JWT ----
# 占位值是写在源码里的公开字符串，任何人拿到仓库都能自签 role:'admin' 的 token
# 接管后台。所以生产环境不允许带着它启动（与 Node 版 middleware/auth.js 同样处理）。
JWT_SECRET = env('JWT_SECRET', 'csvisual_secret_key_change_me')
JWT_EXPIRES = env('JWT_EXPIRES', '7d')

# ---- 运行环境 ----
# production 会启用两处硬约束：必须配置 JWT_SECRET、Cookie 带 Secure。
ENV = env('CSVISUAL_ENV', env('NODE_ENV', 'development')).lower()
IS_PROD = ENV == 'production'

# ---- CORS 白名单 ----
# 逗号分隔，如 'https://csvisual.example.com,https://www.example.com'。
# 留空表示「开发态默认放通本机常见端口」，生产态则只允许同源请求（不带 Origin 的请求，
# 即 curl / 服务端调用，一律放行）。
ALLOWED_ORIGINS = [s.strip() for s in env('ALLOWED_ORIGINS', '').split(',') if s.strip()]

# ---- 限流 ----
# 全局：单 IP 每分钟请求数（0 = 不限）
RATE_WINDOW = int_env('RATE_WINDOW', 60)
RATE_MAX = int_env('RATE_MAX', 600)
# 认证类接口（登录 / 注册 / 找回密码）：单 IP 每窗口次数，防暴力破解与撞库
RATE_AUTH_MAX = int_env('RATE_AUTH_MAX', 20)
RATE_AUTH_WINDOW = int_env('RATE_AUTH_WINDOW', 900)
# 重资源接口（在线运行代码 / AI 对话）：单 IP 每分钟次数
RATE_HEAVY_MAX = int_env('RATE_HEAVY_MAX', 30)
# 连续登录失败锁定
LOGIN_MAX_FAIL = int_env('LOGIN_MAX_FAIL', 5)
LOGIN_LOCK_MINUTES = int_env('LOGIN_LOCK_MINUTES', 15)

# ---- Cookie 令牌通道 ----
# 登录成功后额外下发 HttpOnly Cookie，前端脚本读不到，XSS 偷不走。
# 走 HTTPS 时自动加 Secure；反向代理后若拿不到 https，可显式设 COOKIE_SECURE=1 强制。
COOKIE_SECURE = env('COOKIE_SECURE', '1' if IS_PROD else '0') not in ('0', 'false', 'no')
COOKIE_NAME = env('COOKIE_NAME', 'cv_token')

# ---- 防重放 ----
# 敏感写接口要求 X-Timestamp（毫秒），与服务端时间偏差超过此秒数即拒绝
TS_TOLERANCE = int_env('TS_TOLERANCE', 300)

# ---- 审计日志 ----
AUDIT_LOG = env('AUDIT_LOG', '1') not in ('0', 'false', 'no')
