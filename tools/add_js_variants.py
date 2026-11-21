"""给 labVariants.js 里缺 javascript 的主题补上 JS 实现。

为什么不直接手改：那些代码块是 100~200 行的模板字符串，
用编辑器插入极易和相邻语言的代码串味（上一轮就打进过乱码字符）。
JS 实现放在 _labjs_snippets.py，这里按锚点插入 —— 出错只需重跑本脚本。

插入位置：每个主题块的最后一个小节之后（javascript 一律排最后，
和 collection / concurrency 等已有主题的排法一致）。
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.normpath(os.path.join(ROOT, '..', 'web', 'src', 'data', 'labVariants.js'))
SNIPPETS = os.path.join(ROOT, '_labjs_snippets.py')


def main():
    ns = {}
    with io.open(SNIPPETS, 'r', encoding='utf-8') as f:
        exec(compile(f.read(), SNIPPETS, 'exec'), ns)

    # 主题名 -> snippet 变量名
    plan = [
        ('pointer-memory', 'SNIPPET_POINTER'),
        ('memory-layout', 'SNIPPET_MEMORY'),
        ('oop-class', 'SNIPPET_OOP_CLASS'),
        ('oop-polymorphism', 'SNIPPET_OOP_POLY'),
        ('generics', 'SNIPPET_GENERICS'),
        ('exception', 'SNIPPET_EXCEPTION'),
    ]

    with io.open(TARGET, 'r', encoding='utf-8', newline='') as f:
        src = f.read()
    crlf = '\r\n' in src
    head_end = src.index('export const VARIANTS = {')
    # VARIANTS 块的结束锚点：从 hasVariant 往前找最近的独立 '}' 行。
    # 不能用 index('\n}\n') —— 主题代码里正好有裸 '}' 行（Python 的 class、
    # C 的 struct），会把边界切到 oop-class 中间去。
    k = src.index('export function hasVariant')
    body_end = src.rindex('\n}\n', head_end, k)
    head, body, tail = src[:head_end], src[head_end:body_end], src[body_end:]

    added, skipped = [], []
    for theme, var in plan:
        # 每次都重新扫一遍主题起点。
        # 之前算好 starts 一次然后按序插入，越靠后的主题偏移越偏 ——
        # 结果第 5 个主题插到了错误位置（oop-polymorphism 出现两份 javascript，
        # generics 干脆没插上）。重扫的开销可以忽略，正确性不能。
        starts = [(m.start(), m.group(1))
                  for m in re.finditer(r"^  '?([a-zA-Z0-9_-]+)'?: \{", body, re.M)]
        names = [t[1] for t in starts]
        if theme not in names:
            skipped.append((theme, '未找到主题块'))
            continue
        idx = names.index(theme)
        b_start = starts[idx][0]
        b_end = starts[idx + 1][0] if idx + 1 < len(starts) else len(body)
        block = body[b_start:b_end]

        if re.search(r"^    javascript: `", block, re.M):
            skipped.append((theme, '已有 javascript'))
            continue

        # 锚点 = 块内最后一个 "    <lang>: `"，再找到这个模板字符串的收尾反引号
        lasts = list(re.finditer(r"^    [a-z]+: `", block, re.M))
        if not lasts:
            skipped.append((theme, '块内没有可识别的语言小节'))
            continue
        at = lasts[-1].end()
        close = block.find('`', at)
        if close < 0:
            skipped.append((theme, '模板字符串没有闭合'))
            continue
        after = close + 1
        # 收尾反引号后面若已有逗号就保留，没有就补一个
        if after < len(block) and block[after] == ',':
            after += 1

        snippet = ns[var].rstrip('\n') + '\n'
        block = block[:after] + ',\n' + snippet + block[after:].lstrip('\n')
        body = body[:b_start] + block + body[b_end:]
        added.append(theme)

    out = head + body + tail
    if crlf:
        out = out.replace('\r\n', '\n').replace('\n', '\r\n')
    with io.open(TARGET, 'w', encoding='utf-8', newline='') as f:
        f.write(out)

    print('已补 javascript 的主题：%s' % (', '.join(added) or '（无）'))
    for t, why in skipped:
        print('  跳过 %s：%s' % (t, why))
    return 0 if added else 1


if __name__ == '__main__':
    sys.exit(main())
