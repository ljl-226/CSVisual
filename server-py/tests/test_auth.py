"""认证模块测试：注册 / 登录 / 登出 / 当前用户 / 改密码 / 鉴权。"""

import time

from conftest import assert_ok

from app.core.security import hash_password, check_password, sign_token, verify_token


UID = str(int(time.time() * 1000) % 100000)


# ==================== 注册 ====================
def test_register_ok(client):
    body = client.post('/api/auth/register', json={
        'username': 'py_' + UID,
        'password': 'pass1234',
        'realName': '派森同学',
    }).json()
    data = assert_ok(body, '注册成功用例')
    assert data['role'] == 'student'
    assert data['username'] == 'py_' + UID


def test_register_missing_username(client):
    body = client.post('/api/auth/register', json={'password': 'pass1234'}).json()
    assert body['code'] == 400
    assert '账号和密码' in body['message']


def test_register_missing_password(client):
    body = client.post('/api/auth/register', json={'username': 'py_x1'}).json()
    assert body['code'] == 400


def test_register_username_too_short(client):
    body = client.post('/api/auth/register', json={'username': 'ab', 'password': 'pass1234', 'realName': '边界同学'}).json()
    assert body['code'] == 400
    assert '3-20' in body['message']


def test_register_username_illegal_char(client):
    body = client.post('/api/auth/register', json={'username': 'bad-name!', 'password': 'pass1234', 'realName': '边界同学'}).json()
    assert body['code'] == 400


def test_register_username_chinese_rejected(client):
    body = client.post('/api/auth/register', json={'username': '张三', 'password': 'pass1234', 'realName': '边界同学'}).json()
    assert body['code'] == 400


def test_register_reserved_admin(client):
    for name in ['admin', 'ADMIN', 'Admin']:
        body = client.post('/api/auth/register', json={'username': name, 'password': 'pass1234', 'realName': '边界同学'}).json()
        assert body['code'] == 400, name
        assert '保留' in body['message']


def test_register_password_too_short(client):
    body = client.post('/api/auth/register', json={'username': 'py_x2', 'password': '123', 'realName': '边界同学'}).json()
    assert body['code'] == 400
    assert '6-64' in body['message']


def test_register_password_too_long(client):
    body = client.post('/api/auth/register', json={'username': 'py_x3', 'password': 'a' * 65, 'realName': '边界同学'}).json()
    assert body['code'] == 400


def test_register_duplicate(client):
    client.post('/api/auth/register', json={'username': 'py_dup' + UID, 'password': 'pass1234', 'realName': '重复同学'})
    body = client.post('/api/auth/register', json={'username': 'py_dup' + UID, 'password': 'pass1234', 'realName': '重复同学'}).json()
    assert body['code'] == 400
    assert '已存在' in body['message']


def test_register_boundary_lengths(client):
    """3 位账号 + 6 位密码 = 最小合法组合。

    这里必须是 3 位（再短就该被拒），但 3 位账号的字符空间很小，
    而数据库是长期存在的真实库 —— 曾经用固定的 'p' + UID[-2:]，
    只有 100 种取值，跑上几遍就会撞到已存在的名字而返回 400，
    于是测试变成「第一次通过、之后随机失败」。改成随机取名 + 用完即清理。
    """
    import random
    import string

    from app.db import query

    symbols = string.ascii_lowercase + string.digits
    registered = None
    body = None
    for _ in range(30):
        cand = 'p' + ''.join(random.choices(symbols, k=2))
        body = client.post('/api/auth/register', json={'username': cand, 'password': 'abc123', 'realName': '边界同学'}).json()
        if body.get('code') == 200:
            registered = cand
            break
        if '已存在' not in (body.get('message') or ''):
            break
    try:
        assert registered is not None, f'3 位账号 + 6 位密码应可注册，实际返回 {body}'
    finally:
        if registered:
            query('DELETE FROM user WHERE username = ?', [registered])


def test_register_empty_body(client):
    body = client.post('/api/auth/register', json={}).json()
    assert body['code'] == 400


# ==================== 登录 ====================
def test_login_ok(client):
    body = client.post('/api/auth/login', json={'username': 'student', 'password': '123456'}).json()
    data = assert_ok(body, 'student 应能登录')
    assert 'token' in data
    assert data['user']['role'] == 'student'


def test_login_wrong_password(client):
    body = client.post('/api/auth/login', json={'username': 'student', 'password': 'wrong'}).json()
    assert body['code'] == 400
    assert '账号或密码错误' in body['message']


def test_login_nonexistent_user(client):
    body = client.post('/api/auth/login', json={'username': 'nobody_zzz', 'password': '123456'}).json()
    assert body['code'] == 400


def test_login_empty_body(client):
    body = client.post('/api/auth/login', json={}).json()
    assert body['code'] == 400


def test_login_password_is_hashed(client):
    # 登录成功后返回的 user 里绝不能带 password 字段
    body = client.post('/api/auth/login', json={'username': 'student', 'password': '123456'}).json()
    assert 'password' not in body['data']['user']


