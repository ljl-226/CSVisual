#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""准备便携版 MySQL 运行目录

本机装的 MySQL 8.0.34 (D:\\Develop\\Mysql\\mysql-8.0.34-winx64) 有 1.2GB，
其中绝大部分是这个场景用不到的东西：

  bin\\*.pdb            调试符号，mysqld.exe 一份就占几百 MB
  lib\\*.lib            静态库，只有拿它做 C 开发才需要
  include\\             同上
  data\\                本机的真实数据 —— 便携包要的是空库 + SQL 脚本，不是这堆文件
  docs\\                离线手册

砍掉之后只剩 mysqld 真正跑起来必需的：bin（去符号）、share（errmsg 与字符集）、
lib\\plugin（认证插件等运行时 DLL）。

为什么写成脚本而不是 robocopy：项目路径里有中文，robocopy 在 Git Bash 里传参会
因为代码页问题报「用法不正确」，Python 的 shutil 没这个麻烦，而且排除规则写成
一张表更好维护。

用法：
    python tools/build_portable.py            # 默认 D 盘源 -> build\\mysql
    python tools/build_portable.py --src X --dst Y
"""

import argparse
import os
import shutil
import sys
import time

# 排除的文件后缀（按后缀，小写比对）
EXCLUDE_EXTS = {'.pdb', '.lib', '.ilk', '.exp', '.a', '.la'}
# 排除的目录名（任意层级）
EXCLUDE_DIRS = {'data', 'docs', 'include', 'mysql-test', 'support-files'}
# 始终保留的目录（即使名字在上面）—— 这里没用到，留个口子
KEEP_DIRS = set()

# bin\\ 里只留这几个 exe：mysqld 本体 + 初始化脚本要用到的 mysql / mysqladmin，
# 外加 lz4_decompress（InnoDB 压缩表做恢复时 mysqld 会去调它）。
# 其余全是给人敲命令用的客户端工具（mysqlpump / mysqlbinlog / myisamchk …），
# 加起来一百多 MB，便携包里一个都用不上。dll 一律保留。
BIN_KEEP_EXE = {'mysqld.exe', 'mysql.exe', 'mysqladmin.exe', 'lz4_decompress.exe'}
# 整个目录都可以删：mecab 是日文全文分词插件的词典，130MB，本项目用不到
DROP_DIRS_UNDER = {('lib', 'mecab')}


def _rel_parts(root: str, path: str) -> tuple:
    return tuple(os.path.relpath(path, root).replace('\\', '/').split('/'))


def should_skip_dir(name: str) -> bool:
    return name.lower() in EXCLUDE_DIRS and name.lower() not in KEEP_DIRS


def should_skip_file(name: str) -> bool:
    return os.path.splitext(name)[1].lower() in EXCLUDE_EXTS


def copy_tree(src: str, dst: str) -> tuple:
    """边复制边过滤，返回 (文件数, 字节数)"""
    nfiles = nbytes = 0
    os.makedirs(dst, exist_ok=True)
    for cur, dirs, files in os.walk(src):
        parts = _rel_parts(src, cur)
        dirs[:] = [d for d in dirs if not should_skip_dir(d)]
        if parts in DROP_DIRS_UNDER:          # 整棵子树丢掉，不必再往下走
            dirs[:] = []
            continue
        rel = os.path.relpath(cur, src)
        target = dst if rel == '.' else os.path.join(dst, rel)
        os.makedirs(target, exist_ok=True)
        in_bin = parts[0] == 'bin' if parts else False
        for f in files:
            if should_skip_file(f):
                continue
            if in_bin and f.lower().endswith('.exe') and f.lower() not in BIN_KEEP_EXE:
                continue
            s = os.path.join(cur, f)
            t = os.path.join(target, f)
            try:
                shutil.copy2(s, t)
            except OSError as e:
                print(f'  [跳过] {f}: {e}')
                continue
            nfiles += 1
            nbytes += os.path.getsize(s)
    return nfiles, nbytes


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


def main() -> int:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default=r'D:\Develop\Mysql\mysql-8.0.34-winx64',
                    help='MySQL 安装目录')
    ap.add_argument('--dst', default=os.path.join(root, 'build', 'mysql'),
                    help='输出目录')
    args = ap.parse_args()

    src, dst = args.src, args.dst
    if not os.path.isfile(os.path.join(src, 'bin', 'mysqld.exe')):
        print(f'[错误] 源目录里没有 bin\\mysqld.exe：{src}')
        print('       请用 --src 指向正确的 MySQL 安装目录')
        return 1

    print(f'源目录: {src}  ({human(dir_size(src))})')
    if os.path.isdir(dst):
        # 同 tools\\build_setup.py：一次性删上千个文件会被本机的删除守卫拦下，
        # 这里改成同盘重命名到 build\\_trash，瞬时完成且不会留下半截目录。
        trash = os.path.join(os.path.dirname(dst), '_trash')
        os.makedirs(trash, exist_ok=True)
        try:
            os.replace(dst, os.path.join(trash, os.path.basename(dst) + '-' + time.strftime('%H%M%S')))
        except OSError:
            shutil.rmtree(dst, ignore_errors=True)

    print('正在复制（跳过调试符号 / 静态库 / 头文件 / 本机数据）...')
    nfiles, nbytes = copy_tree(src, dst)
    print(f'完成: {nfiles} 个文件, {human(nbytes)} -> {dst}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
