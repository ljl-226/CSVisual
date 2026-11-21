-- ============================================================
--  算法题库扩容：洛谷风格程序设计题（新增 170 道，总数 30 -> 200）
--  说明：
--    1. 每道题先 INSERT 一条 algorithm，紧跟 SET @aid = LAST_INSERT_ID();，
--       再用 (@aid, ...) 插入该题测试用例，保证用例挂在正确的题目上
--    2. 每个用例的 expected 由 Python 3 真实运行 reference_code 得到，
--       与程序标准输出逐字符一致（含行末换行）
--    3. 测试用例 = 1 个样例（is_sample=1）+ 5 个隐藏用例，由固定随机种子生成
--  本文件由 tools/algo/gen_algo.py 生成，请勿手工编辑
--  执行顺序：... -> seed-textbook -> seed-core20 -> seed-algo200
-- ============================================================

-- ---------- 1. 温度转换（难度 1） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('温度转换', 1, 10, '## 【题目描述】\n\n输入一个摄氏温度 c，按公式 f = c × 9 / 5 + 32 转换为华氏温度并输出。\n\n## 【输入格式】\n\n一行，一个浮点数 c，表示摄氏温度。\n\n## 【输出格式】\n\n一行，一个浮点数，表示华氏温度，保留 1 位小数。\n\n## 【样例】\n\n输入：\n\n```\n36.5\n```\n\n输出：\n\n```\n97.7\n```\n\n## 【数据范围】\n\n-100 ≤ c ≤ 100\n\n## 【提示】\n\n浮点运算直接用 double 精度即可，注意输出格式要求保留 1 位小数，Python 可用 "%.1f"。', '一行，一个浮点数 c，表示摄氏温度。', '一行，一个浮点数，表示华氏温度，保留 1 位小数。',
 '36.5', '97.7', '浮点运算直接用 double 精度即可，注意输出格式要求保留 1 位小数，Python 可用 "%.1f"。', 'import sys\n\nc = float(sys.stdin.read().strip())\nprint("%.1f" % (c * 9 / 5 + 32))\n', 'python',
 '入门,模拟', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '36.5', '97.7\n', 1, 1),
(@aid, '12.5', '54.5\n', 0, 2),
(@aid, '41.9', '107.4\n', 0, 3),
(@aid, '74.4', '165.9\n', 0, 4),
(@aid, '30.4', '86.7\n', 0, 5),
(@aid, '33.1', '91.6\n', 0, 6);

-- ---------- 2. 三角形面积（海伦公式）（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('三角形面积（海伦公式）', 2, 10, '## 【题目描述】\n\n给定三条边长 a、b、c，保证能构成三角形，求该三角形的面积。\n\n## 【输入格式】\n\n一行，三个浮点数 a、b、c，表示三角形三条边长。\n\n## 【输出格式】\n\n一行，一个浮点数，表示三角形面积，保留 2 位小数。\n\n## 【样例】\n\n输入：\n\n```\n3 4 5\n```\n\n输出：\n\n```\n6.00\n```\n\n## 【数据范围】\n\n1 ≤ a, b, c ≤ 100，且保证能构成三角形\n\n## 【提示】\n\n海伦公式：p = (a+b+c)/2，S = √(p(p-a)(p-b)(p-c))。生成用例时已保证三边能构成三角形。', '一行，三个浮点数 a、b、c，表示三角形三条边长。', '一行，一个浮点数，表示三角形面积，保留 2 位小数。',
 '3 4 5', '6.00', '海伦公式：p = (a+b+c)/2，S = √(p(p-a)(p-b)(p-c))。生成用例时已保证三边能构成三角形。', 'import sys\nimport math\n\na, b, c = map(float, sys.stdin.read().split())\np = (a + b + c) / 2\ns = math.sqrt(p * (p - a) * (p - b) * (p - c))\nprint("%.2f" % s)\n', 'python',
 '入门,数学,几何', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3 4 5', '6.00\n', 1, 1),
(@aid, '24 6 20', '48.73\n', 0, 2),
(@aid, '28 39 38', '501.78\n', 0, 3),
(@aid, '43 6 46', '115.35\n', 0, 4),
(@aid, '19 10 12', '52.39\n', 0, 5),
(@aid, '19 3 20', '27.50\n', 0, 6);

-- ---------- 3. 圆的周长与面积（难度 1） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('圆的周长与面积', 1, 10, '## 【题目描述】\n\n给定圆的半径 r，求圆的周长与面积，圆周率取 3.14159。\n\n## 【输入格式】\n\n一行，一个浮点数 r，表示圆的半径。\n\n## 【输出格式】\n\n两行，第一行是周长，第二行是面积，均保留 2 位小数。\n\n## 【样例】\n\n输入：\n\n```\n2\n```\n\n输出：\n\n```\n12.57\n12.57\n```\n\n## 【数据范围】\n\n0 < r ≤ 100\n\n## 【提示】\n\n周长 C = 2πr，面积 S = πr²。注意本题指定了 π 的取值，不要使用其它精度。', '一行，一个浮点数 r，表示圆的半径。', '两行，第一行是周长，第二行是面积，均保留 2 位小数。',
 '2', '12.57\n12.57', '周长 C = 2πr，面积 S = πr²。注意本题指定了 π 的取值，不要使用其它精度。', 'import sys\n\nPI = 3.14159\nr = float(sys.stdin.read().strip())\nprint("%.2f" % (2 * PI * r))\nprint("%.2f" % (PI * r * r))\n', 'python',
 '入门,数学,几何', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '2', '12.57\n12.57\n', 1, 1),
(@aid, '39.30', '246.93\n4852.15\n', 0, 2),
(@aid, '11.14', '69.99\n389.87\n', 0, 3),
(@aid, '3.96', '24.88\n49.27\n', 0, 4),
(@aid, '92.82', '583.20\n27066.53\n', 0, 5),
(@aid, '1.91', '12.00\n11.46\n', 0, 6);

-- ---------- 4. 等差数列求和（难度 1） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('等差数列求和', 1, 10, '## 【题目描述】\n\n给定等差数列的首项 a₁、公差 d 和项数 n，求该数列前 n 项的和。\n\n## 【输入格式】\n\n一行，三个整数 a₁、d、n，分别表示首项、公差与项数。\n\n## 【输出格式】\n\n一行，一个整数，表示前 n 项的和。\n\n## 【样例】\n\n输入：\n\n```\n1 2 5\n```\n\n输出：\n\n```\n25\n```\n\n## 【数据范围】\n\n-10⁴ ≤ a₁, d ≤ 10⁴，1 ≤ n ≤ 10⁶\n\n## 【提示】\n\n求和公式 S = n·a₁ + n(n-1)/2·d，直接套公式是 O(1)，逐项累加是 O(n)，n 很大时公式更稳。', '一行，三个整数 a₁、d、n，分别表示首项、公差与项数。', '一行，一个整数，表示前 n 项的和。',
 '1 2 5', '25', '求和公式 S = n·a₁ + n(n-1)/2·d，直接套公式是 O(1)，逐项累加是 O(n)，n 很大时公式更稳。', 'import sys\n\na1, d, n = map(int, sys.stdin.read().split())\nprint(n * a1 + n * (n - 1) // 2 * d)\n', 'python',
 '入门,数学,数列', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '1 2 5', '25\n', 1, 1),
(@aid, '-25 -20 6903', '-476617635\n', 0, 2),
(@aid, '-29 6 6514', '127088140\n', 0, 3),
(@aid, '-12 8 4296', '73753728\n', 0, 4),
(@aid, '11 -11 6583', '-238238770\n', 0, 5),
(@aid, '25 -14 127', '-108839\n', 0, 6);

-- ---------- 5. 求平均数（难度 1） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('求平均数', 1, 10, '## 【题目描述】\n\n输入 n 个整数，求它们的平均值。\n\n## 【输入格式】\n\n两行。第一行一个整数 n；第二行 n 个用空格分隔的整数。\n\n## 【输出格式】\n\n一行，一个浮点数，表示平均值，保留 2 位小数。\n\n## 【样例】\n\n输入：\n\n```\n4\n1 2 3 4\n```\n\n输出：\n\n```\n2.50\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁵，-10⁹ ≤ 每个数 ≤ 10⁹\n\n## 【提示】\n\n求和后除以 n 即可，注意用浮点除法。n 个数可能很多，读入时用 read().split() 一次性读入更快。', '两行。第一行一个整数 n；第二行 n 个用空格分隔的整数。', '一行，一个浮点数，表示平均值，保留 2 位小数。',
 '4\n1 2 3 4', '2.50', '求和后除以 n 即可，注意用浮点除法。n 个数可能很多，读入时用 read().split() 一次性读入更快。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nnums = list(map(int, data[1:1 + n]))\nprint("%.2f" % (sum(nums) / n))\n', 'python',
 '入门,模拟,统计', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '4\n1 2 3 4', '2.50\n', 1, 1),
(@aid, '20\n-10 310 716 -821 694 825 474 84 -422 416 667 450 631 -223 785 -925 107 918 564 -704', '226.80\n', 0, 2),
(@aid, '6\n977 -780 192 669 -263 -362', '72.17\n', 0, 3),
(@aid, '29\n71 425 -725 -502 881 -459 818 -612 951 804 928 -277 -160 434 -424 -264 573 535 811 -491 752 477 169 662 -809 -510 -456 -469 999', '142.48\n', 0, 4),
(@aid, '29\n-380 -366 -461 -903 -648 -77 683 -255 640 760 176 -110 302 -58 -813 -158 -693 -424 -625 246 -816 -252 210 549 -822 -608 78 205 -27', '-160.24\n', 0, 5),
(@aid, '22\n-785 -621 342 937 78 -209 -801 -234 -151 -19 914 -843 918 98 -725 -693 -674 -101 -681 -986 -114 568', '-171.91\n', 0, 6);

-- ---------- 6. 最大值与最小值（难度 1） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('最大值与最小值', 1, 10, '## 【题目描述】\n\n输入 n 个整数，输出其中的最大值与最小值。\n\n## 【输入格式】\n\n两行。第一行一个整数 n；第二行 n 个用空格分隔的整数。\n\n## 【输出格式】\n\n一行，两个整数，分别为最大值与最小值，用空格分隔。\n\n## 【样例】\n\n输入：\n\n```\n5\n3 9 2 7 5\n```\n\n输出：\n\n```\n9 2\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁵\n\n## 【提示】\n\n一趟线性扫描即可求出最值，时间复杂度 O(n)，不需要排序（排序是 O(n log n)）。', '两行。第一行一个整数 n；第二行 n 个用空格分隔的整数。', '一行，两个整数，分别为最大值与最小值，用空格分隔。',
 '5\n3 9 2 7 5', '9 2', '一趟线性扫描即可求出最值，时间复杂度 O(n)，不需要排序（排序是 O(n log n)）。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nnums = list(map(int, data[1:1 + n]))\nprint(max(nums), min(nums))\n', 'python',
 '入门,模拟,最值', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '5\n3 9 2 7 5', '9 2\n', 1, 1),
(@aid, '35\n4805 -6961 -1001 5441 2282 -8641 1864 6778 -6878 543 -7163 -5226 5812 -5386 -7449 8393 321 4450 -1194 -3571 4665 -6948 -5735 3840 9905 -8054 -5594 9489 -8076 9688 7258 3554 -3341 9663 9865', '9905 -8641\n', 0, 2),
(@aid, '49\n-3410 -2419 5314 4614 -1047 9330 -5509 4775 7897 2172 -417 6168 -3335 -5594 1358 3596 -3635 920 -4721 -8656 -8655 5887 3759 3703 9638 -3789 -4466 -1384 7689 4368 -9858 -7974 -9836 4667 -66 -4864 -7067 -1518 -1662 6636 -3384 2381 -4130 -9029 3673 -9078 9336 -7490 4851', '9638 -9858\n', 0, 3),
(@aid, '22\n5840 8130 -809 -692 -6280 -9458 9949 -274 1634 -5333 5825 1615 7863 7056 1959 8795 -1704 260 -2799 1636 -5563 3962', '9949 -9458\n', 0, 4),
(@aid, '23\n8438 -5243 -6061 4488 -3215 -8436 7549 -2097 -4012 5694 -4198 -5128 179 2630 -9110 -2500 1195 -3052 9476 -5038 3638 2830 6692', '9476 -9110\n', 0, 5),
(@aid, '11\n1923 -9491 9944 9645 -8858 4831 -3174 -6002 1745 3848 1891', '9944 -9491\n', 0, 6);

-- ---------- 7. 斐波那契数列第 n 项（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('斐波那契数列第 n 项', 2, 10, '## 【题目描述】\n\n斐波那契数列定义为 F(1) = 1，F(2) = 1，F(n) = F(n-1) + F(n-2)（n ≥ 3）。给定 n，求 F(n)。\n\n## 【输入格式】\n\n一行，一个整数 n。\n\n## 【输出格式】\n\n一行，一个整数，表示 F(n)。\n\n## 【样例】\n\n输入：\n\n```\n10\n```\n\n输出：\n\n```\n55\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 60\n\n## 【提示】\n\n直接递归会重复计算大量子问题（指数级），应改用递推或迭代，时间 O(n)、空间 O(1)。', '一行，一个整数 n。', '一行，一个整数，表示 F(n)。',
 '10', '55', '直接递归会重复计算大量子问题（指数级），应改用递推或迭代，时间 O(n)、空间 O(1)。', 'import sys\n\nn = int(sys.stdin.read().strip())\na = b = 1\nfor _ in range(3, n + 1):\n    a, b = b, a + b\nprint(a if n <= 2 else b)\n', 'python',
 '递归,递推,数学', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '10', '55\n', 1, 1),
(@aid, '16', '987\n', 0, 2),
(@aid, '4', '3\n', 0, 3),
(@aid, '11', '89\n', 0, 4),
(@aid, '44', '701408733\n', 0, 5),
(@aid, '52', '32951280099\n', 0, 6);

-- ---------- 8. 闰年判断（难度 1） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('闰年判断', 1, 10, '## 【题目描述】\n\n给定一个年份，判断其是否为闰年。闰年规则：能被 400 整除，或者能被 4 整除但不能被 100 整除。\n\n## 【输入格式】\n\n一行，一个整数 y，表示年份。\n\n## 【输出格式】\n\n一行，是闰年输出 Yes，否则输出 No。\n\n## 【样例】\n\n输入：\n\n```\n2000\n```\n\n输出：\n\n```\nYes\n```\n\n## 【数据范围】\n\n1 ≤ y ≤ 10⁴\n\n## 【提示】\n\n条件可写成 (y % 400 == 0) or (y % 4 == 0 and y % 100 != 0)。注意 1900 年不是闰年，2000 年是闰年。', '一行，一个整数 y，表示年份。', '一行，是闰年输出 Yes，否则输出 No。',
 '2000', 'Yes', '条件可写成 (y % 400 == 0) or (y % 4 == 0 and y % 100 != 0)。注意 1900 年不是闰年，2000 年是闰年。', 'import sys\n\ny = int(sys.stdin.read().strip())\nprint("Yes" if (y % 400 == 0 or (y % 4 == 0 and y % 100 != 0)) else "No")\n', 'python',
 '入门,模拟,日期', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '2000', 'Yes\n', 1, 1),
(@aid, '1051', 'No\n', 0, 2),
(@aid, '1180', 'Yes\n', 0, 3),
(@aid, '598', 'No\n', 0, 4),
(@aid, '2227', 'No\n', 0, 5),
(@aid, '703', 'No\n', 0, 6);

-- ---------- 9. 整数反转（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('整数反转', 2, 10, '## 【题目描述】\n\n给定一个整数，将其各位数字反转后输出（保留负号，前导零不输出）。\n\n## 【输入格式】\n\n一行，一个整数 x。\n\n## 【输出格式】\n\n一行，一个整数，表示反转后的结果。\n\n## 【样例】\n\n输入：\n\n```\n-1200\n```\n\n输出：\n\n```\n-21\n```\n\n## 【数据范围】\n\n-10⁹ ≤ x ≤ 10⁹\n\n## 【提示】\n\n也可以不用字符串：反复取 x % 10 拼到结果里再 x //= 10。注意处理负号与末尾的 0。', '一行，一个整数 x。', '一行，一个整数，表示反转后的结果。',
 '-1200', '-21', '也可以不用字符串：反复取 x % 10 拼到结果里再 x //= 10。注意处理负号与末尾的 0。', 'import sys\n\nx = int(sys.stdin.read().strip())\nsign = -1 if x < 0 else 1\ny = int(str(abs(x))[::-1])\nprint(sign * y)\n', 'python',
 '入门,模拟,数学', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '-1200', '-21\n', 1, 1),
(@aid, '-689034582', '-285430986\n', 0, 2),
(@aid, '997158888', '888851799\n', 0, 3),
(@aid, '-6430221', '-1220346\n', 0, 4),
(@aid, '938905195', '591509839\n', 0, 5),
(@aid, '19690240', '4209691\n', 0, 6);

-- ---------- 10. 回文数判断（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('回文数判断', 2, 10, '## 【题目描述】\n\n给定一个非负整数，判断其十进制表示是否为回文（正着读和反着读相同）。\n\n## 【输入格式】\n\n一行，一个非负整数 x。\n\n## 【输出格式】\n\n一行，是回文输出 Yes，否则输出 No。\n\n## 【样例】\n\n输入：\n\n```\n12321\n```\n\n输出：\n\n```\nYes\n```\n\n## 【数据范围】\n\n0 ≤ x ≤ 10⁹\n\n## 【提示】\n\n字符串反转比较最直观；也可只反转后一半数字与原数前半比较，避免大数溢出。', '一行，一个非负整数 x。', '一行，是回文输出 Yes，否则输出 No。',
 '12321', 'Yes', '字符串反转比较最直观；也可只反转后一半数字与原数前半比较，避免大数溢出。', 'import sys\n\ns = sys.stdin.read().strip()\nprint("Yes" if s == s[::-1] else "No")\n', 'python',
 '入门,字符串,模拟', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '12321', 'Yes\n', 1, 1),
(@aid, '342239287', 'No\n', 0, 2),
(@aid, '224202886', 'No\n', 0, 3),
(@aid, '370009928', 'No\n', 0, 4),
(@aid, '118626414', 'No\n', 0, 5),
(@aid, '113611901', 'No\n', 0, 6);

-- ---------- 11. 水仙花数（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('水仙花数', 2, 10, '## 【题目描述】\n\n水仙花数指一个三位数，其各位数字的立方和等于它本身（如 153 = 1³ + 5³ + 3³）。给定区间 [m, n]，输出其中所有的水仙花数。\n\n## 【输入格式】\n\n一行，两个整数 m、n，表示区间端点。\n\n## 【输出格式】\n\n一行，若干个整数，为该区间内所有水仙花数，按从小到大顺序排列，用空格分隔；若不存在则输出 -1。\n\n## 【样例】\n\n输入：\n\n```\n100 400\n```\n\n输出：\n\n```\n153 370 371\n```\n\n## 【数据范围】\n\n100 ≤ m ≤ n ≤ 999\n\n## 【提示】\n\n枚举区间内每个数，拆出百位 a = x//100、十位 b = x//10%10、个位 c = x%10 判断即可。', '一行，两个整数 m、n，表示区间端点。', '一行，若干个整数，为该区间内所有水仙花数，按从小到大顺序排列，用空格分隔；若不存在则输出 -1。',
 '100 400', '153 370 371', '枚举区间内每个数，拆出百位 a = x//100、十位 b = x//10%10、个位 c = x%10 判断即可。', 'import sys\n\nm, n = map(int, sys.stdin.read().split())\nans = []\nfor x in range(m, n + 1):\n    if 100 <= x <= 999 and (x // 100) ** 3 + (x // 10 % 10) ** 3 + (x % 10) ** 3 == x:\n        ans.append(x)\nprint(" ".join(map(str, ans)) if ans else "-1")\n', 'python',
 '枚举,数学,模拟', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '100 400', '153 370 371\n', 1, 1),
(@aid, '100 764', '153 370 371 407\n', 0, 2),
(@aid, '100 879', '153 370 371 407\n', 0, 3),
(@aid, '100 483', '153 370 371 407\n', 0, 4),
(@aid, '100 225', '153\n', 0, 5),
(@aid, '100 536', '153 370 371 407\n', 0, 6);

-- ---------- 12. 数字出现次数统计（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('数字出现次数统计', 2, 10, '## 【题目描述】\n\n给定整数 n 和数字 d（0 ≤ d ≤ 9），统计从 1 到 n 的所有整数的十进制表示中，数字 d 一共出现了多少次。\n\n## 【输入格式】\n\n一行，两个整数 n 和 d。\n\n## 【输出格式】\n\n一行，一个整数，表示数字 d 出现的总次数。\n\n## 【样例】\n\n输入：\n\n```\n12 1\n```\n\n输出：\n\n```\n5\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁴，0 ≤ d ≤ 9\n\n## 【提示】\n\n直接枚举 1..n 并统计每位数字即可（O(n log n)）。若 n 很大，可按位做数位统计优化到 O(log n)。', '一行，两个整数 n 和 d。', '一行，一个整数，表示数字 d 出现的总次数。',
 '12 1', '5', '直接枚举 1..n 并统计每位数字即可（O(n log n)）。若 n 很大，可按位做数位统计优化到 O(log n)。', 'import sys\n\nn, d = map(int, sys.stdin.read().split())\nans = 0\nfor i in range(1, n + 1):\n    ans += str(i).count(str(d))\nprint(ans)\n', 'python',
 '枚举,数学,统计', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '12 1', '5\n', 1, 1),
(@aid, '77 8', '7\n', 0, 2),
(@aid, '260 4', '56\n', 0, 3),
(@aid, '163 5', '36\n', 0, 4),
(@aid, '91 8', '19\n', 0, 5),
(@aid, '216 5', '42\n', 0, 6);

-- ---------- 13. 阶乘计算（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('阶乘计算', 2, 10, '## 【题目描述】\n\n给定整数 n，求 n 的阶乘 n!（0! = 1）。\n\n## 【输入格式】\n\n一行，一个整数 n。\n\n## 【输出格式】\n\n一行，一个整数，表示 n! 的值。\n\n## 【样例】\n\n输入：\n\n```\n5\n```\n\n输出：\n\n```\n120\n```\n\n## 【数据范围】\n\n0 ≤ n ≤ 25\n\n## 【提示】\n\nPython 整数无精度限制，可直接连乘；C/C++ 需要注意 20! 已超出 64 位整数范围。', '一行，一个整数 n。', '一行，一个整数，表示 n! 的值。',
 '5', '120', 'Python 整数无精度限制，可直接连乘；C/C++ 需要注意 20! 已超出 64 位整数范围。', 'import sys\nimport math\n\nn = int(sys.stdin.read().strip())\nprint(math.factorial(n))\n', 'python',
 '入门,数学,递推', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '5', '120\n', 1, 1),
(@aid, '14', '87178291200\n', 0, 2),
(@aid, '12', '479001600\n', 0, 3),
(@aid, '24', '620448401733239439360000\n', 0, 4),
(@aid, '0', '1\n', 0, 5),
(@aid, '25', '15511210043330985984000000\n', 0, 6);

-- ---------- 14. 时间转换（秒转时分秒）（难度 1） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('时间转换（秒转时分秒）', 1, 10, '## 【题目描述】\n\n给定一个整数秒数 t，将其转换为 "H:M:S" 的形式输出（时、分、秒均不带前导零）。\n\n## 【输入格式】\n\n一行，一个整数 t，表示秒数。\n\n## 【输出格式】\n\n一行，形如 H:M:S 的字符串。\n\n## 【样例】\n\n输入：\n\n```\n3661\n```\n\n输出：\n\n```\n1:1:1\n```\n\n## 【数据范围】\n\n0 ≤ t ≤ 10⁹\n\n## 【提示】\n\n整除与取余：时 = t // 3600，分 = (t % 3600) // 60，秒 = t % 60。', '一行，一个整数 t，表示秒数。', '一行，形如 H:M:S 的字符串。',
 '3661', '1:1:1', '整除与取余：时 = t // 3600，分 = (t % 3600) // 60，秒 = t % 60。', 'import sys\n\nt = int(sys.stdin.read().strip())\nh = t // 3600\nm = t % 3600 // 60\ns = t % 60\nprint("%d:%d:%d" % (h, m, s))\n', 'python',
 '入门,模拟,时间', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3661', '1:1:1\n', 1, 1),
(@aid, '93147', '25:52:27\n', 0, 2),
(@aid, '129426', '35:57:6\n', 0, 3),
(@aid, '28054', '7:47:34\n', 0, 4),
(@aid, '174440', '48:27:20\n', 0, 5),
(@aid, '100815', '28:0:15\n', 0, 6);

-- ---------- 15. 成绩等级转换（难度 1） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('成绩等级转换', 1, 10, '## 【题目描述】\n\n给定百分制成绩，按如下规则输出等级：≥90 为 A，≥80 为 B，≥70 为 C，≥60 为 D，其余为 E。\n\n## 【输入格式】\n\n一行，一个整数 s，表示成绩。\n\n## 【输出格式】\n\n一行，一个大写字母，表示等级。\n\n## 【样例】\n\n输入：\n\n```\n85\n```\n\n输出：\n\n```\nB\n```\n\n## 【数据范围】\n\n0 ≤ s ≤ 100\n\n## 【提示】\n\n多分支判断，注意边界是"大于等于"。', '一行，一个整数 s，表示成绩。', '一行，一个大写字母，表示等级。',
 '85', 'B', '多分支判断，注意边界是"大于等于"。', 'import sys\n\ns = int(sys.stdin.read().strip())\nif s >= 90:\n    print("A")\nelif s >= 80:\n    print("B")\nelif s >= 70:\n    print("C")\nelif s >= 60:\n    print("D")\nelse:\n    print("E")\n', 'python',
 '入门,分支,模拟', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '85', 'B\n', 1, 1),
(@aid, '53', 'E\n', 0, 2),
(@aid, '27', 'E\n', 0, 3),
(@aid, '70', 'C\n', 0, 4),
(@aid, '93', 'A\n', 0, 5),
(@aid, '33', 'E\n', 0, 6);

-- ---------- 16. 简单计算器（难度 1） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('简单计算器', 1, 10, '## 【题目描述】\n\n输入两个整数 a、b 和一个运算符 op（+、-、*、/），输出运算结果。除法保留 2 位小数；若除数为 0，输出 Error。\n\n## 【输入格式】\n\n一行，依次为整数 a、运算符 op、整数 b，用空格分隔。\n\n## 【输出格式】\n\n若为加减乘，输出一个整数；若为除法且除数非 0，输出保留 2 位小数的浮点数；除数为 0 时输出 Error。\n\n## 【样例】\n\n输入：\n\n```\n7 / 2\n```\n\n输出：\n\n```\n3.50\n```\n\n## 【数据范围】\n\n-10⁴ ≤ a, b ≤ 10⁴，op ∈ {+, -, *, /}\n\n## 【提示】\n\n用分支处理四种运算符，除法的除零检查必须放在计算之前。', '一行，依次为整数 a、运算符 op、整数 b，用空格分隔。', '若为加减乘，输出一个整数；若为除法且除数非 0，输出保留 2 位小数的浮点数；除数为 0 时输出 Error。',
 '7 / 2', '3.50', '用分支处理四种运算符，除法的除零检查必须放在计算之前。', 'import sys\n\ndata = sys.stdin.read().split()\na = int(data[0])\nop = data[1]\nb = int(data[2])\nif op == "+":\n    print(a + b)\nelif op == "-":\n    print(a - b)\nelif op == "*":\n    print(a * b)\nelse:\n    if b == 0:\n        print("Error")\n    else:\n        print("%.2f" % (a / b))\n', 'python',
 '入门,分支,模拟', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '7 / 2', '3.50\n', 1, 1),
(@aid, '-67 - 66', '-133\n', 0, 2),
(@aid, '43 / 38', '1.13\n', 0, 3),
(@aid, '-66 - 39', '-105\n', 0, 4),
(@aid, '93 + 13', '106\n', 0, 5),
(@aid, '-67 / 79', '-0.85\n', 0, 6);

-- ---------- 17. 字符分类统计（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('字符分类统计', 2, 10, '## 【题目描述】\n\n输入一行字符串（可含空格），统计其中英文字母、数字、空格以及其它字符的个数。\n\n## 【输入格式】\n\n一行字符串 s，长度不超过 200，可包含空格。\n\n## 【输出格式】\n\n一行，四个整数，依次为字母、数字、空格、其它字符的个数，用空格分隔。\n\n## 【样例】\n\n输入：\n\n```\nHello 123!\n```\n\n输出：\n\n```\n5 3 1 1\n```\n\n## 【数据范围】\n\n1 ≤ |s| ≤ 200\n\n## 【提示】\n\n注意整行读入要用 read() 而不是 split()，否则空格会被切掉；用 isalpha/isdigit 判断类别。', '一行字符串 s，长度不超过 200，可包含空格。', '一行，四个整数，依次为字母、数字、空格、其它字符的个数，用空格分隔。',
 'Hello 123!', '5 3 1 1', '注意整行读入要用 read() 而不是 split()，否则空格会被切掉；用 isalpha/isdigit 判断类别。', 'import sys\n\ns = sys.stdin.read().rstrip("\\n")\nletter = digit = space = other = 0\nfor ch in s:\n    if ch.isalpha() and ch.isascii():\n        letter += 1\n    elif ch.isdigit():\n        digit += 1\n    elif ch == " ":\n        space += 1\n    else:\n        other += 1\nprint(letter, digit, space, other)\n', 'python',
 '字符串,模拟,统计', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'Hello 123!', '5 3 1 1\n', 1, 1),
(@aid, 'Za#9ac9Z2!!#Yc2cb19@bX0 Z!0#Zc', '14 8 1 7\n', 0, 2),
(@aid, 'Z0 2Y0 21@ca!X', '5 5 2 2\n', 0, 3),
(@aid, '10X', '1 2 0 0\n', 0, 4),
(@aid, '@Z2Z#Zcc#@caa cZ!@X#0YZ91@9@XYa!@ cZc', '19 5 2 11\n', 0, 5),
(@aid, 'ZZ2#@1!@Z#9X@9Za# 0ca2  ', '8 6 3 7\n', 0, 6);

-- ---------- 18. 大小写互换（难度 1） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('大小写互换', 1, 10, '## 【题目描述】\n\n输入一行字符串，将其中的大写字母变为小写、小写字母变为大写，其余字符保持不变。\n\n## 【输入格式】\n\n一行字符串 s，长度不超过 200，可包含空格。\n\n## 【输出格式】\n\n一行，转换后的字符串。\n\n## 【样例】\n\n输入：\n\n```\nHello World 123\n```\n\n输出：\n\n```\nhELLO wORLD 123\n```\n\n## 【数据范围】\n\n1 ≤ |s| ≤ 200\n\n## 【提示】\n\nPython 可直接用 swapcase()；C 语言可用 ch ^= 32 或判断 ASCII 区间后加减 32。', '一行字符串 s，长度不超过 200，可包含空格。', '一行，转换后的字符串。',
 'Hello World 123', 'hELLO wORLD 123', 'Python 可直接用 swapcase()；C 语言可用 ch ^= 32 或判断 ASCII 区间后加减 32。', 'import sys\n\ns = sys.stdin.read().rstrip("\\n")\nprint(s.swapcase())\n', 'python',
 '字符串,入门,模拟', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'Hello World 123', 'hELLO wORLD 123\n', 1, 1),
(@aid, '9  19Yc10ac9X00cX0ca119YZac1Y0Y 9Za0Y Z ', '9  19yC10AC9x00Cx0CA119yzAC1y0y 9zA0y z \n', 0, 2),
(@aid, 'bZc9aa0ZZ0 abab0bY ', 'BzC9AA0zz0 ABAB0By \n', 0, 3),
(@aid, '9', '9\n', 0, 4),
(@aid, '9aa09 acX11 X0  1Z01Y a1bc', '9AA09 ACx11 x0  1z01y A1BC\n', 0, 5),
(@aid, 'aa1ZY9aZZ10X0  XXY10', 'AA1zy9Azz10x0  xxy10\n', 0, 6);

-- ---------- 19. 数组逆序输出（难度 1） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('数组逆序输出', 1, 10, '## 【题目描述】\n\n输入 n 个整数，按与输入相反的顺序输出。\n\n## 【输入格式】\n\n两行。第一行一个整数 n；第二行 n 个用空格分隔的整数。\n\n## 【输出格式】\n\n一行，n 个整数，为原数组的逆序，用空格分隔。\n\n## 【样例】\n\n输入：\n\n```\n5\n1 2 3 4 5\n```\n\n输出：\n\n```\n5 4 3 2 1\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁵\n\n## 【提示】\n\n从后往前遍历即可，不必真的反转数组，空间 O(1)。', '两行。第一行一个整数 n；第二行 n 个用空格分隔的整数。', '一行，n 个整数，为原数组的逆序，用空格分隔。',
 '5\n1 2 3 4 5', '5 4 3 2 1', '从后往前遍历即可，不必真的反转数组，空间 O(1)。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nprint(" ".join(data[1:1 + n][::-1]))\n', 'python',
 '数组,入门,模拟', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '5\n1 2 3 4 5', '5 4 3 2 1\n', 1, 1),
(@aid, '17\n-45 -63 -6 99 39 -51 70 -100 -76 -53 -54 -18 -28 -3 4 3 57', '57 3 4 -3 -28 -18 -54 -53 -76 -100 70 -51 39 99 -6 -63 -45\n', 0, 2),
(@aid, '27\n-84 -93 -80 -57 -87 -39 -57 19 -28 26 -95 81 3 -52 81 -60 -41 6 -78 -15 -63 29 -30 -59 55 -4 -20', '-20 -4 55 -59 -30 29 -63 -15 -78 6 -41 -60 81 -52 3 81 -95 26 -28 19 -57 -39 -87 -57 -80 -93 -84\n', 0, 3),
(@aid, '18\n-50 -96 -69 95 42 -76 74 -54 85 -87 -2 37 -52 94 72 -58 -68 -79', '-79 -68 -58 72 94 -52 37 -2 -87 85 -54 74 -76 42 95 -69 -96 -50\n', 0, 4),
(@aid, '24\n83 89 -32 17 -66 89 98 49 98 11 -4 -20 48 95 -15 9 59 29 -79 -100 22 20 11 -81', '-81 11 20 22 -100 -79 29 59 9 -15 95 48 -20 -4 11 98 49 98 89 -66 17 -32 89 83\n', 0, 5),
(@aid, '22\n-16 -20 28 -21 4 55 -51 -83 -10 43 15 62 23 6 9 -76 -39 13 52 -75 79 -65', '-65 79 -75 52 13 -39 -76 9 6 23 62 15 43 -10 -83 -51 55 4 -21 28 -20 -16\n', 0, 6);

-- ---------- 20. 第二大不相同元素（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('第二大不相同元素', 2, 10, '## 【题目描述】\n\n输入 n 个整数，输出其中严格第二大的值（即小于最大值的最大的不同数值）。保证至少存在两个不同的数。\n\n## 【输入格式】\n\n两行。第一行一个整数 n；第二行 n 个用空格分隔的整数。\n\n## 【输出格式】\n\n一行，一个整数，表示严格第二大的值。\n\n## 【样例】\n\n输入：\n\n```\n5\n3 9 2 9 7\n```\n\n输出：\n\n```\n7\n```\n\n## 【数据范围】\n\n2 ≤ n ≤ 10⁵，保证至少有两个不同的数\n\n## 【提示】\n\n先去重再排序取第二项，或一趟扫描同时维护最大值与次大值（后者时间 O(n)、空间 O(1)）。', '两行。第一行一个整数 n；第二行 n 个用空格分隔的整数。', '一行，一个整数，表示严格第二大的值。',
 '5\n3 9 2 9 7', '7', '先去重再排序取第二项，或一趟扫描同时维护最大值与次大值（后者时间 O(n)、空间 O(1)）。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nnums = list(map(int, data[1:1 + n]))\nvals = sorted(set(nums), reverse=True)\nprint(vals[1])\n', 'python',
 '数组,最值,模拟', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '5\n3 9 2 9 7', '7\n', 1, 1),
(@aid, '18\n15 3 18 8 18 6 4 17 11 2 19 12 20 8 18 11 13 14', '19\n', 0, 2),
(@aid, '11\n18 9 13 9 7 7 10 12 8 12 3', '13\n', 0, 3),
(@aid, '30\n7 9 15 15 1 11 2 14 20 19 12 8 12 3 15 17 3 20 14 17 14 14 5 19 6 1 2 5 16 10', '19\n', 0, 4),
(@aid, '18\n10 17 13 4 20 16 13 5 9 4 12 13 16 5 7 11 1 19', '19\n', 0, 5),
(@aid, '29\n14 1 1 9 2 12 17 6 9 15 16 6 6 13 6 7 2 3 7 9 17 5 4 13 7 11 17 12 17', '16\n', 0, 6);

-- ---------- 21. 苹果与虫子（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('苹果与虫子', 2, 10, '## 【题目描述】\n\n有 n 个苹果，一条虫子每 x 小时吃掉一个苹果，经过 y 小时后还剩多少个完整的苹果（不足一个的不算完整）。\n\n## 【输入格式】\n\n一行，三个整数 n、x、y，分别表示苹果总数、吃完一个苹果所需小时数、经过的小时数。\n\n## 【输出格式】\n\n一行，一个整数，表示剩余完整苹果数（不能为负）。\n\n## 【样例】\n\n输入：\n\n```\n10 3 25\n```\n\n输出：\n\n```\n1\n```\n\n## 【数据范围】\n\n1 ≤ n, x ≤ 100，0 ≤ y ≤ 10⁴\n\n## 【提示】\n\n吃掉的苹果数是 ⌈y/x⌉，向上取整可写成 (y + x - 1) // x；剩余数不能小于 0。', '一行，三个整数 n、x、y，分别表示苹果总数、吃完一个苹果所需小时数、经过的小时数。', '一行，一个整数，表示剩余完整苹果数（不能为负）。',
 '10 3 25', '1', '吃掉的苹果数是 ⌈y/x⌉，向上取整可写成 (y + x - 1) // x；剩余数不能小于 0。', 'import sys\n\nn, x, y = map(int, sys.stdin.read().split())\neaten = (y + x - 1) // x\nprint(max(0, n - eaten))\n', 'python',
 '入门,模拟,数学', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '10 3 25', '1\n', 1, 1),
(@aid, '96 2 40', '76\n', 0, 2),
(@aid, '51 3 496', '0\n', 0, 3),
(@aid, '98 10 267', '71\n', 0, 4),
(@aid, '99 4 325', '17\n', 0, 5),
(@aid, '35 4 9', '32\n', 0, 6);

-- ---------- 22. 买铅笔（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('买铅笔', 2, 10, '## 【题目描述】\n\n老师需要买至少 n 支铅笔。商店有三种包装，第 i 种每包 aᵢ 支、售价 bᵢ 元（必须整包购买）。求最少需要花多少钱。\n\n## 【输入格式】\n\n第一行一个整数 n，表示需要的铅笔数。接下来三行，每行两个整数 aᵢ、bᵢ，表示第 i 种包装的支数与价格。\n\n## 【输出格式】\n\n一行，一个整数，表示最小花费。\n\n## 【样例】\n\n输入：\n\n```\n57\n2 2\n50 30\n30 27\n```\n\n输出：\n\n```\n54\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁴，1 ≤ aᵢ, bᵢ ≤ 10⁴\n\n## 【提示】\n\n对每种包装分别计算"买够 n 支需要几包"再乘价格，取三者最小值。买够的向上取整同理。', '第一行一个整数 n，表示需要的铅笔数。接下来三行，每行两个整数 aᵢ、bᵢ，表示第 i 种包装的支数与价格。', '一行，一个整数，表示最小花费。',
 '57\n2 2\n50 30\n30 27', '54', '对每种包装分别计算"买够 n 支需要几包"再乘价格，取三者最小值。买够的向上取整同理。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\npacks = [(int(data[1 + 2 * i]), int(data[2 + 2 * i])) for i in range(3)]\nans = min(((n + a - 1) // a) * b for a, b in packs)\nprint(ans)\n', 'python',
 '枚举,贪心,入门', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '57\n2 2\n50 30\n30 27', '54\n', 1, 1),
(@aid, '590\n64 99\n88 18\n1 75', '126\n', 0, 2),
(@aid, '407\n93 94\n80 96\n8 7', '357\n', 0, 3),
(@aid, '366\n30 59\n7 64\n82 64', '320\n', 0, 4),
(@aid, '432\n14 65\n85 27\n28 2', '32\n', 0, 5),
(@aid, '481\n56 88\n26 5\n6 70', '95\n', 0, 6);

-- ---------- 23. 能被 k 整除的数的个数（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('能被 k 整除的数的个数', 2, 10, '## 【题目描述】\n\n给定整数 n 和 k，求 1 到 n 之间（含端点）能被 k 整除的整数个数。\n\n## 【输入格式】\n\n一行，两个整数 n 和 k。\n\n## 【输出格式】\n\n一行，一个整数，表示个数。\n\n## 【样例】\n\n输入：\n\n```\n20 3\n```\n\n输出：\n\n```\n6\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁹，1 ≤ k ≤ 10⁴\n\n## 【提示】\n\n答案就是 ⌊n/k⌋，无需逐个枚举，O(1) 解决。', '一行，两个整数 n 和 k。', '一行，一个整数，表示个数。',
 '20 3', '6', '答案就是 ⌊n/k⌋，无需逐个枚举，O(1) 解决。', 'import sys\n\nn, k = map(int, sys.stdin.read().split())\nprint(n // k)\n', 'python',
 '数学,枚举,整除', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '20 3', '6\n', 1, 1),
(@aid, '762744 59', '12927\n', 0, 2),
(@aid, '771937 41', '18827\n', 0, 3),
(@aid, '976752 72', '13566\n', 0, 4),
(@aid, '384170 79', '4862\n', 0, 5),
(@aid, '275033 7', '39290\n', 0, 6);

-- ---------- 24. 分糖果（难度 1） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('分糖果', 1, 10, '## 【题目描述】\n\n有 n 颗糖果要平均分给 m 个小朋友，求每人分到几颗、还剩几颗。\n\n## 【输入格式】\n\n一行，两个整数 n 和 m。\n\n## 【输出格式】\n\n一行，两个整数，分别为每人分到的数量与剩余数量，用空格分隔。\n\n## 【样例】\n\n输入：\n\n```\n17 5\n```\n\n输出：\n\n```\n3 2\n```\n\n## 【数据范围】\n\n0 ≤ n ≤ 10⁶，1 ≤ m ≤ 10³\n\n## 【提示】\n\n整除与取余运算：每人 n // m 颗，剩余 n % m 颗。', '一行，两个整数 n 和 m。', '一行，两个整数，分别为每人分到的数量与剩余数量，用空格分隔。',
 '17 5', '3 2', '整除与取余运算：每人 n // m 颗，剩余 n % m 颗。', 'import sys\n\nn, m = map(int, sys.stdin.read().split())\nprint(n // m, n % m)\n', 'python',
 '入门,数学,整除', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '17 5', '3 2\n', 1, 1),
(@aid, '641 11', '58 3\n', 0, 2),
(@aid, '544 43', '12 28\n', 0, 3),
(@aid, '312 30', '10 12\n', 0, 4),
(@aid, '877 32', '27 13\n', 0, 5),
(@aid, '738 41', '18 0\n', 0, 6);

-- ---------- 25. 奇数与偶数分别求和（难度 1） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('奇数与偶数分别求和', 1, 10, '## 【题目描述】\n\n输入 n 个整数，分别求其中所有奇数之和与所有偶数之和。\n\n## 【输入格式】\n\n两行。第一行一个整数 n；第二行 n 个用空格分隔的整数。\n\n## 【输出格式】\n\n一行，两个整数，依次为奇数之和与偶数之和，用空格分隔。\n\n## 【样例】\n\n输入：\n\n```\n6\n1 2 3 4 5 6\n```\n\n输出：\n\n```\n9 12\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁵\n\n## 【提示】\n\n一趟扫描按 x % 2 分类累加即可。注意负数取余：Python 中 -3 % 2 == 1，也能正确归入奇数。', '两行。第一行一个整数 n；第二行 n 个用空格分隔的整数。', '一行，两个整数，依次为奇数之和与偶数之和，用空格分隔。',
 '6\n1 2 3 4 5 6', '9 12', '一趟扫描按 x % 2 分类累加即可。注意负数取余：Python 中 -3 % 2 == 1，也能正确归入奇数。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nodd = even = 0\nfor x in map(int, data[1:1 + n]):\n    if x % 2:\n        odd += x\n    else:\n        even += x\nprint(odd, even)\n', 'python',
 '入门,模拟,统计', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '6\n1 2 3 4 5 6', '9 12\n', 1, 1),
(@aid, '5\n91 -96 30 64 61', '152 -2\n', 0, 2),
(@aid, '2\n18 95', '95 18\n', 0, 3),
(@aid, '12\n-26 -78 50 -32 -25 -52 56 -3 -4 64 77 -22', '49 -44\n', 0, 4),
(@aid, '5\n-22 25 42 -58 92', '25 54\n', 0, 5),
(@aid, '19\n-22 2 32 95 -5 13 56 -68 80 75 69 49 23 88 -47 89 -4 31 -67', '325 164\n', 0, 6);

-- ---------- 26. 调和级数求和（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('调和级数求和', 2, 10, '## 【题目描述】\n\n已知调和级数 S(n) = 1 + 1/2 + 1/3 + … + 1/n。给定一个实数 k，求最小的 n，使得 S(n) > k。\n\n## 【输入格式】\n\n一行，一个实数 k。\n\n## 【输出格式】\n\n一行，一个整数 n，即满足 S(n) > k 的最小正整数。\n\n## 【样例】\n\n输入：\n\n```\n1.0\n```\n\n输出：\n\n```\n2\n```\n\n## 【数据范围】\n\n1 ≤ k ≤ 15\n\n## 【提示】\n\n从 n = 1 开始不断累加 1/n 直到和超过 k。注意用浮点累加，且循环条件是"不超过就继续加"。', '一行，一个实数 k。', '一行，一个整数 n，即满足 S(n) > k 的最小正整数。',
 '1.0', '2', '从 n = 1 开始不断累加 1/n 直到和超过 k。注意用浮点累加，且循环条件是"不超过就继续加"。', 'import sys\n\nk = float(sys.stdin.read().strip())\ns = 0.0\nn = 0\nwhile s <= k:\n    n += 1\n    s += 1.0 / n\nprint(n)\n', 'python',
 '模拟,数学,级数', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '1.0', '2\n', 1, 1),
(@aid, '5.0', '83\n', 0, 2),
(@aid, '2.0', '4\n', 0, 3),
(@aid, '10.0', '12367\n', 0, 4),
(@aid, '3.5', '19\n', 0, 5),
(@aid, '6.0', '227\n', 0, 6);

-- ---------- 27. 摘苹果（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('摘苹果', 2, 10, '## 【题目描述】\n\n树上有 10 个苹果，每个苹果的高度已知。陶陶身高 h 厘米，她站在 30 厘米高的板凳上，手能够到的最大高度为 h + 30。求她能摘到多少个苹果。\n\n## 【输入格式】\n\n两行。第一行 10 个整数，表示每个苹果的高度；第二行一个整数 h，表示陶陶的身高。\n\n## 【输出格式】\n\n一行，一个整数，表示能摘到的苹果数。\n\n## 【样例】\n\n输入：\n\n```\n100 200 150 140 129 134 167 198 200 111\n110\n```\n\n输出：\n\n```\n5\n```\n\n## 【数据范围】\n\n100 ≤ 苹果高度 ≤ 300，100 ≤ h ≤ 200\n\n## 【提示】\n\n逐个判断苹果高度是否不超过 h + 30 即可，遍历一遍统计计数。', '两行。第一行 10 个整数，表示每个苹果的高度；第二行一个整数 h，表示陶陶的身高。', '一行，一个整数，表示能摘到的苹果数。',
 '100 200 150 140 129 134 167 198 200 111\n110', '5', '逐个判断苹果高度是否不超过 h + 30 即可，遍历一遍统计计数。', 'import sys\n\ndata = sys.stdin.read().split()\napples = list(map(int, data[:10]))\nh = int(data[10])\nprint(sum(1 for a in apples if a <= h + 30))\n', 'python',
 '模拟,入门,统计', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '100 200 150 140 129 134 167 198 200 111\n110', '5\n', 1, 1),
(@aid, '244 151 194 224 199 168 193 107 114 195\n159', '4\n', 0, 2),
(@aid, '198 127 149 221 216 133 235 161 199 113\n198', '9\n', 0, 3),
(@aid, '146 145 163 181 244 130 150 203 107 209\n175', '8\n', 0, 4),
(@aid, '137 108 116 157 235 109 117 124 172 133\n81', '2\n', 0, 5),
(@aid, '171 102 188 239 223 198 238 139 225 217\n84', '1\n', 0, 6);

-- ---------- 28. 校门外的树（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('校门外的树', 2, 10, '## 【题目描述】\n\n一条长度为 L 的马路，从 0 到 L 每个整数点都有一棵树。现要砍掉 M 个区间内的树（区间端点含在内，可能重叠）。求砍完后还剩多少棵树。\n\n## 【输入格式】\n\n第一行两个整数 L、M；接下来 M 行，每行两个整数 l、r，表示一个要砍伐的区间。\n\n## 【输出格式】\n\n一行，一个整数，表示剩余树木数量。\n\n## 【样例】\n\n输入：\n\n```\n500 3\n150 300\n100 200\n470 471\n```\n\n输出：\n\n```\n298\n```\n\n## 【数据范围】\n\n1 ≤ L ≤ 10⁴，1 ≤ M ≤ 100\n\n## 【提示】\n\n用集合记录被砍掉的点可自动处理区间重叠；也可用差分数组，复杂度 O(L + M)。', '第一行两个整数 L、M；接下来 M 行，每行两个整数 l、r，表示一个要砍伐的区间。', '一行，一个整数，表示剩余树木数量。',
 '500 3\n150 300\n100 200\n470 471', '298', '用集合记录被砍掉的点可自动处理区间重叠；也可用差分数组，复杂度 O(L + M)。', 'import sys\n\ndata = sys.stdin.read().split()\nL = int(data[0])\nM = int(data[1])\nremoved = set()\nfor i in range(M):\n    l = int(data[2 + 2 * i])\n    rr = int(data[3 + 2 * i])\n    removed.update(range(l, rr + 1))\nprint(L + 1 - len(removed))\n', 'python',
 '模拟,区间,枚举', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '500 3\n150 300\n100 200\n470 471', '298\n', 1, 1),
(@aid, '121 7\n10 101\n7 26\n23 121\n9 62\n51 82\n22 67\n3 103', '3\n', 0, 2),
(@aid, '33 8\n11 33\n22 24\n3 30\n8 22\n18 28\n0 24\n13 22\n13 23', '0\n', 0, 3),
(@aid, '10 4\n2 3\n2 6\n4 9\n4 8', '3\n', 0, 4),
(@aid, '462 6\n176 378\n288 309\n145 200\n104 290\n143 428\n127 321', '138\n', 0, 5),
(@aid, '234 7\n19 125\n31 132\n38 60\n33 229\n78 209\n7 128\n149 157', '12\n', 0, 6);

-- ---------- 29. 阶乘求和（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('阶乘求和', 2, 10, '## 【题目描述】\n\n给定整数 n，求 S = 1! + 2! + … + n!。\n\n## 【输入格式】\n\n一行，一个整数 n。\n\n## 【输出格式】\n\n一行，一个整数，表示 S 的值。\n\n## 【样例】\n\n输入：\n\n```\n5\n```\n\n输出：\n\n```\n153\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 20\n\n## 【提示】\n\n边求阶乘边累加，不必每层重新计算：i! = (i-1)! × i，一趟循环即可。', '一行，一个整数 n。', '一行，一个整数，表示 S 的值。',
 '5', '153', '边求阶乘边累加，不必每层重新计算：i! = (i-1)! × i，一趟循环即可。', 'import sys\n\nn = int(sys.stdin.read().strip())\nfact = 1\nans = 0\nfor i in range(1, n + 1):\n    fact *= i\n    ans += fact\nprint(ans)\n', 'python',
 '数学,递推,阶乘', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '5', '153\n', 1, 1),
(@aid, '11', '43954713\n', 0, 2),
(@aid, '5', '153\n', 0, 3),
(@aid, '7', '5913\n', 0, 4),
(@aid, '9', '409113\n', 0, 5),
(@aid, '5', '153\n', 0, 6);

-- ---------- 30. 单词个数统计（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('单词个数统计', 2, 10, '## 【题目描述】\n\n输入一行英文句子，统计其中单词的个数。单词由连续的非空格字符组成。\n\n## 【输入格式】\n\n一行字符串 s，长度不超过 200，单词之间用一个或多个空格分隔。\n\n## 【输出格式】\n\n一行，一个整数，表示单词个数。\n\n## 【样例】\n\n输入：\n\n```\nHello   World  Python\n```\n\n输出：\n\n```\n3\n```\n\n## 【数据范围】\n\n1 ≤ |s| ≤ 200\n\n## 【提示】\n\n用 split() 默认按任意空白切分并自动忽略连续空格，比手写状态机简洁得多。', '一行字符串 s，长度不超过 200，单词之间用一个或多个空格分隔。', '一行，一个整数，表示单词个数。',
 'Hello   World  Python', '3', '用 split() 默认按任意空白切分并自动忽略连续空格，比手写状态机简洁得多。', 'import sys\n\ns = sys.stdin.read().rstrip("\\n")\nprint(len(s.split()))\n', 'python',
 '字符串,模拟,统计', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'Hello   World  Python', '3\n', 1, 1),
(@aid, 'afbe fedb cdf', '3\n', 0, 2),
(@aid, 'dc', '1\n', 0, 3),
(@aid, 'fceed b edfccb da ccacca aeeeaa', '6\n', 0, 4),
(@aid, 'e bd cbc cddb fbcbcd aeb dfecbc', '7\n', 0, 5),
(@aid, 'f bfe fedfac ebcbf bfcfb', '5\n', 0, 6);

-- ---------- 31. ISBN 号码校验（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('ISBN 号码校验', 3, 20, '## 【题目描述】\n\n国际标准书号 ISBN 由 9 位数字、1 位识别码和 3 个分隔符 "-" 组成，形如 "0-670-82162-4"。识别码计算方法：用前 9 位数字分别乘以 1 到 9，求和后对 11 取模；余数为 10 时识别码为 "X"，否则为余数本身。给定一串 ISBN，若识别码正确则输出 Right，否则输出修正后的完整 ISBN。\n\n## 【输入格式】\n\n一行，一个形如 "a-bbb-ccccc-d" 的 ISBN 字符串。\n\n## 【输出格式】\n\n若识别码正确，输出 Right；否则输出修正后的 ISBN 字符串。\n\n## 【样例】\n\n输入：\n\n```\n0-670-82162-0\n```\n\n输出：\n\n```\n0-670-82162-4\n```\n\n## 【数据范围】\n\n输入保证为标准 ISBN 格式\n\n## 【提示】\n\n去掉分隔符取出 10 位字符，前 9 位加权求和（权重 1~9）后 mod 11，注意余数 10 对应字母 X。', '一行，一个形如 "a-bbb-ccccc-d" 的 ISBN 字符串。', '若识别码正确，输出 Right；否则输出修正后的 ISBN 字符串。',
 '0-670-82162-0', '0-670-82162-4', '去掉分隔符取出 10 位字符，前 9 位加权求和（权重 1~9）后 mod 11，注意余数 10 对应字母 X。', 'import sys\n\ns = sys.stdin.read().strip()\ndigits = [c for c in s if c != "-"]\ntotal = sum(int(digits[i]) * (i + 1) for i in range(9))\nrem = total % 11\ncode = "X" if rem == 10 else str(rem)\nif digits[9] == code:\n    print("Right")\nelse:\n    print(s[:-1] + code)\n', 'python',
 '字符串,模拟,校验', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '0-670-82162-0', '0-670-82162-4\n', 1, 1),
(@aid, '9-823-40290-8', '9-823-40290-6\n', 0, 2),
(@aid, '3-539-41655-3', '3-539-41655-2\n', 0, 3),
(@aid, '0-025-62580-6', '0-025-62580-2\n', 0, 4),
(@aid, '8-387-89650-0', 'Right\n', 0, 5),
(@aid, '1-162-65376-0', 'Right\n', 0, 6);

-- ---------- 32. 乒乓球（11 分制与 21 分制）（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('乒乓球（11 分制与 21 分制）', 3, 20, '## 【题目描述】\n\n一场比赛中记录了一串得分序列，W 表示华华得分、L 表示对手得分、E 表示比赛结束。请分别按 11 分制与 21 分制统计每局的比分。规则：一方先达到 11（或 21）分且领先至少 2 分，该局结束；比赛结束（E）时也要输出当前未结束局的比分。\n\n## 【输入格式】\n\n一行字符串，由 W、L、E 组成，以 E 结尾。\n\n## 【输出格式】\n\n先输出若干行 11 分制的每局比分（形如 "11:0"），再输出一个空行，然后输出若干行 21 分制的每局比分。\n\n## 【样例】\n\n输入：\n\n```\nWWWWWWWWWWLLLLLLLLLLLWWWWWWWWWWLLLLLLLLLLLE\n```\n\n输出：\n\n```\n13:11\n7:11\n0:0\n\n20:22\n0:0\n```\n\n## 【数据范围】\n\n字符串长度 ≤ 10⁵\n\n## 【提示】\n\n按字符模拟得分，达到目标分且分差 ≥ 2 时结算一局并把比分清零；E 时把当前局（哪怕是 0:0）也输出。', '一行字符串，由 W、L、E 组成，以 E 结尾。', '先输出若干行 11 分制的每局比分（形如 "11:0"），再输出一个空行，然后输出若干行 21 分制的每局比分。',
 'WWWWWWWWWWLLLLLLLLLLLWWWWWWWWWWLLLLLLLLLLLE', '13:11\n7:11\n0:0\n\n20:22\n0:0', '按字符模拟得分，达到目标分且分差 ≥ 2 时结算一局并把比分清零；E 时把当前局（哪怕是 0:0）也输出。', 'import sys\n\ns = sys.stdin.read().strip()\n\n\ndef score(seq, target):\n    a = b = 0\n    out = []\n    for ch in seq:\n        if ch == "E":\n            break\n        if ch == "W":\n            a += 1\n        else:\n            b += 1\n        if (a >= target or b >= target) and abs(a - b) >= 2:\n            out.append("%d:%d" % (a, b))\n            a = b = 0\n    out.append("%d:%d" % (a, b))\n    return out\n\n\nfor part in (score(s, 11), score(s, 21)):\n    print("\\n".join(part))\n    print()\n', 'python',
 '模拟,字符串,洛谷经典', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'WWWWWWWWWWLLLLLLLLLLLWWWWWWWWWWLLLLLLLLLLLE', '13:11\n7:11\n0:0\n\n20:22\n0:0\n\n', 1, 1),
(@aid, 'WWWLWLWWWWLLLLLLWWWWLLLWWLWLLWWWWLWWLLWWLWLWLLWWWLE', '11:8\n11:9\n6:5\n\n21:15\n7:7\n\n', 0, 2),
(@aid, 'WLLLLLLLLLWWLWLWWWLLLWWWLWWWLLLWLLWWLWWLLLLLWWWLLWLWLLLWWLLWLLLWWLLWLLWWWWLE', '4:11\n11:9\n8:11\n10:11\n\n16:21\n17:21\n0:0\n\n', 0, 3),
(@aid, 'WWWWLWWLWWWLLWLWWLLE', '11:5\n1:2\n\n12:7\n\n', 0, 4),
(@aid, 'WWLLLLWLWWWWWWWWLWWLWWWLWWLLLWLE', '11:5\n8:7\n\n19:12\n\n', 0, 5),
(@aid, 'LLLLLWLLWLLWWLWWLWWLLLWLWWWWLWLWWLWWWWLWLWWWLWWWLWLLWWWLE', '6:11\n11:7\n11:4\n3:3\n\n21:19\n10:6\n\n', 0, 6);

-- ---------- 33. 某年某月的天数（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('某年某月的天数', 2, 10, '## 【题目描述】\n\n给定年份 y 和月份 m，输出该月的天数（需考虑闰年）。\n\n## 【输入格式】\n\n一行，两个整数 y、m，分别表示年份与月份。\n\n## 【输出格式】\n\n一行，一个整数，表示该月的天数。\n\n## 【样例】\n\n输入：\n\n```\n2000 2\n```\n\n输出：\n\n```\n29\n```\n\n## 【数据范围】\n\n1 ≤ y ≤ 10⁴，1 ≤ m ≤ 12\n\n## 【提示】\n\n先按平年查表，2 月再单独判断闰年：能被 400 整除，或能被 4 整除但不能被 100 整除。', '一行，两个整数 y、m，分别表示年份与月份。', '一行，一个整数，表示该月的天数。',
 '2000 2', '29', '先按平年查表，2 月再单独判断闰年：能被 400 整除，或能被 4 整除但不能被 100 整除。', 'import sys\n\ny, m = map(int, sys.stdin.read().split())\ndays = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]\nif m == 2 and (y % 400 == 0 or (y % 4 == 0 and y % 100 != 0)):\n    print(29)\nelse:\n    print(days[m - 1])\n', 'python',
 '模拟,日期,数学', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '2000 2', '29\n', 1, 1),
(@aid, '19 11', '30\n', 0, 2),
(@aid, '2889 7', '31\n', 0, 3),
(@aid, '1873 3', '31\n', 0, 4),
(@aid, '1450 7', '31\n', 0, 5),
(@aid, '2084 4', '30\n', 0, 6);

-- ---------- 34. 鸡兔同笼（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('鸡兔同笼', 2, 10, '## 【题目描述】\n\n已知笼子里共有 n 个头、m 只脚，求鸡和兔各有多少只；若无解则输出 No solution。\n\n## 【输入格式】\n\n一行，两个整数 n、m，分别表示头的总数与脚的总数。\n\n## 【输出格式】\n\n若有解，输出两个整数（鸡的数量与兔的数量），用空格分隔；否则输出 No solution。\n\n## 【样例】\n\n输入：\n\n```\n10 32\n```\n\n输出：\n\n```\n4 6\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁴，1 ≤ m ≤ 10⁴\n\n## 【提示】\n\n解方程：兔 = (m - 2n)/2，鸡 = n - 兔。要检查脚数为偶数、结果非负且为整数。', '一行，两个整数 n、m，分别表示头的总数与脚的总数。', '若有解，输出两个整数（鸡的数量与兔的数量），用空格分隔；否则输出 No solution。',
 '10 32', '4 6', '解方程：兔 = (m - 2n)/2，鸡 = n - 兔。要检查脚数为偶数、结果非负且为整数。', 'import sys\n\nn, m = map(int, sys.stdin.read().split())\n# 鸡 x 只，兔 y 只：x + y = n，2x + 4y = m\ny = (m - 2 * n) / 2\nx = n - y\nif m % 2 == 0 and y == int(y) and 0 <= y <= n:\n    print(int(x), int(y))\nelse:\n    print("No solution")\n', 'python',
 '数学,枚举,方程', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '10 32', '4 6\n', 1, 1),
(@aid, '36 59', 'No solution\n', 0, 2),
(@aid, '43 54', 'No solution\n', 0, 3),
(@aid, '47 97', 'No solution\n', 0, 4),
(@aid, '33 121', 'No solution\n', 0, 5),
(@aid, '26 185', 'No solution\n', 0, 6);

-- ---------- 35. 石头剪刀布（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('石头剪刀布', 2, 10, '## 【题目描述】\n\n两人玩石头剪刀布共 n 局，每局给出双方的手势（0 表示石头、1 表示剪刀、2 表示布）。石头胜剪刀、剪刀胜布、布胜石头。统计两人各胜多少局。\n\n## 【输入格式】\n\n第一行一个整数 n；接下来 n 行，每行两个整数 a、b，分别表示两人的手势。\n\n## 【输出格式】\n\n一行，两个整数，依次为第一个人与第二个人获胜的局数，用空格分隔。\n\n## 【样例】\n\n输入：\n\n```\n3\n0 1\n2 0\n1 1\n```\n\n输出：\n\n```\n2 0\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁴\n\n## 【提示】\n\n手势编号 0/1/2 成环：若 (a - b) % 3 == 1 则 a 输（即 b 胜），否则 a 胜；相等为平局。', '第一行一个整数 n；接下来 n 行，每行两个整数 a、b，分别表示两人的手势。', '一行，两个整数，依次为第一个人与第二个人获胜的局数，用空格分隔。',
 '3\n0 1\n2 0\n1 1', '2 0', '手势编号 0/1/2 成环：若 (a - b) % 3 == 1 则 a 输（即 b 胜），否则 a 胜；相等为平局。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nw1 = w2 = 0\nfor i in range(n):\n    a = int(data[1 + 2 * i])\n    b = int(data[2 + 2 * i])\n    if a == b:\n        continue\n    if (a - b) % 3 == 1:\n        w2 += 1\n    else:\n        w1 += 1\nprint(w1, w2)\n', 'python',
 '模拟,数学,博弈', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3\n0 1\n2 0\n1 1', '2 0\n', 1, 1),
(@aid, '17\n1 2\n2 2\n2 0\n2 0\n1 1\n0 0\n1 0\n2 2\n1 2\n0 0\n0 2\n0 0\n0 1\n0 1\n0 1\n0 1\n1 2', '9 2\n', 0, 2),
(@aid, '16\n1 2\n1 0\n0 0\n0 2\n2 1\n2 2\n1 1\n0 1\n1 1\n0 2\n0 1\n0 1\n0 0\n1 0\n0 1\n0 1', '6 5\n', 0, 3),
(@aid, '24\n2 1\n2 1\n2 1\n0 0\n0 1\n2 2\n2 2\n1 2\n2 1\n1 1\n0 1\n2 2\n0 2\n2 0\n1 2\n1 0\n1 1\n1 2\n1 2\n0 0\n2 1\n0 1\n1 0\n1 0', '8 9\n', 0, 4),
(@aid, '13\n1 2\n0 2\n0 1\n2 1\n0 2\n1 2\n2 1\n0 0\n1 2\n1 1\n2 2\n2 2\n0 1', '5 4\n', 0, 5),
(@aid, '1\n2 2', '0 0\n', 0, 6);

-- ---------- 36. 区间内的素数（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('区间内的素数', 2, 10, '## 【题目描述】\n\n给定两个整数 m、n，输出 [m, n] 区间内所有的素数。\n\n## 【输入格式】\n\n一行，两个整数 m、n。\n\n## 【输出格式】\n\n一行，若干个素数，按从小到大排列，用空格分隔；若不存在则输出 -1。\n\n## 【样例】\n\n输入：\n\n```\n10 30\n```\n\n输出：\n\n```\n11 13 17 19 23 29\n```\n\n## 【数据范围】\n\n1 ≤ m ≤ n ≤ 10⁴\n\n## 【提示】\n\n判断素数只需试除到 √x；若区间很大，用埃氏筛一次性筛出所有素数会快得多。', '一行，两个整数 m、n。', '一行，若干个素数，按从小到大排列，用空格分隔；若不存在则输出 -1。',
 '10 30', '11 13 17 19 23 29', '判断素数只需试除到 √x；若区间很大，用埃氏筛一次性筛出所有素数会快得多。', 'import sys\n\n\ndef is_prime(x):\n    if x < 2:\n        return False\n    i = 2\n    while i * i <= x:\n        if x % i == 0:\n            return False\n        i += 1\n    return True\n\n\nm, n = map(int, sys.stdin.read().split())\nans = [str(x) for x in range(m, n + 1) if is_prime(x)]\nprint(" ".join(ans) if ans else "-1")\n', 'python',
 '素数,枚举,数学', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '10 30', '11 13 17 19 23 29\n', 1, 1),
(@aid, '99 365', '101 103 107 109 113 127 131 137 139 149 151 157 163 167 173 179 181 191 193 197 199 211 223 227 229 233 239 241 251 257 263 269 271 277 281 283 293 307 311 313 317 331 337 347 349 353 359\n', 0, 2),
(@aid, '77 124', '79 83 89 97 101 103 107 109 113\n', 0, 3),
(@aid, '22 274', '23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89 97 101 103 107 109 113 127 131 137 139 149 151 157 163 167 173 179 181 191 193 197 199 211 223 227 229 233 239 241 251 257 263 269 271\n', 0, 4),
(@aid, '46 296', '47 53 59 61 67 71 73 79 83 89 97 101 103 107 109 113 127 131 137 139 149 151 157 163 167 173 179 181 191 193 197 199 211 223 227 229 233 239 241 251 257 263 269 271 277 281 283 293\n', 0, 5),
(@aid, '84 407', '89 97 101 103 107 109 113 127 131 137 139 149 151 157 163 167 173 179 181 191 193 197 199 211 223 227 229 233 239 241 251 257 263 269 271 277 281 283 293 307 311 313 317 331 337 347 349 353 359 367 373 379 383 389 397 401\n', 0, 6);

-- ---------- 37. 真因子之和（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('真因子之和', 2, 10, '## 【题目描述】\n\n给定正整数 n，求 n 的所有真因子（小于 n 的正因子）之和。\n\n## 【输入格式】\n\n一行，一个整数 n。\n\n## 【输出格式】\n\n一行，一个整数，表示真因子之和。\n\n## 【样例】\n\n输入：\n\n```\n28\n```\n\n输出：\n\n```\n28\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁶\n\n## 【提示】\n\n试除到 √n，成对加入因子 i 与 n/i；注意排除 n 本身，且 i == n/i 时只加一次。当结果等于 n 时 n 就是完全数（如 6、28）。', '一行，一个整数 n。', '一行，一个整数，表示真因子之和。',
 '28', '28', '试除到 √n，成对加入因子 i 与 n/i；注意排除 n 本身，且 i == n/i 时只加一次。当结果等于 n 时 n 就是完全数（如 6、28）。', 'import sys\n\nn = int(sys.stdin.read().strip())\nans = 0\ni = 1\nwhile i * i <= n:\n    if n % i == 0:\n        ans += i\n        j = n // i\n        if j != i and j != n:\n            ans += j\n    i += 1\nif n == 1:\n    ans = 0\nprint(ans)\n', 'python',
 '数学,枚举,因子', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '28', '28\n', 1, 1),
(@aid, '5333', '1\n', 0, 2),
(@aid, '4953', '2215\n', 0, 3),
(@aid, '8522', '4264\n', 0, 4),
(@aid, '1215', '969\n', 0, 5),
(@aid, '9254', '6634\n', 0, 6);

-- ---------- 38. 数字直角三角形（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('数字直角三角形', 2, 10, '## 【题目描述】\n\n给定整数 n，输出一个由数字组成的直角三角形图案：第 i 行（从 1 开始）输出从 1 到 i 的数字，每个数字之间无空格，左对齐。\n\n## 【输入格式】\n\n一行，一个整数 n。\n\n## 【输出格式】\n\nn 行，第 i 行为 1 到 i 依次排列的数字串。\n\n## 【样例】\n\n输入：\n\n```\n4\n```\n\n输出：\n\n```\n1\n12\n123\n1234\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 20\n\n## 【提示】\n\n双重循环：外层控制行号 i，内层输出 1..i。', '一行，一个整数 n。', 'n 行，第 i 行为 1 到 i 依次排列的数字串。',
 '4', '1\n12\n123\n1234', '双重循环：外层控制行号 i，内层输出 1..i。', 'import sys\n\nn = int(sys.stdin.read().strip())\nfor i in range(1, n + 1):\n    print("".join(str(j) for j in range(1, i + 1)))\n', 'python',
 '模拟,图形输出,循环', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '4', '1\n12\n123\n1234\n', 1, 1),
(@aid, '5', '1\n12\n123\n1234\n12345\n', 0, 2),
(@aid, '5', '1\n12\n123\n1234\n12345\n', 0, 3),
(@aid, '14', '1\n12\n123\n1234\n12345\n123456\n1234567\n12345678\n123456789\n12345678910\n1234567891011\n123456789101112\n12345678910111213\n1234567891011121314\n', 0, 4),
(@aid, '10', '1\n12\n123\n1234\n12345\n123456\n1234567\n12345678\n123456789\n12345678910\n', 0, 5),
(@aid, '14', '1\n12\n123\n1234\n12345\n123456\n1234567\n12345678\n123456789\n12345678910\n1234567891011\n123456789101112\n12345678910111213\n1234567891011121314\n', 0, 6);

-- ---------- 39. 螺旋方阵（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('螺旋方阵', 3, 20, '## 【题目描述】\n\n给定整数 n，按顺时针螺旋顺序把 1 到 n² 填入 n × n 的方阵并输出（每行数字用空格分隔）。\n\n## 【输入格式】\n\n一行，一个整数 n。\n\n## 【输出格式】\n\nn 行，每行 n 个整数，为螺旋方阵。\n\n## 【样例】\n\n输入：\n\n```\n4\n```\n\n输出：\n\n```\n1 2 3 4\n12 13 14 5\n11 16 15 6\n10 9 8 7\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 30\n\n## 【提示】\n\n维护上下左右四个边界，每填完一条边就收缩对应边界，直到边界交错为止。', '一行，一个整数 n。', 'n 行，每行 n 个整数，为螺旋方阵。',
 '4', '1 2 3 4\n12 13 14 5\n11 16 15 6\n10 9 8 7', '维护上下左右四个边界，每填完一条边就收缩对应边界，直到边界交错为止。', 'import sys\n\nn = int(sys.stdin.read().strip())\na = [[0] * n for _ in range(n)]\ntop, bottom, left, right = 0, n - 1, 0, n - 1\ncur = 1\nwhile top <= bottom and left <= right:\n    for j in range(left, right + 1):\n        a[top][j] = cur\n        cur += 1\n    top += 1\n    for i in range(top, bottom + 1):\n        a[i][right] = cur\n        cur += 1\n    right -= 1\n    if top <= bottom:\n        for j in range(right, left - 1, -1):\n            a[bottom][j] = cur\n            cur += 1\n        bottom -= 1\n    if left <= right:\n        for i in range(bottom, top - 1, -1):\n            a[i][left] = cur\n            cur += 1\n        left += 1\nfor row in a:\n    print(" ".join(map(str, row)))\n', 'python',
 '模拟,矩阵,螺旋', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '4', '1 2 3 4\n12 13 14 5\n11 16 15 6\n10 9 8 7\n', 1, 1),
(@aid, '2', '1 2\n4 3\n', 0, 2),
(@aid, '5', '1 2 3 4 5\n16 17 18 19 6\n15 24 25 20 7\n14 23 22 21 8\n13 12 11 10 9\n', 0, 3),
(@aid, '11', '1 2 3 4 5 6 7 8 9 10 11\n40 41 42 43 44 45 46 47 48 49 12\n39 72 73 74 75 76 77 78 79 50 13\n38 71 96 97 98 99 100 101 80 51 14\n37 70 95 112 113 114 115 102 81 52 15\n36 69 94 111 120 121 116 103 82 53 16\n35 68 93 110 119 118 117 104 83 54 17\n34 67 92 109 108 107 106 105 84 55 18\n33 66 91 90 89 88 87 86 85 56 19\n32 65 64 63 62 61 60 59 58 57 20\n31 30 29 28 27 26 25 24 23 22 21\n', 0, 4),
(@aid, '6', '1 2 3 4 5 6\n20 21 22 23 24 7\n19 32 33 34 25 8\n18 31 36 35 26 9\n17 30 29 28 27 10\n16 15 14 13 12 11\n', 0, 5),
(@aid, '7', '1 2 3 4 5 6 7\n24 25 26 27 28 29 8\n23 40 41 42 43 30 9\n22 39 48 49 44 31 10\n21 38 47 46 45 32 11\n20 37 36 35 34 33 12\n19 18 17 16 15 14 13\n', 0, 6);

-- ---------- 40. 杨辉三角（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('杨辉三角', 2, 10, '## 【题目描述】\n\n给定整数 n，输出杨辉三角的前 n 行。第 i 行（从 1 开始）有 i 个数，每个数等于上一行相邻两数之和，两端为 1。\n\n## 【输入格式】\n\n一行，一个整数 n。\n\n## 【输出格式】\n\nn 行，每行若干个整数，为杨辉三角的一行，用空格分隔。\n\n## 【样例】\n\n输入：\n\n```\n5\n```\n\n输出：\n\n```\n1\n1 1\n1 2 1\n1 3 3 1\n1 4 6 4 1\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 30\n\n## 【提示】\n\n用上一行滚动生成下一行，空间 O(n)；也可直接用组合数 C(i, j) 计算每一项。', '一行，一个整数 n。', 'n 行，每行若干个整数，为杨辉三角的一行，用空格分隔。',
 '5', '1\n1 1\n1 2 1\n1 3 3 1\n1 4 6 4 1', '用上一行滚动生成下一行，空间 O(n)；也可直接用组合数 C(i, j) 计算每一项。', 'import sys\n\nn = int(sys.stdin.read().strip())\nrow = [1]\nfor i in range(n):\n    print(" ".join(map(str, row)))\n    row = [1] + [row[j] + row[j + 1] for j in range(len(row) - 1)] + [1]\n', 'python',
 '数学,递推,组合', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '5', '1\n1 1\n1 2 1\n1 3 3 1\n1 4 6 4 1\n', 1, 1),
(@aid, '4', '1\n1 1\n1 2 1\n1 3 3 1\n', 0, 2),
(@aid, '3', '1\n1 1\n1 2 1\n', 0, 3),
(@aid, '8', '1\n1 1\n1 2 1\n1 3 3 1\n1 4 6 4 1\n1 5 10 10 5 1\n1 6 15 20 15 6 1\n1 7 21 35 35 21 7 1\n', 0, 4),
(@aid, '14', '1\n1 1\n1 2 1\n1 3 3 1\n1 4 6 4 1\n1 5 10 10 5 1\n1 6 15 20 15 6 1\n1 7 21 35 35 21 7 1\n1 8 28 56 70 56 28 8 1\n1 9 36 84 126 126 84 36 9 1\n1 10 45 120 210 252 210 120 45 10 1\n1 11 55 165 330 462 462 330 165 55 11 1\n1 12 66 220 495 792 924 792 495 220 66 12 1\n1 13 78 286 715 1287 1716 1716 1287 715 286 78 13 1\n', 0, 5),
(@aid, '4', '1\n1 1\n1 2 1\n1 3 3 1\n', 0, 6);

-- ---------- 41. 约瑟夫问题（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('约瑟夫问题', 3, 20, '## 【题目描述】\n\nn 个人围成一圈，从第 1 个人开始报数，报到 m 的人出圈，然后从下一个人重新从 1 开始报数，直到所有人出圈。求出圈的顺序。\n\n## 【输入格式】\n\n一行，两个整数 n、m。\n\n## 【输出格式】\n\n一行，n 个整数，依次为出圈人的原始编号，用空格分隔。\n\n## 【样例】\n\n输入：\n\n```\n7 3\n```\n\n输出：\n\n```\n3 6 2 7 5 1 4\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10³，1 ≤ m ≤ 10³\n\n## 【提示】\n\n用列表模拟圈：每轮计算要删除的下标 (idx + m - 1) % 剩余人数，弹出并记录，复杂度 O(n²)，n 较小时够用。', '一行，两个整数 n、m。', '一行，n 个整数，依次为出圈人的原始编号，用空格分隔。',
 '7 3', '3 6 2 7 5 1 4', '用列表模拟圈：每轮计算要删除的下标 (idx + m - 1) % 剩余人数，弹出并记录，复杂度 O(n²)，n 较小时够用。', 'import sys\n\nn, m = map(int, sys.stdin.read().split())\npeople = list(range(1, n + 1))\nidx = 0\nans = []\nwhile people:\n    idx = (idx + m - 1) % len(people)\n    ans.append(people.pop(idx))\nprint(" ".join(map(str, ans)))\n', 'python',
 '模拟,约瑟夫,队列', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '7 3', '3 6 2 7 5 1 4\n', 1, 1),
(@aid, '46 3', '3 6 9 12 15 18 21 24 27 30 33 36 39 42 45 2 7 11 16 20 25 29 34 38 43 1 8 14 22 28 35 41 4 13 23 32 44 10 26 40 17 37 19 5 31 46\n', 0, 2),
(@aid, '22 13', '13 4 18 10 3 20 15 11 8 7 9 14 19 2 17 12 16 1 5 6 21 22\n', 0, 3),
(@aid, '19 20', '1 3 6 10 15 4 13 7 19 18 5 12 9 14 11 8 17 16 2\n', 0, 4),
(@aid, '26 15', '15 4 20 10 1 19 12 6 26 23 21 18 22 25 5 11 24 13 8 9 17 16 7 3 14 2\n', 0, 5),
(@aid, '30 15', '15 30 16 2 19 6 24 12 3 23 14 8 1 27 25 22 26 29 7 13 28 17 10 11 21 20 9 5 18 4\n', 0, 6);

-- ---------- 42. 行李托运费用（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('行李托运费用', 2, 10, '## 【题目描述】\n\n行李托运收费标准：重量不超过 10 千克收费 0 元；超过 10 千克但不超过 20 千克，超出部分每千克 5 元；超过 20 千克，超出 20 千克的部分每千克 10 元（前 10 千克超出部分仍按 5 元计）。给定重量 w（整数千克），求费用。\n\n## 【输入格式】\n\n一行，一个整数 w，表示行李重量（千克）。\n\n## 【输出格式】\n\n一行，一个整数，表示托运费用。\n\n## 【样例】\n\n输入：\n\n```\n25\n```\n\n输出：\n\n```\n100\n```\n\n## 【数据范围】\n\n0 ≤ w ≤ 10⁴\n\n## 【提示】\n\n分段计费：先算 10~20 千克区间的 5 元/千克，再算 20 千克以上的 10 元/千克。', '一行，一个整数 w，表示行李重量（千克）。', '一行，一个整数，表示托运费用。',
 '25', '100', '分段计费：先算 10~20 千克区间的 5 元/千克，再算 20 千克以上的 10 元/千克。', 'import sys\n\nw = int(sys.stdin.read().strip())\nif w <= 10:\n    print(0)\nelif w <= 20:\n    print((w - 10) * 5)\nelse:\n    print(10 * 5 + (w - 20) * 10)\n', 'python',
 '模拟,分段,数学', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '25', '100\n', 1, 1),
(@aid, '51', '360\n', 0, 2),
(@aid, '41', '260\n', 0, 3),
(@aid, '75', '600\n', 0, 4),
(@aid, '95', '800\n', 0, 5),
(@aid, '61', '460\n', 0, 6);

-- ---------- 43. 时间加法（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('时间加法', 2, 10, '## 【题目描述】\n\n给定两个时刻（时、分、秒），求它们相加后的时刻（超过 24 小时从 0 重新开始）。\n\n## 【输入格式】\n\n两行，每行三个整数 h、m、s，表示一个时刻。\n\n## 【输出格式】\n\n一行，三个整数，为相加后的时、分、秒，用空格分隔。\n\n## 【样例】\n\n输入：\n\n```\n23 59 59\n0 0 2\n```\n\n输出：\n\n```\n0 0 1\n```\n\n## 【数据范围】\n\n0 ≤ h ≤ 23，0 ≤ m, s ≤ 59\n\n## 【提示】\n\n统一换算成秒相加，再对 86400（一天的总秒数）取模，最后拆分回时分秒，可避免复杂的进位讨论。', '两行，每行三个整数 h、m、s，表示一个时刻。', '一行，三个整数，为相加后的时、分、秒，用空格分隔。',
 '23 59 59\n0 0 2', '0 0 1', '统一换算成秒相加，再对 86400（一天的总秒数）取模，最后拆分回时分秒，可避免复杂的进位讨论。', 'import sys\n\ndata = list(map(int, sys.stdin.read().split()))\nt1 = data[0] * 3600 + data[1] * 60 + data[2]\nt2 = data[3] * 3600 + data[4] * 60 + data[5]\nt = (t1 + t2) % (24 * 3600)\nprint(t // 3600, t % 3600 // 60, t % 60)\n', 'python',
 '模拟,时间,数学', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '23 59 59\n0 0 2', '0 0 1\n', 1, 1),
(@aid, '11 40 24\n7 23 26', '19 3 50\n', 0, 2),
(@aid, '20 19 14\n16 37 6', '12 56 20\n', 0, 3),
(@aid, '23 11 32\n5 40 2', '4 51 34\n', 0, 4),
(@aid, '15 28 58\n5 39 40', '21 8 38\n', 0, 5),
(@aid, '15 42 4\n15 21 11', '7 3 15\n', 0, 6);

-- ---------- 44. 十六进制转十进制（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('十六进制转十进制', 2, 10, '## 【题目描述】\n\n给定一个十六进制正整数（只含数字与大写字母 A~F），输出其对应的十进制值。\n\n## 【输入格式】\n\n一行，一个十六进制字符串 s，长度不超过 8。\n\n## 【输出格式】\n\n一行，一个整数，表示十进制值。\n\n## 【样例】\n\n输入：\n\n```\n1A3F\n```\n\n输出：\n\n```\n6719\n```\n\n## 【数据范围】\n\n1 ≤ |s| ≤ 8\n\n## 【提示】\n\n按位加权：从高位到低位 ans = ans × 16 + 本位数码值；Python 可直接用 int(s, 16)。', '一行，一个十六进制字符串 s，长度不超过 8。', '一行，一个整数，表示十进制值。',
 '1A3F', '6719', '按位加权：从高位到低位 ans = ans × 16 + 本位数码值；Python 可直接用 int(s, 16)。', 'import sys\n\ns = sys.stdin.read().strip()\nprint(int(s, 16))\n', 'python',
 '进制转换,数学,字符串', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '1A3F', '6719\n', 1, 1),
(@aid, '2B39C4', '2832836\n', 0, 2),
(@aid, 'A53BFB', '10828795\n', 0, 3),
(@aid, '644586', '6571398\n', 0, 4),
(@aid, 'DB56D6', '14374614\n', 0, 5),
(@aid, '8EF2DA', '9368282\n', 0, 6);

-- ---------- 45. 成绩统计（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('成绩统计', 2, 10, '## 【题目描述】\n\n输入 n 个学生的百分制成绩，求平均分（保留 1 位小数）与及格率（成绩 ≥ 60 的比例，以百分数表示，保留 1 位小数）。\n\n## 【输入格式】\n\n两行。第一行一个整数 n；第二行 n 个整数，表示成绩。\n\n## 【输出格式】\n\n一行，两个值：平均分与及格百分数（不含 % 号，保留 1 位小数），用空格分隔。\n\n## 【样例】\n\n输入：\n\n```\n5\n50 60 70 80 90\n```\n\n输出：\n\n```\n70.0 80.0\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁵，0 ≤ 成绩 ≤ 100\n\n## 【提示】\n\n一次遍历求和与计数，最后格式化输出；注意整除要用浮点除法。', '两行。第一行一个整数 n；第二行 n 个整数，表示成绩。', '一行，两个值：平均分与及格百分数（不含 % 号，保留 1 位小数），用空格分隔。',
 '5\n50 60 70 80 90', '70.0 80.0', '一次遍历求和与计数，最后格式化输出；注意整除要用浮点除法。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nsc = list(map(int, data[1:1 + n]))\navg = sum(sc) / n\nrate = sum(1 for x in sc if x >= 60) / n * 100\nprint("%.1f %.1f" % (avg, rate))\n', 'python',
 '模拟,统计,数学', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '5\n50 60 70 80 90', '70.0 80.0\n', 1, 1),
(@aid, '13\n44 60 22 86 43 15 1 15 78 88 95 70 67', '52.6 53.8\n', 0, 2),
(@aid, '37\n44 55 53 0 54 28 94 51 22 93 77 24 88 87 41 29 7 16 89 100 81 25 41 20 100 83 98 22 20 11 76 87 19 89 22 64 39', '52.7 40.5\n', 0, 3),
(@aid, '37\n44 50 80 79 36 12 26 70 6 14 88 16 12 73 56 21 90 84 9 19 50 32 8 13 24 88 87 95 49 37 12 98 29 80 84 18 13', '46.0 35.1\n', 0, 4),
(@aid, '6\n54 84 32 72 26 87', '59.2 50.0\n', 0, 5),
(@aid, '9\n58 30 82 54 70 0 59 50 81', '53.8 33.3\n', 0, 6);

-- ---------- 46. 数组去重并排序（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('数组去重并排序', 2, 10, '## 【题目描述】\n\n输入 n 个整数，去掉重复元素后按从小到大排序输出。\n\n## 【输入格式】\n\n两行。第一行一个整数 n；第二行 n 个整数。\n\n## 【输出格式】\n\n两行。第一行一个整数 m，表示去重后的个数；第二行 m 个整数，为排序去重后的结果，用空格分隔。\n\n## 【样例】\n\n输入：\n\n```\n6\n3 1 2 3 2 1\n```\n\n输出：\n\n```\n3\n1 2 3\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁵\n\n## 【提示】\n\n集合去重 + 排序，复杂度 O(n log n)；也可先排序再去重（相邻比较）。', '两行。第一行一个整数 n；第二行 n 个整数。', '两行。第一行一个整数 m，表示去重后的个数；第二行 m 个整数，为排序去重后的结果，用空格分隔。',
 '6\n3 1 2 3 2 1', '3\n1 2 3', '集合去重 + 排序，复杂度 O(n log n)；也可先排序再去重（相邻比较）。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nvals = sorted(set(map(int, data[1:1 + n])))\nprint(len(vals))\nprint(" ".join(map(str, vals)))\n', 'python',
 '排序,去重,数组', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '6\n3 1 2 3 2 1', '3\n1 2 3\n', 1, 1),
(@aid, '10\n55 66 -96 -40 91 -8 -66 68 -17 -36', '10\n-96 -66 -40 -36 -17 -8 55 66 68 91\n', 0, 2),
(@aid, '16\n12 29 85 -63 -14 -80 94 12 82 17 86 52 59 -86 -7 65', '15\n-86 -80 -63 -14 -7 12 17 29 52 59 65 82 85 86 94\n', 0, 3),
(@aid, '18\n-77 -60 14 70 -18 20 78 -13 91 21 40 -42 93 -71 -72 92 -5 53', '18\n-77 -72 -71 -60 -42 -18 -13 -5 14 20 21 40 53 70 78 91 92 93\n', 0, 4),
(@aid, '10\n71 -76 13 -16 73 40 23 21 -63 56', '10\n-76 -63 -16 13 21 23 40 56 71 73\n', 0, 5),
(@aid, '7\n11 -95 -23 38 59 43 -96', '7\n-96 -95 -23 11 38 43 59\n', 0, 6);

-- ---------- 47. 最长连续递增段（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('最长连续递增段', 2, 10, '## 【题目描述】\n\n输入 n 个整数，求其中最长的一段连续严格递增（后一个数严格大于前一个数）的子数组长度。\n\n## 【输入格式】\n\n两行。第一行一个整数 n；第二行 n 个整数。\n\n## 【输出格式】\n\n一行，一个整数，表示最长连续递增段的长度。\n\n## 【样例】\n\n输入：\n\n```\n7\n1 2 3 1 2 1 2\n```\n\n输出：\n\n```\n3\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁵\n\n## 【提示】\n\n一趟扫描维护"当前递增段长度"，遇到下降就重置为 1，同时更新最大值。', '两行。第一行一个整数 n；第二行 n 个整数。', '一行，一个整数，表示最长连续递增段的长度。',
 '7\n1 2 3 1 2 1 2', '3', '一趟扫描维护"当前递增段长度"，遇到下降就重置为 1，同时更新最大值。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nnums = list(map(int, data[1:1 + n]))\nbest = cur = 1\nfor i in range(1, n):\n    if nums[i] > nums[i - 1]:\n        cur += 1\n    else:\n        cur = 1\n    best = max(best, cur)\nprint(best)\n', 'python',
 '数组,枚举,统计', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '7\n1 2 3 1 2 1 2', '3\n', 1, 1),
(@aid, '21\n30 15 13 18 4 28 10 26 5 5 19 30 10 16 23 8 26 8 8 15 26', '3\n', 0, 2),
(@aid, '37\n29 7 8 19 13 13 27 22 18 26 15 4 16 10 27 4 17 21 24 24 23 21 9 30 28 27 1 4 14 14 30 18 11 4 5 21 20', '4\n', 0, 3),
(@aid, '17\n22 28 17 1 17 28 8 4 25 13 17 5 6 23 18 29 10', '3\n', 0, 4),
(@aid, '13\n7 12 13 29 28 25 24 10 1 19 21 16 18', '4\n', 0, 5),
(@aid, '25\n29 14 13 21 20 16 19 26 17 8 7 8 8 27 7 25 28 30 18 22 6 8 26 5 28', '4\n', 0, 6);

-- ---------- 48. 字符串游程压缩（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('字符串游程压缩', 3, 20, '## 【题目描述】\n\n给定一个字符串，将其按游程编码（Run-Length Encoding）压缩：连续相同的字符压缩为「字符 + 连续出现次数」，只输出出现次数大于 1 的组，其余字符原样输出。\n\n## 【输入格式】\n\n一行字符串 s，只含大小写字母，长度不超过 200。\n\n## 【输出格式】\n\n一行，压缩后的字符串。\n\n## 【样例】\n\n输入：\n\n```\naaabbcdddd\n```\n\n输出：\n\n```\na3b2cd4\n```\n\n## 【数据范围】\n\n1 ≤ |s| ≤ 200\n\n## 【提示】\n\n一趟扫描统计连续相同字符的段长，段长为 1 时不写数字。注意循环结束后要处理最后一段。', '一行字符串 s，只含大小写字母，长度不超过 200。', '一行，压缩后的字符串。',
 'aaabbcdddd', 'a3b2cd4', '一趟扫描统计连续相同字符的段长，段长为 1 时不写数字。注意循环结束后要处理最后一段。', 'import sys\n\ns = sys.stdin.read().strip()\nif not s:\n    print("")\nelse:\n    out = []\n    cur = s[0]\n    cnt = 1\n    for ch in s[1:]:\n        if ch == cur:\n            cnt += 1\n        else:\n            out.append(cur + (str(cnt) if cnt > 1 else ""))\n            cur = ch\n            cnt = 1\n    out.append(cur + (str(cnt) if cnt > 1 else ""))\n    print("".join(out))\n', 'python',
 '字符串,模拟,压缩', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'aaabbcdddd', 'a3b2cd4\n', 1, 1),
(@aid, 'dccbcdcaaaacbdaddaaabdadcbcaddb', 'dc2bcdca4cbdad2a3bdadcbcad2b\n', 0, 2),
(@aid, 'dcabdcdcbadaaabdabddddddbacbcadabacdac', 'dcabdcdcbada3bdabd6bacbcadabacdac\n', 0, 3),
(@aid, 'abcddacaddddadbca', 'abcd2acad4adbca\n', 0, 4),
(@aid, 'bdddcdcdaababaccbcadcbbcaccbbaccc', 'bd3cdcda2babac2bcadcb2cac2b2ac3\n', 0, 5),
(@aid, 'bda', 'bda\n', 0, 6);

-- ---------- 49. 大整数加法（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('大整数加法', 3, 20, '## 【题目描述】\n\n给定两个不超过 100 位的非负整数，求它们的和（结果可能超过任何整数类型的范围）。\n\n## 【输入格式】\n\n两行，每行一个非负整数，位数不超过 100，不含前导零（0 本身除外）。\n\n## 【输出格式】\n\n一行，一个整数，表示两数之和，不含前导零。\n\n## 【样例】\n\n输入：\n\n```\n12345678901234567890\n98765432109876543210\n```\n\n输出：\n\n```\n111111111011111111100\n```\n\n## 【数据范围】\n\n每个数位数 ≤ 100\n\n## 【提示】\n\n无法用内置整数类型时，把数字当字符串从低位逐位相加并处理进位，最后反转输出。', '两行，每行一个非负整数，位数不超过 100，不含前导零（0 本身除外）。', '一行，一个整数，表示两数之和，不含前导零。',
 '12345678901234567890\n98765432109876543210', '111111111011111111100', '无法用内置整数类型时，把数字当字符串从低位逐位相加并处理进位，最后反转输出。', 'import sys\n\ndata = sys.stdin.read().split()\na = data[0][::-1]\nb = data[1][::-1]\nres = []\ncarry = 0\nfor i in range(max(len(a), len(b))):\n    da = int(a[i]) if i < len(a) else 0\n    db = int(b[i]) if i < len(b) else 0\n    s = da + db + carry\n    res.append(str(s % 10))\n    carry = s // 10\nif carry:\n    res.append(str(carry))\nprint("".join(res[::-1]).lstrip("0") or "0")\n', 'python',
 '字符串,高精度,数学', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '12345678901234567890\n98765432109876543210', '111111111011111111100\n', 1, 1),
(@aid, '3062147877930802401397857650379472705056\n8685302214612257610124473953397080285282', '11747450092543060011522331603776552990338\n', 0, 2),
(@aid, '5038927360828528631672388029104488967572\n1393237225848795832733269861763181025959', '6432164586677324464405657890867669993531\n', 0, 3),
(@aid, '1145513762103266438371169225032665700018\n5184455459370378626806917478160856383256', '6329969221473645065178086703193522083274\n', 0, 4),
(@aid, '563915226372505073772222690238345206788\n7581361047916257157534917708349580885233', '8145276274288762231307140398587926092021\n', 0, 5),
(@aid, '2450023038878329514558074230298757888652\n1870756276491489708298545538218431941852', '4320779315369819222856619768517189830504\n', 0, 6);

-- ---------- 50. 排序输出（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('排序输出', 2, 10, '## 【题目描述】\n\n输入 n 个整数，按从小到大排序后输出。\n\n## 【输入格式】\n\n两行。第一行一个整数 n；第二行 n 个整数。\n\n## 【输出格式】\n\n一行，n 个整数，为排序结果，用空格分隔。\n\n## 【样例】\n\n输入：\n\n```\n5\n3 1 4 1 5\n```\n\n输出：\n\n```\n1 1 3 4 5\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁵\n\n## 【提示】\n\n直接使用内置排序（Timsort / 快排）即可，平均复杂度 O(n log n)。', '两行。第一行一个整数 n；第二行 n 个整数。', '一行，n 个整数，为排序结果，用空格分隔。',
 '5\n3 1 4 1 5', '1 1 3 4 5', '直接使用内置排序（Timsort / 快排）即可，平均复杂度 O(n log n)。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nnums = list(map(int, data[1:1 + n]))\nnums.sort()\nprint(" ".join(map(str, nums)))\n', 'python',
 '排序,入门', '洛谷', 6);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '5\n3 1 4 1 5', '1 1 3 4 5\n', 1, 1),
(@aid, '2\n6357 6287', '6287 6357\n', 0, 2),
(@aid, '16\n8588 1606 237 5189 6114 6013 6044 4658 8635 6060 2902 1033 7641 1604 2190 9381', '237 1033 1604 1606 2190 2902 4658 5189 6013 6044 6060 6114 7641 8588 8635 9381\n', 0, 3),
(@aid, '14\n8485 5143 5936 7179 4525 -199 1356 -255 9837 4887 4545 356 9623 6987', '-255 -199 356 1356 4525 4545 4887 5143 5936 6987 7179 8485 9623 9837\n', 0, 4),
(@aid, '11\n9729 6915 7775 770 -609 3121 9137 2363 4919 2689 5140', '-609 770 2363 2689 3121 4919 5140 6915 7775 9137 9729\n', 0, 5),
(@aid, '3\n188 3820 9098', '188 3820 9098\n', 0, 6);

-- ---------- 51. 第 k 小的数（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('第 k 小的数', 2, 10, '## 【题目描述】\n\n输入 n 个整数与一个整数 k，输出其中第 k 小的数（k 从 1 开始计数，重复元素分别计数）。\n\n## 【输入格式】\n\n两行。第一行两个整数 n、k；第二行 n 个整数。\n\n## 【输出格式】\n\n一行，一个整数，表示第 k 小的数。\n\n## 【样例】\n\n输入：\n\n```\n5 3\n3 1 4 1 5\n```\n\n输出：\n\n```\n3\n```\n\n## 【数据范围】\n\n1 ≤ k ≤ n ≤ 10⁵\n\n## 【提示】\n\n排序后直接取下标 k-1，O(n log n)；若只需 Top-K，可用堆或快速选择做到 O(n log k)。', '两行。第一行两个整数 n、k；第二行 n 个整数。', '一行，一个整数，表示第 k 小的数。',
 '5 3\n3 1 4 1 5', '3', '排序后直接取下标 k-1，O(n log n)；若只需 Top-K，可用堆或快速选择做到 O(n log k)。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nk = int(data[1])\nnums = sorted(map(int, data[2:2 + n]))\nprint(nums[k - 1])\n', 'python',
 '排序,选择问题', '洛谷', 6);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '5 3\n3 1 4 1 5', '3\n', 1, 1),
(@aid, '12 6\n561 395 140 78 890 431 138 973 337 228 498 543', '395\n', 0, 2),
(@aid, '12 1\n892 825 710 173 724 720 115 653 276 296 850 196', '115\n', 0, 3),
(@aid, '29 25\n499 255 124 87 66 758 967 260 649 963 739 951 603 288 337 68 718 840 612 399 680 534 105 457 369 345 666 755 343', '758\n', 0, 4),
(@aid, '31 9\n587 764 535 466 926 182 722 263 783 619 280 372 971 942 535 258 730 852 708 998 462 48 393 629 809 405 851 697 815 86 927', '405\n', 0, 5),
(@aid, '36 10\n13 127 95 293 776 783 289 419 369 876 523 266 423 574 397 334 670 637 328 96 52 995 470 997 335 961 841 118 482 375 977 884 602 529 747 341', '328\n', 0, 6);

-- ---------- 52. 逆序对个数（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('逆序对个数', 3, 20, '## 【题目描述】\n\n给定一个长度为 n 的序列，求其中逆序对的个数。逆序对指满足 i < j 且 a[i] > a[j] 的数对。\n\n## 【输入格式】\n\n两行。第一行一个整数 n；第二行 n 个整数。\n\n## 【输出格式】\n\n一行，一个整数，表示逆序对个数。\n\n## 【样例】\n\n输入：\n\n```\n5\n3 1 4 1 5\n```\n\n输出：\n\n```\n3\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁵\n\n## 【提示】\n\n归并排序时，右侧元素被选中说明它与左侧剩余的所有元素都构成逆序对，因此一次累加 len(left) - i。也可用树状数组 + 离散化求解。', '两行。第一行一个整数 n；第二行 n 个整数。', '一行，一个整数，表示逆序对个数。',
 '5\n3 1 4 1 5', '3', '归并排序时，右侧元素被选中说明它与左侧剩余的所有元素都构成逆序对，因此一次累加 len(left) - i。也可用树状数组 + 离散化求解。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nnums = list(map(int, data[1:1 + n]))\n\n\ndef merge_sort(a):\n    if len(a) <= 1:\n        return a, 0\n    mid = len(a) // 2\n    left, c1 = merge_sort(a[:mid])\n    right, c2 = merge_sort(a[mid:])\n    merged = []\n    i = j = 0\n    cnt = c1 + c2\n    while i < len(left) and j < len(right):\n        if left[i] <= right[j]:\n            merged.append(left[i])\n            i += 1\n        else:\n            merged.append(right[j])\n            cnt += len(left) - i\n            j += 1\n    merged.extend(left[i:])\n    merged.extend(right[j:])\n    return merged, cnt\n\n\nprint(merge_sort(nums)[1])\n', 'python',
 '排序,归并,分治,逆序对', '洛谷', 7);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '5\n3 1 4 1 5', '3\n', 1, 1),
(@aid, '13\n-80 -366 -4 -145 -499 41 -958 -231 -171 -729 -457 -812 -651', '55\n', 0, 2),
(@aid, '6\n-386 -428 -518 -854 -923 -43', '10\n', 0, 3),
(@aid, '18\n-418 -732 -996 -693 -335 -974 85 -214 -163 -969 -109 -563 -226 -866 -788 22 -186 -117', '56\n', 0, 4),
(@aid, '9\n-938 -408 -523 -602 -452 -370 44 -535 -529', '14\n', 0, 5),
(@aid, '16\n-36 -717 -476 -454 -461 -619 -885 -784 89 85 -886 -456 -172 -302 -948 -735', '68\n', 0, 6);

-- ---------- 53. 有序数组的二分查找（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('有序数组的二分查找', 2, 10, '## 【题目描述】\n\n给定一个升序排列的 n 个整数和 q 次询问，每次询问一个整数 x 是否出现在数组中，若在则输出其首次出现的下标（从 1 开始），否则输出 -1。\n\n## 【输入格式】\n\n第一行两个整数 n、q；第二行 n 个升序整数；接下来 q 行，每行一个整数 x。\n\n## 【输出格式】\n\nq 行，每行一个整数，表示查找结果。\n\n## 【样例】\n\n输入：\n\n```\n6 3\n1 2 2 3 4 5\n2\n6\n1\n```\n\n输出：\n\n```\n2\n-1\n1\n```\n\n## 【数据范围】\n\n1 ≤ n, q ≤ 10⁵\n\n## 【提示】\n\n二分查找每次排除一半区间，复杂度 O(log n)；要找"首次出现"的位置应使用左边界二分（bisect_left）。', '第一行两个整数 n、q；第二行 n 个升序整数；接下来 q 行，每行一个整数 x。', 'q 行，每行一个整数，表示查找结果。',
 '6 3\n1 2 2 3 4 5\n2\n6\n1', '2\n-1\n1', '二分查找每次排除一半区间，复杂度 O(log n)；要找"首次出现"的位置应使用左边界二分（bisect_left）。', 'import sys\nimport bisect\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nq = int(data[1])\nnums = list(map(int, data[2:2 + n]))\nout = []\nfor i in range(q):\n    x = int(data[2 + n + i])\n    pos = bisect.bisect_left(nums, x)\n    out.append(str(pos + 1) if pos < n and nums[pos] == x else "-1")\nprint("\\n".join(out))\n', 'python',
 '二分,查找,数组', '洛谷', 40);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '6 3\n1 2 2 3 4 5\n2\n6\n1', '2\n-1\n1\n', 1, 1),
(@aid, '15 4\n6 10 11 14 17 19 21 29 30 31 40 42 44 47 50\n47\n53\n25\n9', '14\n-1\n-1\n-1\n', 0, 2),
(@aid, '12 2\n1 2 4 16 16 26 30 34 39 41 44 45\n53\n5', '-1\n-1\n', 0, 3),
(@aid, '10 3\n12 12 18 18 20 25 28 34 37 43\n38\n52\n12', '-1\n-1\n1\n', 0, 4),
(@aid, '28 4\n0 1 2 2 4 5 6 10 10 14 21 22 23 30 31 32 34 34 34 39 40 41 42 44 45 48 48 49\n20\n10\n27\n9', '-1\n8\n-1\n-1\n', 0, 5),
(@aid, '25 5\n0 3 12 12 14 15 15 17 17 17 17 18 19 20 26 27 27 33 35 36 37 44 46 47 50\n8\n35\n10\n38\n44', '-1\n19\n-1\n-1\n22\n', 0, 6);

-- ---------- 54. 木材加工（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('木材加工', 3, 20, '## 【题目描述】\n\n有 n 根原木，长度分别为 Lᵢ。现需要切出 k 段长度相同的小段（每段长度必须为整数），求小段的最大可能长度；若无法切出 k 段则输出 0。\n\n## 【输入格式】\n\n第一行两个整数 n、k；第二行 n 个整数，表示每根原木的长度。\n\n## 【输出格式】\n\n一行，一个整数，表示最大长度。\n\n## 【样例】\n\n输入：\n\n```\n3 7\n10 15 12\n```\n\n输出：\n\n```\n5\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁵，1 ≤ k ≤ 10⁸，1 ≤ Lᵢ ≤ 10⁸\n\n## 【提示】\n\n答案具有单调性：长度越小能切出的段数越多。对长度二分，判断"能否切出至少 k 段"，这是典型的二分答案模板。', '第一行两个整数 n、k；第二行 n 个整数，表示每根原木的长度。', '一行，一个整数，表示最大长度。',
 '3 7\n10 15 12', '5', '答案具有单调性：长度越小能切出的段数越多。对长度二分，判断"能否切出至少 k 段"，这是典型的二分答案模板。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nk = int(data[1])\nlogs = list(map(int, data[2:2 + n]))\nlo, hi = 0, max(logs)\nwhile lo < hi:\n    mid = (lo + hi + 1) // 2\n    if sum(L // mid for L in logs) >= k:\n        lo = mid\n    else:\n        hi = mid - 1\nprint(lo)\n', 'python',
 '二分答案,贪心,洛谷经典', '洛谷', 40);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3 7\n10 15 12', '5\n', 1, 1),
(@aid, '16 45\n44 120 44 118 48 134 64 29 103 197 91 23 104 139 73', '24\n', 0, 2),
(@aid, '7 50\n159 52 115 91', '8\n', 0, 3),
(@aid, '4 36\n164 67 131 2 194 122 90 34 122 151', '9\n', 0, 4),
(@aid, '19 44\n144 23 159 157 68 46 71 122 77 143 71 44 128 21 86 180 121 109 8', '35\n', 0, 5),
(@aid, '1 44\n28 199 19 73 33 184', '0\n', 0, 6);

-- ---------- 55. 跳石头（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('跳石头', 3, 20, '## 【题目描述】\n\n一条河上有 n 块石头，起点到终点的距离为 L，石头到起点的距离已知（单调递增）。现要移走最多 m 块石头，使得剩余相邻石头（含起点与终点）之间最小距离尽可能大。求这个最大化的最小距离。\n\n## 【输入格式】\n\n第一行三个整数 L、n、m；第二行 n 个整数，表示每块石头到起点的距离（递增）。\n\n## 【输出格式】\n\n一行，一个整数，表示最优的最小跳跃距离。\n\n## 【样例】\n\n输入：\n\n```\n25 5 2\n2 11 14 17 21\n```\n\n输出：\n\n```\n4\n```\n\n## 【数据范围】\n\n1 ≤ L ≤ 10⁹，1 ≤ n ≤ 5×10⁴，m ≤ n\n\n## 【提示】\n\n对"最小距离 d"二分：贪心地从左到右检查，若与上一块保留的石头距离小于 d 就移走当前石头，统计移走数量是否不超过 m。', '第一行三个整数 L、n、m；第二行 n 个整数，表示每块石头到起点的距离（递增）。', '一行，一个整数，表示最优的最小跳跃距离。',
 '25 5 2\n2 11 14 17 21', '4', '对"最小距离 d"二分：贪心地从左到右检查，若与上一块保留的石头距离小于 d 就移走当前石头，统计移走数量是否不超过 m。', 'import sys\n\ndata = sys.stdin.read().split()\nL = int(data[0])\nn = int(data[1])\nm = int(data[2])\nrocks = list(map(int, data[3:3 + n]))\n\n\ndef ok(d):\n    removed = 0\n    last = 0\n    for p in rocks:\n        if p - last < d:\n            removed += 1\n        else:\n            last = p\n    if L - last < d:\n        removed += 1\n    return removed <= m\n\n\nlo, hi = 0, L\nwhile lo < hi:\n    mid = (lo + hi + 1) // 2\n    if ok(mid):\n        lo = mid\n    else:\n        hi = mid - 1\nprint(lo)\n', 'python',
 '二分答案,贪心,洛谷经典', '洛谷', 40);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '25 5 2\n2 11 14 17 21', '4\n', 1, 1),
(@aid, '745 4 0\n180 193 451 580', '13\n', 0, 2),
(@aid, '448 3 1\n69 168 415', '69\n', 0, 3),
(@aid, '746 4 2\n103 225 266 435', '210\n', 0, 4),
(@aid, '251 15 3\n6 42 73 74 87 100 103 129 163 169 179 189 189 192 206', '3\n', 0, 5),
(@aid, '317 14 5\n124 137 147 151 159 175 180 213 217 236 271 289 310 316', '10\n', 0, 6);

-- ---------- 56. 一元三次方程求解（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('一元三次方程求解', 3, 20, '## 【题目描述】\n\n给定一元三次方程 ax³ + bx² + cx + d = 0 的四个整数系数，已知该方程在 [-100, 100] 内恰有三个不同实根，且任意两根之差的绝对值 ≥ 1。求这三个实根。\n\n## 【输入格式】\n\n一行，四个整数 a、b、c、d（a ≠ 0）。\n\n## 【输出格式】\n\n一行，三个实数，为三个根，从小到大排列，保留 2 位小数，用空格分隔。\n\n## 【样例】\n\n输入：\n\n```\n1 -6 11 -6\n```\n\n输出：\n\n```\n1.00 2.00 3.00\n```\n\n## 【数据范围】\n\n-100 ≤ 系数 ≤ 100，a ≠ 0\n\n## 【提示】\n\n先用步长 1 扫描找到根所在的区间（端点异号），再在区间内二分逼近；注意端点正好为根的情况要单独处理。', '一行，四个整数 a、b、c、d（a ≠ 0）。', '一行，三个实数，为三个根，从小到大排列，保留 2 位小数，用空格分隔。',
 '1 -6 11 -6', '1.00 2.00 3.00', '先用步长 1 扫描找到根所在的区间（端点异号），再在区间内二分逼近；注意端点正好为根的情况要单独处理。', 'import sys\n\na, b, c, d = map(int, sys.stdin.read().split())\n\n\ndef f(x):\n    return ((a * x + b) * x + c) * x + d\n\n\nroots = []\ni = -100\nwhile i <= 100:\n    if abs(f(i)) < 1e-7:\n        roots.append(float(i))\n    elif i < 100 and f(i) * f(i + 1) < 0:\n        lo, hi = float(i), float(i + 1)\n        for _ in range(80):\n            mid = (lo + hi) / 2\n            if f(lo) * f(mid) <= 0:\n                hi = mid\n            else:\n                lo = mid\n        roots.append((lo + hi) / 2)\n    i += 1\nroots.sort()\nprint(" ".join("%.2f" % x for x in roots[:3]))\n', 'python',
 '二分,数学,洛谷经典', '洛谷', 40);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '1 -6 11 -6', '1.00 2.00 3.00\n', 1, 1),
(@aid, '3 -99 1062 -3696', '8.00 11.00 14.00\n', 0, 2),
(@aid, '3 -18 -1125 5700', '-19.00 5.00 20.00\n', 0, 3),
(@aid, '2 -20 32 0', '0.00 2.00 8.00\n', 0, 4),
(@aid, '1 2 -65 150', '-10.00 3.00 5.00\n', 0, 5),
(@aid, '1 -17 38 56', '-1.00 4.00 14.00\n', 0, 6);

-- ---------- 57. 前缀和区间求和（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('前缀和区间求和', 2, 10, '## 【题目描述】\n\n给定一个长度为 n 的整数序列和 m 次询问，每次询问区间 [l, r] 的元素之和。\n\n## 【输入格式】\n\n第一行两个整数 n、m；第二行 n 个整数；接下来 m 行，每行两个整数 l、r。\n\n## 【输出格式】\n\nm 行，每行一个整数，表示对应区间的元素和。\n\n## 【样例】\n\n输入：\n\n```\n5 2\n1 2 3 4 5\n1 3\n2 5\n```\n\n输出：\n\n```\n6\n14\n```\n\n## 【数据范围】\n\n1 ≤ n, m ≤ 10⁵\n\n## 【提示】\n\n预处理前缀和 pre[i] = a₁ + … + aᵢ，则区间和为 pre[r] - pre[l-1]，每次询问 O(1)，总体 O(n + m)。', '第一行两个整数 n、m；第二行 n 个整数；接下来 m 行，每行两个整数 l、r。', 'm 行，每行一个整数，表示对应区间的元素和。',
 '5 2\n1 2 3 4 5\n1 3\n2 5', '6\n14', '预处理前缀和 pre[i] = a₁ + … + aᵢ，则区间和为 pre[r] - pre[l-1]，每次询问 O(1)，总体 O(n + m)。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nm = int(data[1])\nnums = list(map(int, data[2:2 + n]))\npre = [0]\nfor x in nums:\n    pre.append(pre[-1] + x)\nout = []\nfor i in range(m):\n    l = int(data[2 + n + 2 * i])\n    rr = int(data[3 + n + 2 * i])\n    out.append(str(pre[rr] - pre[l - 1]))\nprint("\\n".join(out))\n', 'python',
 '前缀和,数组,查询', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '5 2\n1 2 3 4 5\n1 3\n2 5', '6\n14\n', 1, 1),
(@aid, '2 1\n31 -31\n1 2', '0\n', 0, 2),
(@aid, '18 6\n-73 47 -79 0 -78 -63 32 7 90 21 -11 -99 -41 -35 -27 1 1 -67\n5 16\n11 14\n6 7\n8 10\n5 14\n6 8', '-203\n-186\n-31\n118\n-177\n-24\n', 0, 3),
(@aid, '6 5\n37 12 -13 40 -89 40\n6 6\n2 6\n4 5\n5 6\n3 6', '40\n-10\n-49\n-49\n-22\n', 0, 4),
(@aid, '24 7\n-57 44 93 -7 -15 83 -99 -30 -28 -68 -64 -47 -91 68 90 38 -32 -42 -73 -11 22 17 -47 67\n6 8\n9 17\n5 19\n7 17\n8 24\n2 3\n5 10', '-46\n-134\n-310\n-263\n-231\n137\n-157\n', 0, 5),
(@aid, '26 4\n81 -15 -36 20 23 -45 -85 12 78 -59 27 91 20 24 79 -6 100 40 -46 -12 63 88 36 -100 42 -60\n24 25\n9 24\n1 10\n22 24', '-58\n423\n-26\n24\n', 0, 6);

-- ---------- 58. 最大子段和（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('最大子段和', 2, 10, '## 【题目描述】\n\n给定一个长度为 n 的整数序列，求其连续子段的最大和（子段至少包含一个元素）。\n\n## 【输入格式】\n\n两行。第一行一个整数 n；第二行 n 个整数。\n\n## 【输出格式】\n\n一行，一个整数，表示最大子段和。\n\n## 【样例】\n\n输入：\n\n```\n7\n-2 11 -4 13 -5 -2 4\n```\n\n输出：\n\n```\n20\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁵\n\n## 【提示】\n\nKadane 算法：维护"以当前位置结尾的最大子段和"，状态转移 cur = max(x, cur + x)，一趟扫描 O(n)。', '两行。第一行一个整数 n；第二行 n 个整数。', '一行，一个整数，表示最大子段和。',
 '7\n-2 11 -4 13 -5 -2 4', '20', 'Kadane 算法：维护"以当前位置结尾的最大子段和"，状态转移 cur = max(x, cur + x)，一趟扫描 O(n)。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nnums = list(map(int, data[1:1 + n]))\nbest = cur = nums[0]\nfor x in nums[1:]:\n    cur = max(x, cur + x)\n    best = max(best, cur)\nprint(best)\n', 'python',
 '动态规划,前缀和,最大子段和', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '7\n-2 11 -4 13 -5 -2 4', '20\n', 1, 1),
(@aid, '4\n-299 -216 -226 -543', '-216\n', 0, 2),
(@aid, '3\n8 -878 -8', '8\n', 0, 3),
(@aid, '19\n-975 -613 -808 -881 -802 -430 -240 -560 -212 -913 -849 -972 -414 -992 -330 -898 -326 0 -393', '0\n', 0, 4),
(@aid, '2\n-809 -609', '-609\n', 0, 5),
(@aid, '5\n-682 -612 -821 -908 -664', '-612\n', 0, 6);

-- ---------- 59. 差分数组区间加法（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('差分数组区间加法', 2, 10, '## 【题目描述】\n\n给定一个长度为 n 的序列（初始全为 0）和 m 次操作，每次操作把区间 [l, r] 内的所有元素加上 v。求所有操作完成后的序列。\n\n## 【输入格式】\n\n第一行两个整数 n、m；接下来 m 行，每行三个整数 l、r、v。\n\n## 【输出格式】\n\n一行，n 个整数，为最终序列，用空格分隔。\n\n## 【样例】\n\n输入：\n\n```\n5 2\n1 3 2\n2 5 -1\n```\n\n输出：\n\n```\n2 1 1 -1 -1\n```\n\n## 【数据范围】\n\n1 ≤ n, m ≤ 10⁵\n\n## 【提示】\n\n区间加 [l, r] 只需 diff[l] += v、diff[r+1] -= v，最后做一次前缀和还原，整体 O(n + m)，比逐个元素加的 O(nm) 快得多。', '第一行两个整数 n、m；接下来 m 行，每行三个整数 l、r、v。', '一行，n 个整数，为最终序列，用空格分隔。',
 '5 2\n1 3 2\n2 5 -1', '2 1 1 -1 -1', '区间加 [l, r] 只需 diff[l] += v、diff[r+1] -= v，最后做一次前缀和还原，整体 O(n + m)，比逐个元素加的 O(nm) 快得多。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nm = int(data[1])\ndiff = [0] * (n + 2)\nfor i in range(m):\n    l = int(data[2 + 3 * i])\n    rr = int(data[3 + 3 * i])\n    v = int(data[4 + 3 * i])\n    diff[l] += v\n    diff[rr + 1] -= v\ncur = 0\nout = []\nfor i in range(1, n + 1):\n    cur += diff[i]\n    out.append(str(cur))\nprint(" ".join(out))\n', 'python',
 '差分,数组,区间操作', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '5 2\n1 3 2\n2 5 -1', '2 1 1 -1 -1\n', 1, 1),
(@aid, '9 5\n6 7 18\n2 9 1\n1 3 -8\n4 5 19\n1 4 8', '0 1 1 28 20 19 19 1 1\n', 0, 2),
(@aid, '11 1\n3 10 12', '0 0 12 12 12 12 12 12 12 12 0\n', 0, 3),
(@aid, '23 8\n16 21 6\n18 21 -15\n5 8 18\n3 16 -6\n9 11 -11\n7 18 -10\n11 12 -9\n2 5 2', '0 2 -4 -4 14 12 2 2 -27 -27 -36 -25 -16 -16 -16 -10 -4 -19 -9 -9 -9 0 0\n', 0, 4),
(@aid, '4 8\n1 1 -14\n1 4 -4\n1 2 3\n1 4 18\n4 4 4\n3 4 16\n1 3 -18\n1 2 -6', '-21 -7 12 34\n', 0, 5),
(@aid, '15 2\n1 13 14\n1 13 -19', '-5 -5 -5 -5 -5 -5 -5 -5 -5 -5 -5 -5 -5 0 0\n', 0, 6);

-- ---------- 60. 借教室（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('借教室', 3, 20, '## 【题目描述】\n\n有 n 天，第 i 天最多可借出 rᵢ 间教室。现有 m 份订单，第 j 份订单要在第 sⱼ 天到第 tⱼ 天每天借 dⱼ 间教室。请按订单顺序处理，输出第一份无法满足的订单编号；若全部满足则输出 0。\n\n## 【输入格式】\n\n第一行两个整数 n、m；第二行 n 个整数 rᵢ；接下来 m 行，每行三个整数 dⱼ、sⱼ、tⱼ。\n\n## 【输出格式】\n\n一行，一个整数，表示第一个无法满足的订单编号（全部满足输出 0）。\n\n## 【样例】\n\n输入：\n\n```\n4 3\n2 5 4 3\n2 1 3\n3 2 4\n4 2 4\n```\n\n输出：\n\n```\n2\n```\n\n## 【数据范围】\n\n1 ≤ n, m ≤ 10⁶（本题数据较小）\n\n## 【提示】\n\n"前 k 份订单是否都能满足"关于 k 单调，可二分订单数；每次判定用差分数组 O(n + k) 求出每天用量。', '第一行两个整数 n、m；第二行 n 个整数 rᵢ；接下来 m 行，每行三个整数 dⱼ、sⱼ、tⱼ。', '一行，一个整数，表示第一个无法满足的订单编号（全部满足输出 0）。',
 '4 3\n2 5 4 3\n2 1 3\n3 2 4\n4 2 4', '2', '"前 k 份订单是否都能满足"关于 k 单调，可二分订单数；每次判定用差分数组 O(n + k) 求出每天用量。', 'import sys\n\ndata = sys.stdin.read().split()\nidx = 0\nn = int(data[idx]); idx += 1\nm = int(data[idx]); idx += 1\nroom = list(map(int, data[idx:idx + n])); idx += n\norders = []\nfor _ in range(m):\n    d = int(data[idx]); s = int(data[idx + 1]); t = int(data[idx + 2]); idx += 3\n    orders.append((d, s, t))\n\n\ndef feasible(k):\n    diff = [0] * (n + 2)\n    for i in range(k):\n        d, s, t = orders[i]\n        diff[s] += d\n        diff[t + 1] -= d\n    used = 0\n    for i in range(1, n + 1):\n        used += diff[i]\n        if used > room[i - 1]:\n            return False\n    return True\n\n\nlo, hi = 0, m\nwhile lo < hi:\n    mid = (lo + hi + 1) // 2\n    if feasible(mid):\n        lo = mid\n    else:\n        hi = mid - 1\nprint(0 if lo == m else lo + 1)\n', 'python',
 '差分,二分答案,洛谷经典', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '4 3\n2 5 4 3\n2 1 3\n3 2 4\n4 2 4', '2\n', 1, 1),
(@aid, '11 7\n9 20 15 6 10 14 30 25 4 24 25\n10 6 8\n14 2 6\n17 6 10\n4 2 3\n9 5 8\n9 4 7\n2 2 4', '2\n', 0, 2),
(@aid, '19 10\n17 5 8 17 8 14 3 21 13 5 21 18 13 22 26 29 1 4 20\n14 2 7\n13 14 18\n12 5 8\n18 8 13\n13 1 3\n14 2 11\n14 16 19\n7 18 18\n3 2 8\n14 6 11', '1\n', 0, 3),
(@aid, '4 6\n24 8 16 30\n8 2 4\n13 2 3\n18 1 1\n3 3 3\n6 4 4\n6 4 4', '2\n', 0, 4),
(@aid, '16 6\n1 1 19 25 6 21 19 26 27 27 17 25 23 18 2 27\n4 4 6\n18 12 14\n16 9 12\n8 9 11\n15 7 9\n9 3 5', '3\n', 0, 5),
(@aid, '11 2\n24 11 27 18 16 30 9 9 19 12 19\n7 4 10\n2 2 11', '0\n', 0, 6);

-- ---------- 61. 二维前缀和（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('二维前缀和', 3, 20, '## 【题目描述】\n\n给定一个 n 行 m 列的矩阵和 q 次询问，每次询问以 (x₁, y₁) 为左上角、(x₂, y₂) 为右下角的子矩阵元素之和。\n\n## 【输入格式】\n\n第一行三个整数 n、m、q；接下来 n 行，每行 m 个整数；接下来 q 行，每行四个整数 x₁、y₁、x₂、y₂。\n\n## 【输出格式】\n\nq 行，每行一个整数，表示子矩阵之和。\n\n## 【样例】\n\n输入：\n\n```\n3 3 2\n1 2 3\n4 5 6\n7 8 9\n1 1 2 2\n1 1 3 3\n```\n\n输出：\n\n```\n12\n45\n```\n\n## 【数据范围】\n\n1 ≤ n, m ≤ 10³，1 ≤ q ≤ 10⁵\n\n## 【提示】\n\n二维前缀和：pre[i][j] = a[i][j] + pre[i-1][j] + pre[i][j-1] - pre[i-1][j-1]，查询用容斥原理 O(1)。', '第一行三个整数 n、m、q；接下来 n 行，每行 m 个整数；接下来 q 行，每行四个整数 x₁、y₁、x₂、y₂。', 'q 行，每行一个整数，表示子矩阵之和。',
 '3 3 2\n1 2 3\n4 5 6\n7 8 9\n1 1 2 2\n1 1 3 3', '12\n45', '二维前缀和：pre[i][j] = a[i][j] + pre[i-1][j] + pre[i][j-1] - pre[i-1][j-1]，查询用容斥原理 O(1)。', 'import sys\n\ndata = sys.stdin.read().split()\nidx = 0\nn = int(data[idx]); m = int(data[idx + 1]); q = int(data[idx + 2]); idx += 3\npre = [[0] * (m + 1) for _ in range(n + 1)]\nfor i in range(1, n + 1):\n    for j in range(1, m + 1):\n        v = int(data[idx]); idx += 1\n        pre[i][j] = v + pre[i - 1][j] + pre[i][j - 1] - pre[i - 1][j - 1]\nout = []\nfor _ in range(q):\n    x1 = int(data[idx]); y1 = int(data[idx + 1]); x2 = int(data[idx + 2]); y2 = int(data[idx + 3]); idx += 4\n    out.append(str(pre[x2][y2] - pre[x1 - 1][y2] - pre[x2][y1 - 1] + pre[x1 - 1][y1 - 1]))\nprint("\\n".join(out))\n', 'python',
 '前缀和,矩阵,查询', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3 3 2\n1 2 3\n4 5 6\n7 8 9\n1 1 2 2\n1 1 3 3', '12\n45\n', 1, 1),
(@aid, '5 2 5\n6 1\n17 15\n16 15\n12 8\n4 1\n3 1 4 1\n3 1 4 2\n1 2 2 2\n1 1 4 2\n3 1 4 2', '28\n51\n16\n90\n51\n', 0, 2),
(@aid, '5 4 2\n17 0 1 13\n4 20 19 8\n2 0 4 14\n0 7 19 12\n16 4 0 15\n1 3 1 3\n4 3 5 4', '1\n46\n', 0, 3),
(@aid, '3 3 5\n15 9 3\n18 16 18\n8 7 16\n1 2 1 3\n3 1 3 3\n1 1 3 3\n3 3 3 3\n1 2 2 3', '12\n31\n110\n16\n46\n', 0, 4),
(@aid, '4 8 5\n16 12 19 17 18 14 1 6\n3 7 6 3 12 1 11 6\n5 4 17 11 2 1 5 12\n18 17 13 15 13 17 9 1\n2 2 4 3\n1 3 2 7\n2 5 4 5\n1 1 4 6\n4 7 4 8', '64\n102\n27\n261\n10\n', 0, 5),
(@aid, '3 8 2\n10 11 18 1 5 19 18 5\n15 19 1 13 9 0 5 12\n4 0 15 5 18 3 15 4\n1 3 2 4\n2 6 3 7', '33\n23\n', 0, 6);

-- ---------- 62. 有序数组的两数之和（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('有序数组的两数之和', 2, 10, '## 【题目描述】\n\n给定升序排列的 n 个整数和一个目标值 t，判断是否存在两个不同位置的元素之和恰好等于 t。存在输出 Yes，否则输出 No。\n\n## 【输入格式】\n\n第一行两个整数 n、t；第二行 n 个升序整数。\n\n## 【输出格式】\n\n一行，Yes 或 No。\n\n## 【样例】\n\n输入：\n\n```\n5 9\n1 2 3 6 8\n```\n\n输出：\n\n```\nYes\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁵\n\n## 【提示】\n\n利用有序性用双指针：和偏小则左指针右移，偏大则右指针左移，一趟 O(n)，比哈希表的 O(n) 更省空间。', '第一行两个整数 n、t；第二行 n 个升序整数。', '一行，Yes 或 No。',
 '5 9\n1 2 3 6 8', 'Yes', '利用有序性用双指针：和偏小则左指针右移，偏大则右指针左移，一趟 O(n)，比哈希表的 O(n) 更省空间。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nt = int(data[1])\nnums = list(map(int, data[2:2 + n]))\ni, j = 0, n - 1\nok = False\nwhile i < j:\n    s = nums[i] + nums[j]\n    if s == t:\n        ok = True\n        break\n    elif s < t:\n        i += 1\n    else:\n        j -= 1\nprint("Yes" if ok else "No")\n', 'python',
 '双指针,数组,查找', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '5 9\n1 2 3 6 8', 'Yes\n', 1, 1),
(@aid, '22 55\n0 0 1 4 6 10 13 18 18 20 27 31 32 32 35 35 39 40 41 41 41 44', 'Yes\n', 0, 2),
(@aid, '9 39\n16 17 20 25 28 31 35 48 48', 'No\n', 0, 3),
(@aid, '27 79\n3 10 18 23 25 26 26 30 30 30 31 32 32 33 34 34 36 39 40 41 42 42 43 43 47 49 49', 'Yes\n', 0, 4),
(@aid, '5 24\n5 18 25 25 32', 'No\n', 0, 5),
(@aid, '19 39\n0 1 3 5 6 10 11 12 14 26 31 32 34 34 36 36 40 45 46', 'Yes\n', 0, 6);

-- ---------- 63. 盛最多水的容器（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('盛最多水的容器', 3, 20, '## 【题目描述】\n\n给定 n 个非负整数 a₁…aₙ，第 i 个数表示坐标 (i, aᵢ) 处有一块竖直挡板。求任意两块挡板与 x 轴构成的容器能容纳的最大水量（即 max(|i - j| × min(aᵢ, aⱼ))）。\n\n## 【输入格式】\n\n两行。第一行一个整数 n；第二行 n 个非负整数。\n\n## 【输出格式】\n\n一行，一个整数，表示最大水量。\n\n## 【样例】\n\n输入：\n\n```\n6\n1 3 5 2 4 6\n```\n\n输出：\n\n```\n15\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁵\n\n## 【提示】\n\n双指针从两端向中间收缩：每次移动较矮的那一侧（因为移动高的一侧不可能得到更优解），整体 O(n)。', '两行。第一行一个整数 n；第二行 n 个非负整数。', '一行，一个整数，表示最大水量。',
 '6\n1 3 5 2 4 6', '15', '双指针从两端向中间收缩：每次移动较矮的那一侧（因为移动高的一侧不可能得到更优解），整体 O(n)。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nnums = list(map(int, data[1:1 + n]))\ni, j = 0, n - 1\nbest = 0\nwhile i < j:\n    water = (j - i) * min(nums[i], nums[j])\n    best = max(best, water)\n    if nums[i] < nums[j]:\n        i += 1\n    else:\n        j -= 1\nprint(best)\n', 'python',
 '双指针,贪心,数组', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '6\n1 3 5 2 4 6', '15\n', 1, 1),
(@aid, '15\n-506 -192 -269 -668 -815 -563 -157 -365 -499 -516 -507 -465 -590 -381 -587', '0\n', 0, 2),
(@aid, '3\n-314 3 -5', '0\n', 0, 3),
(@aid, '4\n-437 -967 -231 -597', '0\n', 0, 4),
(@aid, '18\n-920 -570 -926 -641 -51 -648 -339 -445 -937 -599 -192 26 -153 -570 -828 -199 -528 -674', '0\n', 0, 5),
(@aid, '11\n-258 -491 -784 -830 -711 -800 -978 -682 -906 -627 -53', '0\n', 0, 6);

-- ---------- 64. 合并两个有序数组（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('合并两个有序数组', 2, 10, '## 【题目描述】\n\n给定两个升序排列的整数数组，将它们合并为一个升序数组并输出。\n\n## 【输入格式】\n\n第一行两个整数 n、m；第二行 n 个升序整数；第三行 m 个升序整数。\n\n## 【输出格式】\n\n一行，n + m 个整数，为合并后的升序数组，用空格分隔。\n\n## 【样例】\n\n输入：\n\n```\n3 4\n1 3 5\n2 4 6 8\n```\n\n输出：\n\n```\n1 2 3 4 5 6 8\n```\n\n## 【数据范围】\n\n1 ≤ n, m ≤ 10⁵\n\n## 【提示】\n\n二路归并：两个指针分别扫描两个数组，每次取较小者，O(n + m)。这与归并排序的合并步骤完全相同。', '第一行两个整数 n、m；第二行 n 个升序整数；第三行 m 个升序整数。', '一行，n + m 个整数，为合并后的升序数组，用空格分隔。',
 '3 4\n1 3 5\n2 4 6 8', '1 2 3 4 5 6 8', '二路归并：两个指针分别扫描两个数组，每次取较小者，O(n + m)。这与归并排序的合并步骤完全相同。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nm = int(data[1])\na = list(map(int, data[2:2 + n]))\nb = list(map(int, data[2 + n:2 + n + m]))\ni = j = 0\nout = []\nwhile i < n and j < m:\n    if a[i] <= b[j]:\n        out.append(a[i]); i += 1\n    else:\n        out.append(b[j]); j += 1\nout.extend(a[i:])\nout.extend(b[j:])\nprint(" ".join(map(str, out)))\n', 'python',
 '归并,双指针,数组', '洛谷', 7);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3 4\n1 3 5\n2 4 6 8', '1 2 3 4 5 6 8\n', 1, 1),
(@aid, '4 14\n12 29 36 55\n2 3 8 18 19 23 23 26 26 28 33 34 41 59', '2 3 8 12 18 19 23 23 26 26 28 29 33 34 36 41 55 59\n', 0, 2),
(@aid, '9 6\n2 4 13 28 29 36 39 40 56\n16 19 27 33 36 56', '2 4 13 16 19 27 28 29 33 36 36 39 40 56 56\n', 0, 3),
(@aid, '6 13\n13 20 41 45 59 60\n5 12 14 17 23 24 30 36 41 50 51 52 56', '5 12 13 14 17 20 23 24 30 36 41 41 45 50 51 52 56 59 60\n', 0, 4),
(@aid, '5 11\n25 40 48 50 54\n9 17 20 34 37 43 44 46 52 55 58', '9 17 20 25 34 37 40 43 44 46 48 50 52 54 55 58\n', 0, 5),
(@aid, '8 11\n21 23 24 28 29 30 44 56\n11 12 18 18 21 22 28 39 48 54 59', '11 12 18 18 21 21 22 23 24 28 28 29 30 39 44 48 54 56 59\n', 0, 6);

-- ---------- 65. 成绩排序（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('成绩排序', 2, 10, '## 【题目描述】\n\n给定 n 名学生的语文、数学、英语成绩与学号，按总分降序排序；总分相同时按语文成绩降序；仍相同时按学号升序。输出排序后的学号序列。\n\n## 【输入格式】\n\n第一行一个整数 n；接下来 n 行，每行四个整数：学号、语文、数学、英语。\n\n## 【输出格式】\n\n一行，n 个整数，为排序后的学号序列，用空格分隔。\n\n## 【样例】\n\n输入：\n\n```\n3\n1 90 80 70\n2 90 70 80\n3 80 90 90\n```\n\n输出：\n\n```\n3 1 2\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁵\n\n## 【提示】\n\n多关键字排序：把"降序"的键取负数即可用统一升序排序；Python 的 sort 默认按元组字典序比较。', '第一行一个整数 n；接下来 n 行，每行四个整数：学号、语文、数学、英语。', '一行，n 个整数，为排序后的学号序列，用空格分隔。',
 '3\n1 90 80 70\n2 90 70 80\n3 80 90 90', '3 1 2', '多关键字排序：把"降序"的键取负数即可用统一升序排序；Python 的 sort 默认按元组字典序比较。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nstus = []\nfor i in range(n):\n    sid, cn, ma, en = map(int, data[1 + 4 * i:5 + 4 * i])\n    stus.append((-(cn + ma + en), -cn, sid))\nstus.sort()\nprint(" ".join(str(s[2]) for s in stus))\n', 'python',
 '排序,多关键字', '洛谷', 6);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3\n1 90 80 70\n2 90 70 80\n3 80 90 90', '3 1 2\n', 1, 1),
(@aid, '19\n1 69 86 85\n2 62 85 84\n3 69 77 93\n4 59 54 84\n5 75 51 61\n6 83 66 66\n7 93 86 90\n8 83 68 60\n9 61 92 50\n10 99 52 85\n11 56 86 55\n12 73 73 92\n13 55 95 68\n14 90 61 69\n15 76 50 55\n16 97 98 77\n17 96 94 95\n18 84 93 83\n19 53 94 93', '17 16 7 18 1 19 3 12 10 2 14 13 6 8 9 4 11 5 15\n', 0, 2),
(@aid, '4\n1 83 89 88\n2 87 53 92\n3 71 55 64\n4 61 80 91', '1 2 4 3\n', 0, 3),
(@aid, '2\n1 74 52 84\n2 80 62 64', '1 2\n', 0, 4),
(@aid, '12\n1 95 96 96\n2 84 84 65\n3 79 69 84\n4 87 79 62\n5 100 66 74\n6 86 74 82\n7 58 59 90\n8 89 50 71\n9 98 96 91\n10 84 79 58\n11 86 60 97\n12 55 78 52', '1 9 11 6 5 2 3 4 10 8 7 12\n', 0, 5),
(@aid, '13\n1 69 81 66\n2 92 76 53\n3 89 59 64\n4 75 94 62\n5 54 81 59\n6 60 75 70\n7 62 70 56\n8 86 80 87\n9 58 73 73\n10 91 72 78\n11 62 81 90\n12 54 60 72\n13 88 66 80', '8 10 13 11 4 2 1 3 6 9 5 7 12\n', 0, 6);

-- ---------- 66. 第 k 大的数（快速选择）（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('第 k 大的数（快速选择）', 2, 10, '## 【题目描述】\n\n给定 n 个整数与整数 k，输出其中第 k 大的数（k 从 1 开始，重复元素分别计数）。要求不使用完整排序。\n\n## 【输入格式】\n\n两行。第一行两个整数 n、k；第二行 n 个整数。\n\n## 【输出格式】\n\n一行，一个整数，表示第 k 大的数。\n\n## 【样例】\n\n输入：\n\n```\n6 2\n3 1 5 2 5 4\n```\n\n输出：\n\n```\n5\n```\n\n## 【数据范围】\n\n1 ≤ k ≤ n ≤ 10⁵\n\n## 【提示】\n\n维护一个大小为 k 的小顶堆：堆顶就是第 k 大。复杂度 O(n log k)，比全排序的 O(n log n) 更省。', '两行。第一行两个整数 n、k；第二行 n 个整数。', '一行，一个整数，表示第 k 大的数。',
 '6 2\n3 1 5 2 5 4', '5', '维护一个大小为 k 的小顶堆：堆顶就是第 k 大。复杂度 O(n log k)，比全排序的 O(n log n) 更省。', 'import sys\nimport heapq\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nk = int(data[1])\nnums = list(map(int, data[2:2 + n]))\nheap = []\nfor x in nums:\n    if len(heap) < k:\n        heapq.heappush(heap, x)\n    elif x > heap[0]:\n        heapq.heapreplace(heap, x)\nprint(heap[0])\n', 'python',
 '堆,选择问题,TopK', '洛谷', 37);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '6 2\n3 1 5 2 5 4', '5\n', 1, 1),
(@aid, '39 15\n2 20 7 1 18 8 91 34 70 38 82 4 2 0 99 85 79 15 20 59 32 30 71 50 75 99 26 94 45 95 37 8 78 80 88 97 56 21 74', '71\n', 0, 2),
(@aid, '1 1\n19', '19\n', 0, 3),
(@aid, '1 1\n52', '52\n', 0, 4),
(@aid, '1 1\n34', '34\n', 0, 5),
(@aid, '23 22\n1 71 28 65 61 75 15 25 91 44 28 32 56 40 13 0 89 72 20 93 15 18 15', '1\n', 0, 6);

-- ---------- 67. 三分法求极值（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('三分法求极值', 3, 20, '## 【题目描述】\n\n给定实数 p、q 和区间 [l, r]，求函数 f(x) = (x - p)² + q 在该区间上的最小值，保留 4 位小数。要求使用三分查找求解。\n\n## 【输入格式】\n\n一行，四个实数 p、q、l、r。\n\n## 【输出格式】\n\n一行，一个实数，表示最小值，保留 4 位小数。\n\n## 【样例】\n\n输入：\n\n```\n0 3 -5 5\n```\n\n输出：\n\n```\n3.0000\n```\n\n## 【数据范围】\n\n-100 ≤ p, q, l, r ≤ 100，l < r\n\n## 【提示】\n\n单峰（单谷）函数可用三分法：比较两个三等分点的函数值，舍去远离极值的一侧，迭代收敛。', '一行，四个实数 p、q、l、r。', '一行，一个实数，表示最小值，保留 4 位小数。',
 '0 3 -5 5', '3.0000', '单峰（单谷）函数可用三分法：比较两个三等分点的函数值，舍去远离极值的一侧，迭代收敛。', 'import sys\n\np, q, l, r = map(float, sys.stdin.read().split())\n\n\ndef f(x):\n    return (x - p) ** 2 + q\n\n\nfor _ in range(200):\n    m1 = l + (r - l) / 3\n    m2 = r - (r - l) / 3\n    if f(m1) < f(m2):\n        r = m2\n    else:\n        l = m1\nprint("%.4f" % f((l + r) / 2))\n', 'python',
 '三分查找,数学,极值', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '0 3 -5 5', '3.0000\n', 1, 1),
(@aid, '-2.87 -7.96 -14.44 6.08', '-7.9600\n', 0, 2),
(@aid, '5.35 -4.19 -6.84 17.06', '-4.1900\n', 0, 3),
(@aid, '5.19 9.21 -13.32 17.71', '9.2100\n', 0, 4),
(@aid, '4.26 7.32 -11.16 7.40', '7.3200\n', 0, 5),
(@aid, '-4.16 -1.09 -10.81 14.39', '-1.0900\n', 0, 6);

-- ---------- 68. 整数平方根（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('整数平方根', 2, 10, '## 【题目描述】\n\n给定非负整数 x，求其算术平方根的整数部分（即不超过 √x 的最大整数）。\n\n## 【输入格式】\n\n一行，一个非负整数 x。\n\n## 【输出格式】\n\n一行，一个整数，表示 ⌊√x⌋。\n\n## 【样例】\n\n输入：\n\n```\n8\n```\n\n输出：\n\n```\n2\n```\n\n## 【数据范围】\n\n0 ≤ x ≤ 10¹²\n\n## 【提示】\n\n对答案二分：找到最大的 mid 使 mid² ≤ x。注意 mid * mid 在大数时可能溢出（C/C++ 需改用除法判断）。', '一行，一个非负整数 x。', '一行，一个整数，表示 ⌊√x⌋。',
 '8', '2', '对答案二分：找到最大的 mid 使 mid² ≤ x。注意 mid * mid 在大数时可能溢出（C/C++ 需改用除法判断）。', 'import sys\n\nx = int(sys.stdin.read().strip())\nlo, hi = 0, x\nwhile lo < hi:\n    mid = (lo + hi + 1) // 2\n    if mid * mid <= x:\n        lo = mid\n    else:\n        hi = mid - 1\nprint(lo)\n', 'python',
 '二分,数学,查找', '洛谷', 40);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '8', '2\n', 1, 1),
(@aid, '727346337042', '852846\n', 0, 2),
(@aid, '916382900467', '957278\n', 0, 3),
(@aid, '486745800400', '697671\n', 0, 4),
(@aid, '471925662689', '686968\n', 0, 5),
(@aid, '385087211452', '620553\n', 0, 6);

-- ---------- 69. 众数统计（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('众数统计', 2, 10, '## 【题目描述】\n\n给定 n 个整数，求出现次数最多的数（众数）；若有多个众数，输出其中最小的那个。同时输出它出现的次数。\n\n## 【输入格式】\n\n两行。第一行一个整数 n；第二行 n 个整数。\n\n## 【输出格式】\n\n一行，两个整数，依次为众数与其出现次数，用空格分隔。\n\n## 【样例】\n\n输入：\n\n```\n7\n1 2 1 3 2 1 4\n```\n\n输出：\n\n```\n1 3\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁵\n\n## 【提示】\n\n哈希表统计频次，再按"次数降序、数值升序"取最优项；也可排序后一趟扫描统计连续段。', '两行。第一行一个整数 n；第二行 n 个整数。', '一行，两个整数，依次为众数与其出现次数，用空格分隔。',
 '7\n1 2 1 3 2 1 4', '1 3', '哈希表统计频次，再按"次数降序、数值升序"取最优项；也可排序后一趟扫描统计连续段。', 'import sys\nfrom collections import Counter\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nnums = list(map(int, data[1:1 + n]))\nif not nums:\n    print("0 0")\nelse:\n    cnt = Counter(nums)\n    best = min(cnt.items(), key=lambda kv: (-kv[1], kv[0]))\n    print(best[0], best[1])\n', 'python',
 '哈希,统计,排序', '洛谷', 33);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '7\n1 2 1 3 2 1 4', '1 3\n', 1, 1),
(@aid, '2\n-958 -887', '-958 1\n', 0, 2),
(@aid, '12\n-394 -29 -710 -752 -416 -994 -93 -248 -233 -619 -821 -869', '-994 1\n', 0, 3),
(@aid, '8\n-65 -121 -906 -463 -737 -190 -22 -681', '-906 1\n', 0, 4),
(@aid, '8\n-838 -47 -282 -477 -622 -101 -645 -71', '-838 1\n', 0, 5),
(@aid, '19\n-39 -293 -760 -92 -878 -491 -651 -351 -807 -985 -439 -695 -691 -219 -624 -961 -228 -197 -108', '-985 1\n', 0, 6);

-- ---------- 70. 中位数（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('中位数', 2, 10, '## 【题目描述】\n\n给定 n 个整数，求它们的中位数：若 n 为奇数，输出排序后正中间的数；若 n 为偶数，输出排序后中间两个数的平均值（保留 1 位小数）。\n\n## 【输入格式】\n\n两行。第一行一个整数 n；第二行 n 个整数。\n\n## 【输出格式】\n\n一行，中位数（偶数个时保留 1 位小数）。\n\n## 【样例】\n\n输入：\n\n```\n4\n1 2 3 4\n```\n\n输出：\n\n```\n2.5\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁵\n\n## 【提示】\n\n排序后分奇偶处理：奇数取下标 n//2，偶数取中间两项平均值。', '两行。第一行一个整数 n；第二行 n 个整数。', '一行，中位数（偶数个时保留 1 位小数）。',
 '4\n1 2 3 4', '2.5', '排序后分奇偶处理：奇数取下标 n//2，偶数取中间两项平均值。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nnums = sorted(map(int, data[1:1 + n]))\nif n % 2:\n    print(nums[n // 2])\nelse:\n    print("%.1f" % ((nums[n // 2 - 1] + nums[n // 2]) / 2))\n', 'python',
 '排序,统计,数学', '洛谷', 6);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '4\n1 2 3 4', '2.5\n', 1, 1),
(@aid, '12\n-522 -646 -224 -791 -995 -250 -805 -617 -530 -565 -838 -860', '-631.5\n', 0, 2),
(@aid, '5\n-91 -225 -700 -246 -673', '-246\n', 0, 3),
(@aid, '20\n-648 -349 -677 -406 -339 -493 -723 -812 -761 -54 -938 -278 -478 -525 -527 74 -475 -680 -638 -520', '-522.5\n', 0, 4),
(@aid, '5\n-43 -540 -249 -763 -631', '-540\n', 0, 5),
(@aid, '3\n-956 -170 -714', '-714\n', 0, 6);

-- ---------- 71. 最大差值（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('最大差值', 2, 10, '## 【题目描述】\n\n给定 n 个整数，求其中任意两个元素（要求前者下标小于后者下标）之差的最大值 a[j] - a[i]（j > i）；若不存在这样的数对则输出 0。\n\n## 【输入格式】\n\n两行。第一行一个整数 n；第二行 n 个整数。\n\n## 【输出格式】\n\n一行，一个整数，表示最大差值。\n\n## 【样例】\n\n输入：\n\n```\n5\n3 9 2 7 5\n```\n\n输出：\n\n```\n6\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁵\n\n## 【提示】\n\n一趟扫描维护"到目前为止的最小值"，用当前值减去它更新答案，O(n)。', '两行。第一行一个整数 n；第二行 n 个整数。', '一行，一个整数，表示最大差值。',
 '5\n3 9 2 7 5', '6', '一趟扫描维护"到目前为止的最小值"，用当前值减去它更新答案，O(n)。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nnums = list(map(int, data[1:1 + n]))\nif n < 2:\n    print(0)\nelse:\n    mn = nums[0]\n    best = 0\n    for x in nums[1:]:\n        best = max(best, x - mn)\n        mn = min(mn, x)\n    print(best)\n', 'python',
 '数组,枚举,最值', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '5\n3 9 2 7 5', '6\n', 1, 1),
(@aid, '10\n-489 169 -849 -894 -854 -762 -48 -504 30 -848', '924\n', 0, 2),
(@aid, '12\n-995 -523 -879 -962 -619 -498 26 199 -398 -399 -287 -598', '1194\n', 0, 3),
(@aid, '16\n-308 -565 -647 -107 -23 -604 -325 -336 -673 131 141 -158 -678 -525 -652 -853', '814\n', 0, 4),
(@aid, '6\n106 -132 -159 -196 -143 -123', '73\n', 0, 5),
(@aid, '3\n-343 187 -687', '530\n', 0, 6);

-- ---------- 72. 和为 k 的最长子数组（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('和为 k 的最长子数组', 3, 20, '## 【题目描述】\n\n给定一个长度为 n 的整数序列（可能含负数）和整数 k，求元素和恰好等于 k 的最长连续子数组的长度；若不存在则输出 0。\n\n## 【输入格式】\n\n第一行两个整数 n、k；第二行 n 个整数。\n\n## 【输出格式】\n\n一行，一个整数，表示最长长度。\n\n## 【样例】\n\n输入：\n\n```\n7 3\n1 -1 5 -2 3 0 1\n```\n\n输出：\n\n```\n4\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁵\n\n## 【提示】\n\n前缀和 + 哈希：若 pre[j] - pre[i] = k，则区间 (i, j] 和为 k。记录每个前缀和首次出现的位置，保留最早的那个可得到最长长度。', '第一行两个整数 n、k；第二行 n 个整数。', '一行，一个整数，表示最长长度。',
 '7 3\n1 -1 5 -2 3 0 1', '4', '前缀和 + 哈希：若 pre[j] - pre[i] = k，则区间 (i, j] 和为 k。记录每个前缀和首次出现的位置，保留最早的那个可得到最长长度。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nk = int(data[1])\nnums = list(map(int, data[2:2 + n]))\nfirst = {0: 0}\npre = 0\nbest = 0\nfor i, x in enumerate(nums, 1):\n    pre += x\n    if pre - k in first:\n        best = max(best, i - first[pre - k])\n    if pre not in first:\n        first[pre] = i\nprint(best)\n', 'python',
 '前缀和,哈希,子数组', '洛谷', 33);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '7 3\n1 -1 5 -2 3 0 1', '4\n', 1, 1),
(@aid, '7 18\n4 8 -10 -9 2 -10 3 -5 0 -10 5 6 8 6 -9', '0\n', 0, 2),
(@aid, '25 -12\n-1 6 6 -1 7 -9 -9 -8 -7 -5 3 -5 9 -4 -5 2 7 3 8 9 8 -8 -6 -9 2', '23\n', 0, 3),
(@aid, '3 -19\n-10 10 2 -3 -9 0 2 -2 -10 8 1 4 -3 4 -5 6 1 6 -9', '0\n', 0, 4),
(@aid, '3 3\n10 0 -7 -1', '3\n', 0, 5),
(@aid, '24 -18\n-9 3 9 -5', '0\n', 0, 6);

-- ---------- 73. 长度最小的连续子数组（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('长度最小的连续子数组', 3, 20, '## 【题目描述】\n\n给定一个长度为 n 的正整数序列和整数 s，求元素和不小于 s 的最短连续子数组的长度；若不存在则输出 0。\n\n## 【输入格式】\n\n第一行两个整数 n、s；第二行 n 个正整数。\n\n## 【输出格式】\n\n一行，一个整数，表示最短长度。\n\n## 【样例】\n\n输入：\n\n```\n6 7\n2 3 1 2 4 3\n```\n\n输出：\n\n```\n2\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁵\n\n## 【提示】\n\n滑动窗口（双指针）：右指针扩张窗口使和增大，达标后左指针尽量右移收缩，每个元素进出各一次，O(n)。', '第一行两个整数 n、s；第二行 n 个正整数。', '一行，一个整数，表示最短长度。',
 '6 7\n2 3 1 2 4 3', '2', '滑动窗口（双指针）：右指针扩张窗口使和增大，达标后左指针尽量右移收缩，每个元素进出各一次，O(n)。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\ns = int(data[1])\nnums = list(map(int, data[2:2 + n]))\nbest = n + 1\nleft = 0\ntotal = 0\nfor right, x in enumerate(nums):\n    total += x\n    while total >= s:\n        best = min(best, right - left + 1)\n        total -= nums[left]\n        left += 1\nprint(0 if best == n + 1 else best)\n', 'python',
 '双指针,滑动窗口,子数组', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '6 7\n2 3 1 2 4 3', '2\n', 1, 1),
(@aid, '1 28\n17 6 16 4 5 8 16 13 13 17 10 8 15 2 7 20 5 16 2 3 4 6 18', '0\n', 0, 2),
(@aid, '5 58\n6 8 6 8 13 10 6 6', '0\n', 0, 3),
(@aid, '21 20\n2 1 3 20 8 19 12 12 3 19 2 10 8 2 1 10 9 4 3 11 14 14 5 15 3', '1\n', 0, 4),
(@aid, '15 31\n15 15 4 11 12 11 16 12 15 17 11 13 10 12 11', '2\n', 0, 5),
(@aid, '16 40\n6 2', '0\n', 0, 6);

-- ---------- 74. 离散化求区间和（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('离散化求区间和', 3, 20, '## 【题目描述】\n\n在一条数轴上有 n 次"在某点 x 处加上 c"的操作，随后有 m 次询问，每次询问区间 [l, r] 上的数值总和。坐标范围可达 10⁹，但操作与询问涉及的坐标总数不超过 3×10⁵。\n\n## 【输入格式】\n\n第一行两个整数 n、m；接下来 n 行，每行两个整数 x、c；接下来 m 行，每行两个整数 l、r。\n\n## 【输出格式】\n\nm 行，每行一个整数，表示对应区间的数值和。\n\n## 【样例】\n\n输入：\n\n```\n3 2\n10 5\n100 3\n1000 8\n1 100\n10 1000\n```\n\n输出：\n\n```\n8\n16\n```\n\n## 【数据范围】\n\n1 ≤ n, m ≤ 10⁵，坐标 ≤ 10⁹\n\n## 【提示】\n\n坐标范围大但点数少时先"离散化"：把所有出现过的坐标排序去重，用下标代替原坐标，再做前缀和。注意 pos(l) 应取第一个 ≥ l 的位置。', '第一行两个整数 n、m；接下来 n 行，每行两个整数 x、c；接下来 m 行，每行两个整数 l、r。', 'm 行，每行一个整数，表示对应区间的数值和。',
 '3 2\n10 5\n100 3\n1000 8\n1 100\n10 1000', '8\n16', '坐标范围大但点数少时先"离散化"：把所有出现过的坐标排序去重，用下标代替原坐标，再做前缀和。注意 pos(l) 应取第一个 ≥ l 的位置。', 'import sys\n\ndata = sys.stdin.read().split()\nidx = 0\nn = int(data[idx]); m = int(data[idx + 1]); idx += 2\nadds = []\ncoords = []\nfor _ in range(n):\n    x = int(data[idx]); c = int(data[idx + 1]); idx += 2\n    adds.append((x, c))\n    coords.append(x)\nqueries = []\nfor _ in range(m):\n    l = int(data[idx]); rr = int(data[idx + 1]); idx += 2\n    queries.append((l, rr))\n    coords.append(l)\n    coords.append(rr)\nvals = sorted(set(coords))\n\n\ndef pos(x):\n    lo, hi = 0, len(vals) - 1\n    while lo < hi:\n        mid = (lo + hi) // 2\n        if vals[mid] >= x:\n            hi = mid\n        else:\n            lo = mid + 1\n    return lo\n\n\narr = [0] * len(vals)\nfor x, c in adds:\n    arr[pos(x)] += c\npre = [0]\nfor v in arr:\n    pre.append(pre[-1] + v)\nout = []\nfor l, rr in queries:\n    out.append(str(pre[pos(rr) + 1] - pre[pos(l)]))\nprint("\\n".join(out))\n', 'python',
 '离散化,前缀和,二分', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3 2\n10 5\n100 3\n1000 8\n1 100\n10 1000', '8\n16\n', 1, 1),
(@aid, '11 1\n969484 88\n883592 40\n908619 70\n995621 75\n529422 42\n790467 86\n235658 90\n875348 76\n378767 53\n600060 19\n977448 70\n50379 689876', '204\n', 0, 2),
(@aid, '10 2\n815816 8\n219762 94\n183752 85\n160570 21\n463359 81\n551769 50\n327471 40\n112033 79\n917955 16\n264056 92\n157598 385067\n754785 979467', '332\n24\n', 0, 3),
(@aid, '1 2\n167571 2\n1758 796127\n7191 195503', '2\n2\n', 0, 4),
(@aid, '2 5\n755953 26\n553900 31\n254790 771317\n349041 817923\n72667 587988\n330398 763989\n611894 655293', '57\n57\n31\n57\n0\n', 0, 5),
(@aid, '7 2\n305070 56\n954583 31\n365683 22\n809720 48\n866013 53\n309720 77\n868517 6\n197884 928822\n7000 936769', '262\n262\n', 0, 6);

-- ---------- 75. 全排列（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('全排列', 3, 20, '## 【题目描述】\n\n给定整数 n，按字典序输出 1 到 n 的所有排列，每个排列占一行，数字之间用空格分隔。\n\n## 【输入格式】\n\n一行，一个整数 n。\n\n## 【输出格式】\n\n若干行，每行为一个排列。\n\n## 【样例】\n\n输入：\n\n```\n3\n```\n\n输出：\n\n```\n1 2 3\n1 3 2\n2 1 3\n2 3 1\n3 1 2\n3 2 1\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 8\n\n## 【提示】\n\n回溯法：维护 used 数组与当前路径，每层枚举未使用的数字，递归到叶子即得到一个排列。因为按从小到大的顺序枚举，输出天然是字典序。', '一行，一个整数 n。', '若干行，每行为一个排列。',
 '3', '1 2 3\n1 3 2\n2 1 3\n2 3 1\n3 1 2\n3 2 1', '回溯法：维护 used 数组与当前路径，每层枚举未使用的数字，递归到叶子即得到一个排列。因为按从小到大的顺序枚举，输出天然是字典序。', 'import sys\n\nn = int(sys.stdin.read().strip())\nnums = list(range(1, n + 1))\nused = [False] * n\npath = []\nout = []\n\n\ndef dfs():\n    if len(path) == n:\n        out.append(" ".join(map(str, path)))\n        return\n    for i in range(n):\n        if not used[i]:\n            used[i] = True\n            path.append(nums[i])\n            dfs()\n            path.pop()\n            used[i] = False\n\n\ndfs()\nprint("\\n".join(out))\n', 'python',
 'DFS,回溯,全排列', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3', '1 2 3\n1 3 2\n2 1 3\n2 3 1\n3 1 2\n3 2 1\n', 1, 1),
(@aid, '1', '1\n', 0, 2),
(@aid, '1', '1\n', 0, 3),
(@aid, '2', '1 2\n2 1\n', 0, 4),
(@aid, '6', '1 2 3 4 5 6\n1 2 3 4 6 5\n1 2 3 5 4 6\n1 2 3 5 6 4\n1 2 3 6 4 5\n1 2 3 6 5 4\n1 2 4 3 5 6\n1 2 4 3 6 5\n1 2 4 5 3 6\n1 2 4 5 6 3\n1 2 4 6 3 5\n1 2 4 6 5 3\n1 2 5 3 4 6\n1 2 5 3 6 4\n1 2 5 4 3 6\n1 2 5 4 6 3\n1 2 5 6 3 4\n1 2 5 6 4 3\n1 2 6 3 4 5\n1 2 6 3 5 4\n1 2 6 4 3 5\n1 2 6 4 5 3\n1 2 6 5 3 4\n1 2 6 5 4 3\n1 3 2 4 5 6\n1 3 2 4 6 5\n1 3 2 5 4 6\n1 3 2 5 6 4\n1 3 2 6 4 5\n1 3 2 6 5 4\n1 3 4 2 5 6\n1 3 4 2 6 5\n1 3 4 5 2 6\n1 3 4 5 6 2\n1 3 4 6 2 5\n1 3 4 6 5 2\n1 3 5 2 4 6\n1 3 5 2 6 4\n1 3 5 4 2 6\n1 3 5 4 6 2\n1 3 5 6 2 4\n1 3 5 6 4 2\n1 3 6 2 4 5\n1 3 6 2 5 4\n1 3 6 4 2 5\n1 3 6 4 5 2\n1 3 6 5 2 4\n1 3 6 5 4 2\n1 4 2 3 5 6\n1 4 2 3 6 5\n1 4 2 5 3 6\n1 4 2 5 6 3\n1 4 2 6 3 5\n1 4 2 6 5 3\n1 4 3 2 5 6\n1 4 3 2 6 5\n1 4 3 5 2 6\n1 4 3 5 6 2\n1 4 3 6 2 5\n1 4 3 6 5 2\n1 4 5 2 3 6\n1 4 5 2 6 3\n1 4 5 3 2 6\n1 4 5 3 6 2\n1 4 5 6 2 3\n1 4 5 6 3 2\n1 4 6 2 3 5\n1 4 6 2 5 3\n1 4 6 3 2 5\n1 4 6 3 5 2\n1 4 6 5 2 3\n1 4 6 5 3 2\n1 5 2 3 4 6\n1 5 2 3 6 4\n1 5 2 4 3 6\n1 5 2 4 6 3\n1 5 2 6 3 4\n1 5 2 6 4 3\n1 5 3 2 4 6\n1 5 3 2 6 4\n1 5 3 4 2 6\n1 5 3 4 6 2\n1 5 3 6 2 4\n1 5 3 6 4 2\n1 5 4 2 3 6\n1 5 4 2 6 3\n1 5 4 3 2 6\n1 5 4 3 6 2\n1 5 4 6 2 3\n1 5 4 6 3 2\n1 5 6 2 3 4\n1 5 6 2 4 3\n1 5 6 3 2 4\n1 5 6 3 4 2\n1 5 6 4 2 3\n1 5 6 4 3 2\n1 6 2 3 4 5\n1 6 2 3 5 4\n1 6 2 4 3 5\n1 6 2 4 5 3\n1 6 2 5 3 4\n1 6 2 5 4 3\n1 6 3 2 4 5\n1 6 3 2 5 4\n1 6 3 4 2 5\n1 6 3 4 5 2\n1 6 3 5 2 4\n1 6 3 5 4 2\n1 6 4 2 3 5\n1 6 4 2 5 3\n1 6 4 3 2 5\n1 6 4 3 5 2\n1 6 4 5 2 3\n1 6 4 5 3 2\n1 6 5 2 3 4\n1 6 5 2 4 3\n1 6 5 3 2 4\n1 6 5 3 4 2\n1 6 5 4 2 3\n1 6 5 4 3 2\n2 1 3 4 5 6\n2 1 3 4 6 5\n2 1 3 5 4 6\n2 1 3 5 6 4\n2 1 3 6 4 5\n2 1 3 6 5 4\n2 1 4 3 5 6\n2 1 4 3 6 5\n2 1 4 5 3 6\n2 1 4 5 6 3\n2 1 4 6 3 5\n2 1 4 6 5 3\n2 1 5 3 4 6\n2 1 5 3 6 4\n2 1 5 4 3 6\n2 1 5 4 6 3\n2 1 5 6 3 4\n2 1 5 6 4 3\n2 1 6 3 4 5\n2 1 6 3 5 4\n2 1 6 4 3 5\n2 1 6 4 5 3\n2 1 6 5 3 4\n2 1 6 5 4 3\n2 3 1 4 5 6\n2 3 1 4 6 5\n2 3 1 5 4 6\n2 3 1 5 6 4\n2 3 1 6 4 5\n2 3 1 6 5 4\n2 3 4 1 5 6\n2 3 4 1 6 5\n2 3 4 5 1 6\n2 3 4 5 6 1\n2 3 4 6 1 5\n2 3 4 6 5 1\n2 3 5 1 4 6\n2 3 5 1 6 4\n2 3 5 4 1 6\n2 3 5 4 6 1\n2 3 5 6 1 4\n2 3 5 6 4 1\n2 3 6 1 4 5\n2 3 6 1 5 4\n2 3 6 4 1 5\n2 3 6 4 5 1\n2 3 6 5 1 4\n2 3 6 5 4 1\n2 4 1 3 5 6\n2 4 1 3 6 5\n2 4 1 5 3 6\n2 4 1 5 6 3\n2 4 1 6 3 5\n2 4 1 6 5 3\n2 4 3 1 5 6\n2 4 3 1 6 5\n2 4 3 5 1 6\n2 4 3 5 6 1\n2 4 3 6 1 5\n2 4 3 6 5 1\n2 4 5 1 3 6\n2 4 5 1 6 3\n2 4 5 3 1 6\n2 4 5 3 6 1\n2 4 5 6 1 3\n2 4 5 6 3 1\n2 4 6 1 3 5\n2 4 6 1 5 3\n2 4 6 3 1 5\n2 4 6 3 5 1\n2 4 6 5 1 3\n2 4 6 5 3 1\n2 5 1 3 4 6\n2 5 1 3 6 4\n2 5 1 4 3 6\n2 5 1 4 6 3\n2 5 1 6 3 4\n2 5 1 6 4 3\n2 5 3 1 4 6\n2 5 3 1 6 4\n2 5 3 4 1 6\n2 5 3 4 6 1\n2 5 3 6 1 4\n2 5 3 6 4 1\n2 5 4 1 3 6\n2 5 4 1 6 3\n2 5 4 3 1 6\n2 5 4 3 6 1\n2 5 4 6 1 3\n2 5 4 6 3 1\n2 5 6 1 3 4\n2 5 6 1 4 3\n2 5 6 3 1 4\n2 5 6 3 4 1\n2 5 6 4 1 3\n2 5 6 4 3 1\n2 6 1 3 4 5\n2 6 1 3 5 4\n2 6 1 4 3 5\n2 6 1 4 5 3\n2 6 1 5 3 4\n2 6 1 5 4 3\n2 6 3 1 4 5\n2 6 3 1 5 4\n2 6 3 4 1 5\n2 6 3 4 5 1\n2 6 3 5 1 4\n2 6 3 5 4 1\n2 6 4 1 3 5\n2 6 4 1 5 3\n2 6 4 3 1 5\n2 6 4 3 5 1\n2 6 4 5 1 3\n2 6 4 5 3 1\n2 6 5 1 3 4\n2 6 5 1 4 3\n2 6 5 3 1 4\n2 6 5 3 4 1\n2 6 5 4 1 3\n2 6 5 4 3 1\n3 1 2 4 5 6\n3 1 2 4 6 5\n3 1 2 5 4 6\n3 1 2 5 6 4\n3 1 2 6 4 5\n3 1 2 6 5 4\n3 1 4 2 5 6\n3 1 4 2 6 5\n3 1 4 5 2 6\n3 1 4 5 6 2\n3 1 4 6 2 5\n3 1 4 6 5 2\n3 1 5 2 4 6\n3 1 5 2 6 4\n3 1 5 4 2 6\n3 1 5 4 6 2\n3 1 5 6 2 4\n3 1 5 6 4 2\n3 1 6 2 4 5\n3 1 6 2 5 4\n3 1 6 4 2 5\n3 1 6 4 5 2\n3 1 6 5 2 4\n3 1 6 5 4 2\n3 2 1 4 5 6\n3 2 1 4 6 5\n3 2 1 5 4 6\n3 2 1 5 6 4\n3 2 1 6 4 5\n3 2 1 6 5 4\n3 2 4 1 5 6\n3 2 4 1 6 5\n3 2 4 5 1 6\n3 2 4 5 6 1\n3 2 4 6 1 5\n3 2 4 6 5 1\n3 2 5 1 4 6\n3 2 5 1 6 4\n3 2 5 4 1 6\n3 2 5 4 6 1\n3 2 5 6 1 4\n3 2 5 6 4 1\n3 2 6 1 4 5\n3 2 6 1 5 4\n3 2 6 4 1 5\n3 2 6 4 5 1\n3 2 6 5 1 4\n3 2 6 5 4 1\n3 4 1 2 5 6\n3 4 1 2 6 5\n3 4 1 5 2 6\n3 4 1 5 6 2\n3 4 1 6 2 5\n3 4 1 6 5 2\n3 4 2 1 5 6\n3 4 2 1 6 5\n3 4 2 5 1 6\n3 4 2 5 6 1\n3 4 2 6 1 5\n3 4 2 6 5 1\n3 4 5 1 2 6\n3 4 5 1 6 2\n3 4 5 2 1 6\n3 4 5 2 6 1\n3 4 5 6 1 2\n3 4 5 6 2 1\n3 4 6 1 2 5\n3 4 6 1 5 2\n3 4 6 2 1 5\n3 4 6 2 5 1\n3 4 6 5 1 2\n3 4 6 5 2 1\n3 5 1 2 4 6\n3 5 1 2 6 4\n3 5 1 4 2 6\n3 5 1 4 6 2\n3 5 1 6 2 4\n3 5 1 6 4 2\n3 5 2 1 4 6\n3 5 2 1 6 4\n3 5 2 4 1 6\n3 5 2 4 6 1\n3 5 2 6 1 4\n3 5 2 6 4 1\n3 5 4 1 2 6\n3 5 4 1 6 2\n3 5 4 2 1 6\n3 5 4 2 6 1\n3 5 4 6 1 2\n3 5 4 6 2 1\n3 5 6 1 2 4\n3 5 6 1 4 2\n3 5 6 2 1 4\n3 5 6 2 4 1\n3 5 6 4 1 2\n3 5 6 4 2 1\n3 6 1 2 4 5\n3 6 1 2 5 4\n3 6 1 4 2 5\n3 6 1 4 5 2\n3 6 1 5 2 4\n3 6 1 5 4 2\n3 6 2 1 4 5\n3 6 2 1 5 4\n3 6 2 4 1 5\n3 6 2 4 5 1\n3 6 2 5 1 4\n3 6 2 5 4 1\n3 6 4 1 2 5\n3 6 4 1 5 2\n3 6 4 2 1 5\n3 6 4 2 5 1\n3 6 4 5 1 2\n3 6 4 5 2 1\n3 6 5 1 2 4\n3 6 5 1 4 2\n3 6 5 2 1 4\n3 6 5 2 4 1\n3 6 5 4 1 2\n3 6 5 4 2 1\n4 1 2 3 5 6\n4 1 2 3 6 5\n4 1 2 5 3 6\n4 1 2 5 6 3\n4 1 2 6 3 5\n4 1 2 6 5 3\n4 1 3 2 5 6\n4 1 3 2 6 5\n4 1 3 5 2 6\n4 1 3 5 6 2\n4 1 3 6 2 5\n4 1 3 6 5 2\n4 1 5 2 3 6\n4 1 5 2 6 3\n4 1 5 3 2 6\n4 1 5 3 6 2\n4 1 5 6 2 3\n4 1 5 6 3 2\n4 1 6 2 3 5\n4 1 6 2 5 3\n4 1 6 3 2 5\n4 1 6 3 5 2\n4 1 6 5 2 3\n4 1 6 5 3 2\n4 2 1 3 5 6\n4 2 1 3 6 5\n4 2 1 5 3 6\n4 2 1 5 6 3\n4 2 1 6 3 5\n4 2 1 6 5 3\n4 2 3 1 5 6\n4 2 3 1 6 5\n4 2 3 5 1 6\n4 2 3 5 6 1\n4 2 3 6 1 5\n4 2 3 6 5 1\n4 2 5 1 3 6\n4 2 5 1 6 3\n4 2 5 3 1 6\n4 2 5 3 6 1\n4 2 5 6 1 3\n4 2 5 6 3 1\n4 2 6 1 3 5\n4 2 6 1 5 3\n4 2 6 3 1 5\n4 2 6 3 5 1\n4 2 6 5 1 3\n4 2 6 5 3 1\n4 3 1 2 5 6\n4 3 1 2 6 5\n4 3 1 5 2 6\n4 3 1 5 6 2\n4 3 1 6 2 5\n4 3 1 6 5 2\n4 3 2 1 5 6\n4 3 2 1 6 5\n4 3 2 5 1 6\n4 3 2 5 6 1\n4 3 2 6 1 5\n4 3 2 6 5 1\n4 3 5 1 2 6\n4 3 5 1 6 2\n4 3 5 2 1 6\n4 3 5 2 6 1\n4 3 5 6 1 2\n4 3 5 6 2 1\n4 3 6 1 2 5\n4 3 6 1 5 2\n4 3 6 2 1 5\n4 3 6 2 5 1\n4 3 6 5 1 2\n4 3 6 5 2 1\n4 5 1 2 3 6\n4 5 1 2 6 3\n4 5 1 3 2 6\n4 5 1 3 6 2\n4 5 1 6 2 3\n4 5 1 6 3 2\n4 5 2 1 3 6\n4 5 2 1 6 3\n4 5 2 3 1 6\n4 5 2 3 6 1\n4 5 2 6 1 3\n4 5 2 6 3 1\n4 5 3 1 2 6\n4 5 3 1 6 2\n4 5 3 2 1 6\n4 5 3 2 6 1\n4 5 3 6 1 2\n4 5 3 6 2 1\n4 5 6 1 2 3\n4 5 6 1 3 2\n4 5 6 2 1 3\n4 5 6 2 3 1\n4 5 6 3 1 2\n4 5 6 3 2 1\n4 6 1 2 3 5\n4 6 1 2 5 3\n4 6 1 3 2 5\n4 6 1 3 5 2\n4 6 1 5 2 3\n4 6 1 5 3 2\n4 6 2 1 3 5\n4 6 2 1 5 3\n4 6 2 3 1 5\n4 6 2 3 5 1\n4 6 2 5 1 3\n4 6 2 5 3 1\n4 6 3 1 2 5\n4 6 3 1 5 2\n4 6 3 2 1 5\n4 6 3 2 5 1\n4 6 3 5 1 2\n4 6 3 5 2 1\n4 6 5 1 2 3\n4 6 5 1 3 2\n4 6 5 2 1 3\n4 6 5 2 3 1\n4 6 5 3 1 2\n4 6 5 3 2 1\n5 1 2 3 4 6\n5 1 2 3 6 4\n5 1 2 4 3 6\n5 1 2 4 6 3\n5 1 2 6 3 4\n5 1 2 6 4 3\n5 1 3 2 4 6\n5 1 3 2 6 4\n5 1 3 4 2 6\n5 1 3 4 6 2\n5 1 3 6 2 4\n5 1 3 6 4 2\n5 1 4 2 3 6\n5 1 4 2 6 3\n5 1 4 3 2 6\n5 1 4 3 6 2\n5 1 4 6 2 3\n5 1 4 6 3 2\n5 1 6 2 3 4\n5 1 6 2 4 3\n5 1 6 3 2 4\n5 1 6 3 4 2\n5 1 6 4 2 3\n5 1 6 4 3 2\n5 2 1 3 4 6\n5 2 1 3 6 4\n5 2 1 4 3 6\n5 2 1 4 6 3\n5 2 1 6 3 4\n5 2 1 6 4 3\n5 2 3 1 4 6\n5 2 3 1 6 4\n5 2 3 4 1 6\n5 2 3 4 6 1\n5 2 3 6 1 4\n5 2 3 6 4 1\n5 2 4 1 3 6\n5 2 4 1 6 3\n5 2 4 3 1 6\n5 2 4 3 6 1\n5 2 4 6 1 3\n5 2 4 6 3 1\n5 2 6 1 3 4\n5 2 6 1 4 3\n5 2 6 3 1 4\n5 2 6 3 4 1\n5 2 6 4 1 3\n5 2 6 4 3 1\n5 3 1 2 4 6\n5 3 1 2 6 4\n5 3 1 4 2 6\n5 3 1 4 6 2\n5 3 1 6 2 4\n5 3 1 6 4 2\n5 3 2 1 4 6\n5 3 2 1 6 4\n5 3 2 4 1 6\n5 3 2 4 6 1\n5 3 2 6 1 4\n5 3 2 6 4 1\n5 3 4 1 2 6\n5 3 4 1 6 2\n5 3 4 2 1 6\n5 3 4 2 6 1\n5 3 4 6 1 2\n5 3 4 6 2 1\n5 3 6 1 2 4\n5 3 6 1 4 2\n5 3 6 2 1 4\n5 3 6 2 4 1\n5 3 6 4 1 2\n5 3 6 4 2 1\n5 4 1 2 3 6\n5 4 1 2 6 3\n5 4 1 3 2 6\n5 4 1 3 6 2\n5 4 1 6 2 3\n5 4 1 6 3 2\n5 4 2 1 3 6\n5 4 2 1 6 3\n5 4 2 3 1 6\n5 4 2 3 6 1\n5 4 2 6 1 3\n5 4 2 6 3 1\n5 4 3 1 2 6\n5 4 3 1 6 2\n5 4 3 2 1 6\n5 4 3 2 6 1\n5 4 3 6 1 2\n5 4 3 6 2 1\n5 4 6 1 2 3\n5 4 6 1 3 2\n5 4 6 2 1 3\n5 4 6 2 3 1\n5 4 6 3 1 2\n5 4 6 3 2 1\n5 6 1 2 3 4\n5 6 1 2 4 3\n5 6 1 3 2 4\n5 6 1 3 4 2\n5 6 1 4 2 3\n5 6 1 4 3 2\n5 6 2 1 3 4\n5 6 2 1 4 3\n5 6 2 3 1 4\n5 6 2 3 4 1\n5 6 2 4 1 3\n5 6 2 4 3 1\n5 6 3 1 2 4\n5 6 3 1 4 2\n5 6 3 2 1 4\n5 6 3 2 4 1\n5 6 3 4 1 2\n5 6 3 4 2 1\n5 6 4 1 2 3\n5 6 4 1 3 2\n5 6 4 2 1 3\n5 6 4 2 3 1\n5 6 4 3 1 2\n5 6 4 3 2 1\n6 1 2 3 4 5\n6 1 2 3 5 4\n6 1 2 4 3 5\n6 1 2 4 5 3\n6 1 2 5 3 4\n6 1 2 5 4 3\n6 1 3 2 4 5\n6 1 3 2 5 4\n6 1 3 4 2 5\n6 1 3 4 5 2\n6 1 3 5 2 4\n6 1 3 5 4 2\n6 1 4 2 3 5\n6 1 4 2 5 3\n6 1 4 3 2 5\n6 1 4 3 5 2\n6 1 4 5 2 3\n6 1 4 5 3 2\n6 1 5 2 3 4\n6 1 5 2 4 3\n6 1 5 3 2 4\n6 1 5 3 4 2\n6 1 5 4 2 3\n6 1 5 4 3 2\n6 2 1 3 4 5\n6 2 1 3 5 4\n6 2 1 4 3 5\n6 2 1 4 5 3\n6 2 1 5 3 4\n6 2 1 5 4 3\n6 2 3 1 4 5\n6 2 3 1 5 4\n6 2 3 4 1 5\n6 2 3 4 5 1\n6 2 3 5 1 4\n6 2 3 5 4 1\n6 2 4 1 3 5\n6 2 4 1 5 3\n6 2 4 3 1 5\n6 2 4 3 5 1\n6 2 4 5 1 3\n6 2 4 5 3 1\n6 2 5 1 3 4\n6 2 5 1 4 3\n6 2 5 3 1 4\n6 2 5 3 4 1\n6 2 5 4 1 3\n6 2 5 4 3 1\n6 3 1 2 4 5\n6 3 1 2 5 4\n6 3 1 4 2 5\n6 3 1 4 5 2\n6 3 1 5 2 4\n6 3 1 5 4 2\n6 3 2 1 4 5\n6 3 2 1 5 4\n6 3 2 4 1 5\n6 3 2 4 5 1\n6 3 2 5 1 4\n6 3 2 5 4 1\n6 3 4 1 2 5\n6 3 4 1 5 2\n6 3 4 2 1 5\n6 3 4 2 5 1\n6 3 4 5 1 2\n6 3 4 5 2 1\n6 3 5 1 2 4\n6 3 5 1 4 2\n6 3 5 2 1 4\n6 3 5 2 4 1\n6 3 5 4 1 2\n6 3 5 4 2 1\n6 4 1 2 3 5\n6 4 1 2 5 3\n6 4 1 3 2 5\n6 4 1 3 5 2\n6 4 1 5 2 3\n6 4 1 5 3 2\n6 4 2 1 3 5\n6 4 2 1 5 3\n6 4 2 3 1 5\n6 4 2 3 5 1\n6 4 2 5 1 3\n6 4 2 5 3 1\n6 4 3 1 2 5\n6 4 3 1 5 2\n6 4 3 2 1 5\n6 4 3 2 5 1\n6 4 3 5 1 2\n6 4 3 5 2 1\n6 4 5 1 2 3\n6 4 5 1 3 2\n6 4 5 2 1 3\n6 4 5 2 3 1\n6 4 5 3 1 2\n6 4 5 3 2 1\n6 5 1 2 3 4\n6 5 1 2 4 3\n6 5 1 3 2 4\n6 5 1 3 4 2\n6 5 1 4 2 3\n6 5 1 4 3 2\n6 5 2 1 3 4\n6 5 2 1 4 3\n6 5 2 3 1 4\n6 5 2 3 4 1\n6 5 2 4 1 3\n6 5 2 4 3 1\n6 5 3 1 2 4\n6 5 3 1 4 2\n6 5 3 2 1 4\n6 5 3 2 4 1\n6 5 3 4 1 2\n6 5 3 4 2 1\n6 5 4 1 2 3\n6 5 4 1 3 2\n6 5 4 2 1 3\n6 5 4 2 3 1\n6 5 4 3 1 2\n6 5 4 3 2 1\n', 0, 5),
(@aid, '6', '1 2 3 4 5 6\n1 2 3 4 6 5\n1 2 3 5 4 6\n1 2 3 5 6 4\n1 2 3 6 4 5\n1 2 3 6 5 4\n1 2 4 3 5 6\n1 2 4 3 6 5\n1 2 4 5 3 6\n1 2 4 5 6 3\n1 2 4 6 3 5\n1 2 4 6 5 3\n1 2 5 3 4 6\n1 2 5 3 6 4\n1 2 5 4 3 6\n1 2 5 4 6 3\n1 2 5 6 3 4\n1 2 5 6 4 3\n1 2 6 3 4 5\n1 2 6 3 5 4\n1 2 6 4 3 5\n1 2 6 4 5 3\n1 2 6 5 3 4\n1 2 6 5 4 3\n1 3 2 4 5 6\n1 3 2 4 6 5\n1 3 2 5 4 6\n1 3 2 5 6 4\n1 3 2 6 4 5\n1 3 2 6 5 4\n1 3 4 2 5 6\n1 3 4 2 6 5\n1 3 4 5 2 6\n1 3 4 5 6 2\n1 3 4 6 2 5\n1 3 4 6 5 2\n1 3 5 2 4 6\n1 3 5 2 6 4\n1 3 5 4 2 6\n1 3 5 4 6 2\n1 3 5 6 2 4\n1 3 5 6 4 2\n1 3 6 2 4 5\n1 3 6 2 5 4\n1 3 6 4 2 5\n1 3 6 4 5 2\n1 3 6 5 2 4\n1 3 6 5 4 2\n1 4 2 3 5 6\n1 4 2 3 6 5\n1 4 2 5 3 6\n1 4 2 5 6 3\n1 4 2 6 3 5\n1 4 2 6 5 3\n1 4 3 2 5 6\n1 4 3 2 6 5\n1 4 3 5 2 6\n1 4 3 5 6 2\n1 4 3 6 2 5\n1 4 3 6 5 2\n1 4 5 2 3 6\n1 4 5 2 6 3\n1 4 5 3 2 6\n1 4 5 3 6 2\n1 4 5 6 2 3\n1 4 5 6 3 2\n1 4 6 2 3 5\n1 4 6 2 5 3\n1 4 6 3 2 5\n1 4 6 3 5 2\n1 4 6 5 2 3\n1 4 6 5 3 2\n1 5 2 3 4 6\n1 5 2 3 6 4\n1 5 2 4 3 6\n1 5 2 4 6 3\n1 5 2 6 3 4\n1 5 2 6 4 3\n1 5 3 2 4 6\n1 5 3 2 6 4\n1 5 3 4 2 6\n1 5 3 4 6 2\n1 5 3 6 2 4\n1 5 3 6 4 2\n1 5 4 2 3 6\n1 5 4 2 6 3\n1 5 4 3 2 6\n1 5 4 3 6 2\n1 5 4 6 2 3\n1 5 4 6 3 2\n1 5 6 2 3 4\n1 5 6 2 4 3\n1 5 6 3 2 4\n1 5 6 3 4 2\n1 5 6 4 2 3\n1 5 6 4 3 2\n1 6 2 3 4 5\n1 6 2 3 5 4\n1 6 2 4 3 5\n1 6 2 4 5 3\n1 6 2 5 3 4\n1 6 2 5 4 3\n1 6 3 2 4 5\n1 6 3 2 5 4\n1 6 3 4 2 5\n1 6 3 4 5 2\n1 6 3 5 2 4\n1 6 3 5 4 2\n1 6 4 2 3 5\n1 6 4 2 5 3\n1 6 4 3 2 5\n1 6 4 3 5 2\n1 6 4 5 2 3\n1 6 4 5 3 2\n1 6 5 2 3 4\n1 6 5 2 4 3\n1 6 5 3 2 4\n1 6 5 3 4 2\n1 6 5 4 2 3\n1 6 5 4 3 2\n2 1 3 4 5 6\n2 1 3 4 6 5\n2 1 3 5 4 6\n2 1 3 5 6 4\n2 1 3 6 4 5\n2 1 3 6 5 4\n2 1 4 3 5 6\n2 1 4 3 6 5\n2 1 4 5 3 6\n2 1 4 5 6 3\n2 1 4 6 3 5\n2 1 4 6 5 3\n2 1 5 3 4 6\n2 1 5 3 6 4\n2 1 5 4 3 6\n2 1 5 4 6 3\n2 1 5 6 3 4\n2 1 5 6 4 3\n2 1 6 3 4 5\n2 1 6 3 5 4\n2 1 6 4 3 5\n2 1 6 4 5 3\n2 1 6 5 3 4\n2 1 6 5 4 3\n2 3 1 4 5 6\n2 3 1 4 6 5\n2 3 1 5 4 6\n2 3 1 5 6 4\n2 3 1 6 4 5\n2 3 1 6 5 4\n2 3 4 1 5 6\n2 3 4 1 6 5\n2 3 4 5 1 6\n2 3 4 5 6 1\n2 3 4 6 1 5\n2 3 4 6 5 1\n2 3 5 1 4 6\n2 3 5 1 6 4\n2 3 5 4 1 6\n2 3 5 4 6 1\n2 3 5 6 1 4\n2 3 5 6 4 1\n2 3 6 1 4 5\n2 3 6 1 5 4\n2 3 6 4 1 5\n2 3 6 4 5 1\n2 3 6 5 1 4\n2 3 6 5 4 1\n2 4 1 3 5 6\n2 4 1 3 6 5\n2 4 1 5 3 6\n2 4 1 5 6 3\n2 4 1 6 3 5\n2 4 1 6 5 3\n2 4 3 1 5 6\n2 4 3 1 6 5\n2 4 3 5 1 6\n2 4 3 5 6 1\n2 4 3 6 1 5\n2 4 3 6 5 1\n2 4 5 1 3 6\n2 4 5 1 6 3\n2 4 5 3 1 6\n2 4 5 3 6 1\n2 4 5 6 1 3\n2 4 5 6 3 1\n2 4 6 1 3 5\n2 4 6 1 5 3\n2 4 6 3 1 5\n2 4 6 3 5 1\n2 4 6 5 1 3\n2 4 6 5 3 1\n2 5 1 3 4 6\n2 5 1 3 6 4\n2 5 1 4 3 6\n2 5 1 4 6 3\n2 5 1 6 3 4\n2 5 1 6 4 3\n2 5 3 1 4 6\n2 5 3 1 6 4\n2 5 3 4 1 6\n2 5 3 4 6 1\n2 5 3 6 1 4\n2 5 3 6 4 1\n2 5 4 1 3 6\n2 5 4 1 6 3\n2 5 4 3 1 6\n2 5 4 3 6 1\n2 5 4 6 1 3\n2 5 4 6 3 1\n2 5 6 1 3 4\n2 5 6 1 4 3\n2 5 6 3 1 4\n2 5 6 3 4 1\n2 5 6 4 1 3\n2 5 6 4 3 1\n2 6 1 3 4 5\n2 6 1 3 5 4\n2 6 1 4 3 5\n2 6 1 4 5 3\n2 6 1 5 3 4\n2 6 1 5 4 3\n2 6 3 1 4 5\n2 6 3 1 5 4\n2 6 3 4 1 5\n2 6 3 4 5 1\n2 6 3 5 1 4\n2 6 3 5 4 1\n2 6 4 1 3 5\n2 6 4 1 5 3\n2 6 4 3 1 5\n2 6 4 3 5 1\n2 6 4 5 1 3\n2 6 4 5 3 1\n2 6 5 1 3 4\n2 6 5 1 4 3\n2 6 5 3 1 4\n2 6 5 3 4 1\n2 6 5 4 1 3\n2 6 5 4 3 1\n3 1 2 4 5 6\n3 1 2 4 6 5\n3 1 2 5 4 6\n3 1 2 5 6 4\n3 1 2 6 4 5\n3 1 2 6 5 4\n3 1 4 2 5 6\n3 1 4 2 6 5\n3 1 4 5 2 6\n3 1 4 5 6 2\n3 1 4 6 2 5\n3 1 4 6 5 2\n3 1 5 2 4 6\n3 1 5 2 6 4\n3 1 5 4 2 6\n3 1 5 4 6 2\n3 1 5 6 2 4\n3 1 5 6 4 2\n3 1 6 2 4 5\n3 1 6 2 5 4\n3 1 6 4 2 5\n3 1 6 4 5 2\n3 1 6 5 2 4\n3 1 6 5 4 2\n3 2 1 4 5 6\n3 2 1 4 6 5\n3 2 1 5 4 6\n3 2 1 5 6 4\n3 2 1 6 4 5\n3 2 1 6 5 4\n3 2 4 1 5 6\n3 2 4 1 6 5\n3 2 4 5 1 6\n3 2 4 5 6 1\n3 2 4 6 1 5\n3 2 4 6 5 1\n3 2 5 1 4 6\n3 2 5 1 6 4\n3 2 5 4 1 6\n3 2 5 4 6 1\n3 2 5 6 1 4\n3 2 5 6 4 1\n3 2 6 1 4 5\n3 2 6 1 5 4\n3 2 6 4 1 5\n3 2 6 4 5 1\n3 2 6 5 1 4\n3 2 6 5 4 1\n3 4 1 2 5 6\n3 4 1 2 6 5\n3 4 1 5 2 6\n3 4 1 5 6 2\n3 4 1 6 2 5\n3 4 1 6 5 2\n3 4 2 1 5 6\n3 4 2 1 6 5\n3 4 2 5 1 6\n3 4 2 5 6 1\n3 4 2 6 1 5\n3 4 2 6 5 1\n3 4 5 1 2 6\n3 4 5 1 6 2\n3 4 5 2 1 6\n3 4 5 2 6 1\n3 4 5 6 1 2\n3 4 5 6 2 1\n3 4 6 1 2 5\n3 4 6 1 5 2\n3 4 6 2 1 5\n3 4 6 2 5 1\n3 4 6 5 1 2\n3 4 6 5 2 1\n3 5 1 2 4 6\n3 5 1 2 6 4\n3 5 1 4 2 6\n3 5 1 4 6 2\n3 5 1 6 2 4\n3 5 1 6 4 2\n3 5 2 1 4 6\n3 5 2 1 6 4\n3 5 2 4 1 6\n3 5 2 4 6 1\n3 5 2 6 1 4\n3 5 2 6 4 1\n3 5 4 1 2 6\n3 5 4 1 6 2\n3 5 4 2 1 6\n3 5 4 2 6 1\n3 5 4 6 1 2\n3 5 4 6 2 1\n3 5 6 1 2 4\n3 5 6 1 4 2\n3 5 6 2 1 4\n3 5 6 2 4 1\n3 5 6 4 1 2\n3 5 6 4 2 1\n3 6 1 2 4 5\n3 6 1 2 5 4\n3 6 1 4 2 5\n3 6 1 4 5 2\n3 6 1 5 2 4\n3 6 1 5 4 2\n3 6 2 1 4 5\n3 6 2 1 5 4\n3 6 2 4 1 5\n3 6 2 4 5 1\n3 6 2 5 1 4\n3 6 2 5 4 1\n3 6 4 1 2 5\n3 6 4 1 5 2\n3 6 4 2 1 5\n3 6 4 2 5 1\n3 6 4 5 1 2\n3 6 4 5 2 1\n3 6 5 1 2 4\n3 6 5 1 4 2\n3 6 5 2 1 4\n3 6 5 2 4 1\n3 6 5 4 1 2\n3 6 5 4 2 1\n4 1 2 3 5 6\n4 1 2 3 6 5\n4 1 2 5 3 6\n4 1 2 5 6 3\n4 1 2 6 3 5\n4 1 2 6 5 3\n4 1 3 2 5 6\n4 1 3 2 6 5\n4 1 3 5 2 6\n4 1 3 5 6 2\n4 1 3 6 2 5\n4 1 3 6 5 2\n4 1 5 2 3 6\n4 1 5 2 6 3\n4 1 5 3 2 6\n4 1 5 3 6 2\n4 1 5 6 2 3\n4 1 5 6 3 2\n4 1 6 2 3 5\n4 1 6 2 5 3\n4 1 6 3 2 5\n4 1 6 3 5 2\n4 1 6 5 2 3\n4 1 6 5 3 2\n4 2 1 3 5 6\n4 2 1 3 6 5\n4 2 1 5 3 6\n4 2 1 5 6 3\n4 2 1 6 3 5\n4 2 1 6 5 3\n4 2 3 1 5 6\n4 2 3 1 6 5\n4 2 3 5 1 6\n4 2 3 5 6 1\n4 2 3 6 1 5\n4 2 3 6 5 1\n4 2 5 1 3 6\n4 2 5 1 6 3\n4 2 5 3 1 6\n4 2 5 3 6 1\n4 2 5 6 1 3\n4 2 5 6 3 1\n4 2 6 1 3 5\n4 2 6 1 5 3\n4 2 6 3 1 5\n4 2 6 3 5 1\n4 2 6 5 1 3\n4 2 6 5 3 1\n4 3 1 2 5 6\n4 3 1 2 6 5\n4 3 1 5 2 6\n4 3 1 5 6 2\n4 3 1 6 2 5\n4 3 1 6 5 2\n4 3 2 1 5 6\n4 3 2 1 6 5\n4 3 2 5 1 6\n4 3 2 5 6 1\n4 3 2 6 1 5\n4 3 2 6 5 1\n4 3 5 1 2 6\n4 3 5 1 6 2\n4 3 5 2 1 6\n4 3 5 2 6 1\n4 3 5 6 1 2\n4 3 5 6 2 1\n4 3 6 1 2 5\n4 3 6 1 5 2\n4 3 6 2 1 5\n4 3 6 2 5 1\n4 3 6 5 1 2\n4 3 6 5 2 1\n4 5 1 2 3 6\n4 5 1 2 6 3\n4 5 1 3 2 6\n4 5 1 3 6 2\n4 5 1 6 2 3\n4 5 1 6 3 2\n4 5 2 1 3 6\n4 5 2 1 6 3\n4 5 2 3 1 6\n4 5 2 3 6 1\n4 5 2 6 1 3\n4 5 2 6 3 1\n4 5 3 1 2 6\n4 5 3 1 6 2\n4 5 3 2 1 6\n4 5 3 2 6 1\n4 5 3 6 1 2\n4 5 3 6 2 1\n4 5 6 1 2 3\n4 5 6 1 3 2\n4 5 6 2 1 3\n4 5 6 2 3 1\n4 5 6 3 1 2\n4 5 6 3 2 1\n4 6 1 2 3 5\n4 6 1 2 5 3\n4 6 1 3 2 5\n4 6 1 3 5 2\n4 6 1 5 2 3\n4 6 1 5 3 2\n4 6 2 1 3 5\n4 6 2 1 5 3\n4 6 2 3 1 5\n4 6 2 3 5 1\n4 6 2 5 1 3\n4 6 2 5 3 1\n4 6 3 1 2 5\n4 6 3 1 5 2\n4 6 3 2 1 5\n4 6 3 2 5 1\n4 6 3 5 1 2\n4 6 3 5 2 1\n4 6 5 1 2 3\n4 6 5 1 3 2\n4 6 5 2 1 3\n4 6 5 2 3 1\n4 6 5 3 1 2\n4 6 5 3 2 1\n5 1 2 3 4 6\n5 1 2 3 6 4\n5 1 2 4 3 6\n5 1 2 4 6 3\n5 1 2 6 3 4\n5 1 2 6 4 3\n5 1 3 2 4 6\n5 1 3 2 6 4\n5 1 3 4 2 6\n5 1 3 4 6 2\n5 1 3 6 2 4\n5 1 3 6 4 2\n5 1 4 2 3 6\n5 1 4 2 6 3\n5 1 4 3 2 6\n5 1 4 3 6 2\n5 1 4 6 2 3\n5 1 4 6 3 2\n5 1 6 2 3 4\n5 1 6 2 4 3\n5 1 6 3 2 4\n5 1 6 3 4 2\n5 1 6 4 2 3\n5 1 6 4 3 2\n5 2 1 3 4 6\n5 2 1 3 6 4\n5 2 1 4 3 6\n5 2 1 4 6 3\n5 2 1 6 3 4\n5 2 1 6 4 3\n5 2 3 1 4 6\n5 2 3 1 6 4\n5 2 3 4 1 6\n5 2 3 4 6 1\n5 2 3 6 1 4\n5 2 3 6 4 1\n5 2 4 1 3 6\n5 2 4 1 6 3\n5 2 4 3 1 6\n5 2 4 3 6 1\n5 2 4 6 1 3\n5 2 4 6 3 1\n5 2 6 1 3 4\n5 2 6 1 4 3\n5 2 6 3 1 4\n5 2 6 3 4 1\n5 2 6 4 1 3\n5 2 6 4 3 1\n5 3 1 2 4 6\n5 3 1 2 6 4\n5 3 1 4 2 6\n5 3 1 4 6 2\n5 3 1 6 2 4\n5 3 1 6 4 2\n5 3 2 1 4 6\n5 3 2 1 6 4\n5 3 2 4 1 6\n5 3 2 4 6 1\n5 3 2 6 1 4\n5 3 2 6 4 1\n5 3 4 1 2 6\n5 3 4 1 6 2\n5 3 4 2 1 6\n5 3 4 2 6 1\n5 3 4 6 1 2\n5 3 4 6 2 1\n5 3 6 1 2 4\n5 3 6 1 4 2\n5 3 6 2 1 4\n5 3 6 2 4 1\n5 3 6 4 1 2\n5 3 6 4 2 1\n5 4 1 2 3 6\n5 4 1 2 6 3\n5 4 1 3 2 6\n5 4 1 3 6 2\n5 4 1 6 2 3\n5 4 1 6 3 2\n5 4 2 1 3 6\n5 4 2 1 6 3\n5 4 2 3 1 6\n5 4 2 3 6 1\n5 4 2 6 1 3\n5 4 2 6 3 1\n5 4 3 1 2 6\n5 4 3 1 6 2\n5 4 3 2 1 6\n5 4 3 2 6 1\n5 4 3 6 1 2\n5 4 3 6 2 1\n5 4 6 1 2 3\n5 4 6 1 3 2\n5 4 6 2 1 3\n5 4 6 2 3 1\n5 4 6 3 1 2\n5 4 6 3 2 1\n5 6 1 2 3 4\n5 6 1 2 4 3\n5 6 1 3 2 4\n5 6 1 3 4 2\n5 6 1 4 2 3\n5 6 1 4 3 2\n5 6 2 1 3 4\n5 6 2 1 4 3\n5 6 2 3 1 4\n5 6 2 3 4 1\n5 6 2 4 1 3\n5 6 2 4 3 1\n5 6 3 1 2 4\n5 6 3 1 4 2\n5 6 3 2 1 4\n5 6 3 2 4 1\n5 6 3 4 1 2\n5 6 3 4 2 1\n5 6 4 1 2 3\n5 6 4 1 3 2\n5 6 4 2 1 3\n5 6 4 2 3 1\n5 6 4 3 1 2\n5 6 4 3 2 1\n6 1 2 3 4 5\n6 1 2 3 5 4\n6 1 2 4 3 5\n6 1 2 4 5 3\n6 1 2 5 3 4\n6 1 2 5 4 3\n6 1 3 2 4 5\n6 1 3 2 5 4\n6 1 3 4 2 5\n6 1 3 4 5 2\n6 1 3 5 2 4\n6 1 3 5 4 2\n6 1 4 2 3 5\n6 1 4 2 5 3\n6 1 4 3 2 5\n6 1 4 3 5 2\n6 1 4 5 2 3\n6 1 4 5 3 2\n6 1 5 2 3 4\n6 1 5 2 4 3\n6 1 5 3 2 4\n6 1 5 3 4 2\n6 1 5 4 2 3\n6 1 5 4 3 2\n6 2 1 3 4 5\n6 2 1 3 5 4\n6 2 1 4 3 5\n6 2 1 4 5 3\n6 2 1 5 3 4\n6 2 1 5 4 3\n6 2 3 1 4 5\n6 2 3 1 5 4\n6 2 3 4 1 5\n6 2 3 4 5 1\n6 2 3 5 1 4\n6 2 3 5 4 1\n6 2 4 1 3 5\n6 2 4 1 5 3\n6 2 4 3 1 5\n6 2 4 3 5 1\n6 2 4 5 1 3\n6 2 4 5 3 1\n6 2 5 1 3 4\n6 2 5 1 4 3\n6 2 5 3 1 4\n6 2 5 3 4 1\n6 2 5 4 1 3\n6 2 5 4 3 1\n6 3 1 2 4 5\n6 3 1 2 5 4\n6 3 1 4 2 5\n6 3 1 4 5 2\n6 3 1 5 2 4\n6 3 1 5 4 2\n6 3 2 1 4 5\n6 3 2 1 5 4\n6 3 2 4 1 5\n6 3 2 4 5 1\n6 3 2 5 1 4\n6 3 2 5 4 1\n6 3 4 1 2 5\n6 3 4 1 5 2\n6 3 4 2 1 5\n6 3 4 2 5 1\n6 3 4 5 1 2\n6 3 4 5 2 1\n6 3 5 1 2 4\n6 3 5 1 4 2\n6 3 5 2 1 4\n6 3 5 2 4 1\n6 3 5 4 1 2\n6 3 5 4 2 1\n6 4 1 2 3 5\n6 4 1 2 5 3\n6 4 1 3 2 5\n6 4 1 3 5 2\n6 4 1 5 2 3\n6 4 1 5 3 2\n6 4 2 1 3 5\n6 4 2 1 5 3\n6 4 2 3 1 5\n6 4 2 3 5 1\n6 4 2 5 1 3\n6 4 2 5 3 1\n6 4 3 1 2 5\n6 4 3 1 5 2\n6 4 3 2 1 5\n6 4 3 2 5 1\n6 4 3 5 1 2\n6 4 3 5 2 1\n6 4 5 1 2 3\n6 4 5 1 3 2\n6 4 5 2 1 3\n6 4 5 2 3 1\n6 4 5 3 1 2\n6 4 5 3 2 1\n6 5 1 2 3 4\n6 5 1 2 4 3\n6 5 1 3 2 4\n6 5 1 3 4 2\n6 5 1 4 2 3\n6 5 1 4 3 2\n6 5 2 1 3 4\n6 5 2 1 4 3\n6 5 2 3 1 4\n6 5 2 3 4 1\n6 5 2 4 1 3\n6 5 2 4 3 1\n6 5 3 1 2 4\n6 5 3 1 4 2\n6 5 3 2 1 4\n6 5 3 2 4 1\n6 5 3 4 1 2\n6 5 3 4 2 1\n6 5 4 1 2 3\n6 5 4 1 3 2\n6 5 4 2 1 3\n6 5 4 2 3 1\n6 5 4 3 1 2\n6 5 4 3 2 1\n', 0, 6);

-- ---------- 76. 组合输出（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('组合输出', 3, 20, '## 【题目描述】\n\n给定整数 n 和 m，按字典序输出从 1 到 n 中选取 m 个数的所有组合，每个组合占一行，同一行内数字从小到大排列。\n\n## 【输入格式】\n\n一行，两个整数 n、m。\n\n## 【输出格式】\n\n若干行，每行为一个组合。\n\n## 【样例】\n\n输入：\n\n```\n4 2\n```\n\n输出：\n\n```\n1 2\n1 3\n1 4\n2 3\n2 4\n3 4\n```\n\n## 【数据范围】\n\n1 ≤ m ≤ n ≤ 10\n\n## 【提示】\n\n组合与排列的区别是"不考虑顺序"，因此每层从 start 开始枚举并保证递增，避免重复（这正是组合不去重的常用技巧）。', '一行，两个整数 n、m。', '若干行，每行为一个组合。',
 '4 2', '1 2\n1 3\n1 4\n2 3\n2 4\n3 4', '组合与排列的区别是"不考虑顺序"，因此每层从 start 开始枚举并保证递增，避免重复（这正是组合不去重的常用技巧）。', 'import sys\n\nn, m = map(int, sys.stdin.read().split())\npath = []\nout = []\n\n\ndef dfs(start):\n    if len(path) == m:\n        out.append(" ".join(map(str, path)))\n        return\n    for i in range(start, n + 1):\n        path.append(i)\n        dfs(i + 1)\n        path.pop()\n\n\ndfs(1)\nprint("\\n".join(out))\n', 'python',
 'DFS,回溯,组合', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '4 2', '1 2\n1 3\n1 4\n2 3\n2 4\n3 4\n', 1, 1),
(@aid, '8 3', '1 2 3\n1 2 4\n1 2 5\n1 2 6\n1 2 7\n1 2 8\n1 3 4\n1 3 5\n1 3 6\n1 3 7\n1 3 8\n1 4 5\n1 4 6\n1 4 7\n1 4 8\n1 5 6\n1 5 7\n1 5 8\n1 6 7\n1 6 8\n1 7 8\n2 3 4\n2 3 5\n2 3 6\n2 3 7\n2 3 8\n2 4 5\n2 4 6\n2 4 7\n2 4 8\n2 5 6\n2 5 7\n2 5 8\n2 6 7\n2 6 8\n2 7 8\n3 4 5\n3 4 6\n3 4 7\n3 4 8\n3 5 6\n3 5 7\n3 5 8\n3 6 7\n3 6 8\n3 7 8\n4 5 6\n4 5 7\n4 5 8\n4 6 7\n4 6 8\n4 7 8\n5 6 7\n5 6 8\n5 7 8\n6 7 8\n', 0, 2),
(@aid, '2 2', '1 2\n', 0, 3),
(@aid, '1 1', '1\n', 0, 4),
(@aid, '8 6', '1 2 3 4 5 6\n1 2 3 4 5 7\n1 2 3 4 5 8\n1 2 3 4 6 7\n1 2 3 4 6 8\n1 2 3 4 7 8\n1 2 3 5 6 7\n1 2 3 5 6 8\n1 2 3 5 7 8\n1 2 3 6 7 8\n1 2 4 5 6 7\n1 2 4 5 6 8\n1 2 4 5 7 8\n1 2 4 6 7 8\n1 2 5 6 7 8\n1 3 4 5 6 7\n1 3 4 5 6 8\n1 3 4 5 7 8\n1 3 4 6 7 8\n1 3 5 6 7 8\n1 4 5 6 7 8\n2 3 4 5 6 7\n2 3 4 5 6 8\n2 3 4 5 7 8\n2 3 4 6 7 8\n2 3 5 6 7 8\n2 4 5 6 7 8\n3 4 5 6 7 8\n', 0, 5),
(@aid, '6 6', '1 2 3 4 5 6\n', 0, 6);

-- ---------- 77. N 皇后问题（难度 4） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('N 皇后问题', 4, 30, '## 【题目描述】\n\n在 n × n 的棋盘上放置 n 个皇后，使它们互不攻击（不同行、不同列、不同对角线）。求满足条件的方案总数。\n\n## 【输入格式】\n\n一行，一个整数 n。\n\n## 【输出格式】\n\n一行，一个整数，表示方案数。\n\n## 【样例】\n\n输入：\n\n```\n4\n```\n\n输出：\n\n```\n2\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10\n\n## 【提示】\n\n按行放置，用三个布尔数组记录列与两条对角线（主对角线 row+c 为常数，副对角线 row-c+n 为常数）是否被占用，即可 O(1) 判断冲突。', '一行，一个整数 n。', '一行，一个整数，表示方案数。',
 '4', '2', '按行放置，用三个布尔数组记录列与两条对角线（主对角线 row+c 为常数，副对角线 row-c+n 为常数）是否被占用，即可 O(1) 判断冲突。', 'import sys\n\nn = int(sys.stdin.read().strip())\ncol = [False] * n\nd1 = [False] * (2 * n)\nd2 = [False] * (2 * n)\nans = 0\n\n\ndef dfs(row):\n    global ans\n    if row == n:\n        ans += 1\n        return\n    for c in range(n):\n        if col[c] or d1[row + c] or d2[row - c + n]:\n            continue\n        col[c] = d1[row + c] = d2[row - c + n] = True\n        dfs(row + 1)\n        col[c] = d1[row + c] = d2[row - c + n] = False\n\n\ndfs(0)\nprint(ans)\n', 'python',
 'DFS,回溯,经典', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '4', '2\n', 1, 1),
(@aid, '2', '0\n', 0, 2),
(@aid, '1', '1\n', 0, 3),
(@aid, '2', '0\n', 0, 4),
(@aid, '4', '2\n', 0, 5),
(@aid, '5', '10\n', 0, 6);

-- ---------- 78. 迷宫路径计数（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('迷宫路径计数', 3, 20, '## 【题目描述】\n\n给定一个 n 行 m 列的迷宫，"." 表示可通行、"#" 表示障碍。从左上角走到右下角，每次只能向右或向下移动一步，求不同的路径条数。\n\n## 【输入格式】\n\n第一行两个整数 n、m；接下来 n 行，每行一个长度为 m 的字符串。\n\n## 【输出格式】\n\n一行，一个整数，表示路径条数。\n\n## 【样例】\n\n输入：\n\n```\n3 3\n...\n.#.\n...\n```\n\n输出：\n\n```\n2\n```\n\n## 【数据范围】\n\n1 ≤ n, m ≤ 100\n\n## 【提示】\n\n只能向右/向下时，到达 (i, j) 的路径数 = 上方 + 左方，这是最基础的二维递推；若允许四个方向则需要搜索。', '第一行两个整数 n、m；接下来 n 行，每行一个长度为 m 的字符串。', '一行，一个整数，表示路径条数。',
 '3 3\n...\n.#.\n...', '2', '只能向右/向下时，到达 (i, j) 的路径数 = 上方 + 左方，这是最基础的二维递推；若允许四个方向则需要搜索。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nm = int(data[1])\ngrid = data[2:2 + n]\ndp = [[0] * m for _ in range(n)]\nfor i in range(n):\n    for j in range(m):\n        if grid[i][j] == "#":\n            continue\n        if i == 0 and j == 0:\n            dp[i][j] = 1\n        else:\n            dp[i][j] = (dp[i - 1][j] if i > 0 else 0) + (dp[i][j - 1] if j > 0 else 0)\nprint(dp[n - 1][m - 1])\n', 'python',
 '动态规划,递推,迷宫', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3 3\n...\n.#.\n...', '2\n', 1, 1),
(@aid, '2 4\n....\n..#.', '1\n', 0, 2),
(@aid, '8 3\n...\n.#.\n...\n...\n..#\n.#.\n.##\n...', '1\n', 0, 3),
(@aid, '5 6\n....#.\n.#...#\n..#...\n.....#\n......', '17\n', 0, 4),
(@aid, '3 3\n.#.\n...\n...', '3\n', 0, 5),
(@aid, '5 2\n..\n#.\n..\n.#\n#.', '0\n', 0, 6);

-- ---------- 79. 迷宫最短步数（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('迷宫最短步数', 3, 20, '## 【题目描述】\n\n给定一个 n 行 m 列的迷宫，"." 可通行、"#" 为障碍。从左上角走到右下角，每次可上下左右移动一步，求最少步数；若无法到达输出 -1。\n\n## 【输入格式】\n\n第一行两个整数 n、m；接下来 n 行，每行一个长度为 m 的字符串。\n\n## 【输出格式】\n\n一行，一个整数，表示最少步数或 -1。\n\n## 【样例】\n\n输入：\n\n```\n3 3\n...\n.#.\n...\n```\n\n输出：\n\n```\n4\n```\n\n## 【数据范围】\n\n1 ≤ n, m ≤ 100\n\n## 【提示】\n\n边权均为 1 的无权图最短路用 BFS：首次到达某点的步数即最短距离，复杂度 O(nm)。', '第一行两个整数 n、m；接下来 n 行，每行一个长度为 m 的字符串。', '一行，一个整数，表示最少步数或 -1。',
 '3 3\n...\n.#.\n...', '4', '边权均为 1 的无权图最短路用 BFS：首次到达某点的步数即最短距离，复杂度 O(nm)。', 'import sys\nfrom collections import deque\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nm = int(data[1])\ngrid = data[2:2 + n]\ndist = [[-1] * m for _ in range(n)]\ndist[0][0] = 0\nq = deque([(0, 0)])\nwhile q:\n    i, j = q.popleft()\n    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):\n        x, y = i + di, j + dj\n        if 0 <= x < n and 0 <= y < m and grid[x][y] == "." and dist[x][y] == -1:\n            dist[x][y] = dist[i][j] + 1\n            q.append((x, y))\nprint(dist[n - 1][m - 1])\n', 'python',
 'BFS,最短路,迷宫', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3 3\n...\n.#.\n...', '4\n', 1, 1),
(@aid, '5 7\n.#....#\n...#...\n##...#.\n##.....\n...#...', '10\n', 0, 2),
(@aid, '7 3\n.#.\n...\n...\n...\n...\n.#.\n...', '8\n', 0, 3),
(@aid, '6 2\n..\n.#\n#.\n..\n..\n#.', '-1\n', 0, 4),
(@aid, '7 4\n.#..\n.#..\n.###\n.#..\n##..\n.#..\n#...', '-1\n', 0, 5),
(@aid, '4 2\n..\n..\n..\n..', '4\n', 0, 6);

-- ---------- 80. 素数环（难度 4） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('素数环', 4, 30, '## 【题目描述】\n\n把 1 到 n 这 n 个数排成一个环，使得环上任意相邻两个数（含首尾）之和都是素数。求满足条件的环的个数（旋转与镜像视为不同的方案，按第一个数固定为 1 的方式计数）。\n\n## 【输入格式】\n\n一行，一个整数 n。\n\n## 【输出格式】\n\n一行，一个整数，表示方案数。\n\n## 【样例】\n\n输入：\n\n```\n6\n```\n\n输出：\n\n```\n2\n```\n\n## 【数据范围】\n\n2 ≤ n ≤ 12\n\n## 【提示】\n\n固定第一个数为 1 可消除旋转重复；每次尝试放一个未使用的数，要求与上一个数之和为素数，最后还要检查首尾之和。', '一行，一个整数 n。', '一行，一个整数，表示方案数。',
 '6', '2', '固定第一个数为 1 可消除旋转重复；每次尝试放一个未使用的数，要求与上一个数之和为素数，最后还要检查首尾之和。', 'import sys\n\nn = int(sys.stdin.read().strip())\n\n\ndef is_prime(x):\n    if x < 2:\n        return False\n    i = 2\n    while i * i <= x:\n        if x % i == 0:\n            return False\n        i += 1\n    return True\n\n\nused = [False] * (n + 1)\npath = [1]\nused[1] = True\nans = 0\n\n\ndef dfs():\n    global ans\n    if len(path) == n:\n        if is_prime(path[-1] + 1):\n            ans += 1\n        return\n    for x in range(2, n + 1):\n        if not used[x] and is_prime(path[-1] + x):\n            used[x] = True\n            path.append(x)\n            dfs()\n            path.pop()\n            used[x] = False\n\n\ndfs()\nprint(ans)\n', 'python',
 'DFS,回溯,素数,经典', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '6', '2\n', 1, 1),
(@aid, '6', '2\n', 0, 2),
(@aid, '6', '2\n', 0, 3),
(@aid, '4', '2\n', 0, 4),
(@aid, '4', '2\n', 0, 5),
(@aid, '2', '1\n', 0, 6);

-- ---------- 81. 子集枚举（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('子集枚举', 3, 20, '## 【题目描述】\n\n给定整数 n，输出集合 {1, 2, …, n} 的所有子集（含空集），每个子集占一行，元素之间用空格分隔，空集输出空行。\n\n## 【输入格式】\n\n一行，一个整数 n。\n\n## 【输出格式】\n\n2ⁿ 行，每行为一个子集（空集为一行空字符串）。\n\n## 【样例】\n\n输入：\n\n```\n3\n```\n\n输出：\n\n```\n\n1\n2\n1 2\n3\n1 3\n2 3\n1 2 3\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10\n\n## 【提示】\n\n每个元素有"选/不选"两种分支，递归深度为 n，共 2ⁿ 个叶子；也可用 n 位二进制掩码从 0 枚举到 2ⁿ-1。', '一行，一个整数 n。', '2ⁿ 行，每行为一个子集（空集为一行空字符串）。',
 '3', '\n1\n2\n1 2\n3\n1 3\n2 3\n1 2 3', '每个元素有"选/不选"两种分支，递归深度为 n，共 2ⁿ 个叶子；也可用 n 位二进制掩码从 0 枚举到 2ⁿ-1。', 'import sys\n\nn = int(sys.stdin.read().strip())\nout = []\nfor mask in range(1 << n):\n    out.append(" ".join(str(i + 1) for i in range(n) if mask >> i & 1))\nprint("\\n".join(out))\n', 'python',
 'DFS,回溯,子集', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3', '\n1\n2\n1 2\n3\n1 3\n2 3\n1 2 3\n', 1, 1),
(@aid, '1', '\n1\n', 0, 2),
(@aid, '4', '\n1\n2\n1 2\n3\n1 3\n2 3\n1 2 3\n4\n1 4\n2 4\n1 2 4\n3 4\n1 3 4\n2 3 4\n1 2 3 4\n', 0, 3),
(@aid, '2', '\n1\n2\n1 2\n', 0, 4),
(@aid, '1', '\n1\n', 0, 5),
(@aid, '4', '\n1\n2\n1 2\n3\n1 3\n2 3\n1 2 3\n4\n1 4\n2 4\n1 2 4\n3 4\n1 3 4\n2 3 4\n1 2 3 4\n', 0, 6);

-- ---------- 82. 数的划分（难度 4） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('数的划分', 4, 30, '## 【题目描述】\n\n把正整数 n 划分成 k 个正整数的和（不考虑顺序，如 5 = 1 + 4 与 5 = 4 + 1 视为同一种），求划分方案数。\n\n## 【输入格式】\n\n一行，两个整数 n、k。\n\n## 【输出格式】\n\n一行，一个整数，表示方案数。\n\n## 【样例】\n\n输入：\n\n```\n7 3\n```\n\n输出：\n\n```\n4\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 100，1 ≤ k ≤ 6\n\n## 【提示】\n\n为避免重复，规定划分出的数不递减（每层从 start 开始枚举）；剪枝：若剩余部分即使全取 x 也不够则提前 break。', '一行，两个整数 n、k。', '一行，一个整数，表示方案数。',
 '7 3', '4', '为避免重复，规定划分出的数不递减（每层从 start 开始枚举）；剪枝：若剩余部分即使全取 x 也不够则提前 break。', 'import sys\n\nn, k = map(int, sys.stdin.read().split())\nans = 0\npath = []\n\n\ndef dfs(remain, cnt, start):\n    global ans\n    if cnt == k:\n        if remain == 0:\n            ans += 1\n        return\n    for x in range(start, remain + 1):\n        if x * (k - cnt) > remain:\n            break\n        dfs(remain - x, cnt + 1, x)\n\n\ndfs(n, 0, 1)\nprint(ans)\n', 'python',
 'DFS,回溯,整数划分', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '7 3', '4\n', 1, 1),
(@aid, '7 2', '3\n', 0, 2),
(@aid, '14 2', '7\n', 0, 3),
(@aid, '9 4', '6\n', 0, 4),
(@aid, '10 3', '8\n', 0, 5),
(@aid, '9 5', '5\n', 0, 6);

-- ---------- 83. 连通块计数（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('连通块计数', 3, 20, '## 【题目描述】\n\n给定一个 n 行 m 列的 0/1 矩阵，求其中四连通（上下左右）的 1 构成的连通块个数。\n\n## 【输入格式】\n\n第一行两个整数 n、m；接下来 n 行，每行 m 个 0 或 1，用空格分隔。\n\n## 【输出格式】\n\n一行，一个整数，表示连通块个数。\n\n## 【样例】\n\n输入：\n\n```\n3 4\n1 1 0 0\n0 1 0 1\n0 0 1 1\n```\n\n输出：\n\n```\n2\n```\n\n## 【数据范围】\n\n1 ≤ n, m ≤ 100\n\n## 【提示】\n\n洪水填充（Flood Fill）：遇到未访问的 1 就计数并把整个连通块标记为已访问。DFS/BFS/并查集都可以，复杂度 O(nm)。', '第一行两个整数 n、m；接下来 n 行，每行 m 个 0 或 1，用空格分隔。', '一行，一个整数，表示连通块个数。',
 '3 4\n1 1 0 0\n0 1 0 1\n0 0 1 1', '2', '洪水填充（Flood Fill）：遇到未访问的 1 就计数并把整个连通块标记为已访问。DFS/BFS/并查集都可以，复杂度 O(nm)。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nm = int(data[1])\ngrid = [list(map(int, data[2 + i * m:2 + (i + 1) * m])) for i in range(n)]\nseen = [[False] * m for _ in range(n)]\nans = 0\nfor i in range(n):\n    for j in range(m):\n        if grid[i][j] == 1 and not seen[i][j]:\n            ans += 1\n            stack = [(i, j)]\n            seen[i][j] = True\n            while stack:\n                x, y = stack.pop()\n                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):\n                    a, b = x + dx, y + dy\n                    if 0 <= a < n and 0 <= b < m and grid[a][b] == 1 and not seen[a][b]:\n                        seen[a][b] = True\n                        stack.append((a, b))\nprint(ans)\n', 'python',
 'DFS,BFS,连通块', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3 4\n1 1 0 0\n0 1 0 1\n0 0 1 1', '2\n', 1, 1),
(@aid, '3 5\n1 1 1 0 1\n1 0 1 1 1\n1 0 0 0 0', '1\n', 0, 2),
(@aid, '5 6\n0 1 1 1 0 0\n1 0 1 0 0 0\n0 0 1 1 1 1\n0 0 1 0 1 1\n0 1 0 0 0 1', '3\n', 0, 3),
(@aid, '8 9\n0 1 1 1 0 1 1 0 0\n1 0 1 0 1 0 0 1 1\n1 1 0 0 0 0 0 0 0\n0 0 0 0 0 1 0 0 0\n1 1 1 0 1 1 0 0 1\n1 1 1 0 0 0 0 1 1\n0 1 1 0 0 0 0 1 1\n0 1 0 0 0 1 1 0 1', '9\n', 0, 4),
(@aid, '4 8\n0 1 0 1 0 1 0 1\n1 0 0 0 0 1 1 0\n1 0 0 1 0 1 0 0\n0 1 1 1 0 0 0 1', '7\n', 0, 5),
(@aid, '7 8\n0 1 1 1 1 1 1 1\n1 1 0 0 1 1 1 1\n0 1 0 1 0 1 1 1\n1 0 0 0 0 1 0 1\n0 1 1 0 0 1 1 0\n1 1 1 1 1 1 1 0\n1 0 0 1 0 1 1 1', '3\n', 0, 6);

-- ---------- 84. 最大连通块大小（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('最大连通块大小', 3, 20, '## 【题目描述】\n\n给定一个 n 行 m 列的 0/1 矩阵，求其中四连通的 1 构成的连通块中，包含元素个数最多的那个块的大小。\n\n## 【输入格式】\n\n第一行两个整数 n、m；接下来 n 行，每行 m 个 0 或 1，用空格分隔。\n\n## 【输出格式】\n\n一行，一个整数，表示最大连通块的大小（全为 0 时输出 0）。\n\n## 【样例】\n\n输入：\n\n```\n3 4\n1 1 0 0\n0 1 0 1\n0 0 1 1\n```\n\n输出：\n\n```\n3\n```\n\n## 【数据范围】\n\n1 ≤ n, m ≤ 100\n\n## 【提示】\n\n与连通块计数同框架，只是在每次洪水填充时统计块内元素个数并更新最大值。', '第一行两个整数 n、m；接下来 n 行，每行 m 个 0 或 1，用空格分隔。', '一行，一个整数，表示最大连通块的大小（全为 0 时输出 0）。',
 '3 4\n1 1 0 0\n0 1 0 1\n0 0 1 1', '3', '与连通块计数同框架，只是在每次洪水填充时统计块内元素个数并更新最大值。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nm = int(data[1])\ngrid = [list(map(int, data[2 + i * m:2 + (i + 1) * m])) for i in range(n)]\nseen = [[False] * m for _ in range(n)]\nbest = 0\nfor i in range(n):\n    for j in range(m):\n        if grid[i][j] == 1 and not seen[i][j]:\n            size = 0\n            stack = [(i, j)]\n            seen[i][j] = True\n            while stack:\n                x, y = stack.pop()\n                size += 1\n                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):\n                    a, b = x + dx, y + dy\n                    if 0 <= a < n and 0 <= b < m and grid[a][b] == 1 and not seen[a][b]:\n                        seen[a][b] = True\n                        stack.append((a, b))\n            best = max(best, size)\nprint(best)\n', 'python',
 'DFS,BFS,连通块', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3 4\n1 1 0 0\n0 1 0 1\n0 0 1 1', '3\n', 1, 1),
(@aid, '8 4\n1 1 0 0\n1 1 0 0\n1 0 1 1\n1 0 0 1\n1 0 0 0\n1 1 0 1\n1 1 0 1\n0 1 1 1', '16\n', 0, 2),
(@aid, '3 7\n1 0 1 1 0 0 0\n0 0 0 1 1 0 0\n1 1 0 0 0 1 1', '4\n', 0, 3),
(@aid, '4 9\n1 1 0 0 0 1 1 1 0\n0 0 0 0 0 1 1 1 1\n1 0 1 1 1 1 0 1 0\n0 0 0 0 0 1 0 1 1', '15\n', 0, 4),
(@aid, '6 2\n0 1\n1 0\n0 0\n0 1\n0 0\n1 1', '2\n', 0, 5),
(@aid, '10 10\n1 1 0 1 0 0 1 1 1 1\n0 0 0 1 0 1 1 0 0 1\n1 0 1 1 0 0 0 1 1 0\n0 0 0 1 0 1 1 1 0 1\n0 0 1 1 0 1 0 0 1 0\n0 1 1 1 1 1 0 0 0 1\n0 1 0 0 0 1 0 0 0 1\n1 1 1 1 1 1 0 1 0 0\n1 1 0 0 0 0 0 0 0 1\n1 1 1 0 0 0 1 0 0 0', '31\n', 0, 6);

-- ---------- 85. 图的连通性判断（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('图的连通性判断', 3, 20, '## 【题目描述】\n\n给定一个有 n 个结点、m 条边的无向图，判断它是否连通（任意两点之间都存在路径）。\n\n## 【输入格式】\n\n第一行两个整数 n、m；接下来 m 行，每行两个整数 u、v，表示一条无向边。\n\n## 【输出格式】\n\n一行，连通输出 Yes，否则输出 No。\n\n## 【样例】\n\n输入：\n\n```\n4 3\n1 2\n2 3\n3 4\n```\n\n输出：\n\n```\nYes\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁵，0 ≤ m ≤ 10⁵\n\n## 【提示】\n\n从 1 号点做一次 DFS/BFS，统计访问到的点数是否等于 n。也可用并查集把所有边合并后看是否只有一个集合。', '第一行两个整数 n、m；接下来 m 行，每行两个整数 u、v，表示一条无向边。', '一行，连通输出 Yes，否则输出 No。',
 '4 3\n1 2\n2 3\n3 4', 'Yes', '从 1 号点做一次 DFS/BFS，统计访问到的点数是否等于 n。也可用并查集把所有边合并后看是否只有一个集合。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nm = int(data[1])\nadj = [[] for _ in range(n + 1)]\nfor i in range(m):\n    u = int(data[2 + 2 * i])\n    v = int(data[3 + 2 * i])\n    adj[u].append(v)\n    adj[v].append(u)\nseen = [False] * (n + 1)\nseen[1] = True\nstack = [1]\ncnt = 1\nwhile stack:\n    x = stack.pop()\n    for y in adj[x]:\n        if not seen[y]:\n            seen[y] = True\n            cnt += 1\n            stack.append(y)\nprint("Yes" if cnt == n else "No")\n', 'python',
 'DFS,BFS,图,连通性', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '4 3\n1 2\n2 3\n3 4', 'Yes\n', 1, 1),
(@aid, '5 11\n5 4\n3 3\n1 1\n4 5\n2 5\n2 1\n3 5\n2 5\n5 4\n1 2\n5 5', 'Yes\n', 0, 2),
(@aid, '13 14\n10 11\n9 4\n10 7\n2 10\n13 11\n11 8\n4 5\n7 5\n6 13\n6 5\n10 6\n10 13\n11 1\n11 1', 'No\n', 0, 3),
(@aid, '9 24\n2 3\n5 4\n8 7\n2 6\n4 4\n9 1\n1 6\n6 2\n5 9\n5 1\n2 7\n2 8\n2 1\n9 2\n6 3\n6 6\n6 8\n7 3\n4 2\n3 1\n6 9\n6 9\n7 2\n7 6', 'Yes\n', 0, 4),
(@aid, '5 27\n1 4\n5 4\n3 3\n1 1\n4 3\n3 1\n3 4\n3 4\n5 5\n1 4\n4 4\n1 4\n1 4\n4 4\n3 2\n3 4\n1 3\n2 5\n3 3\n1 1\n3 4\n4 2\n3 5\n1 1\n2 4\n2 3\n5 4', 'Yes\n', 0, 5),
(@aid, '20 2\n5 16\n16 7', 'No\n', 0, 6);

-- ---------- 86. 可达性判断（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('可达性判断', 3, 20, '## 【题目描述】\n\n给定一个 n 行 m 列的迷宫（"." 可通行、"#" 为障碍）和起点、终点坐标，判断从起点能否走到终点（可上下左右移动）。\n\n## 【输入格式】\n\n第一行两个整数 n、m；接下来 n 行迷宫；最后一行四个整数 sx、sy、tx、ty，表示起点与终点坐标（行、列均从 1 开始）。\n\n## 【输出格式】\n\n一行，能到达输出 Yes，否则输出 No。\n\n## 【样例】\n\n输入：\n\n```\n3 3\n...\n.#.\n...\n1 1 3 3\n```\n\n输出：\n\n```\nYes\n```\n\n## 【数据范围】\n\n1 ≤ n, m ≤ 100\n\n## 【提示】\n\n只需判断可达性时，BFS 一旦弹出终点即可提前结束，不必遍历完整个图。', '第一行两个整数 n、m；接下来 n 行迷宫；最后一行四个整数 sx、sy、tx、ty，表示起点与终点坐标（行、列均从 1 开始）。', '一行，能到达输出 Yes，否则输出 No。',
 '3 3\n...\n.#.\n...\n1 1 3 3', 'Yes', '只需判断可达性时，BFS 一旦弹出终点即可提前结束，不必遍历完整个图。', 'import sys\nfrom collections import deque\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nm = int(data[1])\ngrid = data[2:2 + n]\nsx = int(data[2 + n]); sy = int(data[3 + n]); tx = int(data[4 + n]); ty = int(data[5 + n])\nseen = [[False] * m for _ in range(n)]\nq = deque([(sx - 1, sy - 1)])\nseen[sx - 1][sy - 1] = True\nok = False\nwhile q:\n    i, j = q.popleft()\n    if (i, j) == (tx - 1, ty - 1):\n        ok = True\n        break\n    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):\n        x, y = i + di, j + dj\n        if 0 <= x < n and 0 <= y < m and grid[x][y] == "." and not seen[x][y]:\n            seen[x][y] = True\n            q.append((x, y))\nprint("Yes" if ok else "No")\n', 'python',
 'BFS,迷宫,可达性', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3 3\n...\n.#.\n...\n1 1 3 3', 'Yes\n', 1, 1),
(@aid, '6 7\n..####.\n..#.#..\n.......\n#.###.#\n..#.#.#\n.#.#...\n1 1 6 7', 'Yes\n', 0, 2),
(@aid, '8 8\n......##\n....##..\n.##...#.\n....#...\n.#..#..#\n.......#\n.....#.#\n........\n1 1 8 8', 'Yes\n', 0, 3),
(@aid, '8 3\n.#.\n#.#\n.#.\n.##\n...\n...\n.#.\n...\n1 1 8 3', 'No\n', 0, 4),
(@aid, '7 5\n..#..\n.#...\n.....\n.#...\n.#...\n.....\n...#.\n1 1 7 5', 'Yes\n', 0, 5),
(@aid, '5 4\n....\n.#..\n..##\n....\n.#..\n1 1 5 4', 'Yes\n', 0, 6);

-- ---------- 87. 选数求和为素数（难度 4） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('选数求和为素数', 4, 30, '## 【题目描述】\n\n给定 n 个整数和整数 k，从中选出 k 个数（不要求连续），求这 k 个数之和为素数的选法总数。\n\n## 【输入格式】\n\n第一行两个整数 n、k；第二行 n 个整数。\n\n## 【输出格式】\n\n一行，一个整数，表示选法总数。\n\n## 【样例】\n\n输入：\n\n```\n4 2\n1 2 3 4\n```\n\n输出：\n\n```\n4\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 20，1 ≤ k ≤ n\n\n## 【提示】\n\n组合型枚举（每层从 start 开始避免重复），到叶子时判断和是否为素数。与"素数环"同属经典回溯题。', '第一行两个整数 n、k；第二行 n 个整数。', '一行，一个整数，表示选法总数。',
 '4 2\n1 2 3 4', '4', '组合型枚举（每层从 start 开始避免重复），到叶子时判断和是否为素数。与"素数环"同属经典回溯题。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nk = int(data[1])\nnums = list(map(int, data[2:2 + n]))\n\n\ndef is_prime(x):\n    if x < 2:\n        return False\n    i = 2\n    while i * i <= x:\n        if x % i == 0:\n            return False\n        i += 1\n    return True\n\n\nans = 0\n\n\ndef dfs(start, cnt, total):\n    global ans\n    if cnt == k:\n        if is_prime(total):\n            ans += 1\n        return\n    for i in range(start, n):\n        dfs(i + 1, cnt + 1, total + nums[i])\n\n\ndfs(0, 0, 0)\nprint(ans)\n', 'python',
 'DFS,回溯,素数,枚举', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '4 2\n1 2 3 4', '4\n', 1, 1),
(@aid, '1 1\n26', '0\n', 0, 2),
(@aid, '1 1\n11', '1\n', 0, 3),
(@aid, '7 3\n18 8 15 17 8 20 14', '11\n', 0, 4),
(@aid, '6 2\n14 27 25 17 3 30', '4\n', 0, 5),
(@aid, '8 1\n11 20 29 1 7 27 17 30', '4\n', 0, 6);

-- ---------- 88. 滑雪（最长下降路径）（难度 4） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('滑雪（最长下降路径）', 4, 30, '## 【题目描述】\n\n给定一个 n 行 m 列的地形高度矩阵，可以从任意点出发，每次只能滑向高度严格更低的相邻格（上下左右）。求最长滑行路径经过的格子数。\n\n## 【输入格式】\n\n第一行两个整数 n、m；接下来 n 行，每行 m 个整数，表示高度。\n\n## 【输出格式】\n\n一行，一个整数，表示最长路径长度。\n\n## 【样例】\n\n输入：\n\n```\n3 3\n1 2 3\n6 5 4\n7 8 9\n```\n\n输出：\n\n```\n9\n```\n\n## 【数据范围】\n\n1 ≤ n, m ≤ 100\n\n## 【提示】\n\n记忆化搜索：dfs(i,j) 表示从该点出发的最长长度，只向更低的格子转移，用 memo 避免重复计算，整体 O(nm)。', '第一行两个整数 n、m；接下来 n 行，每行 m 个整数，表示高度。', '一行，一个整数，表示最长路径长度。',
 '3 3\n1 2 3\n6 5 4\n7 8 9', '9', '记忆化搜索：dfs(i,j) 表示从该点出发的最长长度，只向更低的格子转移，用 memo 避免重复计算，整体 O(nm)。', 'import sys\n\nsys.setrecursionlimit(10000)\ndata = sys.stdin.read().split()\nn = int(data[0])\nm = int(data[1])\nh = [list(map(int, data[2 + i * m:2 + (i + 1) * m])) for i in range(n)]\nmemo = [[0] * m for _ in range(n)]\n\n\ndef dfs(i, j):\n    if memo[i][j]:\n        return memo[i][j]\n    best = 1\n    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):\n        x, y = i + di, j + dj\n        if 0 <= x < n and 0 <= y < m and h[x][y] < h[i][j]:\n            best = max(best, 1 + dfs(x, y))\n    memo[i][j] = best\n    return best\n\n\nprint(max(dfs(i, j) for i in range(n) for j in range(m)))\n', 'python',
 '记忆化搜索,DFS,动态规划', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3 3\n1 2 3\n6 5 4\n7 8 9', '9\n', 1, 1),
(@aid, '7 6\n9 14 5 46 25 38\n15 42 23 29 27 29\n12 27 20 3 31 12\n43 7 38 16 38 41\n2 12 4 5 20 41\n50 31 28 42 42 11\n28 26 45 4 32 43', '5\n', 0, 2),
(@aid, '2 3\n36 17 5\n28 38 1', '4\n', 0, 3),
(@aid, '8 2\n42 33\n50 1\n41 36\n38 15\n29 33\n3 37\n23 28\n22 25', '5\n', 0, 4),
(@aid, '3 6\n12 35 12 22 2 35\n44 15 18 5 6 19\n37 28 23 29 44 14', '6\n', 0, 5),
(@aid, '6 4\n17 16 5 19\n9 36 35 19\n30 26 31 16\n4 47 13 39\n35 2 37 42\n2 31 42 6', '4\n', 0, 6);

-- ---------- 89. 下一个排列（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('下一个排列', 2, 10, '## 【题目描述】\n\n给定一个 1 到 n 的排列，求其字典序的下一个排列；若已是最后一个（完全降序），输出 No。\n\n## 【输入格式】\n\n两行。第一行一个整数 n；第二行 n 个整数，表示一个排列。\n\n## 【输出格式】\n\n一行，下一个排列（用空格分隔）或 No。\n\n## 【样例】\n\n输入：\n\n```\n4\n1 3 4 2\n```\n\n输出：\n\n```\n1 4 2 3\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁴\n\n## 【提示】\n\n标准 next_permutation 三步：从右找第一个 a[i] < a[i+1]；从右找第一个大于 a[i] 的 a[j] 与之交换；翻转 i 之后的部分使其升序。', '两行。第一行一个整数 n；第二行 n 个整数，表示一个排列。', '一行，下一个排列（用空格分隔）或 No。',
 '4\n1 3 4 2', '1 4 2 3', '标准 next_permutation 三步：从右找第一个 a[i] < a[i+1]；从右找第一个大于 a[i] 的 a[j] 与之交换；翻转 i 之后的部分使其升序。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\na = list(map(int, data[1:1 + n]))\ni = n - 2\nwhile i >= 0 and a[i] >= a[i + 1]:\n    i -= 1\nif i < 0:\n    print("No")\nelse:\n    j = n - 1\n    while a[j] <= a[i]:\n        j -= 1\n    a[i], a[j] = a[j], a[i]\n    a[i + 1:] = reversed(a[i + 1:])\n    print(" ".join(map(str, a)))\n', 'python',
 '排列,贪心,构造', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '4\n1 3 4 2', '1 4 2 3\n', 1, 1),
(@aid, '2\n1 2', '2 1\n', 0, 2),
(@aid, '4\n4 1 2 3', '4 1 3 2\n', 0, 3),
(@aid, '8\n6 5 3 2 7 4 1 8', '6 5 3 2 7 4 8 1\n', 0, 4),
(@aid, '5\n3 4 5 1 2', '3 4 5 2 1\n', 0, 5),
(@aid, '7\n1 4 6 5 2 7 3', '1 4 6 5 3 2 7\n', 0, 6);

-- ---------- 90. 汉诺塔步数（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('汉诺塔步数', 2, 10, '## 【题目描述】\n\n给定 n 个圆盘，求按汉诺塔规则（一次移动一个盘，大盘不能放在小盘上）把所有盘子从 A 柱移到 C 柱所需的最少步数。\n\n## 【输入格式】\n\n一行，一个整数 n。\n\n## 【输出格式】\n\n一行，一个整数，表示最少步数。\n\n## 【样例】\n\n输入：\n\n```\n3\n```\n\n输出：\n\n```\n7\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 60\n\n## 【提示】\n\n递推关系 T(n) = 2T(n-1) + 1，解得 T(n) = 2ⁿ - 1：先把 n-1 个移到 B，再移最大盘，最后把 n-1 个移回 C。', '一行，一个整数 n。', '一行，一个整数，表示最少步数。',
 '3', '7', '递推关系 T(n) = 2T(n-1) + 1，解得 T(n) = 2ⁿ - 1：先把 n-1 个移到 B，再移最大盘，最后把 n-1 个移回 C。', 'import sys\n\nn = int(sys.stdin.read().strip())\nprint(2 ** n - 1)\n', 'python',
 '递归,递推,经典', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3', '7\n', 1, 1),
(@aid, '26', '67108863\n', 0, 2),
(@aid, '26', '67108863\n', 0, 3),
(@aid, '3', '7\n', 0, 4),
(@aid, '19', '524287\n', 0, 5),
(@aid, '9', '511\n', 0, 6);

-- ---------- 91. 十进制转二进制（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('十进制转二进制', 2, 10, '## 【题目描述】\n\n给定一个非负整数，输出它的二进制表示（不含前导零）。\n\n## 【输入格式】\n\n一行，一个非负整数 x。\n\n## 【输出格式】\n\n一行，一个字符串，为 x 的二进制表示。\n\n## 【样例】\n\n输入：\n\n```\n13\n```\n\n输出：\n\n```\n1101\n```\n\n## 【数据范围】\n\n0 ≤ x ≤ 10⁹\n\n## 【提示】\n\n"除二取余，逆序输出"；也可递归：先输出 x//2 的二进制再输出 x%2。x = 0 时要特判输出 0。', '一行，一个非负整数 x。', '一行，一个字符串，为 x 的二进制表示。',
 '13', '1101', '"除二取余，逆序输出"；也可递归：先输出 x//2 的二进制再输出 x%2。x = 0 时要特判输出 0。', 'import sys\n\nx = int(sys.stdin.read().strip())\nprint(bin(x)[2:])\n', 'python',
 '进制转换,递归,数学', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '13', '1101\n', 1, 1),
(@aid, '945642882', '111000010111010101110110000010\n', 0, 2),
(@aid, '759594434', '101101010001100111110111000010\n', 0, 3),
(@aid, '689081728', '101001000100101000110110000000\n', 0, 4),
(@aid, '792484184', '101111001111000101100101011000\n', 0, 5),
(@aid, '71221212', '100001111101011111111011100\n', 0, 6);

-- ---------- 92. 字符串全排列去重（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('字符串全排列去重', 3, 20, '## 【题目描述】\n\n给定一个字符串（长度不超过 7，可能含重复字符），按字典序输出其所有不同的排列，每个占一行。\n\n## 【输入格式】\n\n一行，一个字符串 s，只含小写字母。\n\n## 【输出格式】\n\n若干行，每行为一个不重复的排列，按字典序排列。\n\n## 【样例】\n\n输入：\n\n```\naab\n```\n\n输出：\n\n```\naab\naba\nbaa\n```\n\n## 【数据范围】\n\n1 ≤ |s| ≤ 7\n\n## 【提示】\n\n先排序，再用"同一层中相同字符只取第一个未使用的"这一规则去重，这是处理重复元素排列的标准写法。', '一行，一个字符串 s，只含小写字母。', '若干行，每行为一个不重复的排列，按字典序排列。',
 'aab', 'aab\naba\nbaa', '先排序，再用"同一层中相同字符只取第一个未使用的"这一规则去重，这是处理重复元素排列的标准写法。', 'import sys\n\ns = sys.stdin.read().strip()\nchars = sorted(s)\nn = len(chars)\nused = [False] * n\npath = []\nout = []\n\n\ndef dfs():\n    if len(path) == n:\n        out.append("".join(path))\n        return\n    for i in range(n):\n        if used[i]:\n            continue\n        if i > 0 and chars[i] == chars[i - 1] and not used[i - 1]:\n            continue\n        used[i] = True\n        path.append(chars[i])\n        dfs()\n        path.pop()\n        used[i] = False\n\n\ndfs()\nprint("\\n".join(out))\n', 'python',
 'DFS,回溯,排列,去重', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'aab', 'aab\naba\nbaa\n', 1, 1),
(@aid, 'bcb', 'bbc\nbcb\ncbb\n', 0, 2),
(@aid, 'cbba', 'abbc\nabcb\nacbb\nbabc\nbacb\nbbac\nbbca\nbcab\nbcba\ncabb\ncbab\ncbba\n', 0, 3),
(@aid, 'ba', 'ab\nba\n', 0, 4),
(@aid, 'aaabb', 'aaabb\naabab\naabba\nabaab\nababa\nabbaa\nbaaab\nbaaba\nbabaa\nbbaaa\n', 0, 5),
(@aid, 'bb', 'bb\n', 0, 6);

-- ---------- 93. 平分数组（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('平分数组', 3, 20, '## 【题目描述】\n\n给定 n 个正整数，判断能否把它们分成两组，使得两组元素之和相等。\n\n## 【输入格式】\n\n两行。第一行一个整数 n；第二行 n 个正整数。\n\n## 【输出格式】\n\n一行，能则输出 Yes，否则输出 No。\n\n## 【样例】\n\n输入：\n\n```\n4\n1 5 11 5\n```\n\n输出：\n\n```\nYes\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 20\n\n## 【提示】\n\n总和为奇数直接判否；否则转化为"能否选出若干数使其和为总和的一半"，即子集和问题，可用回溯（本题规模小）或 0/1 背包。', '两行。第一行一个整数 n；第二行 n 个正整数。', '一行，能则输出 Yes，否则输出 No。',
 '4\n1 5 11 5', 'Yes', '总和为奇数直接判否；否则转化为"能否选出若干数使其和为总和的一半"，即子集和问题，可用回溯（本题规模小）或 0/1 背包。', 'import sys\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nnums = list(map(int, data[1:1 + n]))\ntotal = sum(nums)\nif total % 2:\n    print("No")\nelse:\n    target = total // 2\n    ok = [False]\n\n    def dfs(i, s):\n        if ok[0] or s == target:\n            ok[0] = True\n            return\n        if i == n or s > target:\n            return\n        dfs(i + 1, s + nums[i])\n        dfs(i + 1, s)\n\n    dfs(0, 0)\n    print("Yes" if ok[0] else "No")\n', 'python',
 'DFS,回溯,子集和', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '4\n1 5 11 5', 'Yes\n', 1, 1),
(@aid, '13\n38 1 11 2 23 16 13 22 11 32 21 5 8', 'No\n', 0, 2),
(@aid, '12\n33 40 11 13 27 6 9 18 14 2 24 12', 'No\n', 0, 3),
(@aid, '4\n13 1 1 10', 'No\n', 0, 4),
(@aid, '19\n16 1 26 10 20 27 39 2 25 38 21 38 35 11 19 14 31 20 18', 'No\n', 0, 5),
(@aid, '19\n40 19 27 28 31 21 36 38 25 11 5 18 6 25 5 12 13 31 5', 'Yes\n', 0, 6);

-- ---------- 94. 无权图单源最短路（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('无权图单源最短路', 3, 20, '## 【题目描述】\n\n给定一个有 n 个结点、m 条边的无向无权图和起点 s，求 s 到每个点的最短距离；不可达输出 -1（起点自身为 0）。\n\n## 【输入格式】\n\n第一行三个整数 n、m、s；接下来 m 行，每行两个整数 u、v，表示一条无向边。\n\n## 【输出格式】\n\n一行，n 个整数，依次为 s 到 1..n 号点的最短距离，用空格分隔。\n\n## 【样例】\n\n输入：\n\n```\n5 4 1\n1 2\n2 3\n3 4\n4 5\n```\n\n输出：\n\n```\n0 1 2 3 4\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁵，0 ≤ m ≤ 2×10⁵\n\n## 【提示】\n\n无权图（边权均为 1）的单源最短路用 BFS：按层扩散，首次到达即最短，复杂度 O(n + m)。', '第一行三个整数 n、m、s；接下来 m 行，每行两个整数 u、v，表示一条无向边。', '一行，n 个整数，依次为 s 到 1..n 号点的最短距离，用空格分隔。',
 '5 4 1\n1 2\n2 3\n3 4\n4 5', '0 1 2 3 4', '无权图（边权均为 1）的单源最短路用 BFS：按层扩散，首次到达即最短，复杂度 O(n + m)。', 'import sys\nfrom collections import deque\n\ndata = sys.stdin.read().split()\nn = int(data[0])\nm = int(data[1])\ns = int(data[2])\nadj = [[] for _ in range(n + 1)]\nfor i in range(m):\n    u = int(data[3 + 2 * i])\n    v = int(data[4 + 2 * i])\n    adj[u].append(v)\n    adj[v].append(u)\ndist = [-1] * (n + 1)\ndist[s] = 0\nq = deque([s])\nwhile q:\n    x = q.popleft()\n    for y in adj[x]:\n        if dist[y] == -1:\n            dist[y] = dist[x] + 1\n            q.append(y)\nprint(" ".join(str(d) for d in dist[1:]))\n', 'python',
 'BFS,最短路,图', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '5 4 1\n1 2\n2 3\n3 4\n4 5', '0 1 2 3 4\n', 1, 1),
(@aid, '3 30 3\n2 2\n3 3\n1 3\n2 1\n1 3\n2 1\n2 2\n2 3\n3 1\n3 2\n1 3\n1 1\n2 3\n2 3\n2 3\n1 3\n1 2\n1 2\n2 2\n3 3\n3 2\n1 2\n2 2\n2 1\n1 2\n1 3\n2 2\n1 3\n1 1\n3 3', '1 1 0\n', 0, 2),
(@aid, '5 21 5\n4 4\n5 4\n1 2\n5 4\n1 4\n4 2\n3 2\n3 5\n3 5\n5 5\n4 4\n2 5\n1 4\n5 5\n5 3\n3 3\n1 5\n3 1\n4 2\n4 5\n5 4', '1 1 1 1 0\n', 0, 3),
(@aid, '16 25 14\n13 8\n4 9\n14 4\n2 9\n1 10\n8 14\n2 2\n7 3\n12 9\n6 3\n4 4\n10 1\n4 1\n9 7\n9 16\n4 1\n10 15\n14 10\n12 8\n10 8\n4 12\n6 8\n12 10\n10 12\n15 6', '2 3 3 1 -1 2 3 1 2 1 -1 2 2 0 2 3\n', 0, 4),
(@aid, '15 6 3\n1 10\n13 3\n3 8\n12 5\n10 9\n3 11', '-1 -1 0 -1 -1 -1 -1 1 -1 -1 1 -1 1 -1 -1\n', 0, 5),
(@aid, '6 21 5\n3 5\n4 2\n6 2\n4 5\n1 2\n5 4\n5 2\n6 4\n6 1\n2 1\n1 4\n4 3\n2 4\n4 1\n5 1\n4 4\n6 2\n5 1\n5 3\n1 5\n5 3', '1 1 1 1 0 2\n', 0, 6);

-- ---------- 95. 字符串反转（切片与双指针）（难度 1） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('字符串反转（切片与双指针）', 1, 10, '## 【题目描述】\n\n输入一个字符串（不含空格），将其反转后输出。\n\n## 【输入格式】\n\n一行，一个字符串 s。\n\n## 【输出格式】\n\n一行，反转后的字符串。\n\n## 【样例】\n\n输入：\n\n```\nabcdef\n```\n\n输出：\n\n```\nfedcba\n```\n\n## 【数据范围】\n\n1 ≤ |s| ≤ 100，仅含小写字母\n\n## 【提示】\n\nPython 中 s[::-1] 即逆序切片；也可双指针首尾交换，原地反转。', '一行，一个字符串 s。', '一行，反转后的字符串。',
 'abcdef', 'fedcba', 'Python 中 s[::-1] 即逆序切片；也可双指针首尾交换，原地反转。', 'import sys\n\ns = sys.stdin.readline().rstrip(\'\\n\')\nprint(s[::-1])\n', 'python',
 '字符串,基础', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'abcdef', 'fedcba\n', 1, 1),
(@aid, 'iuhksltkmrku', 'ukrmktlskhui\n', 0, 2),
(@aid, 'ylgxojrnqrtdzq', 'qzdtrqnrjoxgly\n', 0, 3),
(@aid, 'ekb', 'bke\n', 0, 4),
(@aid, 'urjiuscs', 'scsuijru\n', 0, 5),
(@aid, 'sandbeazivpdxpqy', 'yqpxdpvizaebdnas\n', 0, 6);

-- ---------- 96. 统计字符出现次数（难度 1） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('统计字符出现次数', 1, 10, '## 【题目描述】\n\n给定一个字符串和一个字符，统计该字符在字符串中出现的次数。\n\n## 【输入格式】\n\n两行。第一行一个字符串 s；第二行一个字符 c。\n\n## 【输出格式】\n\n一行，一个整数，表示出现次数。\n\n## 【样例】\n\n输入：\n\n```\nhello world\nl\n```\n\n输出：\n\n```\n3\n```\n\n## 【数据范围】\n\n1 ≤ |s| ≤ 1000，c 为单个可见字符\n\n## 【提示】\n\n遍历计数或用内置 count；注意第二行可能读到空串，需要 strip。', '两行。第一行一个字符串 s；第二行一个字符 c。', '一行，一个整数，表示出现次数。',
 'hello world\nl', '3', '遍历计数或用内置 count；注意第二行可能读到空串，需要 strip。', 'import sys\n\nlines = sys.stdin.read().split(\'\\n\')\ns = lines[0]\nc = lines[1].strip()\nprint(s.count(c))\n', 'python',
 '字符串,计数', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'hello world\nl', '3\n', 1, 1),
(@aid, 'array graph\nh', '1\n', 0, 2),
(@aid, 'struct algorithm graph code\nc', '2\n', 0, 3),
(@aid, 'hello node data\n ', '16\n', 0, 4),
(@aid, 'node world moon hello acm code struct python\n ', '45\n', 0, 5),
(@aid, 'code struct data code\nd', '3\n', 0, 6);

-- ---------- 97. 判断回文串（难度 1） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('判断回文串', 1, 10, '## 【题目描述】\n\n给定一个字符串（只含大小写字母），判断它是否是回文串（正读反读相同，区分大小写）。\n\n## 【输入格式】\n\n一行，一个字符串 s。\n\n## 【输出格式】\n\n一行，是回文输出 Yes，否则输出 No。\n\n## 【样例】\n\n输入：\n\n```\nlevel\n```\n\n输出：\n\n```\nYes\n```\n\n## 【数据范围】\n\n1 ≤ |s| ≤ 1000\n\n## 【提示】\n\n回文的本质是与自身的逆序相等；用双指针从两端向中间比较可以省去额外空间。', '一行，一个字符串 s。', '一行，是回文输出 Yes，否则输出 No。',
 'level', 'Yes', '回文的本质是与自身的逆序相等；用双指针从两端向中间比较可以省去额外空间。', 'import sys\n\ns = sys.stdin.readline().strip()\nprint(\'Yes\' if s == s[::-1] else \'No\')\n', 'python',
 '字符串,回文', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'level', 'Yes\n', 1, 1),
(@aid, 'bwqdpyypdqwb', 'Yes\n', 0, 2),
(@aid, 'fmmf', 'Yes\n', 0, 3),
(@aid, 'bnxhcsz', 'No\n', 0, 4),
(@aid, 't', 'Yes\n', 0, 5),
(@aid, 'sw', 'No\n', 0, 6);

-- ---------- 98. 字符串中的数字求和（难度 1） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('字符串中的数字求和', 1, 10, '## 【题目描述】\n\n给定一个字符串，求其中所有数字字符所代表数字之和。例如 "a1b2c3" 的结果为 1+2+3=6。\n\n## 【输入格式】\n\n一行，一个字符串 s（可含空格以换行结束）。\n\n## 【输出格式】\n\n一行，一个整数，表示数字之和。\n\n## 【样例】\n\n输入：\n\n```\na1b2c3\n```\n\n输出：\n\n```\n6\n```\n\n## 【数据范围】\n\n1 ≤ |s| ≤ 1000\n\n## 【提示】\n\n逐字符判断 isdigit() 后累加即可，注意字符到数字用 int(ch) 而不是 ord 换算。', '一行，一个字符串 s（可含空格以换行结束）。', '一行，一个整数，表示数字之和。',
 'a1b2c3', '6', '逐字符判断 isdigit() 后累加即可，注意字符到数字用 int(ch) 而不是 ord 换算。', 'import sys\n\ns = sys.stdin.readline().strip()\nprint(sum(int(ch) for ch in s if ch.isdigit()))\n', 'python',
 '字符串,模拟', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'a1b2c3', '6\n', 1, 1),
(@aid, 'C', '0\n', 0, 2),
(@aid, '8qznEf1RrH04Bb1U', '14\n', 0, 3),
(@aid, 'LxsuoawWNpWLhe', '0\n', 0, 4),
(@aid, 'HRabSS', '0\n', 0, 5),
(@aid, 'tEnPsI', '0\n', 0, 6);

-- ---------- 99. 最长单词（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('最长单词', 2, 10, '## 【题目描述】\n\n给定一行英文句子（单词间以单个空格分隔，不含标点），输出其中长度最大的单词；若有多个，输出最先出现的那个。\n\n## 【输入格式】\n\n一行，一个句子。\n\n## 【输出格式】\n\n一行，最长的单词。\n\n## 【样例】\n\n输入：\n\n```\ni love programming very much\n```\n\n输出：\n\n```\nprogramming\n```\n\n## 【数据范围】\n\n句子长度 ≤ 1000，至少含一个单词\n\n## 【提示】\n\n按空格 split 后线性扫描取最大长度；注意保持"最先出现"要在严格大于时才更新。', '一行，一个句子。', '一行，最长的单词。',
 'i love programming very much', 'programming', '按空格 split 后线性扫描取最大长度；注意保持"最先出现"要在严格大于时才更新。', 'import sys\n\nwords = sys.stdin.readline().strip().split()\nans = words[0]\nfor w in words:\n    if len(w) > len(ans):\n        ans = w\nprint(ans)\n', 'python',
 '字符串,模拟', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'i love programming very much', 'programming\n', 1, 1),
(@aid, 'hello code python world acm tree array code', 'python\n', 0, 2),
(@aid, 'cpp acm', 'cpp\n', 0, 3),
(@aid, 'python algorithm world', 'algorithm\n', 0, 4),
(@aid, 'cpp world graph', 'world\n', 0, 5),
(@aid, 'array hello world code acm moon tree', 'array\n', 0, 6);

-- ---------- 100. 删除指定字符（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('删除指定字符', 2, 10, '## 【题目描述】\n\n给定一个字符串 s 和一个字符 c，删除 s 中出现的所有字符 c 后输出。\n\n## 【输入格式】\n\n两行。第一行字符串 s；第二行字符 c。\n\n## 【输出格式】\n\n一行，删除后的字符串。\n\n## 【样例】\n\n输入：\n\n```\nbanana\na\n```\n\n输出：\n\n```\nbnn\n```\n\n## 【数据范围】\n\n1 ≤ |s| ≤ 1000\n\n## 【提示】\n\n用 replace 或遍历时跳过目标字符拼接新串；字符串不可变，注意 O(n) 拼接代价。', '两行。第一行字符串 s；第二行字符 c。', '一行，删除后的字符串。',
 'banana\na', 'bnn', '用 replace 或遍历时跳过目标字符拼接新串；字符串不可变，注意 O(n) 拼接代价。', 'import sys\n\nlines = sys.stdin.read().split(\'\\n\')\ns = lines[0]\nc = lines[1].strip()\nprint(s.replace(c, \'\'))\n', 'python',
 '字符串,模拟', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'banana\na', 'bnn\n', 1, 1),
(@aid, 'abaaabbbbc\na', 'bbbbbc\n', 0, 2),
(@aid, 'aaccbbbbcbccbccccccb\na', 'ccbbbbcbccbccccccb\n', 0, 3),
(@aid, 'ab\nb', 'a\n', 0, 4),
(@aid, 'bccbaaaacabbacc\na', 'bccbcbbcc\n', 0, 5),
(@aid, 'babccaaacbacbbabaaa\na', 'bbcccbcbbb\n', 0, 6);

-- ---------- 101. 统计单词数（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('统计单词数', 2, 10, '## 【题目描述】\n\n给定一行文本（单词间可能有多余空格），统计其中单词的个数。\n\n## 【输入格式】\n\n一行，一个字符串。\n\n## 【输出格式】\n\n一行，一个整数，表示单词个数。\n\n## 【样例】\n\n输入：\n\n```\n  hello   world  \n```\n\n输出：\n\n```\n2\n```\n\n## 【数据范围】\n\n字符串长度 ≤ 1000\n\n## 【提示】\n\n不带参数的 split() 会自动忽略连续空格与首尾空白，比按单空格切分更稳健。', '一行，一个字符串。', '一行，一个整数，表示单词个数。',
 '  hello   world  ', '2', '不带参数的 split() 会自动忽略连续空格与首尾空白，比按单空格切分更稳健。', 'import sys\n\ns = sys.stdin.readline().strip()\nprint(len(s.split()))\n', 'python',
 '字符串,模拟', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '  hello   world  ', '2\n', 1, 1),
(@aid, '  data   moon   world   sun   cpp  ', '5\n', 0, 2),
(@aid, '  acm   array   tree  ', '3\n', 0, 3),
(@aid, '  array   luogu   struct   struct   data   code   hello   cpp  ', '8\n', 0, 4),
(@aid, '  struct   cpp   sun   node   test   data   python  ', '7\n', 0, 5),
(@aid, '  struct  ', '1\n', 0, 6);

-- ---------- 102. 字符串替换（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('字符串替换', 2, 10, '## 【题目描述】\n\n给定字符串 s 和两个字符 a、b，把 s 中所有字符 a 替换成字符 b 后输出。\n\n## 【输入格式】\n\n三行。第一行字符串 s；第二行字符 a；第三行字符 b。\n\n## 【输出格式】\n\n一行，替换后的字符串。\n\n## 【样例】\n\n输入：\n\n```\nmississippi\ns\np\n```\n\n输出：\n\n```\nmippippippi\n```\n\n## 【数据范围】\n\n1 ≤ |s| ≤ 1000\n\n## 【提示】\n\n逐字符判断替换；若要替换子串则用 replace，注意替换后的内容不会再被继续替换。', '三行。第一行字符串 s；第二行字符 a；第三行字符 b。', '一行，替换后的字符串。',
 'mississippi\ns\np', 'mippippippi', '逐字符判断替换；若要替换子串则用 replace，注意替换后的内容不会再被继续替换。', 'import sys\n\nlines = sys.stdin.read().split(\'\\n\')\ns = lines[0]\na = lines[1].strip()\nb = lines[2].strip()\nprint(\'\'.join(b if ch == a else ch for ch in s))\n', 'python',
 '字符串,模拟', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'mississippi\ns\np', 'mippippippi\n', 1, 1),
(@aid, 'cbcbbbac\nc\nx', 'xbxbbbax\n', 0, 2),
(@aid, 'acbbcabcaabbccbcc\nb\ny', 'acyycaycaayyccycc\n', 0, 3),
(@aid, 'abaaccacc\nc\ny', 'abaayyayy\n', 0, 4),
(@aid, 'babbbbbcbccaacbbac\nb\ny', 'yayyyyycyccaacyyac\n', 0, 5),
(@aid, 'b\nb\nx', 'x\n', 0, 6);

-- ---------- 103. 单词首字母大写（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('单词首字母大写', 2, 10, '## 【题目描述】\n\n给定一行英文句子（单词间以单个空格分隔），把每个单词的首字母改成大写，其余字母保持不变。\n\n## 【输入格式】\n\n一行，一个句子。\n\n## 【输出格式】\n\n一行，处理后的句子。\n\n## 【样例】\n\n输入：\n\n```\nhello world\n```\n\n输出：\n\n```\nHello World\n```\n\n## 【数据范围】\n\n句子长度 ≤ 1000，单词均为小写字母\n\n## 【提示】\n\n先切分再对每个单词做首字母 upper() 处理，最后拼回；也可用 capitalize() 但会改写其余字母。', '一行，一个句子。', '一行，处理后的句子。',
 'hello world', 'Hello World', '先切分再对每个单词做首字母 upper() 处理，最后拼回；也可用 capitalize() 但会改写其余字母。', 'import sys\n\ns = sys.stdin.readline().strip()\nprint(\' \'.join(w[0].upper() + w[1:] for w in s.split(\' \')))\n', 'python',
 '字符串,模拟', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'hello world', 'Hello World\n', 1, 1),
(@aid, 'graph data luogu acm', 'Graph Data Luogu Acm\n', 0, 2),
(@aid, 'struct tree graph cpp', 'Struct Tree Graph Cpp\n', 0, 3),
(@aid, 'struct test cpp test moon code acm luogu', 'Struct Test Cpp Test Moon Code Acm Luogu\n', 0, 4),
(@aid, 'acm sun acm tree moon luogu luogu', 'Acm Sun Acm Tree Moon Luogu Luogu\n', 0, 5),
(@aid, 'data code algorithm python world code', 'Data Code Algorithm Python World Code\n', 0, 6);

-- ---------- 104. 字符串的最小周期（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('字符串的最小周期', 2, 10, '## 【题目描述】\n\n给定一个字符串 s，求它的最小周期 k，即最小的正整数 k 使得 s 恰好由某个长度为 k 的前缀重复若干次构成（k 一定整除 |s|）。\n\n## 【输入格式】\n\n一行，一个字符串 s。\n\n## 【输出格式】\n\n一行，一个整数，表示最小周期。\n\n## 【样例】\n\n输入：\n\n```\nababab\n```\n\n输出：\n\n```\n2\n```\n\n## 【数据范围】\n\n1 ≤ |s| ≤ 1000\n\n## 【提示】\n\n枚举 1..n 中能整除 n 的长度 k，检查 s[:k] 重复 n/k 次是否等于原串，第一个满足的即最小周期。', '一行，一个字符串 s。', '一行，一个整数，表示最小周期。',
 'ababab', '2', '枚举 1..n 中能整除 n 的长度 k，检查 s[:k] 重复 n/k 次是否等于原串，第一个满足的即最小周期。', 'import sys\n\ns = sys.stdin.readline().strip()\nn = len(s)\nfor k in range(1, n + 1):\n    if n % k == 0 and s[:k] * (n // k) == s:\n        print(k)\n        break\n', 'python',
 '字符串,枚举,周期', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'ababab', '2\n', 1, 1),
(@aid, 'qqq', '1\n', 0, 2),
(@aid, 'ababababab', '2\n', 0, 3),
(@aid, 'abcabcabc', '3\n', 0, 4),
(@aid, 'abcabc', '3\n', 0, 5),
(@aid, 'ab', '2\n', 0, 6);

-- ---------- 105. 最长公共前缀（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('最长公共前缀', 2, 10, '## 【题目描述】\n\n给定 n 个字符串，求它们的最长公共前缀；若不存在公共前缀，输出空行。\n\n## 【输入格式】\n\n第一行一个整数 n；接下来 n 行，每行一个字符串。\n\n## 【输出格式】\n\n一行，最长公共前缀（可能为空）。\n\n## 【样例】\n\n输入：\n\n```\n3\nflower\nflow\nflight\n```\n\n输出：\n\n```\nfl\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 200，每个串长度 ≤ 200\n\n## 【提示】\n\n以第一个串为基准逐字符与后续串比对，一旦失配即截断；也可纵向扫描列。', '第一行一个整数 n；接下来 n 行，每行一个字符串。', '一行，最长公共前缀（可能为空）。',
 '3\nflower\nflow\nflight', 'fl', '以第一个串为基准逐字符与后续串比对，一旦失配即截断；也可纵向扫描列。', 'import sys\n\ndata = sys.stdin.read().split(\'\\n\')\nn = int(data[0])\nstrs = data[1:1 + n]\nans = strs[0]\nfor s in strs[1:]:\n    i = 0\n    while i < len(ans) and i < len(s) and ans[i] == s[i]:\n        i += 1\n    ans = ans[:i]\nprint(ans)\n', 'python',
 '字符串,模拟', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3\nflower\nflow\nflight', 'fl\n', 1, 1),
(@aid, '5\nccbbcddc\nddddc\ndd\ncca\nb', '\n', 0, 2),
(@aid, '6\ncda\ncbcdcaca\nba\nbacb\ncbdb\nbcabcad', '\n', 0, 3),
(@aid, '6\nb\ncbddc\nbbbbb\ndaaa\nbabc\naddd', '\n', 0, 4),
(@aid, '6\nbdbbbaa\ncaab\ncbddaaba\ncabcb\ndb\na', '\n', 0, 5),
(@aid, '4\ncbb\ncacb\nbcabdcd\ncaa', '\n', 0, 6);

-- ---------- 106. 子串查找（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('子串查找', 3, 20, '## 【题目描述】\n\n给定文本串 t 和模式串 p，求 p 在 t 中第一次出现的位置（下标从 0 开始）；若不存在，输出 -1。\n\n## 【输入格式】\n\n两行。第一行为文本串 t；第二行为模式串 p。\n\n## 【输出格式】\n\n一行，一个整数。\n\n## 【样例】\n\n输入：\n\n```\nhello world\nworld\n```\n\n输出：\n\n```\n6\n```\n\n## 【数据范围】\n\n1 ≤ |p| ≤ |t| ≤ 10⁴\n\n## 【提示】\n\n可直接用内置 find（底层为高效的双指针/两段匹配）；手写实现可练习朴素匹配或 KMP。', '两行。第一行为文本串 t；第二行为模式串 p。', '一行，一个整数。',
 'hello world\nworld', '6', '可直接用内置 find（底层为高效的双指针/两段匹配）；手写实现可练习朴素匹配或 KMP。', 'import sys\n\ndata = sys.stdin.read().split(\'\\n\')\nt = data[0]\np = data[1]\nprint(t.find(p))\n', 'python',
 '字符串,匹配,KMP', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'hello world\nworld', '6\n', 1, 1),
(@aid, 'b   cca\nc', '4\n', 0, 2),
(@aid, 'cbaddada bdcbcca dc\ndc', '10\n', 0, 3),
(@aid, 'a a bbabd c dabd daca d\nb', '4\n', 0, 4),
(@aid, 'bcd cdb dbaababcd\nb d', '6\n', 0, 5),
(@aid, 'acbdccd b\nc', '1\n', 0, 6);

-- ---------- 107. 字符串压缩（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('字符串压缩', 2, 10, '## 【题目描述】\n\n给定一个字符串，将其中连续相同的字符压缩为「字符 + 连续个数」的形式；若某字符只连续出现 1 次，则只输出该字符。\n\n## 【输入格式】\n\n一行，一个字符串 s。\n\n## 【输出格式】\n\n一行，压缩后的字符串。\n\n## 【样例】\n\n输入：\n\n```\naaabbcdddd\n```\n\n输出：\n\n```\na3b2cd4\n```\n\n## 【数据范围】\n\n1 ≤ |s| ≤ 1000，仅含小写字母\n\n## 【提示】\n\n双指针扫描每一段连续区间，记录段长；注意段长为 1 时不输出数字。', '一行，一个字符串 s。', '一行，压缩后的字符串。',
 'aaabbcdddd', 'a3b2cd4', '双指针扫描每一段连续区间，记录段长；注意段长为 1 时不输出数字。', 'import sys\n\ns = sys.stdin.readline().strip()\nres = []\ni = 0\nwhile i < len(s):\n    j = i\n    while j < len(s) and s[j] == s[i]:\n        j += 1\n    cnt = j - i\n    res.append(s[i] if cnt == 1 else s[i] + str(cnt))\n    i = j\nprint(\'\'.join(res))\n', 'python',
 '字符串,双指针,游程编码', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'aaabbcdddd', 'a3b2cd4\n', 1, 1),
(@aid, 'cadca', 'cadca\n', 0, 2),
(@aid, 'cdbacacbaadacaacadb', 'cdbacacba2daca2cadb\n', 0, 3),
(@aid, 'aaddbdbdd', 'a2d2bdbd2\n', 0, 4),
(@aid, 'bdbcadcadbadcabb', 'bdbcadcadbadcab2\n', 0, 5),
(@aid, 'abbbd', 'ab3d\n', 0, 6);

-- ---------- 108. 罗马数字转整数（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('罗马数字转整数', 2, 10, '## 【题目描述】\n\n给定一个罗马数字字符串（由 I、V、X、L、C、D、M 组成，且符合书写规则），将其转换为整数。特殊规则：小的数字在大的数字左边时做减法，如 IV = 4、IX = 9。\n\n## 【输入格式】\n\n一行，一个罗马数字字符串。\n\n## 【输出格式】\n\n一行，一个整数。\n\n## 【样例】\n\n输入：\n\n```\nMCMXCIV\n```\n\n输出：\n\n```\n1994\n```\n\n## 【数据范围】\n\n1 ≤ |s| ≤ 15\n\n## 【提示】\n\n从左到右扫描：当前符号值小于右边符号值时减去它，否则加上它。这是处理"左减右加"的统一写法。', '一行，一个罗马数字字符串。', '一行，一个整数。',
 'MCMXCIV', '1994', '从左到右扫描：当前符号值小于右边符号值时减去它，否则加上它。这是处理"左减右加"的统一写法。', 'import sys\n\ns = sys.stdin.readline().strip()\nval = {\'I\': 1, \'V\': 5, \'X\': 10, \'L\': 50, \'C\': 100, \'D\': 500, \'M\': 1000}\nans = 0\nfor i in range(len(s)):\n    if i + 1 < len(s) and val[s[i]] < val[s[i + 1]]:\n        ans -= val[s[i]]\n    else:\n        ans += val[s[i]]\nprint(ans)\n', 'python',
 '字符串,模拟,哈希映射', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'MCMXCIV', '1994\n', 1, 1),
(@aid, 'CXXCXLC', '240\n', 0, 2),
(@aid, 'LIIDM', '550\n', 0, 3),
(@aid, 'LIMXLX', '1099\n', 0, 4),
(@aid, 'DVIMLDVC', '2049\n', 0, 5),
(@aid, 'XCXILC', '149\n', 0, 6);

-- ---------- 109. 整数转罗马数字（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('整数转罗马数字', 3, 20, '## 【题目描述】\n\n给定一个 1 到 3999 之间的整数，输出它的罗马数字表示。\n\n## 【输入格式】\n\n一行，一个整数 n。\n\n## 【输出格式】\n\n一行，对应的罗马数字。\n\n## 【样例】\n\n输入：\n\n```\n1994\n```\n\n输出：\n\n```\nMCMXCIV\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 3999\n\n## 【提示】\n\n贪心：把 6 种减法组合（4 与 9 的各档）也放进制表，从大到小不断扣除并拼接符号。', '一行，一个整数 n。', '一行，对应的罗马数字。',
 '1994', 'MCMXCIV', '贪心：把 6 种减法组合（4 与 9 的各档）也放进制表，从大到小不断扣除并拼接符号。', 'import sys\n\nn = int(sys.stdin.read().strip())\npairs = [(1000, \'M\'), (900, \'CM\'), (500, \'D\'), (400, \'CD\'), (100, \'C\'), (90, \'XC\'),\n         (50, \'L\'), (40, \'XL\'), (10, \'X\'), (9, \'IX\'), (5, \'V\'), (4, \'IV\'), (1, \'I\')]\nres = []\nfor v, sym in pairs:\n    while n >= v:\n        res.append(sym)\n        n -= v\nprint(\'\'.join(res))\n', 'python',
 '字符串,贪心,模拟', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '1994', 'MCMXCIV\n', 1, 1),
(@aid, '2522', 'MMDXXII\n', 0, 2),
(@aid, '3585', 'MMMDLXXXV\n', 0, 3),
(@aid, '1621', 'MDCXXI\n', 0, 4),
(@aid, '2994', 'MMCMXCIV\n', 0, 5),
(@aid, '986', 'CMLXXXVI\n', 0, 6);

-- ---------- 110. 有效的括号（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('有效的括号', 2, 10, '## 【题目描述】\n\n给定一个只含 ()[]{} 六种字符的字符串，判断其中的括号是否合法匹配（每个左括号都有对应类型、正确顺序的右括号）。\n\n## 【输入格式】\n\n一行，一个字符串 s。\n\n## 【输出格式】\n\n一行，合法输出 Yes，否则输出 No。\n\n## 【样例】\n\n输入：\n\n```\n([]{})\n```\n\n输出：\n\n```\nYes\n```\n\n## 【数据范围】\n\n1 ≤ |s| ≤ 10⁴\n\n## 【提示】\n\n栈的经典应用：遇左括号入栈，遇右括号检查栈顶是否为对应左括号；最后栈必须为空。', '一行，一个字符串 s。', '一行，合法输出 Yes，否则输出 No。',
 '([]{})', 'Yes', '栈的经典应用：遇左括号入栈，遇右括号检查栈顶是否为对应左括号；最后栈必须为空。', 'import sys\n\ns = sys.stdin.readline().strip()\nmp = {\')\': \'(\', \']\': \'[\', \'}\': \'{\'}\nst = []\nok = True\nfor ch in s:\n    if ch in mp:\n        if not st or st[-1] != mp[ch]:\n            ok = False\n            break\n        st.pop()\n    else:\n        st.append(ch)\nif st:\n    ok = False\nprint(\'Yes\' if ok else \'No\')\n', 'python',
 '字符串,栈', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '([]{})', 'Yes\n', 1, 1),
(@aid, '][[](){})(', 'No\n', 0, 2),
(@aid, ')(()(){}', 'No\n', 0, 3),
(@aid, '[]{}()', 'Yes\n', 0, 4),
(@aid, '[]()()[]', 'Yes\n', 0, 5),
(@aid, ')(', 'No\n', 0, 6);

-- ---------- 111. 最长无重复字符子串（滑动窗口）（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('最长无重复字符子串（滑动窗口）', 3, 20, '## 【题目描述】\n\n给定一个字符串，求其中不含重复字符的最长子串的长度。\n\n## 【输入格式】\n\n一行，一个字符串 s。\n\n## 【输出格式】\n\n一行，一个整数，表示最长无重复字符子串的长度。\n\n## 【样例】\n\n输入：\n\n```\nabcabcbb\n```\n\n输出：\n\n```\n3\n```\n\n## 【数据范围】\n\n1 ≤ |s| ≤ 10⁴，仅含小写字母\n\n## 【提示】\n\n滑动窗口 + 哈希表记录每个字符最后出现位置：右端点右移时，若字符已在窗口内就把左端点跳到其后一位。', '一行，一个字符串 s。', '一行，一个整数，表示最长无重复字符子串的长度。',
 'abcabcbb', '3', '滑动窗口 + 哈希表记录每个字符最后出现位置：右端点右移时，若字符已在窗口内就把左端点跳到其后一位。', 'import sys\n\ns = sys.stdin.readline().strip()\nlast = {}\nleft = 0\nans = 0\nfor i, ch in enumerate(s):\n    if ch in last and last[ch] >= left:\n        left = last[ch] + 1\n    last[ch] = i\n    ans = max(ans, i - left + 1)\nprint(ans)\n', 'python',
 '字符串,滑动窗口,哈希表', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'abcabcbb', '3\n', 1, 1),
(@aid, 'dddcdabcbdbcd', '4\n', 0, 2),
(@aid, 'cbacadcbbdcd', '4\n', 0, 3),
(@aid, 'ccdaddbdcdbcdabaddcdcddbcadbd', '4\n', 0, 4),
(@aid, 'cccdadbdcbbaabaddbdd', '3\n', 0, 5),
(@aid, 'cbbcccabababa', '3\n', 0, 6);

-- ---------- 112. 单词倒排（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('单词倒排', 2, 10, '## 【题目描述】\n\n给定一行英文句子（单词间以单个空格分隔），把单词的顺序颠倒后输出（单词本身不反转）。\n\n## 【输入格式】\n\n一行，一个句子。\n\n## 【输出格式】\n\n一行，倒排后的句子。\n\n## 【样例】\n\n输入：\n\n```\nthe sky is blue\n```\n\n输出：\n\n```\nblue is sky the\n```\n\n## 【数据范围】\n\n句子长度 ≤ 1000\n\n## 【提示】\n\n切分后逆序拼接；若要求整体反转再逐词反转则是另一种原地做法。', '一行，一个句子。', '一行，倒排后的句子。',
 'the sky is blue', 'blue is sky the', '切分后逆序拼接；若要求整体反转再逐词反转则是另一种原地做法。', 'import sys\n\nwords = sys.stdin.readline().strip().split(\' \')\nprint(\' \'.join(reversed(words)))\n', 'python',
 '字符串,模拟', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'the sky is blue', 'blue is sky the\n', 1, 1),
(@aid, 'luogu sun array hello struct', 'struct hello array sun luogu\n', 0, 2),
(@aid, 'cpp moon', 'moon cpp\n', 0, 3),
(@aid, 'struct luogu code array struct python node node test', 'test node node python struct array code luogu struct\n', 0, 4),
(@aid, 'code tree acm struct array', 'array struct acm tree code\n', 0, 5),
(@aid, 'tree node code sun', 'sun code node tree\n', 0, 6);

-- ---------- 113. 判断字母异位词（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('判断字母异位词', 2, 10, '## 【题目描述】\n\n给定两个只含小写字母的字符串，判断它们是否互为字母异位词（字符及出现次数完全相同，顺序可不同）。\n\n## 【输入格式】\n\n两行，每行一个字符串。\n\n## 【输出格式】\n\n一行，是输出 Yes，否则输出 No。\n\n## 【样例】\n\n输入：\n\n```\nlisten\nsilent\n```\n\n输出：\n\n```\nYes\n```\n\n## 【数据范围】\n\n1 ≤ |s| ≤ 1000\n\n## 【提示】\n\n排序后比较是最简洁的 O(n log n) 写法；也可以用长度 26 的计数数组做到 O(n)。', '两行，每行一个字符串。', '一行，是输出 Yes，否则输出 No。',
 'listen\nsilent', 'Yes', '排序后比较是最简洁的 O(n log n) 写法；也可以用长度 26 的计数数组做到 O(n)。', 'import sys\n\ndata = sys.stdin.read().split(\'\\n\')\na = data[0].strip()\nb = data[1].strip()\nprint(\'Yes\' if sorted(a) == sorted(b) else \'No\')\n', 'python',
 '字符串,哈希,排序', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'listen\nsilent', 'Yes\n', 1, 1),
(@aid, 'cc\ndd', 'No\n', 0, 2),
(@aid, 'faa\nafa', 'Yes\n', 0, 3),
(@aid, 'bcbbeeeace\ncaffdeccde', 'No\n', 0, 4),
(@aid, 'aeec\necea', 'Yes\n', 0, 5),
(@aid, 'edca\naced', 'Yes\n', 0, 6);

-- ---------- 114. 字符串转整数（atoi）（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('字符串转整数（atoi）', 3, 20, '## 【题目描述】\n\n模拟 atoi：读入一个字符串，跳过前导空格，读取可选的正负号，之后尽可能多地读取连续数字字符并转成整数；若结果超出 [-2³¹, 2³¹-1] 则截断到边界；若第一个非空格字符不是数字或正负号，输出 0。\n\n## 【输入格式】\n\n一行，一个字符串 s。\n\n## 【输出格式】\n\n一行，一个整数。\n\n## 【样例】\n\n输入：\n\n```\n   -4193 with words\n```\n\n输出：\n\n```\n-4193\n```\n\n## 【数据范围】\n\n1 ≤ |s| ≤ 200\n\n## 【提示】\n\n按"去空格 → 读符号 → 读数字 → 溢出截断"四步实现；溢出要在累加过程中或最后统一裁剪。', '一行，一个字符串 s。', '一行，一个整数。',
 '   -4193 with words', '-4193', '按"去空格 → 读符号 → 读数字 → 溢出截断"四步实现；溢出要在累加过程中或最后统一裁剪。', 'import sys\n\ns = sys.stdin.readline().strip()\nINT_MAX = 2 ** 31 - 1\nINT_MIN = -2 ** 31\ni, n = 0, len(s)\nwhile i < n and s[i] == \' \':\n    i += 1\nsign = 1\nif i < n and s[i] in \'+-\':\n    if s[i] == \'-\':\n        sign = -1\n    i += 1\nans = 0\nwhile i < n and s[i].isdigit():\n    ans = ans * 10 + int(s[i])\n    i += 1\nans *= sign\nif ans > INT_MAX:\n    ans = INT_MAX\nif ans < INT_MIN:\n    ans = INT_MIN\nprint(ans)\n', 'python',
 '字符串,模拟,边界处理', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '   -4193 with words', '-4193\n', 1, 1),
(@aid, '  798841195053', '2147483647\n', 0, 2),
(@aid, '   317274058409', '2147483647\n', 0, 3),
(@aid, ' 288756062366 abc', '2147483647\n', 0, 4),
(@aid, '959', '959\n', 0, 5),
(@aid, '   84557667907 abc', '2147483647\n', 0, 6);

-- ---------- 115. 最大公约数与最小公倍数（辗转相除）（难度 1） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('最大公约数与最小公倍数（辗转相除）', 1, 10, '## 【题目描述】\n\n给定两个正整数 a、b，求它们的最大公约数和最小公倍数。\n\n## 【输入格式】\n\n一行，两个正整数 a、b。\n\n## 【输出格式】\n\n一行，两个整数，依次为最大公约数和最小公倍数，用空格分隔。\n\n## 【样例】\n\n输入：\n\n```\n12 18\n```\n\n输出：\n\n```\n6 36\n```\n\n## 【数据范围】\n\n1 ≤ a, b ≤ 10⁹\n\n## 【提示】\n\n辗转相除法（欧几里得算法）求 gcd；利用 a × b = gcd × lcm，写成 a // g * b 可避免中间结果溢出。', '一行，两个正整数 a、b。', '一行，两个整数，依次为最大公约数和最小公倍数，用空格分隔。',
 '12 18', '6 36', '辗转相除法（欧几里得算法）求 gcd；利用 a × b = gcd × lcm，写成 a // g * b 可避免中间结果溢出。', 'import sys\nimport math\n\na, b = map(int, sys.stdin.read().split())\ng = math.gcd(a, b)\nprint(g, a // g * b)\n', 'python',
 '数论,gcd,辗转相除', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '12 18', '6 36\n', 1, 1),
(@aid, '38735 532303', '1 20618756705\n', 0, 2),
(@aid, '279342 249191', '1 69609512322\n', 0, 3),
(@aid, '503764 472542', '2 119024824044\n', 0, 4),
(@aid, '847809 590285', '1 500448935565\n', 0, 5),
(@aid, '715040 225679', '1 161369512160\n', 0, 6);

-- ---------- 116. 素数判定（难度 1） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('素数判定', 1, 10, '## 【题目描述】\n\n给定一个正整数 n，判断它是否为素数（质数）。\n\n## 【输入格式】\n\n一行，一个整数 n。\n\n## 【输出格式】\n\n一行，是素数输出 Yes，否则输出 No。\n\n## 【样例】\n\n输入：\n\n```\n17\n```\n\n输出：\n\n```\nYes\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁹\n\n## 【提示】\n\n只需试除到 √n：若 n 存在大于 √n 的因子，必然对应一个小于 √n 的因子。', '一行，一个整数 n。', '一行，是素数输出 Yes，否则输出 No。',
 '17', 'Yes', '只需试除到 √n：若 n 存在大于 √n 的因子，必然对应一个小于 √n 的因子。', 'import sys\n\nn = int(sys.stdin.read().strip())\nif n < 2:\n    print(\'No\')\nelse:\n    ok = True\n    i = 2\n    while i * i <= n:\n        if n % i == 0:\n            ok = False\n            break\n        i += 1\n    print(\'Yes\' if ok else \'No\')\n', 'python',
 '数论,素数,试除法', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '17', 'Yes\n', 1, 1),
(@aid, '614369', 'No\n', 0, 2),
(@aid, '139500', 'No\n', 0, 3),
(@aid, '821719', 'No\n', 0, 4),
(@aid, '195489', 'No\n', 0, 5),
(@aid, '559255', 'No\n', 0, 6);

-- ---------- 117. 分解质因数（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('分解质因数', 2, 10, '## 【题目描述】\n\n给定一个大于 1 的整数 n，将其分解成若干质因数的乘积，按质因数从小到大的顺序输出，形如「n = p1 * p2 * ...」（数与运算符之间各有一个空格）。\n\n## 【输入格式】\n\n一行，一个整数 n。\n\n## 【输出格式】\n\n一行，分解式。\n\n## 【样例】\n\n输入：\n\n```\n60\n```\n\n输出：\n\n```\n60 = 2 * 2 * 3 * 5\n```\n\n## 【数据范围】\n\n2 ≤ n ≤ 10⁹\n\n## 【提示】\n\n从 2 开始试除，把能整除的因子全部除尽再前进；最后剩下大于 1 的数本身也是一个质因数。', '一行，一个整数 n。', '一行，分解式。',
 '60', '60 = 2 * 2 * 3 * 5', '从 2 开始试除，把能整除的因子全部除尽再前进；最后剩下大于 1 的数本身也是一个质因数。', 'import sys\n\nn = int(sys.stdin.read().strip())\norig = n\nres = []\nd = 2\nwhile d * d <= n:\n    while n % d == 0:\n        res.append(d)\n        n //= d\n    d += 1\nif n > 1:\n    res.append(n)\nprint(\'%d = %s\' % (orig, \' * \'.join(map(str, res))))\n', 'python',
 '数论,质因数分解', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '60', '60 = 2 * 2 * 3 * 5\n', 1, 1),
(@aid, '876313', '876313 = 233 * 3761\n', 0, 2),
(@aid, '26440', '26440 = 2 * 2 * 2 * 5 * 661\n', 0, 3),
(@aid, '275149', '275149 = 7 * 23 * 1709\n', 0, 4),
(@aid, '601595', '601595 = 5 * 120319\n', 0, 5),
(@aid, '433928', '433928 = 2 * 2 * 2 * 11 * 4931\n', 0, 6);

-- ---------- 118. 筛法求素数个数（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('筛法求素数个数', 2, 10, '## 【题目描述】\n\n给定整数 n，求不超过 n 的素数个数。\n\n## 【输入格式】\n\n一行，一个整数 n。\n\n## 【输出格式】\n\n一行，一个整数，表示素数个数。\n\n## 【样例】\n\n输入：\n\n```\n10\n```\n\n输出：\n\n```\n4\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁶\n\n## 【提示】\n\n埃氏筛：从 2 开始，把每个素数的倍数全部标记为合数，注意从 i*i 开始标记以避免重复。', '一行，一个整数 n。', '一行，一个整数，表示素数个数。',
 '10', '4', '埃氏筛：从 2 开始，把每个素数的倍数全部标记为合数，注意从 i*i 开始标记以避免重复。', 'import sys\n\nn = int(sys.stdin.read().strip())\nis_prime = [True] * (n + 1)\nif n >= 0:\n    is_prime[0] = False\nif n >= 1:\n    is_prime[1] = False\ni = 2\nwhile i * i <= n:\n    if is_prime[i]:\n        for j in range(i * i, n + 1, i):\n            is_prime[j] = False\n    i += 1\nprint(sum(1 for x in range(2, n + 1) if is_prime[x]))\n', 'python',
 '数论,素数,埃氏筛', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '10', '4\n', 1, 1),
(@aid, '55367', '5623\n', 0, 2),
(@aid, '30906', '3332\n', 0, 3),
(@aid, '47093', '4858\n', 0, 4),
(@aid, '89290', '8647\n', 0, 5),
(@aid, '36310', '3853\n', 0, 6);

-- ---------- 119. 二进制中 1 的个数（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('二进制中 1 的个数', 2, 10, '## 【题目描述】\n\n给定一个非负整数 n，求它的二进制表示中 1 的个数。\n\n## 【输入格式】\n\n一行，一个整数 n。\n\n## 【输出格式】\n\n一行，一个整数。\n\n## 【样例】\n\n输入：\n\n```\n13\n```\n\n输出：\n\n```\n3\n```\n\n## 【数据范围】\n\n0 ≤ n ≤ 10¹⁸\n\n## 【提示】\n\nBrian Kernighan 技巧：n & (n-1) 会消去最低位的 1，循环次数等于 1 的个数，比逐位检查更快。', '一行，一个整数 n。', '一行，一个整数。',
 '13', '3', 'Brian Kernighan 技巧：n & (n-1) 会消去最低位的 1，循环次数等于 1 的个数，比逐位检查更快。', 'import sys\n\nn = int(sys.stdin.read().strip())\nans = 0\nwhile n:\n    n &= n - 1\n    ans += 1\nprint(ans)\n', 'python',
 '数论,位运算', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '13', '3\n', 1, 1),
(@aid, '361858202', '12\n', 0, 2),
(@aid, '163887169', '11\n', 0, 3),
(@aid, '576368114', '16\n', 0, 4),
(@aid, '906378830', '15\n', 0, 5),
(@aid, '598238513', '13\n', 0, 6);

-- ---------- 120. 快速幂（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('快速幂', 3, 20, '## 【题目描述】\n\n给定三个整数 a、b、m，求 aᵇ mod m 的值。\n\n## 【输入格式】\n\n一行，三个整数 a、b、m。\n\n## 【输出格式】\n\n一行，一个整数，表示 aᵇ mod m。\n\n## 【样例】\n\n输入：\n\n```\n2 10 1000\n```\n\n输出：\n\n```\n24\n```\n\n## 【数据范围】\n\n0 ≤ a, b ≤ 10⁹，1 ≤ m ≤ 10⁹\n\n## 【提示】\n\n二进制拆分指数：底数不断平方，指数的每一位为 1 时就把当前底数乘入答案，复杂度 O(log b)。', '一行，三个整数 a、b、m。', '一行，一个整数，表示 aᵇ mod m。',
 '2 10 1000', '24', '二进制拆分指数：底数不断平方，指数的每一位为 1 时就把当前底数乘入答案，复杂度 O(log b)。', 'import sys\n\na, b, m = map(int, sys.stdin.read().split())\nres = 1 % m\na %= m\nwhile b:\n    if b & 1:\n        res = res * a % m\n    a = a * a % m\n    b >>= 1\nprint(res)\n', 'python',
 '数论,快速幂,分治', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '2 10 1000', '24\n', 1, 1),
(@aid, '890816 493496075 844149643', '134790448\n', 0, 2),
(@aid, '674100 994011004 453775838', '421811446\n', 0, 3),
(@aid, '768658 406642572 495752131', '93045331\n', 0, 4),
(@aid, '517532 725178587 481092142', '207545754\n', 0, 5),
(@aid, '714561 676333989 903280087', '841507974\n', 0, 6);

-- ---------- 121. 乘法逆元（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('乘法逆元', 3, 20, '## 【题目描述】\n\n给定互质的正整数 a 和 m，求 a 在模 m 意义下的乘法逆元 x（即满足 a·x ≡ 1 (mod m) 且 0 < x < m 的最小正整数解）。\n\n## 【输入格式】\n\n一行，两个正整数 a、m，保证 gcd(a, m) = 1。\n\n## 【输出格式】\n\n一行，一个整数，表示逆元。\n\n## 【样例】\n\n输入：\n\n```\n3 11\n```\n\n输出：\n\n```\n4\n```\n\n## 【数据范围】\n\n1 ≤ a < m ≤ 10⁹，保证互质\n\n## 【提示】\n\n扩展欧几里得求出 a·x + m·y = 1 的一组解，x 对 m 取正模即为逆元；当 m 为素数时也可用费马小定理 a^(m-2)。', '一行，两个正整数 a、m，保证 gcd(a, m) = 1。', '一行，一个整数，表示逆元。',
 '3 11', '4', '扩展欧几里得求出 a·x + m·y = 1 的一组解，x 对 m 取正模即为逆元；当 m 为素数时也可用费马小定理 a^(m-2)。', 'import sys\n\na, m = map(int, sys.stdin.read().split())\n\n\ndef exgcd(a, b):\n    if b == 0:\n        return a, 1, 0\n    g, x, y = exgcd(b, a % b)\n    return g, y, x - (a // b) * y\n\n\ng, x, y = exgcd(a, m)\nprint(x % m)\n', 'python',
 '数论,扩展欧几里得,逆元', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3 11', '4\n', 1, 1),
(@aid, '429 1009', '294\n', 0, 2),
(@aid, '6623 10007', '5107\n', 0, 3),
(@aid, '59 101', '12\n', 0, 4),
(@aid, '3 101', '34\n', 0, 5),
(@aid, '6754 10007', '6900\n', 0, 6);

-- ---------- 122. 十进制转 k 进制（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('十进制转 k 进制', 2, 10, '## 【题目描述】\n\n给定一个十进制非负整数 n 和进制 k（2 ≤ k ≤ 16），输出 n 的 k 进制表示（大于 9 的数位用大写字母 A-F 表示）。\n\n## 【输入格式】\n\n一行，两个整数 n、k。\n\n## 【输出格式】\n\n一行，转换后的字符串。\n\n## 【样例】\n\n输入：\n\n```\n255 16\n```\n\n输出：\n\n```\nFF\n```\n\n## 【数据范围】\n\n0 ≤ n ≤ 10⁹，2 ≤ k ≤ 16\n\n## 【提示】\n\n不断对 k 取余得到低位、再整除 k，最后把得到的数位逆序输出；注意 n = 0 的特判。', '一行，两个整数 n、k。', '一行，转换后的字符串。',
 '255 16', 'FF', '不断对 k 取余得到低位、再整除 k，最后把得到的数位逆序输出；注意 n = 0 的特判。', 'import sys\n\nn, k = map(int, sys.stdin.read().split())\ndigits = \'0123456789ABCDEF\'\nif n == 0:\n    print(\'0\')\nelse:\n    res = []\n    while n:\n        res.append(digits[n % k])\n        n //= k\n    print(\'\'.join(reversed(res)))\n', 'python',
 '数论,进制转换', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '255 16', 'FF\n', 1, 1),
(@aid, '655992660 11', '307321AA4\n', 0, 2),
(@aid, '890641308 5', '3311001010213\n', 0, 3),
(@aid, '772907628 2', '101110000100011010001001101100\n', 0, 4),
(@aid, '643794957 6', '143514432113\n', 0, 5),
(@aid, '235541275 16', 'E0A131B\n', 0, 6);

-- ---------- 123. k 进制转十进制（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('k 进制转十进制', 2, 10, '## 【题目描述】\n\n给定一个 k 进制（2 ≤ k ≤ 16，数位可含大写字母 A-F）的非负整数字符串 s，输出它对应的十进制值。\n\n## 【输入格式】\n\n两行。第一行为进制 k；第二行为字符串 s。\n\n## 【输出格式】\n\n一行，一个整数，表示十进制值。\n\n## 【样例】\n\n输入：\n\n```\n16\nFF\n```\n\n输出：\n\n```\n255\n```\n\n## 【数据范围】\n\n2 ≤ k ≤ 16，1 ≤ |s| ≤ 10\n\n## 【提示】\n\n秦九韶算法：ans = ans × k + 当前位的值，从左到右扫一遍即可，无需计算每一位的幂。', '两行。第一行为进制 k；第二行为字符串 s。', '一行，一个整数，表示十进制值。',
 '16\nFF', '255', '秦九韶算法：ans = ans × k + 当前位的值，从左到右扫一遍即可，无需计算每一位的幂。', 'import sys\n\ndata = sys.stdin.read().split(\'\\n\')\nk = int(data[0])\ns = data[1].strip()\nans = 0\nfor ch in s:\n    if ch.isdigit():\n        v = int(ch)\n    else:\n        v = ord(ch) - ord(\'A\') + 10\n    ans = ans * k + v\nprint(ans)\n', 'python',
 '数论,进制转换', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '16\nFF', '255\n', 1, 1),
(@aid, '14\n728', '1408\n', 0, 2),
(@aid, '14\nBCB9', '32699\n', 0, 3),
(@aid, '8\n564435', '190749\n', 0, 4),
(@aid, '9\n5263427', '2817205\n', 0, 5),
(@aid, '4\n0203', '35\n', 0, 6);

-- ---------- 124. 阶乘末尾零的个数（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('阶乘末尾零的个数', 2, 10, '## 【题目描述】\n\n给定正整数 n，求 n! 的十进制表示末尾有多少个连续的 0。\n\n## 【输入格式】\n\n一行，一个整数 n。\n\n## 【输出格式】\n\n一行，一个整数。\n\n## 【样例】\n\n输入：\n\n```\n100\n```\n\n输出：\n\n```\n24\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁹\n\n## 【提示】\n\n每个末尾 0 来自因子 2 × 5，而因子 2 远多于 5，所以只需统计 1..n 中因子 5 的总个数：不断除以 5 累加。', '一行，一个整数 n。', '一行，一个整数。',
 '100', '24', '每个末尾 0 来自因子 2 × 5，而因子 2 远多于 5，所以只需统计 1..n 中因子 5 的总个数：不断除以 5 累加。', 'import sys\n\nn = int(sys.stdin.read().strip())\nans = 0\nwhile n:\n    n //= 5\n    ans += n\nprint(ans)\n', 'python',
 '数论,阶乘,计数', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '100', '24\n', 1, 1),
(@aid, '392663', '98163\n', 0, 2),
(@aid, '604257', '151060\n', 0, 3),
(@aid, '79569', '19889\n', 0, 4),
(@aid, '910732', '227679\n', 0, 5),
(@aid, '524982', '131240\n', 0, 6);

-- ---------- 125. 完全平方数判定（难度 1） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('完全平方数判定', 1, 10, '## 【题目描述】\n\n给定一个非负整数 n，判断它是否为完全平方数。\n\n## 【输入格式】\n\n一行，一个整数 n。\n\n## 【输出格式】\n\n一行，是输出 Yes，否则输出 No。\n\n## 【样例】\n\n输入：\n\n```\n144\n```\n\n输出：\n\n```\nYes\n```\n\n## 【数据范围】\n\n0 ≤ n ≤ 10¹²\n\n## 【提示】\n\n用整数平方根 isqrt 再平方比较，避免浮点误差；也可二分查找。', '一行，一个整数 n。', '一行，是输出 Yes，否则输出 No。',
 '144', 'Yes', '用整数平方根 isqrt 再平方比较，避免浮点误差；也可二分查找。', 'import sys\nimport math\n\nn = int(sys.stdin.read().strip())\nr = int(math.isqrt(n))\nprint(\'Yes\' if r * r == n else \'No\')\n', 'python',
 '数论,二分,数学', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '144', 'Yes\n', 1, 1),
(@aid, '245241752011', 'No\n', 0, 2),
(@aid, '296303588663', 'No\n', 0, 3),
(@aid, '840905317627', 'No\n', 0, 4),
(@aid, '181985842984', 'No\n', 0, 5),
(@aid, '100948377465', 'No\n', 0, 6);

-- ---------- 126. 约数个数（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('约数个数', 2, 10, '## 【题目描述】\n\n给定一个正整数 n，求它的正约数个数。\n\n## 【输入格式】\n\n一行，一个整数 n。\n\n## 【输出格式】\n\n一行，一个整数。\n\n## 【样例】\n\n输入：\n\n```\n12\n```\n\n输出：\n\n```\n6\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁹\n\n## 【提示】\n\n先质因数分解 n = ∏ pᵢ^aᵢ，则约数个数为 ∏(aᵢ + 1)：每个质因子可选 0..aᵢ 个。', '一行，一个整数 n。', '一行，一个整数。',
 '12', '6', '先质因数分解 n = ∏ pᵢ^aᵢ，则约数个数为 ∏(aᵢ + 1)：每个质因子可选 0..aᵢ 个。', 'import sys\n\nn = int(sys.stdin.read().strip())\nans = 1\nd = 2\ncnt = 0\nwhile d * d <= n:\n    while n % d == 0:\n        cnt += 1\n        n //= d\n    if cnt:\n        ans *= cnt + 1\n        cnt = 0\n    d += 1\nif n > 1:\n    ans *= 2\nprint(ans)\n', 'python',
 '数论,约数,分解', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '12', '6\n', 1, 1),
(@aid, '341713527', '8\n', 0, 2),
(@aid, '191624244', '48\n', 0, 3),
(@aid, '607653438', '32\n', 0, 4),
(@aid, '866812538', '4\n', 0, 5),
(@aid, '798426433', '12\n', 0, 6);

-- ---------- 127. 约数之和（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('约数之和', 2, 10, '## 【题目描述】\n\n给定一个正整数 n，求它的所有正约数之和。\n\n## 【输入格式】\n\n一行，一个整数 n。\n\n## 【输出格式】\n\n一行，一个整数。\n\n## 【样例】\n\n输入：\n\n```\n12\n```\n\n输出：\n\n```\n28\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁸\n\n## 【提示】\n\n若 n = ∏ pᵢ^aᵢ，则约数和为 ∏(1 + pᵢ + … + pᵢ^aᵢ)；代码中的 p = p*d + 1 正是等比和的递推。', '一行，一个整数 n。', '一行，一个整数。',
 '12', '28', '若 n = ∏ pᵢ^aᵢ，则约数和为 ∏(1 + pᵢ + … + pᵢ^aᵢ)；代码中的 p = p*d + 1 正是等比和的递推。', 'import sys\n\nn = int(sys.stdin.read().strip())\nans = 1\nd = 2\nwhile d * d <= n:\n    if n % d == 0:\n        p = 1\n        while n % d == 0:\n            n //= d\n            p = p * d + 1\n        ans *= p\n    d += 1\nif n > 1:\n    ans *= n + 1\nprint(ans)\n', 'python',
 '数论,约数,等比数列', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '12', '28\n', 1, 1),
(@aid, '41029256', '76929870\n', 0, 2),
(@aid, '42012895', '53676000\n', 0, 3),
(@aid, '6576035', '8038992\n', 0, 4),
(@aid, '51714296', '96964320\n', 0, 5),
(@aid, '20277622', '30416436\n', 0, 6);

-- ---------- 128. 最大质因子（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('最大质因子', 2, 10, '## 【题目描述】\n\n给定一个大于 1 的整数 n，求它的最大质因子。\n\n## 【输入格式】\n\n一行，一个整数 n。\n\n## 【输出格式】\n\n一行，一个整数。\n\n## 【样例】\n\n输入：\n\n```\n60\n```\n\n输出：\n\n```\n5\n```\n\n## 【数据范围】\n\n2 ≤ n ≤ 10⁹\n\n## 【提示】\n\n边分解边记录最后除尽的因子；循环结束后若剩余的 n 大于 1，它本身就是最大的质因子。', '一行，一个整数 n。', '一行，一个整数。',
 '60', '5', '边分解边记录最后除尽的因子；循环结束后若剩余的 n 大于 1，它本身就是最大的质因子。', 'import sys\n\nn = int(sys.stdin.read().strip())\nans = 1\nd = 2\nwhile d * d <= n:\n    while n % d == 0:\n        ans = d\n        n //= d\n    d += 1\nif n > 1:\n    ans = n\nprint(ans)\n', 'python',
 '数论,质因数', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '60', '5\n', 1, 1),
(@aid, '243486902', '16963\n', 0, 2),
(@aid, '503188268', '187477\n', 0, 3),
(@aid, '234167582', '10643981\n', 0, 4),
(@aid, '84245569', '46061\n', 0, 5),
(@aid, '27337881', '17903\n', 0, 6);

-- ---------- 129. 欧拉函数（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('欧拉函数', 3, 20, '## 【题目描述】\n\n给定正整数 n，求欧拉函数 φ(n)，即 1 到 n 中与 n 互质的数的个数。\n\n## 【输入格式】\n\n一行，一个整数 n。\n\n## 【输出格式】\n\n一行，一个整数。\n\n## 【样例】\n\n输入：\n\n```\n10\n```\n\n输出：\n\n```\n4\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁹\n\n## 【提示】\n\n利用公式 φ(n) = n × ∏(1 - 1/p)：对每个不同质因子 p，执行 ans = ans // p × (p - 1)。', '一行，一个整数 n。', '一行，一个整数。',
 '10', '4', '利用公式 φ(n) = n × ∏(1 - 1/p)：对每个不同质因子 p，执行 ans = ans // p × (p - 1)。', 'import sys\n\nn = int(sys.stdin.read().strip())\nans = n\nx = n\nd = 2\nwhile d * d <= x:\n    if x % d == 0:\n        while x % d == 0:\n            x //= d\n        ans = ans // d * (d - 1)\n    d += 1\nif x > 1:\n    ans = ans // x * (x - 1)\nprint(ans)\n', 'python',
 '数论,欧拉函数', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '10', '4\n', 1, 1),
(@aid, '588792516', '178459776\n', 0, 2),
(@aid, '652320966', '196848000\n', 0, 3),
(@aid, '200686547', '183644160\n', 0, 4),
(@aid, '427063441', '362499840\n', 0, 5),
(@aid, '434263600', '170752000\n', 0, 6);

-- ---------- 130. 分数化简（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('分数化简', 2, 10, '## 【题目描述】\n\n给定一个分数 a/b，将其化为最简分数后输出；若分母为 1 则只输出分子。\n\n## 【输入格式】\n\n一行，形如 a/b 的分数（a、b 为正整数）。\n\n## 【输出格式】\n\n一行，化简后的结果。\n\n## 【样例】\n\n输入：\n\n```\n12/18\n```\n\n输出：\n\n```\n2/3\n```\n\n## 【数据范围】\n\n1 ≤ a, b ≤ 10⁹\n\n## 【提示】\n\n分子分母同除以最大公约数即得最简分数；注意化简后分母为 1 时的输出格式。', '一行，形如 a/b 的分数（a、b 为正整数）。', '一行，化简后的结果。',
 '12/18', '2/3', '分子分母同除以最大公约数即得最简分数；注意化简后分母为 1 时的输出格式。', 'import sys\nimport math\n\ns = sys.stdin.read().strip()\na, b = map(int, s.split(\'/\'))\ng = math.gcd(a, b)\na //= g\nb //= g\nprint(str(a) if b == 1 else \'%d/%d\' % (a, b))\n', 'python',
 '数论,gcd,分数', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '12/18', '2/3\n', 1, 1),
(@aid, '152/44', '38/11\n', 0, 2),
(@aid, '99/29', '99/29\n', 0, 3),
(@aid, '105/26', '105/26\n', 0, 4),
(@aid, '198/19', '198/19\n', 0, 5),
(@aid, '23/32', '23/32\n', 0, 6);

-- ---------- 131. 分数加法（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('分数加法', 2, 10, '## 【题目描述】\n\n给定两个分数 a/b 和 c/d，求它们的和，并化为最简分数输出；若分母为 1 则只输出分子。\n\n## 【输入格式】\n\n一行，两个形如 a/b 的分数，用空格分隔。\n\n## 【输出格式】\n\n一行，相加并化简后的结果。\n\n## 【样例】\n\n输入：\n\n```\n1/2 1/3\n```\n\n输出：\n\n```\n5/6\n```\n\n## 【数据范围】\n\n1 ≤ a, b, c, d ≤ 10⁴\n\n## 【提示】\n\n通分后分子相加，再用 gcd 约分；先通分后约分可以少写一次约分逻辑。', '一行，两个形如 a/b 的分数，用空格分隔。', '一行，相加并化简后的结果。',
 '1/2 1/3', '5/6', '通分后分子相加，再用 gcd 约分；先通分后约分可以少写一次约分逻辑。', 'import sys\nimport math\n\nparts = sys.stdin.read().split()\na, b = map(int, parts[0].split(\'/\'))\nc, d = map(int, parts[1].split(\'/\'))\np = a * d + c * b\nq = b * d\ng = math.gcd(p, q)\np //= g\nq //= g\nprint(str(p) if q == 1 else \'%d/%d\' % (p, q))\n', 'python',
 '数论,gcd,分数运算', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '1/2 1/3', '5/6\n', 1, 1),
(@aid, '12/58 162/51', '1668/493\n', 0, 2),
(@aid, '200/19 35/33', '7265/627\n', 0, 3),
(@aid, '147/3 26/47', '2329/47\n', 0, 4),
(@aid, '91/32 95/18', '2339/288\n', 0, 5),
(@aid, '3/27 102/49', '967/441\n', 0, 6);

-- ---------- 132. 斐波那契第 n 项取模（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('斐波那契第 n 项取模', 2, 10, '## 【题目描述】\n\n求斐波那契数列第 n 项对 10⁹+7 取模的值。数列定义为 F(1) = 1，F(2) = 1，F(n) = F(n-1) + F(n-2)（n ≥ 3）。\n\n## 【输入格式】\n\n一行，一个整数 n。\n\n## 【输出格式】\n\n一行，一个整数。\n\n## 【样例】\n\n输入：\n\n```\n10\n```\n\n输出：\n\n```\n55\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁷\n\n## 【提示】\n\n滚动变量迭代即可，只需保留前两项，边加边取模防止数值爆炸，O(n) 时间 O(1) 空间。', '一行，一个整数 n。', '一行，一个整数。',
 '10', '55', '滚动变量迭代即可，只需保留前两项，边加边取模防止数值爆炸，O(n) 时间 O(1) 空间。', 'import sys\n\nMOD = 10 ** 9 + 7\nn = int(sys.stdin.read().strip())\na, b = 1, 1\nfor _ in range(3, n + 1):\n    a, b = b, (a + b) % MOD\nprint(a if n <= 2 else b % MOD)\n', 'python',
 '递推,取模,斐波那契', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '10', '55\n', 1, 1),
(@aid, '844370', '836233114\n', 0, 2),
(@aid, '531467', '643312741\n', 0, 3),
(@aid, '805243', '263543265\n', 0, 4),
(@aid, '810248', '276776090\n', 0, 5),
(@aid, '426539', '490757911\n', 0, 6);

-- ---------- 133. 3n+1 问题（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('3n+1 问题', 2, 10, '## 【题目描述】\n\n给定一个正整数 n，反复执行：若为偶数则除以 2，若为奇数则变为 3n+1，直到变成 1 为止。求需要的变换次数。\n\n## 【输入格式】\n\n一行，一个整数 n。\n\n## 【输出格式】\n\n一行，一个整数，表示变换次数。\n\n## 【样例】\n\n输入：\n\n```\n3\n```\n\n输出：\n\n```\n7\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁶\n\n## 【提示】\n\n直接按规则模拟即可（考拉兹猜想至今未被证明，但对题目给定范围一定收敛）。注意用整数运算避免溢出。', '一行，一个整数 n。', '一行，一个整数，表示变换次数。',
 '3', '7', '直接按规则模拟即可（考拉兹猜想至今未被证明，但对题目给定范围一定收敛）。注意用整数运算避免溢出。', 'import sys\n\nn = int(sys.stdin.read().strip())\ncnt = 0\nwhile n != 1:\n    if n % 2 == 0:\n        n //= 2\n    else:\n        n = 3 * n + 1\n    cnt += 1\nprint(cnt)\n', 'python',
 '模拟,数论,考拉兹', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3', '7\n', 1, 1),
(@aid, '956', '54\n', 0, 2),
(@aid, '774', '121\n', 0, 3),
(@aid, '678', '51\n', 0, 4),
(@aid, '758', '59\n', 0, 5),
(@aid, '738', '20\n', 0, 6);

-- ---------- 134. 数字黑洞 495（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('数字黑洞 495', 2, 10, '## 【题目描述】\n\n给定一个各位数字不全相同的三位数 n，重复下列操作：把三个数字重新排列成最大数和最小数（允许前导零），用最大数减最小数得到新数；直到结果等于 495 为止。求操作的次数。\n\n## 【输入格式】\n\n一行，一个三位数 n（各位数字不全相同）。\n\n## 【输出格式】\n\n一行，一个整数，表示操作次数。\n\n## 【样例】\n\n输入：\n\n```\n123\n```\n\n输出：\n\n```\n5\n```\n\n## 【数据范围】\n\n100 ≤ n ≤ 999，各位数字不全相同\n\n## 【提示】\n\n每次重排得到最大与最小三位数并相减；补零用 \'%03d\' 格式化保证始终取到三位，最终必然收敛到 495。', '一行，一个三位数 n（各位数字不全相同）。', '一行，一个整数，表示操作次数。',
 '123', '5', '每次重排得到最大与最小三位数并相减；补零用 \'%03d\' 格式化保证始终取到三位，最终必然收敛到 495。', 'import sys\n\nn = int(sys.stdin.read().strip())\ncnt = 0\nwhile n != 495:\n    digits = sorted(\'%03d\' % n)\n    small = int(\'\'.join(digits))\n    big = int(\'\'.join(reversed(digits)))\n    n = big - small\n    cnt += 1\nprint(cnt)\n', 'python',
 '模拟,数论,卡普雷卡尔', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '123', '5\n', 1, 1),
(@aid, '852', '2\n', 0, 2),
(@aid, '443', '6\n', 0, 3),
(@aid, '845', '3\n', 0, 4),
(@aid, '391', '4\n', 0, 5),
(@aid, '478', '3\n', 0, 6);

-- ---------- 135. 爬楼梯（斐波那契递推）（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('爬楼梯（斐波那契递推）', 2, 10, '## 【题目描述】\n\n有 n 阶楼梯，每次可以上 1 阶或 2 阶，求到达顶楼的不同方法数（答案保证在 64 位整数范围内）。\n\n## 【输入格式】\n\n一行，一个整数 n。\n\n## 【输出格式】\n\n一行，一个整数，表示方法数。\n\n## 【样例】\n\n输入：\n\n```\n5\n```\n\n输出：\n\n```\n8\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 60\n\n## 【提示】\n\n设 f(n) 为到达第 n 阶的方法数，最后一跳可能是 1 阶或 2 阶，故 f(n) = f(n-1) + f(n-2)，即斐波那契。', '一行，一个整数 n。', '一行，一个整数，表示方法数。',
 '5', '8', '设 f(n) 为到达第 n 阶的方法数，最后一跳可能是 1 阶或 2 阶，故 f(n) = f(n-1) + f(n-2)，即斐波那契。', 'import sys\n\nn = int(sys.stdin.read().strip())\na, b = 1, 1\nfor _ in range(2, n + 1):\n    a, b = b, a + b\nprint(b)\n', 'python',
 '动态规划,递推,斐波那契', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '5', '8\n', 1, 1),
(@aid, '11', '144\n', 0, 2),
(@aid, '28', '514229\n', 0, 3),
(@aid, '1', '1\n', 0, 4),
(@aid, '60', '2504730781961\n', 0, 5),
(@aid, '1', '1\n', 0, 6);

-- ---------- 136. 数字三角形（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('数字三角形', 2, 10, '## 【题目描述】\n\n给定一个 n 行的数字三角形，从第 1 行唯一的数出发，每次可以走到下一行中与当前位置相邻（正下方或右下方）的数，求到达最后一行时经过的数字之和的最大值。\n\n## 【输入格式】\n\n第一行一个整数 n；接下来 n 行，第 i 行有 i 个整数。\n\n## 【输出格式】\n\n一行，一个整数，表示最大和。\n\n## 【样例】\n\n输入：\n\n```\n5\n7\n3 8\n8 1 0\n2 7 4 4\n4 5 2 6 5\n```\n\n输出：\n\n```\n30\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 100，每个数 ∈ [0, 100]\n\n## 【提示】\n\n自底向上递推：dp[i][j] = a[i][j] + max(dp[i+1][j], dp[i+1][j+1])，可直接在原数组上原地累加，省去额外空间。', '第一行一个整数 n；接下来 n 行，第 i 行有 i 个整数。', '一行，一个整数，表示最大和。',
 '5\n7\n3 8\n8 1 0\n2 7 4 4\n4 5 2 6 5', '30', '自底向上递推：dp[i][j] = a[i][j] + max(dp[i+1][j], dp[i+1][j+1])，可直接在原数组上原地累加，省去额外空间。', 'import sys\n\ndata = list(map(int, sys.stdin.read().split()))\nn = data[0]\nvals = data[1:]\ntri = []\npos = 0\nfor i in range(1, n + 1):\n    tri.append(vals[pos:pos + i])\n    pos += i\nfor i in range(n - 2, -1, -1):\n    for j in range(len(tri[i])):\n        tri[i][j] += max(tri[i + 1][j], tri[i + 1][j + 1])\nprint(tri[0][0])\n', 'python',
 '动态规划,线性DP', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '5\n7\n3 8\n8 1 0\n2 7 4 4\n4 5 2 6 5', '30\n', 1, 1),
(@aid, '4\n8\n12 7\n10 5 13\n3 5 5 17', '45\n', 0, 2),
(@aid, '4\n4\n9 19\n7 6 4\n17 0 11 6', '40\n', 0, 3),
(@aid, '2\n11\n6 1', '17\n', 0, 4),
(@aid, '8\n15\n18 10\n2 7 2\n17 11 19 4\n0 10 4 13 15\n12 12 20 9 18 15\n10 3 5 0 1 13 13\n5 20 5 15 10 16 13 20', '119\n', 0, 5),
(@aid, '2\n10\n11 17', '27\n', 0, 6);

-- ---------- 137. 不同路径数（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('不同路径数', 2, 10, '## 【题目描述】\n\n一个机器人位于 m 行 n 列网格的左上角，每次只能向右或向下移动一步，问到达右下角共有多少条不同路径。\n\n## 【输入格式】\n\n一行，两个整数 m、n。\n\n## 【输出格式】\n\n一行，一个整数，表示路径条数（保证不超过 64 位整数）。\n\n## 【样例】\n\n输入：\n\n```\n3 3\n```\n\n输出：\n\n```\n6\n```\n\n## 【数据范围】\n\n1 ≤ m, n ≤ 30\n\n## 【提示】\n\ndp[i][j] = dp[i-1][j] + dp[i][j-1]，第一行第一列均为 1；用一维数组滚动可把空间压到 O(n)。', '一行，两个整数 m、n。', '一行，一个整数，表示路径条数（保证不超过 64 位整数）。',
 '3 3', '6', 'dp[i][j] = dp[i-1][j] + dp[i][j-1]，第一行第一列均为 1；用一维数组滚动可把空间压到 O(n)。', 'import sys\n\nm, n = map(int, sys.stdin.read().split())\ndp = [1] * n\nfor _ in range(1, m):\n    for j in range(1, n):\n        dp[j] += dp[j - 1]\nprint(dp[n - 1])\n', 'python',
 '动态规划,网格DP,计数', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3 3', '6\n', 1, 1),
(@aid, '11 7', '8008\n', 0, 2),
(@aid, '15 4', '680\n', 0, 3),
(@aid, '12 9', '75582\n', 0, 4),
(@aid, '4 9', '165\n', 0, 5),
(@aid, '6 14', '8568\n', 0, 6);

-- ---------- 138. 最低通行费（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('最低通行费', 2, 10, '## 【题目描述】\n\n一个 n × n 的网格，每个格子有一个费用。从左上角走到右下角，每次只能向右或向下走，求经过格子的费用之和（包含起点与终点）的最小值。\n\n## 【输入格式】\n\n第一行一个整数 n；接下来 n 行，每行 n 个整数。\n\n## 【输出格式】\n\n一行，一个整数，表示最小费用。\n\n## 【样例】\n\n输入：\n\n```\n3\n1 3 1\n1 5 1\n4 2 1\n```\n\n输出：\n\n```\n7\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 100，费用 ∈ [1, 100]\n\n## 【提示】\n\n与"不同路径数"同构，只是把计数换成取最小值；注意起点要单独初始化。', '第一行一个整数 n；接下来 n 行，每行 n 个整数。', '一行，一个整数，表示最小费用。',
 '3\n1 3 1\n1 5 1\n4 2 1', '7', '与"不同路径数"同构，只是把计数换成取最小值；注意起点要单独初始化。', 'import sys\n\ndata = list(map(int, sys.stdin.read().split()))\nn = data[0]\na = [data[1 + i * n:1 + (i + 1) * n] for i in range(n)]\nINF = 10 ** 15\ndp = [[INF] * n for _ in range(n)]\ndp[0][0] = a[0][0]\nfor i in range(n):\n    for j in range(n):\n        if i == 0 and j == 0:\n            continue\n        best = INF\n        if i:\n            best = min(best, dp[i - 1][j])\n        if j:\n            best = min(best, dp[i][j - 1])\n        dp[i][j] = best + a[i][j]\nprint(dp[n - 1][n - 1])\n', 'python',
 '动态规划,网格DP', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3\n1 3 1\n1 5 1\n4 2 1', '7\n', 1, 1),
(@aid, '4\n18 12 27 16\n18 12 26 14\n7 13 25 21\n22 22 6 10', '93\n', 0, 2),
(@aid, '8\n29 7 2 11 25 19 2 21\n24 30 30 4 30 29 4 10\n3 24 27 19 27 7 30 1\n9 2 21 29 28 12 13 25\n20 16 23 2 15 3 8 4\n14 6 3 4 2 24 24 27\n27 1 1 30 25 25 29 15\n27 30 8 14 30 7 8 2', '160\n', 0, 3),
(@aid, '2\n12 25\n14 4', '30\n', 0, 4),
(@aid, '4\n7 21 7 22\n3 3 3 11\n18 1 8 10\n22 15 7 6', '35\n', 0, 5),
(@aid, '4\n4 15 30 6\n1 30 18 22\n10 15 10 4\n25 12 12 17', '61\n', 0, 6);

-- ---------- 139. 最长上升子序列（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('最长上升子序列', 3, 20, '## 【题目描述】\n\n给定一个长度为 n 的整数序列，求它的最长严格上升子序列的长度。\n\n## 【输入格式】\n\n第一行一个整数 n；第二行 n 个整数。\n\n## 【输出格式】\n\n一行，一个整数。\n\n## 【样例】\n\n输入：\n\n```\n8\n10 9 2 5 3 7 101 18\n```\n\n输出：\n\n```\n4\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁵\n\n## 【提示】\n\ntails[k] 维护长度为 k+1 的上升子序列的最小结尾，用二分找到第一个 ≥ x 的位置替换它，复杂度 O(n log n)。', '第一行一个整数 n；第二行 n 个整数。', '一行，一个整数。',
 '8\n10 9 2 5 3 7 101 18', '4', 'tails[k] 维护长度为 k+1 的上升子序列的最小结尾，用二分找到第一个 ≥ x 的位置替换它，复杂度 O(n log n)。', 'import sys\nimport bisect\n\ndata = list(map(int, sys.stdin.read().split()))\nn = data[0]\na = data[1:1 + n]\ntails = []\nfor x in a:\n    i = bisect.bisect_left(tails, x)\n    if i == len(tails):\n        tails.append(x)\n    else:\n        tails[i] = x\nprint(len(tails))\n', 'python',
 '动态规划,LIS,二分', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '8\n10 9 2 5 3 7 101 18', '4\n', 1, 1),
(@aid, '14\n396 222 120 429 382 300 299 12 405 290 36 4 230 214', '3\n', 0, 2),
(@aid, '16\n454 234 7 405 67 191 411 25 281 141 61 446 2 476 30 400', '6\n', 0, 3),
(@aid, '7\n487 424 188 284 458 171 453', '3\n', 0, 4),
(@aid, '13\n224 452 154 239 337 229 443 218 417 133 343 97 337', '4\n', 0, 5),
(@aid, '1\n271', '1\n', 0, 6);

-- ---------- 140. 最长公共子序列（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('最长公共子序列', 3, 20, '## 【题目描述】\n\n给定两个字符串 s 和 t，求它们的最长公共子序列的长度（子序列不要求连续，但顺序必须一致）。\n\n## 【输入格式】\n\n两行，每行一个字符串。\n\n## 【输出格式】\n\n一行，一个整数。\n\n## 【样例】\n\n输入：\n\n```\nabcde\nace\n```\n\n输出：\n\n```\n3\n```\n\n## 【数据范围】\n\n1 ≤ |s|, |t| ≤ 1000\n\n## 【提示】\n\n经典二维 DP：字符相等时 dp[i][j] = dp[i-1][j-1] + 1，否则取 dp[i-1][j] 与 dp[i][j-1] 的最大值；可用滚动数组降维。', '两行，每行一个字符串。', '一行，一个整数。',
 'abcde\nace', '3', '经典二维 DP：字符相等时 dp[i][j] = dp[i-1][j-1] + 1，否则取 dp[i-1][j] 与 dp[i][j-1] 的最大值；可用滚动数组降维。', 'import sys\n\ndata = sys.stdin.read().split(\'\\n\')\ns = data[0].strip()\nt = data[1].strip()\nn, m = len(s), len(t)\ndp = [0] * (m + 1)\nfor i in range(1, n + 1):\n    prev = 0\n    for j in range(1, m + 1):\n        tmp = dp[j]\n        if s[i - 1] == t[j - 1]:\n            dp[j] = prev + 1\n        else:\n            dp[j] = max(dp[j], dp[j - 1])\n        prev = tmp\nprint(dp[m])\n', 'python',
 '动态规划,LCS', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'abcde\nace', '3\n', 1, 1),
(@aid, 'bee\ncecdaee', '2\n', 0, 2),
(@aid, 'eaadcbbcbc\nabdaaadce', '4\n', 0, 3),
(@aid, 'bbebabd\ncebcbea', '4\n', 0, 4),
(@aid, 'eeee\nbeaa', '1\n', 0, 5),
(@aid, 'acaaebccb\ndbaaeeabdd', '4\n', 0, 6);

-- ---------- 141. 最长公共子串（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('最长公共子串', 2, 10, '## 【题目描述】\n\n给定两个字符串 s 和 t，求它们的最长公共子串的长度（子串要求连续）。\n\n## 【输入格式】\n\n两行，每行一个字符串。\n\n## 【输出格式】\n\n一行，一个整数。\n\n## 【样例】\n\n输入：\n\n```\nabcdef\ncde\n```\n\n输出：\n\n```\n3\n```\n\n## 【数据范围】\n\n1 ≤ |s|, |t| ≤ 1000\n\n## 【提示】\n\n与 LCS 的区别在于：字符失配时 dp 值必须清零（子串要求连续），答案在过程中取最大值而不是取 dp[n][m]。', '两行，每行一个字符串。', '一行，一个整数。',
 'abcdef\ncde', '3', '与 LCS 的区别在于：字符失配时 dp 值必须清零（子串要求连续），答案在过程中取最大值而不是取 dp[n][m]。', 'import sys\n\ndata = sys.stdin.read().split(\'\\n\')\ns = data[0].strip()\nt = data[1].strip()\nn, m = len(s), len(t)\ndp = [0] * (m + 1)\nans = 0\nfor i in range(1, n + 1):\n    prev = 0\n    for j in range(1, m + 1):\n        tmp = dp[j]\n        if s[i - 1] == t[j - 1]:\n            dp[j] = prev + 1\n        else:\n            dp[j] = 0\n        prev = tmp\n        ans = max(ans, dp[j])\nprint(ans)\n', 'python',
 '动态规划,子串', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'abcdef\ncde', '3\n', 1, 1),
(@aid, 'eabcebec\nebcbcaabc', '3\n', 0, 2),
(@aid, 'bbceedde\naeedced', '3\n', 0, 3),
(@aid, 'acbdea\nbacabc', '2\n', 0, 4),
(@aid, 'edbedacacc\naca', '3\n', 0, 5),
(@aid, 'bceecbd\ndbdadc', '2\n', 0, 6);

-- ---------- 142. 0/1 背包（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('0/1 背包', 3, 20, '## 【题目描述】\n\n有 n 个物品和一个容量为 W 的背包，每个物品只能取一次，第 i 个物品重量为 wᵢ、价值为 vᵢ。求在不超过容量的前提下能取得的最大总价值。\n\n## 【输入格式】\n\n第一行两个整数 n、W；接下来 n 行，每行两个整数 wᵢ、vᵢ。\n\n## 【输出格式】\n\n一行，一个整数，表示最大总价值。\n\n## 【样例】\n\n输入：\n\n```\n4 5\n2 3\n1 2\n3 4\n2 2\n```\n\n输出：\n\n```\n7\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 100，1 ≤ W ≤ 1000\n\n## 【提示】\n\n一维滚动数组的关键：容量必须**从大到小**枚举，保证每个物品只被放入一次（否则就变成完全背包）。', '第一行两个整数 n、W；接下来 n 行，每行两个整数 wᵢ、vᵢ。', '一行，一个整数，表示最大总价值。',
 '4 5\n2 3\n1 2\n3 4\n2 2', '7', '一维滚动数组的关键：容量必须**从大到小**枚举，保证每个物品只被放入一次（否则就变成完全背包）。', 'import sys\n\ndata = list(map(int, sys.stdin.read().split()))\nn, W = data[0], data[1]\ndp = [0] * (W + 1)\np = 2\nfor _ in range(n):\n    w, v = data[p], data[p + 1]\n    p += 2\n    for j in range(W, w - 1, -1):\n        if dp[j - w] + v > dp[j]:\n            dp[j] = dp[j - w] + v\nprint(max(dp))\n', 'python',
 '动态规划,背包,0/1背包', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '4 5\n2 3\n1 2\n3 4\n2 2', '7\n', 1, 1),
(@aid, '6 17\n17 24\n4 29\n5 46\n4 5\n1 28\n14 13', '108\n', 0, 2),
(@aid, '7 20\n14 48\n20 14\n13 11\n4 11\n13 21\n8 25\n17 33', '59\n', 0, 3),
(@aid, '4 12\n1 19\n6 17\n4 42\n10 43', '78\n', 0, 4),
(@aid, '2 20\n6 2\n4 37', '39\n', 0, 5),
(@aid, '7 10\n6 21\n3 29\n3 23\n2 38\n5 40\n7 9\n3 33', '111\n', 0, 6);

-- ---------- 143. 完全背包（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('完全背包', 3, 20, '## 【题目描述】\n\n有 n 种物品和一个容量为 W 的背包，每种物品可以取任意多个，第 i 种物品重量为 wᵢ、价值为 vᵢ。求在不超过容量的前提下能取得的最大总价值。\n\n## 【输入格式】\n\n第一行两个整数 n、W；接下来 n 行，每行两个整数 wᵢ、vᵢ。\n\n## 【输出格式】\n\n一行，一个整数，表示最大总价值。\n\n## 【样例】\n\n输入：\n\n```\n3 7\n2 3\n3 4\n4 5\n```\n\n输出：\n\n```\n10\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 100，1 ≤ W ≤ 1000\n\n## 【提示】\n\n与 0/1 背包唯一的区别是容量**从小到大**枚举，这样同一个物品可以被重复选取。', '第一行两个整数 n、W；接下来 n 行，每行两个整数 wᵢ、vᵢ。', '一行，一个整数，表示最大总价值。',
 '3 7\n2 3\n3 4\n4 5', '10', '与 0/1 背包唯一的区别是容量**从小到大**枚举，这样同一个物品可以被重复选取。', 'import sys\n\ndata = list(map(int, sys.stdin.read().split()))\nn, W = data[0], data[1]\ndp = [0] * (W + 1)\np = 2\nfor _ in range(n):\n    w, v = data[p], data[p + 1]\n    p += 2\n    for j in range(w, W + 1):\n        if dp[j - w] + v > dp[j]:\n            dp[j] = dp[j - w] + v\nprint(max(dp))\n', 'python',
 '动态规划,背包,完全背包', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3 7\n2 3\n3 4\n4 5', '10\n', 1, 1),
(@aid, '6 25\n9 48\n14 15\n16 1\n16 20\n25 38\n18 25', '96\n', 0, 2),
(@aid, '1 5\n4 39', '39\n', 0, 3),
(@aid, '6 12\n9 41\n3 45\n2 50\n7 6\n7 48\n4 34', '300\n', 0, 4),
(@aid, '4 6\n4 25\n4 46\n3 21\n4 47', '47\n', 0, 5),
(@aid, '1 28\n1 26', '728\n', 0, 6);

-- ---------- 144. 硬币找零（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('硬币找零', 3, 20, '## 【题目描述】\n\n给定 n 种面值的硬币和一个目标金额 M，每种硬币可以无限使用，求凑出 M 所需的最少硬币数；若无法凑出，输出 -1。\n\n## 【输入格式】\n\n第一行两个整数 n、M；第二行 n 个整数，表示各硬币面值。\n\n## 【输出格式】\n\n一行，一个整数。\n\n## 【样例】\n\n输入：\n\n```\n3 11\n1 2 5\n```\n\n输出：\n\n```\n3\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 20，1 ≤ M ≤ 10⁴\n\n## 【提示】\n\n完全背包的最小值版本：dp[j] = min(dp[j], dp[j-c] + 1)，初始化 dp[0] = 0、其余为无穷大，最后判断是否仍为无穷。', '第一行两个整数 n、M；第二行 n 个整数，表示各硬币面值。', '一行，一个整数。',
 '3 11\n1 2 5', '3', '完全背包的最小值版本：dp[j] = min(dp[j], dp[j-c] + 1)，初始化 dp[0] = 0、其余为无穷大，最后判断是否仍为无穷。', 'import sys\n\ndata = list(map(int, sys.stdin.read().split()))\nn, M = data[0], data[1]\ncoins = data[2:2 + n]\nINF = 10 ** 9\ndp = [INF] * (M + 1)\ndp[0] = 0\nfor c in coins:\n    for j in range(c, M + 1):\n        if dp[j - c] + 1 < dp[j]:\n            dp[j] = dp[j - c] + 1\nprint(-1 if dp[M] >= INF else dp[M])\n', 'python',
 '动态规划,背包,完全背包', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3 11\n1 2 5', '3\n', 1, 1),
(@aid, '1 118\n22', '-1\n', 0, 2),
(@aid, '1 169\n2', '-1\n', 0, 3),
(@aid, '6 84\n1 9 10 14 27 30', '3\n', 0, 4),
(@aid, '7 8\n1 12 13 15 17 18 24', '8\n', 0, 5),
(@aid, '6 181\n1 3 5 6 26 29', '8\n', 0, 6);

-- ---------- 145. 装箱问题（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('装箱问题', 2, 10, '## 【题目描述】\n\n有一个容量为 V 的箱子和 n 个物品，每个物品有一个体积。求在箱子中放入若干物品后，箱子剩余空间的最小值。\n\n## 【输入格式】\n\n第一行一个整数 V；第二行一个整数 n；接下来 n 行，每行一个整数表示物品体积。\n\n## 【输出格式】\n\n一行，一个整数，表示最小剩余空间。\n\n## 【样例】\n\n输入：\n\n```\n24\n6\n8\n3\n12\n7\n9\n7\n```\n\n输出：\n\n```\n0\n```\n\n## 【数据范围】\n\n1 ≤ V ≤ 20000，1 ≤ n ≤ 30\n\n## 【提示】\n\n把"价值"看成体积本身，就是求不超过 V 的最大可装体积（0/1 背包），答案用 V 减去它。', '第一行一个整数 V；第二行一个整数 n；接下来 n 行，每行一个整数表示物品体积。', '一行，一个整数，表示最小剩余空间。',
 '24\n6\n8\n3\n12\n7\n9\n7', '0', '把"价值"看成体积本身，就是求不超过 V 的最大可装体积（0/1 背包），答案用 V 减去它。', 'import sys\n\ndata = list(map(int, sys.stdin.read().split()))\nV = data[0]\nn = data[1]\nitems = data[2:2 + n]\ndp = [0] * (V + 1)\nfor w in items:\n    for j in range(V, w - 1, -1):\n        if dp[j - w] + w > dp[j]:\n            dp[j] = dp[j - w] + w\nprint(V - dp[V])\n', 'python',
 '动态规划,背包', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '24\n6\n8\n3\n12\n7\n9\n7', '0\n', 1, 1),
(@aid, '39\n8\n20\n20\n17\n11\n7\n39\n9\n30', '0\n', 0, 2),
(@aid, '36\n5\n36\n21\n2\n23\n26', '0\n', 0, 3),
(@aid, '37\n8\n36\n17\n36\n24\n35\n34\n30\n28', '1\n', 0, 4),
(@aid, '46\n6\n42\n18\n32\n18\n45\n11', '1\n', 0, 5),
(@aid, '38\n10\n21\n5\n38\n9\n35\n10\n24\n15\n25\n33', '0\n', 0, 6);

-- ---------- 146. 打家劫舍（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('打家劫舍', 3, 20, '## 【题目描述】\n\n沿街有一排房屋，每个房屋里有一定金额的现金。小偷不能连续偷相邻的两间房屋，求一夜之间能偷到的最大金额。\n\n## 【输入格式】\n\n第一行一个整数 n；第二行 n 个非负整数。\n\n## 【输出格式】\n\n一行，一个整数。\n\n## 【样例】\n\n输入：\n\n```\n4\n1 2 3 1\n```\n\n输出：\n\n```\n4\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁵\n\n## 【提示】\n\n到第 i 间为止只有"偷 / 不偷"两种状态，转移为 cur = max(cur, prev + a[i])，用两个变量滚动即可。', '第一行一个整数 n；第二行 n 个非负整数。', '一行，一个整数。',
 '4\n1 2 3 1', '4', '到第 i 间为止只有"偷 / 不偷"两种状态，转移为 cur = max(cur, prev + a[i])，用两个变量滚动即可。', 'import sys\n\ndata = list(map(int, sys.stdin.read().split()))\nn = data[0]\na = data[1:1 + n]\nprev, cur = 0, 0\nfor x in a:\n    prev, cur = cur, max(cur, prev + x)\nprint(cur)\n', 'python',
 '动态规划,线性DP', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '4\n1 2 3 1', '4\n', 1, 1),
(@aid, '11\n90 76 76 34 43 9 69 46 63 80 5', '358\n', 0, 2),
(@aid, '14\n23 99 73 73 68 81 3 28 38 50 74 13 81 21', '446\n', 0, 3),
(@aid, '2\n45 47', '47\n', 0, 4),
(@aid, '15\n87 47 88 71 0 21 35 25 15 80 82 28 87 9 81', '475\n', 0, 5),
(@aid, '19\n51 49 3 15 41 65 48 48 37 96 53 87 100 72 2 59 38 93 35', '586\n', 0, 6);

-- ---------- 147. 三角形最小路径和（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('三角形最小路径和', 3, 20, '## 【题目描述】\n\n给定一个 n 行的数字三角形，从顶部出发，每次只能走到下一行相邻的数（正下方或右下方），求到达底部时经过数字之和的最小值。\n\n## 【输入格式】\n\n第一行一个整数 n；接下来 n 行，第 i 行有 i 个整数。\n\n## 【输出格式】\n\n一行，一个整数。\n\n## 【样例】\n\n输入：\n\n```\n4\n2\n3 4\n6 5 7\n4 1 8 3\n```\n\n输出：\n\n```\n11\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 100，每个数 ∈ [0, 100]\n\n## 【提示】\n\n与"数字三角形"完全同构，只是把 max 换成 min，自底向上原地递推即可。', '第一行一个整数 n；接下来 n 行，第 i 行有 i 个整数。', '一行，一个整数。',
 '4\n2\n3 4\n6 5 7\n4 1 8 3', '11', '与"数字三角形"完全同构，只是把 max 换成 min，自底向上原地递推即可。', 'import sys\n\ndata = list(map(int, sys.stdin.read().split()))\nn = data[0]\nvals = data[1:]\ntri = []\npos = 0\nfor i in range(1, n + 1):\n    tri.append(vals[pos:pos + i])\n    pos += i\nfor i in range(n - 2, -1, -1):\n    for j in range(len(tri[i])):\n        tri[i][j] += min(tri[i + 1][j], tri[i + 1][j + 1])\nprint(tri[0][0])\n', 'python',
 '动态规划,线性DP', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '4\n2\n3 4\n6 5 7\n4 1 8 3', '11\n', 1, 1),
(@aid, '6\n5\n9 19\n4 20 12\n11 15 1 16\n6 2 14 13 9\n10 5 14 18 16 0', '36\n', 0, 2),
(@aid, '5\n4\n6 13\n13 18 13\n16 20 16 8\n7 4 4 14 14', '43\n', 0, 3),
(@aid, '5\n2\n17 9\n10 20 5\n13 15 15 20\n11 4 6 17 11', '37\n', 0, 4),
(@aid, '8\n0\n4 10\n4 5 5\n11 13 11 6\n6 10 9 8 14\n14 1 14 19 6 18\n17 9 3 14 11 15 11\n15 3 19 6 12 12 1 4', '35\n', 0, 5),
(@aid, '3\n3\n0 3\n17 20 1', '7\n', 0, 6);

-- ---------- 148. 买卖股票的最佳时机（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('买卖股票的最佳时机', 2, 10, '## 【题目描述】\n\n给定一支股票连续 n 天的价格，你只能选择在某一天买入，并在之后的某一天卖出（只允许一次交易），求最大利润；若无论如何都亏本，输出 0。\n\n## 【输入格式】\n\n第一行一个整数 n；第二行 n 个整数。\n\n## 【输出格式】\n\n一行，一个整数。\n\n## 【样例】\n\n输入：\n\n```\n6\n7 1 5 3 6 4\n```\n\n输出：\n\n```\n5\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁵\n\n## 【提示】\n\n从左到右扫描，维护此前见过的最低买入价 low，用当天价格减 low 更新最大利润；一次遍历即可。', '第一行一个整数 n；第二行 n 个整数。', '一行，一个整数。',
 '6\n7 1 5 3 6 4', '5', '从左到右扫描，维护此前见过的最低买入价 low，用当天价格减 low 更新最大利润；一次遍历即可。', 'import sys\n\ndata = list(map(int, sys.stdin.read().split()))\nn = data[0]\na = data[1:1 + n]\nif n < 2:\n    print(0)\nelse:\n    low = a[0]\n    ans = 0\n    for x in a[1:]:\n        if x - low > ans:\n            ans = x - low\n        if x < low:\n            low = x\n    print(ans)\n', 'python',
 '动态规划,贪心', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '6\n7 1 5 3 6 4', '5\n', 1, 1),
(@aid, '13\n32 43 82 25 6 16 25 100 69 35 19 91 25', '94\n', 0, 2),
(@aid, '2\n36 76', '40\n', 0, 3),
(@aid, '9\n100 57 72 38 34 8 69 2 77', '75\n', 0, 4),
(@aid, '5\n82 92 81 7 21', '14\n', 0, 5),
(@aid, '8\n60 45 28 53 30 64 57 78', '50\n', 0, 6);

-- ---------- 149. 带障碍的不同路径（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('带障碍的不同路径', 3, 20, '## 【题目描述】\n\n一个 m 行 n 列的网格，其中 1 表示障碍、0 表示可通行。机器人从左上角走到右下角，每次只能向右或向下，求不同路径的条数。\n\n## 【输入格式】\n\n第一行两个整数 m、n；接下来 m 行，每行 n 个 0 或 1。\n\n## 【输出格式】\n\n一行，一个整数，表示路径条数。\n\n## 【样例】\n\n输入：\n\n```\n3 3\n0 0 0\n0 1 0\n0 0 0\n```\n\n输出：\n\n```\n2\n```\n\n## 【数据范围】\n\n1 ≤ m, n ≤ 100\n\n## 【提示】\n\n在"不同路径数"基础上增加障碍判断：遇到障碍格子时 dp 值置 0，起点若可通行则为 1。', '第一行两个整数 m、n；接下来 m 行，每行 n 个 0 或 1。', '一行，一个整数，表示路径条数。',
 '3 3\n0 0 0\n0 1 0\n0 0 0', '2', '在"不同路径数"基础上增加障碍判断：遇到障碍格子时 dp 值置 0，起点若可通行则为 1。', 'import sys\n\ndata = list(map(int, sys.stdin.read().split()))\nm, n = data[0], data[1]\ngrid = [data[2 + i * n:2 + (i + 1) * n] for i in range(m)]\ndp = [0] * n\nfor i in range(m):\n    for j in range(n):\n        if grid[i][j] == 1:\n            dp[j] = 0\n        elif i == 0 and j == 0:\n            dp[j] = 1\n        elif j:\n            dp[j] += dp[j - 1]\nprint(dp[n - 1])\n', 'python',
 '动态规划,网格DP', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3 3\n0 0 0\n0 1 0\n0 0 0', '2\n', 1, 1),
(@aid, '4 3\n0 1 0\n0 0 0\n0 0 0\n0 0 1', '0\n', 0, 2),
(@aid, '6 7\n0 0 1 0 1 0 1\n0 0 0 0 0 1 1\n0 0 1 1 0 0 0\n1 0 0 0 0 0 0\n0 0 1 1 0 0 0\n0 0 0 0 0 0 0', '41\n', 0, 3),
(@aid, '7 3\n0 0 1\n0 1 0\n0 1 1\n1 0 1\n0 0 0\n0 0 0\n0 0 0', '0\n', 0, 4),
(@aid, '3 5\n0 0 0 0 0\n0 0 1 1 0\n0 0 0 0 0', '4\n', 0, 5),
(@aid, '4 3\n0 1 0\n1 0 1\n0 0 0\n0 0 1', '0\n', 0, 6);

-- ---------- 150. 最长回文子串（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('最长回文子串', 3, 20, '## 【题目描述】\n\n给定一个字符串 s，求它的最长回文子串的长度。\n\n## 【输入格式】\n\n一行，一个字符串 s。\n\n## 【输出格式】\n\n一行，一个整数。\n\n## 【样例】\n\n输入：\n\n```\nbabad\n```\n\n输出：\n\n```\n3\n```\n\n## 【数据范围】\n\n1 ≤ |s| ≤ 1000\n\n## 【提示】\n\n中心扩展法：枚举每个中心（奇长度以字符为中心、偶长度以空隙为中心），向两侧扩展直到失配，O(n²) 时间 O(1) 空间。', '一行，一个字符串 s。', '一行，一个整数。',
 'babad', '3', '中心扩展法：枚举每个中心（奇长度以字符为中心、偶长度以空隙为中心），向两侧扩展直到失配，O(n²) 时间 O(1) 空间。', 'import sys\n\ns = sys.stdin.readline().strip()\nn = len(s)\nans = 0\nfor c in range(n):\n    k = 0\n    while c - k >= 0 and c + k < n and s[c - k] == s[c + k]:\n        k += 1\n    ans = max(ans, 2 * k - 1)\n    k = 0\n    while c - k >= 0 and c + 1 + k < n and s[c - k] == s[c + 1 + k]:\n        k += 1\n    ans = max(ans, 2 * k)\nprint(ans)\n', 'python',
 '动态规划,字符串,中心扩展', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'babad', '3\n', 1, 1),
(@aid, 'dabaadadaa', '7\n', 0, 2),
(@aid, 'cdccdc', '6\n', 0, 3),
(@aid, 'ccbbcbdcbacacbadbdbacbbbba', '4\n', 0, 4),
(@aid, 'aabddbbdcabb', '4\n', 0, 5),
(@aid, 'dbcaacdddbcbbdcab', '4\n', 0, 6);

-- ---------- 151. 编辑距离（Levenshtein）（难度 4） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('编辑距离（Levenshtein）', 4, 30, '## 【题目描述】\n\n给定两个字符串 s 和 t，允许三种操作：插入一个字符、删除一个字符、替换一个字符（每次代价均为 1）。求把 s 变成 t 的最少操作次数。\n\n## 【输入格式】\n\n两行，每行一个字符串。\n\n## 【输出格式】\n\n一行，一个整数。\n\n## 【样例】\n\n输入：\n\n```\nhorse\nros\n```\n\n输出：\n\n```\n3\n```\n\n## 【数据范围】\n\n1 ≤ |s|, |t| ≤ 500\n\n## 【提示】\n\ndp[i][j] 表示 s 前 i 个字符变成 t 前 j 个字符的最少步数；字符相等时直接继承 dp[i-1][j-1]，否则在插入、删除、替换三者中取最小再加一。', '两行，每行一个字符串。', '一行，一个整数。',
 'horse\nros', '3', 'dp[i][j] 表示 s 前 i 个字符变成 t 前 j 个字符的最少步数；字符相等时直接继承 dp[i-1][j-1]，否则在插入、删除、替换三者中取最小再加一。', 'import sys\n\ndata = sys.stdin.read().split(\'\\n\')\ns = data[0].strip()\nt = data[1].strip()\nn, m = len(s), len(t)\ndp = list(range(m + 1))\nfor i in range(1, n + 1):\n    prev = dp[0]\n    dp[0] = i\n    for j in range(1, m + 1):\n        tmp = dp[j]\n        if s[i - 1] == t[j - 1]:\n            dp[j] = prev\n        else:\n            dp[j] = 1 + min(prev, dp[j], dp[j - 1])\n        prev = tmp\nprint(dp[m])\n', 'python',
 '动态规划,编辑距离,字符串', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, 'horse\nros', '3\n', 1, 1),
(@aid, 'bbadeae\ncb', '6\n', 0, 2),
(@aid, 'dce\nee', '2\n', 0, 3),
(@aid, 'eebadde\nccab', '6\n', 0, 4),
(@aid, 'cceced\ndbdddd', '5\n', 0, 5),
(@aid, 'decdeeaed\necac', '6\n', 0, 6);

-- ---------- 152. 石子合并（直线）（难度 4） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('石子合并（直线）', 4, 30, '## 【题目描述】\n\nn 堆石子排成一排，每堆有 aᵢ 个石子。每次只能把相邻的两堆合并成一堆，合并的代价为这两堆石子总数。求把所有石子合并成一堆的最小总代价。\n\n## 【输入格式】\n\n第一行一个整数 n；第二行 n 个整数。\n\n## 【输出格式】\n\n一行，一个整数。\n\n## 【样例】\n\n输入：\n\n```\n4\n4 5 9 4\n```\n\n输出：\n\n```\n44\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 100\n\n## 【提示】\n\n区间 DP 模板：先枚举区间长度，再枚举左端点，最后枚举最后一次合并的分割点 k，代价为该区间石子总数（用前缀和 O(1) 求出）。', '第一行一个整数 n；第二行 n 个整数。', '一行，一个整数。',
 '4\n4 5 9 4', '44', '区间 DP 模板：先枚举区间长度，再枚举左端点，最后枚举最后一次合并的分割点 k，代价为该区间石子总数（用前缀和 O(1) 求出）。', 'import sys\n\ndata = list(map(int, sys.stdin.read().split()))\nn = data[0]\na = data[1:1 + n]\npre = [0] * (n + 1)\nfor i in range(n):\n    pre[i + 1] = pre[i] + a[i]\nINF = 10 ** 18\ndp = [[0] * n for _ in range(n)]\nfor length in range(2, n + 1):\n    for i in range(n - length + 1):\n        j = i + length - 1\n        best = INF\n        for k in range(i, j):\n            v = dp[i][k] + dp[k + 1][j] + pre[j + 1] - pre[i]\n            if v < best:\n                best = v\n        dp[i][j] = best\nprint(dp[0][n - 1])\n', 'python',
 '动态规划,区间DP', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '4\n4 5 9 4', '44\n', 1, 1),
(@aid, '5\n37 10 11 13 34', '228\n', 0, 2),
(@aid, '2\n32 5', '37\n', 0, 3),
(@aid, '12\n6 31 5 36 25 39 12 26 11 4 14 18', '799\n', 0, 4),
(@aid, '2\n42 8', '50\n', 0, 5),
(@aid, '12\n1 10 23 1 14 7 30 14 26 26 1 15', '568\n', 0, 6);

-- ---------- 153. 第 n 个丑数（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('第 n 个丑数', 3, 20, '## 【题目描述】\n\n只包含质因子 2、3、5 的正整数称为丑数，1 是第一个丑数。求第 n 个丑数。\n\n## 【输入格式】\n\n一行，一个整数 n。\n\n## 【输出格式】\n\n一行，一个整数。\n\n## 【样例】\n\n输入：\n\n```\n10\n```\n\n输出：\n\n```\n12\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 2000\n\n## 【提示】\n\n三指针法：每个丑数都由某个已有的丑数乘 2/3/5 得到，用三个指针分别记录下一次乘法的候选位置，每次取最小值并推进对应指针（相等时都要推进以去重）。', '一行，一个整数 n。', '一行，一个整数。',
 '10', '12', '三指针法：每个丑数都由某个已有的丑数乘 2/3/5 得到，用三个指针分别记录下一次乘法的候选位置，每次取最小值并推进对应指针（相等时都要推进以去重）。', 'import sys\n\nn = int(sys.stdin.read().strip())\nugly = [1]\ni2 = i3 = i5 = 0\nfor _ in range(1, n):\n    a, b, c = ugly[i2] * 2, ugly[i3] * 3, ugly[i5] * 5\n    nxt = min(a, b, c)\n    ugly.append(nxt)\n    if nxt == a:\n        i2 += 1\n    if nxt == b:\n        i3 += 1\n    if nxt == c:\n        i5 += 1\nprint(ugly[n - 1])\n', 'python',
 '动态规划,多指针,数学', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '10', '12\n', 1, 1),
(@aid, '9', '10\n', 0, 2),
(@aid, '121', '2880\n', 0, 3),
(@aid, '280', '62208\n', 0, 4),
(@aid, '25', '54\n', 0, 5),
(@aid, '97', '1440\n', 0, 6);

-- ---------- 154. 最大子矩阵和（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('最大子矩阵和', 3, 20, '## 【题目描述】\n\n给定一个 n 行 m 列的整数矩阵，求它的一个非空子矩阵（连续的行与列围成的矩形），使得子矩阵内所有元素之和最大。\n\n## 【输入格式】\n\n第一行两个整数 n、m；接下来 n 行，每行 m 个整数。\n\n## 【输出格式】\n\n一行，一个整数，表示最大子矩阵和。\n\n## 【样例】\n\n输入：\n\n```\n2 3\n1 2 3\n-4 5 6\n```\n\n输出：\n\n```\n16\n```\n\n## 【数据范围】\n\n1 ≤ n, m ≤ 100，元素 ∈ [-100, 100]\n\n## 【提示】\n\n枚举上下边界，把两行之间的元素按列压缩成一维数组，问题就转化为一维最大子段和，整体 O(n²m)。', '第一行两个整数 n、m；接下来 n 行，每行 m 个整数。', '一行，一个整数，表示最大子矩阵和。',
 '2 3\n1 2 3\n-4 5 6', '16', '枚举上下边界，把两行之间的元素按列压缩成一维数组，问题就转化为一维最大子段和，整体 O(n²m)。', 'import sys\n\ndata = list(map(int, sys.stdin.read().split()))\nn, m = data[0], data[1]\na = [data[2 + i * m:2 + (i + 1) * m] for i in range(n)]\nans = -(10 ** 18)\nfor top in range(n):\n    col = [0] * m\n    for bottom in range(top, n):\n        for j in range(m):\n            col[j] += a[bottom][j]\n        cur = col[0]\n        best = col[0]\n        for x in col[1:]:\n            cur = max(x, cur + x)\n            best = max(best, cur)\n        ans = max(ans, best)\nprint(ans)\n', 'python',
 '动态规划,降维,最大子段和', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '2 3\n1 2 3\n-4 5 6', '16\n', 1, 1),
(@aid, '2 6\n9 -7 10 20 -6 -5\n-5 -8 16 4 -5 -4', '50\n', 0, 2),
(@aid, '6 8\n3 5 8 9 2 0 -1 4\n8 -6 -9 -1 11 -9 4 4\n-6 6 1 1 -5 7 9 -8\n-3 2 -6 8 -1 18 12 -9\n19 4 20 -7 -3 3 -2 3\n-9 -1 -9 -8 17 -9 3 -6', '101\n', 0, 3),
(@aid, '8 6\n8 9 14 -6 -3 -1\n14 -7 20 19 0 -3\n20 15 9 16 13 13\n0 19 -4 -6 10 -5\n14 7 -5 15 11 19\n5 8 20 14 5 10\n18 14 17 -9 -5 -4\n-1 17 5 7 20 8', '374\n', 0, 4),
(@aid, '3 7\n-8 -9 18 -5 11 -5 -7\n4 9 17 20 -4 13 10\n-7 7 -5 14 -9 -4 16', '87\n', 0, 5),
(@aid, '7 5\n15 2 7 17 -8\n7 15 13 6 1\n-6 -9 4 8 17\n15 16 16 6 -2\n4 6 1 12 7\n20 13 -4 14 16\n10 -1 20 16 7', '281\n', 0, 6);

-- ---------- 155. 亲戚（并查集）（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('亲戚（并查集）', 2, 10, '## 【题目描述】\n\n有 n 个人，给出 m 组亲戚关系（关系具有传递性）。接下来有 q 次询问，每次询问两个人是否为亲戚。\n\n## 【输入格式】\n\n第一行三个整数 n、m、q；接下来 m 行，每行两个整数 a、b，表示 a 与 b 是亲戚；接下来 q 行，每行两个整数 x、y，表示一次询问。\n\n## 【输出格式】\n\n每次询问输出一行，是亲戚输出 Yes，否则输出 No。\n\n## 【样例】\n\n输入：\n\n```\n5 3 2\n1 2\n2 3\n4 5\n1 3\n2 4\n```\n\n输出：\n\n```\nYes\nNo\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁴，1 ≤ m, q ≤ 10⁴\n\n## 【提示】\n\n并查集模板：find 用路径压缩、union 时把一棵树的根挂到另一棵树根下；两个人在同一集合即为亲戚。', '第一行三个整数 n、m、q；接下来 m 行，每行两个整数 a、b，表示 a 与 b 是亲戚；接下来 q 行，每行两个整数 x、y，表示一次询问。', '每次询问输出一行，是亲戚输出 Yes，否则输出 No。',
 '5 3 2\n1 2\n2 3\n4 5\n1 3\n2 4', 'Yes\nNo', '并查集模板：find 用路径压缩、union 时把一棵树的根挂到另一棵树根下；两个人在同一集合即为亲戚。', 'import sys\n\ndata = list(map(int, sys.stdin.read().split()))\nn, m, q = data[0], data[1], data[2]\nfa = list(range(n + 1))\n\n\ndef find(x):\n    while fa[x] != x:\n        fa[x] = fa[fa[x]]\n        x = fa[x]\n    return x\n\n\np = 3\nfor _ in range(m):\n    a, b = data[p], data[p + 1]\n    p += 2\n    ra, rb = find(a), find(b)\n    if ra != rb:\n        fa[ra] = rb\nout = []\nfor _ in range(q):\n    x, y = data[p], data[p + 1]\n    p += 2\n    out.append(\'Yes\' if find(x) == find(y) else \'No\')\nprint(\'\\n\'.join(out))\n', 'python',
 '并查集,图论', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '5 3 2\n1 2\n2 3\n4 5\n1 3\n2 4', 'Yes\nNo\n', 1, 1),
(@aid, '7 7 1\n4 1\n1 2\n4 2\n7 5\n7 7\n5 7\n3 4\n3 6', 'No\n', 0, 2),
(@aid, '3 3 2\n1 2\n1 3\n1 1\n2 3\n2 3', 'Yes\nYes\n', 0, 3),
(@aid, '12 6 5\n12 6\n3 10\n6 8\n9 10\n3 6\n12 9\n6 1\n4 5\n9 10\n7 5\n7 10', 'No\nNo\nYes\nNo\nNo\n', 0, 4),
(@aid, '10 7 4\n8 4\n1 9\n10 10\n3 3\n5 8\n1 10\n2 4\n2 8\n9 5\n8 2\n3 3', 'Yes\nNo\nYes\nYes\n', 0, 5),
(@aid, '12 1 4\n1 1\n3 10\n2 5\n4 8\n4 8', 'No\nNo\nNo\nNo\n', 0, 6);

-- ---------- 156. 连通块计数（并查集）（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('连通块计数（并查集）', 2, 10, '## 【题目描述】\n\n给定一张 n 个点、m 条边的无向图，求其中连通块的个数。\n\n## 【输入格式】\n\n第一行两个整数 n、m；接下来 m 行，每行两个整数 u、v，表示一条无向边。\n\n## 【输出格式】\n\n一行，一个整数，表示连通块个数。\n\n## 【样例】\n\n输入：\n\n```\n5 2\n1 2\n3 4\n```\n\n输出：\n\n```\n3\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁴，0 ≤ m ≤ 10⁵\n\n## 【提示】\n\n初始连通块数为 n，每合并两个不同集合就减一；也可用 DFS/BFS  flood fill 计数。', '第一行两个整数 n、m；接下来 m 行，每行两个整数 u、v，表示一条无向边。', '一行，一个整数，表示连通块个数。',
 '5 2\n1 2\n3 4', '3', '初始连通块数为 n，每合并两个不同集合就减一；也可用 DFS/BFS  flood fill 计数。', 'import sys\n\ndata = list(map(int, sys.stdin.read().split()))\nn, m = data[0], data[1]\nfa = list(range(n + 1))\n\n\ndef find(x):\n    while fa[x] != x:\n        fa[x] = fa[fa[x]]\n        x = fa[x]\n    return x\n\n\ncnt = n\np = 2\nfor _ in range(m):\n    u, v = data[p], data[p + 1]\n    p += 2\n    ru, rv = find(u), find(v)\n    if ru != rv:\n        fa[ru] = rv\n        cnt -= 1\nprint(cnt)\n', 'python',
 '并查集,图论,连通性', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '5 2\n1 2\n3 4', '3\n', 1, 1),
(@aid, '2 1\n1 2', '1\n', 0, 2),
(@aid, '5 4\n1 2\n1 3\n3 4\n2 5', '1\n', 0, 3),
(@aid, '8 7\n1 2\n1 3\n2 4\n3 5\n4 6\n1 7\n6 8', '1\n', 0, 4),
(@aid, '3 2\n1 2\n2 3', '1\n', 0, 5),
(@aid, '6 5\n1 2\n2 3\n1 4\n3 5\n3 6', '1\n', 0, 6);

-- ---------- 157. 最小生成树（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('最小生成树', 3, 20, '## 【题目描述】\n\n给定一个 n 个点、m 条边的带权无向连通图，求其最小生成树的边权之和。\n\n## 【输入格式】\n\n第一行两个整数 n、m；接下来 m 行，每行三个整数 u、v、w，表示一条权值为 w 的无向边。\n\n## 【输出格式】\n\n一行，一个整数，表示最小生成树的权值和。\n\n## 【样例】\n\n输入：\n\n```\n4 5\n1 2 2\n1 3 3\n2 3 1\n2 4 4\n3 4 5\n```\n\n输出：\n\n```\n7\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁴，1 ≤ m ≤ 10⁵\n\n## 【提示】\n\nKruskal 算法：把边按权值升序排序，用并查集依次选取两端不在同一集合的边，选满 n-1 条即得到最小生成树。', '第一行两个整数 n、m；接下来 m 行，每行三个整数 u、v、w，表示一条权值为 w 的无向边。', '一行，一个整数，表示最小生成树的权值和。',
 '4 5\n1 2 2\n1 3 3\n2 3 1\n2 4 4\n3 4 5', '7', 'Kruskal 算法：把边按权值升序排序，用并查集依次选取两端不在同一集合的边，选满 n-1 条即得到最小生成树。', 'import sys\n\ndata = list(map(int, sys.stdin.read().split()))\nn, m = data[0], data[1]\nedges = [(data[2 + 3 * i], data[3 + 3 * i], data[4 + 3 * i]) for i in range(m)]\nedges.sort(key=lambda e: e[2])\nfa = list(range(n + 1))\n\n\ndef find(x):\n    while fa[x] != x:\n        fa[x] = fa[fa[x]]\n        x = fa[x]\n    return x\n\n\nans = 0\ncnt = 0\nfor u, v, w in edges:\n    ru, rv = find(u), find(v)\n    if ru != rv:\n        fa[ru] = rv\n        ans += w\n        cnt += 1\n        if cnt == n - 1:\n            break\nprint(ans)\n', 'python',
 '图论,最小生成树,并查集', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '4 5\n1 2 2\n1 3 3\n2 3 1\n2 4 4\n3 4 5', '7\n', 1, 1),
(@aid, '8 8\n1 2 11\n1 3 91\n1 4 46\n2 5 89\n1 6 58\n3 7 85\n6 8 71\n8 7 92', '451\n', 0, 2),
(@aid, '4 5\n1 2 96\n1 3 90\n2 4 56\n3 2 83\n2 3 49', '195\n', 0, 3),
(@aid, '5 8\n1 2 55\n1 3 93\n3 4 90\n3 5 43\n1 4 40\n5 2 78\n3 2 85\n2 3 77', '215\n', 0, 4),
(@aid, '3 3\n1 2 24\n2 3 32\n3 1 46', '56\n', 0, 5),
(@aid, '3 3\n1 2 71\n1 3 30\n2 3 56', '86\n', 0, 6);

-- ---------- 158. 单源最短路（Dijkstra）（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('单源最短路（Dijkstra）', 3, 20, '## 【题目描述】\n\n给定一个 n 个点、m 条边的正权无向图，求 1 号点到 n 号点的最短距离；若不可达，输出 -1。\n\n## 【输入格式】\n\n第一行两个整数 n、m；接下来 m 行，每行三个整数 u、v、w，表示一条权值为 w 的无向边。\n\n## 【输出格式】\n\n一行，一个整数。\n\n## 【样例】\n\n输入：\n\n```\n4 4\n1 2 1\n2 4 5\n1 3 4\n3 4 2\n```\n\n输出：\n\n```\n6\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁴，1 ≤ m ≤ 10⁵，1 ≤ w ≤ 10⁴\n\n## 【提示】\n\nDijkstra + 优先队列：每次取出当前距离最小的点并松弛它的出边；边权必须非负，用堆可以把复杂度降到 O(m log n)。', '第一行两个整数 n、m；接下来 m 行，每行三个整数 u、v、w，表示一条权值为 w 的无向边。', '一行，一个整数。',
 '4 4\n1 2 1\n2 4 5\n1 3 4\n3 4 2', '6', 'Dijkstra + 优先队列：每次取出当前距离最小的点并松弛它的出边；边权必须非负，用堆可以把复杂度降到 O(m log n)。', 'import sys\nimport heapq\n\ndata = list(map(int, sys.stdin.read().split()))\nn, m = data[0], data[1]\nadj = [[] for _ in range(n + 1)]\np = 2\nfor _ in range(m):\n    u, v, w = data[p], data[p + 1], data[p + 2]\n    p += 3\n    adj[u].append((v, w))\n    adj[v].append((u, w))\nINF = 10 ** 18\ndist = [INF] * (n + 1)\ndist[1] = 0\npq = [(0, 1)]\nwhile pq:\n    d, x = heapq.heappop(pq)\n    if d > dist[x]:\n        continue\n    for y, w in adj[x]:\n        if dist[x] + w < dist[y]:\n            dist[y] = dist[x] + w\n            heapq.heappush(pq, (dist[y], y))\nprint(-1 if dist[n] >= INF else dist[n])\n', 'python',
 '图论,最短路,Dijkstra', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '4 4\n1 2 1\n2 4 5\n1 3 4\n3 4 2', '6\n', 1, 1),
(@aid, '6 7\n1 2 70\n2 3 10\n1 4 83\n4 5 57\n2 6 7\n6 5 78\n3 1 4', '21\n', 0, 2),
(@aid, '2 1\n1 2 13', '13\n', 0, 3),
(@aid, '4 6\n1 2 29\n1 3 15\n2 4 43\n3 4 59\n3 2 49\n4 3 54', '69\n', 0, 4),
(@aid, '5 4\n1 2 48\n1 3 62\n1 4 27\n2 5 90', '138\n', 0, 5),
(@aid, '4 4\n1 2 23\n2 3 23\n3 4 70\n3 1 7', '77\n', 0, 6);

-- ---------- 159. 多源最短路（Floyd）（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('多源最短路（Floyd）', 3, 20, '## 【题目描述】\n\n给定一个 n 个点、m 条边的正权无向图和 q 次询问，每次询问两个点 u、v，求它们之间的最短距离；若不可达输出 -1。\n\n## 【输入格式】\n\n第一行三个整数 n、m、q；接下来 m 行，每行三个整数 u、v、w；接下来 q 行，每行两个整数 u、v。\n\n## 【输出格式】\n\n每次询问输出一行，一个整数。\n\n## 【样例】\n\n输入：\n\n```\n4 4 2\n1 2 1\n2 3 2\n3 4 3\n1 4 10\n1 4\n2 4\n```\n\n输出：\n\n```\n6\n5\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 200，1 ≤ m ≤ 10⁴，1 ≤ q ≤ 10⁴\n\n## 【提示】\n\nFloyd 本质是动态规划：三重循环枚举中转点 k，d[i][j] = min(d[i][j], d[i][k] + d[k][j])；k 必须写在最外层。', '第一行三个整数 n、m、q；接下来 m 行，每行三个整数 u、v、w；接下来 q 行，每行两个整数 u、v。', '每次询问输出一行，一个整数。',
 '4 4 2\n1 2 1\n2 3 2\n3 4 3\n1 4 10\n1 4\n2 4', '6\n5', 'Floyd 本质是动态规划：三重循环枚举中转点 k，d[i][j] = min(d[i][j], d[i][k] + d[k][j])；k 必须写在最外层。', 'import sys\n\nINF = 10 ** 15\ndata = list(map(int, sys.stdin.read().split()))\nn, m, q = data[0], data[1], data[2]\nd = [[INF] * (n + 1) for _ in range(n + 1)]\nfor i in range(1, n + 1):\n    d[i][i] = 0\np = 3\nfor _ in range(m):\n    u, v, w = data[p], data[p + 1], data[p + 2]\n    p += 3\n    if w < d[u][v]:\n        d[u][v] = d[v][u] = w\nfor k in range(1, n + 1):\n    for i in range(1, n + 1):\n        dik = d[i][k]\n        if dik >= INF:\n            continue\n        row = d[i]\n        dk = d[k]\n        for j in range(1, n + 1):\n            v = dik + dk[j]\n            if v < row[j]:\n                row[j] = v\nout = []\nfor _ in range(q):\n    u, v = data[p], data[p + 1]\n    p += 2\n    out.append(str(-1 if d[u][v] >= INF else d[u][v]))\nprint(\'\\n\'.join(out))\n', 'python',
 '图论,最短路,Floyd', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '4 4 2\n1 2 1\n2 3 2\n3 4 3\n1 4 10\n1 4\n2 4', '6\n5\n', 1, 1),
(@aid, '3 3 1\n1 2 59\n1 3 50\n2 3 60\n3 2', '60\n', 0, 2),
(@aid, '8 8 2\n1 2 18\n2 3 52\n3 4 32\n1 5 24\n4 6 89\n6 7 90\n3 8 69\n1 3 100\n7 7\n7 4', '0\n179\n', 0, 3),
(@aid, '7 9 3\n1 2 83\n2 3 27\n1 4 33\n4 5 100\n5 6 79\n6 7 23\n1 5 37\n3 7 15\n3 4 20\n1 2\n4 6\n5 1', '80\n58\n37\n', 0, 4),
(@aid, '9 10 3\n1 2 42\n1 3 81\n2 4 54\n1 5 36\n2 6 10\n6 7 36\n7 8 47\n1 9 69\n1 6 81\n7 3 34\n2 6\n8 5\n5 2', '10\n171\n78\n', 0, 5),
(@aid, '2 1 2\n1 2 7\n1 1\n1 2', '0\n7\n', 0, 6);

-- ---------- 160. 拓扑排序（字典序最小）（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('拓扑排序（字典序最小）', 3, 20, '## 【题目描述】\n\n给定一个 n 个点、m 条边的有向图，输出它的字典序最小的拓扑序列；若图中存在环，输出 -1。\n\n## 【输入格式】\n\n第一行两个整数 n、m；接下来 m 行，每行两个整数 u、v，表示一条 u → v 的有向边。\n\n## 【输出格式】\n\n一行，若可拓扑排序则输出 n 个整数（用空格分隔），否则输出 -1。\n\n## 【样例】\n\n输入：\n\n```\n4 3\n1 2\n2 3\n1 4\n```\n\n输出：\n\n```\n1 2 3 4\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁴，0 ≤ m ≤ 10⁵\n\n## 【提示】\n\n不断取出入度为 0 的点，删除它的出边；要得到字典序最小的序列，用**小根堆**代替普通队列即可。', '第一行两个整数 n、m；接下来 m 行，每行两个整数 u、v，表示一条 u → v 的有向边。', '一行，若可拓扑排序则输出 n 个整数（用空格分隔），否则输出 -1。',
 '4 3\n1 2\n2 3\n1 4', '1 2 3 4', '不断取出入度为 0 的点，删除它的出边；要得到字典序最小的序列，用**小根堆**代替普通队列即可。', 'import sys\nimport heapq\n\ndata = list(map(int, sys.stdin.read().split()))\nn, m = data[0], data[1]\nindeg = [0] * (n + 1)\nadj = [[] for _ in range(n + 1)]\np = 2\nfor _ in range(m):\n    u, v = data[p], data[p + 1]\n    p += 2\n    adj[u].append(v)\n    indeg[v] += 1\nheap = [i for i in range(1, n + 1) if indeg[i] == 0]\nheapq.heapify(heap)\nres = []\nwhile heap:\n    x = heapq.heappop(heap)\n    res.append(x)\n    for y in adj[x]:\n        indeg[y] -= 1\n        if indeg[y] == 0:\n            heapq.heappush(heap, y)\nprint(\' \'.join(map(str, res)) if len(res) == n else \'-1\')\n', 'python',
 '图论,拓扑排序,DAG', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '4 3\n1 2\n2 3\n1 4', '1 2 3 4\n', 1, 1),
(@aid, '2 0\n', '1 2\n', 0, 2),
(@aid, '4 1\n1 2', '1 2 3 4\n', 0, 3),
(@aid, '5 4\n1 2\n1 3\n2 3\n2 5', '1 2 3 4 5\n', 0, 4),
(@aid, '4 3\n2 3\n2 4\n3 4', '1 2 3 4\n', 0, 5),
(@aid, '2 1\n1 2', '1 2\n', 0, 6);

-- ---------- 161. 有向图判环（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('有向图判环', 3, 20, '## 【题目描述】\n\n给定一个 n 个点、m 条边的有向图，判断其中是否存在环。\n\n## 【输入格式】\n\n第一行两个整数 n、m；接下来 m 行，每行两个整数 u、v，表示一条 u → v 的有向边。\n\n## 【输出格式】\n\n一行，有环输出 Yes，否则输出 No。\n\n## 【样例】\n\n输入：\n\n```\n3 3\n1 2\n2 3\n3 1\n```\n\n输出：\n\n```\nYes\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁴，0 ≤ m ≤ 10⁵\n\n## 【提示】\n\n拓扑排序判环：若能被全部弹出（cnt == n）说明无环；剩余点数大于 0 则一定存在环。也可用 DFS 三色标记法。', '第一行两个整数 n、m；接下来 m 行，每行两个整数 u、v，表示一条 u → v 的有向边。', '一行，有环输出 Yes，否则输出 No。',
 '3 3\n1 2\n2 3\n3 1', 'Yes', '拓扑排序判环：若能被全部弹出（cnt == n）说明无环；剩余点数大于 0 则一定存在环。也可用 DFS 三色标记法。', 'import sys\n\ndata = list(map(int, sys.stdin.read().split()))\nn, m = data[0], data[1]\nindeg = [0] * (n + 1)\nadj = [[] for _ in range(n + 1)]\np = 2\nfor _ in range(m):\n    u, v = data[p], data[p + 1]\n    p += 2\n    adj[u].append(v)\n    indeg[v] += 1\nfrom collections import deque\nq = deque(i for i in range(1, n + 1) if indeg[i] == 0)\ncnt = 0\nwhile q:\n    x = q.popleft()\n    cnt += 1\n    for y in adj[x]:\n        indeg[y] -= 1\n        if indeg[y] == 0:\n            q.append(y)\nprint(\'Yes\' if cnt < n else \'No\')\n', 'python',
 '图论,拓扑排序,判环', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3 3\n1 2\n2 3\n3 1', 'Yes\n', 1, 1),
(@aid, '5 1\n1 3', 'No\n', 0, 2),
(@aid, '5 4\n1 3\n2 5\n4 5\n4 3', 'No\n', 0, 3),
(@aid, '5 4\n1 2\n1 3\n2 5\n5 2', 'Yes\n', 0, 4),
(@aid, '6 2\n2 6\n3 5', 'No\n', 0, 5),
(@aid, '5 2\n1 3\n2 5', 'No\n', 0, 6);

-- ---------- 162. 树的直径（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('树的直径', 3, 20, '## 【题目描述】\n\n给定一棵 n 个结点的树（边权均为 1），求树的直径，即树中相距最远的两个结点之间的距离（按边数计）。\n\n## 【输入格式】\n\n第一行一个整数 n；接下来 n-1 行，每行两个整数 u、v，表示一条树边。\n\n## 【输出格式】\n\n一行，一个整数，表示直径长度。\n\n## 【样例】\n\n输入：\n\n```\n5\n1 2\n1 3\n3 4\n3 5\n```\n\n输出：\n\n```\n3\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁵\n\n## 【提示】\n\n两遍 BFS：先从任意点出发找到最远点 a，再从 a 出发做 BFS，得到的最大距离就是直径（树中结论成立，带权树同样适用）。', '第一行一个整数 n；接下来 n-1 行，每行两个整数 u、v，表示一条树边。', '一行，一个整数，表示直径长度。',
 '5\n1 2\n1 3\n3 4\n3 5', '3', '两遍 BFS：先从任意点出发找到最远点 a，再从 a 出发做 BFS，得到的最大距离就是直径（树中结论成立，带权树同样适用）。', 'import sys\nfrom collections import deque\n\ndata = list(map(int, sys.stdin.read().split()))\nn = data[0]\nadj = [[] for _ in range(n + 1)]\np = 1\nfor _ in range(n - 1):\n    u, v = data[p], data[p + 1]\n    p += 2\n    adj[u].append(v)\n    adj[v].append(u)\n\n\ndef bfs(s):\n    dist = [-1] * (n + 1)\n    dist[s] = 0\n    q = deque([s])\n    far = s\n    while q:\n        x = q.popleft()\n        if dist[x] > dist[far]:\n            far = x\n        for y in adj[x]:\n            if dist[y] == -1:\n                dist[y] = dist[x] + 1\n                q.append(y)\n    return far, dist[far]\n\n\na, _ = bfs(1)\nb, d = bfs(a)\nprint(d)\n', 'python',
 '图论,树,直径', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '5\n1 2\n1 3\n3 4\n3 5', '3\n', 1, 1),
(@aid, '6\n1 2\n2 3\n2 4\n3 5\n5 6', '4\n', 0, 2),
(@aid, '5\n1 2\n2 3\n2 4\n2 5', '2\n', 0, 3),
(@aid, '5\n1 2\n2 3\n3 4\n2 5', '3\n', 0, 4),
(@aid, '6\n1 2\n2 3\n3 4\n4 5\n4 6', '4\n', 0, 5),
(@aid, '2\n1 2', '1\n', 0, 6);

-- ---------- 163. 二叉树的遍历（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('二叉树的遍历', 3, 20, '## 【题目描述】\n\n给定一棵二叉树的先序遍历序列和中序遍历序列（结点权值互不相同），输出它的后序遍历序列。\n\n## 【输入格式】\n\n两行。第一行为先序遍历序列；第二行为中序遍历序列，结点之间用空格分隔。\n\n## 【输出格式】\n\n一行，后序遍历序列，结点之间用空格分隔。\n\n## 【样例】\n\n输入：\n\n```\n1 2 4 5 3 6\n4 2 5 1 6 3\n```\n\n输出：\n\n```\n4 5 2 6 3 1\n```\n\n## 【数据范围】\n\n1 ≤ 结点数 ≤ 10⁴，权值互不相同\n\n## 【提示】\n\n先序的第一个元素就是根，在中序中找到根的位置即可划分出左右子树，再递归处理；用哈希表记录中序下标可避免线性查找。', '两行。第一行为先序遍历序列；第二行为中序遍历序列，结点之间用空格分隔。', '一行，后序遍历序列，结点之间用空格分隔。',
 '1 2 4 5 3 6\n4 2 5 1 6 3', '4 5 2 6 3 1', '先序的第一个元素就是根，在中序中找到根的位置即可划分出左右子树，再递归处理；用哈希表记录中序下标可避免线性查找。', 'import sys\n\ndata = sys.stdin.read().split(\'\\n\')\npre = list(map(int, data[0].split()))\nmid = list(map(int, data[1].split()))\npos = {v: i for i, v in enumerate(mid)}\nres = []\n\n\ndef build(pl, pr, ml, mr):\n    if pl > pr:\n        return\n    root = pre[pl]\n    k = pos[root]\n    build(pl + 1, pl + k - ml, ml, k - 1)\n    build(pl + k - ml + 1, pr, k + 1, mr)\n    res.append(root)\n\n\nbuild(0, len(pre) - 1, 0, len(mid) - 1)\nprint(\' \'.join(map(str, res)))\n', 'python',
 '数据结构,二叉树,遍历', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '1 2 4 5 3 6\n4 2 5 1 6 3', '4 5 2 6 3 1\n', 1, 1),
(@aid, '76 63 11 34 64 95 87\n11 34 63 64 76 87 95', '34 11 64 63 87 95 76\n', 0, 2),
(@aid, '98 51 44 43 68 58 89 83 84\n43 44 51 58 68 83 84 89 98', '43 44 58 84 83 89 68 51 98\n', 0, 3),
(@aid, '33 31 69 76 89 77 91 93 92\n31 33 69 76 77 89 91 92 93', '31 77 92 93 91 89 76 69 33\n', 0, 4),
(@aid, '75 54 43 23 1\n1 23 43 54 75', '1 23 43 54 75\n', 0, 5),
(@aid, '51\n51', '51\n', 0, 6);

-- ---------- 164. 二叉搜索树查找（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('二叉搜索树查找', 2, 10, '## 【题目描述】\n\n依次把 n 个整数插入到一棵初始为空的二叉搜索树中（权值相等时插入右子树），然后查找给定的值 x 是否存在于树中。\n\n## 【输入格式】\n\n第一行两个整数 n、x；第二行 n 个整数，表示插入序列。\n\n## 【输出格式】\n\n一行，存在输出 Yes，否则输出 No。\n\n## 【样例】\n\n输入：\n\n```\n6 7\n5 3 8 2 4 9\n```\n\n输出：\n\n```\nNo\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁵\n\n## 【提示】\n\nBST 的中序遍历是有序序列，查找时只需沿一条路径向下比较，平均 O(log n)；注意退化成链时会变成 O(n)。', '第一行两个整数 n、x；第二行 n 个整数，表示插入序列。', '一行，存在输出 Yes，否则输出 No。',
 '6 7\n5 3 8 2 4 9', 'No', 'BST 的中序遍历是有序序列，查找时只需沿一条路径向下比较，平均 O(log n)；注意退化成链时会变成 O(n)。', 'import sys\n\ndata = list(map(int, sys.stdin.read().split()))\nn, x = data[0], data[1]\nseq = data[2:2 + n]\n\n\nclass Node:\n    __slots__ = (\'v\', \'l\', \'r\')\n\n    def __init__(self, v):\n        self.v = v\n        self.l = None\n        self.r = None\n\n\nroot = None\nfor v in seq:\n    nd = Node(v)\n    if root is None:\n        root = nd\n        continue\n    cur = root\n    while True:\n        if v < cur.v:\n            if cur.l is None:\n                cur.l = nd\n                break\n            cur = cur.l\n        else:\n            if cur.r is None:\n                cur.r = nd\n                break\n            cur = cur.r\ncur = root\nfound = False\nwhile cur:\n    if x == cur.v:\n        found = True\n        break\n    cur = cur.l if x < cur.v else cur.r\nprint(\'Yes\' if found else \'No\')\n', 'python',
 '数据结构,二叉搜索树', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '6 7\n5 3 8 2 4 9', 'No\n', 1, 1),
(@aid, '9 80\n2 80 94 66 79 55 73 85 42', 'Yes\n', 0, 2),
(@aid, '4 85\n12 88 20 34 55 77 85 7', 'No\n', 0, 3),
(@aid, '9 16\n16 45', 'Yes\n', 0, 4),
(@aid, '5 33\n51 30 60 18 33 82 63', 'Yes\n', 0, 5),
(@aid, '10 10\n27 23 10 22 78 93 32 55', 'Yes\n', 0, 6);

-- ---------- 165. 最小的 k 个数（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('最小的 k 个数', 2, 10, '## 【题目描述】\n\n给定 n 个整数和整数 k，输出其中最小的 k 个数（按从小到大的顺序）。\n\n## 【输入格式】\n\n第一行两个整数 n、k；第二行 n 个整数。\n\n## 【输出格式】\n\n一行，k 个整数，用空格分隔。\n\n## 【样例】\n\n输入：\n\n```\n5 3\n4 5 1 6 2\n```\n\n输出：\n\n```\n1 2 4\n```\n\n## 【数据范围】\n\n1 ≤ k ≤ n ≤ 10⁵\n\n## 【提示】\n\n排序取前 k 个最简单；数据量大时用大小为 k 的大根堆维护当前最小的 k 个数，可做到 O(n log k)。', '第一行两个整数 n、k；第二行 n 个整数。', '一行，k 个整数，用空格分隔。',
 '5 3\n4 5 1 6 2', '1 2 4', '排序取前 k 个最简单；数据量大时用大小为 k 的大根堆维护当前最小的 k 个数，可做到 O(n log k)。', 'import sys\n\ndata = list(map(int, sys.stdin.read().split()))\nn, k = data[0], data[1]\na = data[2:2 + n]\na.sort()\nprint(\' \'.join(map(str, a[:k])))\n', 'python',
 '数据结构,堆,排序', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '5 3\n4 5 1 6 2', '1 2 4\n', 1, 1),
(@aid, '2 1\n695 835', '695\n', 0, 2),
(@aid, '14 10\n14 192 417 523 931 352 78 949 530 449 302 832 151 323', '14 78 151 192 302 323 352 417 449 523\n', 0, 3),
(@aid, '9 1\n75 649 765 606 47 495 813 519 421', '47\n', 0, 4),
(@aid, '18 13\n397 984 314 190 415 974 588 553 484 514 977 411 732 95 436 373 932 914', '95 190 314 373 397 411 415 436 484 514 553 588 732\n', 0, 5),
(@aid, '3 1\n447 253 882', '253\n', 0, 6);

-- ---------- 166. 合并果子（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('合并果子', 3, 20, '## 【题目描述】\n\n有 n 堆果子，每堆重量为 aᵢ。每次可以把任意两堆合并成一堆，耗费的体力等于两堆重量之和。求把所有果子合并成一堆的最小总体力。\n\n## 【输入格式】\n\n第一行一个整数 n；第二行 n 个整数。\n\n## 【输出格式】\n\n一行，一个整数，表示最小体力。\n\n## 【样例】\n\n输入：\n\n```\n3\n1 2 9\n```\n\n输出：\n\n```\n15\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁴\n\n## 【提示】\n\n哈夫曼贪心：每次取最小的两堆合并，把合并结果放回堆中；用优先队列实现，复杂度 O(n log n)。', '第一行一个整数 n；第二行 n 个整数。', '一行，一个整数，表示最小体力。',
 '3\n1 2 9', '15', '哈夫曼贪心：每次取最小的两堆合并，把合并结果放回堆中；用优先队列实现，复杂度 O(n log n)。', 'import sys\nimport heapq\n\ndata = list(map(int, sys.stdin.read().split()))\nn = data[0]\na = data[1:1 + n]\nheapq.heapify(a)\nans = 0\nwhile len(a) > 1:\n    x = heapq.heappop(a)\n    y = heapq.heappop(a)\n    s = x + y\n    ans += s\n    heapq.heappush(a, s)\nprint(ans)\n', 'python',
 '贪心,优先队列,哈夫曼', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '3\n1 2 9', '15\n', 1, 1),
(@aid, '10\n13 10 88 93 39 26 54 22 79 69', '1519\n', 0, 2),
(@aid, '12\n34 20 18 53 8 33 20 58 28 57 18 56', '1380\n', 0, 3),
(@aid, '9\n74 26 44 72 30 33 36 61 7', '1168\n', 0, 4),
(@aid, '14\n32 10 54 31 93 68 74 27 44 91 69 21 67 85', '2804\n', 0, 5),
(@aid, '15\n49 75 30 17 61 12 41 44 3 13 82 35 72 19 39', '2157\n', 0, 6);

-- ---------- 167. 下一个更大元素（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('下一个更大元素', 3, 20, '## 【题目描述】\n\n给定一个长度为 n 的整数序列，对每个元素求它右边第一个比它大的元素的值；若不存在，记为 -1。\n\n## 【输入格式】\n\n第一行一个整数 n；第二行 n 个整数。\n\n## 【输出格式】\n\n一行，n 个整数，用空格分隔。\n\n## 【样例】\n\n输入：\n\n```\n5\n2 1 2 4 3\n```\n\n输出：\n\n```\n4 2 4 -1 -1\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁵\n\n## 【提示】\n\n单调栈：从右往左扫描，维护一个严格递减的栈，栈顶就是右侧第一个更大的元素；弹出所有不大于当前元素的栈顶后再入栈。', '第一行一个整数 n；第二行 n 个整数。', '一行，n 个整数，用空格分隔。',
 '5\n2 1 2 4 3', '4 2 4 -1 -1', '单调栈：从右往左扫描，维护一个严格递减的栈，栈顶就是右侧第一个更大的元素；弹出所有不大于当前元素的栈顶后再入栈。', 'import sys\n\ndata = list(map(int, sys.stdin.read().split()))\nn = data[0]\na = data[1:1 + n]\nres = [-1] * n\nst = []\nfor i in range(n - 1, -1, -1):\n    while st and st[-1] <= a[i]:\n        st.pop()\n    if st:\n        res[i] = st[-1]\n    st.append(a[i])\nprint(\' \'.join(map(str, res)))\n', 'python',
 '数据结构,单调栈', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '5\n2 1 2 4 3', '4 2 4 -1 -1\n', 1, 1),
(@aid, '11\n9 41 48 26 5 26 33 48 30 10 5', '41 48 -1 33 26 33 48 -1 -1 -1 -1\n', 0, 2),
(@aid, '17\n34 26 37 1 22 31 46 6 8 2 49 41 35 15 47 13 25', '37 37 46 22 31 46 49 8 49 49 -1 47 47 47 -1 25 -1\n', 0, 3),
(@aid, '5\n23 18 40 41 2', '40 40 41 -1 -1\n', 0, 4),
(@aid, '16\n8 8 15 22 46 37 34 30 22 33 39 39 25 11 19 49', '15 15 22 46 49 39 39 33 33 39 49 49 49 19 49 -1\n', 0, 5),
(@aid, '4\n26 19 50 42', '50 50 -1 -1\n', 0, 6);

-- ---------- 168. 滑动窗口最大值（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('滑动窗口最大值', 3, 20, '## 【题目描述】\n\n给定一个长度为 n 的整数序列和一个窗口大小 k，求每个长度为 k 的连续子区间中的最大值，按窗口从左到右的顺序输出。\n\n## 【输入格式】\n\n第一行两个整数 n、k；第二行 n 个整数。\n\n## 【输出格式】\n\n一行，n-k+1 个整数，用空格分隔。\n\n## 【样例】\n\n输入：\n\n```\n8 3\n1 3 -1 -3 5 3 6 7\n```\n\n输出：\n\n```\n3 3 5 5 6 7\n```\n\n## 【数据范围】\n\n1 ≤ k ≤ n ≤ 10⁵\n\n## 【提示】\n\n单调队列：队列中保持递减，队首即当前窗口最大值；元素滑出窗口时才从队首删除，整体 O(n)。', '第一行两个整数 n、k；第二行 n 个整数。', '一行，n-k+1 个整数，用空格分隔。',
 '8 3\n1 3 -1 -3 5 3 6 7', '3 3 5 5 6 7', '单调队列：队列中保持递减，队首即当前窗口最大值；元素滑出窗口时才从队首删除，整体 O(n)。', 'import sys\nfrom collections import deque\n\ndata = list(map(int, sys.stdin.read().split()))\nn, k = data[0], data[1]\na = data[2:2 + n]\nq = deque()\nout = []\nfor i, x in enumerate(a):\n    while q and q[-1] < x:\n        q.pop()\n    q.append(x)\n    if i >= k and q[0] == a[i - k]:\n        q.popleft()\n    if i >= k - 1:\n        out.append(str(q[0]))\nprint(\' \'.join(out))\n', 'python',
 '数据结构,单调队列,滑动窗口', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '8 3\n1 3 -1 -3 5 3 6 7', '3 3 5 5 6 7\n', 1, 1),
(@aid, '24 17\n10 68 57 32 65 51 23 78 36 75 34 44 84 26 50 49 15 52 46 32 84 20 4 3', '84 84 84 84 84 84 84 84\n', 0, 2),
(@aid, '16 12\n48 44 95 57 86 65 42 18 9 47 89 92 72 99 100 56', '95 95 99 100 100\n', 0, 3),
(@aid, '5 1\n43 10 32 58 1', '43 10 32 58 1\n', 0, 4),
(@aid, '24 17\n24 8 69 19 95 31 89 14 73 93 83 22 15 70 28 87 88 97 57 92 11 65 43 96', '95 97 97 97 97 97 97 97\n', 0, 5),
(@aid, '20 5\n31 17 3 64 28 31 87 18 51 79 76 51 35 87 65 11 55 89 74 47', '64 64 87 87 87 87 87 79 79 87 87 87 87 89 89 89\n', 0, 6);

-- ---------- 169. 两数之和（哈希表）（难度 2） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('两数之和（哈希表）', 2, 10, '## 【题目描述】\n\n给定一个整数序列和一个目标值 target，找出和为目标值的两个元素的下标（下标从 0 开始，答案唯一）；若不存在，输出 -1 -1。\n\n## 【输入格式】\n\n第一行两个整数 n、target；第二行 n 个整数。\n\n## 【输出格式】\n\n一行，两个整数，表示两个下标，小的在前。\n\n## 【样例】\n\n输入：\n\n```\n4 9\n2 7 11 15\n```\n\n输出：\n\n```\n0 1\n```\n\n## 【数据范围】\n\n2 ≤ n ≤ 10⁵\n\n## 【提示】\n\n一边扫描一边把"值 → 下标"存入哈希表，对当前元素 x 只需查 target - x 是否已出现过，O(n) 一次遍历。', '第一行两个整数 n、target；第二行 n 个整数。', '一行，两个整数，表示两个下标，小的在前。',
 '4 9\n2 7 11 15', '0 1', '一边扫描一边把"值 → 下标"存入哈希表，对当前元素 x 只需查 target - x 是否已出现过，O(n) 一次遍历。', 'import sys\n\ndata = list(map(int, sys.stdin.read().split()))\nn, target = data[0], data[1]\na = data[2:2 + n]\nseen = {}\nans = (-1, -1)\nfor i, x in enumerate(a):\n    need = target - x\n    if need in seen:\n        ans = (seen[need], i)\n        break\n    seen[x] = i\nprint(ans[0], ans[1])\n', 'python',
 '数据结构,哈希表', '洛谷', 8);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '4 9\n2 7 11 15', '0 1\n', 1, 1),
(@aid, '9 98\n80 66 15 61 9 89 39 99 48', '4 5\n', 0, 2),
(@aid, '4 67\n65 2 30 90', '0 1\n', 0, 3),
(@aid, '9 50\n73 14 29 59 36 64 89 84 76', '1 4\n', 0, 4),
(@aid, '14 129\n56 89 45 70 11 77 62 46 21 89 60 73 93 86', '0 11\n', 0, 5),
(@aid, '9 122\n30 46 92 30 79 13 87 45 90', '0 2\n', 0, 6);

-- ---------- 170. 二分图判定（难度 3） ----------
INSERT INTO algorithm
  (title, difficulty, weight, description, input_desc, output_desc,
   sample_input, sample_output, hints, reference_code, reference_language,
   tags, source, knowledge_id)
VALUES
('二分图判定', 3, 20, '## 【题目描述】\n\n给定一个 n 个点、m 条边的无向图，判断它是否是二分图（能否把点分成两个集合，使得每条边的两个端点分属不同集合）。\n\n## 【输入格式】\n\n第一行两个整数 n、m；接下来 m 行，每行两个整数 u、v，表示一条无向边。\n\n## 【输出格式】\n\n一行，是二分图输出 Yes，否则输出 No。\n\n## 【样例】\n\n输入：\n\n```\n4 4\n1 2\n2 3\n3 4\n4 1\n```\n\n输出：\n\n```\nYes\n```\n\n## 【数据范围】\n\n1 ≤ n ≤ 10⁴，0 ≤ m ≤ 10⁵\n\n## 【提示】\n\nBFS/DFS 二染色：从任一点开始染成 1，相邻点必须染成相反颜色；若出现一条边两端颜色相同，说明存在奇环，不是二分图。', '第一行两个整数 n、m；接下来 m 行，每行两个整数 u、v，表示一条无向边。', '一行，是二分图输出 Yes，否则输出 No。',
 '4 4\n1 2\n2 3\n3 4\n4 1', 'Yes', 'BFS/DFS 二染色：从任一点开始染成 1，相邻点必须染成相反颜色；若出现一条边两端颜色相同，说明存在奇环，不是二分图。', 'import sys\nfrom collections import deque\n\ndata = list(map(int, sys.stdin.read().split()))\nn, m = data[0], data[1]\nadj = [[] for _ in range(n + 1)]\np = 2\nfor _ in range(m):\n    u, v = data[p], data[p + 1]\n    p += 2\n    adj[u].append(v)\n    adj[v].append(u)\ncolor = [0] * (n + 1)\nok = True\nfor s in range(1, n + 1):\n    if color[s]:\n        continue\n    color[s] = 1\n    q = deque([s])\n    while q and ok:\n        x = q.popleft()\n        for y in adj[x]:\n            if color[y] == 0:\n                color[y] = -color[x]\n                q.append(y)\n            elif color[y] == color[x]:\n                ok = False\n                break\nprint(\'Yes\' if ok else \'No\')\n', 'python',
 '图论,二分图,染色', '洛谷', NULL);
SET @aid = LAST_INSERT_ID();
INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES
(@aid, '4 4\n1 2\n2 3\n3 4\n4 1', 'Yes\n', 1, 1),
(@aid, '10 3\n5 9\n7 9\n8 9', 'Yes\n', 0, 2),
(@aid, '3 0\n', 'Yes\n', 0, 3),
(@aid, '2 1\n1 2', 'Yes\n', 0, 4),
(@aid, '7 2\n1 5\n5 6', 'Yes\n', 0, 5),
(@aid, '9 6\n2 7\n2 9\n3 9\n5 9\n7 8\n4 6', 'Yes\n', 0, 6);
