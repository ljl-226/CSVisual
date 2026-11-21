#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CSVisual 内置工具链部署脚本

为什么要这个东西
----------------
原来在线运行依赖「用户机器上装过什么编译器」：换台电脑、或者朋友拿到压缩包解压，
点运行就只看到一句「本机未检测到 C 运行环境」。在线判题站（洛谷、Codeforces 之类）
不存在这个问题，因为编译器装在平台自己那边。

本脚本把编译器装进项目自身的 runtime/ 目录，让运行环境由项目提供、而不是由访客决定。
部署一次之后，任何人拿到这个项目、无论电脑上有没有装过 gcc/JDK，点运行都能出结果。

部署产物
--------
    runtime/c-cpp/bin/gcc.exe      C / C++（w64devkit，已裁剪掉 Fortran/cmake/vim/32 位库）
    runtime/java/bin/javac.exe     Java（由 JDK 用 jlink 裁剪出的私有运行时）
    runtime/python/python.exe      Python（可选；服务自身就是 Python，通常不必部署）
    runtime/node/node.exe          Node（可选；前端本身就需要 Node，通常不必部署）
    runtime/.manifest.json         部署清单（来源、版本、体积、验证结果）

用法（在项目根目录执行）
------------------------
    python tools/setup_runtime.py                 自动：下载官方便携包，联网失败才用本机已装
    python tools/setup_runtime.py --lang c,cpp    只准备指定语言
    python tools/setup_runtime.py --from-local    只用本机已装的工具链，全程不联网
    python tools/setup_runtime.py --download      跳过本机，直接下载官方便携包
    python tools/setup_runtime.py --archive X     用已下载好的 C/C++ 压缩包（离线部署）
    python tools/setup_runtime.py --verify        部署后逐语言真实编译运行验证
    python tools/setup_runtime.py --info          只看当前状态，不做任何改动
    python tools/setup_runtime.py --clean         删除已部署的内置工具链
    python tools/setup_runtime.py --ensure        启动前的就绪检查（启动脚本会调它）

脚本只用标准库，不依赖 pip 装任何东西 —— 否则「部署工具链」本身又变成一个环境依赖。

