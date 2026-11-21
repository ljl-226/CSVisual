"""数据体检与修复脚本（幂等）。

背景：Node 版的边界测试会往库里插入伪造 ID（如 knowledge_id=99999999）的行，
部分用例还直接 UPDATE 了已有可视化的外键，跑完没清理，留下三类问题：

1. 孤儿行：knowledge.course_id / question.knowledge_id / visualization.knowledge_id
   指向不存在的父记录 —— 会让「知识点详情页」返回 404，前端出现空白卡片。
2. 外键被改写：可视化 35/36 的 knowledge_id 被改成了 99999999 / 110，
   导致「双向链表」「二叉排序树」两个知识点下的可视化消失（内容本身还在）。
3. 测试残留：name='x' 的假知识点、标题为「临时题」的假题目。

用法：
    python -m app.scripts.repair --dry-run   # 只报告，不改动
    python -m app.scripts.repair             # 执行修复
"""

import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db import connection, query, query_one  # noqa: E402

BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'backups')

# 已知被测试改写的外键，按种子文件 seed-core3.sql 的原始定义还原
# 格式：(表名, 主键, 外键列, 正确的外键值)
FK_FIXUPS = [
    ('visualization', 35, 'knowledge_id', 35),
    ('visualization', 36, 'knowledge_id', 36),
]


def _dump(rows, title):
    print(f'--- {title} ---')
    for r in rows:
        print('   ', json.dumps(r, ensure_ascii=False, default=str))
    if not rows:
        print('    (无)')
    print()


def scan():
    """扫出所有孤儿行与外键异常，返回结构化报告。"""
    report = {
        'orphan_knowledge': query(
            'SELECT k.id, k.name, k.course_id FROM knowledge k '
            'LEFT JOIN course c ON c.id = k.course_id WHERE c.id IS NULL').rows,
        'orphan_question': query(
            'SELECT q.id, q.title, q.knowledge_id FROM question q '
            'LEFT JOIN knowledge k ON k.id = q.knowledge_id WHERE k.id IS NULL').rows,
        'orphan_visualization': query(
            'SELECT v.id, v.title, v.knowledge_id FROM visualization v '
            'LEFT JOIN knowledge k ON k.id = v.knowledge_id WHERE k.id IS NULL').rows,
        'orphan_algorithm': query(
            'SELECT a.id, a.title, a.knowledge_id FROM algorithm a '
            'LEFT JOIN knowledge k ON k.id = a.knowledge_id '
            'WHERE a.knowledge_id IS NOT NULL AND k.id IS NULL').rows,
        'orphan_answer_record': query(
            'SELECT r.id, r.question_id FROM answer_record r '
            'LEFT JOIN question q ON q.id = r.question_id WHERE q.id IS NULL').rows,
        'orphan_wrong_question': query(
            'SELECT w.id, w.question_id FROM wrong_question w '
            'LEFT JOIN question q ON q.id = w.question_id WHERE q.id IS NULL').rows,
        'orphan_favorite': query(
            'SELECT f.id, f.knowledge_id FROM favorite f '
            'LEFT JOIN knowledge k ON k.id = f.knowledge_id WHERE k.id IS NULL').rows,
        'orphan_study_record': query(
            'SELECT s.id, s.knowledge_id FROM study_record s '
            'LEFT JOIN knowledge k ON k.id = s.knowledge_id WHERE k.id IS NULL').rows,
        'fk_mismatch': [],
    }

    for table, pk, col, right in FK_FIXUPS:
        row = query_one(f'SELECT id, `{col}` FROM `{table}` WHERE id = ?', [pk])
        if row and int(row[col] or 0) != right:
            report['fk_mismatch'].append({
                'table': table, 'id': pk, 'column': col,
                'current': row[col], 'expected': right,
            })
    return report


def _backup(report, dry_run: bool):
    """修复前把将被删除的行导出成 JSON，留作回滚依据。"""
    if all(not report[k] for k in report):
        return None
    os.makedirs(BACKUP_DIR, exist_ok=True)
    name = f'repair-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
    path = os.path.join(BACKUP_DIR, name)
    if not dry_run:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    return path


