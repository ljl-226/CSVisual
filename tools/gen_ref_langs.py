# -*- coding: utf-8 -*-
"""把算法题的 Python 参考答案转成 C / C++ / Java / JavaScript 版本，并**真实验证**。

为什么不用「正则翻译 Python 源码」：
    实测这 200 道题里有 16 道含 `def` 自定义函数、33 道用列表推导、
    还有字典、集合、切片 [::-1]、enumerate、reversed、递归。
    逐行机械翻译会产出「能编译但逻辑错」的代码 —— 对学生来说比没有更糟。
    所以改成让大模型按题面重写一份，再用项目自己的判题引擎跑全部测试用例，
    **全部通过才入库**，跑不过的语言直接不写，���端如实显示「暂无该语言参考答案」。

流程：
    1. 取题面（description / input_desc / output_desc / 样例）
    2. 连同 Python 参考答案一起发给 LLM，要求输出目标语言的等价实现
    3. judge(cases, lang, code) 跑全部用例
    4. accepted 才 INSERT，且 verified=1

用法：
    python tools/gen_ref_langs.py --limit 5 --langs cpp      # 试跑
    python tools/gen_ref_langs.py --limit 0                  # 全量
    python tools/gen_ref_langs.py --only-missing            # 只补没写过的
    python tools/gen_ref_langs.py --dry-run                 # 不写库
"""
import sys
import os
import re
import json
import time
import argparse

sys.path.insert(0, 'server-py')

from app.db import query  # noqa: E402
from app.routers.algorithm import judge  # noqa: E402
from app.agent.llm import call_llm  # noqa: E402

TARGET_LANGS = ['c', 'cpp', 'java', 'javascript']

# 每门语言额外要注意的坑，写进提示词里（都是评测环境特有的，不写 LLM 会踩）
LANG_NOTES = {
    'c': [
        '评测机只认 main 函数，返回 int，结尾 return 0。',
        '用 printf 输出，不要用 puts 除非确定不需要换行。',
        '需要大整数/字符串处理时用 malloc 分配或静态数组，并 #include <string.h>。',
    ],
    'cpp': [
        '评测只编译单个 .cpp 文件，main 必须返回 int。',
        '开头写 ios::sync_with_stdio(false); cin.tie(nullptr); 否则大数据会超时。',
        '可以用 vector / string / map / set / algorithm 头文件里的东西。',
    ],
    'java': [
        '**类名必须严格是 Main**，评测机按这个约定找入口，改名会判编译失败。',
        '**不需要 package 语句**，直接 import。',
        'main 方法写成 public static void main(String[] args) throws IOException。',
        '大数据用 BufferedReader + StringBuilder，别用 Scanner（慢 10 倍容易超时）。',
    ],
    'javascript': [
        '运行环境是 **Node.js（V8）**，不是浏览器，不能用 document / window。',
        '用 require("fs").readFileSync(0, "utf8") 读标准输入。',
        '必须自己定义并调用 main 函数，顶层直接写逻辑在 strict 模式下也能跑，但用 main 更清晰。',
    ],
}

PROMPT = '''你是一位算法竞赛教练。给你一道题和它的 Python 参考答案，请写出 {lang} 的等价实现。

【题目】
{title}

【题面】
{desc}

【输入格式】
{input_desc}

【输出格式】
{output_desc}

【样例输入】
{sample_input}

【样例输出】
{sample_output}

【Python 参考答案（已验证通过，可以照着它的思路翻译）】
```python
{py_code}
```

【{lang} 注意事项】
{notes}

【硬性要求】
1. 必须是**完整可运行**的程序，包含该语言读标准输入的代码。
2. 逻辑必须与 Python 参考答案**完全等价**，包括输出格式（小数位数、空格分隔、换行）。
3. 不要输出任何解释文字，只输出代码本身。
4. 严格只输出一个代码块，格式为：
```{fence}
你的代码
```

现在输出 {lang} 代码：'''

SYSTEM = ('你是算法竞赛教练，专精把 Python 解法等价改写成 C / C++ / Java / JavaScript。'
          '你只输出代码，不输出解释。代码必须能通过编译并正确读标准输入。')


def build_prompt(row, lang):
    fence = {'c': 'c', 'cpp': 'cpp', 'java': 'java', 'javascript': 'javascript'}[lang]
    desc = (row['description'] or '')[:2500]
    return PROMPT.format(
        title=row['title'],
        lang={'c': 'C', 'cpp': 'C++', 'java': 'Java', 'javascript': 'JavaScript'}[lang],
        desc=desc,
        input_desc=(row.get('input_desc') or '见题面')[:500],
        output_desc=(row.get('output_desc') or '见题面')[:500],
        sample_input=(row.get('sample_input') or '')[:300],
        sample_output=(row.get('sample_output') or '')[:300],
        py_code=row['reference_code'],
        notes='\n'.join('- ' + x for x in LANG_NOTES[lang]),
        fence=fence,
    )


