"""tools/pack.py 的单元测试。

打包脚本是被我改坏过一次的东西：它原先在 cmd 里直接写中文，整包打包时会
抽风式地抛一行乱码命令错误。现在批处理退化成纯 ASCII 启动器，真正的活都在
pack.py 里 —— 那这些活就必须能被自动化验证，不能只靠「双击看看」。

这里的测试都不碰真实 runtime\\（456 MB），用 tmp_path 搭一个同构的小仓库。
"""

import os
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / 'tools') not in sys.path:
    sys.path.insert(0, str(ROOT / 'tools'))

import pack  # noqa: E402


# ==================== 辅助 ====================
def make_repo(tmp_path):
    """搭一个和真实项目同构的小仓库，返回根目录 Path。"""
    (tmp_path / 'server-py' / 'src').mkdir(parents=True)
    (tmp_path / 'server-py' / '.venv').mkdir(parents=True)
    (tmp_path / 'server-py' / '.env').write_text('DB_PASSWORD=secret', encoding='utf-8')
    (tmp_path / 'server-py' / 'app.py').write_text('print(1)', encoding='utf-8')
    (tmp_path / 'server-py' / 'src' / 'main.py').write_text('print(1)', encoding='utf-8')
    (tmp_path / 'server-py' / '.venv' / 'big.pyc').write_text('x' * 10, encoding='utf-8')

    (tmp_path / 'web' / 'src').mkdir(parents=True)
    (tmp_path / 'web' / 'src' / 'main.js').write_text('// web', encoding='utf-8')
    (tmp_path / 'web' / 'dist' / 'assets').mkdir(parents=True)
    (tmp_path / 'web' / 'dist' / 'assets' / 'a.js').write_text('x', encoding='utf-8')

    (tmp_path / 'tools').mkdir(parents=True)
    (tmp_path / 'tools' / 'pack.py').write_text('# pack', encoding='utf-8')
    (tmp_path / 'tools' / 'stale.pyc').write_bytes(b'\x00\x01')

    (tmp_path / 'runtime' / 'c-cpp' / 'bin').mkdir(parents=True)
    (tmp_path / 'runtime' / 'c-cpp' / 'bin' / 'gcc.exe').write_bytes(b'MZ' + b'\x00' * 200)

    (tmp_path / 'README.md').write_text('# hi', encoding='utf-8')
    (tmp_path / 'start.bat').write_text('@echo off', encoding='utf-8')
    return tmp_path


# ==================== 体积显示 ====================
def test_human_sizes():
    assert pack.human(0) == '0 B'
    assert pack.human(999) == '999 B'
    assert pack.human(1024) == '1.0 KB'
    assert pack.human(2 * 1024 ** 2) == '2.0 MB'
    assert 'GB' in pack.human(5 * 1024 ** 3)


# ==================== 遍历与剪枝 ====================
def test_iter_files_prunes_excluded_dirs(tmp_path):
    make_repo(tmp_path)
    src = tmp_path / 'server-py'
    got = [rel for _abs, rel in pack.iter_files(src, {'.venv'}, set())]
    assert '.venv/big.pyc' not in got
    assert 'app.py' in got
    assert 'src/main.py' in got


def test_iter_files_applies_file_globs(tmp_path):
    make_repo(tmp_path)
    src = tmp_path / 'server-py'
    got = [rel for _abs, rel in pack.iter_files(src, set(), {'.env'})]
    assert '.env' not in got
    assert 'app.py' in got


def test_iter_files_emits_empty_dirs(tmp_path):
    (tmp_path / 'a' / 'b').mkdir(parents=True)
    (tmp_path / 'a' / 'keep.txt').write_text('x', encoding='utf-8')
    entries = list(pack.iter_files(tmp_path, set(), set()))
    empties = [rel for abs_p, rel in entries if abs_p is None]
    assert empties, '空目录应该被记录，否则解压后目录结构会缺胳膊少腿'


