# -*- coding: utf-8 -*-
"""第五批：字符串处理（20 道）"""
import random
import string

from common import P

_WORDS = ['hello', 'world', 'cpp', 'python', 'data', 'struct', 'algorithm', 'code',
          'test', 'luogu', 'acm', 'sun', 'moon', 'tree', 'node', 'graph', 'array']


def _gen_words(r, n=None):
    n = n or r.randint(1, 8)
    return ' '.join(r.choice(_WORDS) for _ in range(n))


def _gen_anagram(r):
    a = list(''.join(r.choice('abcdef') for _ in range(r.randint(1, 10))))
    if r.random() < 0.5:
        b = list(a)
        r.shuffle(b)
        b = ''.join(b)
    else:
        b = ''.join(r.choice('abcdef') for _ in range(len(a)))
    return '%s\n%s' % (''.join(a), b)


PROBLEMS = [
    P('字符串反转（切片与双指针）', 1,
      '输入一个字符串（不含空格），将其反转后输出。',
      '一行，一个字符串 s。',
      '一行，反转后的字符串。',
      'abcdef', 'fedcba',
      '''import sys

s = sys.stdin.readline().rstrip('\\n')
print(s[::-1])
''',
      lambda r: ''.join(r.choice(string.ascii_lowercase) for _ in range(r.randint(1, 20))),
      hint='Python 中 s[::-1] 即逆序切片；也可双指针首尾交换，原地反转。',
      scope='1 ≤ |s| ≤ 100，仅含小写字母', tags='字符串,基础', kid=8),

    P('统计字符出现次数', 1,
      '给定一个字符串和一个字符，统计该字符在字符串中出现的次数。',
      '两行。第一行一个字符串 s；第二行一个字符 c。',
      '一行，一个整数，表示出现次数。',
      'hello world\nl', '3',
      '''import sys

lines = sys.stdin.read().split('\\n')
s = lines[0]
c = lines[1].strip()
print(s.count(c))
''',
      lambda r: (lambda s: '%s\n%s' % (s, r.choice(s)))(_gen_words(r, r.randint(2, 8))),
      hint='遍历计数或用内置 count；注意第二行可能读到空串，需要 strip。',
      scope='1 ≤ |s| ≤ 1000，c 为单个可见字符', tags='字符串,计数', kid=8),

    P('判断回文串', 1,
      '给定一个字符串（只含大小写字母），判断它是否是回文串（正读反读相同，区分大小写）。',
      '一行，一个字符串 s。',
      '一行，是回文输出 Yes，否则输出 No。',
      'level', 'Yes',
      '''import sys

s = sys.stdin.readline().strip()
print('Yes' if s == s[::-1] else 'No')
''',
      lambda r: (lambda t: t if r.random() < 0.5 else t + t[::-1])(
          ''.join(r.choice(string.ascii_lowercase) for _ in range(r.randint(1, 10)))),
      hint='回文的本质是与自身的逆序相等；用双指针从两端向中间比较可以省去额外空间。',
      scope='1 ≤ |s| ≤ 1000', tags='字符串,回文', kid=8),

    P('字符串中的数字求和', 1,
      '给定一个字符串，求其中所有数字字符所代表数字之和。例如 "a1b2c3" 的结果为 1+2+3=6。',
      '一行，一个字符串 s（可含空格以换行结束）。',
      '一行，一个整数，表示数字之和。',
      'a1b2c3', '6',
      '''import sys

s = sys.stdin.readline().strip()
print(sum(int(ch) for ch in s if ch.isdigit()))
''',
      lambda r: ''.join(r.choice(string.ascii_letters + string.digits) for _ in range(r.randint(1, 20))),
      hint='逐字符判断 isdigit() 后累加即可，注意字符到数字用 int(ch) 而不是 ord 换算。',
      scope='1 ≤ |s| ≤ 1000', tags='字符串,模拟', kid=8),

    P('最长单词', 2,
      '给定一行英文句子（单词间以单个空格分隔，不含标点），输出其中长度最大的单词；若有多个，输出最先出现的那个。',
      '一行，一个句子。',
      '一行，最长的单词。',
      'i love programming very much', 'programming',
      '''import sys

words = sys.stdin.readline().strip().split()
ans = words[0]
for w in words:
    if len(w) > len(ans):
        ans = w
print(ans)
''',
      lambda r: _gen_words(r, r.randint(2, 10)),
      hint='按空格 split 后线性扫描取最大长度；注意保持"最先出现"要在严格大于时才更新。',
      scope='句子长度 ≤ 1000，至少含一个单词', tags='字符串,模拟', kid=8),

    P('删除指定字符', 2,
      '给定一个字符串 s 和一个字符 c，删除 s 中出现的所有字符 c 后输出。',
      '两行。第一行字符串 s；第二行字符 c。',
      '一行，删除后的字符串。',
      'banana\na', 'bnn',
      '''import sys

lines = sys.stdin.read().split('\\n')
s = lines[0]
c = lines[1].strip()
print(s.replace(c, ''))
''',
      lambda r: (lambda s: '%s\n%s' % (s, r.choice(s)))(
          ''.join(r.choice('abc') for _ in range(r.randint(1, 20)))),
      hint='用 replace 或遍历时跳过目标字符拼接新串；字符串不可变，注意 O(n) 拼接代价。',
      scope='1 ≤ |s| ≤ 1000', tags='字符串,模拟', kid=8),

    P('统计单词数', 2,
      '给定一行文本（单词间可能有多余空格），统计其中单词的个数。',
      '一行，一个字符串。',
      '一行，一个整数，表示单词个数。',
      '  hello   world  ', '2',
      '''import sys

s = sys.stdin.readline().strip()
print(len(s.split()))
''',
      lambda r: '  ' + '   '.join(r.choice(_WORDS) for _ in range(r.randint(1, 8))) + '  ',
      hint='不带参数的 split() 会自动忽略连续空格与首尾空白，比按单空格切分更稳健。',
      scope='字符串长度 ≤ 1000', tags='字符串,模拟', kid=8),

    P('字符串替换', 2,
      '给定字符串 s 和两个字符 a、b，把 s 中所有字符 a 替换成字符 b 后输出。',
      '三行。第一行字符串 s；第二行字符 a；第三行字符 b。',
      '一行，替换后的字符串。',
      'mississippi\ns\np', 'mippippippi',
      '''import sys

lines = sys.stdin.read().split('\\n')
s = lines[0]
a = lines[1].strip()
b = lines[2].strip()
print(''.join(b if ch == a else ch for ch in s))
''',
      lambda r: (lambda s: '%s\n%s\n%s' % (s, r.choice('abc'), r.choice('xyz')))(
          ''.join(r.choice('abc') for _ in range(r.randint(1, 20)))),
      hint='逐字符判断替换；若要替换子串则用 replace，注意替换后的内容不会再被继续替换。',
      scope='1 ≤ |s| ≤ 1000', tags='字符串,模拟', kid=8),

    P('单词首字母大写', 2,
      '给定一行英文句子（单词间以单个空格分隔），把每个单词的首字母改成大写，其余字母保持不变。',
      '一行，一个句子。',
      '一行，处理后的句子。',
      'hello world', 'Hello World',
      '''import sys

s = sys.stdin.readline().strip()
print(' '.join(w[0].upper() + w[1:] for w in s.split(' ')))
''',
      lambda r: ' '.join(r.choice(_WORDS) for _ in range(r.randint(1, 8))),
      hint='先切分再对每个单词做首字母 upper() 处理，最后拼回；也可用 capitalize() 但会改写其余字母。',
      scope='句子长度 ≤ 1000，单词均为小写字母', tags='字符串,模拟', kid=8),

    P('字符串的最小周期', 2,
      '给定一个字符串 s，求它的最小周期 k，即最小的正整数 k 使得 s 恰好由某个长度为 k 的前缀重复若干次构成（k 一定整除 |s|）。',
      '一行，一个字符串 s。',
      '一行，一个整数，表示最小周期。',
      'ababab', '2',
      '''import sys

s = sys.stdin.readline().strip()
n = len(s)
for k in range(1, n + 1):
    if n % k == 0 and s[:k] * (n // k) == s:
        print(k)
        break
''',
      lambda r: (lambda k: r.choice(['ab', 'abc', 'xyz', 'ab', 'q']) * k)(r.randint(1, 5)),
      hint='枚举 1..n 中能整除 n 的长度 k，检查 s[:k] 重复 n/k 次是否等于原串，第一个满足的即最小周期。',
      scope='1 ≤ |s| ≤ 1000', tags='字符串,枚举,周期', kid=8),

    P('最长公共前缀', 2,
      '给定 n 个字符串，求它们的最长公共前缀；若不存在公共前缀，输出空行。',
      '第一行一个整数 n；接下来 n 行，每行一个字符串。',
      '一行，最长公共前缀（可能为空）。',
      '3\nflower\nflow\nflight', 'fl',
      '''import sys

data = sys.stdin.read().split('\\n')
n = int(data[0])
strs = data[1:1 + n]
ans = strs[0]
for s in strs[1:]:
    i = 0
    while i < len(ans) and i < len(s) and ans[i] == s[i]:
        i += 1
    ans = ans[:i]
print(ans)
''',
      lambda r: (lambda n: '%d\n%s' % (n, '\n'.join(
          ''.join(r.choice('abcd') for _ in range(r.randint(1, 8))) for _ in range(n))))(r.randint(2, 6)),
      hint='以第一个串为基准逐字符与后续串比对，一旦失配即截断；也可纵向扫描列。',
      scope='1 ≤ n ≤ 200，每个串长度 ≤ 200', tags='字符串,模拟', kid=8),

    P('子串查找', 3,
      '给定文本串 t 和模式串 p，求 p 在 t 中第一次出现的位置（下标从 0 开始）；若不存在，输出 -1。',
      '两行。第一行为文本串 t；第二行为模式串 p。',
      '一行，一个整数。',
      'hello world\nworld', '6',
      '''import sys

data = sys.stdin.read().split('\\n')
t = data[0]
p = data[1]
print(t.find(p))
''',
      lambda r: (lambda t: '%s\n%s' % (t, t[r.randint(0, max(0, len(t) - 2)):][:r.randint(1, 3)]))(
          ''.join(r.choice('abcd ') for _ in range(r.randint(5, 30)))),
      hint='可直接用内置 find（底层为高效的双指针/两段匹配）；手写实现可练习朴素匹配或 KMP。',
      scope='1 ≤ |p| ≤ |t| ≤ 10⁴', tags='字符串,匹配,KMP', kid=8),

    P('字符串压缩', 2,
      '给定一个字符串，将其中连续相同的字符压缩为「字符 + 连续个数」的形式；若某字符只连续出现 1 次，则只输出该字符。',
      '一行，一个字符串 s。',
      '一行，压缩后的字符串。',
      'aaabbcdddd', 'a3b2cd4',
      '''import sys

s = sys.stdin.readline().strip()
res = []
i = 0
while i < len(s):
    j = i
    while j < len(s) and s[j] == s[i]:
        j += 1
    cnt = j - i
    res.append(s[i] if cnt == 1 else s[i] + str(cnt))
    i = j
print(''.join(res))
''',
      lambda r: ''.join(r.choice('abcd') for _ in range(r.randint(1, 25))),
      hint='双指针扫描每一段连续区间，记录段长；注意段长为 1 时不输出数字。',
      scope='1 ≤ |s| ≤ 1000，仅含小写字母', tags='字符串,双指针,游程编码', kid=8),

    P('罗马数字转整数', 2,
      '给定一个罗马数字字符串（由 I、V、X、L、C、D、M 组成，且符合书写规则），将其转换为整数。特殊规则：小的数字在大的数字左边时做减法，如 IV = 4、IX = 9。',
      '一行，一个罗马数字字符串。',
      '一行，一个整数。',
      'MCMXCIV', '1994',
      '''import sys

s = sys.stdin.readline().strip()
val = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
ans = 0
for i in range(len(s)):
    if i + 1 < len(s) and val[s[i]] < val[s[i + 1]]:
        ans -= val[s[i]]
    else:
        ans += val[s[i]]
print(ans)
''',
      lambda r: (lambda x: ''.join(r.choice('IVXLCDM') for _ in range(r.randint(1, 8))))(r.random()),
      hint='从左到右扫描：当前符号值小于右边符号值时减去它，否则加上它。这是处理"左减右加"的统一写法。',
      scope='1 ≤ |s| ≤ 15', tags='字符串,模拟,哈希映射', kid=8),

    P('整数转罗马数字', 3,
      '给定一个 1 到 3999 之间的整数，输出它的罗马数字表示。',
      '一行，一个整数 n。',
      '一行，对应的罗马数字。',
      '1994', 'MCMXCIV',
      '''import sys

n = int(sys.stdin.read().strip())
pairs = [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), (100, 'C'), (90, 'XC'),
         (50, 'L'), (40, 'XL'), (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]
res = []
for v, sym in pairs:
    while n >= v:
        res.append(sym)
        n -= v
print(''.join(res))
''',
      lambda r: str(r.randint(1, 3999)),
      hint='贪心：把 6 种减法组合（4 与 9 的各档）也放进制表，从大到小不断扣除并拼接符号。',
      scope='1 ≤ n ≤ 3999', tags='字符串,贪心,模拟', kid=8),

    P('有效的括号', 2,
      '给定一个只含 ()[]{} 六种字符的字符串，判断其中的括号是否合法匹配（每个左括号都有对应类型、正确顺序的右括号）。',
      '一行，一个字符串 s。',
      '一行，合法输出 Yes，否则输出 No。',
      '([]{})', 'Yes',
      '''import sys

s = sys.stdin.readline().strip()
mp = {')': '(', ']': '[', '}': '{'}
st = []
ok = True
for ch in s:
    if ch in mp:
        if not st or st[-1] != mp[ch]:
            ok = False
            break
        st.pop()
    else:
        st.append(ch)
if st:
    ok = False
print('Yes' if ok else 'No')
''',
      lambda r: (lambda pairs: ''.join(
          (lambda o, c: o + c if r.random() < 0.7 else c + o)(*r.choice(pairs))
          for _ in range(r.randint(1, 6))))([('(', ')'), ('[', ']'), ('{', '}')]),
      hint='栈的经典应用：遇左括号入栈，遇右括号检查栈顶是否为对应左括号；最后栈必须为空。',
      scope='1 ≤ |s| ≤ 10⁴', tags='字符串,栈', kid=8),

    P('最长无重复字符子串（滑动窗口）', 3,
      '给定一个字符串，求其中不含重复字符的最长子串的长度。',
      '一行，一个字符串 s。',
      '一行，一个整数，表示最长无重复字符子串的长度。',
      'abcabcbb', '3',
      '''import sys

s = sys.stdin.readline().strip()
last = {}
left = 0
ans = 0
for i, ch in enumerate(s):
    if ch in last and last[ch] >= left:
        left = last[ch] + 1
    last[ch] = i
    ans = max(ans, i - left + 1)
print(ans)
''',
      lambda r: ''.join(r.choice('abcd') for _ in range(r.randint(1, 30))),
      hint='滑动窗口 + 哈希表记录每个字符最后出现位置：右端点右移时，若字符已在窗口内就把左端点跳到其后一位。',
      scope='1 ≤ |s| ≤ 10⁴，仅含小写字母', tags='字符串,滑动窗口,哈希表', kid=8),

    P('单词倒排', 2,
      '给定一行英文句子（单词间以单个空格分隔），把单词的顺序颠倒后输出（单词本身不反转）。',
      '一行，一个句子。',
      '一行，倒排后的句子。',
      'the sky is blue', 'blue is sky the',
      '''import sys

words = sys.stdin.readline().strip().split(' ')
print(' '.join(reversed(words)))
''',
      lambda r: _gen_words(r, r.randint(2, 9)),
      hint='切分后逆序拼接；若要求整体反转再逐词反转则是另一种原地做法。',
      scope='句子长度 ≤ 1000', tags='字符串,模拟', kid=8),

    P('判断字母异位词', 2,
      '给定两个只含小写字母的字符串，判断它们是否互为字母异位词（字符及出现次数完全相同，顺序可不同）。',
      '两行，每行一个字符串。',
      '一行，是输出 Yes，否则输出 No。',
      'listen\nsilent', 'Yes',
      '''import sys

data = sys.stdin.read().split('\\n')
a = data[0].strip()
b = data[1].strip()
print('Yes' if sorted(a) == sorted(b) else 'No')
''',
      _gen_anagram,
      hint='排序后比较是最简洁的 O(n log n) 写法；也可以用长度 26 的计数数组做到 O(n)。',
      scope='1 ≤ |s| ≤ 1000', tags='字符串,哈希,排序', kid=8),

    P('字符串转整数（atoi）', 3,
      '模拟 atoi：读入一个字符串，跳过前导空格，读取可选的正负号，之后尽可能多地读取连续数字字符并转成整数；若结果超出 [-2³¹, 2³¹-1] 则截断到边界；若第一个非空格字符不是数字或正负号，输出 0。',
      '一行，一个字符串 s。',
      '一行，一个整数。',
      '   -4193 with words', '-4193',
      '''import sys

s = sys.stdin.readline().strip()
INT_MAX = 2 ** 31 - 1
INT_MIN = -2 ** 31
i, n = 0, len(s)
while i < n and s[i] == ' ':
    i += 1
sign = 1
if i < n and s[i] in '+-':
    if s[i] == '-':
        sign = -1
    i += 1
ans = 0
while i < n and s[i].isdigit():
    ans = ans * 10 + int(s[i])
    i += 1
ans *= sign
if ans > INT_MAX:
    ans = INT_MAX
if ans < INT_MIN:
    ans = INT_MIN
print(ans)
''',
      lambda r: (lambda v: (' ' * r.randint(0, 3)) + (r.choice(['', '-', '+']) if r.random() < 0.6 else '') + str(v)
                 + ('' if r.random() < 0.5 else ' abc'))(r.choice([r.randint(0, 999), r.randint(0, 10 ** 12)])),
      hint='按"去空格 → 读符号 → 读数字 → 溢出截断"四步实现；溢出要在累加过程中或最后统一裁剪。',
      scope='1 ≤ |s| ≤ 200', tags='字符串,模拟,边界处理', kid=8),
]
