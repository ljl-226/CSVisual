"""找回密码测试：不经过管理员，用户凭「账号 + 姓名」自证身份后自己重设密码。

守三条线：
  1) 注册必须填姓名（不填的账号等于永远找不回密码）
  2) 姓名对不上、账号不存在，返回同一句文案（否则这接口能枚举注册名单）
  3) 改名后立刻按新姓名生效，旧姓名失效
"""

import time

from conftest import assert_ok

UID = str(int(time.time() * 1000) % 100000)


def _register(client, name, password='OldPass123', real_name='找回测试'):
    body = client.post('/api/auth/register',
                       json={'username': name, 'password': password, 'realName': real_name}).json()
    assert_ok(body, name)
    token = client.post('/api/auth/login', json={'username': name, 'password': password}).json()['data']['token']
    return token


# ==================== 注册：姓名必填 ====================
def test_register_without_real_name_rejected(client):
    body = client.post('/api/auth/register',
                       json={'username': 'py_fn0' + UID, 'password': 'OldPass123'}).json()
    assert body['code'] == 400
    assert '姓名' in body['message']


def test_register_too_short_real_name_rejected(client):
    body = client.post('/api/auth/register',
                       json={'username': 'py_fn1' + UID, 'password': 'OldPass123', 'realName': '张'}).json()
    assert body['code'] == 400


def test_register_ok_and_me_echoes_real_name(client):
    token = _register(client, 'py_fn2' + UID)
    me = client.get('/api/auth/me', headers={'Authorization': 'Bearer ' + token}).json()
    assert assert_ok(me)['realName'] == '找回测试'


# ==================== 姓名找回主流程 ====================
def test_forgot_confirm_ok_and_old_password_dead(client):
    username = 'py_fb7' + UID
    _register(client, username)

    body = client.post('/api/auth/forgot/confirm', json={
        'username': username, 'realName': '找回测试', 'newPassword': 'NewPass456'}).json()
    assert_ok(body, '姓名正确应可重置')

    assert client.post('/api/auth/login', json={'username': username,
                                                'password': 'NewPass456'}).json()['code'] == 200, '新密码应能登录'
    assert client.post('/api/auth/login', json={'username': username,
                                                'password': 'OldPass123'}).json()['code'] == 400, '旧密码应失效'


def test_forgot_confirm_wrong_name_rejected(client):
    username = 'py_fb6' + UID
    _register(client, username)
    body = client.post('/api/auth/forgot/confirm', json={
        'username': username, 'realName': '别人', 'newPassword': 'NewPass456'}).json()
    assert body['code'] == 400


def test_forgot_confirm_short_password_rejected(client):
    username = 'py_fb8' + UID
    _register(client, username)
    body = client.post('/api/auth/forgot/confirm', json={
        'username': username, 'realName': '找回测试', 'newPassword': '123'}).json()
    assert body['code'] == 400
    assert '6-64' in body['message']


def test_forgot_confirm_name_space_insensitive(client):
    """手打姓名多敲一个空格不该让人找不回密码。"""
    username = 'py_fb9' + UID
    _register(client, username, real_name='张 三')
    body = client.post('/api/auth/forgot/confirm', json={
        'username': username, 'realName': '张三', 'newPassword': 'NewPass789'}).json()
    assert_ok(body, '姓名内空格应容错')


# ==================== 改名 ====================
def test_profile_rename_takes_effect(client):
    username = 'py_fb11' + UID
    token = _register(client, username, real_name='旧名字')
    assert_ok(client.post('/api/auth/profile', headers={'Authorization': 'Bearer ' + token},
                          json={'realName': '新名字'}).json(), '改名应成功')

    ok = client.post('/api/auth/forgot/confirm', json={
        'username': username, 'realName': '新名字', 'newPassword': 'NewPass321'}).json()
    assert ok['code'] == 200, ok
    assert client.post('/api/auth/forgot/confirm', json={
        'username': username, 'realName': '旧名字', 'newPassword': 'NewPass321'}).json()['code'] == 400, '旧姓名应失效'


def test_profile_rename_need_login(client):
    assert client.post('/api/auth/profile', json={'realName': '随便'}).status_code == 401


def test_profile_rename_bad_name(client):
    token = _register(client, 'py_fb12' + UID)
    body = client.post('/api/auth/profile', headers={'Authorization': 'Bearer ' + token},
                       json={'realName': '   '}).json()
    assert body['code'] == 400


# ==================== 边界与防枚举 ====================
def test_unknown_user_and_wrong_name_same_message(client):
    """账号不存在与姓名不符必须同一句，否则这接口成了免费的注册名单探测器。"""
    username = 'py_fb10' + UID
    _register(client, username)
    ghost = client.post('/api/auth/forgot/confirm', json={
        'username': 'ghost_' + UID, 'realName': '找回测试', 'newPassword': 'NewPass456'}).json()
    wrong = client.post('/api/auth/forgot/confirm', json={
        'username': username, 'realName': '别人', 'newPassword': 'NewPass456'}).json()
    assert ghost['code'] == 400 and wrong['code'] == 400
    assert ghost['message'] == wrong['message']


def test_forgot_confirm_missing_fields(client):
    assert client.post('/api/auth/forgot/confirm', json={'username': 'x'}).json()['code'] == 400
    assert client.post('/api/auth/forgot/confirm', json={}).json()['code'] == 400
