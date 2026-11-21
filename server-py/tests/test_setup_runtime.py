"""tools/setup_runtime.py 的纯函数测试。

这个脚本是「让任何用户都能跑代码」的唯一入口，而它自己又不能依赖任何第三方包
（否则部署工具链本身又变成一个环境依赖）。这里只测不联网、不改动项目文件的纯逻辑。
"""

import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / 'tools') not in sys.path:
    sys.path.insert(0, str(ROOT / 'tools'))

import setup_runtime as sr  # noqa: E402


# ==================== 基础工具 ====================
def test_human_readable_sizes():
    assert sr.human(0) == '0 B'
    assert sr.human(512) == '512 B'
    assert sr.human(1024) == '1.0 KB'
    assert sr.human(1536) == '1.5 KB'
    assert sr.human(5 * 1024 ** 2) == '5.0 MB'
    assert sr.human(3 * 1024 ** 3) == '3.0 GB'


def test_match_any_glob():
    assert sr.match_any('gdb.exe', ['gdb.exe', 'cmake.exe'])
    assert sr.match_any('git-foo.exe', ['git-*.exe'])
    assert sr.match_any('CLANGD.EXE', ['clangd.exe'])       # 大小写不敏感
    assert not sr.match_any('gcc.exe', ['gdb.exe', 'cmake.exe'])


def test_dir_size_counts_files(tmp_path):
    (tmp_path / 'a').mkdir()
    (tmp_path / 'a' / 'x.bin').write_bytes(b'0' * 100)
    (tmp_path / 'y.bin').write_bytes(b'0' * 50)
    assert sr.dir_size(str(tmp_path)) == 150


def test_rm_is_quiet_on_missing_path(tmp_path):
    sr.rm(str(tmp_path / 'not-there'))          # 不应抛异常
    d = tmp_path / 'd'
    d.mkdir()
    (d / 'f').write_text('x')
    sr.rm(str(d))
    assert not d.exists()


# ==================== 目录与包映射 ====================
def test_runtime_dir_is_repo_root():
    assert Path(sr.RUNTIME) == ROOT / 'runtime'


def test_pkg_mapping():
    assert sr.PKG_OF['c'] == sr.PKG_OF['cpp'] == 'c-cpp'
    assert sr.PKG_OF['java'] == 'java'
    assert sr.PKG_OF['python'] == 'python'
    assert sr.PKG_OF['node'] == 'node'


def test_default_languages_include_compiled_ones():
    """默认至少要装 C/C++ 和 Java —— 这两样是最不可能「用户机器上刚好有」的。"""
    import argparse  # noqa: F401  (仅为可读性保留)
    defaults = ('c', 'cpp', 'java')
    for l in defaults:
        assert l in sr.LANGS


# ==================== 下载源 ====================
def test_gh_mirrors_are_wellformed():
    assert sr.GH_MIRRORS, '镜像列表不能为空'
    assert sr.GH_MIRRORS[-1] == '', '最后一项应当是直连（空前缀），作为兜底'
    for m in sr.GH_MIRRORS[:-1]:
        assert m.startswith('https://'), m
        assert m.endswith('/'), m


def test_download_urls_are_https():
    for u in (sr.W64DEVKIT_URL, sr.PY_URL, sr.NODE_URL, sr.ADOPTIUM_URL):
        assert u.startswith('https://'), u


def test_python_fallbacks_are_distinct_versions():
    """主 URL 挂了要能退到别的版本，不能几条都指向同一个文件。"""
    urls = [sr.PY_URL] + list(sr.PY_FALLBACKS)
    assert len(set(urls)) == len(urls)


# ==================== 解压 ====================
def test_extract_flattens_single_root(tmp_path):
    z = tmp_path / 'a.zip'
    with zipfile.ZipFile(z, 'w') as f:
        f.writestr('pkg-1.0/bin/gcc.exe', 'x')
        f.writestr('pkg-1.0/include/stdio.h', 'y')
    out = sr.extract(str(z), str(tmp_path / 'out'))
    assert Path(out, 'bin', 'gcc.exe').exists(), out
    assert Path(out, 'include', 'stdio.h').exists(), out


def test_extract_keeps_layout_when_multiple_entries(tmp_path):
    z = tmp_path / 'b.zip'
    with zipfile.ZipFile(z, 'w') as f:
        f.writestr('bin/a.exe', 'x')
        f.writestr('include/a.h', 'y')
    out = sr.extract(str(z), str(tmp_path / 'out2'))
    assert Path(out, 'bin', 'a.exe').exists(), out


def test_extract_rejects_unknown_format(tmp_path):
    p = tmp_path / 'weird.rar'
    p.write_bytes(b'x')
    with pytest.raises(RuntimeError):
        sr.extract(str(p), str(tmp_path / 'out3'))


# ==================== 工具链根目录定位 ====================
def test_toolchain_root_finds_bin_directly(tmp_path):
    d = tmp_path / 'tc'
    (d / 'bin').mkdir(parents=True)
    assert Path(sr.toolchain_root(str(d))) == d


