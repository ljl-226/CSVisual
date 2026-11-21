"""在线代码运行测试。

执行环境分两种情况：
- 能创建子进程（本机 / 常规服务器）：断言真实输出；
- 受限沙箱：子进程被禁，接口返回「无法启动运行环境」的降级提示。

两种结果都放行，但必须保证「不伪造成功」——这点与 Node 版一致。
"""

import os

import pytest

from conftest import assert_fail, assert_ok
from app.routers.code import LANGS, collect_compiler_candidates, detect_env, find_python, with_bin_dir


def test_env_endpoint(client, auth):
    data = assert_ok(client.get('/api/code/env', headers=auth).json())
    for lang in LANGS:
        assert lang in data
        assert 'available' in data[lang]


def test_env_python_uses_current_interpreter():
    """服务本身就跑在 Python 上，解释器必然可用"""
    import sys

    assert find_python() == sys.executable


def test_collect_compiler_candidates_returns_paths():
    cands = collect_compiler_candidates('gcc')
    assert 'gcc' in cands          # PATH 中的裸命令
    assert len(cands) >= 1
    # 深度扫描结果若存在，必须包含 bin 目录（历史上漏掉 bin 会导致整次扫描一无所获）
    for p in cands:
        if '\\' in p or '/' in p:
            assert p.endswith('gcc.exe') or p.endswith('gcc'), p


def test_with_bin_dir_includes_compiler_dir():
    env = with_bin_dir('C:\\mingw64\\bin\\gcc.exe')
    assert env['PATH'].startswith('C:\\mingw64\\bin')


def test_run_requires_login(client):
    r = client.post('/api/code/run', json={'language': 'python', 'code': 'print(1)'})
    assert r.status_code == 401


def test_run_rejects_unknown_language(client, auth):
    assert_fail(client.post('/api/code/run', headers=auth,
                            json={'language': 'cobol', 'code': 'print(1)'}).json(), 400)


def test_run_rejects_empty_code(client, auth):
    assert_fail(client.post('/api/code/run', headers=auth,
                            json={'language': 'python', 'code': '   '}).json(), 400)


def test_run_rejects_too_long(client, auth):
    assert_fail(client.post('/api/code/run', headers=auth,
                            json={'language': 'python', 'code': 'a' * 20001}).json(), 400)


def test_run_python_or_degrade(client, auth):
    """要么真跑出结果，要么明确告知环境不可用 —— 绝不伪造成功"""
    data = assert_ok(client.post('/api/code/run', headers=auth,
                                 json={'language': 'python', 'code': 'print("hello-py")'}).json())
    if data.get('unsupported'):
        assert '无法在线执行' in data['stderr']
    elif data.get('error'):
        assert '无法启动运行环境' in data['stderr'] or '执行超时' in data['stderr']
    else:
        assert 'hello-py' in data['output']


def test_run_never_fakes_success(client, auth):
    """代码语法错误时不能返回 0 退出码还带空输出"""
    data = assert_ok(client.post('/api/code/run', headers=auth,
                                 json={'language': 'python', 'code': 'print(1'}).json())
    if not data.get('unsupported'):
        assert data['error'] is True
        assert data['stderr']


def test_detect_env_cached():
    env = detect_env()
    assert env is detect_env()   # 60 秒内缓存复用，避免每次请求都扫描磁盘


def test_run_rate_limit(client, auth):
    """每分钟 30 次上限"""
    last = None
    for i in range(32):
        last = client.post('/api/code/run', headers=auth,
                           json={'language': 'python', 'code': 'print(1)'}).json()
    assert last['code'] == 429


# ==================== stdin 回归测试 ====================
def test_run_passes_stdin_to_process():
    """回归：subprocess 的 input 必须是 bytes。

    传 str 会让内部写入线程抛 TypeError 后静默死掉，子进程 stdin 永不关闭，
    凡是读输入的程序都会卡到超时——判题 100% 失败。这类 bug 不会报错、只会超时，
    所以必须单独锁住。
    """
    import sys
    sys.path.insert(0, '.')
    from app.routers.code import detect_env, run

    env = detect_env()
    py = env.get('python', {}).get('bin')
    if not py:
        pytest.skip('本机未检测到 Python 解释器')

    import tempfile
    code = 'import sys\nprint(sum(int(x) for x in sys.stdin.read().split()))\n'
    with tempfile.TemporaryDirectory() as d:
        fp = os.path.join(d, 'main.py')
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(code)
        r = run(py, [fp], {'stdin': '3 5 7', 'timeout': 8000, 'cwd': d})
    assert r['spawnError'] is None, f"不应超时: {r['spawnError']}"
    assert r['stdout'].strip() == '15'


def test_run_stdin_bytes_not_translated():
    """stdin 按 bytes 传入，不做换行转换，保证判题逐字符比对不被干扰。"""
    import sys
    sys.path.insert(0, '.')
    from app.routers.code import detect_env, run

    env = detect_env()
    py = env.get('python', {}).get('bin')
    if not py:
        pytest.skip('本机未检测到 Python 解释器')

    import tempfile
    code = 'import sys\nd = sys.stdin.buffer.read()\nprint(len(d))\n'
    with tempfile.TemporaryDirectory() as d:
        fp = os.path.join(d, 'main.py')
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(code)
        r = run(py, [fp], {'stdin': 'ab\ncd', 'timeout': 8000, 'cwd': d})
    assert r['stdout'].strip() == '5', f"换行被转换了: {r['stdout']!r}"


def test_run_empty_stdin_does_not_hang():
    """不传 stdin 时也要正常关闭管道，不能让读输入的程序挂住。"""
    import sys
    sys.path.insert(0, '.')
    from app.routers.code import detect_env, run

    env = detect_env()
    py = env.get('python', {}).get('bin')
    if not py:
        pytest.skip('本机未检测到 Python 解释器')

    import tempfile
    code = 'import sys\nprint("EOF:" + sys.stdin.read())\n'
    with tempfile.TemporaryDirectory() as d:
        fp = os.path.join(d, 'main.py')
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(code)
        r = run(py, [fp], {'timeout': 8000, 'cwd': d})
    assert r['spawnError'] is None, f"空 stdin 不应卡住: {r['spawnError']}"
    assert r['stdout'].strip() == 'EOF:'
