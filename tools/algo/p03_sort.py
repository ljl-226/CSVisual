# -*- coding: utf-8 -*-
"""第三批：排序、二分、前缀和与差分（25 道）"""
from common import P


def _gen_ints(r, n=None, lo=-1000, hi=1000):
    n = n or r.randint(2, 20)
    return '%d\n%s' % (n, ' '.join(str(r.randint(lo, hi)) for _ in range(n)))


def _gen_two_sorted(r):
    """生成两个长度与声明一致的升序数组"""
    n = r.randint(1, 15)
    m = r.randint(1, 15)
    a = ' '.join(str(x) for x in sorted(r.randint(0, 60) for _ in range(n)))
    b = ' '.join(str(x) for x in sorted(r.randint(0, 60) for _ in range(m)))
    return '%d %d\n%s\n%s' % (n, m, a, b)


def _gen_cubic(r):
    """随机取三个互不相同的整数根，展开成一元三次方程系数"""
    a = r.choice([1, 2, -1, 3])
    roots = r.sample(range(-20, 21), 3)
    s1 = sum(roots)
    s2 = roots[0] * roots[1] + roots[0] * roots[2] + roots[1] * roots[2]
    s3 = roots[0] * roots[1] * roots[2]
    return '%d %d %d %d' % (a, -a * s1, a * s2, -a * s3)


