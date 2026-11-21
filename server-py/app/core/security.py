"""鉴权工具：JWT 签发/校验 + bcrypt 密码散列 + 临时凭据生成。"""

import re
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import COOKIE_NAME, COOKIE_SECURE, JWT_EXPIRES, JWT_SECRET


def _parse_expires(text: str) -> timedelta:
    """把 '7d' / '12h' / '30m' 这类写法转成 timedelta（PyJWT 只认秒数）。"""
    m = re.match(r'^(\d+)\s*([smhd])$', str(text).strip().lower())
    if not m:
        return timedelta(days=7)
    n = int(m.group(1))
    return {'s': timedelta(seconds=n), 'm': timedelta(minutes=n),
            'h': timedelta(hours=n), 'd': timedelta(days=n)}[m.group(2)]


def token_max_age() -> int:
    """Cookie 有效期，跟 JWT 的 exp 对齐（秒）。"""
    return int(_parse_expires(JWT_EXPIRES).total_seconds())


def cookie_kwargs() -> dict:
    """登录 Cookie 的参数。

    HttpOnly：JS 读不到，XSS 拿不到令牌（这是把令牌从 localStorage 挪出来的全部意义）
    SameSite=Lax：跨站表单 / iframe 不会自动带上，挡住大部分 CSRF
    Secure：仅 HTTPS 传输（生产强制，本地 http 下由 COOKIE_SECURE=0 关闭，否则浏览器根本不存）
    Path=/：全站接口都能带上
    """
    return {
        'key': COOKIE_NAME,
        'httponly': True,
        'samesite': 'lax',
        'secure': COOKIE_SECURE,
        'path': '/',
        'max_age': token_max_age(),
    }


def sign_token(user) -> str:
    """签发 token。payload 与 Node 版一致：{id, username, role}"""
    payload = {
        'id': user['id'],
        'username': user['username'],
        'role': user['role'],
        'exp': datetime.now(timezone.utc) + _parse_expires(JWT_EXPIRES),
        'iat': datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')


def verify_token(token: str):
    """校验 token，失败返回 None（调用方统一转成 401）。"""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise
    except jwt.PyJWTError:
        return None


def hash_password(plain: str) -> str:
    # bcryptjs 与 Py-bcrypt 生成的 $2a$/$2b$ 前缀互通，库里已有密码无需重置
    return bcrypt.hashpw(str(plain).encode('utf-8'), bcrypt.gensalt(10)).decode('utf-8')


def hash_answer(plain: str) -> str:
    """密保答案 / 邮箱验证码的散列。

    与 hash_password 走同一套 bcrypt，但刻意分开命名：密码是凭据本身，
    密保答案是「证明我是我」的第二因子，将来若换了散列策略不该彼此牵连。
    验证码存哈希是为了让库被拖走时也拿不到可用的验证码。
    """
    return hash_password(plain)


def check_answer(plain: str, hashed: str) -> bool:
    return check_password(plain, hashed)


def check_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(str(plain or '').encode('utf-8'), str(hashed or '').encode('utf-8'))
    except Exception:
        return False


# --------------------------------------------------------------------------
# 临时密码 / 申请单号
#
# 字符集里没有 i l o 0 1：临时密码要靠人手抄给另一个人、单号要靠用户自己
# 敲进输入框，抄错一位就得重来一遍流程 —— 把长得像的字符剔除掉，
# 「大写 I 还是小写 l」这类问题根本不会发生。
# --------------------------------------------------------------------------
TEMP_PWD_ALPHABET = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
TICKET_ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'


def gen_temp_password(length: int = 8) -> str:
    """随机临时密码。

    随机而不是统一重置成 123456：临时密码依赖管理员转告，在用户改掉它之前，
    它就是这个账号的口令 —— 猜得到的口令等于没换。"""
    return ''.join(secrets.choice(TEMP_PWD_ALPHABET) for _ in range(length))


def gen_ticket() -> str:
    """"TP-XXXXXX" 形式的申请单号。用户拿它回来取临时密码，
    所以它是临时的取件凭证 —— 必须短到能手抄，也必须随机到猜不出来。"""
    return 'TP-' + ''.join(secrets.choice(TICKET_ALPHABET) for _ in range(6))