def repair(dry_run: bool = False, quiet: bool = False):
    """quiet=True 时只在真的有问题才打印（供服务启动时调用，避免每次启动刷屏）。"""
    report = scan()
    total = sum(len(v) for v in report.values())

    if total == 0:
        if not quiet:
            print('数据体检：未发现脏数据。')
        return {'changed': 0, 'report': report}

    print('=' * 60)
    print('数据体检报告' + ('（演练模式，不会改动数据库）' if dry_run else ''))
    print('=' * 60)
    for key, rows in report.items():
        _dump(rows, key)

    backup_path = _backup(report, dry_run)
    if backup_path:
        print(f'备份已写入: {backup_path}' if not dry_run else f'（演练）备份将写入: {backup_path}')

    if dry_run:
        print(f'演练结束：共发现 {total} 处问题，未做任何改动。')
        return {'changed': 0, 'report': report, 'backup': backup_path}

    changed = 0
    with connection() as conn:
        cur = conn.cursor()

        # 1. 先修外键：把被改写的外键还原回正确的父记录。
        #    关键：修完之后必须把这些 id 从孤儿清单里剔除 ——
        #    孤儿清单是修复前扫出来的，若照原样删会把刚救回来的行又删掉。
        restored = {(item['table'], item['id']) for item in report['fk_mismatch']}
        for item in report['fk_mismatch']:
            cur.execute(
                f"UPDATE `{item['table']}` SET `{item['column']}` = %s WHERE id = %s",
                [item['expected'], item['id']],
            )
            changed += cur.rowcount

        def _survivors(rows, table):
            return [r for r in rows if (table, r['id']) not in restored]

        report['orphan_visualization'] = _survivors(report['orphan_visualization'], 'visualization')
        report['orphan_question'] = _survivors(report['orphan_question'], 'question')
        report['orphan_knowledge'] = _survivors(report['orphan_knowledge'], 'knowledge')

        # 2. 再清孤儿行：从叶子表往父表删，避免残留引用
        for row in report['orphan_answer_record']:
            cur.execute('DELETE FROM answer_record WHERE id = %s', [row['id']])
            changed += cur.rowcount
        for row in report['orphan_wrong_question']:
            cur.execute('DELETE FROM wrong_question WHERE id = %s', [row['id']])
            changed += cur.rowcount
        for row in report['orphan_favorite']:
            cur.execute('DELETE FROM favorite WHERE id = %s', [row['id']])
            changed += cur.rowcount
        for row in report['orphan_study_record']:
            cur.execute('DELETE FROM study_record WHERE id = %s', [row['id']])
            changed += cur.rowcount

        # 孤儿题目可能还挂着答题/错题记录，先清干净再删题
        for row in report['orphan_question']:
            qid = row['id']
            cur.execute('DELETE FROM answer_record WHERE question_id = %s', [qid])
            cur.execute('DELETE FROM wrong_question WHERE question_id = %s', [qid])
            cur.execute('DELETE FROM question WHERE id = %s', [qid])
            changed += cur.rowcount

        for row in report['orphan_visualization']:
            cur.execute('DELETE FROM visualization WHERE id = %s', [row['id']])
            changed += cur.rowcount
        for row in report['orphan_algorithm']:
            cur.execute('DELETE FROM algorithm_submit WHERE algorithm_id = %s', [row['id']])
            cur.execute('DELETE FROM algorithm_case WHERE algorithm_id = %s', [row['id']])
            cur.execute('DELETE FROM algorithm WHERE id = %s', [row['id']])
            changed += cur.rowcount
        for row in report['orphan_knowledge']:
            kid = row['id']
            cur.execute('DELETE FROM study_record WHERE knowledge_id = %s', [kid])
            cur.execute('DELETE FROM favorite WHERE knowledge_id = %s', [kid])
            cur.execute('DELETE FROM knowledge WHERE id = %s', [kid])
            changed += cur.rowcount

        conn.commit()

    print(f'修复完成，共处理 {changed} 行。')
    after = scan()
    left = sum(len(v) for v in after.values())
    print(f'复检：剩余问题 {left} 处。')
    return {'changed': changed, 'report': report, 'backup': backup_path, 'remaining': left}


if __name__ == '__main__':
    repair(dry_run='--dry-run' in sys.argv)