PROBLEMS = [
    P('排序输出', 2,
      '输入 n 个整数，按从小到大排序后输出。',
      '两行。第一行一个整数 n；第二行 n 个整数。',
      '一行，n 个整数，为排序结果，用空格分隔。',
      '5\n3 1 4 1 5', '1 1 3 4 5',
      'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nnums = list(map(int, data[1:1 + n]))\nnums.sort()\nprint(" ".join(map(str, nums)))\n',
      lambda r: _gen_ints(r, hi=10000),
      hint='直接使用内置排序（Timsort / 快排）即可，平均复杂度 O(n log n)。',
      scope='1 ≤ n ≤ 10⁵', tags='排序,入门', kid=6),

    P('第 k 小的数', 2,
      '输入 n 个整数与一个整数 k，输出其中第 k 小的数（k 从 1 开始计数，重复元素分别计数）。',
      '两行。第一行两个整数 n、k；第二行 n 个整数。',
      '一行，一个整数，表示第 k 小的数。',
      '5 3\n3 1 4 1 5', '3',
      'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nk = int(data[1])\nnums = sorted(map(int, data[2:2 + n]))\nprint(nums[k - 1])\n',
      lambda r: (lambda n: '%d %d\n%s' % (n, r.randint(1, n), ' '.join(str(r.randint(0, 999)) for _ in range(n))))(
          r.randint(1, 40)),
      hint='排序后直接取下标 k-1，O(n log n)；若只需 Top-K，可用堆或快速选择做到 O(n log k)。',
      scope='1 ≤ k ≤ n ≤ 10⁵', tags='排序,选择问题', kid=6),

    P('逆序对个数', 3,
      '给定一个长度为 n 的序列，求其中逆序对的个数。逆序对指满足 i < j 且 a[i] > a[j] 的数对。',
      '两行。第一行一个整数 n；第二行 n 个整数。',
      '一行，一个整数，表示逆序对个数。',
      '5\n3 1 4 1 5', '3',
      'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nnums = list(map(int, data[1:1 + n]))\n\n\ndef merge_sort(a):\n    if len(a) <= 1:\n        return a, 0\n    mid = len(a) // 2\n    left, c1 = merge_sort(a[:mid])\n    right, c2 = merge_sort(a[mid:])\n    merged = []\n    i = j = 0\n    cnt = c1 + c2\n    while i < len(left) and j < len(right):\n        if left[i] <= right[j]:\n            merged.append(left[i])\n            i += 1\n        else:\n            merged.append(right[j])\n            cnt += len(left) - i\n            j += 1\n    merged.extend(left[i:])\n    merged.extend(right[j:])\n    return merged, cnt\n\n\nprint(merge_sort(nums)[1])\n',
      lambda r: _gen_ints(r, hi=100),
      hint='归并排序时，右侧元素被选中说明它与左侧剩余的所有元素都构成逆序对，因此一次累加 len(left) - i。也可用树状数组 + 离散化求解。',
      scope='1 ≤ n ≤ 10⁵', tags='排序,归并,分治,逆序对', kid=7),

    P('有序数组的二分查找', 2,
      '给定一个升序排列的 n 个整数和 q 次询问，每次询问一个整数 x 是否出现在数组中，若在则输出其首次出现的下标（从 1 开始），否则输出 -1。',
      '第一行两个整数 n、q；第二行 n 个升序整数；接下来 q 行，每行一个整数 x。',
      'q 行，每行一个整数，表示查找结果。',
      '6 3\n1 2 2 3 4 5\n2\n6\n1', '2\n-1\n1',
      'import sys\nimport bisect\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nq = int(data[1])\nnums = list(map(int, data[2:2 + n]))\nout = []\nfor i in range(q):\n    x = int(data[2 + n + i])\n    pos = bisect.bisect_left(nums, x)\n    out.append(str(pos + 1) if pos < n and nums[pos] == x else "-1")\nprint("\\n".join(out))\n',
      lambda r: (lambda n, q: '%d %d\n%s\n%s' % (
          n, q, ' '.join(str(x) for x in sorted(r.randint(0, 50) for _ in range(n))),
          '\n'.join(str(r.randint(0, 55)) for _ in range(q))))(r.randint(1, 30), r.randint(1, 10)),
      hint='二分查找每次排除一半区间，复杂度 O(log n)；要找"首次出现"的位置应使用左边界二分（bisect_left）。',
      scope='1 ≤ n, q ≤ 10⁵', tags='二分,查找,数组', kid=40),

    P('木材加工', 3,
      '有 n 根原木，长度分别为 Lᵢ。现需要切出 k 段长度相同的小段（每段长度必须为整数），求小段的最大可能长度；若无法切出 k 段则输出 0。',
      '第一行两个整数 n、k；第二行 n 个整数，表示每根原木的长度。',
      '一行，一个整数，表示最大长度。',
      '3 7\n10 15 12', '5',
      'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nk = int(data[1])\nlogs = list(map(int, data[2:2 + n]))\nlo, hi = 0, max(logs)\nwhile lo < hi:\n    mid = (lo + hi + 1) // 2\n    if sum(L // mid for L in logs) >= k:\n        lo = mid\n    else:\n        hi = mid - 1\nprint(lo)\n',
      lambda r: '%d %d\n%s' % (r.randint(1, 20), r.randint(1, 50),
                               ' '.join(str(r.randint(1, 200)) for _ in range(r.randint(1, 20)))),
      hint='答案具有单调性：长度越小能切出的段数越多。对长度二分，判断"能否切出至少 k 段"，这是典型的二分答案模板。',
      scope='1 ≤ n ≤ 10⁵，1 ≤ k ≤ 10⁸，1 ≤ Lᵢ ≤ 10⁸', tags='二分答案,贪心,洛谷经典', kid=40),

    P('跳石头', 3,
      '一条河上有 n 块石头，起点到终点的距离为 L，石头到起点的距离已知（单调递增）。现要移走最多 m 块石头，使得剩余相邻石头（含起点与终点）之间最小距离尽可能大。求这个最大化的最小距离。',
      '第一行三个整数 L、n、m；第二行 n 个整数，表示每块石头到起点的距离（递增）。',
      '一行，一个整数，表示最优的最小跳跃距离。',
      '25 5 2\n2 11 14 17 21', '4',
      'import sys\n\ndata = sys.stdin.read().split()\nL = int(data[0])\nn = int(data[1])\nm = int(data[2])\nrocks = list(map(int, data[3:3 + n]))\n\n\ndef ok(d):\n    removed = 0\n    last = 0\n    for p in rocks:\n        if p - last < d:\n            removed += 1\n        else:\n            last = p\n    if L - last < d:\n        removed += 1\n    return removed <= m\n\n\nlo, hi = 0, L\nwhile lo < hi:\n    mid = (lo + hi + 1) // 2\n    if ok(mid):\n        lo = mid\n    else:\n        hi = mid - 1\nprint(lo)\n',
      lambda r: (lambda L, n: '%d %d %d\n%s' % (L, n, r.randint(0, max(0, n - 1)),
                                                ' '.join(str(x) for x in sorted(r.randint(1, L - 1) for _ in range(n)))))(
          r.randint(10, 1000), r.randint(1, 20)),
      hint='对"最小距离 d"二分：贪心地从左到右检查，若与上一块保留的石头距离小于 d 就移走当前石头，统计移走数量是否不超过 m。',
      scope='1 ≤ L ≤ 10⁹，1 ≤ n ≤ 5×10⁴，m ≤ n', tags='二分答案,贪心,洛谷经典', kid=40),

    P('一元三次方程求解', 3,
      '给定一元三次方程 ax³ + bx² + cx + d = 0 的四个整数系数，已知该方程在 [-100, 100] 内恰有三个不同实根，且任意两根之差的绝对值 ≥ 1。求这三个实根。',
      '一行，四个整数 a、b、c、d（a ≠ 0）。',
      '一行，三个实数，为三个根，从小到大排列，保留 2 位小数，用空格分隔。',
      '1 -6 11 -6', '1.00 2.00 3.00',
      'import sys\n\na, b, c, d = map(int, sys.stdin.read().split())\n\n\ndef f(x):\n    return ((a * x + b) * x + c) * x + d\n\n\nroots = []\ni = -100\nwhile i <= 100:\n    if abs(f(i)) < 1e-7:\n        roots.append(float(i))\n    elif i < 100 and f(i) * f(i + 1) < 0:\n        lo, hi = float(i), float(i + 1)\n        for _ in range(80):\n            mid = (lo + hi) / 2\n            if f(lo) * f(mid) <= 0:\n                hi = mid\n            else:\n                lo = mid\n        roots.append((lo + hi) / 2)\n    i += 1\nroots.sort()\nprint(" ".join("%.2f" % x for x in roots[:3]))\n',
      _gen_cubic,
      hint='先用步长 1 扫描找到根所在的区间（端点异号），再在区间内二分逼近；注意端点正好为根的情况要单独处理。',
      scope='-100 ≤ 系数 ≤ 100，a ≠ 0', tags='二分,数学,洛谷经典', kid=40),

    P('前缀和区间求和', 2,
      '给定一个长度为 n 的整数序列和 m 次询问，每次询问区间 [l, r] 的元素之和。',
      '第一行两个整数 n、m；第二行 n 个整数；接下来 m 行，每行两个整数 l、r。',
      'm 行，每行一个整数，表示对应区间的元素和。',
      '5 2\n1 2 3 4 5\n1 3\n2 5', '6\n14',
      'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nm = int(data[1])\nnums = list(map(int, data[2:2 + n]))\npre = [0]\nfor x in nums:\n    pre.append(pre[-1] + x)\nout = []\nfor i in range(m):\n    l = int(data[2 + n + 2 * i])\n    rr = int(data[3 + n + 2 * i])\n    out.append(str(pre[rr] - pre[l - 1]))\nprint("\\n".join(out))\n',
      lambda r: (lambda n, m: '%d %d\n%s\n%s' % (
          n, m, ' '.join(str(r.randint(-100, 100)) for _ in range(n)),
          '\n'.join((lambda a, b: '%d %d' % (min(a, b), max(a, b)))(r.randint(1, n), r.randint(1, n))
                    for _ in range(m))))(r.randint(1, 30), r.randint(1, 8)),
      hint='预处理前缀和 pre[i] = a₁ + … + aᵢ，则区间和为 pre[r] - pre[l-1]，每次询问 O(1)，总体 O(n + m)。',
      scope='1 ≤ n, m ≤ 10⁵', tags='前缀和,数组,查询'),

    P('最大子段和', 2,
      '给定一个长度为 n 的整数序列，求其连续子段的最大和（子段至少包含一个元素）。',
      '两行。第一行一个整数 n；第二行 n 个整数。',
      '一行，一个整数，表示最大子段和。',
      '7\n-2 11 -4 13 -5 -2 4', '20',
      'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nnums = list(map(int, data[1:1 + n]))\nbest = cur = nums[0]\nfor x in nums[1:]:\n    cur = max(x, cur + x)\n    best = max(best, cur)\nprint(best)\n',
      lambda r: _gen_ints(r, hi=50),
      hint='Kadane 算法：维护"以当前位置结尾的最大子段和"，状态转移 cur = max(x, cur + x)，一趟扫描 O(n)。',
      scope='1 ≤ n ≤ 10⁵', tags='动态规划,前缀和,最大子段和'),

    P('差分数组区间加法', 2,
      '给定一个长度为 n 的序列（初始全为 0）和 m 次操作，每次操作把区间 [l, r] 内的所有元素加上 v。求所有操作完成后的序列。',
      '第一行两个整数 n、m；接下来 m 行，每行三个整数 l、r、v。',
      '一行，n 个整数，为最终序列，用空格分隔。',
      '5 2\n1 3 2\n2 5 -1', '2 1 1 -1 -1',
      'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nm = int(data[1])\ndiff = [0] * (n + 2)\nfor i in range(m):\n    l = int(data[2 + 3 * i])\n    rr = int(data[3 + 3 * i])\n    v = int(data[4 + 3 * i])\n    diff[l] += v\n    diff[rr + 1] -= v\ncur = 0\nout = []\nfor i in range(1, n + 1):\n    cur += diff[i]\n    out.append(str(cur))\nprint(" ".join(out))\n',
      lambda r: (lambda n, m: '%d %d\n%s' % (n, m, '\n'.join(
          (lambda a, b: '%d %d %d' % (min(a, b), max(a, b), r.randint(-20, 20)))(r.randint(1, n), r.randint(1, n))
          for _ in range(m))))(r.randint(2, 30), r.randint(1, 8)),
      hint='区间加 [l, r] 只需 diff[l] += v、diff[r+1] -= v，最后做一次前缀和还原，整体 O(n + m)，比逐个元素加的 O(nm) 快得多。',
      scope='1 ≤ n, m ≤ 10⁵', tags='差分,数组,区间操作'),

    P('借教室', 3,
      '有 n 天，第 i 天最多可借出 rᵢ 间教室。现有 m 份订单，第 j 份订单要在第 sⱼ 天到第 tⱼ 天每天借 dⱼ 间教室。请按订单顺序处理，输出第一份无法满足的订单编号；若全部满足则输出 0。',
      '第一行两个整数 n、m；第二行 n 个整数 rᵢ；接下来 m 行，每行三个整数 dⱼ、sⱼ、tⱼ。',
      '一行，一个整数，表示第一个无法满足的订单编号（全部满足输出 0）。',
      '4 3\n2 5 4 3\n2 1 3\n3 2 4\n4 2 4', '2',
      'import sys\n\ndata = sys.stdin.read().split()\nidx = 0\nn = int(data[idx]); idx += 1\nm = int(data[idx]); idx += 1\nroom = list(map(int, data[idx:idx + n])); idx += n\norders = []\nfor _ in range(m):\n    d = int(data[idx]); s = int(data[idx + 1]); t = int(data[idx + 2]); idx += 3\n    orders.append((d, s, t))\n\n\ndef feasible(k):\n    diff = [0] * (n + 2)\n    for i in range(k):\n        d, s, t = orders[i]\n        diff[s] += d\n        diff[t + 1] -= d\n    used = 0\n    for i in range(1, n + 1):\n        used += diff[i]\n        if used > room[i - 1]:\n            return False\n    return True\n\n\nlo, hi = 0, m\nwhile lo < hi:\n    mid = (lo + hi + 1) // 2\n    if feasible(mid):\n        lo = mid\n    else:\n        hi = mid - 1\nprint(0 if lo == m else lo + 1)\n',
      lambda r: (lambda n, m: '%d %d\n%s\n%s' % (
          n, m, ' '.join(str(r.randint(1, 30)) for _ in range(n)),
          '\n'.join((lambda a, b: '%d %d %d' % (r.randint(1, 20), min(a, b), max(a, b)))(
              r.randint(1, n), r.randint(1, n)) for _ in range(m))))(r.randint(2, 20), r.randint(1, 10)),
      hint='"前 k 份订单是否都能满足"关于 k 单调，可二分订单数；每次判定用差分数组 O(n + k) 求出每天用量。',
      scope='1 ≤ n, m ≤ 10⁶（本题数据较小）', tags='差分,二分答案,洛谷经典'),

    P('二维前缀和', 3,
      '给定一个 n 行 m 列的矩阵和 q 次询问，每次询问以 (x₁, y₁) 为左上角、(x₂, y₂) 为右下角的子矩阵元素之和。',
      '第一行三个整数 n、m、q；接下来 n 行，每行 m 个整数；接下来 q 行，每行四个整数 x₁、y₁、x₂、y₂。',
      'q 行，每行一个整数，表示子矩阵之和。',
      '3 3 2\n1 2 3\n4 5 6\n7 8 9\n1 1 2 2\n1 1 3 3', '12\n45',
      'import sys\n\ndata = sys.stdin.read().split()\nidx = 0\nn = int(data[idx]); m = int(data[idx + 1]); q = int(data[idx + 2]); idx += 3\npre = [[0] * (m + 1) for _ in range(n + 1)]\nfor i in range(1, n + 1):\n    for j in range(1, m + 1):\n        v = int(data[idx]); idx += 1\n        pre[i][j] = v + pre[i - 1][j] + pre[i][j - 1] - pre[i - 1][j - 1]\nout = []\nfor _ in range(q):\n    x1 = int(data[idx]); y1 = int(data[idx + 1]); x2 = int(data[idx + 2]); y2 = int(data[idx + 3]); idx += 4\n    out.append(str(pre[x2][y2] - pre[x1 - 1][y2] - pre[x2][y1 - 1] + pre[x1 - 1][y1 - 1]))\nprint("\\n".join(out))\n',
      lambda r: (lambda n, m, q: '%d %d %d\n%s\n%s' % (
          n, m, q, '\n'.join(' '.join(str(r.randint(0, 20)) for _ in range(m)) for _ in range(n)),
          '\n'.join((lambda a, b, c, d: '%d %d %d %d' % (min(a, c), min(b, d), max(a, c), max(b, d)))(
              r.randint(1, n), r.randint(1, m), r.randint(1, n), r.randint(1, m)) for _ in range(q))))(
          r.randint(2, 8), r.randint(2, 8), r.randint(1, 5)),
      hint='二维前缀和：pre[i][j] = a[i][j] + pre[i-1][j] + pre[i][j-1] - pre[i-1][j-1]，查询用容斥原理 O(1)。',
      scope='1 ≤ n, m ≤ 10³，1 ≤ q ≤ 10⁵', tags='前缀和,矩阵,查询'),

    P('有序数组的两数之和', 2,
      '给定升序排列的 n 个整数和一个目标值 t，判断是否存在两个不同位置的元素之和恰好等于 t。存在输出 Yes，否则输出 No。',
      '第一行两个整数 n、t；第二行 n 个升序整数。',
      '一行，Yes 或 No。',
      '5 9\n1 2 3 6 8', 'Yes',
      'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nt = int(data[1])\nnums = list(map(int, data[2:2 + n]))\ni, j = 0, n - 1\nok = False\nwhile i < j:\n    s = nums[i] + nums[j]\n    if s == t:\n        ok = True\n        break\n    elif s < t:\n        i += 1\n    else:\n        j -= 1\nprint("Yes" if ok else "No")\n',
      lambda r: (lambda n: '%d %d\n%s' % (n, r.randint(0, 100),
                                          ' '.join(str(x) for x in sorted(r.randint(0, 50) for _ in range(n)))))(
          r.randint(2, 30)),
      hint='利用有序性用双指针：和偏小则左指针右移，偏大则右指针左移，一趟 O(n)，比哈希表的 O(n) 更省空间。',
      scope='1 ≤ n ≤ 10⁵', tags='双指针,数组,查找'),

    P('盛最多水的容器', 3,
      '给定 n 个非负整数 a₁…aₙ，第 i 个数表示坐标 (i, aᵢ) 处有一块竖直挡板。求任意两块挡板与 x 轴构成的容器能容纳的最大水量（即 max(|i - j| × min(aᵢ, aⱼ))）。',
      '两行。第一行一个整数 n；第二行 n 个非负整数。',
      '一行，一个整数，表示最大水量。',
      '6\n1 3 5 2 4 6', '15',
      'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nnums = list(map(int, data[1:1 + n]))\ni, j = 0, n - 1\nbest = 0\nwhile i < j:\n    water = (j - i) * min(nums[i], nums[j])\n    best = max(best, water)\n    if nums[i] < nums[j]:\n        i += 1\n    else:\n        j -= 1\nprint(best)\n',
      lambda r: _gen_ints(r, hi=50),
      hint='双指针从两端向中间收缩：每次移动较矮的那一侧（因为移动高的一侧不可能得到更优解），整体 O(n)。',
      scope='1 ≤ n ≤ 10⁵', tags='双指针,贪心,数组'),

    P('合并两个有序数组', 2,
      '给定两个升序排列的整数数组，将它们合并为一个升序数组并输出。',
      '第一行两个整数 n、m；第二行 n 个升序整数；第三行 m 个升序整数。',
      '一行，n + m 个整数，为合并后的升序数组，用空格分隔。',
      '3 4\n1 3 5\n2 4 6 8', '1 2 3 4 5 6 8',
      'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nm = int(data[1])\na = list(map(int, data[2:2 + n]))\nb = list(map(int, data[2 + n:2 + n + m]))\ni = j = 0\nout = []\nwhile i < n and j < m:\n    if a[i] <= b[j]:\n        out.append(a[i]); i += 1\n    else:\n        out.append(b[j]); j += 1\nout.extend(a[i:])\nout.extend(b[j:])\nprint(" ".join(map(str, out)))\n',
      _gen_two_sorted,
      hint='二路归并：两个指针分别扫描两个数组，每次取较小者，O(n + m)。这与归并排序的合并步骤完全相同。',
      scope='1 ≤ n, m ≤ 10⁵', tags='归并,双指针,数组', kid=7),

    P('成绩排序', 2,
      '给定 n 名学生的语文、数学、英语成绩与学号，按总分降序排序；总分相同时按语文成绩降序；仍相同时按学号升序。输出排序后的学号序列。',
      '第一行一个整数 n；接下来 n 行，每行四个整数：学号、语文、数学、英语。',
      '一行，n 个整数，为排序后的学号序列，用空格分隔。',
      '3\n1 90 80 70\n2 90 70 80\n3 80 90 90', '3 1 2',
      'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nstus = []\nfor i in range(n):\n    sid, cn, ma, en = map(int, data[1 + 4 * i:5 + 4 * i])\n    stus.append((-(cn + ma + en), -cn, sid))\nstus.sort()\nprint(" ".join(str(s[2]) for s in stus))\n',
      lambda r: (lambda n: '%d\n%s' % (n, '\n'.join(
          '%d %d %d %d' % (i + 1, r.randint(50, 100), r.randint(50, 100), r.randint(50, 100)) for i in range(n))))(
          r.randint(1, 20)),
      hint='多关键字排序：把"降序"的键取负数即可用统一升序排序；Python 的 sort 默认按元组字典序比较。',
      scope='1 ≤ n ≤ 10⁵', tags='排序,多关键字', kid=6),

    P('第 k 大的数（快速选择）', 2,
      '给定 n 个整数与整数 k，输出其中第 k 大的数（k 从 1 开始，重复元素分别计数）。要求不使用完整排序。',
      '两行。第一行两个整数 n、k；第二行 n 个整数。',
      '一行，一个整数，表示第 k 大的数。',
      '6 2\n3 1 5 2 5 4', '5',
      'import sys\nimport heapq\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nk = int(data[1])\nnums = list(map(int, data[2:2 + n]))\nheap = []\nfor x in nums:\n    if len(heap) < k:\n        heapq.heappush(heap, x)\n    elif x > heap[0]:\n        heapq.heapreplace(heap, x)\nprint(heap[0])\n',
      lambda r: (lambda n: '%d %d\n%s' % (n, r.randint(1, n), ' '.join(str(r.randint(0, 99)) for _ in range(n))))(
          r.randint(1, 40)),
      hint='维护一个大小为 k 的小顶堆：堆顶就是第 k 大。复杂度 O(n log k)，比全排序的 O(n log n) 更省。',
      scope='1 ≤ k ≤ n ≤ 10⁵', tags='堆,选择问题,TopK', kid=37),

    P('三分法求极值', 3,
      '给定实数 p、q 和区间 [l, r]，求函数 f(x) = (x - p)² + q 在该区间上的最小值，保留 4 位小数。要求使用三分查找求解。',
      '一行，四个实数 p、q、l、r。',
      '一行，一个实数，表示最小值，保留 4 位小数。',
      '0 3 -5 5', '3.0000',
      'import sys\n\np, q, l, r = map(float, sys.stdin.read().split())\n\n\ndef f(x):\n    return (x - p) ** 2 + q\n\n\nfor _ in range(200):\n    m1 = l + (r - l) / 3\n    m2 = r - (r - l) / 3\n    if f(m1) < f(m2):\n        r = m2\n    else:\n        l = m1\nprint("%.4f" % f((l + r) / 2))\n',
      lambda r: '%.2f %.2f %.2f %.2f' % (r.uniform(-10, 10), r.uniform(-10, 10), r.uniform(-20, -5), r.uniform(5, 20)),
      hint='单峰（单谷）函数可用三分法：比较两个三等分点的函数值，舍去远离极值的一侧，迭代收敛。',
      scope='-100 ≤ p, q, l, r ≤ 100，l < r', tags='三分查找,数学,极值'),

    P('整数平方根', 2,
      '给定非负整数 x，求其算术平方根的整数部分（即不超过 √x 的最大整数）。',
      '一行，一个非负整数 x。',
      '一行，一个整数，表示 ⌊√x⌋。',
      '8', '2',
      'import sys\n\nx = int(sys.stdin.read().strip())\nlo, hi = 0, x\nwhile lo < hi:\n    mid = (lo + hi + 1) // 2\n    if mid * mid <= x:\n        lo = mid\n    else:\n        hi = mid - 1\nprint(lo)\n',
      lambda r: str(r.randint(0, 10**12)),
      hint='对答案二分：找到最大的 mid 使 mid² ≤ x。注意 mid * mid 在大数时可能溢出（C/C++ 需改用除法判断）。',
      scope='0 ≤ x ≤ 10¹²', tags='二分,数学,查找', kid=40),

    P('众数统计', 2,
      '给定 n 个整数，求出现次数最多的数（众数）；若有多个众数，输出其中最小的那个。同时输出它出现的次数。',
      '两行。第一行一个整数 n；第二行 n 个整数。',
      '一行，两个整数，依次为众数与其出现次数，用空格分隔。',
      '7\n1 2 1 3 2 1 4', '1 3',
      'import sys\nfrom collections import Counter\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nnums = list(map(int, data[1:1 + n]))\nif not nums:\n    print("0 0")\nelse:\n    cnt = Counter(nums)\n    best = min(cnt.items(), key=lambda kv: (-kv[1], kv[0]))\n    print(best[0], best[1])\n',
      lambda r: _gen_ints(r, hi=20),
      hint='哈希表统计频次，再按"次数降序、数值升序"取最优项；也可排序后一趟扫描统计连续段。',
      scope='1 ≤ n ≤ 10⁵', tags='哈希,统计,排序', kid=33),

    P('中位数', 2,
      '给定 n 个整数，求它们的中位数：若 n 为奇数，输出排序后正中间的数；若 n 为偶数，输出排序后中间两个数的平均值（保留 1 位小数）。',
      '两行。第一行一个整数 n；第二行 n 个整数。',
      '一行，中位数（偶数个时保留 1 位小数）。',
      '4\n1 2 3 4', '2.5',
      'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nnums = sorted(map(int, data[1:1 + n]))\nif n % 2:\n    print(nums[n // 2])\nelse:\n    print("%.1f" % ((nums[n // 2 - 1] + nums[n // 2]) / 2))\n',
      lambda r: _gen_ints(r, hi=100),
      hint='排序后分奇偶处理：奇数取下标 n//2，偶数取中间两项平均值。',
      scope='1 ≤ n ≤ 10⁵', tags='排序,统计,数学', kid=6),

    P('最大差值', 2,
      '给定 n 个整数，求其中任意两个元素（要求前者下标小于后者下标）之差的最大值 a[j] - a[i]（j > i）；若不存在这样的数对则输出 0。',
      '两行。第一行一个整数 n；第二行 n 个整数。',
      '一行，一个整数，表示最大差值。',
      '5\n3 9 2 7 5', '6',
      'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nnums = list(map(int, data[1:1 + n]))\nif n < 2:\n    print(0)\nelse:\n    mn = nums[0]\n    best = 0\n    for x in nums[1:]:\n        best = max(best, x - mn)\n        mn = min(mn, x)\n    print(best)\n',
      lambda r: _gen_ints(r, hi=200),
      hint='一趟扫描维护"到目前为止的最小值"，用当前值减去它更新答案，O(n)。',
      scope='1 ≤ n ≤ 10⁵', tags='数组,枚举,最值'),

    P('和为 k 的最长子数组', 3,
      '给定一个长度为 n 的整数序列（可能含负数）和整数 k，求元素和恰好等于 k 的最长连续子数组的长度；若不存在则输出 0。',
      '第一行两个整数 n、k；第二行 n 个整数。',
      '一行，一个整数，表示最长长度。',
      '7 3\n1 -1 5 -2 3 0 1', '4',
      'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nk = int(data[1])\nnums = list(map(int, data[2:2 + n]))\nfirst = {0: 0}\npre = 0\nbest = 0\nfor i, x in enumerate(nums, 1):\n    pre += x\n    if pre - k in first:\n        best = max(best, i - first[pre - k])\n    if pre not in first:\n        first[pre] = i\nprint(best)\n',
      lambda r: '%d %d\n%s' % (r.randint(1, 25), r.randint(-20, 20),
                                ' '.join(str(r.randint(-10, 10)) for _ in range(r.randint(1, 25)))),
      hint='前缀和 + 哈希：若 pre[j] - pre[i] = k，则区间 (i, j] 和为 k。记录每个前缀和首次出现的位置，保留最早的那个可得到最长长度。',
      scope='1 ≤ n ≤ 10⁵', tags='前缀和,哈希,子数组', kid=33),

    P('长度最小的连续子数组', 3,
      '给定一个长度为 n 的正整数序列和整数 s，求元素和不小于 s 的最短连续子数组的长度；若不存在则输出 0。',
      '第一行两个整数 n、s；第二行 n 个正整数。',
      '一行，一个整数，表示最短长度。',
      '6 7\n2 3 1 2 4 3', '2',
      'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\ns = int(data[1])\nnums = list(map(int, data[2:2 + n]))\nbest = n + 1\nleft = 0\ntotal = 0\nfor right, x in enumerate(nums):\n    total += x\n    while total >= s:\n        best = min(best, right - left + 1)\n        total -= nums[left]\n        left += 1\nprint(0 if best == n + 1 else best)\n',
      lambda r: '%d %d\n%s' % (r.randint(1, 25), r.randint(1, 60),
                                ' '.join(str(r.randint(1, 20)) for _ in range(r.randint(1, 25)))),
      hint='滑动窗口（双指针）：右指针扩张窗口使和增大，达标后左指针尽量右移收缩，每个元素进出各一次，O(n)。',
      scope='1 ≤ n ≤ 10⁵', tags='双指针,滑动窗口,子数组'),

    P('离散化求区间和', 3,
      '在一条数轴上有 n 次"在某点 x 处加上 c"的操作，随后有 m 次询问，每次询问区间 [l, r] 上的数值总和。坐标范围可达 10⁹，但操作与询问涉及的坐标总数不超过 3×10⁵。',
      '第一行两个整数 n、m；接下来 n 行，每行两个整数 x、c；接下来 m 行，每行两个整数 l、r。',
      'm 行，每行一个整数，表示对应区间的数值和。',
      '3 2\n10 5\n100 3\n1000 8\n1 100\n10 1000', '8\n16',
      'import sys\n\ndata = sys.stdin.read().split()\nidx = 0\nn = int(data[idx]); m = int(data[idx + 1]); idx += 2\nadds = []\ncoords = []\nfor _ in range(n):\n    x = int(data[idx]); c = int(data[idx + 1]); idx += 2\n    adds.append((x, c))\n    coords.append(x)\nqueries = []\nfor _ in range(m):\n    l = int(data[idx]); rr = int(data[idx + 1]); idx += 2\n    queries.append((l, rr))\n    coords.append(l)\n    coords.append(rr)\nvals = sorted(set(coords))\n\n\ndef pos(x):\n    lo, hi = 0, len(vals) - 1\n    while lo < hi:\n        mid = (lo + hi) // 2\n        if vals[mid] >= x:\n            hi = mid\n        else:\n            lo = mid + 1\n    return lo\n\n\narr = [0] * len(vals)\nfor x, c in adds:\n    arr[pos(x)] += c\npre = [0]\nfor v in arr:\n    pre.append(pre[-1] + v)\nout = []\nfor l, rr in queries:\n    out.append(str(pre[pos(rr) + 1] - pre[pos(l)]))\nprint("\\n".join(out))\n',
      lambda r: (lambda n, m: '%d %d\n%s\n%s' % (
          n, m, '\n'.join('%d %d' % (r.randint(1, 10**6), r.randint(1, 100)) for _ in range(n)),
          '\n'.join((lambda a, b: '%d %d' % (min(a, b), max(a, b)))(r.randint(1, 10**6), r.randint(1, 10**6))
                    for _ in range(m))))(r.randint(1, 15), r.randint(1, 6)),
      hint='坐标范围大但点数少时先"离散化"：把所有出现过的坐标排序去重，用下标代替原坐标，再做前缀和。注意 pos(l) 应取第一个 ≥ l 的位置。',
      scope='1 ≤ n, m ≤ 10⁵，坐标 ≤ 10⁹', tags='离散化,前缀和,二分'),
]
