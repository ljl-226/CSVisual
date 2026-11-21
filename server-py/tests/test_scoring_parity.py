"""跨后端判分一致性测试

本项目有 Node/Express 与 Python/FastAPI 两套后端，**共用同一个 MySQL**。
任何判分规则只修一边，同一份答卷就会在两套后端得到不同分数 —— 学生会直接看到。
而这类偏差靠单侧测试永远发现不了：Node 的测试跑 Node 的实现，Python 的测试跑
Python 的实现，各自都是绿的。

这里做两件事：
1. **对齐**：同一批用例分别喂给两套实现，结果必须逐条相同。
2. **锚定期望**：先固定「什么是对的」，防止两套实现一起错某个方向还互相印证。

依赖 Node 运行时；若机器上没有 node，则跳过对齐部分、只跑期望锚定。
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from app.utils.validate import is_answer_correct
from app.agent.grading import detect_slack

ROOT = Path(__file__).resolve().parents[2]
NODE_CLI = ROOT / 'server' / 'scripts' / 'validate-cli.cjs'

_has_node = shutil.which('node') is not None and NODE_CLI.exists()

# (标准答案, 用户作答, 题型, 期望是否正确)
ANSWER_CASES = [
    # 单选题：单选的答案绝不能被判断题的互认规则带偏。
    # 曾经因为没有按题型区分，答案为 A 的单选答 T/TRUE/对/YES/1 全部判正确
    ('A', 'A', 'single', True),
    ('A', 'T', 'single', False),
    ('A', 'TRUE', 'single', False),
    ('A', '对', 'single', False),
    ('A', 'YES', 'single', False),
    ('A', '1', 'single', False),
    ('B', 'B', 'single', True),
    ('B', 'F', 'single', False),
    ('B', '错', 'single', False),
    ('B', '0', 'single', False),
    ('C', 'C', 'single', True),
    ('C', 'A', 'single', False),
    ('D', 'D', 'single', True),

    # 判断题：必须跨写法互认 T/F、对/错、A/B
    ('A', 'A', 'judge', True),
    ('A', 'T', 'judge', True),
    ('A', 'TRUE', 'judge', True),
    ('A', '对', 'judge', True),
    ('A', '正确', 'judge', True),
    ('B', 'B', 'judge', True),
    ('B', 'F', 'judge', True),
    ('B', 'FALSE', 'judge', True),
    ('B', '错', 'judge', True),
    ('B', '错误', 'judge', True),
    ('A', 'B', 'judge', False),
    ('B', 'A', 'judge', False),

    # 多选题：忽略填写顺序
    ('AB', 'AB', 'multi', True),
    ('AB', 'BA', 'multi', True),
    ('ABD', 'DBA', 'multi', True),
    ('A,B', 'B,A', 'multi', True),
    ('AB', 'AC', 'multi', False),
    ('AB', 'A', 'multi', False),
    ('ABC', 'ABCD', 'multi', False),

    # 边界：空作答
    ('A', '', 'single', False),
    ('A', '   ', 'single', False),
]

SLACK_CASES = [
    # 这些才是真敷衍
    ('不会', True),
    ('不知道', True),
    ('不清楚', True),
    ('没思路', True),
    ('好的', True),
    ('嗯', True),
    ('', True),
    ('abc', True),

    # 这些是认真作答，只是叙述里恰好带了「不会」这类词。
    # 曾经用无锚点的子串匹配，下面全部被判 0 分
    ('先这样处理，就不会出现重复访存的情况', False),
    ('如果不用信号量，就不知道哪个进程先执行了', False),
    ('引入虚存后程序不必了解物理内存的细节', False),
    ('TCP 通过三次握手建立连接，四次挥手释放连接', False),
    ('这道题的关键是不清楚的地方要先假设，再验证', False),
    ('这样就不会导致死锁，因为破坏了环路等待条件', False),
]


def _run_node(mode, payload):
    proc = subprocess.run(
        ['node', str(NODE_CLI), mode, json.dumps(payload, ensure_ascii=False)],
        capture_output=True, text=True, encoding='utf-8', timeout=90,
    )
    if proc.returncode != 0:
        pytest.fail('Node 侧执行失败：' + (proc.stderr or proc.stdout or '').strip()[:400])
    return json.loads(proc.stdout)


def test_answer_expected_values():
    """先锚定什么是对的，别让两套实现互相印证着一起错"""
    for right, user, qtype, expected in ANSWER_CASES:
        got = is_answer_correct(right, user, qtype)
        assert got is expected, (
            f'is_answer_correct({right!r}, {user!r}, {qtype!r}) = {got}，应为 {expected}'
        )


def test_slack_expected_values():
    for answer, expected in SLACK_CASES:
        got = bool(detect_slack(answer)['hit'])
        assert got is expected, f'detect_slack({answer!r}) = {got}，应为 {expected}'


@pytest.mark.skipif(not _has_node, reason='本机没有 node，跳过对齐校验')
def test_answer_matches_node():
    payload = [{'r': r, 'u': u, 't': t} for r, u, t, _ in ANSWER_CASES]
    node_out = _run_node('answer', payload)
    assert len(node_out) == len(ANSWER_CASES), 'Node 返回结果数量不符'

    mismatch = []
    for (right, user, qtype, expected), got_node in zip(ANSWER_CASES, node_out):
        got_py = is_answer_correct(right, user, qtype)
        if bool(got_py) != bool(got_node):
            mismatch.append(
                f'({right!r}, {user!r}, {qtype!r}): Node={got_node} Python={got_py}'
            )
        if bool(got_node) != expected:
            mismatch.append(
                f'({right!r}, {user!r}, {qtype!r}): Node 结果 {got_node} 与期望 {expected} 不符'
            )
    assert not mismatch, '两套后端判分结果不一致：\n  ' + '\n  '.join(mismatch)


@pytest.mark.skipif(not _has_node, reason='本机没有 node，跳过对齐校验')
def test_slack_matches_node():
    node_out = _run_node('slack', [a for a, _ in SLACK_CASES])
    assert len(node_out) == len(SLACK_CASES), 'Node 返回结果数量不符'

    mismatch = []
    for (answer, expected), got_node in zip(SLACK_CASES, node_out):
        got_py = bool(detect_slack(answer)['hit'])
        if got_py != bool(got_node):
            mismatch.append(f'{answer!r}: Node={got_node} Python={got_py}')
        if bool(got_node) != expected:
            mismatch.append(f'{answer!r}: Node 结果 {got_node} 与期望 {expected} 不符')
    assert not mismatch, '两套后端敷衍作答判定不一致：\n  ' + '\n  '.join(mismatch)


# ---------------------------------------------------------------------------
# 舍入：Python round() 是银行家舍入，Node Math.round() 是四舍五入。
# 同一份答卷在两套后端必须同分，否则学生会看到自己的分数跳变。
# ---------------------------------------------------------------------------

ROUND_CASES = [
    # (输入, Math.round 的期望值)
    (2.5, 3),      # Python round -> 2（差 1 分）
    (62.5, 63),    # Python round -> 62（差 1 分）
    (0.5, 1),      # Python round -> 0
    (1.5, 2),      # Python round -> 2（一致）
    (3.5, 4),      # Python round -> 4（一致）
    (-0.5, 0),     # JS Math.round(-0.5) = -0 -> 0
    (10.4, 10),
    (10.6, 11),
    (0, 0),
    (100, 100),
]


def test_round_half_up_matches_math_round():
    """直接锚定四舍五入语义，不能退回内置的银行家舍入"""
    from app.utils.num import round_half_up

    for value, expected in ROUND_CASES:
        got = round_half_up(value)
        assert got == expected, f'round_half_up({value}) = {got}，应为 {expected}'


@pytest.mark.skipif(not _has_node, reason='本机没有 node，跳过对齐校验')
def test_round_matches_node():
    """真实跑一遍 Node 的 Math.round，逐条比对"""
    proc = subprocess.run(
        ['node', '-e',
         'const c=JSON.parse(process.argv[1]);console.log(JSON.stringify(c.map(Math.round)))',
         json.dumps([v for v, _ in ROUND_CASES])],
        capture_output=True, text=True, encoding='utf-8', timeout=60,
    )
    assert proc.returncode == 0, 'Node 执行失败：' + proc.stderr[:300]
    node_out = json.loads(proc.stdout)

    from app.utils.num import round_half_up

    mismatch = []
    for (value, expected), node_val in zip(ROUND_CASES, node_out):
        py_val = round_half_up(value)
        if py_val != node_val:
            mismatch.append(f'{value}: Node={node_val} Python={py_val}')
        if node_val != expected:
            mismatch.append(f'{value}: Node 结果 {node_val} 与记录值 {expected} 不符')
    assert not mismatch, '舍入行为与 Node 不一致：\n  ' + '\n  '.join(mismatch)


def test_source_has_no_bare_round_in_scoring():
    """静态守卫：算分路径上不许再出现裸 round()，防止以后又写回去"""
    import ast

    offenders = []
    for path in [
        ROOT / 'server-py' / 'app' / 'agent' / 'grading.py',
        ROOT / 'server-py' / 'app' / 'agent' / 'report.py',
        ROOT / 'server-py' / 'app' / 'routers' / 'question.py',
        ROOT / 'server-py' / 'app' / 'routers' / 'algorithm.py',
    ]:
        if not path.exists():
            continue
        tree = ast.parse(path.read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == 'round':
                    offenders.append(f'{path.name}:{node.lineno} 使用了内置 round()')
    assert not offenders, (
        '这些位置必须用 app.utils.num.round_half_up（与 Node 的 Math.round 对齐）：\n  '
        + '\n  '.join(offenders)
    )


# ---------------------------------------------------------------------------
# 布尔字段（上下架 status / 是否样例用例 isSample）
# 管理端传 null / "abc" / "true" 是常事，不能崩也不能误判为真
# ---------------------------------------------------------------------------

# (输入, 期望)
BOOL_CASES = [
    (True, 1), (False, 0),
    (1, 1), (0, 0),
    ('1', 1), ('0', 0),
    ('true', 1), ('false', 0),
    ('TRUE', 1), ('FALSE', 0),
    ('ON', 1), ('OFF', 0),
    ('', 0),
    (None, 0),
    ('abc', 0),        # 非法值按下架处理（Node 旧实现会误判成 1）
    (2, 1),            # 非 0 数字视为真
]


def test_bool_expected_values():
    from app.utils.validate import to_bool_int

    for value, expected in BOOL_CASES:
        got = to_bool_int(value)
        assert got == expected, f'to_bool_int({value!r}) = {got}，应为 {expected}'


@pytest.mark.skipif(not _has_node, reason='本机没有 node，跳过对齐校验')
def test_bool_matches_node():
    from app.utils.validate import to_bool_int

    # None 过不了 JSON，用逐条调用代替批量
    for value, expected in BOOL_CASES:
        if value is None:
            continue
        node_out = _run_node('bool', [value])
        assert len(node_out) == 1
        got_py = to_bool_int(value)
        assert bool(got_py) == bool(node_out[0]), (
            f'to_bool_int({value!r}): Node={node_out[0]} Python={got_py}'
        )
        assert int(node_out[0]) == expected, (
            f'to_bool_int({value!r}): Node 结果 {node_out[0]} 与期望 {expected} 不符'
        )


def test_admin_has_no_bare_int_cast():
    """静态守卫：admin 路由里不许对布尔字段用裸 int()，否则一个 null 就是 500。

    difficulty / weight / sortNo 这类真正的整数字段允许用 int()，
    但必须写在 `int(v) if str(v).isdigit() else 0` 这种被 isdigit 短路保护的形式里 ——
    短路求值保证 int() 只在确定是数字时才执行，这类一律放行。
    """
    import ast

    path = ROOT / 'server-py' / 'app' / 'routers' / 'admin.py'
    tree = ast.parse(path.read_text(encoding='utf-8'))

    # 被 isdigit 短路保护的位置视为安全
    safe_lines = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.IfExp) and 'isdigit' in ast.dump(node.test):
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call) and getattr(sub.func, 'id', None) == 'int':
                    safe_lines.add(sub.lineno)

    def _arg_name(call):
        for a in call.args:
            if isinstance(a, ast.Name):
                return a.id
        return None

    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, 'id', None) == 'int':
            if node.lineno in safe_lines:
                continue
            name = _arg_name(node)
            # 只盯一眼就看出是布尔语义的那些字段名
            if name in ('v', 'is_sample', 'status', 'isSample'):
                offenders.append(f'admin.py:{node.lineno} 对 {name} 用了未受保护的 int()')
    assert not offenders, '改用 to_bool_int()：\n  ' + '\n  '.join(offenders)
