"""pytest 公共夹具。

测试通过 FastAPI TestClient 直接调用 ASGI 应用（进程内、不占端口），
既避免受限环境无法监听端口的问题，也让测试稳定、快速。
"""

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault('DB_NAME', os.getenv('DB_NAME') or 'cs_visual')

# 认证类限流与登录失败锁定在测试里必须放开：注册 / 登录 / 改密码这类用例一轮要调几十次，
# 20/15min 的上限一触就被打成 429，失败现象却和「账号被锁」混在一起，非常难排查。
# RATE_HEAVY_MAX（在线运行 30/min）不能用环境变量一刀切 ——
# test_code.py::test_run_rate_limit 要靠默认 30/min 才能验证限流生效，
# 所以改成按用例放宽（见下面的 _loose_heavy_rate 夹具）。
os.environ.setdefault('RATE_AUTH_MAX', '100000')
os.environ.setdefault('RATE_AUTH_WINDOW', '900')
os.environ.setdefault('LOGIN_MAX_FAIL', '100000')

import time  # noqa: E402

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope='session')
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def _loose_heavy_rate(request):
    """除限流用例外，把「在线运行」的 30/min 上限临时放宽。

    单跑 test_code.py 是绿的，全量跑却挂两条：全量一共要打几十次 /code/run，
    配额在前面的用例里就被耗光，轮到这两条时只剩 429 —— 现象看起来像「运行接口坏了」，
    实际是限流计数跨用例累积。限流本身没错，错的是测试之间共享了一份计数器。

    只对 test_run_rate_limit 保持默认：它断言的正是「第 31 次会被拒」。
    shield 每次请求都读 C.RATE_HEAVY_MAX，所以改模块属性即时生效。
    """
    if request.node.name == 'test_run_rate_limit':
        yield
        return
    from app.core import config as C
    old = C.RATE_HEAVY_MAX
    C.RATE_HEAVY_MAX = 100000
    try:
        yield
    finally:
        C.RATE_HEAVY_MAX = old


@pytest.fixture(autouse=True)
def _fresh_client(client):
    """每个用例都从「干净的未登录连接」开始，做两件事：

    1. 清 Cookie —— 令牌现在由后端下发 HttpOnly Cookie，而 TestClient 会一直攒着 Cookie：
       上一个用例登录后，下一个断言 401 的用例会带着它的 Cookie 拿到 200（管理员接口是 403），
       表现成「鉴权好像没生效」。
    2. 重盖一次 X-Timestamp —— 防重放校验要求时间戳落在 ±5 分钟内，
       用默认请求头带上当前时间即可（TestClient 不支持 httpx 的 event_hooks，
       所以不能在出口统一盖章，只能在每个用例前刷新）。"""
    client.cookies.clear()
    client.headers['X-Timestamp'] = str(int(time.time() * 1000))
    yield


def _login(client, username, password):
    r = client.post('/api/auth/login', json={'username': username, 'password': password})
    body = r.json()
    assert body.get('code') == 200, f'{username} 登录失败: {body}'
    return body['data']['token']


@pytest.fixture(scope='session')
def student_token(client):
    return _login(client, 'student', '123456')


@pytest.fixture(scope='session')
def admin_token(client):
    return _login(client, 'admin', 'admin123')


@pytest.fixture
def auth(student_token):
    return {'Authorization': 'Bearer ' + student_token}


@pytest.fixture
def admin_auth(admin_token):
    return {'Authorization': 'Bearer ' + admin_token}


def assert_ok(body, message='接口应返回成功'):
    assert body.get('code') == 200, f'{message}: {body}'
    return body.get('data')


def assert_fail(body, code=None):
    assert body.get('code') != 200, f'接口本应失败: {body}'
    if code is not None:
        assert body.get('code') == code, body
    return body