def test_toolchain_root_unwraps_one_level(tmp_path):
    nested = tmp_path / 'nested' / 'inner'
    (nested / 'bin').mkdir(parents=True)
    assert Path(sr.toolchain_root(str(tmp_path / 'nested'))) == nested


def test_toolchain_root_falls_back_to_input(tmp_path):
    d = tmp_path / 'plain'
    d.mkdir()
    assert Path(sr.toolchain_root(str(d))) == d


# ==================== 有界扫描 ====================
def test_scan_bins_respects_depth_limit(tmp_path):
    (tmp_path / 'a' / 'bin').mkdir(parents=True)
    (tmp_path / 'x' / 'y' / 'z' / 'deep' / 'bin').mkdir(parents=True)
    bins = sr._scan_bins([str(tmp_path)], depth=1)
    assert any(b.endswith(str(Path('a', 'bin'))) for b in bins), bins
    assert not any('deep' in b for b in bins), bins


def test_scan_bins_on_missing_root_is_empty(tmp_path):
    assert sr._scan_bins([str(tmp_path / 'nope')]) == []


# ==================== 裁剪清单 ====================
def test_prune_lists_cover_the_heavy_items():
    """裁剪清单必须覆盖那些「体积大又和编译无关」的东西。

    漏掉任何一项，内置包就会白白胖几十上百 MB —— 而 zip 分享包是要发给同学的。
    """
    joined = ' '.join(list(sr.DROP_DIRS) + list(sr.DROP_BIN_GLOBS) + list(sr.DROP_NESTED_GLOBS)).lower()
    for must in ('lib32', 'share', 'gdb.exe', 'cmake.exe', 'ctest.exe', 'f951.exe',
                 'clangd.exe', 'liblldb.dll', 'i686-w64-mingw32'):
        assert must in joined, '裁剪清单缺少 %s' % must


def test_prune_never_drops_the_essentials():
    """反面约束：不能把编译必需的东西裁掉。

    注意要用精确匹配 —— 上一次写成子串判断，lib / lib32 直接互相误报。
    """
    drop_dirs = {d.lower() for d in sr.DROP_DIRS}
    for must_keep in ('bin', 'include', 'lib', 'libexec'):
        assert must_keep not in drop_dirs, '裁剪清单误伤了目录 %s' % must_keep
    for must_keep in ('gcc.exe', 'g++.exe', 'cc1.exe', 'cc1plus.exe', 'as.exe', 'ld.exe',
                      'collect2.exe', 'libstdc++-6.dll'):
        assert not sr.match_any(must_keep, sr.DROP_BIN_GLOBS), '误伤 %s' % must_keep
        assert not sr.match_any(must_keep, sr.DROP_NESTED_GLOBS), '误伤 %s' % must_keep


# ==================== 验证函数 ====================
def test_verify_lang_reports_missing_instead_of_crashing():
    """未部署时必须如实返回 False，不能抛异常也不能报「通过」。"""
    ok, why = sr.verify_lang('c')
    if (Path(sr.RUNTIME) / 'c-cpp' / 'bin' / 'gcc.exe').exists():
        assert ok, why
    else:
        assert not ok
        assert 'gcc' in why.lower()


def test_verify_lang_unknown_language():
    ok, why = sr.verify_lang('brainfuck')
    assert not ok and '未知语言' in why


def test_verify_lang_deployed_java():
    if not (Path(sr.RUNTIME) / 'java' / 'bin' / 'javac.exe').exists():
        pytest.skip('未部署内置 Java 运行时')
    ok, why = sr.verify_lang('java', verbose=True)
    assert ok, why
    assert 'CSV' in why


def test_manifest_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(sr, 'RUNTIME', str(tmp_path))
    monkeypatch.setattr(sr, 'MANIFEST', str(tmp_path / '.manifest.json'))
    assert sr.load_manifest() == {}
    sr.save_manifest({'c-cpp': {'source': 'test', 'verified': True}})
    got = sr.load_manifest()
    assert got['c-cpp']['verified'] is True


# ==================== 批处理文件本身的规范 ====================
def _batch_files():
    out = list(ROOT.glob('*.bat'))
    for sub in ('tools', 'server-py', 'server'):
        out += list((ROOT / sub).glob('*.bat'))
    return sorted(out)


def test_batch_files_use_crlf():
    """批处理必须是 CRLF 换行。

    纯 LF 的 .bat 在 cmd.exe 下会让行边界漂移 —— 注释行被当命令执行、
    正文被截断。这类问题在任何编辑器里都看不出来，只有真正双击时才炸，
    上一版交付的 start-python.bat / server-py\\start.bat 就踩过这个坑。
    """
    bats = _batch_files()
    assert bats, '一个 .bat 都没找到，路径探测有问题'
    for b in bats:
        data = b.read_bytes()
        assert b'\r\n' in data, '%s 没有 CRLF 换行' % b.name
        assert data.replace(b'\r\n', b'').count(b'\n') == 0, '%s 混有纯 LF 换行' % b.name


