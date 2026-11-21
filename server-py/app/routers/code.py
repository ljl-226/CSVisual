"""
在线代码运行（编程语言模块配套）

设计要点：
  1. 白名单语言，拒绝未知 language
  2. 每次运行在独立临时目录，超时强杀，输出截断，运行后清理
  3. 本机没有对应编译器/解释器时，不伪造成功，返回「环境缺失」提示由前端降级展示
  4. 简易限流，避免误触死循环把服务拖垮

与 Node 版的差异：JavaScript 原先可用 vm 在进程内沙箱执行，Python 没有等价能力，
这里改为调用本机 node 子进程（探测到 node 就可用，否则如实报"环境缺失"）。
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time

from fastapi import APIRouter, Depends, Request

from app.core.body import body_of
from app.core.deps import current_user
from app.core.response import fail, ok
from app.utils.remote_run import NOTICE, is_env_error, remote_run

router = APIRouter()

RUN_ROOT = os.path.join(tempfile.gettempdir(), 'csvisual-run')
MAX_CODE = 20000
MAX_OUT = 8000
MAX_STDIN = 20000        # 运行输入（stdin）最大长度
TIMEOUT = 5000

# 代码里出现这些写法 = 这个程序要从标准输入读数据
_READS_STDIN = re.compile(
    r'scanf\s*\(|getchar\s*\(|gets\s*\(|getline\s*\(|cin\s*>>|std::cin'
    r'|input\s*\(|raw_input\s*\(|sys\.stdin'
    r'|Scanner|System\.in|readLine|readline'
    r'|prompt\s*\(|readFileSync\s*\(\s*0|readSync\s*\(',
    re.IGNORECASE)

_STDIN_TIP = (
    '\n\n提示：这段程序要从键盘读数据（scanf / input / Scanner 等），'
    '但这次运行没有给它任何输入。请在编辑器下方的「程序输入（stdin）」框里'
    '填好要输入的内容（多个数据用空格或换行分隔），再点「运行」。'
)


def stdin_hint(code, has_stdin, failed, out):
    """「程序在等你敲字，可你没给它东西」时的兜底提示，与 Node 端 stdinHint 同构。

    在线运行一次请求跑完，没法像真终端那样中途等人敲键盘；用户第一次直接点运行，
    看到的只有 EOFError / NoSuchElementException 之类的冰冷报错。这里把正确用法讲清楚。
    """
    if has_stdin or not _READS_STDIN.search(code or ''):
        return ''
    if not failed and str(out or '').strip():
        return ''          # 有输出说明没被输入卡住
    return _STDIN_TIP


WINDOWS = os.name == 'nt'

LANGS = {
    'c': {'ext': 'c', 'bin': ['gcc', 'clang', 'cc'], 'label': 'C'},
    'cpp': {'ext': 'cpp', 'bin': ['g++', 'clang++'], 'label': 'C++'},
    'java': {'ext': 'java', 'bin': ['javac'], 'label': 'Java'},
    'python': {'ext': 'py', 'bin': ['python', 'python3', 'py'], 'label': 'Python'},
    'javascript': {'ext': 'js', 'bin': None, 'label': 'JavaScript'},
}

IS_WINDOWS = WINDOWS


# ==================== 项目内置工具链 ====================
# 为什么要有这一层：原来的探测完全依赖「用户机器上装过什么」，换台电脑就可能点不动运行按钮。
# 内置一份工具链后，探测顺序固定为「内置 → 环境变量 → PATH → 常见安装目录 → 受限扫描」，
# 与在线判题站把编译器装在自己服务器上是同一个思路：运行环境由平台提供，不由访客决定。
#
# 目录约定（可通过 CSVISUAL_RUNTIME 覆盖）：
#   runtime/c-cpp/bin/{gcc,g++}.exe         C / C++
#   runtime/java/bin/javac.exe              Java（jlink 裁剪过的私有运行时）
#   runtime/python/python.exe               Python
#   runtime/node/node.exe                   Node（JavaScript）
# 该目录由 tools/setup_runtime.py 生成，可以不存在 —— 不存在时自动退回原有探测逻辑。

def _repo_root():
    """server-py/app/routers/code.py → 仓库根目录"""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(os.path.dirname(here)))


def runtime_dirs():
    """按优先级返回可能存放内置工具链的目录"""
    out = []
    env_dir = os.getenv('CSVISUAL_RUNTIME')
    if env_dir:
        out.append(os.path.abspath(env_dir))
    out.append(os.path.join(_repo_root(), 'runtime'))
    out.append(os.path.join(_repo_root(), 'server-py', 'runtime'))
    seen, uniq = set(), []
    for d in out:
        if d not in seen:
            seen.add(d)
            uniq.append(d)
    return uniq


def bundled_bin(*rel_parts):
    """在内置工具链目录里定位一个可执行文件，未部署则返回 None"""
    parts = list(rel_parts)
    if IS_WINDOWS and not parts[-1].lower().endswith(('.exe', '.bat', '.cmd')):
        parts[-1] += '.exe'
    for d in runtime_dirs():
        p = os.path.join(d, *parts)
        if os.path.exists(p):
            return p
    return None


def is_bundled(path):
    """判断某个可执行文件是否来自内置工具链（用于在 /code/env 里如实标注来源）"""
    if not path:
        return False
    target = os.path.normcase(os.path.abspath(path))
    for d in runtime_dirs():
        if not os.path.isdir(d):
            continue
        root = os.path.normcase(os.path.abspath(d)) + os.sep
        if target.startswith(root):
            return True
    return False


# ==================== 工具 ====================
def ensure_dir(d):
    os.makedirs(d, exist_ok=True)


def cleanup(d):
    try:
        shutil.rmtree(d, ignore_errors=True)
    except Exception:
        pass


def truncate(s):
    text = str(s or '')
    return text[:MAX_OUT] + '\n...（输出过长已截断）' if len(text) > MAX_OUT else text


def decode_smart(raw):
    """与 Node 版 decodeSmart 同构：子进程输出的编码不随机器漂移。
    先按 UTF-8 严格试解（绝大多数情况）；出现替换符再按 GBK 试解一次；
    都不干净才退回 UTF-8 宽容解。顺序不能反 —— GBK 中文按 UTF-8 解几乎必然
    产生替换符，而反方向的误解往往「合法但错误」，没有信号可判。"""
    if raw is None:
        return ''
    if isinstance(raw, str):
        return raw
    try:
        out = raw.decode('utf-8')
        if '\ufffd' not in out:
            return out
    except UnicodeDecodeError:
        pass
    try:
        out = raw.decode('gbk')
        if '\ufffd' not in out:
            return out
    except (UnicodeDecodeError, LookupError):
        pass
    return raw.decode('utf-8', 'ignore')


def utf8_env():
    """强制子进程用 UTF-8 说话（与 Node 版 utf8Env 同构）：
    Python 3.7+ 靠 PYTHONUTF8=1 把 print 的管道编码从本地 ANSI 掰成 UTF-8；
    Java 侧由调用点拼 -Dstdout.encoding / -Dfile.encoding 双属性。"""
    env = dict(os.environ)
    env['PYTHONUTF8'] = '1'
    env['PYTHONIOENCODING'] = 'utf-8'
    return env


JAVA_UTF8_ARGS = ['-Dfile.encoding=UTF-8', '-Dstdout.encoding=UTF-8', '-Dstderr.encoding=UTF-8']

# Windows 上杀软常把刚写出的 exe/py 锁一小会儿，spawn 直接 EBUSY/EPERM，
# 等一拍重试一次大多就能过 —— 用户不该看到莫名其妙的「运行失败（EBUSY）」
# winerror/errno 意义上的瞬时失败：5=ERROR_ACCESS_DENIED，13=EACCES，16=EBUSY，
# 32=ERROR_SHARING_VIOLATION —— 杀软扫描新写出的文件时最常见
_TRANSIENT_SPAWN = {5, 13, 16, 32}


def run(cmd, args, opts=None):
    """等价于 Node 版 exec()：把「子进程根本没起来」的信息透传出来，
    否则前端只看到"失败"二字，无从排查（受限环境常见 EBUSY/EPERM）。"""
    opts = opts or {}
    timeout = (opts.get('timeout') or TIMEOUT) / 1000.0

    # stdin 必须编码成 bytes：subprocess 的管道默认是二进制模式，
    # 直接传 str 会让内部的写入线程抛 TypeError 后静默死掉，
    # 结果子进程的 stdin 永远不会关闭 —— 凡是读输入的程序（判题必读）都会卡到超时。
    # 不用 text=True 是刻意的：文本模式在 Windows 上会把 \n 翻译成 \r\n，
    # 判题是逐字符比对输出，任何换行转换都会造成误判。
    raw_stdin = opts.get('stdin') or ''
    if not isinstance(raw_stdin, bytes):
        raw_stdin = str(raw_stdin).encode('utf-8')

    def _run():
        return subprocess.run(
            [cmd] + list(args),
            input=raw_stdin,
            timeout=timeout,
            cwd=opts.get('cwd'),
            env=opts.get('env'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=0x08000000 if IS_WINDOWS else 0,  # CREATE_NO_WINDOW
        )

    try:
        try:
            proc = _run()
        except OSError as e:
            code = getattr(e, 'winerror', None) or getattr(e, 'errno', None)
            if code in _TRANSIENT_SPAWN:
                time.sleep(0.3)
                proc = _run()
            else:
                raise
        out = decode_smart(proc.stdout)
        err = decode_smart(proc.stderr)
        return {'status': proc.returncode, 'stdout': out, 'stderr': err, 'spawnError': None}
    except subprocess.TimeoutExpired as e:
        out = decode_smart(e.stdout)
        err = decode_smart(e.stderr)
        return {
            'status': -1,
            'stdout': out,
            'stderr': err,
            'spawnError': f'执行超时（{int((opts.get("timeout") or TIMEOUT) / 1000)}s），可能存在死循环或等待输入。',
        }
    except OSError as e:
        # 命令不存在 / 环境禁止创建进程（EBUSY/EPERM）
        return {
            'status': None,
            'stdout': '',
            'stderr': '',
            'spawnError': f'无法启动运行环境（{getattr(e, "winerror", None) or getattr(e, "errno", None) or e}）。'
                          '常见原因与解决办法：\n'
                          '1. 杀毒软件/安全软件正在短暂占用编译器 —— 等 1 分钟重试即可；\n'
                          '2. 后端不是通过 start.bat 启动的（例如由开发工具拉起，继承了受限环境）—— '
                          '请关闭当前后端，回到项目根目录双击 start.bat 重新启动。',
        }


def has_bin(cmd):
    """命令是否可用（只探测能否启动，不判断版本）"""
    if os.path.dirname(cmd):
        return os.path.exists(cmd)
    r = run(cmd, ['--version'], {'timeout': 3000})
    return r['spawnError'] is None


def scan_subdirs(root, rel):
    """扫描目录下的所有子目录，找出第一个存在的 rel 文件。

    Windows 上 Python / JDK / MinGW 常装在「带版本号的目录」里且不在 PATH 中，
    只查 PATH 会误判为"未安装"。
    """
    try:
        if not os.path.isdir(root):
            return None
        for name in os.listdir(root):
            p = os.path.join(root, name, rel)
            if os.path.isdir(os.path.join(root, name)) and os.path.exists(p):
                return p
    except OSError:
        pass
    return None


def find_python():
    """优先用内置解释器，其次是服务自身所在解释器（必然可用）"""
    bundled = bundled_bin('python', 'python')
    if bundled:
        return bundled
    exe = sys.executable
    if exe and os.path.exists(exe):
        return exe
    if os.getenv('PYTHON_PATH') and os.path.exists(os.getenv('PYTHON_PATH')):
        return os.getenv('PYTHON_PATH')
    for cmd in ['python', 'python3', 'py']:
        if has_bin(cmd):
            return cmd
    home = os.path.expanduser('~')
    roots = [
        os.path.join(home, 'AppData', 'Local', 'Programs', 'Python'),
        os.path.join(home, '.workbuddy', 'binaries', 'python', 'versions'),
        'C:\\Python313', 'C:\\Python312', 'C:\\Python311',
    ]
    for r in roots:
        p = scan_subdirs(r, 'python.exe')
        if p:
            return p
        if os.path.isfile(r):
            return r
    return None


def find_node():
    """JavaScript 需要 node 运行时"""
    bundled = bundled_bin('node', 'node')
    if bundled:
        return bundled
    if os.getenv('NODE_PATH_BIN') and os.path.exists(os.getenv('NODE_PATH_BIN')):
        return os.getenv('NODE_PATH_BIN')
    found = shutil.which('node')
    if found:
        return found
    for cand in [r'C:\Program Files\nodejs\node.exe',
                 os.path.join(os.path.expanduser('~'), '.workbuddy', 'binaries', 'node', 'versions')]:
        if os.path.exists(cand) and os.path.isfile(cand):
            return cand
        sub = scan_subdirs(cand, os.path.join('bin', 'node.exe')) or scan_subdirs(cand, 'node.exe')
        if sub:
            return sub
    return None


def find_jdk():
    """JDK：返回 { javac, java }，二者需成对出现"""
    # 内置优先：jlink 裁剪过的私有运行时，只含 javac + java，不污染也不依赖用户环境
    bjavac = bundled_bin('java', 'bin', 'javac')
    if bjavac:
        bjava = bundled_bin('java', 'bin', 'java')
        if bjava:
            return {'javac': bjavac, 'java': bjava}

    home = os.path.expanduser('~')
    dirs = []
    if os.getenv('JAVA_HOME'):
        dirs.append(os.path.join(os.getenv('JAVA_HOME'), 'bin'))
    dirs += [
        os.path.join(home, '.workbuddy', 'binaries', 'java'),
        'C:\\Program Files\\Java',
        'C:\\Program Files\\Eclipse Adoptium',
        'C:\\Program Files\\Microsoft',
        'C:\\Program Files\\BellSoft',
        'C:\\Program Files\\Amazon Corretto',
    ]
    exe_name = 'javac.exe' if IS_WINDOWS else 'javac'
    for d in dirs:
        javac = scan_subdirs(d, os.path.join('bin', exe_name))
        if not javac and os.path.exists(os.path.join(d, exe_name)):
            javac = os.path.join(d, exe_name)
        if javac:
            java = os.path.join(os.path.dirname(javac), 'java.exe' if IS_WINDOWS else 'java')
            return {'javac': javac, 'java': java if os.path.exists(java) else 'java'}
    if has_bin('javac'):
        return {'javac': 'javac', 'java': 'java'}
    return None


def deep_find(file_name, roots, max_depth=6, max_results=15):
    """深度查找编译器可执行文件。

    只深入名字里带 mingw/llvm/gcc/clang/tdm/dev-cpp/winlibs/msys/bin 的目录，
    避免在 Program Files 这类大目录上做无谓的全量遍历。
    """
    import re as _re

    hint = _re.compile(r'(mingw|llvm|gcc|clang|tdm|dev-?cpp|winlibs|msys|codeblocks|^bin$)', _re.I)
    lower = file_name.lower()
    out = []

    def walk(directory, depth):
        if depth > max_depth or len(out) >= max_results:
            return
        try:
            entries = os.listdir(directory)
        except OSError:
            return
        for name in entries:
            if len(out) >= max_results:
                return
            p = os.path.join(directory, name)
            if os.path.isfile(p):
                if name.lower() == lower:
                    out.append(p)
            elif os.path.isdir(p) and (depth < 2 or hint.search(name)):
                walk(p, depth + 1)

    for r in roots:
        walk(r, 0)
    return out


def collect_compiler_candidates(bin_name):
    """收集 C/C++ 编译器的全部候选路径（内置 → 环境变量 → PATH → 常见安装位 → 深度扫描）"""
    lst = []
    seen = set()

    def push(p):
        if p and p not in seen:
            seen.add(p)
            lst.append(p)

    # 内置工具链排在第一位：只要部署过，任何机器上都用同一份编译器
    for rel in [('c-cpp', 'bin'),
                ('c-cpp', 'mingw64', 'bin'),
                ('c-cpp', 'x86_64-w64-mingw32', 'bin'),
                ('c-cpp', 'ucrt64', 'bin')]:
        push(bundled_bin(*rel, bin_name))

    if os.getenv('CC_PATH'):
        push(os.getenv('CC_PATH'))
    if os.getenv('CXX_PATH'):
        push(os.getenv('CXX_PATH'))

    push(bin_name)

    home = os.path.expanduser('~')
    roots = [
        'C:\\msys64\\mingw64\\bin', 'C:\\msys64\\ucrt64\\bin', 'C:\\msys64\\clang64\\bin',
        'C:\\mingw64\\bin', 'C:\\MinGW\\bin', 'C:\\TDM-GCC-64\\bin',
        'C:\\Program Files\\mingw-w64', 'C:\\Program Files\\LLVM\\bin',
        'C:\\Program Files\\CodeBlocks\\MinGW\\bin',
        os.path.join(home, 'scoop', 'apps'),
        os.path.join(home, '.workbuddy', 'binaries', 'mingw64', 'bin'),
    ]
    for r in roots:
        push(os.path.join(r, bin_name + ('.exe' if IS_WINDOWS else '')))
        sub = scan_subdirs(r, os.path.join('bin', bin_name + ('.exe' if IS_WINDOWS else '')))
        if sub:
            push(sub)

    deep_roots = [
        os.path.join(home, 'AppData', 'Local', 'Microsoft', 'WinGet', 'Packages'),
        'C:\\Program Files', 'C:\\Program Files (x86)', 'C:\\Qt',
        'D:\\Develop', 'D:\\Program Files', 'D:\\',
    ]
    for p in deep_find(bin_name + ('.exe' if IS_WINDOWS else ''), deep_roots):
        push(p)
    return lst


def with_bin_dir(bin_path):
    """把编译器所在目录加进 PATH，保证生成的 .exe 能找到运行时 DLL"""
    env = os.environ.copy()
    if os.path.dirname(bin_path):
        sep = ';' if IS_WINDOWS else ':'
        env['PATH'] = os.path.dirname(bin_path) + sep + env.get('PATH', '')
    return env


_probe_cache = {}


def verify_compiler(bin_path, lang):
    """真实编译 + 运行一个 hello world，验证编译器「真的能用」。

    机器上可能存在被卸载残留、缺少运行时、或版本过旧的编译器
    （例如 Dev-C++ 自带的 gcc 4.8.1 在现代环境下会静默失败），
    只判断"文件存在"会误报可用，用户点了运行却拿到空输出，无从排查。
    """
    key = lang + '|' + bin_path
    if key in _probe_cache:
        return _probe_cache[key]

    import random
    d = os.path.join(RUN_ROOT, 'probe-' + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6)))
    ensure_dir(d)
    res = {'ok': False, 'reason': ''}
    env_path = with_bin_dir(bin_path)
    try:
        ext = 'cpp' if lang == 'cpp' else 'c'
        src = os.path.join(d, 'probe.' + ext)
        exe = os.path.join(d, 'probe.exe' if IS_WINDOWS else 'probe')
        with open(src, 'w', encoding='utf-8') as f:
            if lang == 'cpp':
                f.write('#include <iostream>\n#include <vector>\nint main(){std::vector<int> v{1,2};std::cout<<"ok"<<v.size();}\n')
            else:
                f.write('#include <stdio.h>\nint main(){printf("ok%d", 1);return 0;}\n')
        args = [src, '-o', exe, '-std=c++17'] if lang == 'cpp' else [src, '-o', exe]
        c = run(bin_path, args, {'timeout': 25000, 'cwd': d, 'env': env_path})
        if c['spawnError']:
            res = {'ok': False, 'reason': '无法启动编译器（' + str(c['spawnError']).split('（')[0].strip('。') + '）'}
        elif c['status'] != 0:
            first = (c['stderr'] or '').split('\n')[0][:100]
            res = {'ok': False, 'reason': '编译失败：' + first}
        else:
            r = run(exe, [], {'timeout': 10000, 'cwd': d, 'env': env_path})
            if r['spawnError']:
                res = {'ok': False, 'reason': '可执行文件无法启动（' + str(r['spawnError']).split('（')[0].strip('。') + '）'}
            elif r['status'] != 0:
                res = {'ok': False, 'reason': '运行失败：' + (r['stderr'] or '').split('\n')[0][:100]}
            elif 'ok' not in (r['stdout'] or ''):
                res = {'ok': False, 'reason': '运行输出异常（可能缺少运行时库）'}
            else:
                res = {'ok': True}
    except Exception as e:
        res = {'ok': False, 'reason': str(e)}
    finally:
        cleanup(d)

    _probe_cache[key] = res
    return res


def find_compiler(lang):
    """找出第一个「能真正编译并运行」的 C/C++ 编译器"""
    names = ['g++', 'clang++', 'c++'] if lang == 'cpp' else ['gcc', 'clang', 'cc']
    tried = []
    fallback = None
    for n in names:
        for p in collect_compiler_candidates(n):
            if os.path.dirname(p) == '':
                if not has_bin(p):
                    continue
            elif not os.path.exists(p):
                continue
            v = verify_compiler(p, lang)
            if v['ok']:
                return {'bin': p, 'tried': tried}
            tried.append(p + ' → ' + v.get('reason', ''))
            # 受限环境禁止创建子进程（EBUSY/EPERM）时无从验证，
            # 退化为「文件存在即视为可用」，避免把装好的编译器误判成没装
            if not fallback and ('无法启动编译器' in v.get('reason', '') or '可执行文件无法启动' in v.get('reason', '')):
                fallback = p
    return {'bin': fallback, 'tried': tried, 'probeSkipped': bool(fallback)}


_cache = {'env': None, 'at': 0}


# ==================== 内置工具链自愈部署（与 Node 版同构） ====================
# 后端一旦探测到编译器缺失，自动在后台拉起部署脚本（--ensure --auto 无人值守）。
# 进程内只触发一次 + 跨进程用 tools/.runtime-deploying 标记（30 分钟内不叠加）。
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
_deploy_lock = os.path.join(_REPO_ROOT, 'tools', '.runtime-deploying')
_deploy_log = os.path.join(_REPO_ROOT, 'tools', 'runtime-deploy.log')
_deploy_state = {'running': False, 'at': 0.0}


def _trigger_runtime_deploy():
    if _deploy_state['running']:
        return True
    try:
        if os.path.exists(_deploy_lock) and time.time() - os.path.getmtime(_deploy_lock) < 30 * 60:
            _deploy_state['running'] = True
            _deploy_state['at'] = time.time()
            return True
    except OSError:
        pass
    script = os.path.join(_REPO_ROOT, 'tools', 'setup_runtime.py')
    if not os.path.exists(script):
        return False
    py = find_python()
    if not py:
        return False
    try:
        with open(_deploy_lock, 'w') as f:
            f.write(str(int(time.time() * 1000)))
    except OSError:
        pass
    try:
        logf = open(_deploy_log, 'a', encoding='utf-8', errors='replace')
        kwargs = {}
        if IS_WINDOWS:
            kwargs['creationflags'] = 0x00000008 | 0x08000000  # DETACHED_PROCESS | CREATE_NO_WINDOW
        subprocess.Popen(
            [py, script, '--ensure', '--auto'],
            stdin=subprocess.DEVNULL, stdout=logf, stderr=logf,
            cwd=_REPO_ROOT, env=utf8_env(), **kwargs,
        )
        logf.close()
    except OSError:
        return False
    _deploy_state['running'] = True
    _deploy_state['at'] = time.time()
    return True


def _deploy_in_progress():
    if _deploy_state['running']:
        return time.time() - _deploy_state['at'] < 30 * 60
    try:
        return os.path.exists(_deploy_lock) and time.time() - os.path.getmtime(_deploy_lock) < 30 * 60
    except OSError:
        return False


def _missing_hint(lang, tried=None):
    """环境缺失时给出「下一步怎么做」，而不是只丢一句不可用。
    缺失即自愈：顺手拉起后台部署；起不来（没 Python 等）就退回手动指引。"""
    _trigger_runtime_deploy()
    if _deploy_in_progress():
        base = (f"未检测到 {LANGS[lang]['label']} 运行环境。系统已开始自动部署内置工具链"
                '（首次需联网下载约 64MB，通常 1~3 分钟），部署完成后无需重启，再次点击「运行」即可。\n'
                '也可以手动双击 tools\\setup-runtime.bat，部署进度见 tools\\runtime-deploy.log。')
    else:
        base = (f"未检测到 {LANGS[lang]['label']} 运行环境，无法在线执行。\n"
                '可在项目根目录双击 tools\\setup-runtime.bat 部署内置工具链 —— '
                '部署一次之后，任何用户、任何机器都无需再自行安装编译器。')
    # 具体失败原因在两种分支下都要带出来：用户看到「gcc.exe → 编译失败」时，
    # 最需要的就是那一行，而部署提示只是告诉他下一步怎么办，不能把它盖掉。
    if tried:
        base += '\n已尝试但不可用：' + '；'.join(str(t) for t in tried[:2])
    return base


def detect_env():
    now = time.time()
    if _cache['env'] and (now - _cache['at']) < 60:
        return _cache['env']

    env = {}
    for lang in LANGS:
        if lang == 'javascript':
            node = find_node()
            version = ''
            if node:
                r = run(node, ['--version'], {'timeout': 3000})
                version = (r['stdout'] or '').strip()
            env[lang] = {
                'available': bool(node),
                'bin': node or 'node',
                'version': version or None,
                'source': 'bundled' if is_bundled(node) else ('system' if node else None),
                'hint': '' if node else _missing_hint(lang),
            }
            continue

        if lang == 'c' or lang == 'cpp':
            r = find_compiler(lang)
            bin_path = r['bin']
            env[lang] = {
                'available': bool(bin_path),
                'bin': bin_path or LANGS[lang]['bin'][0],
                'source': 'bundled' if is_bundled(bin_path) else ('system' if bin_path else None),
                'hint': '' if bin_path else _missing_hint(lang, r.get('tried')),
            }
            continue

        # java / python 的探测函数自带「内置优先」，必须排在 PATH 探测之前 ——
        # 否则系统 PATH 里那个 javac 会先被命中，内置运行时永远轮不上。
        if lang == 'java':
            jdk = find_jdk()
            if jdk:
                env['java'] = {
                    'available': True,
                    'bin': jdk['javac'],
                    'javaBin': jdk['java'],
                    'source': 'bundled' if is_bundled(jdk['javac']) else 'system',
                }
                continue
        if lang == 'python':
            exe = find_python()
            if exe:
                env['python'] = {
                    'available': True,
                    'bin': exe,
                    'source': 'bundled' if is_bundled(exe) else 'system',
                }
                continue

        bin_path = None
        for b in LANGS[lang]['bin']:
            if has_bin(b):
                bin_path = b
                break
        env[lang] = {
            'available': bool(bin_path),
            'bin': bin_path or LANGS[lang]['bin'][0],
            'source': 'bundled' if is_bundled(bin_path) else ('system' if bin_path else None),
            'hint': '' if bin_path else _missing_hint(lang),
        }

    _cache['env'] = env
    _cache['at'] = now
    return env


# ==================== 限流 ====================
_hits = {}
_hits_lock = threading.Lock()


def throttle(uid):
    now = time.time()
    with _hits_lock:
        arr = [t for t in _hits.get(uid, []) if now - t < 60]
        arr.append(now)
        _hits[uid] = arr
        return len(arr) > 30


# ==================== 接口 ====================
@router.get('/env')
def code_env(user: dict = Depends(current_user)):
    return ok(detect_env())


def execute(lang: str, code: str, uid, stdin: str = ''):
    """真正跑一段代码（不含鉴权与限流），返回 {output, error, stderr, time}。

    抽出成独立函数是为了让 Agent 的 code_run 工具也能复用同一套编译/执行逻辑，
    避免「在线运行」与「助手帮你跑」两条链路行为不一致（两处各写一份迟早分叉）。

    stdin：运行前预先喂给程序的标准输入。在线运行一次请求跑完，没法像真终端
    那样中途等人敲键盘，而这个函数原来是**完全不传 stdin** 的 —— 子进程管道空着
    立刻 EOF，scanf / input() / Scanner 一类读输入的程序必然拿到空数据或直接报错。
    """
    import random

    # 末尾补换行 = 手工敲的那个回车；没这个尾巴，C 的 scanf("%d") 有时读不到最后一个数
    if stdin and not stdin.endswith('\n'):
        stdin += '\n'
    has_stdin = bool(stdin and stdin.strip())

    env = detect_env()
    if not env[lang]['available']:
        # 本机没有该语言环境 → 先试云端沙箱兜底，跑不动再把自救指引还给用户
        rr = remote_run(lang, code, stdin)
        if rr['ok']:
            return _cloud(rr, 0)
        return {
            'output': '',
            'error': True,
            # 与 /code/env 复用同一份提示，避免两处文案各说各话
            'stderr': _missing_hint(lang) + '\n\n云端兜底也失败：' + rr['reason']
                      + stdin_hint(code, has_stdin, True, ''),
            'time': 0,
            'unsupported': True,
        }

    # 云端兜底结果统一在这里成型：四个接入点只是时机不同，结构必须一致；
    # hint 也要接上——「云端跑挂了其实是因为没给输入」最难排查，别漏掉这句提示。
    def _cloud(rr, elapsed):
        rr_out = str(rr.get('stdout') or '')
        return {
            'output': truncate(rr_out),
            'stderr': NOTICE + truncate(str(rr.get('stderr') or ''))
                      + stdin_hint(code, has_stdin, rr.get('exitCode') != 0, rr_out),
            'error': rr.get('exitCode') != 0,
            'time': elapsed,
            'remote': True,
        }

    d = os.path.join(RUN_ROOT, f"{uid}-{int(time.time() * 1000)}-"
                               f"{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))}")
    ensure_dir(d)
    t0 = int(time.time() * 1000)

    try:
        out = ''
        err = ''
        failed = False

        if lang in ('javascript', 'python'):
            file_path = os.path.join(d, f"main.{LANGS[lang]['ext']}")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            if lang == 'python':
                # -X utf8 + PYTHONUTF8：print 输出强制 UTF-8，不随机器 ANSI 代码页漂移
                r = run(env[lang]['bin'], ['-X', 'utf8', file_path],
                        {'cwd': d, 'env': utf8_env(), 'stdin': stdin})
            else:
                r = run(env[lang]['bin'], [file_path], {'cwd': d, 'stdin': stdin})
            out = r['stdout'] or ''
            err = r['spawnError'] or r['stderr'] or ''
            failed = r['status'] != 0 or bool(r['spawnError'])
        elif lang in ('c', 'cpp'):
            src = os.path.join(d, f"main.{LANGS[lang]['ext']}")
            with open(src, 'w', encoding='utf-8') as f:
                f.write(code)
            exe = os.path.join(d, 'main.exe' if IS_WINDOWS else 'main')
            args = [src, '-o', exe, '-std=c++17'] if lang == 'cpp' else [src, '-o', exe]
            run_env = with_bin_dir(env[lang]['bin'])
            c = run(env[lang]['bin'], args, {'timeout': 15000, 'cwd': d, 'env': run_env})
            if c['status'] != 0:
                # 编译器本身拉不起来（EBUSY/受限环境）→ 云端兜底；真编译错误照常返回
                if c['spawnError'] and is_env_error(c['spawnError']):
                    rr = remote_run(lang, code, stdin)
                    if rr['ok']:
                        return _cloud(rr, int(time.time() * 1000) - t0)
                return {
                    'output': '',
                    'error': True,
                    'stderr': '编译失败：\n' + truncate(c['spawnError'] or c['stderr'] or ''),
                    'time': int(time.time() * 1000) - t0,
                }
            r = run(exe, [], {'cwd': d, 'env': run_env, 'stdin': stdin})
            out = r['stdout'] or ''
            err = r['spawnError'] or r['stderr'] or ''
            failed = r['status'] != 0 or bool(r['spawnError'])
        elif lang == 'java':
            import re as _re

            cls_match = _re.search(r'public\s+class\s+([A-Za-z_]\w*)', code)
            cls = cls_match.group(1) if cls_match else None
            src_text = code
            if cls and cls != 'Main':
                src_text = _re.sub(r'\b' + cls + r'\b', 'Main', code)
            file_path = os.path.join(d, 'Main.java')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(src_text)
            javac = (env['java'].get('bin') if env.get('java') else None) or 'javac'
            java_bin = (env['java'].get('javaBin') if env.get('java') else None) or 'java'
            c = run(javac, ['-encoding', 'UTF-8', file_path], {'timeout': 15000, 'cwd': d})
            if c['status'] != 0:
                if c['spawnError'] and is_env_error(c['spawnError']):
                    rr = remote_run(lang, code, stdin)
                    if rr['ok']:
                        return _cloud(rr, int(time.time() * 1000) - t0)
                return {
                    'output': '',
                    'error': True,
                    'stderr': '编译失败：\n' + truncate(c['spawnError'] or c['stderr'] or ''),
                    'time': int(time.time() * 1000) - t0,
                }
            r = run(java_bin, JAVA_UTF8_ARGS + ['-cp', d, 'Main'],
                    {'cwd': d, 'env': utf8_env(), 'stdin': stdin})
            out = r['stdout'] or ''
            err = r['spawnError'] or r['stderr'] or ''
            failed = r['status'] != 0 or bool(r['spawnError'])
        else:  # pragma: no cover - 语言白名单已保证不会出现
            out, err, failed = '', '不支持的语言', True

        # 云端兜底：本机子进程拉不起来（EBUSY/受限环境/杀软占用）时，
        # 把同一份代码交给云端沙箱执行 —— 结果是真实执行结果，不是伪造的
        if failed and not out and is_env_error(err):
            rr = remote_run(lang, code, stdin)
            if rr['ok']:
                return _cloud(rr, int(time.time() * 1000) - t0)
            err += '\n\n云端兜底也失败：' + rr['reason']

        return {
            'output': truncate(out),
            'stderr': truncate(err) + stdin_hint(code, has_stdin, failed, out),
            'error': failed,
            'time': int(time.time() * 1000) - t0,
        }
    except Exception as e:
        return {
            'output': '',
            'error': True,
            'stderr': '运行异常：' + str(e),
            'time': int(time.time() * 1000) - t0,
        }
    finally:
        cleanup(d)
@router.post('/run')
def run_code(request: Request, user: dict = Depends(current_user)):
    body = body_of(request)
    language = body.get('language')
    code = body.get('code')
    lang = str(language or '').lower()
    # 用户在「程序输入（stdin）」框里写的内容，随代码一起提交，运行前喂给程序
    raw_stdin = body.get('stdin')
    stdin = raw_stdin if isinstance(raw_stdin, str) else ''

    if os.getenv('CODE_RUN') == '0':
        return fail(403, '在线运行功能已由管理员关闭')
    if lang not in LANGS:
        return fail(400, f"不支持的语言：{language or '(空)'}，可选 {' / '.join(LANGS.keys())}")
    if not isinstance(code, str) or not code.strip():
        return fail(400, '代码不能为空')
    if len(code) > MAX_CODE:
        return fail(400, f'代码过长（上限 {MAX_CODE} 字符）')
    if len(stdin) > MAX_STDIN:
        return fail(400, f'输入内容过长（上限 {MAX_STDIN} 字符）')
    if throttle(user['id']):
        return fail(429, '运行过于频繁，请稍后再试（每分钟上限 30 次）')

    return ok(execute(lang, code, user['id'], stdin))