def extract_code(text, lang):
    """从 LLM 回复里抽出代码块。模型有时会在代码前后加话，必须容错。"""
    if not text:
        return None
    fences = ['```' + lang, '```cpp', '```c', '```java', '```javascript', '```js', '```']
    best = None
    for f in fences:
        m = re.search(re.escape(f) + r'\s*\n(.*?)\n?```', text, re.S)
        if m:
            best = m.group(1)
            break
    if best is None:
        # 没有围栏 —— 有些回复直接给裸代码
        best = text.strip()
    best = best.strip()
    if not best or len(best) < 20:
        return None
    # 清掉可能残留的行号
    best = re.sub(r'^\s*\d+\s*\|', '', best, flags=re.M)
    best = re.sub(r'^\s*\d+\s*$', '', best, flags=re.M)
    return best.strip() + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=0, help='0 = 全量')
    ap.add_argument('--offset', type=int, default=0)
    ap.add_argument('--langs', default=','.join(TARGET_LANGS))
    ap.add_argument('--only-missing', action='store_true', help='只处理还没写过的 (题, 语言)')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    langs = [x.strip() for x in args.langs.split(',') if x.strip()]

    have = {}
    if args.only_missing:
        for r in query('SELECT algorithm_id, language FROM algorithm_reference_lang').rows:
            have[(int(r['algorithm_id']), r['language'])] = True

    rows = query(
        'SELECT id, title, description, input_desc, output_desc, sample_input, sample_output, '
        'reference_code FROM algorithm WHERE status = 1 AND reference_code IS NOT NULL '
        'AND reference_code != \'\' ORDER BY id').rows
    rows = [dict(r) for r in rows]
    if args.offset:
        rows = rows[args.offset:]
    if args.limit:
        rows = rows[:args.limit]

    print('待处理 %d 题，目标语言 %s' % (len(rows), ','.join(langs)))
    if not os.getenv('LLM_API_KEY'):
        print('!! LLM_API_KEY 未配置，无法生成。'
              '请在 server-py/.env 里填入，或改用别的方式补充参考答案。')
        return 1

    stat = {l: {'ok': 0, 'skip': 0, 'fail': 0} for l in langs}
    failed = []

    for i, r in enumerate(rows, 1):
        cases = [dict(c) for c in query(
            'SELECT stdin, expected FROM algorithm_case WHERE algorithm_id = ? ORDER BY sort_no',
            (r['id'],)).rows]
        if not cases:
            continue
        for lang in langs:
            if args.only_missing and have.get((int(r['id']), lang)):
                stat[lang]['skip'] += 1
                continue
            try:
                # call_llm 收的是 messages 数组；temperature 调低让输出更贴合参考实现
                text = call_llm(
                    [{'role': 'system', 'content': SYSTEM},
                     {'role': 'user', 'content': build_prompt(r, lang)}],
                    temperature=0.2)
            except Exception as e:
                print('  [LLM 失败] id=%s %s: %s' % (r['id'], lang, str(e)[:120]))
                stat[lang]['fail'] += 1
                continue
            code = extract_code(text, lang)
            if not code:
                stat[lang]['fail'] += 1
                failed.append((r['title'], lang, 'llm_no_code', ''))
                continue
            res = judge(cases, lang, code)
            if res['status'] == 'accepted':
                stat[lang]['ok'] += 1
                if not args.dry_run:
                    query('INSERT INTO algorithm_reference_lang (algorithm_id, language, code, verified) '
                          'VALUES (?,?,?,1) ON DUPLICATE KEY UPDATE code=VALUES(code), verified=1',
                          (r['id'], lang, code))
            else:
                stat[lang]['fail'] += 1
                failed.append((r['title'], lang, res['status'], (res.get('message') or '')[:150]))
            time.sleep(0.4)   # 轻微限速，避免打爆接口
        if i % 5 == 0:
            print('  ...%d/%d  %s' % (i, len(rows), {l: stat[l]['ok'] for l in langs}))

    print('=' * 60)
    for l in langs:
        s = stat[l]
        print('%-11s 通过 %3d   跳过 %3d   失败 %3d' % (l, s['ok'], s['skip'], s['fail']))
    if failed:
        print('--- 失败明细（前 20 条）---')
        for f in failed[:20]:
            print('   %s [%s] %s | %s' % f)
    print('写库：%s' % ('否（dry-run）' if args.dry_run else '是'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