关于 tools/ 下的 .bat：它们刻意只写 ASCII。cmd.exe 解析批处理时按当前代码页逐字节读取，
UTF-8 中文遇上 chcp 切换会让行边界错位，把注释行当成命令执行。
所以中文提示一律由本脚本输出，批处理只负责找到 Python 并把参数原样传进来。
"""

import argparse
import fnmatch
import glob
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.request
import zipfile

if sys.version_info < (3, 7):  # pragma: no cover
    sys.exit('需要 Python 3.7 及以上版本')

# 输出被重定向到文件/管道时，中文可能撞上非 UTF-8 的代码页而抛 UnicodeEncodeError。
# 这里只是不让它崩：真正给用户看的提示宁可少一个字，也不该把整个部署打断。
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(errors='replace')
    except Exception:  # pragma: no cover - 老解释器没有 reconfigure
        pass

IS_WINDOWS = os.name == 'nt'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNTIME = os.path.join(ROOT, 'runtime')
MANIFEST = os.path.join(RUNTIME, '.manifest.json')

LANGS = ['c', 'cpp', 'java', 'python', 'node']
# c 与 cpp 共用同一个包（同一个 gcc 发行版同时提供两者）
PKG_OF = {'c': 'c-cpp', 'cpp': 'c-cpp', 'java': 'java', 'python': 'python', 'node': 'node'}

# GitHub 资源在国内经常被代理掐断，按顺序试加速镜像，哪个通用哪个
GH_MIRRORS = [
    'https://gh-proxy.com/',
    'https://ghfast.top/',
    'https://ghproxy.net/',
    '',
]

W64DEVKIT_TAG = 'v2.10.0'
W64DEVKIT_ASSET = 'w64devkit-x64-2.10.0.7z.exe'
W64DEVKIT_URL = ('https://github.com/skeeto/w64devkit/releases/download/%s/%s'
                 % (W64DEVKIT_TAG, W64DEVKIT_ASSET))

PY_URL = 'https://www.python.org/ftp/python/3.12.10/python-3.12.10-embed-amd64.zip'
PY_FALLBACKS = [
    'https://www.python.org/ftp/python/3.12.7/python-3.12.7-embed-amd64.zip',
    'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip',
]

ADOPTIUM_URL = ('https://api.adoptium.net/v3/binary/latest/{v}/ga/windows/x64/jdk/hotspot/'
                'normal/eclipse?project=jdk')

NODE_URL = 'https://nodejs.org/dist/v22.11.0/node-v22.11.0-win-x64.zip'

# 编译单个 C/C++ 源文件用不到、但很占体积的东西。
# 同时适配 w64devkit 与 LLVM-MinGW 两种发行版（后者多出各架构目录）。
DROP_DIRS = [
    'lib32',                     # 32 位运行库，x86_64 用不到
    'share',                     # vim / cmake / nsis 的文档与数据
    'src', 'etc',                # 自带源码与配置
    'Dockerfile', 'w64devkit.exe', 'w64devkit.ini',
    'aarch64-w64-mingw32', 'armv7-w64-mingw32', 'arm64ec-w64-mingw32', 'i686-w64-mingw32',
    'python', 'busybox',         # LLVM-MinGW 里附带的无关内容
]
DROP_BIN_GLOBS = [
    'cmake.exe', 'ccmake.exe', 'ctest.exe', 'cpack.exe', 'cmcldeps.exe', 'dcmake.exe',
    'gdb.exe', 'gdbserver.exe', 'gdb-add-index',
    'gfortran.exe',
    'clangd.exe', 'clang-tidy.exe', 'clang-format.exe', 'clang-apply-replacements.exe',
    'lldb.exe', 'lldb-server.exe', 'liblldb.dll', 'libpython*.dll',
    'ccache.exe', 'cppcheck.exe', 'ctags.exe', 'vim.exe', 'vimdiff.exe', 'xxd.exe',
    'git.exe', 'git-*.exe', 'busybox.exe', 'emacs*.exe', 'mg.exe', 'tcc.exe', 'sqlite3.exe',
]
DROP_NESTED_GLOBS = [
    'f951.exe',                  # Fortran 前端，约 39 MB
    'install-tools',
]


# ==================== 输出 ====================
class C:
    G = '\033[32m'
    Y = '\033[33m'
    R = '\033[31m'
    B = '\033[36m'
    D = '\033[90m'
    X = '\033[0m'


def _supports_color():
    if os.getenv('NO_COLOR'):
        return False
    if IS_WINDOWS:
        # 老版 cmd 需要先开启 VT 处理，失败就退回纯文本，别打出乱码
        try:
            import ctypes
            k = ctypes.windll.kernel32
            return bool(k.SetConsoleMode(k.GetStdHandle(-11), 7))
        except Exception:
            return False
    return sys.stdout.isatty()


if not _supports_color():
    for _n in ('G', 'Y', 'R', 'B', 'D', 'X'):
        setattr(C, _n, '')


def log(msg=''):
    print(msg, flush=True)


def step(msg):
    log('%s==>%s %s' % (C.B, C.X, msg))


def good(msg):
    log('  %s√%s %s' % (C.G, C.X, msg))


def warn(msg):
    log('  %s!%s %s' % (C.Y, C.X, msg))


def bad(msg):
    log('  %s×%s %s' % (C.R, C.X, msg))


def info(msg):
    log('  %s%s%s' % (C.D, msg, C.X))


# ==================== 通用工具 ====================
def human(n):
    n = float(n)
    for unit in ('B', 'KB', 'MB', 'GB'):
        if n < 1024 or unit == 'GB':
            return ('%d B' % n) if unit == 'B' else ('%.1f %s' % (n, unit))
        n /= 1024.0


def dir_size(path):
    total = 0
    for base, _dirs, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(base, f))
            except OSError:
                pass
    return total


def rm(path):
    if os.path.isdir(path) and not os.path.islink(path):
        shutil.rmtree(path, ignore_errors=True)
    elif os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass


def load_manifest():
    try:
        with open(MANIFEST, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def save_manifest(m):
    os.makedirs(RUNTIME, exist_ok=True)
    with open(MANIFEST, 'w', encoding='utf-8') as f:
        json.dump(m, f, ensure_ascii=False, indent=2)


def run(cmd, timeout=120, cwd=None):
    """同步执行，返回 (returncode, stdout, stderr)；进程起不来时 returncode 为 None"""
    try:
        p = subprocess.run(cmd, cwd=cwd, timeout=timeout,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        dec = lambda b: (b or b'').decode('utf-8', 'ignore')  # noqa: E731
        return p.returncode, dec(p.stdout), dec(p.stderr)
    except subprocess.TimeoutExpired:
        return -9, '', '超时'
    except OSError as e:
        return None, '', str(e)


def match_any(name, patterns):
    return any(fnmatch.fnmatch(name.lower(), p.lower()) for p in patterns)


# ==================== 下载 ====================
def fetch(url, dest, label=''):
    """带进度地下载，并校验长度完整"""
    req = urllib.request.Request(url, headers={'User-Agent': 'CSVisual-setup/1.0'})
    label = (label or os.path.basename(dest))[:12]
    with urllib.request.urlopen(req, timeout=60) as r:
        total = int(r.headers.get('Content-Length') or 0)
        got = 0
        t0 = time.time()
        with open(dest, 'wb') as f:
            while True:
                chunk = r.read(256 * 1024)
                if not chunk:
                    break
                f.write(chunk)
                got += len(chunk)
                speed = got / max(time.time() - t0, 0.01) / 1048576.0
                if total:
                    sys.stdout.write('\r  %-12s %3d%%  %s / %s  %.1f MB/s   '
                                     % (label, got * 100 // total, human(got), human(total), speed))
                else:
                    sys.stdout.write('\r  %-12s %s   %.1f MB/s   ' % (label, human(got), speed))
                sys.stdout.flush()
    sys.stdout.write('\r' + ' ' * 74 + '\r')
    sys.stdout.flush()
    if total and got < total:
        raise IOError('下载不完整：%s / %s' % (human(got), human(total)))
    return got


def _clear_line():
    sys.stdout.write('\r' + ' ' * 74 + '\r')
    sys.stdout.flush()


def download_github(url, dest, label=''):
    """GitHub 资源走加速镜像，逐个回退"""
    last = None
    for m in GH_MIRRORS:
        target = (m + url) if m else url
        name = ('镜像 ' + m.rstrip('/').replace('https://', '')) if m else '直连'
        try:
            fetch(target, dest, label or name)
            info('来源：%s' % name)
            return
        except Exception as e:
            last = e
            _clear_line()
            warn('%s 失败：%s' % (name, str(e)[:60]))
    raise RuntimeError('所有下载源都失败，最后错误：%s' % last)


def download_any(urls, dest, label=''):
    """普通站点逐条回退"""
    last = None
    for u in urls:
        try:
            fetch(u, dest, label)
            return u
        except Exception as e:
            last = e
            _clear_line()
            warn('%s 失败：%s' % (u, str(e)[:60]))
    raise RuntimeError('下载失败：%s' % last)


# ==================== 解压 ====================
def extract(archive, dest):
    """支持 zip / tar.* / 7z 自解压 exe；解完把多余的一层同名目录压平"""
    os.makedirs(dest, exist_ok=True)
    low = archive.lower()

    if low.endswith('.zip'):
        with zipfile.ZipFile(archive) as z:
            z.extractall(dest)
    elif low.endswith(('.tar.gz', '.tgz', '.tar.xz', '.tar.bz2', '.tar')):
        with tarfile.open(archive) as t:
            t.extractall(dest)
    elif low.endswith(('.7z.exe', '.exe')):
        # 7-Zip 自解压包：-y 覆盖不询问，-o 指定目录（路径不能带空格）
        rc, out, err = run([archive, '-y', '-o' + dest], timeout=900)
        if rc != 0:
            raise RuntimeError('7z 自解压失败（rc=%s）：%s' % (rc, (err or out)[:200]))
    elif low.endswith('.7z'):
        sevenzip = shutil.which('7z') or shutil.which('7za')
        if not sevenzip:
            raise RuntimeError('需要 7z 命令来解压 .7z，请改用官方 .zip 包')
        rc, out, err = run([sevenzip, 'x', '-y', '-o' + dest, archive], timeout=900)
        if rc != 0:
            raise RuntimeError('7z 解压失败：%s' % (err or out)[:200])
    else:
        raise RuntimeError('不支持的压缩格式：%s' % os.path.basename(archive))

    entries = [e for e in os.listdir(dest) if not e.startswith('.')]
    if len(entries) == 1 and os.path.isdir(os.path.join(dest, entries[0])):
        inner = os.path.join(dest, entries[0])
        tmp = dest + '.__flat'
        os.rename(inner, tmp)
        return tmp
    return dest


def toolchain_root(src):
    """定位工具链根目录（含 bin 的那一层）"""
    if os.path.isdir(os.path.join(src, 'bin')):
        return src
    kids = [k for k in os.listdir(src) if os.path.isdir(os.path.join(src, k))]
    if len(kids) == 1:
        sub = os.path.join(src, kids[0])
        if os.path.isdir(os.path.join(sub, 'bin')):
            return sub
    return src


# ==================== 复制（带裁剪）====================
def copy_pruned(src, dst, drop_dirs, drop_bin_globs, drop_nested_globs):
    """把工具链复制到 dst，剔除明显用不到的部分；返回被剔除的条目名列表"""
    os.makedirs(dst, exist_ok=True)
    dropped = []
    for entry in os.listdir(src):
        s = os.path.join(src, entry)
        if entry in drop_dirs:
            dropped.append(entry)
            continue
        if os.path.isdir(s):
            shutil.copytree(s, os.path.join(dst, entry), dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns(*drop_nested_globs))
        else:
            shutil.copy2(s, os.path.join(dst, entry))

    bindir = os.path.join(dst, 'bin')
    if os.path.isdir(bindir):
        for name in os.listdir(bindir):
            if match_any(name, drop_bin_globs):
                rm(os.path.join(bindir, name))
                dropped.append('bin/' + name)
    return dropped


# ==================== 真实可用性验证 ====================
def verify_lang(lang, verbose=False):
    """真的编译并运行一段最小程序。

    只判断「文件存在」会把残缺或版本过旧的工具链误判成可用
    （典型如 Dev-C++ 自带的 gcc 4.8.1），用户点了运行却拿到空输出。
    """
    d = tempfile.mkdtemp(prefix='csvisual-verify-')
    try:
        if lang in ('c', 'cpp'):
            gcc = os.path.join(RUNTIME, 'c-cpp', 'bin', 'g++.exe' if lang == 'cpp' else 'gcc.exe')
            if not os.path.exists(gcc):
                return False, '未找到 %s' % os.path.basename(gcc)
            src = os.path.join(d, 'main.' + ('cpp' if lang == 'cpp' else 'c'))
            exe = os.path.join(d, 'main.exe')
            code = ('#include <iostream>\n#include <vector>\n#include <string>\n'
                    'int main(){std::vector<std::string> v{"a","b"};'
                    'std::cout<<"CSV"<<v.size()<<std::endl;}\n') if lang == 'cpp' else \
                   ('#include <stdio.h>\n#include <stdlib.h>\n'
                    'int main(){int*p=(int*)malloc(sizeof(int)*4);p[3]=42;'
                    'printf("CSV%d\\n",p[3]);free(p);}\n')
            with open(src, 'w', encoding='utf-8') as f:
                f.write(code)
            args = [gcc, src, '-o', exe] + (['-std=c++17'] if lang == 'cpp' else [])
            rc, out, err = run(args, timeout=180, cwd=d)
            if rc != 0:
                return False, '编译失败：%s' % (err or out).strip().split('\n')[0][:120]
            rc, out, err = run([exe], timeout=30, cwd=d)
            if rc != 0:
                return False, '运行失败（可能缺运行时 DLL）：%s' % (err or out).strip()[:120]
            if 'CSV' not in out:
                return False, '输出异常：%r' % out[:60]
            return True, (out.strip() if verbose else '')

        if lang == 'java':
            javac = os.path.join(RUNTIME, 'java', 'bin', 'javac.exe')
            java = os.path.join(RUNTIME, 'java', 'bin', 'java.exe')
            if not (os.path.exists(javac) and os.path.exists(java)):
                return False, '未找到 javac/java'
            src = os.path.join(d, 'Main.java')
            with open(src, 'w', encoding='utf-8') as f:
                f.write('import java.util.*;\npublic class Main{public static void main(String[] a){'
                        'List<Integer> l=new ArrayList<>();l.add(7);'
                        'System.out.println("CSV"+l.size());}}\n')
            rc, out, err = run([javac, '-encoding', 'UTF-8', src], timeout=240, cwd=d)
            if rc != 0:
                return False, '编译失败：%s' % (err or out).strip().split('\n')[0][:120]
            rc, out, err = run([java, '-cp', d, 'Main'], timeout=60, cwd=d)
            if rc != 0:
                return False, '运行失败：%s' % (err or out).strip()[:120]
            if 'CSV' not in out:
                return False, '输出异常：%r' % out[:60]
            return True, (out.strip() if verbose else '')

        if lang == 'python':
            exe = os.path.join(RUNTIME, 'python', 'python.exe')
            if not os.path.exists(exe):
                return False, '未找到 python.exe'
            rc, out, err = run([exe, '-c', 'print("CSV%d" % len([1,2,3]))'], timeout=60)
            if rc != 0 or 'CSV' not in out:
                return False, '运行失败：%s' % (err or out).strip()[:120]
            return True, (out.strip() if verbose else '')

        if lang == 'node':
            exe = os.path.join(RUNTIME, 'node', 'node.exe')
            if not os.path.exists(exe):
                return False, '未找到 node.exe'
            rc, out, err = run([exe, '-e', 'console.log("CSV"+[1,2].length)'], timeout=60)
            if rc != 0 or 'CSV' not in out:
                return False, '运行失败：%s' % (err or out).strip()[:120]
            return True, (out.strip() if verbose else '')

        return False, '未知语言'
    finally:
        rm(d)


# ==================== 本机工具链探测 ====================
def _scan_bins(roots, depth=2, limit=120):
    """在给定根目录下有界地找出所有 bin 目录。

    带深度上限是刻意的：这里只是「用户机器上可能装了编译器」的启发式搜索，
    不值得为此付出全盘遍历的代价（Program Files / D:\\ 下嵌套极深）。
    """
    found = []

    def walk(d, lvl):
        if len(found) >= limit or lvl > depth:
            return
        try:
            entries = os.listdir(d)
        except OSError:
            return
        for name in entries:
            p = os.path.join(d, name)
            if not os.path.isdir(p):
                continue
            if name.lower() == 'bin':
                found.append(p)
            else:
                walk(p, lvl + 1)

    for r in roots:
        if os.path.isdir(r):
            walk(r, 0)
    return found


def find_local_cc():
    """本机已有的 C/C++ 工具链根目录（其 bin 下有 gcc.exe 或 g++.exe）"""
    home = os.path.expanduser('~')
    bins = []
    for exe in ('gcc.exe', 'g++.exe', 'clang.exe'):
        w = shutil.which(exe)
        if w:
            bins.append(os.path.dirname(w))
    bins += [
        r'C:\msys64\ucrt64\bin', r'C:\msys64\mingw64\bin', r'C:\msys64\clang64\bin',
        r'C:\mingw64\bin', r'C:\MinGW\bin', r'C:\TDM-GCC-64\bin',
        r'C:\Program Files\mingw-w64\bin', r'C:\Program Files\LLVM\bin',
        r'D:\Develop\mingw64\bin', r'D:\Develop\w64devkit\bin',
    ]
    # WinGet 装出来的 LLVM-MinGW 埋得比较深：Packages/<包名>/<工具链目录>/bin
    for root, dep in ((os.path.join(home, 'AppData', 'Local', 'Microsoft', 'WinGet', 'Packages'), 4),
                      (os.path.join(home, 'scoop', 'apps'), 3),
                      (r'C:\Program Files', 2), (r'C:\Program Files (x86)', 2),
                      (r'D:\Develop', 2), (r'C:\dev', 2)):
        bins += _scan_bins([root], dep)

    out = []
    for b in bins:
        if not os.path.isdir(b):
            continue
        if os.path.exists(os.path.join(b, 'gcc.exe')) or os.path.exists(os.path.join(b, 'g++.exe')):
            root = os.path.dirname(b)
            if root not in out:
                out.append(root)
    return out


def find_local_jdk():
    """本机已有的 JDK 根目录（bin 下同时有 javac.exe 与 jlink.exe）"""
    cands = []
    if os.getenv('JAVA_HOME'):
        cands.append(os.getenv('JAVA_HOME'))
    w = shutil.which('javac.exe') or shutil.which('javac')
    if w:
        cands.append(os.path.dirname(os.path.dirname(w)))
    for b in _scan_bins([r'C:\Program Files\Java', r'C:\Program Files\Eclipse Adoptium',
                         r'C:\Program Files\Microsoft', r'C:\Program Files\BellSoft',
                         r'C:\Program Files\Amazon Corretto', r'C:\Program Files\Zulu',
                         r'C:\Java', r'D:\Develop', r'D:\Program Files',
                         os.path.join(os.path.expanduser('~'), '.jdks')], depth=2):
        cands.append(os.path.dirname(b))
    out = []
    for c in cands:
        if c and c not in out and os.path.exists(os.path.join(c, 'bin', 'javac.exe')):
            out.append(c)
    return out


# ==================== 各语言部署 ====================
def skip_if_ready(pkg, verify_langs, force):
    """已经部署且验证通过就直接跳过 —— 否则每次重跑都要重新下载几十 MB"""
    if force:
        return None
    d = os.path.join(RUNTIME, pkg)
    if not os.path.isdir(d):
        return None
    for l in verify_langs:
        ok, _ = verify_lang(l)
        if not ok:
            return None
    rec = load_manifest().get(pkg, {})
    info('%s 已部署且验证通过，跳过（加 --force 可强制重装）' % pkg)
    return {'ok': True, 'dir': pkg, 'source': rec.get('source') or '（已部署）',
            'size': dir_size(d), 'verified': True, 'detail': '', 'skipped': True}


def install_c_cpp(mode, tmp, archive=None, no_prune=False, force=False):
    dest = os.path.join(RUNTIME, 'c-cpp')
    done = skip_if_ready('c-cpp', ['c', 'cpp'], force)
    if done:
        return done

    stage, src_desc = None, None

    if archive:
        step('C/C++：使用本地压缩包 %s' % os.path.basename(archive))
        stage = extract(archive, os.path.join(tmp, 'cc-stage'))
        src_desc = '本地压缩包 ' + os.path.basename(archive)
    elif mode == 'local':
        cands = find_local_cc()
        if not cands:
            bad('本机没找到可用的 C/C++ 工具链（要求目录下有 bin/gcc.exe）')
            return None
        stage = cands[0]
        info('使用本机工具链：%s' % stage)
        src_desc = '本机工具链 ' + stage
    else:
        try:
            step('C/C++：下载 w64devkit（约 64 MB，解压后自动裁剪）')
            pkg = os.path.join(tmp, W64DEVKIT_ASSET)
            download_github(W64DEVKIT_URL, pkg, 'w64devkit')
            stage = extract(pkg, os.path.join(tmp, 'cc-stage'))
            src_desc = 'w64devkit ' + W64DEVKIT_TAG
        except Exception as e:
            if mode != 'auto':
                bad('下载失败：%s' % str(e)[:120])
                return None
            # 联网失败就退回用本机已有的编译器，总比什么都没有强
            warn('下载失败（%s），改用本机已有工具链' % str(e)[:60])
            cands = find_local_cc()
            if not cands:
                bad('下载失败且本机也没有 C/C++ 工具链')
                return None
            stage = cands[0]
            src_desc = '本机工具链 ' + stage

    stage = toolchain_root(stage)
    rm(dest)

    if no_prune:
        step('整包复制（--no-prune）')
        shutil.copytree(stage, dest, dirs_exist_ok=True)
    else:
        step('裁剪后复制')
        dropped = copy_pruned(stage, dest, DROP_DIRS, DROP_BIN_GLOBS, DROP_NESTED_GLOBS)
        info('剔除 %d 项，例如：%s' % (len(dropped), ', '.join(dropped[:6])))

    ok_c, why_c = verify_lang('c')
    ok_cpp, why_cpp = verify_lang('cpp')

    if not (ok_c and ok_cpp) and not no_prune:
        # 裁过头就别硬撑：整包重来一次，功能永远优先于体积
        warn('裁剪后验证未过（C=%s / C++=%s），回退为完整复制' % (ok_c, ok_cpp))
        rm(dest)
        shutil.copytree(stage, dest, dirs_exist_ok=True)
        src_desc += '（完整版）'
        ok_c, why_c = verify_lang('c')
        ok_cpp, why_cpp = verify_lang('cpp')

    (good if ok_c else bad)('C   %s' % (why_c or '编译并运行通过'))
    (good if ok_cpp else bad)('C++ %s' % (why_cpp or '编译并运行通过'))

    return {'ok': bool(ok_c and ok_cpp), 'dir': 'c-cpp', 'source': src_desc,
            'size': dir_size(dest), 'verified': bool(ok_c and ok_cpp),
            'detail': '' if (ok_c and ok_cpp) else (why_c or why_cpp)}


def install_java(mode, tmp, no_prune=False, force=False):
    dest = os.path.join(RUNTIME, 'java')
    done = skip_if_ready('java', ['java'], force)
    if done:
        return done

    jdk, src_desc, dl_stage = None, None, None

    if mode == 'local':
        cands = find_local_jdk()
        if not cands:
            bad('本机没找到可用 JDK（要求同时有 bin/javac.exe 和 bin/jlink.exe）')
            return None
        jdk = cands[0]
        src_desc = '本机 JDK ' + jdk
    else:
        ver = os.getenv('CSVISUAL_JDK_VERSION', '21')
        try:
            step('Java：下载 JDK %s（约 190 MB，下载后用 jlink 裁剪）' % ver)
            pkg = os.path.join(tmp, 'jdk.zip')
            download_any([ADOPTIUM_URL.format(v=ver)], pkg, 'jdk')
            dl_stage = extract(pkg, os.path.join(tmp, 'jdk-stage'))
            jdk = toolchain_root(dl_stage)
            src_desc = 'Adoptium JDK ' + ver
        except Exception as e:
            if mode != 'auto':
                bad('下载失败：%s' % str(e)[:120])
                return None
            warn('下载失败（%s），改用本机 JDK' % str(e)[:60])
            cands = find_local_jdk()
            if not cands:
                bad('下载失败且本机也没有 JDK')
                return None
            jdk = cands[0]
            src_desc = '本机 JDK ' + jdk

    jlink = os.path.join(jdk, 'bin', 'jlink.exe')
    if not os.path.exists(jlink):
        bad('该 JDK 没有 jlink（%s），无法生成裁剪运行时；可加 --no-prune 直接整包复制' % jdk)
        return None

    rm(dest)
    if no_prune:
        step('整包复制完整 JDK')
        shutil.copytree(jdk, dest, dirs_exist_ok=True)
    else:
        step('jlink 生成私有运行时（只含 java.base + jdk.compiler）')
        mods = 'java.base,jdk.compiler,jdk.zipfs,jdk.unsupported'
        common = [jlink, '--add-modules', mods, '--output', dest, '--strip-debug',
                  '--no-header-files', '--no-man-pages']
        rc, out, err = run(common + ['--compress=zip-6'], timeout=900)
        if rc != 0:   # JDK 21 以下只认数字形式的压缩级别
            rc, out, err = run(common + ['--compress=2'], timeout=900)
        if rc != 0:
            rc, out, err = run(common, timeout=900)
        if rc != 0:
            warn('jlink 失败（%s），改为整包复制' % (err or out).strip()[:100])
            rm(dest)
            shutil.copytree(jdk, dest, dirs_exist_ok=True)
            src_desc += '（完整版）'
    if dl_stage:
        rm(dl_stage)

    ok, why = verify_lang('java')
    (good if ok else bad)('Java %s' % (why or 'javac 编译 + java 运行通过'))
    return {'ok': ok, 'dir': 'java', 'source': src_desc,
            'size': dir_size(dest), 'verified': ok, 'detail': why}


def install_python(mode, tmp, force=False):
    dest = os.path.join(RUNTIME, 'python')
    done = skip_if_ready('python', ['python'], force)
    if done:
        return done
    src_desc = None
    try:
        if mode == 'local':
            raise RuntimeError('按要求只使用本机解释器')
        step('Python：下载官方 embeddable 包（约 11 MB，版本固定，不受用户环境干扰）')
        pkg = os.path.join(tmp, 'python-embed.zip')
        used = download_any([PY_URL] + PY_FALLBACKS, pkg, 'python')
        stage = extract(pkg, os.path.join(tmp, 'py-stage'))
        rm(dest)
        shutil.copytree(stage, dest, dirs_exist_ok=True)
        src_desc = 'Python embeddable ' + os.path.basename(used).split('-embed')[0]
    except Exception as e:
        if mode != 'local':
            warn('下载失败（%s），改为从本机解释器复制' % str(e)[:60])
        step('Python：从本机解释器复制最小运行时')
        rm(dest)
        os.makedirs(dest, exist_ok=True)
        base = sys.base_prefix
        shutil.copy2(sys.executable, os.path.join(dest, os.path.basename(sys.executable)))
        for name in os.listdir(base):
            if name.startswith('python') and name.endswith('.dll'):
                shutil.copy2(os.path.join(base, name), os.path.join(dest, name))
        for sub in ('DLLs', 'Lib'):
            p = os.path.join(base, sub)
            if os.path.isdir(p):
                shutil.copytree(p, os.path.join(dest, sub), dirs_exist_ok=True)
        src_desc = '本机解释器 ' + sys.executable

    ok, why = verify_lang('python')
    (good if ok else warn)('Python %s' % (why or '运行通过'))
    return {'ok': ok, 'dir': 'python', 'source': src_desc,
            'size': dir_size(dest), 'verified': ok, 'detail': why}


def install_node(mode, tmp, force=False):
    dest = os.path.join(RUNTIME, 'node')
    done = skip_if_ready('node', ['node'], force)
    if done:
        return done
    src_desc = None
    if mode == 'local':
        w = shutil.which('node.exe') or shutil.which('node')
        if not w:
            bad('本机没找到 node')
            return None
        step('Node：复制本机 node.exe')
        rm(dest)
        os.makedirs(dest, exist_ok=True)
        shutil.copy2(w, os.path.join(dest, 'node.exe'))
        src_desc = '本机 node ' + w
    else:
        step('Node：下载官方便携包（约 30 MB）')
        pkg = os.path.join(tmp, 'node.zip')
        try:
            download_any([NODE_URL], pkg, 'node')
        except Exception as e:
            # nodejs.org 在部分网络下不可达，退回直接复制本机 node.exe
            w = shutil.which('node.exe') or shutil.which('node')
            if not w:
                bad('下载失败且本机也没有 node：%s' % str(e)[:80])
                return None
            warn('下载失败（%s），改为复制本机 node.exe' % str(e)[:60])
            rm(dest)
            os.makedirs(dest, exist_ok=True)
            shutil.copy2(w, os.path.join(dest, 'node.exe'))
            src_desc = '本机 node ' + w
            ok, why = verify_lang('node')
            (good if ok else warn)('Node %s' % (why or '运行通过'))
            return {'ok': ok, 'dir': 'node', 'source': src_desc,
                    'size': dir_size(dest), 'verified': ok, 'detail': why}
        stage = extract(pkg, os.path.join(tmp, 'node-stage'))
        rm(dest)
        os.makedirs(dest, exist_ok=True)
        shutil.copy2(os.path.join(stage, 'node.exe'), os.path.join(dest, 'node.exe'))
        src_desc = 'nodejs 便携版 win-x64'

    ok, why = verify_lang('node')
    (good if ok else warn)('Node %s' % (why or '运行通过'))
    return {'ok': ok, 'dir': 'node', 'source': src_desc,
            'size': dir_size(dest), 'verified': ok, 'detail': why}


# ==================== 状态总览 ====================
def show_info():
    m = load_manifest()
    step('内置工具链目录：%s' % RUNTIME)
    if not os.path.isdir(RUNTIME):
        warn('尚未部署 —— 服务会自动退回使用系统已装的编译器')
    else:
        log()
        log('  %-9s %-8s %-10s %-6s %s' % ('语言', '状态', '体积', '验证', '来源'))
        log('  ' + '-' * 76)
        for lang in LANGS:
            d = os.path.join(RUNTIME, PKG_OF[lang])
            if not os.path.isdir(d):
                log('  %-9s %s' % (lang, '未部署'))
                continue
            rec = m.get(PKG_OF[lang], {})
            log('  %-9s %-8s %-10s %-6s %s' % (
                lang, '已部署', human(dir_size(d)),
                '通过' if rec.get('verified') else '?',
                (rec.get('source') or '-')[:46]))
        total = dir_size(RUNTIME)
        log()
        log('  合计 %s（打包压缩后通常约 %s）' % (human(total), human(int(total * 0.10))))

    log()
    step('本机已装的工具链（内置缺失时会回退使用）')
    cc = find_local_cc()
    info('C/C++  %s' % (cc[0] if cc else '未找到'))
    jdk = find_local_jdk()
    info('Java   %s' % (jdk[0] if jdk else '未找到'))
    info('Python %s' % sys.executable)
    node = shutil.which('node.exe') or shutil.which('node')
    info('Node   %s' % (node or '未找到'))


# ==================== 主流程 ====================
def install_all(langs, base_mode='auto', archive='', no_prune=False, force=False, verify=False):
    """部署指定语言，返回退出码。main() 与 --ensure 都走这里，避免两套流程。"""
    unknown = [x for x in langs if x not in LANGS]
    if unknown:
        bad('不支持的语言：%s（可选 %s）' % (','.join(unknown), ','.join(LANGS)))
        return 2

    pkgs = []
    for l in langs:
        if PKG_OF[l] not in pkgs:
            pkgs.append(PKG_OF[l])
    if 'c-cpp' in pkgs:          # c 与 cpp 是同一个包，指定任意一个就装全套
        langs = sorted(set(langs) | {'c', 'cpp'}, key=LANGS.index)

    log()
    log('  CSVisual 内置工具链部署')
    log('  目标目录：%s' % RUNTIME)
    log('  语言　　：%s' % ', '.join(langs))
    log('  方式　　：%s' % {'local': '仅用本机已装（离线）',
                           'download': '仅联网下载',
                           'auto': '优先下载官方便携包（保证版本一致），联网失败才用本机已装'}[base_mode])
    log()

    tmp = tempfile.mkdtemp(prefix='csvisual-runtime-')
    manifest = load_manifest()
    results = {}
    t0 = time.time()
    try:
        for pkg in pkgs:
            log()
            if pkg == 'c-cpp':
                r = install_c_cpp(base_mode, tmp, archive=archive or None,
                                  no_prune=no_prune, force=force)
            elif pkg == 'java':
                r = install_java(base_mode, tmp, no_prune=no_prune, force=force)
            elif pkg == 'python':
                r = install_python(base_mode, tmp, force=force)
            elif pkg == 'node':
                r = install_node('download' if base_mode == 'auto' else base_mode,
                                 tmp, force=force)
            else:
                continue

            if r:
                results[pkg] = r
                manifest[pkg] = {
                    'source': r['source'],
                    'size': r['size'],
                    'verified': bool(r['verified']),
                    'installedAt': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'tool': 'tools/setup_runtime.py',
                }
                save_manifest(manifest)
    finally:
        rm(tmp)

    log()
    log('  ' + '=' * 62)
    step('部署结果')
    all_ok = True
    for pkg, r in results.items():
        if r['ok']:
            good('%-8s %-10s %s' % (pkg, human(r['size']), r['source'][:46]))
        else:
            all_ok = False
            bad('%-8s 失败：%s' % (pkg, r.get('detail') or '未知原因'))
    if not results:
        all_ok = False
        bad('没有任何语言部署成功')

    if verify:
        log()
        step('独立复验（直接在 runtime/ 上重新编译运行）')
        for lang in langs:
            if not os.path.isdir(os.path.join(RUNTIME, PKG_OF[lang])):
                info('%-10s 未部署，跳过' % lang)
                continue
            ok, out = verify_lang(lang, verbose=True)
            (good if ok else bad)('%-10s %s' % (lang, out or '通过'))

    total = dir_size(RUNTIME) if os.path.isdir(RUNTIME) else 0
    log()
    log('  用时 %.1fs，runtime/ 合计 %s（打包压缩后约 %s）'
        % (time.time() - t0, human(total), human(int(total * 0.10))))
    log('  重启后端服务后生效。')
    log()
    return 0 if all_ok else 1


def ensure_mode(auto=False):
    """启动前的就绪检查（--ensure）。

    已部署就一句话通过；没部署时讲清楚「为什么要装、装完什么效果、多大代价」。
    auto=True（--auto）为无人值守模式：不再询问，直接开始部署 ——
    供两条自动链路调用：启动脚本 ensure-runtime.bat、后端检测到缺编译器时的后台自愈。
    交互模式保持原样（手动双击 setup-runtime.bat 时仍问一句），
    这段文案刻意放在 Python 里而不是 .bat：批处理里的中文容易被 cmd 的
    代码页切换搞乱字节偏移，Python 输出中文则一直是对的。
    """
    cc = os.path.join(RUNTIME, 'c-cpp', 'bin', 'gcc.exe')
    if os.path.exists(cc):
        good('内置工具链已就绪（runtime/）')
        return 0

    log()
    log('  ' + '=' * 58)
    log('   尚未部署内置编译器')
    log('  ' + '=' * 58)
    log('   部署后，任何拿到本项目的人都能直接运行 C/C++ 与 Java 代码，')
    log('   不必先在自己电脑上装 gcc 或 JDK —— 就像在线判题站那样。')
    log('   需要联网下载约 64 MB，解压后约 450 MB，只做一次。')
    log()
    if auto:
        # 无人值守：部署过程全部写入本文件所在目录的 runtime-deploy.log，
        # 出问题用户拿着日志来问，比「装没装上」两个字好排查得多。
        log('   --auto 模式：跳过询问，直接开始部署。')
        return install_all(['c', 'cpp', 'java'], 'auto')

    try:
        ans = input('   现在部署吗？（输入 y 回车 = 现在装；直接回车 = 跳过）: ')
    except (EOFError, KeyboardInterrupt):
        ans = ''
    if ans.strip().lower() != 'y':
        log()
        info('已跳过。之后随时双击 tools\\setup-runtime.bat 即可部署。')
        return 0
    return install_all(['c', 'cpp', 'java'], 'auto')


def main():
    ap = argparse.ArgumentParser(
        description='把编译器部署进项目的 runtime/ 目录，让任何用户都能直接运行代码',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--lang', default='',
                    help='要部署的语言，逗号分隔：c,cpp,java,python,node（默认 c,cpp,java）')
    ap.add_argument('--from-local', action='store_true', help='只用本机已装的工具链，不联网')
    ap.add_argument('--download', action='store_true', help='跳过本机，直接下载官方便携包')
    ap.add_argument('--archive', default='', help='使用已下载好的 C/C++ 压缩包（离线部署）')
    ap.add_argument('--no-prune', action='store_true', help='不裁剪，完整复制（更稳但更大）')
    ap.add_argument('--force', action='store_true', help='已部署也重新装一遍（默认会跳过）')
    ap.add_argument('--verify', action='store_true', help='部署后逐语言真实编译运行验证')
    ap.add_argument('--info', action='store_true', help='只显示当前状态')
    ap.add_argument('--clean', action='store_true', help='删除已部署的内置工具链')
    ap.add_argument('--ensure', action='store_true',
                    help='启动前的就绪检查：没装就问一句要不要现在装（供启动脚本调用）')
    ap.add_argument('--auto', action='store_true',
                    help='与 --ensure 连用：无人值守，跳过询问直接部署（供启动脚本与后端自愈调用）')
    args = ap.parse_args()

    if args.ensure:
        return ensure_mode(auto=args.auto)

    if args.info:
        show_info()
        return 0

    if args.clean:
        step('删除内置工具链')
        if not os.path.isdir(RUNTIME):
            warn('本来就没有部署，无需删除')
            return 0
        freed = dir_size(RUNTIME)
        rm(RUNTIME)
        good('已删除，释放 %s；服务会自动退回使用系统编译器' % human(freed))
        return 0

    base_mode = 'local' if args.from_local else ('download' if args.download else 'auto')
    langs = [x.strip().lower() for x in args.lang.split(',') if x.strip()] or ['c', 'cpp', 'java']
    return install_all(langs, base_mode, archive=args.archive, no_prune=args.no_prune,
                       force=args.force, verify=args.verify)


if __name__ == '__main__':
    sys.exit(main())
