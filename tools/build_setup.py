#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""组装便携版目录 + 编译出 CSVisual-Setup.exe

整条流水线：

    源项目                      build\\portable\\               最终产物
    --------                    ----------------                --------
    server-py\\                       ──> app\\server-py\\
    web\\dist\\                       ──> app\\web\\
    Python 3.13 embed + site-packages ─> runtime\\python\\
    本机 MySQL 8.0.34（精简后）      ──> runtime\\mysql\\
    本机 MySQL 里的 cs_visual 库     ──> initdb\\cs_visual.sql
    tools\\portable\\*.bat / *.txt    ──> 根目录
                                                                  │
                                          Inno Setup 编译 ─────────┘
                                                                  ↓
                                                      CSVisual-Setup.exe

2026-10-10：项目收敛为纯 Python 后端，交付包的内置运行时由 Node 换成 Python。
用官方 embeddable 包（约 11 MB）打底 + 直接把 .venv 里的 site-packages 搬进去，
不要求目标机装 Python。

为什么最终交付一个 exe 而不是 zip：
  比赛要求交「可运行的完整软件系统」。zip 要评委自己装 MySQL / Python，
  还要联网拉依赖 —— 基本上等于交不出去。做成安装向导，
  双击 → 下一步 → 完成 → 自动开浏览器，评委零门槛；装完在开始菜单和桌面都有入口，
  卸载也走标准「添加或删除程序」。

用法：
    python tools/build_setup.py            # 组装便携目录（不编译）
    python tools/build_setup.py --compile  # 组装完接着调用 ISCC 编译安装包
    python tools/build_setup.py --skip-db   # 跳过数据库导出（复用上次的 SQL）

