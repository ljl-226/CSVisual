#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CSVisual 分享包打包脚本

为什么不用纯 robocopy + tar 的批处理版本
----------------------------------------
原来的 pack.bat 直接在 cmd 里写中文提示。cmd.exe 按当前代码页逐字节解析批处理，
UTF-8 中文加上 chcp 切换会让行边界漂移，于是「rem 注释」被当成命令执行 ——
整包打包时（压缩 runtime\\ 那条分支）会冒出一行
    '...几十' is not recognized as an internal or external command
脚本能跑完，但用户双击时会看到一行毫无意义的报错，很难判断到底成没成功。

所以和 tools\\setup_runtime.py 一样：批处理只负责找到 Python 并把参数传进来，
所有干活和所有中文输出都在本脚本里完成。

顺带解决的两个老问题
--------------------
1. 不再先把 456 MB 复制进临时目录再压缩 —— 现在边遍历边写进 zip，省掉一整轮磁盘搬运。
2. 排除规则集中在一张表里，不用再维护四段 robocopy 的 /XD /XF 参数。

用法（在项目根目录执行）
------------------------
    python tools/pack.py                 默认打包，含内置工具链
    python tools/pack.py --no-runtime    不含内置工具链（约 1 MB，但对方得自己装编译器）
    python tools/pack.py --out D:\\a.zip  指定输出路径
    python tools/pack.py --dry-run       只统计，不真的压缩

