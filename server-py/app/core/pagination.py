"""列表分页的公共骨架（全项目唯一的分页实现，Python 端）。

约定（与前端 PaginationBar 组件配套，Node 端 utils/paginate.js 行为一致）：
- page/pageSize 不传或传 0 → 返回全量（兼容旧调用方），pageSize 回传 total；
- 响应里 data 恒为数组，total/page/pageSize 平铺在响应顶层；
- where_sql 必须自带 FROM（COUNT 只数行数，借不到 select 里的表名，
  把 FROM 写进 select_sql 会拼出 `SELECT COUNT(*) AS total WHERE 1=1` 语法错误）。
"""

from app.core.response import ok
from app.db import query, query_one

MAX_PAGE_SIZE = 2000


def paginate(where_sql: str, params: list, select_sql: str, order_sql: str,
             page: int, pageSize: int):
    total = int(query_one('SELECT COUNT(*) AS total' + where_sql, list(params))['total'] or 0)
    size = max(0, min(int(pageSize or 0), MAX_PAGE_SIZE))
    cur = max(1, int(page or 1))
    sql = select_sql + where_sql + order_sql
    run_params = list(params)
    if size > 0:
        sql += ' LIMIT ? OFFSET ?'
        run_params += [size, (cur - 1) * size]
    rows = list(query(sql, run_params).rows)
    body = ok(rows)
    body['total'] = total
    body['page'] = cur
    body['pageSize'] = size or total
    return body
