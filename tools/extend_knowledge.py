# -*- coding: utf-8 -*-
"""
知识点扩展工具：为 65 个「带可视化动画」的知识点补充三个章节
  ## 动画观察要点 —— 看动画时该盯哪里（与动画步骤一一对应）
  ## 易错点       —— 该主题最常踩的坑
  ## 考点速记     —— 应试要点

设计原则：
1. 幂等：扩展内容用 VIS-EXT 标记包裹，重复运行是「替换」而不是「追加」。
2. 可回滚：写库前先把受影响的原 content 导出到 tools/.knowledge-backup-<时间戳>.json。
3. 默认 dry-run：必须显式 --apply 才会写库。
4. 只依赖标准库 + 项目自带的 app.db，不引入新依赖。

用法：
    python tools/extend_knowledge.py                # 预览会改什么
    python tools/extend_knowledge.py --apply        # 真正写入
    python tools/extend_knowledge.py --only 6 8     # 只处理指定 id
    python tools/extend_knowledge.py --stats        # 只看当前长度统计
"""
import argparse
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'server-py'))

from app.db import query, connection  # noqa: E402

BEGIN = '<!-- VIS-EXT-BEGIN -->'
END = '<!-- VIS-EXT-END -->'

# 扩展内容：kid -> {'watch': [...], 'pitfall': [...], 'exam': [...]}
# 由同目录下的 knowledge_extras.py 提供，便于单独维护
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from knowledge_extras import EXTRAS  # noqa: E402


def vis_ids():
    """从 VisPlayer.vue 解析出带可视化的知识点 id"""
    src = open(os.path.join(ROOT, 'web/src/views/VisPlayer.vue'), encoding='utf-8').read()
    pat = re.compile(r"kid:\s*(\d+)")
    return sorted({int(m.group(1)) for m in pat.finditer(src)})


def render(kid, name, extra):
    """把扩展数据渲染成 Markdown"""
    out = [BEGIN, '', '## 动画观察要点']
    for i, t in enumerate(extra.get('watch', []), 1):
        out.append('%d. %s' % (i, t))
    out += ['', '## 易错点']
    for t in extra.get('pitfall', []):
        out.append('- %s' % t)
    out += ['', '## 考点速记']
    for t in extra.get('exam', []):
        out.append('- %s' % t)
    out += ['', END]
    return '\n'.join(out)


def apply_ext(content, block):
    """幂等替换：已有 VIS-EXT 段就换掉，没有就接到末尾"""
    if BEGIN in content and END in content:
        pat = re.compile(re.escape(BEGIN) + r'.*?' + re.escape(END), re.S)
        return pat.sub(block, content)
    return content.rstrip() + '\n\n' + block + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='真正写库（默认只预览）')
    ap.add_argument('--only', nargs='*', type=int, help='只处理指定知识点 id')
    ap.add_argument('--stats', action='store_true', help='只看统计')
    args = ap.parse_args()

    ids = vis_ids()
    rows = {r['id']: r for r in query('SELECT id,name,content FROM knowledge').rows}

    if args.stats:
        have = [i for i in ids if i in EXTRAS]
        lens = [len(rows[i]['content'] or '') for i in ids if i in rows]
        print('带可视化知识点: %d' % len(ids))
        print('已编写扩展内容: %d' % len(have))
        print('未编写: %s' % (sorted(set(ids) - set(EXTRAS)) or '无'))
        print('content 长度: min=%d 中位=%d max=%d' % (
            min(lens), sorted(lens)[len(lens) // 2], max(lens)))
        return

    targets = [i for i in (args.only or ids) if i in rows]
    missing_content = [i for i in targets if i not in EXTRAS]
    if missing_content:
        print('跳过（尚未编写扩展内容）: %s' % missing_content)
    targets = [i for i in targets if i in EXTRAS]

    plan = []
    for kid in targets:
        row = rows[kid]
        old = row['content'] or ''
        block = render(kid, row['name'], EXTRAS[kid])
        new = apply_ext(old, block)
        plan.append((kid, row['name'], old, new))

    for kid, name, old, new in plan:
        print('  id=%-3d %-22s %d -> %d 字 (+%d)' % (kid, name, len(old), len(new), len(new) - len(old)))

    if not args.apply:
        print('\n[dry-run] 未写库。确认无误后加 --apply')
        return

    # 回滚备份
    backup = os.path.join(ROOT, 'tools/.knowledge-backup-%d.json' % int(time.time()))
    with open(backup, 'w', encoding='utf-8') as f:
        json.dump({str(k): o for k, _, o, _ in plan}, f, ensure_ascii=False, indent=2)
    print('\n已备份原内容 -> %s' % os.path.basename(backup))

    # 连接默认非 autocommit，必须显式提交
    n = 0
    with connection() as conn:
        try:
            with conn.cursor() as cur:
                for kid, name, old, new in plan:
                    cur.execute('UPDATE knowledge SET content = %s WHERE id = %s', (new, kid))
                    n += 1
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    print('已更新 %d 个知识点' % n)


if __name__ == '__main__':
    main()
