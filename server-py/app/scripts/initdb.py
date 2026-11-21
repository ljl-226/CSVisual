"""一键初始化数据库：建库建表 + 导入种子数据 + 题库。

用法: python -m app.scripts.initdb
注意: 执行前请在 .env 中配置好 DB_* 与 DB_NAME
"""

import os
import sys

import pymysql

from app.core.config import env
from app.scripts.migrate import _sql_dir, split_sql

FILES = ['schema.sql', 'seed.sql', 'question.sql', 'seed-math.sql', 'seed-plus.sql']


def main():
    cfg = {
        'host': env('DB_HOST', '127.0.0.1'),
        'port': int(env('DB_PORT', '3306')),
        'user': env('DB_USER', 'root'),
        'password': env('DB_PASSWORD', ''),
        'charset': 'utf8mb4',
    }
    print(f"连接目标: {cfg['user']}@{cfg['host']}:{cfg['port']}")
    conn = pymysql.connect(**cfg)

    db_name = env('DB_NAME', 'cs_visual')
    print(f'目标数据库: {db_name}')
    with conn.cursor() as cur:
        cur.execute(
            f'CREATE DATABASE IF NOT EXISTS `{db_name}` DEFAULT CHARACTER SET utf8mb4 '
            'DEFAULT COLLATE utf8mb4_general_ci'
        )
        cur.execute(f'USE `{db_name}`')

        # 已初始化过则跳过，避免重复运行脚本清空用户数据（答题记录/错题/注册账号）
        force = '--force' in sys.argv
        if not force:
            cur.execute(
                'SELECT COUNT(*) AS c FROM information_schema.tables WHERE table_schema = %s AND table_name = %s',
                (db_name, 'course'),
            )
            row = cur.fetchone()
            if row and row[0] > 0:
                cur.execute('SELECT COUNT(*) AS c FROM course')
                cnt = cur.fetchone()[0]
                if cnt > 0:
                    print(f'检测到已初始化过（course 表 {cnt} 条），跳过导数据以保留现有记录。')
                    print('如需清空重置，请执行: python -m app.scripts.initdb --force')
                    conn.close()
                    print('\n数据库就绪，无需重复初始化。')
                    return
        else:
            print('（--force）将清空并重建全部数据表...')

    print('已连接 MySQL，开始初始化数据库...')
    for f in FILES:
        path = os.path.join(_sql_dir(), f)
        if not os.path.exists(path):
            print('跳过（文件不存在）:', f)
            continue
        with open(path, 'r', encoding='utf-8') as fh:
            raw = fh.read()
        import re

        # 剥离文件里硬编码的 CREATE DATABASE / USE，统一使用上面的 DB_NAME
        raw = re.sub(r'CREATE\s+DATABASE[^;]*;', '', raw, flags=re.I)
        raw = re.sub(r'^\s*USE\s+[`\w]+;', '', raw, flags=re.I | re.M)
        with conn.cursor() as cur:
            for stmt in split_sql(raw):
                cur.execute(stmt)
        conn.commit()
        print('  ✓ 执行完成:', f)

    conn.close()
    print('\n数据库初始化成功！')
    print('管理员: admin / admin123')
    print('演示学生: student / 123456')
    print('\n接下来: cd ../web && npm run dev')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('初始化失败:', e)
        print('请确认 MySQL 已启动，且 .env 中账号密码正确')
        sys.exit(1)
