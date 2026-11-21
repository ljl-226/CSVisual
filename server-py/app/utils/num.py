"""与 Node 后端对齐的数值工具。

为什么不能直接用 Python 内置的 ``round()``：
Python 的 ``round()`` 是**银行家舍入**（四舍六入五取偶），而 JavaScript 的
``Math.round()`` 是**四舍五入**（.5 一律进位）。

    round(2.5)  -> 2        Math.round(2.5)  -> 3
    round(62.5) -> 62       Math.round(62.5) -> 63

本项目 Node/Express 与 Python/FastAPI 两套后端共用同一个 MySQL，
任何一处算分用了 ``round()``，同一个学生的同一份答卷就会算出两个分数
（实测：8 题答对 5 题，Python 给 62 分，Node 给 63 分）。

所有"算分 / 算百分比"的地方都必须走 ``round_half_up``。
"""

import math


def round_half_up(x) -> int:
    """四舍五入，半值进位 —— 对齐 Node 的 Math.round。

    JS 的 Math.round(x) 定义为 Math.floor(x + 0.5)，对正负数都不需要分支：
        Math.round(2.5)  = 3
        Math.round(-0.5) = -0  （不是 -1，这是最容易搞错的一条）
        Math.round(-1.5) = -1
    所以这里也统一用 floor(n + 0.5)。
    """
    try:
        n = float(x)
    except (TypeError, ValueError):
        return 0
    if not math.isfinite(n):
        return 0
    return int(math.floor(n + 0.5))


def round2(x) -> float:
    """保留 2 位小数，同样按四舍五入（用于 ratio / 覆盖率这类展示性数值）。"""
    try:
        n = float(x)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(n):
        return 0.0
    sign = -1 if n < 0 else 1
    return sign * math.floor(abs(n) * 100 + 0.5) / 100
