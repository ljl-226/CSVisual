# -*- coding: utf-8 -*-
"""第六批：数学与数论（20 道）"""
import math
import random

from common import P

_PRIMES = [7, 11, 13, 17, 97, 101, 997, 1009, 10007]


def _gen_coprime(r):
    m = r.choice(_PRIMES)
    a = r.randint(1, m - 1)
    return '%d %d' % (a, m)


def _gen_frac(r):
    b = r.randint(2, 60)
    a = r.randint(1, 200)
    return '%d/%d' % (a, b)


def _gen_frac2(r):
    return '%s %s' % (_gen_frac(r), _gen_frac(r))


def _gen_digits3(r):
    while True:
        a, b, c = r.randint(1, 9), r.randint(0, 9), r.randint(0, 9)
        if not (a == b == c):
            return '%d%d%d' % (a, b, c)


PROBLEMS = [
    P('最大公约数与最小公倍数（辗转相除）', 1,
      '给定两个正整数 a、b，求它们的最大公约数和最小公倍数。',
      '一行，两个正整数 a、b。',
      '一行，两个整数，依次为最大公约数和最小公倍数，用空格分隔。',
      '12 18', '6 36',
      '''import sys
import math

a, b = map(int, sys.stdin.read().split())
g = math.gcd(a, b)
print(g, a // g * b)
''',
      lambda r: '%d %d' % (r.randint(1, 10 ** 6), r.randint(1, 10 ** 6)),
      hint='辗转相除法（欧几里得算法）求 gcd；利用 a × b = gcd × lcm，写成 a // g * b 可避免中间结果溢出。',
      scope='1 ≤ a, b ≤ 10⁹', tags='数论,gcd,辗转相除', kid=8),

    P('素数判定', 1,
      '给定一个正整数 n，判断它是否为素数（质数）。',
      '一行，一个整数 n。',
      '一行，是素数输出 Yes，否则输出 No。',
      '17', 'Yes',
      '''import sys

n = int(sys.stdin.read().strip())
if n < 2:
    print('No')
else:
    ok = True
    i = 2
    while i * i <= n:
        if n % i == 0:
            ok = False
            break
        i += 1
    print('Yes' if ok else 'No')
''',
      lambda r: str(r.randint(1, 10 ** 6)),
      hint='只需试除到 √n：若 n 存在大于 √n 的因子，必然对应一个小于 √n 的因子。',
      scope='1 ≤ n ≤ 10⁹', tags='数论,素数,试除法', kid=8),

    P('分解质因数', 2,
      '给定一个大于 1 的整数 n，将其分解成若干质因数的乘积，按质因数从小到大的顺序输出，形如「n = p1 * p2 * ...」（数与运算符之间各有一个空格）。',
      '一行，一个整数 n。',
      '一行，分解式。',
      '60', '60 = 2 * 2 * 3 * 5',
      '''import sys

n = int(sys.stdin.read().strip())
orig = n
res = []
d = 2
while d * d <= n:
    while n % d == 0:
        res.append(d)
        n //= d
    d += 1
if n > 1:
    res.append(n)
print('%d = %s' % (orig, ' * '.join(map(str, res))))
''',
      lambda r: str(r.randint(2, 10 ** 6)),
      hint='从 2 开始试除，把能整除的因子全部除尽再前进；最后剩下大于 1 的数本身也是一个质因数。',
      scope='2 ≤ n ≤ 10⁹', tags='数论,质因数分解', kid=8),

    P('筛法求素数个数', 2,
      '给定整数 n，求不超过 n 的素数个数。',
      '一行，一个整数 n。',
      '一行，一个整数，表示素数个数。',
      '10', '4',
      '''import sys

n = int(sys.stdin.read().strip())
is_prime = [True] * (n + 1)
if n >= 0:
    is_prime[0] = False
if n >= 1:
    is_prime[1] = False
i = 2
while i * i <= n:
    if is_prime[i]:
        for j in range(i * i, n + 1, i):
            is_prime[j] = False
    i += 1
print(sum(1 for x in range(2, n + 1) if is_prime[x]))
''',
      lambda r: str(r.randint(1, 10 ** 5)),
      hint='埃氏筛：从 2 开始，把每个素数的倍数全部标记为合数，注意从 i*i 开始标记以避免重复。',
      scope='1 ≤ n ≤ 10⁶', tags='数论,素数,埃氏筛', kid=8),

    P('二进制中 1 的个数', 2,
      '给定一个非负整数 n，求它的二进制表示中 1 的个数。',
      '一行，一个整数 n。',
      '一行，一个整数。',
      '13', '3',
      '''import sys

n = int(sys.stdin.read().strip())
ans = 0
while n:
    n &= n - 1
    ans += 1
print(ans)
''',
      lambda r: str(r.randint(0, 10 ** 9)),
      hint='Brian Kernighan 技巧：n & (n-1) 会消去最低位的 1，循环次数等于 1 的个数，比逐位检查更快。',
      scope='0 ≤ n ≤ 10¹⁸', tags='数论,位运算', kid=8),

    P('快速幂', 3,
      '给定三个整数 a、b、m，求 aᵇ mod m 的值。',
      '一行，三个整数 a、b、m。',
      '一行，一个整数，表示 aᵇ mod m。',
      '2 10 1000', '24',
      '''import sys

a, b, m = map(int, sys.stdin.read().split())
res = 1 % m
a %= m
while b:
    if b & 1:
        res = res * a % m
    a = a * a % m
    b >>= 1
print(res)
''',
      lambda r: '%d %d %d' % (r.randint(1, 10 ** 6), r.randint(0, 10 ** 9), r.randint(2, 10 ** 9)),
      hint='二进制拆分指数：底数不断平方，指数的每一位为 1 时就把当前底数乘入答案，复杂度 O(log b)。',
      scope='0 ≤ a, b ≤ 10⁹，1 ≤ m ≤ 10⁹', tags='数论,快速幂,分治', kid=8),

    P('乘法逆元', 3,
      '给定互质的正整数 a 和 m，求 a 在模 m 意义下的乘法逆元 x（即满足 a·x ≡ 1 (mod m) 且 0 < x < m 的最小正整数解）。',
      '一行，两个正整数 a、m，保证 gcd(a, m) = 1。',
      '一行，一个整数，表示逆元。',
      '3 11', '4',
      '''import sys

a, m = map(int, sys.stdin.read().split())


def exgcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x, y = exgcd(b, a % b)
    return g, y, x - (a // b) * y


g, x, y = exgcd(a, m)
print(x % m)
''',
      _gen_coprime,
      hint='扩展欧几里得求出 a·x + m·y = 1 的一组解，x 对 m 取正模即为逆元；当 m 为素数时也可用费马小定理 a^(m-2)。',
      scope='1 ≤ a < m ≤ 10⁹，保证互质', tags='数论,扩展欧几里得,逆元', kid=8),

    P('十进制转 k 进制', 2,
      '给定一个十进制非负整数 n 和进制 k（2 ≤ k ≤ 16），输出 n 的 k 进制表示（大于 9 的数位用大写字母 A-F 表示）。',
      '一行，两个整数 n、k。',
      '一行，转换后的字符串。',
      '255 16', 'FF',
      '''import sys

n, k = map(int, sys.stdin.read().split())
digits = '0123456789ABCDEF'
if n == 0:
    print('0')
else:
    res = []
    while n:
        res.append(digits[n % k])
        n //= k
    print(''.join(reversed(res)))
''',
      lambda r: '%d %d' % (r.randint(0, 10 ** 9), r.randint(2, 16)),
      hint='不断对 k 取余得到低位、再整除 k，最后把得到的数位逆序输出；注意 n = 0 的特判。',
      scope='0 ≤ n ≤ 10⁹，2 ≤ k ≤ 16', tags='数论,进制转换', kid=8),

    P('k 进制转十进制', 2,
      '给定一个 k 进制（2 ≤ k ≤ 16，数位可含大写字母 A-F）的非负整数字符串 s，输出它对应的十进制值。',
      '两行。第一行为进制 k；第二行为字符串 s。',
      '一行，一个整数，表示十进制值。',
      '16\nFF', '255',
      '''import sys

data = sys.stdin.read().split('\\n')
k = int(data[0])
s = data[1].strip()
ans = 0
for ch in s:
    if ch.isdigit():
        v = int(ch)
    else:
        v = ord(ch) - ord('A') + 10
    ans = ans * k + v
print(ans)
''',
      lambda r: (lambda k: '%d\n%s' % (k, ''.join(
          r.choice('0123456789ABCDEF'[:k]) for _ in range(r.randint(1, 8)))))(r.randint(2, 16)),
      hint='秦九韶算法：ans = ans × k + 当前位的值，从左到右扫一遍即可，无需计算每一位的幂。',
      scope='2 ≤ k ≤ 16，1 ≤ |s| ≤ 10', tags='数论,进制转换', kid=8),

    P('阶乘末尾零的个数', 2,
      '给定正整数 n，求 n! 的十进制表示末尾有多少个连续的 0。',
      '一行，一个整数 n。',
      '一行，一个整数。',
      '100', '24',
      '''import sys

n = int(sys.stdin.read().strip())
ans = 0
while n:
    n //= 5
    ans += n
print(ans)
''',
      lambda r: str(r.randint(1, 10 ** 6)),
      hint='每个末尾 0 来自因子 2 × 5，而因子 2 远多于 5，所以只需统计 1..n 中因子 5 的总个数：不断除以 5 累加。',
      scope='1 ≤ n ≤ 10⁹', tags='数论,阶乘,计数', kid=8),

    P('完全平方数判定', 1,
      '给定一个非负整数 n，判断它是否为完全平方数。',
      '一行，一个整数 n。',
      '一行，是输出 Yes，否则输出 No。',
      '144', 'Yes',
      '''import sys
import math

n = int(sys.stdin.read().strip())
r = int(math.isqrt(n))
print('Yes' if r * r == n else 'No')
''',
      lambda r: str(r.randint(0, 10 ** 12)),
      hint='用整数平方根 isqrt 再平方比较，避免浮点误差；也可二分查找。',
      scope='0 ≤ n ≤ 10¹²', tags='数论,二分,数学', kid=8),

    P('约数个数', 2,
      '给定一个正整数 n，求它的正约数个数。',
      '一行，一个整数 n。',
      '一行，一个整数。',
      '12', '6',
      '''import sys

n = int(sys.stdin.read().strip())
ans = 1
d = 2
cnt = 0
while d * d <= n:
    while n % d == 0:
        cnt += 1
        n //= d
    if cnt:
        ans *= cnt + 1
        cnt = 0
    d += 1
if n > 1:
    ans *= 2
print(ans)
''',
      lambda r: str(r.randint(1, 10 ** 9)),
      hint='先质因数分解 n = ∏ pᵢ^aᵢ，则约数个数为 ∏(aᵢ + 1)：每个质因子可选 0..aᵢ 个。',
      scope='1 ≤ n ≤ 10⁹', tags='数论,约数,分解', kid=8),

    P('约数之和', 2,
      '给定一个正整数 n，求它的所有正约数之和。',
      '一行，一个整数 n。',
      '一行，一个整数。',
      '12', '28',
      '''import sys

n = int(sys.stdin.read().strip())
ans = 1
d = 2
while d * d <= n:
    if n % d == 0:
        p = 1
        while n % d == 0:
            n //= d
            p = p * d + 1
        ans *= p
    d += 1
if n > 1:
    ans *= n + 1
print(ans)
''',
      lambda r: str(r.randint(1, 10 ** 8)),
      hint='若 n = ∏ pᵢ^aᵢ，则约数和为 ∏(1 + pᵢ + … + pᵢ^aᵢ)；代码中的 p = p*d + 1 正是等比和的递推。',
      scope='1 ≤ n ≤ 10⁸', tags='数论,约数,等比数列', kid=8),

    P('最大质因子', 2,
      '给定一个大于 1 的整数 n，求它的最大质因子。',
      '一行，一个整数 n。',
      '一行，一个整数。',
      '60', '5',
      '''import sys

n = int(sys.stdin.read().strip())
ans = 1
d = 2
while d * d <= n:
    while n % d == 0:
        ans = d
        n //= d
    d += 1
if n > 1:
    ans = n
print(ans)
''',
      lambda r: str(r.randint(2, 10 ** 9)),
      hint='边分解边记录最后除尽的因子；循环结束后若剩余的 n 大于 1，它本身就是最大的质因子。',
      scope='2 ≤ n ≤ 10⁹', tags='数论,质因数', kid=8),

    P('欧拉函数', 3,
      '给定正整数 n，求欧拉函数 φ(n)，即 1 到 n 中与 n 互质的数的个数。',
      '一行，一个整数 n。',
      '一行，一个整数。',
      '10', '4',
      '''import sys

n = int(sys.stdin.read().strip())
ans = n
x = n
d = 2
while d * d <= x:
    if x % d == 0:
        while x % d == 0:
            x //= d
        ans = ans // d * (d - 1)
    d += 1
if x > 1:
    ans = ans // x * (x - 1)
print(ans)
''',
      lambda r: str(r.randint(1, 10 ** 9)),
      hint='利用公式 φ(n) = n × ∏(1 - 1/p)：对每个不同质因子 p，执行 ans = ans // p × (p - 1)。',
      scope='1 ≤ n ≤ 10⁹', tags='数论,欧拉函数', kid=8),

    P('分数化简', 2,
      '给定一个分数 a/b，将其化为最简分数后输出；若分母为 1 则只输出分子。',
      '一行，形如 a/b 的分数（a、b 为正整数）。',
      '一行，化简后的结果。',
      '12/18', '2/3',
      '''import sys
import math

s = sys.stdin.read().strip()
a, b = map(int, s.split('/'))
g = math.gcd(a, b)
a //= g
b //= g
print(str(a) if b == 1 else '%d/%d' % (a, b))
''',
      _gen_frac,
      hint='分子分母同除以最大公约数即得最简分数；注意化简后分母为 1 时的输出格式。',
      scope='1 ≤ a, b ≤ 10⁹', tags='数论,gcd,分数', kid=8),

    P('分数加法', 2,
      '给定两个分数 a/b 和 c/d，求它们的和，并化为最简分数输出；若分母为 1 则只输出分子。',
      '一行，两个形如 a/b 的分数，用空格分隔。',
      '一行，相加并化简后的结果。',
      '1/2 1/3', '5/6',
      '''import sys
import math

parts = sys.stdin.read().split()
a, b = map(int, parts[0].split('/'))
c, d = map(int, parts[1].split('/'))
p = a * d + c * b
q = b * d
g = math.gcd(p, q)
p //= g
q //= g
print(str(p) if q == 1 else '%d/%d' % (p, q))
''',
      _gen_frac2,
      hint='通分后分子相加，再用 gcd 约分；先通分后约分可以少写一次约分逻辑。',
      scope='1 ≤ a, b, c, d ≤ 10⁴', tags='数论,gcd,分数运算', kid=8),

    P('斐波那契第 n 项取模', 2,
      '求斐波那契数列第 n 项对 10⁹+7 取模的值。数列定义为 F(1) = 1，F(2) = 1，F(n) = F(n-1) + F(n-2)（n ≥ 3）。',
      '一行，一个整数 n。',
      '一行，一个整数。',
      '10', '55',
      '''import sys

MOD = 10 ** 9 + 7
n = int(sys.stdin.read().strip())
a, b = 1, 1
for _ in range(3, n + 1):
    a, b = b, (a + b) % MOD
print(a if n <= 2 else b % MOD)
''',
      lambda r: str(r.randint(1, 10 ** 6)),
      hint='滚动变量迭代即可，只需保留前两项，边加边取模防止数值爆炸，O(n) 时间 O(1) 空间。',
      scope='1 ≤ n ≤ 10⁷', tags='递推,取模,斐波那契', kid=8),

    P('3n+1 问题', 2,
      '给定一个正整数 n，反复执行：若为偶数则除以 2，若为奇数则变为 3n+1，直到变成 1 为止。求需要的变换次数。',
      '一行，一个整数 n。',
      '一行，一个整数，表示变换次数。',
      '3', '7',
      '''import sys

n = int(sys.stdin.read().strip())
cnt = 0
while n != 1:
    if n % 2 == 0:
        n //= 2
    else:
        n = 3 * n + 1
    cnt += 1
print(cnt)
''',
      lambda r: str(r.randint(1, 1000)),
      hint='直接按规则模拟即可（考拉兹猜想至今未被证明，但对题目给定范围一定收敛）。注意用整数运算避免溢出。',
      scope='1 ≤ n ≤ 10⁶', tags='模拟,数论,考拉兹', kid=8),

    P('数字黑洞 495', 2,
      '给定一个各位数字不全相同的三位数 n，重复下列操作：把三个数字重新排列成最大数和最小数（允许前导零），用最大数减最小数得到新数；直到结果等于 495 为止。求操作的次数。',
      '一行，一个三位数 n（各位数字不全相同）。',
      '一行，一个整数，表示操作次数。',
      '123', '5',
      '''import sys

n = int(sys.stdin.read().strip())
cnt = 0
while n != 495:
    digits = sorted('%03d' % n)
    small = int(''.join(digits))
    big = int(''.join(reversed(digits)))
    n = big - small
    cnt += 1
print(cnt)
''',
      _gen_digits3,
      hint='每次重排得到最大与最小三位数并相减；补零用 \'%03d\' 格式化保证始终取到三位，最终必然收敛到 495。',
      scope='100 ≤ n ≤ 999，各位数字不全相同', tags='模拟,数论,卡普雷卡尔', kid=8),
]