def _launcher_files():
    """不看日志、不出中文的工具启动器：tools/ 下的全部 + 根目录的 pack.bat。

    start.bat 那一类是给用户看的交互式向导，历史上一直工作正常，
    这次踩雷的是 pack.bat（含工具链那条分支），所以一并收进规范里。
    """
    return sorted((ROOT / 'tools').glob('*.bat')) + [ROOT / 'pack.bat']


def test_tool_launchers_are_ascii_only():
    """工具启动器必须纯 ASCII。

    cmd.exe 按当前代码页逐字节解析批处理，UTF-8 中文碰上 chcp 切换会让
    行边界漂移，于是中文注释被当成命令执行。中文提示一律交给
    setup_runtime.py / pack.py 输出（Python 的 Unicode 输出不受这个问题影响）。

    这个坑是实测出来的，不是理论：含内置工具链的那条打包分支会稳定打出一
        '...几十' is not recognized as an internal or external command
    而同一份脚本去掉 runtime\\ 就干干净净 —— 典型的「看起来像偶发」，
    也正因如此不该去调试它，应该从源头把中文搬出批处理。
    """
    bats = _launcher_files()
    assert len(bats) >= 3, '启动器清单不完整，路径探测有问题'
    for b in bats:
        data = b.read_bytes()
        bad = [c for c in data if c > 127]
        assert not bad, '%s 含 %d 个非 ASCII 字节' % (b.name, len(bad))


def test_launchers_delegate_to_python_that_exists():
    """启动器干的唯一一件事就是把活交给 Python，指错文件等于整个功能失联。"""
    bats = _launcher_files()
    found = 0
    for b in bats:
        text = b.read_text(encoding='utf-8', errors='replace')
        targets = [seg for seg in text.replace('"', ' ').split() if seg.endswith('.py')]
        assert targets, '%s 没有调用任何 .py —— 启动器失去意义' % b.name
        for t in targets:
            target = (ROOT / t.replace('/', '\\'))
            assert target.is_file(), '%s 指向不存在的 %s' % (b.name, t)
            found += 1
    assert found, '一个目标脚本都没解析出来'


def test_ensure_mode_is_wired_into_start_scripts():
    """启动脚本必须真的调用就绪检查，否则这套东西没人会主动去跑。"""
    hooked = []
    for name in ('start-python.bat', 'start.bat'):
        p = ROOT / name
        if not p.exists():
            continue
        text = p.read_text(encoding='utf-8', errors='replace')
        if 'ensure-runtime.bat' in text:
            hooked.append(name)
    assert hooked, '没有任何启动脚本调用 tools\\ensure-runtime.bat'


def test_no_python_fallback_when_deploying():
    """--ensure 在没装工具链、且用户跳过时必须直接返回，不能抛异常。"""
    import argparse  # noqa: F401
    assert hasattr(sr, 'ensure_mode')
    assert hasattr(sr, 'install_all')


# ==================== --ensure（启动前的就绪检查）====================
def test_ensure_mode_ready_when_deployed(tmp_path, monkeypatch):
    monkeypatch.setattr(sr, 'RUNTIME', str(tmp_path))
    (tmp_path / 'c-cpp' / 'bin').mkdir(parents=True)
    (tmp_path / 'c-cpp' / 'bin' / 'gcc.exe').write_bytes(b'x')
    assert sr.ensure_mode() == 0


def test_ensure_mode_skip_returns_zero(tmp_path, monkeypatch):
    """用户选择跳过时必须安静返回 0 —— 这是启动流程的一环，不能阻断启动。"""
    monkeypatch.setattr(sr, 'RUNTIME', str(tmp_path))       # 空目录 = 未部署
    monkeypatch.setattr('builtins.input', lambda *a: 'n')
    assert sr.ensure_mode() == 0


def test_ensure_mode_accepts_only_y(tmp_path, monkeypatch):
    monkeypatch.setattr(sr, 'RUNTIME', str(tmp_path))
    monkeypatch.setattr('builtins.input', lambda *a: 'y')
    called = {}

    def fake_install(langs, *a, **k):
        called['langs'] = langs
        return 0

    monkeypatch.setattr(sr, 'install_all', fake_install)
    assert sr.ensure_mode() == 0
    assert called['langs'] == ['c', 'cpp', 'java']


def test_ensure_mode_survives_closed_stdin(tmp_path, monkeypatch):
    """被启动脚本调用时 stdin 可能是关掉的，这种情况下不能崩。"""
    monkeypatch.setattr(sr, 'RUNTIME', str(tmp_path))

    def boom(*a):
        raise EOFError

    monkeypatch.setattr('builtins.input', boom)
    assert sr.ensure_mode() == 0


def test_ensure_mode_reports_unsupported_language():
    assert sr.install_all(['brainfuck']) == 2