脚本只用标准库。
"""

import argparse
import fnmatch
import os
import sys
import zipfile

if sys.version_info < (3, 7):  # pragma: no cover
    sys.exit('需要 Python 3.7 及以上版本')

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(errors='replace')
    except Exception:
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_NAME = 'CSVisual'
DEFAULT_OUT = os.path.join(ROOT, 'CSVisual-源码包.zip')
RUNTIME_DIR = 'runtime'

# 目录 -> (排除的目录名, 排除的文件通配符)
# 排除的从来是三类东西：能重装(npm i)、会带本机隐私或密码(.env)、以及构建产物(dist)。
DIR_RULES = {
    # 注：Node 后端 server/ 已于 2026-10-10 移除（项目收敛为纯 Python 后端），
    # 归档在 build\_trash\server-node-*。这里不再有它的打包规则。
    'server-py': (
        {'uploads', '.venv', '__pycache__', 'backups', '.pytest_cache'},
        {'.env', '*.log', '.deps_ready', '*.pyc'},
    ),
    'web': (
        # *.local 等临时构建产物一律不进包（含我为了校验构建临时建的 .tmp-*）。
        # .vis-dump 是 vis-check 跑完吐出来的动画快照（每个组件一个 JSON），
        # 既是产物也是运行痕迹，打进分享包纯属添乱。
        # .dist* / dist*：dist 是构建产物；.dist_prev 是重建 dist 时被 mv 出来的
        # 上一版备份（vite 清 outDir 要删上百个文件，本地直接删会被删文件守卫拦下），
        # 它和 dist 一样是能随时重新生成的，不该占进分享包。
        {'node_modules', 'dist', 'dist*', '.dist*', '.vite', '.vis-dump', '.tmp-*', '*.local'},
        {'.env', '*.log'},
    ),
    'tools': (
        {'__pycache__'},
        {'*.pyc'},
    ),
    RUNTIME_DIR: (
        # runtime/ 是内置工具链，原则上整目录带走。但历史上调试脚本被随手丢在这里过
        # （tmp-*.js / dist-check / genq 之类），一旦打进去就是 100+ MB 的分享包白送垃圾。
        # 所以这里显式排除这些非工具链内容，而不是无脑 {set()}。
        {'dist-check*', 'genq', '.tmp-*', '__pycache__'},
        {'tmp-*', '*.log', '*.pyc'},
    ),
}

# 根目录直接带上的零散文件（脚本、说明、gitignore）
ROOT_FILES = [
    'README.md',
    'CHANGELOG.md',   # 迭代记录，与 README 配套
    # 目录结构 + 源码清单说明：评委/助教解压后第一眼看到的就是它，
    # 有了它才知道从哪个目录看起、包里为什么不带 node_modules 和 runtime。
    '项目结构与源码清单.md',
    '.gitignore',
    'pack.bat',
    'start.bat',
    'start-python.bat',
    'stop.bat',
    'start.sh',
    'stop.sh',
]


def log(msg=''):
    print(msg, flush=True)


def human(n):
    """字节数转人话。和 setup_runtime.py 里那份保持一致的实现。"""
    step = 1024.0
    for unit in ('B', 'KB', 'MB', 'GB'):
        if abs(n) < step or unit == 'GB':
            if unit == 'B':
                return '%d B' % n
            return '%.1f %s' % (n, unit)
        n /= step
    return '%.1f GB' % n


def excluded_files(name, patterns):
    return any(fnmatch.fnmatch(name, p) for p in patterns)


def iter_files(src, skip_dirs, skip_files):
    """遍历 src，边走边剪枝 excluded 目录，产出相对路径。

    skip_dirs 里的条目一律按 fnmatch 处理：不带通配符时等价于精确匹配，
    带 `*` 时就能一次性覆盖 dist-check*、.tmp-* 这类临时产物，
    不必每次临时建目录都回来补一个硬编码名字。
    """
    for cur, dirs, files in os.walk(src):
        dirs[:] = sorted(d for d in dirs if not excluded_files(d, skip_dirs))
        rel_dir = os.path.relpath(cur, src)
        base = '' if rel_dir == '.' else rel_dir.replace('\\', '/') + '/'
        if not files and cur != src:
            yield None, base
        for f in sorted(files):
            if excluded_files(f, skip_files):
                continue
            yield os.path.join(cur, f), base + f


def collect_jobs(with_runtime):
    """产出 [(磁盘上的绝对路径, zip 内的相对路径)]，结构决定后会和其他地方共用。"""
    jobs = []
    for name, (skip_dirs, skip_files) in sorted(DIR_RULES.items()):
        if name == RUNTIME_DIR and not with_runtime:
            continue
        src = os.path.join(ROOT, name)
        if not os.path.isdir(src):
            continue
        prefix = '%s/%s/' % (ROOT_NAME, name)
        for abs_path, rel in iter_files(src, skip_dirs, skip_files):
            if abs_path is None:
                jobs.append((None, prefix + rel))
            else:
                jobs.append((abs_path, prefix + rel))
    for f in ROOT_FILES:
        p = os.path.join(ROOT, f)
        if os.path.isfile(p):
            jobs.append((p, '%s/%s' % (ROOT_NAME, f)))
    return jobs


def build_zip(jobs, out, with_runtime):
    """把 jobs 写进 zip。返回 (写入的文件数, 压缩前的总字节数)。"""
    total = len(jobs)
    written = 0
    raw = 0
    done = 0
    last_report = 0
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for abs_path, arc in jobs:
            done += 1
            if abs_path is None:
                zi = zipfile.ZipInfo(arc.rstrip('/') + '/')
                zi.compress_type = zipfile.ZIP_STORED
                zf.writestr(zi, b'')
                continue
            try:
                raw += os.path.getsize(abs_path)
            except OSError:
                pass
            zf.write(abs_path, arc)
            written += 1
            if done - last_report >= 1000 or done == total:
                last_report = done
                log('  打包中 %d/%d 个条目...' % (done, total))
    return written, raw


def main():
    ap = argparse.ArgumentParser(description='打包 CSVisual 分享包')
    ap.add_argument('--no-runtime', action='store_true',
                    help='不含内置工具链（体积小，但对方机器上要有编译器）')
    ap.add_argument('--out', default=DEFAULT_OUT, help='输出 zip 路径')
    ap.add_argument('--dry-run', action='store_true',
                    help='只统计条目数与体积，不真的压缩')
    args = ap.parse_args()

    with_runtime = not args.no_runtime
    runtime_ready = os.path.isdir(os.path.join(ROOT, RUNTIME_DIR))

    log('')
    log('  ==========================================================')
    log('   打包 CSVisual 分享包')
    log('  ==========================================================')
    if with_runtime:
        if runtime_ready:
            log('   包含内置工具链（约 456 MB）：对方解压即可运行 C/C++/Java，')
            log('   不需要在自己电脑上装过 gcc 或 JDK。')
        else:
            log('   本机还没部署内置工具链，这一包不会带。')
            log('   需要先双击 tools\\setup-runtime.bat，再回来重新打包。')
            log('   不带工具链对方也能看知识点和可视化，只是点「运行」会')
            log('   提示本机缺 C 环境 —— 我会明确说清楚原因，不会假装成功。')
    else:
        log('   不含内置工具链：对方需自己装编译器，')
        log('   或者拿到后双击 tools\\setup-runtime.bat 现装一份。')
    log('  ==========================================================')
    log('')

    log('  正在清点文件...')
    jobs = collect_jobs(with_runtime and runtime_ready)
    total_bytes = 0
    for abs_path, _arc in jobs:
        if abs_path:
            try:
                total_bytes += os.path.getsize(abs_path)
            except OSError:
                pass
    log('  共 %d 个条目，原始大小 %s' % (len(jobs), human(total_bytes)))

    if args.dry_run:
        log('')
        log('  --dry-run：到此为止，没有生成 zip。')
        return 0

    # 先写 .new.zip 再原子替换，别一上来就 os.remove 掉旧包。
    # 直接删目标的问题是：压缩过程一旦失败（比如磁盘满、被中断），
    # 旧的 CSVisual-源码包.zip 已经没了，用户手上一个能用的包都不剩。
    out = os.path.abspath(args.out)
    tmp = out + '.new'
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)

    log('  正在压缩到 %s（完成后替换正式包）' % tmp)
    written, raw = build_zip(jobs, tmp, with_runtime and runtime_ready)
    try:
        size = os.path.getsize(tmp)
    except OSError:
        size = 0

    # 千万别在 replace 之前先把旧的正式包删掉：
    #   1. os.replace 本身就是原子的覆盖替换（Windows 上会把目标原地顶掉），
    #      不需要先清理，删它是多余的一步；
    #   2. 本机运行环境挂了删除守卫，删旧包会被拦下并抛 SystemExit，
    #      脚本停在一半 —— 此时正式包已经没了，一个能用的包都不剩。
    # 保留 .new 临时文件则是为了给原子替换留退路：压缩失败时正式包不受影响。
    os.replace(tmp, out)

    log('')
    log('  完成：%s' % out)
    log('  写入 %d 个文件，%s → %s' % (written, human(raw), human(size)))
    log('')
    if with_runtime and runtime_ready:
        log('  把这个 zip 发给朋友即可。对方解压后双击 start-python.bat，')
        log('  五种语言都能直接跑，不用自己装任何编译器。')
    else:
        log('  把这个 zip 发给朋友即可。对方解压后双击 start-python.bat 就能用，')
        log('  但代码运行依赖他本机已有的编译器。')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:  # pragma: no cover
        log('\n  已取消。')
        sys.exit(130)