# ==================== collect_jobs ====================
def test_collect_jobs_without_runtime(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    monkeypatch.setattr(pack, 'ROOT', str(repo))
    jobs = pack.collect_jobs(with_runtime=False)
    arcs = [arc for _abs, arc in jobs]
    assert not any(a.startswith('CSVisual/runtime/') for a in arcs)
    assert 'CSVisual/server-py/app.py' in arcs
    assert 'CSVisual/README.md' in arcs


def test_collect_jobs_with_runtime(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    monkeypatch.setattr(pack, 'ROOT', str(repo))
    arcs = [arc for _abs, arc in pack.collect_jobs(with_runtime=True)]
    assert 'CSVisual/runtime/c-cpp/bin/gcc.exe' in arcs


def test_collect_jobs_never_ships_env_or_node_modules(tmp_path, monkeypatch):
    """这是整份列表里最要紧的两条：密码和能重装的依赖。"""
    repo = make_repo(tmp_path)
    monkeypatch.setattr(pack, 'ROOT', str(repo))
    arcs = [arc for _abs, arc in pack.collect_jobs(with_runtime=True)]
    assert not any(a.endswith('.env') for a in arcs), '.env 里有本机数据库密码'
    assert not any('node_modules' in a for a in arcs)
    assert not any(a.endswith('.pyc') for a in arcs)
    assert not any('dist/' in a for a in arcs)


def test_collect_jobs_skips_missing_root_files(tmp_path, monkeypatch):
    """源码里少几个可选文件不该让打包崩。"""
    repo = make_repo(tmp_path)
    (repo / 'stop.sh').unlink(missing_ok=True)
    monkeypatch.setattr(pack, 'ROOT', str(repo))
    arcs = [arc for _abs, arc in pack.collect_jobs(with_runtime=False)]
    assert 'CSVisual/stop.sh' not in arcs
    assert 'CSVisual/README.md' in arcs


def test_collect_jobs_uses_forward_slashes(tmp_path, monkeypatch):
    """zip 内的路径必须是 / —— Windows 的反斜杠进了 zip 别人解压会得到怪名字。"""
    repo = make_repo(tmp_path)
    monkeypatch.setattr(pack, 'ROOT', str(repo))
    for _abs, arc in pack.collect_jobs(with_runtime=True):
        assert '\\' not in arc
        assert arc.startswith('CSVisual/')


# ==================== 真实压缩 ====================
def test_build_zip_roundtrip(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    monkeypatch.setattr(pack, 'ROOT', str(repo))
    jobs = pack.collect_jobs(with_runtime=True)
    out = tmp_path / 'out.zip'
    written, raw = pack.build_zip(jobs, str(out), with_runtime=True)
    assert out.is_file()
    assert written == len([j for j in jobs if j[0] is not None])
    assert raw > 0
    with zipfile.ZipFile(out) as zf:
        names = zf.namelist()
        assert zipfile.ZipInfo
        assert 'CSVisual/server-py/app.py' in names
        assert 'CSVisual/README.md' in names
        assert zf.read('CSVisual/README.md') == b'# hi'
        assert zf.read('CSVisual/runtime/c-cpp/bin/gcc.exe')[:2] == b'MZ'
        assert not any(n.endswith('.env') for n in names)
        assert zf.testzip() is None, '压缩包本身有损坏'


def test_build_zip_compresses(tmp_path, monkeypatch):
    """工具链里有大量可执行文件，压缩率至少应该明显大于 1，否则白白浪费带宽。"""
    repo = make_repo(tmp_path)
    (repo / 'runtime' / 'c-cpp' / 'bin' / 'pad.exe').write_bytes(b'\x00' * 200000)
    monkeypatch.setattr(pack, 'ROOT', str(repo))
    out = tmp_path / 'p.zip'
    _written, raw = pack.build_zip(pack.collect_jobs(True), str(out), True)
    assert raw > 200000
    assert out.stat().st_size < raw * 0.5, '全零文件理应被压得很小'


# ==================== 真实项目的一致性 ====================
def test_dir_rules_match_real_layout():
    """DIR_RULES 里的目录名对不上真实仓库，等于悄悄漏打包。"""
    missing = [d for d in pack.DIR_RULES if not (ROOT / d).is_dir()]
    assert not missing, 'DIR_RULES 指向不存在的目录: %s' % missing


def test_root_files_exist():
    """README 和启动脚本必须在包里，否则对方解压后一脸茫然。"""
    missing = [f for f in ('README.md', 'start-python.bat', 'stop.bat')
               if not (ROOT / f).is_file()]
    assert not missing, '根目录缺少应该随包分发的文件: %s' % missing


def test_pack_py_is_importable_and_ascii_launcher_points_at_it(monkeypatch):
    """批处理里写的调用路径必须真能找到本脚本 —— 改文件名时这条会立刻报警。"""
    launcher = (ROOT / 'pack.bat').read_text(encoding='utf-8', errors='replace')
    assert 'tools\\pack.py' in launcher
    assert (ROOT / 'tools' / 'pack.py').is_file()


def test_dry_run_does_not_write_zip(tmp_path, monkeypatch, capsys):
    repo = make_repo(tmp_path)
    monkeypatch.setattr(pack, 'ROOT', str(repo))
    out = tmp_path / 'never.zip'
    monkeypatch.setattr(pack, 'DEFAULT_OUT', str(out))
    monkeypatch.setattr(sys, 'argv', ['pack.py', '--dry-run'])
    assert pack.main() == 0
    assert not out.exists()
    assert '--dry-run' in capsys.readouterr().out


def test_out_is_overwritten_cleanly(tmp_path, monkeypatch):
    """旧包必须被删掉重写；否则用户会把上一次的产物当成新的发出去。"""
    repo = make_repo(tmp_path)
    monkeypatch.setattr(pack, 'ROOT', str(repo))
    out = tmp_path / 'o.zip'
    out.write_bytes(b'STALE' * 100)
    monkeypatch.setattr(sys, 'argv', ['pack.py', '--out', str(out), '--no-runtime'])
    assert pack.main() == 0
    with zipfile.ZipFile(out) as zf:
        assert zf.testzip() is None
    assert b'STALE' not in out.read_bytes()


@pytest.mark.skipif(not (ROOT / 'runtime').is_dir(),
                    reason='本机还没部署内置工具链')
def test_real_runtime_is_packed_by_default(tmp_path, monkeypatch):
    """本机已部署时，默认打包必须带上工具链 —— 这是「谁都能跑代码」的落点。"""
    jobs = pack.collect_jobs(with_runtime=True)
    arcs = [a for _abs, a in jobs]
    assert any(a.startswith('CSVisual/runtime/') for a in arcs)
    manifest = [a for a in arcs if a.endswith('.manifest.json')]
    assert manifest, '连部署清单都没进包，对方无法知道工具链从哪来'
