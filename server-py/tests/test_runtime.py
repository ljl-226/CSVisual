"""项目内置工具链（runtime/）的探测优先级与契约测试。

背景：改造前在线运行完全依赖「用户机器上装过什么编译器」，换台电脑就点不动运行。
改造后探测顺序固定为「内置 → 环境变量 → PATH → 常见安装目录 → 受限扫描」。

这条优先级必须被测试锁住：一旦被写反，内置工具链会**静默失效** ——
不报任何错，只是又悄悄用回了用户机器上那个编译器，
而「换台电脑就点不动」的原始问题会重新出现且无从察觉。
"""

from pathlib import Path

import pytest

from conftest import assert_ok

from app.routers.code import (_missing_hint, collect_compiler_candidates, detect_env,
                              find_jdk, is_bundled, runtime_dirs)

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME = REPO_ROOT / 'runtime'

CC_BIN = RUNTIME / 'c-cpp' / 'bin'
JAVA_BIN = RUNTIME / 'java' / 'bin'


# ==================== 目录约定 ====================
def test_runtime_dirs_default_to_repo_root():
    dirs = runtime_dirs()
    assert dirs, '至少要有一个候选目录'
    assert Path(dirs[0]) == RUNTIME, dirs


def test_runtime_dirs_env_override(monkeypatch, tmp_path):
    """CSVISUAL_RUNTIME 用于把内置工具链放到别处（例如共享盘）。"""
    monkeypatch.setenv('CSVISUAL_RUNTIME', str(tmp_path))
    assert Path(runtime_dirs()[0]) == tmp_path


def test_runtime_dirs_are_deduplicated():
    dirs = runtime_dirs()
    assert len(dirs) == len(set(dirs)), dirs


def test_is_bundled_detects_membership():
    assert is_bundled(str(CC_BIN / 'gcc.exe')) is True
    assert is_bundled(str(JAVA_BIN / 'javac.exe')) is True
    assert is_bundled('C:/somewhere/else/gcc.exe') is False
    assert is_bundled(None) is False
    assert is_bundled('') is False


# ==================== 探测优先级 ====================
def test_candidates_put_bundled_compiler_first():
    """内置编译器必须排在候选列表第一位。

    排在后面等于没有 —— findCompiler 取第一个「验证通过」的候选，
    只要 PATH 里有个能编过 hello world 的老 gcc，内置工具链就永远不会被用到。
    """
    if not (CC_BIN / 'gcc.exe').exists():
        pytest.skip('未部署内置 C/C++ 工具链（runtime/c-cpp），跳过优先级断言')
    cands = collect_compiler_candidates('gcc')
    assert cands, '候选列表不应为空'
    assert cands[0].lower().startswith(str(RUNTIME).lower()), cands[:3]
    assert Path(cands[0]).name.lower() == 'gcc.exe'


def test_find_jdk_prefers_bundled():
    if not (JAVA_BIN / 'javac.exe').exists():
        pytest.skip('未部署内置 Java 运行时')
    jdk = find_jdk()
    assert jdk is not None
    assert str(JAVA_BIN / 'javac.exe').lower() == str(jdk['javac']).lower(), jdk
    assert str(JAVA_BIN / 'java.exe').lower() == str(jdk['java']).lower(), jdk


# ==================== /code/env 契约 ====================
def test_env_covers_all_languages_with_source():
    env = detect_env()
    for lang in ('c', 'cpp', 'java', 'python', 'javascript'):
        assert lang in env, lang
        assert 'available' in env[lang], lang
        assert 'source' in env[lang], lang
        assert env[lang]['source'] in ('bundled', 'system', None), env[lang]


def test_env_marks_bundled_when_deployed():
    env = detect_env()
    for lang, marker in (('c', CC_BIN / 'gcc.exe'),
                         ('cpp', CC_BIN / 'g++.exe'),
                         ('java', JAVA_BIN / 'javac.exe')):
        if not marker.exists():
            continue
        assert env[lang]['available'] is True, env[lang]
        assert env[lang]['source'] == 'bundled', env[lang]
        assert str(marker).lower() == str(env[lang]['bin']).lower(), env[lang]


def test_java_source_not_degraded_to_system():
    """回归：java 的探测函数自带内置优先，必须排在 PATH 探测之前。

    曾经写成「先查 PATH 再看内置」，结果系统 PATH 里的 javac 先被命中，
    内置运行时永远轮不上 —— 而界面上一切正常，只是悄悄用回了系统 JDK。
    """
    if not (JAVA_BIN / 'javac.exe').exists():
        pytest.skip('未部署内置 Java 运行时')
    assert detect_env()['java']['source'] == 'bundled'


def test_code_env_endpoint_exposes_source(client, auth):
    data = assert_ok(client.get('/api/code/env', headers=auth).json())
    assert {'c', 'cpp', 'java', 'python', 'javascript'} <= set(data.keys())
    for lang, item in data.items():
        assert 'source' in item, lang


# ==================== 缺失时的提示 ====================
def test_missing_hint_points_to_setup_script():
    """环境缺失时必须给出「下一步做什么」，而不是只丢一句不可用。"""
    hint = _missing_hint('c')
    assert 'setup-runtime.bat' in hint
    assert 'C' in hint


def test_missing_hint_includes_failure_reasons_when_given():
    hint = _missing_hint('cpp', ['gcc.exe → 编译失败：xxx'])
    assert 'gcc.exe' in hint


# ==================== 内置产物本身的体检 ====================
def test_bundled_java_runtime_is_actually_trimmed():
    """jlink 裁剪后的运行时应当远小于完整 JDK，否则说明裁剪静默失效了。"""
    if not JAVA_BIN.exists():
        pytest.skip('未部署内置 Java 运行时')
    size = sum(f.stat().st_size for f in (RUNTIME / 'java').rglob('*') if f.is_file())
    assert size < 150 * 1024 * 1024, '内置 Java 运行时 %d 字节，看起来没裁剪' % size


def test_bundled_cc_has_no_fortran_frontend():
    """Fortran 前端（f951.exe）约 39 MB，对 C/C++ 教学平台完全用不到，必须被裁掉。"""
    d = RUNTIME / 'c-cpp'
    if not d.exists():
        pytest.skip('未部署内置 C/C++ 工具链')
    leftovers = [str(p) for p in d.rglob('f951.exe')]
    assert not leftovers, leftovers
