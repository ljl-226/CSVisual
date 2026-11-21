-- ============================================================
--  程序设计算法题（在线判题）种子数据：algorithm + algorithm_case
--  说明：
--    1. weight（权值，用于排名计分）：难度 1-2 -> 10，难度 3 -> 20，难度 4 -> 30，难度 5 -> 50
--    2. knowledge_id 取自 /api/course/1 返回的真实知识点 id，无法对应的写 NULL
--    3. 每道题先单独 INSERT 一条 algorithm，紧跟 SET @aid = LAST_INSERT_ID();，
--       再用 (@aid, ...) 插入该题的测试用例，保证用例挂在正确的题目上
--    4. 每个用例的 expected 由 Python 3.12 真实运行 reference_code 得到，
--       与程序标准输出逐字符一致（含行末换行）
--    5. 参考代码统一为 Python 3，reference_language = 'python'
--  执行顺序：schema.sql -> ... -> seed-algo.sql
-- ============================================================

USE cs_visual;

SET NAMES utf8mb4;

-- ---------- A+B 问题（难度 1，权值 10） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('A+B 问题', 1, 10, '## 【题目描述】\n\n给定两个整数 a 和 b，求它们的和。本题用于熟悉平台的输入输出方式。\n\n## 【输入格式】\n\n一行输入两个用空格分隔的整数 a、b，取值范围 -10^9 ~ 10^9。\n\n## 【输出格式】\n\n输出一个整数，即 a + b 的值。\n\n## 【样例】\n\n输入：\n\n```\n3 5\n```\n\n输出：\n\n```\n8\n```', '一行输入两个用空格分隔的整数 a 和 b（-10^9 <= a, b <= 10^9）。', '输出一个整数，表示 a + b 的结果。', '3 5', '8\n', '签到题，重点在于掌握在线判题的输入输出方式：用 sys.stdin.read() 一次性读入全部内容再 split 成 token 列表，比逐个 input() 更稳（可兼容换行位置不固定的数据）。取前两个 token 转 int 相加后 print 即可。时间复杂度 O(1)，空间复杂度 O(1)。注意负数与大数相加不要溢出（Python 整数无精度限制）。', 'import sys


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    a = int(data[0])
    b = int(data[1])
    print(a + b)


if __name__ == ''__main__'':
    main()
', 'python', '基础,模拟', '基础', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3 5', '8\n', 1, 1),
(@aid, '-2 7', '5\n', 0, 2),
(@aid, '0 0', '0\n', 0, 3),
(@aid, '1000000000 2000000000', '3000000000\n', 0, 4),
(@aid, '-100 -250', '-350\n', 0, 5);

