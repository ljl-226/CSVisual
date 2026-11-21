# -*- coding: utf-8 -*-
"""第七批：动态规划（20 道）"""
from common import P


def _gen_triangle(r, n=None, lo=0, hi=20):
    n = n or r.randint(2, 8)
    rows = []
    for i in range(1, n + 1):
        rows.append(' '.join(str(r.randint(lo, hi)) for _ in range(i)))
    return '%d\n%s' % (n, '\n'.join(rows))


def _gen_grid(r, n=None, m=None, lo=-9, hi=9):
    n = n or r.randint(2, 8)
    m = m or r.randint(2, 8)
    return '%d %d\n%s' % (n, m, '\n'.join(
        ' '.join(str(r.randint(lo, hi)) for _ in range(m)) for _ in range(n)))


def _gen_knapsack(r):
    n = r.randint(1, 8)
    w = r.randint(5, 30)
    items = [(r.randint(1, w), r.randint(1, 50)) for _ in range(n)]
    return '%d %d\n%s' % (n, w, '\n'.join('%d %d' % it for it in items))


def _gen_coins(r):
    n = r.randint(1, 6)
    coins = sorted(set(r.randint(1, 30) for _ in range(n)))
    if 1 not in coins and r.random() < 0.7:
        coins.append(1)
        coins.sort()
    return '%d %d\n%s' % (len(coins), r.randint(1, 200), ' '.join(map(str, coins)))


def _gen_arr(r, n=None, lo=1, hi=100):
    n = n or r.randint(1, 20)
    return '%d\n%s' % (n, ' '.join(str(r.randint(lo, hi)) for _ in range(n)))


def _gen_strs(r):
    import string
    a = ''.join(r.choice('abcde') for _ in range(r.randint(1, 10)))
    b = ''.join(r.choice('abcde') for _ in range(r.randint(1, 10)))
    return '%s\n%s' % (a, b)