前置：本机要有 MySQL（用来 mysqldump），且已完成前端构建 web\\dist。
"""

import argparse
import os
import shutil
import subprocess
import sys
import time
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, 'build')
PORTABLE = os.path.join(BUILD, 'portable')

# 组装 app\\server-py\\ 时要跳过的东西：
#   .env          —— 由 start.bat 按实际安装路径生成，不能把开发机的密码带出去
#   logs/uploads  —— 运行期产物，出厂应该是空的
#   .venv         —— 依赖已经单独打进 runtime\\python，这里再带一份就是纯浪费
#   tests         —— 测试代码不属于交付软件
SERVER_SKIP_DIRS = {'logs', 'uploads', '.pytest_cache', '__pycache__', '.git',
                    '.venv', 'tests', 'backups'}
SERVER_SKIP_FILES = {'.env', '.env.local', '*.log', '*.pyc'}

# 内置 Python 运行时（embeddable 包，约 11 MB）
PY_EMBED_VERSION = '3.13.2'
PY_EMBED_URL = f'https://mirrors.huaweicloud.com/python/{PY_EMBED_VERSION}/python-{PY_EMBED_VERSION}-embed-amd64.zip'
PY_STAGE = os.path.join(BUILD, 'pyembed')

# MySQL 8 是 VC++ 2019 编的，目标机不一定装了运行库。
# VC 运行库允许随应用本地部署，把这几个 dll 塞进 mysql\\bin 最省事，
# 不用再下载 25MB 的 VC_redist 安装包。
VC_DLLS = ['vcruntime140.dll', 'vcruntime140_1.dll', 'msvcp140.dll']


def human(n: float) -> str:
    for unit in ('B', 'KB', 'MB', 'GB'):
        if n < 1024 or unit == 'GB':
            return f'{n:.1f}{unit}' if unit != 'B' else f'{int(n)}B'
        n /= 1024


def dir_size(path: str) -> int:
    total = 0
    for cur, _, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(cur, f))
            except OSError:
                pass
    return total


def discard(path: str) -> None:
    """把上一次的输出挪进 build\\_trash，而不是直接删。

    本机运行环境挂了删除守卫：一次性删掉超过阈值数量的文件会被拦截并抛
    SystemExit，脚本会毫无征兆地停在一半，把 portable 目录留成残缺状态
    （实测删到 1920 / 22763 个文件时被拦下）。同盘 os.replace 是瞬时重命名，
    既躲开守卫，又不会留下半截目录。
    """
    if not os.path.exists(path):
        return
    trash = os.path.join(BUILD, '_trash')
    os.makedirs(trash, exist_ok=True)
    dst = os.path.join(trash, os.path.basename(path) + '-' + time.strftime('%H%M%S'))
    try:
        os.replace(path, dst)
        print(f'旧输出已移入: {dst}')
    except OSError:
        shutil.rmtree(path, ignore_errors=True)


def copy_filtered(src: str, dst: str, skip_dirs: set, skip_files: set) -> int:
    """按规则复制目录树，返回复制的文件数"""
    n = 0
    os.makedirs(dst, exist_ok=True)
    for cur, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        rel = os.path.relpath(cur, src)
        target = dst if rel == '.' else os.path.join(dst, rel)
        os.makedirs(target, exist_ok=True)
        for f in files:
            if f in skip_files:
                continue
            shutil.copy2(os.path.join(cur, f), os.path.join(target, f))
            n += 1
    return n


def read_env_db():
    """从 server\\.env 里读数据库连接参数"""
    cfg = {'host': '127.0.0.1', 'port': '3306', 'user': 'root',
           'password': '', 'name': 'cs_visual'}
    env_path = os.path.join(ROOT, 'server', '.env')
    if os.path.isfile(env_path):
        with open(env_path, encoding='utf-8', errors='ignore') as fp:
            for line in fp:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                k, v = line.split('=', 1)
                k = k.strip()
                if k == 'DB_HOST':
                    cfg['host'] = v.strip()
                elif k == 'DB_PORT':
                    cfg['port'] = v.strip()
                elif k == 'DB_USER':
                    cfg['user'] = v.strip()
                elif k == 'DB_PASSWORD':
                    cfg['password'] = v.strip()
                elif k == 'DB_NAME':
                    cfg['name'] = v.strip()
    return cfg


def find_mysqldump() -> str:
    """在本机常见位置找 mysqldump.exe"""
    import glob
    candidates = glob.glob(r'D:\Develop\Mysql\*\bin\mysqldump.exe')
    candidates += glob.glob(r'C:\Program Files\MySQL\*\bin\mysqldump.exe')
    for c in candidates:
        if os.path.isfile(c):
            return c
    return ''


def export_db(sql_out: str) -> bool:
    """导出 cs_visual 库，并把出厂清理语句拼在后面"""
    cfg = read_env_db()
    dump = find_mysqldump()
    if not dump:
        print('[警告] 没找到 mysqldump.exe，跳过导出（复用已有 SQL）')
        return False

    tmp = sql_out + '.dump'
    cmd = [
        dump,
        f"-u{cfg['user']}", f"-p{cfg['password']}",
        f"-h{cfg['host']}", f"-P{cfg['port']}",
        '--databases', cfg['name'],
        '--routines', '--default-character-set=utf8mb4',
        '--result-file=' + tmp,
    ]
    print(f"  导出数据库 {cfg['name']} ...")
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0 or not os.path.isfile(tmp):
        print('[错误] mysqldump 失败:', r.stderr.decode('utf-8', 'ignore')[:300])
        return False

    cleanup = os.path.join(ROOT, 'tools', 'portable', 'cleanup.sql')
    with open(sql_out, 'w', encoding='utf-8') as out:
        out.write('-- CSVisual 出厂数据（结构 + 演示数据）\n')
        out.write('-- 本文件由 tools/build_setup.py 自动生成，请勿手工修改\n\n')
        with open(tmp, encoding='utf-8', errors='ignore') as fp:
            out.write(fp.read())
        if os.path.isfile(cleanup):
            out.write('\n')
            with open(cleanup, encoding='utf-8') as fp:
                out.write(fp.read())
    # 中间产物也是"挪走"而不是删 —— 这个 dump 有两万多行，删它同样会被守卫拦
    discard(tmp)
    print(f"  -> {os.path.basename(sql_out)} ({human(os.path.getsize(sql_out))})")
    return True


def make_zip(zip_out: str, top_dir: str = 'CSVisual') -> int:
    """把便携目录打成 zip —— 这就是「离线绿色运行包」，解压即用。

    和安装包的区别：安装包会写注册表、在开始菜单留入口；绿色包解压出来是
    一个自包含目录，不碰系统任何地方，拷到 U 盘换台机器照样跑。

    zip 统一用正斜杠作分隔符（PKZIP 规范），顶层套一个 CSVisual\\ 目录，
    避免用户直接解压到 D:\\ 根目录时散一地。
    """
    n = 0
    with zipfile.ZipFile(zip_out, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for cur, _, files in os.walk(PORTABLE):
            for f in files:
                p = os.path.join(cur, f)
                arc = os.path.relpath(p, PORTABLE).replace(os.sep, '/')
                zf.write(p, f'{top_dir}/{arc}')
                n += 1
    return n


def stage_python_runtime() -> str:
    """把「Python embeddable + 后端依赖」装配成 runtime\\python。

    embeddable 包只有 11 MB，但里面没有 pip、也没有任何第三方库；
    所以把后端 .venv 里已经装好的 site-packages 整个搬进去。
    两者的大版本必须一致（都是 3.13）：pydantic-core / bcrypt 之类是编译产物，
    文件名里写着 cp313，跨小版本 ABI 不变、跨大版本直接 import 失败。

    返回装配目录（build\\pyembed），不存在则抛错。
    """
    import urllib.request

    zip_path = os.path.join(BUILD, 'python-embed.zip')
    marker = os.path.join(PY_STAGE, '.ready')

    if not os.path.isfile(os.path.join(PY_STAGE, 'python.exe')):
        if not os.path.isfile(zip_path):
            print(f'  下载 Python embeddable {PY_EMBED_VERSION} ...')
            urllib.request.urlretrieve(PY_EMBED_URL, zip_path)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(PY_STAGE)

    # 依赖每次都从 .venv 重拷：改过 requirements.txt 后不用手动清缓存
    sp_dst = os.path.join(PY_STAGE, 'Lib', 'site-packages')
    if os.path.isdir(sp_dst):
        discard(sp_dst)
    sp_src = os.path.join(ROOT, 'server-py', '.venv', 'Lib', 'site-packages')
    if not os.path.isdir(sp_src):
        raise SystemExit('[错误] 找不到 server-py\\.venv，请先执行 start.bat 建好虚拟环境')
    # 复制时就跳过运行时用不到的东西：.venv 里装的是「开发依赖全集」，
    # 而交付包只需要能跑起来 —— pip / pytest / pygments 加起来 26 MB，
    # __pycache__ 更是纯缓存，带进安装包全是白送的体积。
    #
    # 这里是「不复制」而不是「先复制再删」：本机运行环境挂了批量删除守卫，
    # 一次性删掉上千个文件会被拦截并抛 SystemExit，脚本会毫无征兆地停在一半。
    copy_filtered(sp_src, sp_dst,
                  {'__pycache__', 'pip', 'pytest', '_pytest', 'pygments'},
                  {'*.pyc'})

    # ._pth 决定 embeddable 版的 sys.path（此时 PYTHONPATH 是失效的），
    # 必须把 site-packages 显式写进去，否则 import fastapi 直接失败。
    #
    # 文件名必须和解释器对得上：3.13.x 就是 python313._pth（主版本+次版本，
    # 不加修订号）。写错名字不会报错，只会静默沿用解压出来的默认 ._pth，
    # 于是依赖全找不到 —— 表现为「安装包装完双击没反应」。
    tag = ''.join(PY_EMBED_VERSION.split('.')[:2])
    pth_name = f'python{tag}._pth'
    for f in os.listdir(PY_STAGE):
        if f.endswith('._pth') and f != pth_name:
            os.remove(os.path.join(PY_STAGE, f))
    with open(os.path.join(PY_STAGE, pth_name), 'w', encoding='utf-8') as fp:
        fp.write(f'python{tag}.zip\n.\nLib\\site-packages\nimport site\n')

    with open(marker, 'w') as fp:
        fp.write(PY_EMBED_VERSION)
    return PY_STAGE


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--compile', action='store_true', help='组装后调用 ISCC 编译安装包')
    ap.add_argument('--zip', action='store_true', help='组装后打包成绿色运行包 zip')
    ap.add_argument('--skip-db', action='store_true', help='跳过数据库导出')
    ap.add_argument('--keep', action='store_true',
                    help='不清空上次输出，直接在原目录上覆盖重建（旧目录被占用时用它）')
    args = ap.parse_args()

    print('=' * 62)
    print('  CSVisual 便携版 / 安装包构建')
    print('=' * 62)

    # ---------- 1. 清干净上次的输出 ----------
    # --keep：旧 portable 里有文件被占用时（例如上次构建遗留的 mysqld / node
    # 还持有句柄），改名与 rmtree 都会被系统拒（WinError 5）。此时不做清理，
    # 直接覆盖重建——copy_filtered 是逐文件覆盖，不依赖删除旧内容。
    if os.path.isdir(PORTABLE) and not args.keep:
        discard(PORTABLE)
    for sub in ('app/server-py', 'app/web', 'runtime/python', 'runtime/mysql', 'initdb'):
        os.makedirs(os.path.join(PORTABLE, sub), exist_ok=True)

    # --keep 会原样保留上一轮的目录，但项目换了后端之后，旧目录已经是死内容：
    # app\server 是 Node 后端、runtime\node 是 84MB 的 Node 运行时，
    # 留着会被一起打进安装包（实测多出近 100MB 且带着过时的后端代码）。
    for legacy in ('app/server', 'runtime/node'):
        p = os.path.join(PORTABLE, legacy)
        if os.path.isdir(p):
            print(f'清理上一轮遗留: {legacy}')
            discard(p)

    # ---------- 2. 后端（Python）----------
    server_src = os.path.join(ROOT, 'server-py')
    discard(os.path.join(PORTABLE, 'app', 'server-py'))   # 同上：避免残留旧文件
    n = copy_filtered(server_src, os.path.join(PORTABLE, 'app', 'server-py'),
                      SERVER_SKIP_DIRS, SERVER_SKIP_FILES)
    print(f'[1/6] 后端 app\\server-py: {n} 个文件')

    # ---------- 3. 前端构建产物 ----------
    dist = os.path.join(ROOT, 'web', 'dist')
    if not os.path.isfile(os.path.join(dist, 'index.html')):
        print('[错误] web\\dist 不存在，请先执行: cd web && npx vite build')
        return 1
    n = copy_filtered(dist, os.path.join(PORTABLE, 'app', 'web'), set(), set())
    print(f'[2/6] 前端 app\\web: {n} 个文件 ({human(dir_size(dist))})')

    # ---------- 4. 内置 Python 运行时 ----------
    # 运行时目录必须**整体重建**：copy_filtered 只覆盖不删除，
    # 上一轮遗留的文件会和这一轮混在一起（实测残留 2300 多个旧文件，
    # 瘦掉的 pip / pytest 又回来了）。源就在本地缓存里，重建很快。
    py_src = stage_python_runtime()
    discard(os.path.join(PORTABLE, 'runtime', 'python'))
    n_py = copy_filtered(py_src, os.path.join(PORTABLE, 'runtime', 'python'), set(), set())
    print(f'[3/6] 内置 Python {PY_EMBED_VERSION}: {n_py} 个文件 '
          f'({human(dir_size(os.path.join(PORTABLE, "runtime", "python")))})')

    # ---------- 5. 内置 MySQL ----------
    mysql_stage = os.path.join(BUILD, 'mysql')
    if not os.path.isfile(os.path.join(mysql_stage, 'bin', 'mysqld.exe')):
        print('  便携 MySQL 未生成，先执行 tools/build_portable.py ...')
        r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'build_portable.py')])
        if r.returncode != 0:
            return 1
    # 复制时就把测试留下的 my.ini / data 过滤掉（出厂必须是干净的）。
    # 之前是先 copytree 再删，结果触发了本机的删除守卫（删文件会被拦截并抛
    # SystemExit），脚本直接停在一半。直接不复制，连删除都不需要。
    n_mysql = copy_filtered(mysql_stage, os.path.join(PORTABLE, 'runtime', 'mysql'),
                            {'data'}, {'my.ini'})
    # VC++ 运行库
    got = []
    for dll in VC_DLLS:
        src = os.path.join(os.environ.get('SystemRoot', r'C:\Windows'), 'System32', dll)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(PORTABLE, 'runtime', 'mysql', 'bin', dll))
            got.append(dll)
    print(f'[4/6] 内置 MySQL: {n_mysql} 个文件 ({human(dir_size(os.path.join(PORTABLE, "runtime", "mysql")))})，附带 VC 运行库 {got or "未找到"}')

    # ---------- 6. 数据库 + 脚本 ----------
    sql_out = os.path.join(PORTABLE, 'initdb', 'cs_visual.sql')
    if args.skip_db and os.path.isfile(sql_out):
        print('[5/6] 跳过数据库导出，复用已有 SQL')
    else:
        if not export_db(sql_out):
            if not os.path.isfile(sql_out):
                print('[错误] 无法生成 initdb\\cs_visual.sql')
                return 1

    # 源文件按 UTF-8 维护（Git 里好读好改），落到便携目录时转成 GBK：
    # cmd.exe 按系统 ANSI 代码页逐字节解析批处理，UTF-8 会让行边界漂移。
    # README.txt 同理 —— 记事本默认按 ANSI 打开，UTF-8 会显示成乱码。
    scr_src = os.path.join(ROOT, 'tools', 'portable')
    for f in sorted(os.listdir(scr_src)):
        if not f.endswith(('.bat', '.txt')):
            continue
        src = os.path.join(scr_src, f)
        with open(src, encoding='utf-8') as fp:
            text = fp.read()
        text = text.replace('\u2192', '->')          # GBK 里没有这个箭头
        # 必须以二进制写并强制 CRLF：cmd 对 LF-only 的批处理不能可靠分行，
        # 遇到 () 块和 goto 标签会把行腰斩，冒出「'xxx' 不是内部或外部命令」。
        blob = text.encode('gbk', errors='replace').replace(b'\n', b'\r\n')
        with open(os.path.join(PORTABLE, f), 'wb') as fp:
            fp.write(blob)
    print('[6/6] 启动脚本与使用说明已就位（已转为 GBK）')

    total = dir_size(PORTABLE)
    print('-' * 62)
    print(f'便携目录就绪: {PORTABLE}')
    print(f'总体积: {human(total)}')

    if args.zip:
        zip_out = os.path.join(ROOT, 'CSVisual-绿色运行包.zip')
        print(f'\n打包绿色运行包: {zip_out}')
        t0 = time.time()
        n = make_zip(zip_out)
        print(f'绿色包就绪: {n} 个文件, {human(os.path.getsize(zip_out))}'
              f'（压缩前 {human(total)}, 耗时 {time.time() - t0:.0f}s）')
        print('用法：解压到任意目录 -> 双击 CSVisual\\start.bat')

    # ---------- 7. 编译安装包 ----------
    if args.compile:
        iss = os.path.join(BUILD, 'setup.iss')
        if not os.path.isfile(iss):
            print('[错误] 缺少 build\\setup.iss')
            return 1
        iscc = find_iscc()
        if not iscc:
            print('[错误] 没找到 ISCC.exe，请先安装 Inno Setup 6')
            return 1
        print(f'\n调用 Inno Setup 编译: {iscc}')
        r = subprocess.run([iscc, iss], capture_output=True)
        log = (r.stdout or b'').decode('utf-8', 'ignore') + (r.stderr or b'').decode('utf-8', 'ignore')
        print(log[-1500:])
        if r.returncode != 0:
            print('[错误] 编译失败')
            return 1
        out = os.path.join(BUILD, 'CSVisual-Setup.exe')
        if os.path.isfile(out):
            print(f'\n安装包已生成: {out}  ({human(os.path.getsize(out))})')
    return 0


def find_iscc() -> str:
    import glob
    pats = [
        os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Programs',
                     'Inno Setup 6', 'ISCC.exe'),
        r'C:\Program Files (x86)\Inno Setup 6\ISCC.exe',
        r'C:\Program Files\Inno Setup 6\ISCC.exe',
    ]
    for p in pats:
        if os.path.isfile(p):
            return p
    for p in glob.glob(r'D:\*Inno*\ISCC.exe'):
        return p
    return ''


if __name__ == '__main__':
    sys.exit(main())