-- ---------- 素数判断（难度 1，权值 10） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('素数判断', 1, 10, '## 【题目描述】\n\n给定 T 个整数，判断每个整数是否为素数（质数）。素数定义为大于 1 且除了 1 和它本身外没有其他正因子的整数。\n\n## 【输入格式】\n\n第一行输入整数 T，表示待判定的整数个数（1 <= T <= 100）。\n接下来 T 行，每行一个整数 x（-10^6 <= x <= 10^6）。\n\n## 【输出格式】\n\n对每个 x 输出一行：若为素数输出 `Yes`，否则输出 `No`。\n\n## 【样例】\n\n输入：\n\n```\n5\n2\n1\n97\n100\n7919\n```\n\n输出：\n\n```\nYes\nNo\nYes\nNo\nYes\n```', '第一行一个整数 T（1 <= T <= 100），接下来 T 行每行一个整数 x（-10^6 <= x <= 10^6）。', '对每个 x 输出一行：是素数输出 Yes，否则输出 No。', '5\n2\n1\n97\n100\n7919', 'Yes\nNo\nYes\nNo\nYes\n', '试除法判定素数：小于 2 一定不是素数；2 是素数；偶数（除 2 外）不是素数；之后只枚举奇因子 d = 3,5,7...，循环条件为 d * d <= x（因为若 x 有大于 sqrt(x) 的因子，必有小于 sqrt(x) 的配对因子）。单个数的判定复杂度 O(sqrt(x))，总复杂度 O(T * sqrt(x))，空间 O(1)。注意负数、0、1 都不是素数。', 'import sys


def is_prime(x):
    if x < 2:
        return False
    if x == 2:
        return True
    if x % 2 == 0:
        return False
    d = 3
    while d * d <= x:
        if x % d == 0:
            return False
        d += 2
    return True


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    t = int(data[0])
    out = []
    for i in range(1, t + 1):
        x = int(data[i])
        out.append(''Yes'' if is_prime(x) else ''No'')
    print(''\\n''.join(out))


if __name__ == ''__main__'':
    main()
', 'python', '数学,素数', '基础', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '5\n2\n1\n97\n100\n7919', 'Yes\nNo\nYes\nNo\nYes\n', 1, 1),
(@aid, '1\n1', 'No\n', 0, 2),
(@aid, '3\n0\n2\n4', 'No\nYes\nNo\n', 0, 3),
(@aid, '2\n104729\n104730', 'Yes\nNo\n', 0, 4),
(@aid, '4\n-7\n9\n25\n49', 'No\nNo\nNo\nNo\n', 0, 5);

-- ---------- 最大公约数与最小公倍数（难度 2，权值 10） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('最大公约数与最小公倍数', 2, 10, '## 【题目描述】\n\n给定两个整数 a、b，求它们的最大公约数（GCD）与最小公倍数（LCM）。\n\n## 【输入格式】\n\n一行输入两个整数 a、b，用空格分隔，0 <= |a|, |b| <= 10^9。\n\n## 【输出格式】\n\n输出一行，包含两个整数：最大公约数和最小公倍数，用空格分隔。\n若 a、b 同时为 0，则输出 `0 0`。\n\n## 【样例】\n\n输入：\n\n```\n12 18\n```\n\n输出：\n\n```\n6 36\n```', '一行输入两个整数 a、b（0 <= |a|, |b| <= 10^9）。', '输出一行两个整数，分别为最大公约数和最小公倍数，用空格分隔。', '12 18', '6 36\n', '用欧几里得算法（辗转相除法）求 gcd：反复用 (a, b) -> (b, a % b) 直到 b 为 0，此时的 a 即最大公约数，复杂度 O(log min(a,b))。最小公倍数由恒等式 lcm = |a * b| / gcd 得到，注意先除后乘避免中间结果过大。两个数都为 0 时 gcd 为 0，此时约定 lcm 为 0。负数先取绝对值再计算。', 'import sys


def gcd(a, b):
    a = abs(a)
    b = abs(b)
    while b:
        a, b = b, a % b
    return a


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    a = int(data[0])
    b = int(data[1])
    g = gcd(a, b)
    if g == 0:
        print(0, 0)
    else:
        print(g, abs(a * b) // g)


if __name__ == ''__main__'':
    main()
', 'python', '数学,欧几里得', '基础', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '12 18', '6 36\n', 1, 1),
(@aid, '7 5', '1 35\n', 0, 2),
(@aid, '0 5', '5 0\n', 0, 3),
(@aid, '-12 18', '6 36\n', 0, 4),
(@aid, '0 0', '0 0\n', 0, 5),
(@aid, '1000000007 1000000007', '1000000007 1000000007\n', 0, 6);

-- ---------- 进制转换（难度 2，权值 10） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('进制转换', 2, 10, '## 【题目描述】\n\n将一个十进制整数 n 转换为 r 进制（2 <= r <= 16）表示。\n\n## 【输入格式】\n\n一行输入两个整数 n 和 r，用空格分隔。其中 -10^9 <= n <= 10^9，2 <= r <= 16。\n\n## 【输出格式】\n\n输出一行字符串，即 n 的 r 进制表示。数码 10~15 分别用大写字母 A、B、C、D、E、F 表示；若 n 为负数，结果保留负号。\n\n## 【样例】\n\n输入：\n\n```\n10 2\n```\n\n输出：\n\n```\n1010\n```', '一行输入两个整数 n 和 r（-10^9 <= n <= 10^9，2 <= r <= 16），分别表示十进制数与目标进制。', '输出一行，即 n 的 r 进制表示，10 以上的数码用大写字母 A~F 表示。', '10 2', '1010\n', '除基取余法：反复用 n 对 r 取余得到最低位数码，再令 n = n // r，直到 n 为 0，最后把得到的数码序列逆序输出即为结果。数码表用字符串 0123456789ABCDEF 按下标取字符，避免分支判断。负数先记录符号再对绝对值转换。n = 0 时结果为 0，需要单独处理。时间复杂度 O(log_r |n|)，空间 O(log_r |n|)。', 'import sys

DIGITS = ''0123456789ABCDEF''


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    r = int(data[1])
    if n == 0:
        print(''0'')
        return
    neg = n < 0
    n = abs(n)
    res = []
    while n > 0:
        res.append(DIGITS[n % r])
        n //= r
    if neg:
        res.append(''-'')
    print(''''.join(reversed(res)))


if __name__ == ''__main__'':
    main()
', 'python', '数学,进制', 'NCRE', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '10 2', '1010\n', 1, 1),
(@aid, '255 16', 'FF\n', 0, 2),
(@aid, '0 8', '0\n', 0, 3),
(@aid, '-10 2', '-1010\n', 0, 4),
(@aid, '1000 8', '1750\n', 0, 5),
(@aid, '48879 16', 'BEEF\n', 0, 6);

-- ---------- 字符串反转（难度 1，权值 10） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('字符串反转', 1, 10, '## 【题目描述】\n\n给定 T 个字符串，将每个字符串反转后输出。\n\n## 【输入格式】\n\n第一行输入整数 T，表示字符串个数（1 <= T <= 100）。\n接下来 T 行，每行一个字符串，长度不超过 100，可能包含空格，也可能是空串。\n\n## 【输出格式】\n\n对每个字符串输出一行，即反转后的字符串（原样保留其中的空格）。\n\n## 【样例】\n\n输入：\n\n```\n3\nabc\nHello\n12345\n```\n\n输出：\n\n```\ncba\nolleH\n54321\n```', '第一行一个整数 T（1 <= T <= 100），接下来 T 行，每行一个字符串（长度不超过 100，可含空格，可为空串）。', '对每行字符串输出一行，即其反转后的结果。', '3\nabc\nHello\n12345', 'cba\nolleH\n54321\n', '用 sys.stdin.read().splitlines() 按行读入（不能用 split()，否则会丢掉行内的空格与空行），第 0 行是 T，之后逐行用 Python 切片 s[::-1] 完成反转，最后用 join 一次性输出。切片反转的时间复杂度 O(len(s))，总复杂度为所有字符串长度之和，空间复杂度同阶。注意空串反转后仍是空串，输出一个空行。', 'import sys


def main():
    lines = sys.stdin.read().splitlines()
    if not lines:
        return
    t = int(lines[0].strip())
    out = []
    for i in range(1, t + 1):
        out.append(lines[i][::-1])
    print(''\\n''.join(out))


if __name__ == ''__main__'':
    main()
', 'python', '字符串,基础', '基础', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3\nabc\nHello\n12345', 'cba\nolleH\n54321\n', 1, 1),
(@aid, '1\na', 'a\n', 0, 2),
(@aid, '2\n\nab', '\nba\n', 0, 3),
(@aid, '1\nabcdcba', 'abcdcba\n', 0, 4),
(@aid, '1\nhello world', 'dlrow olleh\n', 0, 5);

-- ---------- 两数之和（难度 2，权值 10） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('两数之和', 2, 10, '## 【题目描述】\n\n给定一个整数数组 nums 和一个目标值 target，请在数组中找出和为目标值的两个整数，并返回它们的数组下标。\n\n你可以假设每种输入只会对应一个答案，且同一个元素不能重复使用；若存在多组解，请输出第一个下标 i 最小的那组。\n\n## 【输入格式】\n\n第一行输入两个整数 n 和 target，用空格分隔（2 <= n <= 10^5）。\n第二行输入 n 个整数，用空格分隔。\n\n## 【输出格式】\n\n输出一行两个整数 i 和 j（下标从 0 开始），用空格分隔，满足 i < j 且 nums[i] + nums[j] == target。\n\n## 【样例】\n\n输入：\n\n```\n4 9\n2 7 11 15\n```\n\n输出：\n\n```\n0 1\n```', '第一行两个整数 n 和 target（2 <= n <= 10^5）；第二行 n 个用空格分隔的整数。', '输出一行两个整数 i 和 j（0 开始的下标），满足 nums[i] + nums[j] == target 且 i < j；若有多解输出 i 最小的那组。', '4 9\n2 7 11 15', '0 1\n', '暴力双重循环 O(n^2) 会超时，用哈希表把"查找补数"降到 O(1)：从左往右扫描，对当前值 v 先查 target - v 是否已在表中（在则直接得到答案，且 i 是最小的），再把 v 与它的下标存入表（只保留首次出现的下标，保证 i 最小）。整体一趟扫描，时间复杂度 O(n)，空间复杂度 O(n)。题目保证有解，且同一元素不能重复使用（先查后存天然满足）。', 'import sys


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    target = int(data[1])
    nums = list(map(int, data[2:2 + n]))
    pos = {}
    ans = (-1, -1)
    for i, v in enumerate(nums):
        need = target - v
        if need in pos:
            ans = (pos[need], i)
            break
        if v not in pos:
            pos[v] = i
    print(ans[0], ans[1])


if __name__ == ''__main__'':
    main()
', 'python', '数组,哈希表', '基础', 33);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '4 9\n2 7 11 15', '0 1\n', 1, 1),
(@aid, '3 6\n3 2 4', '1 2\n', 0, 2),
(@aid, '4 0\n-3 4 3 90', '0 2\n', 0, 3),
(@aid, '4 8\n4 4 4 4', '0 1\n', 0, 4),
(@aid, '2 1000000000\n500000000 500000000', '0 1\n', 0, 5);

-- ---------- 最长无重复字符子串（难度 3，权值 20） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('最长无重复字符子串', 3, 20, '## 【题目描述】\n\n给定一个字符串 s，请找出其中不含有重复字符的最长子串的长度。\n\n子串必须是原字符串中连续的一段。\n\n## 【输入格式】\n\n输入一行字符串 s，长度不超过 10^5，可能包含空格与任意可见字符，也可能是空串。\n\n## 【输出格式】\n\n输出一个整数，表示最长无重复字符子串的长度。\n\n## 【样例】\n\n输入：\n\n```\nabcabcbb\n```\n\n输出：\n\n```\n3\n```\n\n（答案为 "abc"，长度为 3。）', '输入一行字符串 s（长度不超过 10^5，可含空格与任意可见字符，可为空串）。', '输出一个整数，即 s 中不含重复字符的最长子串的长度。', 'abcabcbb', '3\n', '滑动窗口（双指针）：维护窗口 [left, i] 始终无重复字符，用哈希表记录每个字符最后一次出现的下标。右指针 i 逐个右移，若当前字符上次出现的位置 >= left，说明它在窗口内重复，就把 left 跳到该位置 +1；随后更新该字符的最后位置，并用 i - left + 1 更新答案。每个字符只进出窗口一次，时间复杂度 O(n)，空间复杂度 O(字符集大小)。空串答案为 0。', 'import sys


def main():
    s = sys.stdin.readline().rstrip(''\\n'')
    last = {}
    left = 0
    best = 0
    for i, ch in enumerate(s):
        if ch in last and last[ch] >= left:
            left = last[ch] + 1
        last[ch] = i
        cur = i - left + 1
        if cur > best:
            best = cur
    print(best)


if __name__ == ''__main__'':
    main()
', 'python', '字符串,滑动窗口,双指针', '期末', 33);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'abcabcbb', '3\n', 1, 1),
(@aid, 'bbbbb', '1\n', 0, 2),
(@aid, 'pwwkew', '3\n', 0, 3),
(@aid, '', '0\n', 0, 4),
(@aid, 'abcdef', '6\n', 0, 5),
(@aid, 'dvdf', '3\n', 0, 6);

-- ---------- 合并区间（难度 3，权值 20） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('合并区间', 3, 20, '## 【题目描述】\n\n给定若干个闭区间，请把所有有重叠（或首尾相接）的区间合并，输出合并后的区间集合。\n\n两个区间 [a, b] 与 [c, d] 若满足 c <= b，则认为它们可以合并为 [a, max(b, d)]。\n\n## 【输入格式】\n\n第一行输入整数 n，表示区间个数（0 <= n <= 10^5）。\n接下来 n 行，每行两个整数 l、r，用空格分隔，表示闭区间 [l, r]，保证 l <= r。\n\n## 【输出格式】\n\n按左端点从小到大，每行输出一个合并后的区间 `l r`。\n若 n = 0，不输出任何内容。\n\n## 【样例】\n\n输入：\n\n```\n4\n1 3\n2 6\n8 10\n15 18\n```\n\n输出：\n\n```\n1 6\n8 10\n15 18\n```', '第一行一个整数 n（0 <= n <= 10^5）；接下来 n 行，每行两个整数 l 和 r（l <= r），表示一个闭区间。', '按左端点从小到大输出合并后的每个区间，每行一个区间 "l r"；若 n = 0 则不输出任何内容。', '4\n1 3\n2 6\n8 10\n15 18', '1 6\n8 10\n15 18\n', '先按左端点升序排序（左端点相同则按右端点），再线性扫描做合并：维护结果列表，若当前区间的左端点 <= 结果末尾区间的右端点，则二者有交集或相接，把它们合并（右端点取较大者）；否则把当前区间追加进结果。排序 O(n log n)、扫描 O(n)，总时间复杂度 O(n log n)，空间复杂度 O(n)。注意 n = 0 时没有任何输出。', 'import sys


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    nums = list(map(int, data[1:]))
    it = []
    for i in range(n):
        it.append((nums[2 * i], nums[2 * i + 1]))
    it.sort()
    res = []
    for l, r in it:
        if res and l <= res[-1][1]:
            if r > res[-1][1]:
                res[-1] = (res[-1][0], r)
        else:
            res.append((l, r))
    if not res:
        return
    print(''\\n''.join(str(a) + '' '' + str(b) for a, b in res))


if __name__ == ''__main__'':
    main()
', 'python', '数组,排序,区间', '期末', 6);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '4\n1 3\n2 6\n8 10\n15 18', '1 6\n8 10\n15 18\n', 1, 1),
(@aid, '2\n2 3\n1 5', '1 5\n', 0, 2),
(@aid, '0', '', 0, 3),
(@aid, '2\n1 4\n4 5', '1 5\n', 0, 4),
(@aid, '3\n1 10\n2 3\n4 5', '1 10\n', 0, 5);

-- ---------- KMP 子串查找（难度 4，权值 30） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('KMP 子串查找', 4, 30, '## 【题目描述】\n\n给定文本串 T 与模式串 P，请用 KMP 算法找出 P 在 T 中第一次出现的位置。要求时间复杂度为线性，不得使用朴素的字符串暴力匹配（否则大数据会超时）。\n\n## 【输入格式】\n\n第一行输入文本串 T。\n第二行输入模式串 P。\n两串长度均不超过 10^5，均由可见字符组成且不含空格。\n\n## 【输出格式】\n\n输出一个整数：P 在 T 中第一次出现的起始下标（下标从 0 开始）；若 P 不是 T 的子串，输出 -1。\n\n## 【样例】\n\n输入：\n\n```\nababcabcabababd\nababd\n```\n\n输出：\n\n```\n10\n```', '第一行输入文本串 T，第二行输入模式串 P（长度均不超过 10^5，不含空格）。', '输出一个整数：P 在 T 中第一次出现的起始下标（从 0 开始）；若不存在则输出 -1。', 'ababcabcabababd\nababd', '10\n', 'KMP 的核心是"失配时不回退文本指针"。先对模式串预处理出前缀函数 lps[i]（P[0..i] 的最长相等真前后缀长度），用双指针自匹配在线性时间内求出；匹配阶段文本指针 i 只增不减，失配时令 j = lps[j-1] 继续比较，直到 j 等于模式串长度即命中。预处理 O(m)、匹配 O(n)，总复杂度 O(n + m)，空间 O(m)。若模式串为空串，约定匹配位置为 0。', 'import sys


def build_lps(p):
    m = len(p)
    lps = [0] * m
    j = 0
    for i in range(1, m):
        while j > 0 and p[i] != p[j]:
            j = lps[j - 1]
        if p[i] == p[j]:
            j += 1
        lps[i] = j
    return lps


def main():
    lines = sys.stdin.read().splitlines()
    if not lines:
        text = ''''
        pat = ''''
    elif len(lines) < 2:
        text = lines[0]
        pat = ''''
    else:
        text = lines[0]
        pat = lines[1]
    if not pat:
        print(0)
        return
    lps = build_lps(pat)
    j = 0
    ans = -1
    for i, ch in enumerate(text):
        while j > 0 and ch != pat[j]:
            j = lps[j - 1]
        if ch == pat[j]:
            j += 1
        if j == len(pat):
            ans = i - len(pat) + 1
            break
    print(ans)


if __name__ == ''__main__'':
    main()
', 'python', '字符串,KMP', '考研408', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'ababcabcabababd\nababd', '10\n', 1, 1),
(@aid, 'aaaaa\naa', '0\n', 0, 2),
(@aid, 'abcdef\ngh', '-1\n', 0, 3),
(@aid, 'a\na', '0\n', 0, 4),
(@aid, 'mississippi\nissip', '4\n', 0, 5),
(@aid, 'abcabcabc\nabc', '0\n', 0, 6);

-- ---------- 快速排序（难度 3，权值 20） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('快速排序', 3, 20, '## 【题目描述】\n\n给定一个整数序列，请用快速排序算法将其按升序排列并输出。\n\n要求真正实现快速排序的划分与递归过程（禁止直接调用语言内置的 sort）。\n\n## 【输入格式】\n\n第一行输入整数 n（0 <= n <= 10^4）。\n第二行输入 n 个整数，用空格分隔，取值范围 -10^9 ~ 10^9。\n\n## 【输出格式】\n\n输出一行，为升序排列后的 n 个整数，用空格分隔；n = 0 时输出一个空行。\n\n## 【样例】\n\n输入：\n\n```\n8\n49 38 65 97 76 13 27 49\n```\n\n输出：\n\n```\n13 27 38 49 49 65 76 97\n```', '第一行一个整数 n（0 <= n <= 10^4）；第二行 n 个用空格分隔的整数。', '输出一行，即升序排序后的 n 个整数，用空格分隔；n = 0 时输出空行。', '8\n49 38 65 97 76 13 27 49', '13 27 38 49 49 65 76 97\n', '分治思想：选取基准元素 pivot，把数组划分成"小于 pivot""等于 pivot""大于 pivot"三段，再递归排序左右两段后拼接。用三路划分可以天然处理大量重复元素，避免退化。平均时间复杂度 O(n log n)，最坏 O(n^2)，空间复杂度 O(n)（递归栈 O(log n)）。实现时注意基准可取中点元素以降低遇到有序数据退化的概率。', 'import sys


def quick_sort(a):
    if len(a) <= 1:
        return a
    pivot = a[len(a) // 2]
    left = [x for x in a if x < pivot]
    mid = [x for x in a if x == pivot]
    right = [x for x in a if x > pivot]
    return quick_sort(left) + mid + quick_sort(right)


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    a = list(map(int, data[1:1 + n]))
    print('' ''.join(map(str, quick_sort(a))))


if __name__ == ''__main__'':
    main()
', 'python', '排序,分治,快速排序', '期末', 6);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '8\n49 38 65 97 76 13 27 49', '13 27 38 49 49 65 76 97\n', 1, 1),
(@aid, '1\n5', '5\n', 0, 2),
(@aid, '0', '\n', 0, 3),
(@aid, '5\n-3 0 -3 100 -100', '-100 -3 -3 0 100\n', 0, 4),
(@aid, '6\n1000000000 -1000000000 1 2 3 3', '-1000000000 1 2 3 3 1000000000\n', 0, 5),
(@aid, '5\n5 4 3 2 1', '1 2 3 4 5\n', 0, 6);

-- ---------- 归并排序（难度 3，权值 20） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('归并排序', 3, 20, '## 【题目描述】\n\n给定一个整数序列，请用归并排序（二路归并）将其按升序排列并输出。\n\n要求真正实现"递归分治 + 有序段合并"的过程（禁止直接调用语言内置的 sort）。\n\n## 【输入格式】\n\n第一行输入整数 n（0 <= n <= 10^4）。\n第二行输入 n 个整数，用空格分隔，取值范围 -10^9 ~ 10^9。\n\n## 【输出格式】\n\n输出一行，为升序排列后的 n 个整数，用空格分隔；n = 0 时输出一个空行。\n\n## 【样例】\n\n输入：\n\n```\n8\n49 38 65 97 76 13 27 49\n```\n\n输出：\n\n```\n13 27 38 49 49 65 76 97\n```', '第一行一个整数 n（0 <= n <= 10^4）；第二行 n 个用空格分隔的整数。', '输出一行，即升序排序后的 n 个整数，用空格分隔；n = 0 时输出空行。', '8\n49 38 65 97 76 13 27 49', '13 27 38 49 49 65 76 97\n', '分治 + 合并：把序列递归地一分为二，分别排好序后，用双指针把两个有序段按从小到大"归并"成一个有序段（相等元素取左段在前，保证稳定性）。递推式 T(n) = 2T(n/2) + O(n)，时间复杂度恒为 O(n log n)，且不受输入分布影响；空间复杂度 O(n)（归并辅助数组 + 递归栈）。归并排序是稳定排序，这也是它相对快速排序的重要优势。', 'import sys


def merge_sort(a):
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left = merge_sort(a[:mid])
    right = merge_sort(a[mid:])
    res = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            res.append(left[i])
            i += 1
        else:
            res.append(right[j])
            j += 1
    res.extend(left[i:])
    res.extend(right[j:])
    return res


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    a = list(map(int, data[1:1 + n]))
    print('' ''.join(map(str, merge_sort(a))))


if __name__ == ''__main__'':
    main()
', 'python', '排序,分治,归并排序', '期末', 7);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '8\n49 38 65 97 76 13 27 49', '13 27 38 49 49 65 76 97\n', 1, 1),
(@aid, '0', '\n', 0, 2),
(@aid, '1\n-7', '-7\n', 0, 3),
(@aid, '5\n1 1 1 1 1', '1 1 1 1 1\n', 0, 4),
(@aid, '6\n3 -1 2 -1 0 5', '-1 -1 0 2 3 5\n', 0, 5);

-- ---------- 二分查找（难度 2，权值 10） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('二分查找', 2, 10, '## 【题目描述】\n\n给定一个升序（非严格递增）的整数序列和若干次查询，请对每次查询输出关键字在序列中的下标。\n\n若关键字出现多次，输出最靠左的那个下标；若不存在，输出 -1。要求使用二分查找，复杂度为对数级。\n\n## 【输入格式】\n\n第一行输入两个整数 n 和 m，用空格分隔（1 <= n, m <= 10^5），分别表示序列长度与查询次数。\n第二行输入 n 个整数，按非降序排列，用空格分隔。\n接下来 m 行，每行一个待查关键字。\n\n## 【输出格式】\n\n对每个查询输出一行：找到则输出其下标（下标从 0 开始），未找到输出 -1。\n\n## 【样例】\n\n输入：\n\n```\n5 3\n1 3 5 7 9\n3\n7\n4\n```\n\n输出：\n\n```\n1\n3\n-1\n```', '第一行两个整数 n 和 m；第二行 n 个升序（非降）整数；接下来 m 行每行一个待查关键字。', '对每个关键字输出一行：找到则输出其下标（0 开始，若有重复输出最靠左的下标），否则输出 -1。', '5 3\n1 3 5 7 9\n3\n7\n4', '1\n3\n-1\n', '有序序列上二分：维护区间 [lo, hi)，取中点 mid，若 a[mid] < x 则 lo = mid + 1，否则 hi = mid；结束后 lo 即第一个 >= x 的位置，若 a[lo] == x 则输出 lo，否则输出 -1（得到最靠左的下标）。每次查找 O(log n)，总复杂度 O(m log n)，空间 O(1)。', 'import sys


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    m = int(data[1])
    a = list(map(int, data[2:2 + n]))
    qs = list(map(int, data[2 + n:2 + n + m]))
    out = []
    for x in qs:
        lo = 0
        hi = n
        while lo < hi:
            mid = (lo + hi) // 2
            if a[mid] < x:
                lo = mid + 1
            else:
                hi = mid
        if lo < n and a[lo] == x:
            out.append(str(lo))
        else:
            out.append(''-1'')
    print(''\\n''.join(out))


if __name__ == ''__main__'':
    main()
', 'python', '查找,二分,数组', 'NCRE', 40);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '5 3\n1 3 5 7 9\n3\n7\n4', '1\n3\n-1\n', 1, 1),
(@aid, '1 1\n5\n5', '0\n', 0, 2),
(@aid, '1 1\n5\n6', '-1\n', 0, 3),
(@aid, '6 4\n1 2 2 2 3 4\n2\n4\n1\n0', '1\n5\n0\n-1\n', 0, 4),
(@aid, '3 2\n-5 0 5\n-5\n5', '0\n2\n', 0, 5);

-- ---------- 第 K 大元素（难度 3，权值 20） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('第 K 大元素', 3, 20, '## 【题目描述】\n\n给定一个整数数组，请找出其中第 k 大的元素。注意：需要的是排序后的第 k 大，而不是第 k 个不同的元素，重复元素按出现次数分别计数。\n\n要求使用堆（优先队列）求解，而不是对整个数组排序。\n\n## 【输入格式】\n\n第一行输入两个整数 n 和 k，用空格分隔（1 <= k <= n <= 10^5）。\n第二行输入 n 个整数，用空格分隔，取值范围 -10^9 ~ 10^9。\n\n## 【输出格式】\n\n输出一个整数，表示数组中第 k 大的元素。\n\n## 【样例】\n\n输入：\n\n```\n6 2\n3 2 1 5 6 4\n```\n\n输出：\n\n```\n5\n```', '第一行两个整数 n 和 k（1 <= k <= n <= 10^5）；第二行 n 个用空格分隔的整数。', '输出一个整数，即数组中第 k 大的元素（重复元素按出现次数分别计数）。', '6 2\n3 2 1 5 6 4', '5\n', '维护一个容量为 k 的小根堆：遍历数组，堆未满则直接入堆；堆满后若当前元素大于堆顶（堆中 k 个最大值里最小的那个），就用 heapreplace 弹出堆顶并压入当前元素。遍历结束后堆顶即第 k 大元素。时间复杂度 O(n log k)，空间复杂度 O(k)，比整体排序的 O(n log n) 更省，尤其适合 n 很大而 k 很小的场景。也可用快速选择算法做到平均 O(n)。', 'import sys
import heapq


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    k = int(data[1])
    nums = list(map(int, data[2:2 + n]))
    heap = []
    for v in nums:
        if len(heap) < k:
            heapq.heappush(heap, v)
        elif v > heap[0]:
            heapq.heapreplace(heap, v)
    print(heap[0])


if __name__ == ''__main__'':
    main()
', 'python', '堆,优先队列,选择问题', '期末', 37);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '6 2\n3 2 1 5 6 4', '5\n', 1, 1),
(@aid, '6 1\n3 2 1 5 6 4', '6\n', 0, 2),
(@aid, '3 2\n3 3 3', '3\n', 0, 3),
(@aid, '3 2\n-1 -5 -3', '-3\n', 0, 4),
(@aid, '1 1\n42', '42\n', 0, 5),
(@aid, '5 5\n7 3 9 1 4', '1\n', 0, 6);

-- ---------- 反转单链表（难度 3，权值 20） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('反转单链表', 3, 20, '## 【题目描述】\n\n给定一个单链表，请将其反转，并返回反转后链表的元素序列。\n\n要求原地修改指针方向，时间复杂度 O(n)、空间复杂度 O(1)，不得借助数组直接倒序输出。\n\n## 【输入格式】\n\n第一行输入整数 n，表示链表结点个数（0 <= n <= 10^5）。\n第二行输入 n 个整数，用空格分隔，依次为从头结点到尾结点各结点的值。\nn = 0 表示空链表。\n\n## 【输出格式】\n\n输出一行，为反转后链表从头到尾各结点的值，用空格分隔。\n若原链表为空（n = 0），输出 `NULL`。\n\n## 【样例】\n\n输入：\n\n```\n5\n1 2 3 4 5\n```\n\n输出：\n\n```\n5 4 3 2 1\n```', '第一行一个整数 n（0 <= n <= 10^5）；第二行 n 个整数，依次为从头结点到尾结点的元素值。', '输出一行，即反转后从头到尾的元素值，用空格分隔；若原链表为空，输出 NULL。', '5\n1 2 3 4 5', '5 4 3 2 1\n', '迭代法（头插思想）反转：维护 prev、cur 两个指针，每次先暂存 cur.next，再把 cur.next 指向 prev（反转指针方向），然后 prev 与 cur 同时后移；循环结束时 prev 即新头结点。全过程只遍历一次链表，时间复杂度 O(n)，空间复杂度 O(1)，比递归法（栈深 O(n)）更省空间。注意必须"先存后继再改指针"，否则后继结点会丢失。n = 0 时输出 NULL。', 'import sys


class Node:
    __slots__ = (''val'', ''next'')

    def __init__(self, val=0, nxt=None):
        self.val = val
        self.next = nxt


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    vals = list(map(int, data[1:1 + n]))
    head = None
    tail = None
    for v in vals:
        node = Node(v)
        if head is None:
            head = node
            tail = node
        else:
            tail.next = node
            tail = node
    prev = None
    cur = head
    while cur is not None:
        nxt = cur.next
        cur.next = prev
        prev = cur
        cur = nxt
    out = []
    cur = prev
    while cur is not None:
        out.append(str(cur.val))
        cur = cur.next
    if out:
        print('' ''.join(out))
    else:
        print(''NULL'')


if __name__ == ''__main__'':
    main()
', 'python', '链表,双指针', '考研408', 1);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '5\n1 2 3 4 5', '5 4 3 2 1\n', 1, 1),
(@aid, '0', 'NULL\n', 0, 2),
(@aid, '1\n7', '7\n', 0, 3),
(@aid, '3\n-1 0 1', '1 0 -1\n', 0, 4),
(@aid, '4\n2 2 2 2', '2 2 2 2\n', 0, 5);

-- ---------- 括号匹配（难度 2，权值 10） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('括号匹配', 2, 10, '## 【题目描述】\n\n给定一个只由小括号 `()`、中括号 `[]`、大括号 `{}` 组成的字符串，判断其中的括号是否合法匹配。\n\n合法的条件是：每个左括号都必须被相同类型的右括号闭合，且左右括号的嵌套顺序正确（如 `([)]` 是非法的）。空串视为合法。\n\n## 【输入格式】\n\n第一行输入整数 T，表示字符串个数（1 <= T <= 100）。\n接下来 T 行，每行一个字符串，长度不超过 10^4，只含 `()[]{}` 六种字符，可能为空串。\n\n## 【输出格式】\n\n对每个字符串输出一行：匹配输出 `Yes`，否则输出 `No`。\n\n## 【样例】\n\n输入：\n\n```\n3\n{[()]}\n([)]\n([{}])\n```\n\n输出：\n\n```\nYes\nNo\nYes\n```', '第一行一个整数 T（1 <= T <= 100）；接下来 T 行，每行一个只含 ()[]{} 的字符串（可为空串）。', '对每个字符串输出一行：括号完全匹配输出 Yes，否则输出 No。', '5\n{[()]}\n([)]\n\n((()))\n{[]}(', 'Yes\nNo\nYes\nYes\nNo\n', '栈的典型应用：从左到右扫描，遇到左括号 (、[、{ 就入栈；遇到右括号时，若栈为空或栈顶不是与之配对的左括号，立即判定失败，否则弹出栈顶。扫描结束后栈必须为空才算完全匹配（否则有左括号未被闭合）。每个字符最多进出栈一次，时间复杂度 O(n)，空间复杂度 O(n)（最坏全部是左括号）。空串视为匹配。', 'import sys

PAIR = {'')'': ''('', '']'': ''['', ''}'': ''{''}


def check(s):
    stack = []
    for ch in s:
        if ch in ''([{'':
            stack.append(ch)
        elif ch in PAIR:
            if not stack or stack[-1] != PAIR[ch]:
                return False
            stack.pop()
    return not stack


def main():
    lines = sys.stdin.read().splitlines()
    if not lines:
        return
    t = int(lines[0].strip())
    out = []
    for i in range(1, t + 1):
        out.append(''Yes'' if check(lines[i]) else ''No'')
    print(''\\n''.join(out))


if __name__ == ''__main__'':
    main()
', 'python', '栈,字符串', '期末', 2);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '5\n{[()]}\n([)]\n\n((()))\n{[]}(', 'Yes\nNo\nYes\nYes\nNo\n', 1, 1),
(@aid, '1\n(((', 'No\n', 0, 2),
(@aid, '2\n[]\n[)', 'Yes\nNo\n', 0, 3),
(@aid, '3\n{}{}{}\n([{}])\n({)}', 'Yes\nYes\nNo\n', 0, 4),
(@aid, '1\n)((', 'No\n', 0, 5);

-- ---------- 用栈实现队列（难度 3，权值 20） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('用栈实现队列', 3, 20, '## 【题目描述】\n\n请只使用栈（后进先出）的数据结构来实现一个队列（先进先出），支持入队 push 与出队 pop 两种操作。\n\n要求每个操作的摊还时间复杂度为 O(1)。\n\n## 【输入格式】\n\n第一行输入整数 m，表示操作个数（1 <= m <= 10^5）。\n接下来 m 行，每行一个操作：\n- `push x`：把整数 x 插入队尾；\n- `pop`：删除队头元素并输出它；若队列为空，输出 `Empty`。\n\n## 【输出格式】\n\n对每个 `pop` 操作输出一行：队列非空时输出出队元素的值，队列为空时输出 `Empty`。\n\n## 【样例】\n\n输入：\n\n```\n7\npush 1\npush 2\npop\npush 3\npop\npop\npop\n```\n\n输出：\n\n```\n1\n2\n3\nEmpty\n```', '第一行一个整数 m（1 <= m <= 10^5）；接下来 m 行，每行为 "push x" 或 "pop"。', '对每个 pop 操作输出一行：队列非空时输出出队元素，队列为空时输出 Empty。', '7\npush 1\npush 2\npop\npush 3\npop\npop\npop', '1\n2\n3\nEmpty\n', '用两个栈 s1（输入栈）与 s2（输出栈）模拟队列：入队时压入 s1；出队时若 s2 非空直接弹出 s2 栈顶，否则把 s1 中元素逐个弹出并压入 s2（这一倒腾把顺序反转了一次，恰好满足 FIFO），再弹出 s2 栈顶。每个元素最多被搬运一次，因此每个操作的摊还时间复杂度为 O(1)，空间复杂度 O(n)。注意倒腾的触发条件是"s2 为空"，这是保证顺序正确的关键。', 'import sys


def main():
    lines = sys.stdin.read().splitlines()
    if not lines:
        return
    m = int(lines[0].strip())
    sin = []
    sout = []
    out = []
    for i in range(1, m + 1):
        parts = lines[i].split()
        if not parts:
            continue
        if parts[0] == ''push'':
            sin.append(int(parts[1]))
        else:
            if not sout:
                while sin:
                    sout.append(sin.pop())
            if sout:
                out.append(str(sout.pop()))
            else:
                out.append(''Empty'')
    print(''\\n''.join(out))


if __name__ == ''__main__'':
    main()
', 'python', '栈,队列,数据结构设计', '考研408', 2);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '7\npush 1\npush 2\npop\npush 3\npop\npop\npop', '1\n2\n3\nEmpty\n', 1, 1),
(@aid, '1\npop', 'Empty\n', 0, 2),
(@aid, '2\npush 5\npop', '5\n', 0, 3),
(@aid, '6\npush -1\npush -2\npop\npush 10\npop\npop', '-1\n-2\n10\n', 0, 4),
(@aid, '4\npush 1\npop\npush 2\npop', '1\n2\n', 0, 5);

-- ---------- 循环队列（难度 3，权值 20） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('循环队列', 3, 20, '## 【题目描述】\n\n用一个长度为 MaxSize 的一维数组实现循环队列，支持入队与出队操作。\n\n约定：front 指向队头元素所在位置，rear 指向队尾元素的**下一个**位置，牺牲一个存储单元来区分队空与队满（即队列最多存放 MaxSize - 1 个元素）。\n\n## 【输入格式】\n\n第一行输入两个整数 MaxSize 和 m，用空格分隔（2 <= MaxSize <= 10^5，1 <= m <= 10^5），分别表示数组容量与操作个数。\n接下来 m 行，每行一个操作：\n- `enqueue x`：把整数 x 插入队尾。若队列已满，输出 `Full` 且本次入队失败；\n- `dequeue`：删除队头元素。若队列为空，输出 `Empty`；否则输出出队元素的值。\n\n## 【输出格式】\n\n对上述需要提示的操作各输出一行（`Full` 或 `Empty`），以及每次成功出队的元素值，每个一行。\n\n## 【样例】\n\n输入：\n\n```\n5 8\nenqueue 1\nenqueue 2\nenqueue 3\nenqueue 4\ndequeue\ndequeue\nenqueue 5\nenqueue 6\n```\n\n输出：\n\n```\n1\n2\n```', '第一行两个整数 MaxSize 和 m；接下来 m 行，每行为 "enqueue x" 或 "dequeue"。', '对每次 enqueue，若队满输出 Full；对每次 dequeue，若队空输出 Empty，否则输出出队元素。每个输出占一行。', '5 8\nenqueue 1\nenqueue 2\nenqueue 3\nenqueue 4\ndequeue\ndequeue\nenqueue 5\nenqueue 6', '1\n2\n', '用取模把数组首尾相连成环形：front 指向队头元素，rear 指向队尾的下一个位置，牺牲一个单元区分队空队满——队空 front == rear，队满 (rear + 1) % MaxSize == front，元素个数 (rear - front + MaxSize) % MaxSize，最多存 MaxSize - 1 个元素。每次操作只需一次取模，时间 O(1)，空间 O(MaxSize)。', 'import sys


def main():
    lines = sys.stdin.read().splitlines()
    if not lines:
        return
    first = lines[0].split()
    cap = int(first[0])
    m = int(first[1])
    q = [0] * cap
    front = 0
    rear = 0
    out = []
    for i in range(1, m + 1):
        parts = lines[i].split()
        if not parts:
            continue
        if parts[0] == ''enqueue'':
            x = int(parts[1])
            if (rear + 1) % cap == front:
                out.append(''Full'')
            else:
                q[rear] = x
                rear = (rear + 1) % cap
        else:
            if front == rear:
                out.append(''Empty'')
            else:
                out.append(str(q[front]))
                front = (front + 1) % cap
    print(''\\n''.join(out))


if __name__ == ''__main__'':
    main()
', 'python', '队列,循环队列', '考研408', 3);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '5 8\nenqueue 1\nenqueue 2\nenqueue 3\nenqueue 4\ndequeue\ndequeue\nenqueue 5\nenqueue 6', '1\n2\n', 1, 1),
(@aid, '3 5\nenqueue 1\nenqueue 2\nenqueue 3\ndequeue\ndequeue', 'Full\n1\n2\n', 0, 2),
(@aid, '4 3\ndequeue\nenqueue 9\ndequeue', 'Empty\n9\n', 0, 3),
(@aid, '5 6\nenqueue 1\nenqueue 2\nenqueue 3\nenqueue 4\nenqueue 5\ndequeue', 'Full\n1\n', 0, 4),
(@aid, '4 4\nenqueue -5\nenqueue -6\ndequeue\ndequeue', '-5\n-6\n', 0, 5);

-- ---------- 二叉树的三种遍历（难度 3，权值 20） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('二叉树的三种遍历', 3, 20, '## 【题目描述】\n\n给定一棵二叉树每个结点的编号及其左右孩子编号，请输出它的先序、中序、后序遍历序列。\n\n- 先序：根 → 左子树 → 右子树\n- 中序：左子树 → 根 → 右子树\n- 后序：左子树 → 右子树 → 根\n\n## 【输入格式】\n\n第一行输入两个整数 n 和 root，用空格分隔：n 为结点个数（0 <= n <= 10^4），root 为根结点编号。n = 0 表示空树。\n接下来 n 行，每行三个整数 id、l、r，用空格分隔，表示编号为 id 的结点，其左孩子编号为 l、右孩子编号为 r。其中 0 表示对应的孩子为空。\n\n## 【输出格式】\n\n输出三行：\n第一行为先序遍历序列，第二行为中序遍历序列，第三行为后序遍历序列，编号之间用空格分隔。\n若为空树（n = 0），三行都输出空行。\n\n## 【样例】\n\n输入：\n\n```\n7 1\n1 2 3\n2 4 5\n3 6 7\n4 0 0\n5 0 0\n6 0 0\n7 0 0\n```\n\n输出：\n\n```\n1 2 4 5 3 6 7\n4 2 5 1 6 3 7\n4 5 2 6 7 3 1\n```', '第一行两个整数 n 和 root（n = 0 表示空树）；接下来 n 行，每行三个整数 id、l、r，分别为结点编号及其左右孩子编号（0 表示空）。', '输出三行，依次为先序、中序、后序遍历的结点编号序列，编号间用空格分隔；空树时三行均为空行。', '7 1\n1 2 3\n2 4 5\n3 6 7\n4 0 0\n5 0 0\n6 0 0\n7 0 0', '1 2 4 5 3 6 7\n4 2 5 1 6 3 7\n4 5 2 6 7 3 1\n', '用递归定义直接实现：先序"根左右"（先访问根，再递归左子树、右子树），中序"左根右"，后序"左右根"。三者只有访问根的时机不同，因此可以在一次递归中同时收集三个序列，或写三个独立递归函数。每个结点恰好访问一次，时间复杂度 O(n)，空间复杂度 O(h)（h 为树高，递归栈深度，最坏 O(n)）。用字典存左右孩子即可支持非连续编号；递归深度大时需提高递归上限。', 'import sys

sys.setrecursionlimit(1000000)


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    root = int(data[1])
    left = {}
    right = {}
    idx = 2
    for _ in range(n):
        v = int(data[idx])
        l = int(data[idx + 1])
        r = int(data[idx + 2])
        idx += 3
        left[v] = l
        right[v] = r
    pre = []
    ino = []
    post = []

    def dfs(v):
        if v == 0:
            return
        pre.append(v)
        dfs(left.get(v, 0))
        ino.append(v)
        dfs(right.get(v, 0))
        post.append(v)

    dfs(root)
    print('' ''.join(map(str, pre)))
    print('' ''.join(map(str, ino)))
    print('' ''.join(map(str, post)))


if __name__ == ''__main__'':
    main()
', 'python', '二叉树,递归,遍历', '考研408', 4);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '7 1\n1 2 3\n2 4 5\n3 6 7\n4 0 0\n5 0 0\n6 0 0\n7 0 0', '1 2 4 5 3 6 7\n4 2 5 1 6 3 7\n4 5 2 6 7 3 1\n', 1, 1),
(@aid, '1 1\n1 0 0', '1\n1\n1\n', 0, 2),
(@aid, '0 0', '\n\n\n', 0, 3),
(@aid, '4 1\n1 2 0\n2 3 0\n3 4 0\n4 0 0', '1 2 3 4\n4 3 2 1\n4 3 2 1\n', 0, 4),
(@aid, '5 3\n1 0 2\n2 0 0\n3 1 4\n4 0 5\n5 0 0', '3 1 2 4 5\n1 2 3 4 5\n2 1 5 4 3\n', 0, 5);

-- ---------- 二叉树的最大深度（难度 2，权值 10） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('二叉树的最大深度', 2, 10, '## 【题目描述】\n\n给定一棵二叉树，求它的最大深度（即从根结点到最远叶子结点的最长路径上的结点数）。\n\n约定：空树的深度为 0，只有根结点的树深度为 1。\n\n## 【输入格式】\n\n第一行输入两个整数 n 和 root，用空格分隔：n 为结点个数（0 <= n <= 10^4），root 为根结点编号。n = 0 表示空树。\n接下来 n 行，每行三个整数 id、l、r，用空格分隔，表示编号为 id 的结点，其左孩子编号为 l、右孩子编号为 r，0 表示对应孩子为空。\n\n## 【输出格式】\n\n输出一个整数，表示二叉树的最大深度。\n\n## 【样例】\n\n输入：\n\n```\n7 1\n1 2 3\n2 4 5\n3 6 7\n4 0 0\n5 0 0\n6 0 0\n7 0 0\n```\n\n输出：\n\n```\n3\n```', '第一行两个整数 n 和 root（n = 0 表示空树）；接下来 n 行，每行三个整数 id、l、r。', '输出一个整数，即二叉树的最大深度（层数）；空树的深度为 0。', '7 1\n1 2 3\n2 4 5\n3 6 7\n4 0 0\n5 0 0\n6 0 0\n7 0 0', '3\n', '递归求高度：若结点为空则深度为 0，否则其深度 = 1 + max(左子树深度, 右子树深度)。这是二叉树的递归定义直接翻译，每个结点访问一次，时间复杂度 O(n)，空间复杂度 O(h)（递归栈深度，h 为树高）。也可以用层序遍历（BFS）按层计数求解，空间 O(n)。注意空树高度为 0 而不是 1，只有根结点的树高度为 1。', 'import sys

sys.setrecursionlimit(1000000)


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    root = int(data[1])
    left = {}
    right = {}
    idx = 2
    for _ in range(n):
        v = int(data[idx])
        left[v] = int(data[idx + 1])
        right[v] = int(data[idx + 2])
        idx += 3

    def depth(v):
        if v == 0:
            return 0
        ld = depth(left.get(v, 0))
        rd = depth(right.get(v, 0))
        return 1 + (ld if ld > rd else rd)

    print(depth(root))


if __name__ == ''__main__'':
    main()
', 'python', '二叉树,递归,DFS', '期末', 4);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '7 1\n1 2 3\n2 4 5\n3 6 7\n4 0 0\n5 0 0\n6 0 0\n7 0 0', '3\n', 1, 1),
(@aid, '1 1\n1 0 0', '1\n', 0, 2),
(@aid, '0 0', '0\n', 0, 3),
(@aid, '4 1\n1 2 0\n2 3 0\n3 4 0\n4 0 0', '4\n', 0, 4),
(@aid, '5 3\n1 0 2\n2 0 0\n3 1 4\n4 0 5\n5 0 0', '3\n', 0, 5);

-- ---------- 二叉树的最近公共祖先（难度 4，权值 30） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('二叉树的最近公共祖先', 4, 30, '## 【题目描述】\n\n给定一棵二叉树和两个结点编号 u、v，请找出它们的最近公共祖先（LCA）——即同时是 u 和 v 的祖先、且深度最大的那个结点。\n\n结点自身也视为它自己的祖先。\n\n## 【输入格式】\n\n第一行输入两个整数 n 和 root，用空格分隔（1 <= n <= 10^4）。\n接下来 n 行，每行三个整数 id、l、r，用空格分隔，表示编号为 id 的结点，其左孩子编号为 l、右孩子编号为 r，0 表示对应孩子为空。\n最后一行输入两个整数 u、v，用空格分隔，表示待查询的两个结点编号。\n\n## 【输出格式】\n\n输出一个整数：u 与 v 的最近公共祖先编号。若 u 或 v 不是树中的结点，输出 -1。\n\n## 【样例】\n\n输入：\n\n```\n7 1\n1 2 3\n2 4 5\n3 6 7\n4 0 0\n5 0 0\n6 0 0\n7 0 0\n4 5\n```\n\n输出：\n\n```\n2\n```', '第一行两个整数 n 和 root；接下来 n 行每行三个整数 id、l、r；最后一行两个整数 u 和 v。', '输出一个整数，即 u 与 v 的最近公共祖先编号；若 u 或 v 不在树中，输出 -1。', '7 1\n1 2 3\n2 4 5\n3 6 7\n4 0 0\n5 0 0\n6 0 0\n7 0 0\n4 5', '2\n', '后序遍历思想：从根开始递归查找，若当前结点就是 u 或 v 则直接返回它；否则分别在左、右子树中查找，若左右两边都找到了非空结果，说明 u、v 分居当前结点两侧，当前结点即最近公共祖先；若只有一侧非空，则把该侧结果向上传递。整棵树最多遍历一次，时间复杂度 O(n)，空间复杂度 O(h)（递归栈）。查找前先判断 u、v 是否都是树中结点，避免把不存在的结点当成有效结果。', 'import sys

sys.setrecursionlimit(1000000)


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    root = int(data[1])
    left = {}
    right = {}
    idx = 2
    nodes = set()
    for _ in range(n):
        v = int(data[idx])
        l = int(data[idx + 1])
        r = int(data[idx + 2])
        idx += 3
        left[v] = l
        right[v] = r
        nodes.add(v)
    u = int(data[idx])
    v = int(data[idx + 1])
    if u not in nodes or v not in nodes:
        print(-1)
        return

    def lca(x):
        if x == 0:
            return 0
        if x == u or x == v:
            return x
        a = lca(left.get(x, 0))
        b = lca(right.get(x, 0))
        if a and b:
            return x
        return a or b

    print(lca(root))


if __name__ == ''__main__'':
    main()
', 'python', '二叉树,递归,LCA', '考研408', 4);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '7 1\n1 2 3\n2 4 5\n3 6 7\n4 0 0\n5 0 0\n6 0 0\n7 0 0\n4 5', '2\n', 1, 1),
(@aid, '7 1\n1 2 3\n2 4 5\n3 6 7\n4 0 0\n5 0 0\n6 0 0\n7 0 0\n4 6', '1\n', 0, 2),
(@aid, '7 1\n1 2 3\n2 4 5\n3 6 7\n4 0 0\n5 0 0\n6 0 0\n7 0 0\n4 4', '4\n', 0, 3),
(@aid, '7 1\n1 2 3\n2 4 5\n3 6 7\n4 0 0\n5 0 0\n6 0 0\n7 0 0\n1 7', '1\n', 0, 4),
(@aid, '7 1\n1 2 3\n2 4 5\n3 6 7\n4 0 0\n5 0 0\n6 0 0\n7 0 0\n4 99', '-1\n', 0, 5),
(@aid, '4 1\n1 2 0\n2 3 0\n3 4 0\n4 0 0\n3 4', '3\n', 0, 6);

-- ---------- 拓扑排序（难度 4，权值 30） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('拓扑排序', 4, 30, '## 【题目描述】\n\n给定一个有向图（AOV 网），求它的一个拓扑序列。\n\n若图中存在环，则不存在拓扑序列，需要报告有环。为答案唯一，约定：**每一步总是在当前所有入度为 0 的顶点中取编号最小的那个**输出。\n\n## 【输入格式】\n\n第一行输入两个整数 n 和 m，用空格分隔（1 <= n, m <= 10^5），分别表示顶点数与有向边数，顶点编号为 1 ~ n。\n接下来 m 行，每行两个整数 u、v，表示一条从 u 指向 v 的有向边。\n\n## 【输出格式】\n\n若可以拓扑排序，输出一行，为拓扑序列的顶点编号，用空格分隔。\n若图中存在环，输出一行 `Cycle`。\n\n## 【样例】\n\n输入：\n\n```\n6 6\n1 2\n1 3\n2 4\n3 4\n3 5\n4 6\n```\n\n输出：\n\n```\n1 2 3 4 5 6\n```', '第一行两个整数 n 和 m（顶点编号 1~n）；接下来 m 行每行两个整数 u、v，表示有向边 u → v。', '输出一行拓扑序列，顶点编号用空格分隔；若图中存在环（无法拓扑排序），输出 Cycle。', '6 6\n1 2\n1 3\n2 4\n3 4\n3 5\n4 6', '1 2 3 4 5 6\n', 'Kahn 算法：先统计每个顶点的入度，把所有入度为 0 的顶点入队（本题用小根堆保证每次取编号最小的顶点，从而序列唯一）；每次取出一个顶点输出，并删除它的所有出边（把后继入度减 1），入度变为 0 的后继入队。若最终输出的顶点数少于 n，说明图中存在环，输出 Cycle。每条边、每个顶点各处理一次，时间复杂度 O(n + m)，空间复杂度 O(n + m)。', 'import sys
import heapq


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    m = int(data[1])
    g = [[] for _ in range(n + 1)]
    indeg = [0] * (n + 1)
    idx = 2
    for _ in range(m):
        u = int(data[idx])
        v = int(data[idx + 1])
        idx += 2
        g[u].append(v)
        indeg[v] += 1
    heap = [i for i in range(1, n + 1) if indeg[i] == 0]
    heapq.heapify(heap)
    res = []
    while heap:
        u = heapq.heappop(heap)
        res.append(u)
        for v in g[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                heapq.heappush(heap, v)
    if len(res) != n:
        print(''Cycle'')
    else:
        print('' ''.join(map(str, res)))


if __name__ == ''__main__'':
    main()
', 'python', '图,拓扑排序,AOV网', '考研408', 39);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '6 6\n1 2\n1 3\n2 4\n3 4\n3 5\n4 6', '1 2 3 4 5 6\n', 1, 1),
(@aid, '3 3\n1 2\n2 3\n3 1', 'Cycle\n', 0, 2),
(@aid, '1 0', '1\n', 0, 3),
(@aid, '4 1\n2 3', '1 2 3 4\n', 0, 4),
(@aid, '5 4\n1 3\n2 3\n3 4\n3 5', '1 2 3 4 5\n', 0, 5);

-- ---------- Dijkstra 最短路径（难度 5，权值 50） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('Dijkstra 最短路径', 5, 50, '## 【题目描述】\n\n给定一个带非负权无向图和源点 s，请用 Dijkstra 算法求源点到所有顶点的最短距离。\n\n## 【输入格式】\n\n第一行输入三个整数 n、m、s，用空格分隔（1 <= n <= 10^4，0 <= m <= 10^5），分别表示顶点数、边数与源点编号，顶点编号为 1 ~ n。\n接下来 m 行，每行三个整数 u、v、w，用空格分隔，表示顶点 u 与 v 之间有一条权值为 w 的无向边（0 <= w <= 10^9）。\n\n## 【输出格式】\n\n输出一行，包含 n 个整数，用空格分隔：第 i 个数为源点 s 到顶点 i 的最短距离；若不可达，该位置输出 -1。源点到自身的距离为 0。\n\n## 【样例】\n\n输入：\n\n```\n6 9 1\n1 2 6\n1 3 3\n2 3 2\n2 4 5\n3 4 3\n3 5 4\n4 5 2\n4 6 3\n5 6 5\n```\n\n输出：\n\n```\n0 5 3 6 7 9\n```', '第一行三个整数 n、m、s；接下来 m 行每行三个整数 u、v、w，表示 u 与 v 之间有一条权值为 w 的无向边。', '输出一行 n 个整数，依次为源点 s 到顶点 1~n 的最短距离，不可达输出 -1。', '6 9 1\n1 2 6\n1 3 3\n2 3 2\n2 4 5\n3 4 3\n3 5 4\n4 5 2\n4 6 3\n5 6 5', '0 5 3 6 7 9\n', '贪心 + 松弛：dist[s] = 0、其余为无穷，用小根堆每次取出距离最小的未确定顶点 u，对它的每条边尝试松弛，若 dist[u] + w < dist[v] 则更新并入堆；顶点首次出堆时距离即最终值（依赖边权非负）。堆优化复杂度 O(m log n)，空间 O(n + m)；不可达输出 -1，有负权边应改用 Bellman-Ford。', 'import sys
import heapq


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    m = int(data[1])
    s = int(data[2])
    g = [[] for _ in range(n + 1)]
    idx = 3
    for _ in range(m):
        u = int(data[idx])
        v = int(data[idx + 1])
        w = int(data[idx + 2])
        idx += 3
        g[u].append((v, w))
        g[v].append((u, w))
    INF = float(''inf'')
    dist = [INF] * (n + 1)
    dist[s] = 0
    pq = [(0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in g[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    out = []
    for i in range(1, n + 1):
        if dist[i] == INF:
            out.append(''-1'')
        else:
            out.append(str(dist[i]))
    print('' ''.join(out))


if __name__ == ''__main__'':
    main()
', 'python', '图,最短路,贪心,Dijkstra', '考研408', 38);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '6 9 1\n1 2 6\n1 3 3\n2 3 2\n2 4 5\n3 4 3\n3 5 4\n4 5 2\n4 6 3\n5 6 5', '0 5 3 6 7 9\n', 1, 1),
(@aid, '3 1 1\n1 2 5', '0 5 -1\n', 0, 2),
(@aid, '1 0 1', '0\n', 0, 3),
(@aid, '4 3 1\n1 2 1000000000\n2 3 1000000000\n3 4 1000000000', '0 1000000000 2000000000 3000000000\n', 0, 4),
(@aid, '5 5 2\n1 2 7\n2 3 2\n3 4 1\n4 5 3\n1 5 20', '7 0 2 3 6\n', 0, 5);

-- ---------- 01 背包（难度 4，权值 30） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('01 背包', 4, 30, '## 【题目描述】\n\n有 n 个物品和一个容量为 V 的背包。第 i 个物品的重量为 w_i、价值为 v_i，每个物品只能取一次（0-1 背包）。求在不超过背包容量的前提下能取得的 maximum 总价值。\n\n## 【输入格式】\n\n第一行输入两个整数 n 和 V，用空格分隔（0 <= n <= 10^3，0 <= V <= 10^3），分别表示物品数与背包容量。\n接下来 n 行，每行两个整数 w、v，用空格分隔（0 < w <= 10^3，0 <= v <= 10^3），分别为该物品的重量与价值。\n\n## 【输出格式】\n\n输出一个整数，表示能取得的最大总价值。\n\n## 【样例】\n\n输入：\n\n```\n3 5\n2 3\n3 4\n4 5\n```\n\n输出：\n\n```\n7\n```\n\n（选择第 1、2 个物品，总重 5，总价值 7。）', '第一行两个整数 n 和 V；接下来 n 行每行两个整数 w 和 v，分别为物品重量与价值。', '输出一个整数，即不超过背包容量的最大总价值。', '3 5\n2 3\n3 4\n4 5', '7\n', '动态规划：设 dp[c] 表示容量不超过 c 时能取得的最大价值。对每个物品 (w, v)，让容量 c 从 V 倒序枚举到 w，做转移 dp[c] = max(dp[c], dp[c - w] + v)。倒序枚举可以保证每个物品只被放入一次（若正序枚举就变成完全背包）。时间复杂度 O(nV)，空间复杂度 O(V)（一维滚动数组优化）。答案是整个 dp 数组的最大值。', 'import sys


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    cap = int(data[1])
    dp = [0] * (cap + 1)
    idx = 2
    for _ in range(n):
        w = int(data[idx])
        v = int(data[idx + 1])
        idx += 2
        if w <= cap:
            for c in range(cap, w - 1, -1):
                t = dp[c - w] + v
                if t > dp[c]:
                    dp[c] = t
    print(max(dp))


if __name__ == ''__main__'':
    main()
', 'python', '动态规划,背包', '软考', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3 5\n2 3\n3 4\n4 5', '7\n', 1, 1),
(@aid, '0 10', '0\n', 0, 2),
(@aid, '3 0\n1 5\n2 6\n3 7', '0\n', 0, 3),
(@aid, '4 10\n2 3\n3 4\n4 5\n5 6', '13\n', 0, 4),
(@aid, '2 100\n50 100\n51 101', '101\n', 0, 5);

-- ---------- 最长上升子序列 LIS（难度 3，权值 20） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('最长上升子序列 LIS', 3, 20, '## 【题目描述】\n\n给定一个长度为 n 的整数序列，求它的最长严格上升子序列（LIS）的长度。\n\n子序列不要求连续，但必须保持原有顺序，且后一个元素严格大于前一个。\n\n## 【输入格式】\n\n第一行输入整数 n（0 <= n <= 10^5）。\n第二行输入 n 个整数，用空格分隔，取值范围 -10^9 ~ 10^9。\nn = 0 时没有第二行数据。\n\n## 【输出格式】\n\n输出一个整数，表示最长严格上升子序列的长度。\n\n## 【样例】\n\n输入：\n\n```\n8\n10 9 2 5 3 7 101 18\n```\n\n输出：\n\n```\n4\n```\n\n（一个 LIS 为 2, 3, 7, 101。）', '第一行一个整数 n（0 <= n <= 10^5）；第二行 n 个用空格分隔的整数。', '输出一个整数，即最长严格上升子序列的长度。', '8\n10 9 2 5 3 7 101 18', '4\n', '用 tails 数组 + 二分：tails[k] 表示长度为 k+1 的上升子序列的最小结尾元素，它单调递增；对每个 x 二分找到第一个 >= x 的位置替换，找不到则追加，最后 tails 的长度即答案。严格上升用 bisect_left，非降用 bisect_right。时间复杂度 O(n log n)，空间 O(n)。', 'import sys
import bisect


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    a = list(map(int, data[1:1 + n]))
    tails = []
    for x in a:
        i = bisect.bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    print(len(tails))


if __name__ == ''__main__'':
    main()
', 'python', '动态规划,二分,子序列', '期末', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '8\n10 9 2 5 3 7 101 18', '4\n', 1, 1),
(@aid, '6\n0 1 0 3 2 3', '4\n', 0, 2),
(@aid, '4\n7 7 7 7', '1\n', 0, 3),
(@aid, '0', '0\n', 0, 4),
(@aid, '1\n5', '1\n', 0, 5),
(@aid, '5\n-3 -2 -1 0 1', '5\n', 0, 6);

-- ---------- 最长公共子序列 LCS（难度 4，权值 30） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('最长公共子序列 LCS', 4, 30, '## 【题目描述】\n\n给定两个字符串 a 和 b，求它们的最长公共子序列（LCS）的长度。\n\n子序列是指从原串中删去若干字符（也可以不删）后剩下的字符按原顺序组成的串，不要求连续。\n\n## 【输入格式】\n\n两行输入，每行为一个字符串，长度不超过 10^3，由大小写字母组成且不含空格。\n\n## 【输出格式】\n\n输出一个整数，表示最长公共子序列的长度。若没有公共子序列，输出 0。\n\n## 【样例】\n\n输入：\n\n```\nabcde\nace\n```\n\n输出：\n\n```\n3\n```', '两行输入，每行为一个不含空格的字符串（长度不超过 10^3）。', '输出一个整数，即两个字符串的最长公共子序列长度。', 'abcde\nace', '3\n', '二维 DP：dp[i][j] 表示 a 前 i 个字符与 b 前 j 个字符的 LCS 长度。若 a[i-1] == b[j-1]，则 dp[i][j] = dp[i-1][j-1] + 1；否则取 max(dp[i-1][j], dp[i][j-1])。每行只依赖上一行，可用滚动数组把空间压到 O(m)。时间复杂度 O(nm)，空间 O(m)。', 'import sys


def main():
    lines = sys.stdin.read().splitlines()
    if not lines:
        a = ''''
        b = ''''
    elif len(lines) < 2:
        a = lines[0]
        b = ''''
    else:
        a = lines[0]
        b = lines[1]
    n = len(a)
    m = len(b)
    prev = [0] * (m + 1)
    for i in range(1, n + 1):
        cur = [0] * (m + 1)
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1] + 1
            else:
                x = prev[j]
                y = cur[j - 1]
                cur[j] = x if x >= y else y
        prev = cur
    print(prev[m])


if __name__ == ''__main__'':
    main()
', 'python', '动态规划,字符串', '考研408', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'abcde\nace', '3\n', 1, 1),
(@aid, 'abc\nabc', '3\n', 0, 2),
(@aid, 'abc\ndef', '0\n', 0, 3),
(@aid, 'abcbdab\nbdcaba', '4\n', 0, 4),
(@aid, 'a\na', '1\n', 0, 5),
(@aid, 'ab\nbc', '1\n', 0, 6);

-- ---------- 爬楼梯（难度 2，权值 10） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('爬楼梯', 2, 10, '## 【题目描述】\n\n一个楼梯共有 n 阶，每次你可以跨 1 阶或 2 阶。问有多少种不同的方法可以爬到楼顶。\n\n## 【输入格式】\n\n第一行输入整数 T，表示询问个数（1 <= T <= 100）。\n接下来 T 行，每行一个整数 n（1 <= n <= 60）。\n\n## 【输出格式】\n\n对每个 n 输出一行，表示到达第 n 阶的方法总数（结果在 64 位整数范围内）。\n\n## 【样例】\n\n输入：\n\n```\n3\n1\n2\n5\n```\n\n输出：\n\n```\n1\n2\n8\n```', '第一行一个整数 T（1 <= T <= 100）；接下来 T 行每行一个整数 n（1 <= n <= 60）。', '对每个 n 输出一行，即到达第 n 阶楼梯的方法总数。', '3\n1\n2\n5', '1\n2\n8\n', '递推（斐波那契）：到第 n 阶的最后一步要么从 n-1 阶跨 1 阶、要么从 n-2 阶跨 2 阶，故 f(n) = f(n-1) + f(n-2)，边界 f(1) = 1、f(2) = 2。预处理到最大询问值后每次查询 O(1)，总时间 O(n)，空间 O(1)。不要写成指数级的朴素递归。', 'import sys


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    t = int(data[0])
    qs = [int(x) for x in data[1:1 + t]]
    mx = max(qs) if qs else 0
    f = [0] * (mx + 2)
    if mx >= 1:
        f[1] = 1
    if mx >= 2:
        f[2] = 2
    for i in range(3, mx + 1):
        f[i] = f[i - 1] + f[i - 2]
    out = []
    for n in qs:
        out.append(str(f[n]))
    print(''\\n''.join(out))


if __name__ == ''__main__'':
    main()
', 'python', '动态规划,递推', '基础', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3\n1\n2\n5', '1\n2\n8\n', 1, 1),
(@aid, '1\n10', '89\n', 0, 2),
(@aid, '1\n30', '1346269\n', 0, 3),
(@aid, '2\n3\n4', '3\n5\n', 0, 4),
(@aid, '1\n60', '2504730781961\n', 0, 5);

-- ---------- 编辑距离（难度 5，权值 50） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('编辑距离', 5, 50, '## 【题目描述】\n\n给定两个字符串 a 和 b，允许三种操作：插入一个字符、删除一个字符、替换一个字符（每次操作代价均为 1）。求把 a 变成 b 的最少操作次数，即编辑距离（Levenshtein Distance）。\n\n## 【输入格式】\n\n两行输入，每行为一个字符串，长度不超过 10^3，由大小写字母组成且不含空格。\n\n## 【输出格式】\n\n输出一个整数，表示最少操作次数。若两串相等，输出 0。\n\n## 【样例】\n\n输入：\n\n```\nhorse\nros\n```\n\n输出：\n\n```\n3\n```\n\n（horse → rorse 替换 h 为 r；→ rose 删除 r；→ ros 删除 e，共 3 步。）', '两行输入，每行为一个不含空格的字符串（长度不超过 10^3）。', '输出一个整数，即把第一个字符串变成第二个字符串的最少操作次数。', 'horse\nros', '3\n', '二维 DP：dp[i][j] 表示 a 前 i 个字符变成 b 前 j 个字符的最少操作数。字符相等时 dp[i][j] = dp[i-1][j-1]；否则在删除 dp[i-1][j]、插入 dp[i][j-1]、替换 dp[i-1][j-1] 三者取最小后加 1。初始化 dp[0][j] = j、dp[i][0] = i。用滚动数组优化后时间 O(nm)、空间 O(m)。', 'import sys


def main():
    lines = sys.stdin.read().splitlines()
    if not lines:
        a = ''''
        b = ''''
    elif len(lines) < 2:
        a = lines[0]
        b = ''''
    else:
        a = lines[0]
        b = lines[1]
    n = len(a)
    m = len(b)
    prev = list(range(m + 1))
    for i in range(1, n + 1):
        cur = [i] + [0] * m
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1]
            else:
                x = prev[j]
                y = cur[j - 1]
                z = prev[j - 1]
                t = x if x < y else y
                if z < t:
                    t = z
                cur[j] = 1 + t
        prev = cur
    print(prev[m])


if __name__ == ''__main__'':
    main()
', 'python', '动态规划,字符串', '考研408', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'horse\nros', '3\n', 1, 1),
(@aid, 'intention\nexecution', '5\n', 0, 2),
(@aid, 'abc\nabc', '0\n', 0, 3),
(@aid, 'sea\neat', '2\n', 0, 4),
(@aid, 'a\nb', '1\n', 0, 5),
(@aid, 'flaw\nlawn', '2\n', 0, 6);

-- ---------- 活动选择（难度 3，权值 20） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('活动选择', 3, 20, '## 【题目描述】\n\n有 n 个活动，第 i 个活动在时间区间 [s_i, e_i) 内进行（即占用时间从 s_i 开始、到 e_i 前结束）。同一时间只能参加一个活动，两个活动 compatible 的条件是前一个的结束时间不大于后一个的开始时间。\n\n请用贪心算法求出最多能安排多少个互不重叠的活动。\n\n## 【输入格式】\n\n第一行输入整数 n，表示活动个数（0 <= n <= 10^5）。\n接下来 n 行，每行两个整数 s、e，用空格分隔（0 <= s < e <= 10^9），表示活动的开始与结束时间。\n\n## 【输出格式】\n\n输出一个整数，表示最多能安排的活动个数。\n\n## 【样例】\n\n输入：\n\n```\n11\n1 4\n3 5\n0 6\n5 7\n3 9\n5 9\n6 10\n8 11\n8 12\n2 14\n12 16\n```\n\n输出：\n\n```\n4\n```\n\n（可安排 (1,4)、(5,7)、(8,11)、(12,16) 共 4 个。）', '第一行一个整数 n（0 <= n <= 10^5）；接下来 n 行每行两个整数 s 和 e，表示活动的开始与结束时间（区间 [s, e)）。', '输出一个整数，即最多能安排的互不重叠的活动个数。', '11\n1 4\n3 5\n0 6\n5 7\n3 9\n5 9\n6 10\n8 11\n8 12\n2 14\n12 16', '4\n', '区间调度的经典贪心：按结束时间从小到大排序，每次选择"结束最早且与已选活动不冲突"的活动（即其开始时间 >= 上一个已选活动的结束时间）。直觉是尽早结束能留给后续活动最多的空间，可用交换论证证明其最优性。排序 O(n log n)、扫描 O(n)，总时间复杂度 O(n log n)，空间 O(n)。注意按结束时间排序才是正确的贪心策略，按开始时间或按活动时长排序都会得到错误答案。', 'import sys


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    acts = []
    idx = 1
    for _ in range(n):
        s = int(data[idx])
        e = int(data[idx + 1])
        idx += 2
        acts.append((e, s))
    acts.sort()
    cnt = 0
    last_end = None
    for e, s in acts:
        if last_end is None or s >= last_end:
            cnt += 1
            last_end = e
    print(cnt)


if __name__ == ''__main__'':
    main()
', 'python', '贪心,区间调度', '期末', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '11\n1 4\n3 5\n0 6\n5 7\n3 9\n5 9\n6 10\n8 11\n8 12\n2 14\n12 16', '4\n', 1, 1),
(@aid, '0', '0\n', 0, 2),
(@aid, '1\n1 3', '1\n', 0, 3),
(@aid, '3\n1 2\n2 3\n3 4', '3\n', 0, 4),
(@aid, '4\n1 5\n1 5\n1 5\n1 5', '1\n', 0, 5);

-- ---------- BFS 迷宫最短路（难度 4，权值 30） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('BFS 迷宫最短路', 4, 30, '## 【题目描述】\n\n给定一个 n 行 m 列的迷宫，`#` 表示墙壁不可通行，`.` 表示空地可以通行。每次只能向上、下、左、右移动一格（不能走出边界）。\n\n请用广度优先搜索求从起点 (sr, sc) 到终点 (tr, tc) 的最少步数；若无法到达，输出 -1。\n\n## 【输入格式】\n\n第一行输入两个整数 n 和 m，用空格分隔（1 <= n, m <= 500），表示迷宫的行数与列数。\n接下来 n 行，每行一个长度为 m 的字符串，只包含字符 `.` 与 `#`。\n最后一行输入四个整数 sr、sc、tr、tc，用空格分隔（下标均从 0 开始），分别表示起点行列与终点行列。\n\n## 【输出格式】\n\n输出一个整数：最短步数；若不可达输出 -1。起点与终点重合时输出 0。\n\n## 【样例】\n\n输入：\n\n```\n3 3\n...\n.#.\n...\n0 0 2 2\n```\n\n输出：\n\n```\n4\n```', '第一行两个整数 n 和 m；接下来 n 行每行一个长度 m 的字符串（. 可通行，# 为墙）；最后一行四个整数 sr sc tr tc。', '输出一个整数，即从起点到终点的最短步数；若不可达输出 -1。起点与终点重合时输出 0。', '3 3\n...\n.#.\n...\n0 0 2 2', '4\n', '在边权均为 1 的网格图上，BFS 的层序扩展天然保证第一次到达终点的距离就是最短距离。用队列存坐标，用 dist 数组同时充当 visited 标记（初始 -1，入队时写入步数），从起点向四个方向扩展合法且未访问过的格子。每个格子最多入队一次，时间复杂度 O(nm)，空间复杂度 O(nm)。注意起点即终点要特判为 0，且起点若被墙包围则输出 -1。', 'import sys
from collections import deque


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    m = int(data[1])
    grid = []
    idx = 2
    for _ in range(n):
        grid.append(data[idx])
        idx += 1
    sr = int(data[idx])
    sc = int(data[idx + 1])
    tr = int(data[idx + 2])
    tc = int(data[idx + 3])
    if sr == tr and sc == tc:
        print(0)
        return
    dist = [[-1] * m for _ in range(n)]
    dist[sr][sc] = 0
    q = deque()
    q.append((sr, sc))
    ans = -1
    while q:
        r, c = q.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr = r + dr
            nc = c + dc
            if 0 <= nr < n and 0 <= nc < m and grid[nr][nc] != ''#'' and dist[nr][nc] == -1:
                dist[nr][nc] = dist[r][c] + 1
                if nr == tr and nc == tc:
                    ans = dist[nr][nc]
                    break
                q.append((nr, nc))
        if ans != -1:
            break
    print(ans)


if __name__ == ''__main__'':
    main()
', 'python', '图,BFS,最短路', '期末', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3 3\n...\n.#.\n...\n0 0 2 2', '4\n', 1, 1),
(@aid, '1 1\n.\n0 0 0 0', '0\n', 0, 2),
(@aid, '2 2\n.#\n#.\n0 0 1 1', '-1\n', 0, 3),
(@aid, '3 4\n....\n.##.\n....\n0 0 2 3', '5\n', 0, 4),
(@aid, '2 3\n...\n...\n1 2 0 0', '3\n', 0, 5);

-- ---------- DFS 全排列（难度 3，权值 20） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('DFS 全排列', 3, 20, '## 【题目描述】\n\n给定一个正整数 n，请按字典序输出 1 ~ n 的所有全排列。\n\n要求使用深度优先搜索 + 回溯实现，而不是调用语言内置的全排列函数。\n\n## 【输入格式】\n\n输入一行一个整数 n（0 <= n <= 8）。\n\n## 【输出格式】\n\n按字典序输出所有排列，每行一个排列，同一行内的数字用空格分隔。\n若 n = 0，不输出任何内容。\n\n## 【样例】\n\n输入：\n\n```\n3\n```\n\n输出：\n\n```\n1 2 3\n1 3 2\n2 1 3\n2 3 1\n3 1 2\n3 2 1\n```', '输入一行一个整数 n（0 <= n <= 8）。', '按字典序输出 1~n 的所有全排列，每行一个排列，数字间用空格分隔；n = 0 时不输出任何内容。', '3', '1 2 3\n1 3 2\n2 1 3\n2 3 1\n3 1 2\n3 2 1\n', '回溯（DFS）：维护 path 与 used 数组，第 depth 层从小到大枚举未使用的数字，放入 path、标记 used 后递归下一层，返回时撤销标记；depth == n 时输出一个排列。因每层从小到大枚举，天然得到字典序。共 n! 个排列，时间 O(n * n!)，空间 O(n)。', 'import sys


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    if n <= 0:
        return
    path = []
    used = [False] * (n + 1)
    out = []

    def dfs(depth):
        if depth == n:
            out.append('' ''.join(map(str, path)))
            return
        for i in range(1, n + 1):
            if not used[i]:
                used[i] = True
                path.append(i)
                dfs(depth + 1)
                path.pop()
                used[i] = False

    dfs(0)
    print(''\\n''.join(out))


if __name__ == ''__main__'':
    main()
', 'python', '搜索,DFS,回溯,全排列', 'NCRE', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3', '1 2 3\n1 3 2\n2 1 3\n2 3 1\n3 1 2\n3 2 1\n', 1, 1),
(@aid, '1', '1\n', 0, 2),
(@aid, '2', '1 2\n2 1\n', 0, 3),
(@aid, '4', '1 2 3 4\n1 2 4 3\n1 3 2 4\n1 3 4 2\n1 4 2 3\n1 4 3 2\n2 1 3 4\n2 1 4 3\n2 3 1 4\n2 3 4 1\n2 4 1 3\n2 4 3 1\n3 1 2 4\n3 1 4 2\n3 2 1 4\n3 2 4 1\n3 4 1 2\n3 4 2 1\n4 1 2 3\n4 1 3 2\n4 2 1 3\n4 2 3 1\n4 3 1 2\n4 3 2 1\n', 0, 4),
(@aid, '0', '', 0, 5);