PROBLEMS = [
    P('爬楼梯（斐波那契递推）', 2,
      '有 n 阶楼梯，每次可以上 1 阶或 2 阶，求到达顶楼的不同方法数（答案保证在 64 位整数范围内）。',
      '一行，一个整数 n。',
      '一行，一个整数，表示方法数。',
      '5', '8',
      '''import sys

n = int(sys.stdin.read().strip())
a, b = 1, 1
for _ in range(2, n + 1):
    a, b = b, a + b
print(b)
''',
      lambda r: str(r.randint(1, 60)),
      hint='设 f(n) 为到达第 n 阶的方法数，最后一跳可能是 1 阶或 2 阶，故 f(n) = f(n-1) + f(n-2)，即斐波那契。',
      scope='1 ≤ n ≤ 60', tags='动态规划,递推,斐波那契', kid=8),

    P('数字三角形', 2,
      '给定一个 n 行的数字三角形，从第 1 行唯一的数出发，每次可以走到下一行中与当前位置相邻（正下方或右下方）的数，求到达最后一行时经过的数字之和的最大值。',
      '第一行一个整数 n；接下来 n 行，第 i 行有 i 个整数。',
      '一行，一个整数，表示最大和。',
      '5\n7\n3 8\n8 1 0\n2 7 4 4\n4 5 2 6 5', '30',
      '''import sys

data = list(map(int, sys.stdin.read().split()))
n = data[0]
vals = data[1:]
tri = []
pos = 0
for i in range(1, n + 1):
    tri.append(vals[pos:pos + i])
    pos += i
for i in range(n - 2, -1, -1):
    for j in range(len(tri[i])):
        tri[i][j] += max(tri[i + 1][j], tri[i + 1][j + 1])
print(tri[0][0])
''',
      lambda r: _gen_triangle(r),
      hint='自底向上递推：dp[i][j] = a[i][j] + max(dp[i+1][j], dp[i+1][j+1])，可直接在原数组上原地累加，省去额外空间。',
      scope='1 ≤ n ≤ 100，每个数 ∈ [0, 100]', tags='动态规划,线性DP', kid=8),

    P('不同路径数', 2,
      '一个机器人位于 m 行 n 列网格的左上角，每次只能向右或向下移动一步，问到达右下角共有多少条不同路径。',
      '一行，两个整数 m、n。',
      '一行，一个整数，表示路径条数（保证不超过 64 位整数）。',
      '3 3', '6',
      '''import sys

m, n = map(int, sys.stdin.read().split())
dp = [1] * n
for _ in range(1, m):
    for j in range(1, n):
        dp[j] += dp[j - 1]
print(dp[n - 1])
''',
      lambda r: '%d %d' % (r.randint(1, 15), r.randint(1, 15)),
      hint='dp[i][j] = dp[i-1][j] + dp[i][j-1]，第一行第一列均为 1；用一维数组滚动可把空间压到 O(n)。',
      scope='1 ≤ m, n ≤ 30', tags='动态规划,网格DP,计数', kid=8),

    P('最低通行费', 2,
      '一个 n × n 的网格，每个格子有一个费用。从左上角走到右下角，每次只能向右或向下走，求经过格子的费用之和（包含起点与终点）的最小值。',
      '第一行一个整数 n；接下来 n 行，每行 n 个整数。',
      '一行，一个整数，表示最小费用。',
      '3\n1 3 1\n1 5 1\n4 2 1', '7',
      '''import sys

data = list(map(int, sys.stdin.read().split()))
n = data[0]
a = [data[1 + i * n:1 + (i + 1) * n] for i in range(n)]
INF = 10 ** 15
dp = [[INF] * n for _ in range(n)]
dp[0][0] = a[0][0]
for i in range(n):
    for j in range(n):
        if i == 0 and j == 0:
            continue
        best = INF
        if i:
            best = min(best, dp[i - 1][j])
        if j:
            best = min(best, dp[i][j - 1])
        dp[i][j] = best + a[i][j]
print(dp[n - 1][n - 1])
''',
      lambda r: (lambda n: '%d\n%s' % (n, '\n'.join(
          ' '.join(str(r.randint(1, 30)) for _ in range(n)) for _ in range(n))))(r.randint(2, 8)),
      hint='与"不同路径数"同构，只是把计数换成取最小值；注意起点要单独初始化。',
      scope='1 ≤ n ≤ 100，费用 ∈ [1, 100]', tags='动态规划,网格DP', kid=8),

    P('最长上升子序列', 3,
      '给定一个长度为 n 的整数序列，求它的最长严格上升子序列的长度。',
      '第一行一个整数 n；第二行 n 个整数。',
      '一行，一个整数。',
      '8\n10 9 2 5 3 7 101 18', '4',
      '''import sys
import bisect

data = list(map(int, sys.stdin.read().split()))
n = data[0]
a = data[1:1 + n]
tails = []
for x in a:
    i = bisect.bisect_left(tails, x)
    if i == len(tails):
        tails.append(x)
    else:
        tails[i] = x
print(len(tails))
''',
      lambda r: _gen_arr(r, r.randint(1, 25), 1, 500),
      hint='tails[k] 维护长度为 k+1 的上升子序列的最小结尾，用二分找到第一个 ≥ x 的位置替换它，复杂度 O(n log n)。',
      scope='1 ≤ n ≤ 10⁵', tags='动态规划,LIS,二分', kid=8),

    P('最长公共子序列', 3,
      '给定两个字符串 s 和 t，求它们的最长公共子序列的长度（子序列不要求连续，但顺序必须一致）。',
      '两行，每行一个字符串。',
      '一行，一个整数。',
      'abcde\nace', '3',
      '''import sys

data = sys.stdin.read().split('\\n')
s = data[0].strip()
t = data[1].strip()
n, m = len(s), len(t)
dp = [0] * (m + 1)
for i in range(1, n + 1):
    prev = 0
    for j in range(1, m + 1):
        tmp = dp[j]
        if s[i - 1] == t[j - 1]:
            dp[j] = prev + 1
        else:
            dp[j] = max(dp[j], dp[j - 1])
        prev = tmp
print(dp[m])
''',
      _gen_strs,
      hint='经典二维 DP：字符相等时 dp[i][j] = dp[i-1][j-1] + 1，否则取 dp[i-1][j] 与 dp[i][j-1] 的最大值；可用滚动数组降维。',
      scope='1 ≤ |s|, |t| ≤ 1000', tags='动态规划,LCS', kid=8),

    P('最长公共子串', 2,
      '给定两个字符串 s 和 t，求它们的最长公共子串的长度（子串要求连续）。',
      '两行，每行一个字符串。',
      '一行，一个整数。',
      'abcdef\ncde', '3',
      '''import sys

data = sys.stdin.read().split('\\n')
s = data[0].strip()
t = data[1].strip()
n, m = len(s), len(t)
dp = [0] * (m + 1)
ans = 0
for i in range(1, n + 1):
    prev = 0
    for j in range(1, m + 1):
        tmp = dp[j]
        if s[i - 1] == t[j - 1]:
            dp[j] = prev + 1
        else:
            dp[j] = 0
        prev = tmp
        ans = max(ans, dp[j])
print(ans)
''',
      _gen_strs,
      hint='与 LCS 的区别在于：字符失配时 dp 值必须清零（子串要求连续），答案在过程中取最大值而不是取 dp[n][m]。',
      scope='1 ≤ |s|, |t| ≤ 1000', tags='动态规划,子串', kid=8),

    P('0/1 背包', 3,
      '有 n 个物品和一个容量为 W 的背包，每个物品只能取一次，第 i 个物品重量为 wᵢ、价值为 vᵢ。求在不超过容量的前提下能取得的最大总价值。',
      '第一行两个整数 n、W；接下来 n 行，每行两个整数 wᵢ、vᵢ。',
      '一行，一个整数，表示最大总价值。',
      '4 5\n2 3\n1 2\n3 4\n2 2', '7',
      '''import sys

data = list(map(int, sys.stdin.read().split()))
n, W = data[0], data[1]
dp = [0] * (W + 1)
p = 2
for _ in range(n):
    w, v = data[p], data[p + 1]
    p += 2
    for j in range(W, w - 1, -1):
        if dp[j - w] + v > dp[j]:
            dp[j] = dp[j - w] + v
print(max(dp))
''',
      _gen_knapsack,
      hint='一维滚动数组的关键：容量必须**从大到小**枚举，保证每个物品只被放入一次（否则就变成完全背包）。',
      scope='1 ≤ n ≤ 100，1 ≤ W ≤ 1000', tags='动态规划,背包,0/1背包', kid=8),

    P('完全背包', 3,
      '有 n 种物品和一个容量为 W 的背包，每种物品可以取任意多个，第 i 种物品重量为 wᵢ、价值为 vᵢ。求在不超过容量的前提下能取得的最大总价值。',
      '第一行两个整数 n、W；接下来 n 行，每行两个整数 wᵢ、vᵢ。',
      '一行，一个整数，表示最大总价值。',
      '3 7\n2 3\n3 4\n4 5', '10',
      '''import sys

data = list(map(int, sys.stdin.read().split()))
n, W = data[0], data[1]
dp = [0] * (W + 1)
p = 2
for _ in range(n):
    w, v = data[p], data[p + 1]
    p += 2
    for j in range(w, W + 1):
        if dp[j - w] + v > dp[j]:
            dp[j] = dp[j - w] + v
print(max(dp))
''',
      _gen_knapsack,
      hint='与 0/1 背包唯一的区别是容量**从小到大**枚举，这样同一个物品可以被重复选取。',
      scope='1 ≤ n ≤ 100，1 ≤ W ≤ 1000', tags='动态规划,背包,完全背包', kid=8),

    P('硬币找零', 3,
      '给定 n 种面值的硬币和一个目标金额 M，每种硬币可以无限使用，求凑出 M 所需的最少硬币数；若无法凑出，输出 -1。',
      '第一行两个整数 n、M；第二行 n 个整数，表示各硬币面值。',
      '一行，一个整数。',
      '3 11\n1 2 5', '3',
      '''import sys

data = list(map(int, sys.stdin.read().split()))
n, M = data[0], data[1]
coins = data[2:2 + n]
INF = 10 ** 9
dp = [INF] * (M + 1)
dp[0] = 0
for c in coins:
    for j in range(c, M + 1):
        if dp[j - c] + 1 < dp[j]:
            dp[j] = dp[j - c] + 1
print(-1 if dp[M] >= INF else dp[M])
''',
      _gen_coins,
      hint='完全背包的最小值版本：dp[j] = min(dp[j], dp[j-c] + 1)，初始化 dp[0] = 0、其余为无穷大，最后判断是否仍为无穷。',
      scope='1 ≤ n ≤ 20，1 ≤ M ≤ 10⁴', tags='动态规划,背包,完全背包', kid=8),

    P('装箱问题', 2,
      '有一个容量为 V 的箱子和 n 个物品，每个物品有一个体积。求在箱子中放入若干物品后，箱子剩余空间的最小值。',
      '第一行一个整数 V；第二行一个整数 n；接下来 n 行，每行一个整数表示物品体积。',
      '一行，一个整数，表示最小剩余空间。',
      '24\n6\n8\n3\n12\n7\n9\n7', '0',
      '''import sys

data = list(map(int, sys.stdin.read().split()))
V = data[0]
n = data[1]
items = data[2:2 + n]
dp = [0] * (V + 1)
for w in items:
    for j in range(V, w - 1, -1):
        if dp[j - w] + w > dp[j]:
            dp[j] = dp[j - w] + w
print(V - dp[V])
''',
      lambda r: (lambda V, n: '%d\n%d\n%s' % (V, n, '\n'.join(
          str(r.randint(1, V)) for _ in range(n))))(r.randint(10, 50), r.randint(1, 10)),
      hint='把"价值"看成体积本身，就是求不超过 V 的最大可装体积（0/1 背包），答案用 V 减去它。',
      scope='1 ≤ V ≤ 20000，1 ≤ n ≤ 30', tags='动态规划,背包', kid=8),

    P('打家劫舍', 3,
      '沿街有一排房屋，每个房屋里有一定金额的现金。小偷不能连续偷相邻的两间房屋，求一夜之间能偷到的最大金额。',
      '第一行一个整数 n；第二行 n 个非负整数。',
      '一行，一个整数。',
      '4\n1 2 3 1', '4',
      '''import sys

data = list(map(int, sys.stdin.read().split()))
n = data[0]
a = data[1:1 + n]
prev, cur = 0, 0
for x in a:
    prev, cur = cur, max(cur, prev + x)
print(cur)
''',
      lambda r: _gen_arr(r, r.randint(1, 20), 0, 100),
      hint='到第 i 间为止只有"偷 / 不偷"两种状态，转移为 cur = max(cur, prev + a[i])，用两个变量滚动即可。',
      scope='1 ≤ n ≤ 10⁵', tags='动态规划,线性DP', kid=8),

    P('三角形最小路径和', 3,
      '给定一个 n 行的数字三角形，从顶部出发，每次只能走到下一行相邻的数（正下方或右下方），求到达底部时经过数字之和的最小值。',
      '第一行一个整数 n；接下来 n 行，第 i 行有 i 个整数。',
      '一行，一个整数。',
      '4\n2\n3 4\n6 5 7\n4 1 8 3', '11',
      '''import sys

data = list(map(int, sys.stdin.read().split()))
n = data[0]
vals = data[1:]
tri = []
pos = 0
for i in range(1, n + 1):
    tri.append(vals[pos:pos + i])
    pos += i
for i in range(n - 2, -1, -1):
    for j in range(len(tri[i])):
        tri[i][j] += min(tri[i + 1][j], tri[i + 1][j + 1])
print(tri[0][0])
''',
      lambda r: _gen_triangle(r),
      hint='与"数字三角形"完全同构，只是把 max 换成 min，自底向上原地递推即可。',
      scope='1 ≤ n ≤ 100，每个数 ∈ [0, 100]', tags='动态规划,线性DP', kid=8),

    P('买卖股票的最佳时机', 2,
      '给定一支股票连续 n 天的价格，你只能选择在某一天买入，并在之后的某一天卖出（只允许一次交易），求最大利润；若无论如何都亏本，输出 0。',
      '第一行一个整数 n；第二行 n 个整数。',
      '一行，一个整数。',
      '6\n7 1 5 3 6 4', '5',
      '''import sys

data = list(map(int, sys.stdin.read().split()))
n = data[0]
a = data[1:1 + n]
if n < 2:
    print(0)
else:
    low = a[0]
    ans = 0
    for x in a[1:]:
        if x - low > ans:
            ans = x - low
        if x < low:
            low = x
    print(ans)
''',
      lambda r: _gen_arr(r, r.randint(2, 20), 1, 100),
      hint='从左到右扫描，维护此前见过的最低买入价 low，用当天价格减 low 更新最大利润；一次遍历即可。',
      scope='1 ≤ n ≤ 10⁵', tags='动态规划,贪心', kid=8),

    P('带障碍的不同路径', 3,
      '一个 m 行 n 列的网格，其中 1 表示障碍、0 表示可通行。机器人从左上角走到右下角，每次只能向右或向下，求不同路径的条数。',
      '第一行两个整数 m、n；接下来 m 行，每行 n 个 0 或 1。',
      '一行，一个整数，表示路径条数。',
      '3 3\n0 0 0\n0 1 0\n0 0 0', '2',
      '''import sys

data = list(map(int, sys.stdin.read().split()))
m, n = data[0], data[1]
grid = [data[2 + i * n:2 + (i + 1) * n] for i in range(m)]
dp = [0] * n
for i in range(m):
    for j in range(n):
        if grid[i][j] == 1:
            dp[j] = 0
        elif i == 0 and j == 0:
            dp[j] = 1
        elif j:
            dp[j] += dp[j - 1]
print(dp[n - 1])
''',
      lambda r: (lambda m, n: '%d %d\n%s' % (m, n, '\n'.join(
          ' '.join(str(1 if r.random() < 0.2 else 0) for _ in range(n)) for _ in range(m))))(
          r.randint(2, 8), r.randint(2, 8)),
      hint='在"不同路径数"基础上增加障碍判断：遇到障碍格子时 dp 值置 0，起点若可通行则为 1。',
      scope='1 ≤ m, n ≤ 100', tags='动态规划,网格DP', kid=8),

    P('最长回文子串', 3,
      '给定一个字符串 s，求它的最长回文子串的长度。',
      '一行，一个字符串 s。',
      '一行，一个整数。',
      'babad', '3',
      '''import sys

s = sys.stdin.readline().strip()
n = len(s)
ans = 0
for c in range(n):
    k = 0
    while c - k >= 0 and c + k < n and s[c - k] == s[c + k]:
        k += 1
    ans = max(ans, 2 * k - 1)
    k = 0
    while c - k >= 0 and c + 1 + k < n and s[c - k] == s[c + 1 + k]:
        k += 1
    ans = max(ans, 2 * k)
print(ans)
''',
      lambda r: ''.join(r.choice('abcd') for _ in range(r.randint(1, 30))),
      hint='中心扩展法：枚举每个中心（奇长度以字符为中心、偶长度以空隙为中心），向两侧扩展直到失配，O(n²) 时间 O(1) 空间。',
      scope='1 ≤ |s| ≤ 1000', tags='动态规划,字符串,中心扩展', kid=8),

    P('编辑距离（Levenshtein）', 4,
      '给定两个字符串 s 和 t，允许三种操作：插入一个字符、删除一个字符、替换一个字符（每次代价均为 1）。求把 s 变成 t 的最少操作次数。',
      '两行，每行一个字符串。',
      '一行，一个整数。',
      'horse\nros', '3',
      '''import sys

data = sys.stdin.read().split('\\n')
s = data[0].strip()
t = data[1].strip()
n, m = len(s), len(t)
dp = list(range(m + 1))
for i in range(1, n + 1):
    prev = dp[0]
    dp[0] = i
    for j in range(1, m + 1):
        tmp = dp[j]
        if s[i - 1] == t[j - 1]:
            dp[j] = prev
        else:
            dp[j] = 1 + min(prev, dp[j], dp[j - 1])
        prev = tmp
print(dp[m])
''',
      _gen_strs,
      hint='dp[i][j] 表示 s 前 i 个字符变成 t 前 j 个字符的最少步数；字符相等时直接继承 dp[i-1][j-1]，否则在插入、删除、替换三者中取最小再加一。',
      scope='1 ≤ |s|, |t| ≤ 500', tags='动态规划,编辑距离,字符串', kid=8),

    P('石子合并（直线）', 4,
      'n 堆石子排成一排，每堆有 aᵢ 个石子。每次只能把相邻的两堆合并成一堆，合并的代价为这两堆石子总数。求把所有石子合并成一堆的最小总代价。',
      '第一行一个整数 n；第二行 n 个整数。',
      '一行，一个整数。',
      '4\n4 5 9 4', '44',
      '''import sys

data = list(map(int, sys.stdin.read().split()))
n = data[0]
a = data[1:1 + n]
pre = [0] * (n + 1)
for i in range(n):
    pre[i + 1] = pre[i] + a[i]
INF = 10 ** 18
dp = [[0] * n for _ in range(n)]
for length in range(2, n + 1):
    for i in range(n - length + 1):
        j = i + length - 1
        best = INF
        for k in range(i, j):
            v = dp[i][k] + dp[k + 1][j] + pre[j + 1] - pre[i]
            if v < best:
                best = v
        dp[i][j] = best
print(dp[0][n - 1])
''',
      lambda r: _gen_arr(r, r.randint(2, 12), 1, 50),
      hint='区间 DP 模板：先枚举区间长度，再枚举左端点，最后枚举最后一次合并的分割点 k，代价为该区间石子总数（用前缀和 O(1) 求出）。',
      scope='1 ≤ n ≤ 100', tags='动态规划,区间DP', kid=8),

    P('第 n 个丑数', 3,
      '只包含质因子 2、3、5 的正整数称为丑数，1 是第一个丑数。求第 n 个丑数。',
      '一行，一个整数 n。',
      '一行，一个整数。',
      '10', '12',
      '''import sys

n = int(sys.stdin.read().strip())
ugly = [1]
i2 = i3 = i5 = 0
for _ in range(1, n):
    a, b, c = ugly[i2] * 2, ugly[i3] * 3, ugly[i5] * 5
    nxt = min(a, b, c)
    ugly.append(nxt)
    if nxt == a:
        i2 += 1
    if nxt == b:
        i3 += 1
    if nxt == c:
        i5 += 1
print(ugly[n - 1])
''',
      lambda r: str(r.randint(1, 300)),
      hint='三指针法：每个丑数都由某个已有的丑数乘 2/3/5 得到，用三个指针分别记录下一次乘法的候选位置，每次取最小值并推进对应指针（相等时都要推进以去重）。',
      scope='1 ≤ n ≤ 2000', tags='动态规划,多指针,数学', kid=8),

    P('最大子矩阵和', 3,
      '给定一个 n 行 m 列的整数矩阵，求它的一个非空子矩阵（连续的行与列围成的矩形），使得子矩阵内所有元素之和最大。',
      '第一行两个整数 n、m；接下来 n 行，每行 m 个整数。',
      '一行，一个整数，表示最大子矩阵和。',
      '2 3\n1 2 3\n-4 5 6', '16',
      '''import sys

data = list(map(int, sys.stdin.read().split()))
n, m = data[0], data[1]
a = [data[2 + i * m:2 + (i + 1) * m] for i in range(n)]
ans = -(10 ** 18)
for top in range(n):
    col = [0] * m
    for bottom in range(top, n):
        for j in range(m):
            col[j] += a[bottom][j]
        cur = col[0]
        best = col[0]
        for x in col[1:]:
            cur = max(x, cur + x)
            best = max(best, cur)
        ans = max(ans, best)
print(ans)
''',
      lambda r: _gen_grid(r, None, None, -9, 20),
      hint='枚举上下边界，把两行之间的元素按列压缩成一维数组，问题就转化为一维最大子段和，整体 O(n²m)。',
      scope='1 ≤ n, m ≤ 100，元素 ∈ [-100, 100]', tags='动态规划,降维,最大子段和', kid=8),
]