def test_new_user_can_login(client):
    client.post('/api/auth/register', json={'username': 'py_login' + UID, 'password': 'mypass1', 'realName': '登录同学'})
    body = client.post('/api/auth/login', json={'username': 'py_login' + UID, 'password': 'mypass1'}).json()
    assert_ok(body, '新注册用户应能登录')


# ==================== me / logout ====================
def test_me(client, auth):
    data = assert_ok(client.get('/api/auth/me', headers=auth).json())
    assert data['username'] == 'student'
    assert 'password' not in data


def test_me_no_token(client):
    r = client.get('/api/auth/me')
    assert r.status_code == 401
    assert r.json()['code'] == 401


def test_me_bad_token(client):
    r = client.get('/api/auth/me', headers={'Authorization': 'Bearer not-a-jwt'})
    assert r.status_code == 401


def test_me_malformed_header(client):
    # 缺 Bearer 前缀 → 视为未登录
    r = client.get('/api/auth/me', headers={'Authorization': 'abcdefg'})
    assert r.status_code == 401


def test_logout(client, auth):
    assert_ok(client.post('/api/auth/logout', headers=auth).json())


def test_logout_without_token(client):
    assert client.post('/api/auth/logout').status_code == 401


# ==================== 改密码 ====================
def test_change_password_ok(client):
    username = 'py_pwd' + UID
    client.post('/api/auth/register', json={'username': username, 'password': 'oldpass1', 'realName': '改密同学'})
    token = client.post('/api/auth/login',
                        json={'username': username, 'password': 'oldpass1'}).json()['data']['token']
    headers = {'Authorization': 'Bearer ' + token}

    body = client.post('/api/auth/password', headers=headers,
                       json={'oldPassword': 'oldpass1', 'newPassword': 'newpass2'}).json()
    assert_ok(body, '改密应成功')

    # 旧密码失效，新密码可用
    assert client.post('/api/auth/login', json={'username': username, 'password': 'oldpass1'}).json()['code'] == 400
    assert client.post('/api/auth/login', json={'username': username, 'password': 'newpass2'}).json()['code'] == 200


def test_change_password_wrong_old(client, auth):
    body = client.post('/api/auth/password', headers=auth,
                       json={'oldPassword': 'zzzzzz', 'newPassword': 'newpass2'}).json()
    assert body['code'] == 400
    assert '原密码' in body['message']


def test_change_password_missing_fields(client, auth):
    body = client.post('/api/auth/password', headers=auth, json={'oldPassword': '123456'}).json()
    assert body['code'] == 400


def test_change_password_too_short(client, auth):
    body = client.post('/api/auth/password', headers=auth,
                       json={'oldPassword': '123456', 'newPassword': '1'}).json()
    assert body['code'] == 400


def test_change_password_without_token(client):
    assert client.post('/api/auth/password', json={'oldPassword': 'a', 'newPassword': 'b'}).status_code == 401


# ==================== 安全工具函数 ====================
def test_password_hash_roundtrip():
    h = hash_password('hello123')
    assert h != 'hello123'
    assert check_password('hello123', h)
    assert not check_password('hello124', h)


def test_password_hash_compatible_with_bcrypt_prefix():
    # Node 版 bcryptjs 生成的哈希是 $2a$ / $2b$，Python 必须能校验，否则旧用户无法登录
    assert hash_password('abc123456').startswith(('$2a$', '$2b$', '$2y$'))


def test_token_roundtrip():
    token = sign_token({'id': 7, 'username': 'u', 'role': 'student'})
    payload = verify_token(token)
    assert payload['id'] == 7
    assert payload['username'] == 'u'


def test_token_tampered():
    """签名段被改写后必须失效（verify_token 约定返回 None，调用方转 401）。"""
    token = sign_token({'id': 7, 'username': 'u', 'role': 'student'})
    assert verify_token(token[:-3] + 'xyz') is None
    assert verify_token('') is None
    assert verify_token('a.b.c') is None


def test_token_payload_tampered():
    """只换 payload（比如把 role 改成 admin）也必须失效。"""
    import base64
    import json

    token = sign_token({'id': 7, 'username': 'u', 'role': 'student'})
    head, payload, sig = token.split('.')
    raw = json.loads(base64.urlsafe_b64decode(payload + '=='))
    raw['role'] = 'admin'
    raw['id'] = 1
    new_payload = base64.urlsafe_b64encode(json.dumps(raw).encode()).decode().rstrip('=')
    assert verify_token(f'{head}.{new_payload}.{sig}') is None


def test_role_escalation_via_token_rejected(client):
    """手搓一个 role=admin 的 token 但用错密钥，必须被拒。"""
    import jwt as pyjwt
    bad_token = pyjwt.encode({'id': 1, 'username': 'student', 'role': 'admin'}, 'wrong-secret', algorithm='HS256')
    r = client.get('/api/admin/stats', headers={'Authorization': 'Bearer ' + bad_token})
    assert r.status_code in (401, 403)


def test_student_cannot_access_admin(client, auth):
    r = client.get('/api/admin/stats', headers=auth)
    assert r.status_code == 403
