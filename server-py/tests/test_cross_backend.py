"""跨后端一致性保护：只会在真实 MySQL 上炸、且两套代码必须同对错的那类问题。

这里守的是 MySQL 5.7.5+ 的默认 sql_mode ONLY_FULL_GROUP_BY。

这类 SQL 特别阴险：它不是「数据不对」，而是「接口直接 500」。
而与此同时，另一套后端里一模一样的 SQL 也在等着炸 —— 差别只在于
谁先被某个测试撞上。下面这条就是真实案例：

    SELECT status, MAX(score) AS best, MAX(max_score) AS max_score
    FROM algorithm_submit WHERE user_id = ? AND algorithm_id = ?

裸列 status 没进 GROUP BY。MySQL 在**解析期**就拒绝（空表也一样报错），
所以 GET /api/algorithm/:id 直接返回 500。更麻烦的是它就算改成
ANY_VALUE(status) 也只是把它变成「返回哪一行不确定」——语义本来就不成立。

本项目两套后端（Node/Express 与 Python/FastAPI）对外接口逐字一致，
所以任何修在一边的东西，必须同时修在另一边。

2026-10-10：项目已收敛为**只有 Python 后端**，`server/`（Node 端）不再随项目分发。
本文件保留但整体跳过 —— 万一哪天把 Node 端放回 `server/`，跨端校验会自动复活。
"""

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
AGG = re.compile(r'\b(MAX|MIN|SUM|COUNT|AVG|GROUP_CONCAT)\s*\(', re.I)

pytestmark = pytest.mark.skipif(
    not (ROOT.parent / 'server' / 'src').exists(),
    reason='Node 后端 server/ 已移除，跨后端对比无对象（项目现为纯 Python 后端）',
)


def py_sqls(text):
    """Python 里相邻字符串会被解释器隐式拼接，ast 已经帮我们合并好了。"""
    out = []
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            out.append(node.value)
    return out


def js_sqls(text):
    """Node 版用模板字符串跨行，这里按反引号整段取。"""
    out = [m.group(1) for m in re.finditer(r'`([^`]*)`', text, re.S)]
    out += [m.group(1) for m in re.finditer(r"'((?:[^'\\]|\\.)*)'", text)]
    return out


def offending_statements(src, is_py):
    """找出「select 列表里有裸列 + 用了聚合 + 整句没有 GROUP BY」的 SELECT。"""
    found = []
    for raw in (py_sqls(src) if is_py else js_sqls(src)):
        stmt = ' '.join(raw.split())
        if not stmt.upper().startswith('SELECT'):
            continue
        if 'GROUP BY' in stmt.upper():
            continue
        # 聚合只出现在子查询里时，子查询自己带不带 GROUP BY 由它自己负责
        nosub = re.sub(r'\(\s*SELECT[\w\W]*?\)', '()', stmt, flags=re.I)
        if not AGG.search(nosub):
            continue
        m = re.search(r'^SELECT\s+([\w\W]*?)\s+FROM\s', nosub, re.I)
        if not m:
            continue
        bare = []
        for item in [x.strip() for x in m.group(1).split(',')]:
            col = re.sub(r'\s+AS\s+\w+$', '', item, flags=re.I).strip()
            if col == '*' or AGG.search(col) or '(' in col or col.upper().startswith('SELECT'):
                continue
            bare.append(item)
        if bare:
            found.append({'bare': bare, 'sql': stmt[:200]})
    return found


def scanned_targets():
    out = []
    for rel, is_py in [
        ('server/src/routes/algorithm.js', False),
        ('server/src/routes/admin.js', False),
        ('server/src/routes/agent.js', False),
        ('server/src/routes/course.js', False),
        ('server/src/routes/learn.js', False),
        ('server-py/app/routers/algorithm.py', True),
        ('server-py/app/routers/admin.py', True),
        ('server-py/app/routers/agent.py', True),
        ('server-py/app/routers/course.py', True),
        ('server-py/app/routers/learn.py', True),
    ]:
        p = ROOT / rel
        assert p.is_file(), '被扫描的文件不见了: %s' % rel
        out.append((rel, p.read_text(encoding='utf-8', errors='replace'), is_py))
    return out


