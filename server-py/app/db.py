"""
数据库访问层（PyMySQL 连接池）

设计要点：
  1. continue 使用 Node 版同款 SQL 写法（占位符 `?`），由本模块转换为 PyMySQL 可用的形式，
     迁移时 SQL 可以原样照搬，避免手工改写成 `%s` 时漏改、错改。
  2. 一律参数化改写，不做裸字符串拼接。
  3. 返回 dict（DictCursor），字段访问方式与 Node 的 mysql2 RowDataPacket 一致。
"""

import os
import threading
from typing import Any, Dict, List, Optional, Sequence

import pymysql
from dbutils.pooled_db import PooledDB
from pymysql.converters import escape_item
from pymysql.cursors import DictCursor

# 保证 .env 已加载（独立运行迁移脚本时也必须生效，等价于 Node 版 db.js 顶部的 dotenv.config）
import app.core.config as _app_config  # noqa: E402,F401

_env_cache = None


def _load_config() -> Dict[str, Any]:
    global _env_cache
    if _env_cache is None:
        _env_cache = {
            'host': os.getenv('DB_HOST') or '127.0.0.1',
            'port': int(os.getenv('DB_PORT') or 3306),
            'user': os.getenv('DB_USER') or 'root',
            # 空密码场景必须保留为空串，不能回退成默认密码 —— 所以这里逐项判 None 而非用 env()
            'password': os.getenv('DB_PASSWORD') if os.getenv('DB_PASSWORD') is not None else 'root',
            'database': os.getenv('DB_NAME') or 'cs_visual',
            'charset': 'utf8mb4',
            'autocommit': True,
        }
    return _env_cache


_pool: Optional[PooledDB] = None
_lock = threading.Lock()


def get_pool() -> PooledDB:
    global _pool
    if _pool is None:
        with _lock:
            if _pool is None:
                _pool = PooledDB(
                    creator=pymysql,
                    maxconnections=10,
                    mincached=1,
                    maxcached=5,
                    blocking=True,
                    ping=1,
                    cursorclass=DictCursor,
                    **_load_config(),
                )
    return _pool


CHARSET = 'utf8mb4'


class Result:
    """与 Node 版 query() 返回结构对齐：{ rows, affectedRows, insertId }"""

    __slots__ = ('rows', 'affected_rows', 'insert_id')

    def __init__(self, rows: List[Dict], affected_rows: int, insert_id=0):
        self.rows = rows
        self.affected_rows = affected_rows
        self.insert_id = insert_id


def _interpolate(conn, sql: str, params: Sequence[Any]) -> str:
    """把 `?` 占位符替换为经驱动转义后的字面量。

    为什么不用 PyMySQL 自带的 `%s`：一旦传入 args，PyMySQL 会对整条 SQL 做一次
    `query % args` 的格式化，SQL 中原有的 `%`（如 LIKE '%x%'、DATE_FORMAT 的 %Y）
    都必须写成 `%%，否则报 unsupported format character。这里改为先转义再拼接，
    安全性与预编译等价（同样走驱动 escape），且 SQL 里可以放心出现 `%`。
    """
    if not params:
        return sql
    it = iter(params)
    out = []
    quote = None
    i = 0
    n = len(sql)
    while i < n:
        c = sql[i]
        if quote:
            out.append(c)
            if c == '\\':
                if i + 1 < n:
                    out.append(sql[i + 1])
                    i += 1
            elif c == quote:
                # 两个连续引号表示字面量中的一个引号
                if sql[i + 1:i + 2] == quote:
                    out.append(quote)
                    i += 1
                else:
                    quote = None
            i += 1
            continue
        if c in ("'", '"', '`'):
            quote = c
            out.append(c)
            i += 1
            continue
        if c == '?':
            try:
                val = next(it)
            except StopIteration:
                raise ValueError('SQL 参数数量不足: ' + sql)
            out.append(escape_item(val, CHARSET))
            i += 1
            continue
        out.append(c)
        i += 1
    return ''.join(out)


def query(sql: str, params: Optional[Sequence[Any]] = None) -> Result:
    """执行 SQL。返回结果对象；SELECT 走 rows，写操作走 affected_rows/insert_id。"""
    conn = get_pool().connection()
    try:
        real_sql = _interpolate(conn, sql, params or [])
        with conn.cursor() as cur:
            cur.execute(real_sql)
            if cur.description:
                rows = cur.fetchall()
                return Result(rows, 0)
            return Result([], cur.rowcount or 0, cur.lastrowid or 0)
    finally:
        conn.close()


def query_one(sql: str, params: Optional[Sequence[Any]] = None):
    r = query(sql, params)
    return r.rows[0] if r.rows else None


def ping() -> bool:
    try:
        query('SELECT 1')
        return True
    except Exception:
        return False


def connection():
    """取一条独占连接（迁移脚本需要会话变量 @aid / 事务时使用）。"""
    return get_pool().connection()
