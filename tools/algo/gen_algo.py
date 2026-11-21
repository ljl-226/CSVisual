# -*- coding: utf-8 -*-
"""
算法题库扩容生成器（洛谷风格 OI 题）

设计要点：
  1. 题目以「数据 + 参考代码 + 测试数据生成函数」的形式写在 tools/algo/p*.py 中，
     不手写 SQL，避免题干与代码里的引号/换行导致非法转义。
  2. 每个用例的 expected 由**真实运行** reference_code 得到（子进程执行 Python 3），
     保证与判题机标准输出逐字符一致，杜绝"手写出错答案"的问题。
  3. 输出 server-py/sql/seed-algo200.sql，由 migrate.py / migrate.js 负责导入。

用法：python tools/algo/gen_algo.py
"""
import os
import random
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)

OUT = os.path.join(ROOT, 'server-py', 'sql', 'seed-algo200.sql')

# 难度 -> 权值（与 seed-algo.sql 保持一致：1-2 -> 10，3 -> 20，4 -> 30，5 -> 50）
WEIGHT = {1: 10, 2: 10, 3: 20, 4: 30, 5: 50}
CASES_PER_PROBLEM = 6  # 1 个样例 + 5 个隐藏用例


def esc(s):
    """MySQL 单引号字符串转义：反斜杠 -> 换行 -> 单引号，顺序不可颠倒"""
    if s is None:
        return ''
    return str(s).replace('\\', '\\\\').replace('\n', '\\n').replace("'", "\\'")


def run_ref(code, stdin, timeout=8):
    """真实运行参考代码，返回标准输出"""
    p = subprocess.run(
        [sys.executable, '-c', code],
        input=stdin, capture_output=True, text=True, timeout=timeout,
    )
    if p.returncode != 0:
        raise RuntimeError('参考代码运行失败: ' + p.stderr[-500:])
    return p.stdout


def load_problems():
    mods = sorted(f[:-3] for f in os.listdir(HERE) if f.startswith('p') and f.endswith('.py'))
    problems = []
    for m in mods:
        mod = __import__(m)
        lst = getattr(mod, 'PROBLEMS', [])
        if not lst:
            raise RuntimeError(m + ' 中没有 PROBLEMS')
        problems.extend(lst)
    return problems, mods


def build_sql(problems):
    chunks = []
    chunks.append('-- ============================================================')
    chunks.append('--  算法题库扩容：洛谷风格程序设计题（新增 %d 道，总数 30 -> 200）' % len(problems))
    chunks.append('--  说明：')
    chunks.append('--    1. 每道题先 INSERT 一条 algorithm，紧跟 SET @aid = LAST_INSERT_ID();，')
    chunks.append('--       再用 (@aid, ...) 插入该题测试用例，保证用例挂在正确的题目上')
    chunks.append('--    2. 每个用例的 expected 由 Python 3 真实运行 reference_code 得到，')
    chunks.append('--       与程序标准输出逐字符一致（含行末换行）')
    chunks.append('--    3. 测试用例 = 1 个样例（is_sample=1）+ 5 个隐藏用例，由固定随机种子生成')
    chunks.append('--  本文件由 tools/algo/gen_algo.py 生成，请勿手工编辑')
    chunks.append('--  执行顺序：... -> seed-textbook -> seed-core20 -> seed-algo200')
    chunks.append('-- ============================================================')
    chunks.append('')
    for i, p in enumerate(problems):
        chunks.append('-- ---------- %d. %s（难度 %d） ----------' % (i + 1, p['title'], p['difficulty']))
        chunks.append(
            "INSERT INTO algorithm\n"
            "  (title, difficulty, weight, description, input_desc, output_desc,\n"
            "   sample_input, sample_output, hints, reference_code, reference_language,\n"
            "   tags, source, knowledge_id)\nVALUES\n"
            "('%s', %d, %d, '%s', '%s', '%s',\n"
            " '%s', '%s', '%s', '%s', 'python',\n"
            " '%s', '%s', %s);"
            % (
                esc(p['title']), p['difficulty'], WEIGHT[p['difficulty']],
                esc(p['desc']), esc(p.get('in', '')), esc(p.get('out', '')),
                esc(p['sample_in']), esc(p['sample_out']), esc(p.get('hint', '')),
                esc(p['ref']), esc(p.get('tags', '')), esc(p.get('source', '洛谷')),
                'NULL' if p.get('kid') is None else p['kid'],
            )
        )
        chunks.append('SET @aid = LAST_INSERT_ID();')
        rows = []
        for case in p['cases']:
            rows.append("(@aid, '%s', '%s', %d, %d)" % (
                esc(case['stdin']), esc(case['expected']), case['is_sample'], case['sort_no']))
        chunks.append('INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES\n'
                      + ',\n'.join(rows) + ';')
        chunks.append('')
    return '\n'.join(chunks)


def main():
    problems, mods = load_problems()
    print('载入题目数据: %d 个文件，共 %d 道题' % (len(mods), len(problems)))

    # 1) 生成测试输入（固定种子，保证可复现）
    tasks = []  # (problem_index, code, stdin)
    for idx, p in enumerate(problems):
        gen = p['gen']
        rnd = random.Random(10000 + idx)
        inputs = [p['sample_in']] + [gen(rnd) for _ in range(CASES_PER_PROBLEM - 1)]
        for s in inputs:
            tasks.append((idx, p['ref'], s))

    # 2) 并发真实运行参考代码求期望输出
    results = [None] * len(tasks)

    def work(i):
        idx, code, s = tasks[i]
        return run_ref(code, s)

    print('运行参考代码计算期望输出：%d 个用例 ...' % len(tasks))
    with ThreadPoolExecutor(max_workers=16) as ex:
        for i, out in enumerate(ex.map(work, range(len(tasks)))):
            results[i] = out

    # 3) 校验样例输出与真实运行结果一致
    bad = 0
    for idx, p in enumerate(problems):
        real = results[idx * CASES_PER_PROBLEM]
        if real.strip() != p['sample_out'].strip():
            print('  [警告] 《%s》样例输出与参考代码运行结果不一致：\n    题面=%r\n    实际=%r'
                  % (p['title'], p['sample_out'], real))
            bad += 1

    # 4) 组装用例
    for idx, p in enumerate(problems):
        cases = []
        for k in range(CASES_PER_PROBLEM):
            cases.append({
                'stdin': tasks[idx * CASES_PER_PROBLEM + k][2],
                'expected': results[idx * CASES_PER_PROBLEM + k],
                'is_sample': 1 if k == 0 else 0,
                'sort_no': k + 1,
            })
        p['cases'] = cases

    sql = build_sql(problems)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(sql)
    print('已生成 ' + os.path.relpath(OUT, ROOT))
    print('题目数 %d，用例数 %d，样例不一致 %d 处' % (len(problems), len(tasks), bad))
    from collections import Counter
    print('难度分布: ' + str(dict(sorted(Counter(p['difficulty'] for p in problems).items()))))
    if bad:
        sys.exit(1)


if __name__ == '__main__':
    main()