def test_analyzer_actually_catches_the_known_bug():
    """先证明分析器自己有用。

    否则它迟早会退化成一个永远通过的空测试 —— 那种测试比没有更糟，
    因为它会让人误以为这条线有人守着。
    """
    bad_sql = (
        "SELECT status, MAX(score) AS best, MAX(max_score) AS max_score "
        "FROM algorithm_submit WHERE user_id = ? AND algorithm_id = ?"
    )
    py_src = "q = (\n    'SELECT status, MAX(score) AS best '\n    'FROM t WHERE x = ?'\n)"
    assert offending_statements(py_src, True), '分析器漏掉了已知的坏 SQL'

    good_sql = (
        "SELECT status, score AS best FROM algorithm_submit "
        "WHERE user_id = ? ORDER BY score DESC LIMIT 1"
    )
    py_ok = "q = (\n    'SELECT status, score AS best FROM t WHERE x = ? LIMIT 1'\n)"
    assert not offending_statements(py_ok, True), '分析器误报了正常 SQL'
    assert 'MAX(' in bad_sql and 'MAX(' not in good_sql


def test_no_select_mixes_bare_column_with_aggregate():
    """两套后端的聚合查询都不能出现裸列 —— 这是本节保护的主目标。"""
    hits = []
    for rel, src, is_py in scanned_targets():
        for bad in offending_statements(src, is_py):
            hits.append('%s -> 裸列 %s\n      %s' % (rel, bad['bare'], bad['sql']))
    assert not hits, (
        '以下查询会在 MySQL 默认的 ONLY_FULL_GROUP_BY 下报 1140（接口直接 500）。\n'
        '修法是把「取哪一行」写清楚（ORDER BY ... LIMIT 1 或加 GROUP BY），'
        '而不是 ANY_VALUE() 糊过去：\n  ' + '\n  '.join(hits)
    )


def _strip_comments(text, is_py):
    """去掉整行注释再检查。

    代码注释里很可能会写下「以前那个坏写法长什么样」，如果连注释一起扫，
    光是解释这段历史就会被自己判定为违规。
    """
    marker = '#' if is_py else '//'
    return '\n'.join(l for l in text.splitlines() if not l.strip().startswith(marker))


def _region_around(text, anchor, span=900):
    """取某个代码锚点之后的一小段，避免用全文断言误伤同文件里的合法写法。"""
    i = text.find(anchor)
    assert i >= 0, '找不到锚点 %s，源码结构变了' % anchor
    return text[i:i + span]


def test_detail_endpoint_query_is_semantically_explicit():
    """算法题详情那条查询既要不炸，也要明确指定取哪一行。

    这里特意把范围收在 myBest 赋值附近：同一个文件里列表接口也用
    MAX(score) AS best，但那句带了 GROUP BY algorithm_id，是合法的。
    用全文断言去禁一个字符串会误伤它 —— 精确的判断交给上面的分析器。
    """
    cases = [
        ('Python', ROOT / 'server-py/app/routers/algorithm.py', 'my_best = None', True),
        ('Node', ROOT / 'server/src/routes/algorithm.js', 'let myBest = null', False),
    ]
    for label, path, anchor, is_py in cases:
        src = _strip_comments(path.read_text(encoding='utf-8'), is_py)
        region = _region_around(src, anchor)
        # SQL 在源码里是分行拼接的，匹配必须允许跨换行（[^\\n] 会漏掉它们）
        assert re.search(r'ORDER BY[\s\S]{0,200}?LIMIT 1', region, re.I), \
            '%s 版详情里的 myBest 没有用 ORDER BY ... LIMIT 1 明确取哪一条提交' % label
        assert not AGG.search(re.sub(r'\(\s*SELECT[\w\W]*?\)', '()', region, flags=re.I)), \
            '%s 版详情里的 myBest 还在用聚合函数配裸列' % label
