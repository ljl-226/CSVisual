# -*- coding: utf-8 -*-
"""端到端校验：用项目自身的判题引擎 judge() 跑每道新算法题的参考代码，应当全部 AC"""
import sys

sys.path.insert(0, 'server-py')

from app.db import query
from app.routers.algorithm import judge

LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 30
OFFSET = int(sys.argv[2]) if len(sys.argv) > 2 else 0

rows = query(
    "SELECT id, title, reference_code FROM algorithm WHERE source = '洛谷' "
    "ORDER BY id LIMIT ? OFFSET ?", (LIMIT, OFFSET)).rows

ok = 0
bad = []
for r in rows:
    cases = query('SELECT stdin, expected FROM algorithm_case WHERE algorithm_id = ? ORDER BY sort_no',
                  (r['id'],)).rows
    res = judge([dict(c) for c in cases], 'python', r['reference_code'])
    if res['status'] == 'accepted':
        ok += 1
    else:
        bad.append((r['id'], r['title'], res['status'], res['message'][:200]))

print('校验题目数: %d，通过: %d，失败: %d' % (len(rows), ok, len(bad)))
for b in bad:
    print('  [失败] id=%s %s -> %s | %s' % b)
sys.exit(1 if bad else 0)
