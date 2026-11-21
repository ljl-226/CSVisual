"""参数校验工具。

从 Node 版 utils/validate.js 平移。所有来自客户端的 id / 数字 / 字符串都必须先过这一层，
避免非法值直接进 SQL 造成 500、脏数据或注入风险。
"""

import math
import re

from app.db import query_one

ID_RE = re.compile(r'^[1-9]\d{0,9}$')

JUDGE_OPTIONS = '[{"key":"A","text":"正确"},{"key":"B","text":"错误"}]'

TRUE_SET = ['T', 'TRUE', 'A', '对', '正确', '√', 'YES', 'Y', '1']
FALSE_SET = ['F', 'FALSE', 'B', '错', '错误', '×', 'X', 'NO', 'N', '0']


def is_id(v) -> bool:
    """是否为正整数 ID（拒绝 abc / -1 / 0 / 1.5 / 空串 / 注入串）"""
    return bool(ID_RE.match(str(v if v is not None else '').strip()))


def to_int(v, min_v: int = 1, max_v: int = 100, default: int = 10) -> int:
    """转成受控整数：非法值退回默认值，并限制上下界"""
    try:
        n = float(v)
    except (TypeError, ValueError):
        return default
    if n != n or n in (float('inf'), float('-inf')):  # NaN / Inf
        return default
    i = int(n)
    if i < min_v:
        return min_v
    if i > max_v:
        return max_v
    return i


def to_js_string(v) -> str:
    """按 JavaScript String() 的语义把任意 JSON 值转成字符串。

    为什么要单独写这个函数：Node 版到处用 `String(x)` 收口，
    而 Python 的 str() 与 JS 的 String() 在数组上行为完全不同——
        JS      String(['A','B'])  →  'A,B'
        Python  str(['A','B'])     →  "['A', 'B']"
    多选题的作答是数组，照搬 str() 会让答案永远对不上，判分恒为错。
    JSON 只可能送来 None / bool / 数字 / 字符串 / 数组 / 对象，逐个对齐即可。
    """
    if v is None:
        # JS: String(null) === 'null'，但业务上"没作答"应视为空串，保持与原版一致
        return ''
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, str):
        return v
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        # JS: String(1.0) === '1'，Python: str(1.0) === '1.0'
        return str(int(v)) if v.is_integer() else str(v)
    if isinstance(v, (list, tuple)):
        # JS: [].toString() === ''，[[1,2],[3]].toString() === '1,2,3'（摊平一层）
        return ','.join(to_js_string(x) for x in v)
    if isinstance(v, dict):
        return '[object Object]'
    return str(v)


def clamp_text(v, max_len: int = 500, default: str = '') -> str:
    """字符串收紧：底层一律走 to_js_string，保证与 Node 版 String(x) 行为一致。"""
    if v is None:
        return default
    return to_js_string(v)[:max_len]


def to_array(v):
    """确保是数组，且元素为非空 dict"""
    if not isinstance(v, list):
        return []
    return [x for x in v if isinstance(x, dict)]


def normalize_judge_answer(a):
    """把各种写法的判断答案归一到 A(正确) / B(错误)"""
    v = str(a if a is not None else '').strip().upper()
    if v in TRUE_SET:
        return 'A'
    if v in FALSE_SET:
        return 'B'
    return None


BOOL_TRUE = ['1', 'TRUE', 'T', 'YES', 'Y', 'ON', '是', '真']
BOOL_FALSE = ['0', 'FALSE', 'F', 'NO', 'N', 'OFF', '', '否', '假']


def to_bool_int(v, default=0) -> int:
    """把各种写法的布尔值统一成 0/1。

    必须与 Node 版 utils/validate.js 的 toBoolInt 逐值一致。

    曾经这里写成 int(v)，管理端传 null / 'abc' / 'true' 会抛
    TypeError / ValueError，整个接口直接 500 —— 管理员改个上下架状态都能把后台打挂。
    """
    if v is True:
        return 1
    if v is False or v is None:
        return 0
    if isinstance(v, bool):
        return 1 if v else 0
    if isinstance(v, (int, float)):
        if not math.isfinite(v):
            return default
        return 0 if v == 0 else 1
    s = str(v).strip().upper()
    if s in BOOL_TRUE:
        return 1
    if s in BOOL_FALSE:
        return 0
    return default


def _normalize_multi(v) -> str:
    """多选答案归一化：抽出字母排序去重，让 "AB"、"BA"、"B,A" 等价"""
    return ''.join(sorted(set(ch for ch in str(v or '').upper() if ch.isalpha())))


def is_answer_correct(right, user_answer, qtype=None) -> bool:
    """
    判断作答是否正确（兼容判断题 T/F、对/错、A/B 多种写法）。

    必须与 Node 版 utils/validate.js 的 isAnswerCorrect 行为完全一致 —— 两套后端
    共用同一个数据库，判分结果不同是会被学生直接看到的。

    两个坑，都真实发生过：
    1. 判断题的 T↔A、F↔B 跨写法互认，曾经对所有题型生效。于是标准答案为 A 的
       单选题，学生答 T / TRUE / 对 / YES / 1 全被判正确。互认必须限定在判断题内。
    2. 多选题按字符串全等比较，"AB" 与 "BA" 判错。应按集合比较。
    """
    r = str(right or '').strip().upper()
    u = str(user_answer or '').strip().upper()
    if not u:
        return False

    if qtype == 'multi':
        rn, un = _normalize_multi(r), _normalize_multi(u)
        return bool(rn) and rn == un

    if r == u:
        return True

    if qtype == 'judge':
        pair = {'A': 'T', 'T': 'A', 'B': 'F', 'F': 'B'}
        if pair.get(r) and pair[r] == u:
            return True
        if r in TRUE_SET and u in TRUE_SET:
            return True
        if r in FALSE_SET and u in FALSE_SET:
            return True
    return False


ALLOWED_EXISTS_TABLES = [
    'course', 'knowledge', 'question', 'visualization', 'user',
    'algorithm', 'algorithm_case', 'chat_session', 'chat_record',
]


def exists(table: str, id_value) -> bool:
    """校验资源是否存在。表名白名单：新增表后必须同步登记，否则一律返回 False。"""
    if table not in ALLOWED_EXISTS_TABLES:
        return False
    if not is_id(id_value):
        return False
    row = query_one(f'SELECT id FROM `{table}` WHERE id = ?', [id_value])
    return bool(row)


__all__ = [
    'is_id', 'to_int', 'clamp_text', 'to_array', 'exists',
    'JUDGE_OPTIONS', 'normalize_judge_answer', 'is_answer_correct',
    'TRUE_SET', 'FALSE_SET',
]
