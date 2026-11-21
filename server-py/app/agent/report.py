"""个性化学习报告：基于用户真实学习数据生成结构化报告与可读文本。"""

from datetime import datetime

from app.db import query, query_one
from app.utils.num import round_half_up


def collect(user_id):
    knowledge_total = query_one('SELECT COUNT(*) AS c FROM knowledge')
    studied = query_one('SELECT COUNT(DISTINCT knowledge_id) AS c FROM study_record WHERE user_id = ?', [user_id])
    answer_stat = query_one(
        'SELECT COUNT(*) AS total, SUM(is_correct) AS correct FROM answer_record WHERE user_id = ?',
        [user_id],
    )
    wrong_stat = query_one(
        'SELECT COUNT(*) AS c, SUM(wrong_count) AS total_wrong FROM wrong_question WHERE user_id = ?',
        [user_id],
    )
    chat_stat = query_one('SELECT COUNT(*) AS c FROM chat_record WHERE user_id = ?', [user_id])
    # 「错题知识点」应指「有错题的知识点个数」，而不是错题条数 —— 早先前端把
    # wrongCount（不同题目数）标成「错题知识点」，口径容易误读，这里补一个准确字段。
    wrong_knowledge = query_one(
        'SELECT COUNT(DISTINCT q.knowledge_id) AS c FROM wrong_question w '
        'JOIN question q ON q.id = w.question_id WHERE w.user_id = ?',
        [user_id],
    )
    by_course = query(
        'SELECT c.name AS course_name, COUNT(a.id) AS answer_total, SUM(a.is_correct) AS answer_correct, '
        'COUNT(DISTINCT q.knowledge_id) AS touched_knowledge '
        'FROM answer_record a JOIN question q ON q.id = a.question_id '
        'JOIN knowledge k ON k.id = q.knowledge_id JOIN course c ON c.id = k.course_id '
        'WHERE a.user_id = ? GROUP BY c.id, c.name ORDER BY answer_total DESC',
        [user_id],
    )
    weak_points = query(
        'SELECT k.id, k.name, k.route, c.name AS course_name, w.wrong_count '
        'FROM wrong_question w JOIN question q ON q.id = w.question_id '
        'JOIN knowledge k ON k.id = q.knowledge_id JOIN course c ON c.id = k.course_id '
        'WHERE w.user_id = ? ORDER BY w.wrong_count DESC, w.last_wrong_time DESC LIMIT 8',
        [user_id],
    )
    recent_answers = query(
        'SELECT a.is_correct, a.created_at, q.knowledge_id, k.name AS knowledge_name '
        'FROM answer_record a JOIN question q ON q.id = a.question_id '
        'JOIN knowledge k ON k.id = q.knowledge_id '
        'WHERE a.user_id = ? ORDER BY a.created_at DESC LIMIT 20',
        [user_id],
    )
    first_record = query_one('SELECT MIN(last_time) AS first_time FROM study_record WHERE user_id = ?', [user_id])

    answer_total = int(answer_stat['total'] or 0) if answer_stat else 0
    answer_correct = int(answer_stat['correct'] or 0) if answer_stat else 0
    accuracy = round_half_up(answer_correct / answer_total * 100) if answer_total else None

    courses = []
    for row in by_course.rows:
        total = int(row['answer_total'] or 0)
        correct = int(row['answer_correct'] or 0)
        rate = round_half_up(correct / total * 100) if total else 0
        courses.append({
            'courseName': row['course_name'],
            'answerTotal': total,
            'answerCorrect': correct,
            'accuracy': rate,
            'touchedKnowledge': int(row['touched_knowledge'] or 0),
            'mastery': '掌握较好' if rate >= 85 else '基本掌握' if rate >= 60 else ('需要加强' if rate > 0 else '未测试'),
        })

    # 优势知识点：答对且不在错题本里的
    wrong_ids = {w['id'] for w in weak_points.rows}
    strong_points = []
    for r in recent_answers.rows:
        if int(r['is_correct'] or 0) == 1 and r['knowledge_id'] not in wrong_ids:
            if not any(s['id'] == r['knowledge_id'] for s in strong_points):
                strong_points.append({'id': r['knowledge_id'], 'name': r['knowledge_name']})

    days = 0
    if first_record and first_record.get('first_time'):
        delta = datetime.now() - first_record['first_time']
        days = max(1, int(delta.total_seconds() // 86400) + (1 if delta.total_seconds() % 86400 else 0))

    return {
        'knowledgeTotal': int(knowledge_total['c'] or 0) if knowledge_total else 0,
        'studiedKnowledge': int(studied['c'] or 0) if studied else 0,
        'answerTotal': answer_total,
        'answerCorrect': answer_correct,
        'accuracy': accuracy,
        'wrongCount': int(wrong_stat['c'] or 0) if wrong_stat else 0,
        'wrongKnowledgeCount': int(wrong_knowledge['c'] or 0) if wrong_knowledge else 0,
        'wrongTotalTimes': int(wrong_stat['total_wrong'] or 0) if wrong_stat else 0,
        'chatCount': int(chat_stat['c'] or 0) if chat_stat else 0,
        'studyDays': days,
        'courses': courses,
        'weakPoints': [{
            'id': w['id'], 'name': w['name'], 'route': w['route'],
            'courseName': w['course_name'], 'wrongCount': int(w['wrong_count'] or 0),
        } for w in weak_points.rows],
        'strongPoints': strong_points[:5],
    }


def build_suggestions(data):
    tips = []
    if data['answerTotal'] == 0:
        tips.append('你还没有答题记录。建议先挑一个知识点看动画，再做 5 道配套题，建立第一轮反馈。')
        return tips
    if data['accuracy'] is not None and data['accuracy'] < 60:
        tips.append(f"当前正确率 {data['accuracy']}%，说明概念还没吃透。建议先回到可视化动画用「单步执行」慢速过一遍，再做题，不要急着刷量。")
    elif data['accuracy'] is not None and data['accuracy'] >= 85:
        tips.append(f"正确率 {data['accuracy']}%，基础扎实。建议挑战综合题和易错变式，或提前预习下一个知识点。")
    elif data['accuracy'] is not None:
        tips.append(f"正确率 {data['accuracy']}%，处于上升期。建议针对错题集中的知识点做专项突破。")

    if data['weakPoints']:
        top = '、'.join([f"「{w['name']}」(错 {w['wrongCount']} 次)" for w in data['weakPoints'][:3]])
        tips.append(f'优先攻克：{top}。每个都先看动画再做 5 道题，隔一天回来复刷。')
    else:
        tips.append('错题本是空的，很好。建议主动做几道陌生章节的题，检验真实掌握程度。')

    if data['studiedKnowledge'] < data['knowledgeTotal'] * 0.3:
        tips.append(f"你只接触了 {data['studiedKnowledge']}/{data['knowledgeTotal']} 个知识点，覆盖面还比较窄，建议按课程目录系统推进。")

    candidates = [c for c in data['courses'] if c['answerTotal'] >= 3]
    if candidates:
        weak_course = sorted(candidates, key=lambda x: x['accuracy'])[0]
        tips.append(f"四门课里「{weak_course['courseName']}」正确率最低（{weak_course['accuracy']}%），建议本周重点投入。")

    tips.append('每天固定 20 分钟回顾错题本，比一次性刷 100 道新题更有效。')
    return tips


def generate(user_id):
    data = collect(user_id)
    data.update({'suggestions': build_suggestions(data), 'generatedAt': datetime.now().isoformat()})
    return data


def render_markdown(report):
    lines = []
    lines.append('## 📊 你的个性化学习报告')
    lines.append('')
    lines.append('生成时间：' + datetime.fromisoformat(report['generatedAt']).strftime('%Y/%m/%d %H:%M:%S'))
    lines.append('')
    lines.append('### 一、整体概览')
    lines.append('')
    lines.append('| 指标 | 数值 |')
    lines.append('|---|---|')
    lines.append(f"| 已学习知识点 | {report['studiedKnowledge']} / {report['knowledgeTotal']} |")
    lines.append(f"| 累计答题 | {report['answerTotal']} 题 |")
    lines.append(f"| 答对 | {report['answerCorrect']} 题 |")
    lines.append('| 正确率 | ' + ('暂无数据' if report['accuracy'] is None else f"{report['accuracy']}%") + ' |')
    lines.append(f"| 错题本题目 | {report['wrongCount']} 题（累计错 {report['wrongTotalTimes']} 次） |")
    lines.append(f"| 向 Agent 提问 | {report['chatCount']} 次 |")
    lines.append(f"| 学习天数 | {report['studyDays']} 天 |")
    lines.append('')

    if report['courses']:
        lines.append('### 二、各课程掌握情况')
        lines.append('')
        lines.append('| 课程 | 答题数 | 正确率 | 判定 |')
        lines.append('|---|---|---|---|')
        for c in report['courses']:
            lines.append(f"| {c['courseName']} | {c['answerTotal']} | {c['accuracy']}% | {c['mastery']} |")
        lines.append('')

    lines.append('### 三、薄弱知识点（来自错题本）')
    lines.append('')
    if report['weakPoints']:
        for i, w in enumerate(report['weakPoints']):
            lines.append(f"{i + 1}. **{w['courseName']} / {w['name']}** —— 错 {w['wrongCount']} 次")
        lines.append('')
        lines.append('> 点开对应可视化动画，用单步执行看清楚每一步，再回来刷题。')
    else:
        lines.append('暂无错题记录，保持住 👍')
    lines.append('')

    if report['strongPoints']:
        lines.append('### 四、表现较好的知识点')
        lines.append('')
        lines.append('\n'.join([f"· {s['name']}" for s in report['strongPoints']]))
        lines.append('')

    lines.append('### 五、下一步建议')
    lines.append('')
    for i, s in enumerate(report['suggestions']):
        lines.append(f'{i + 1}. {s}')
    lines.append('')
    lines.append('---')
    lines.append('需要我针对其中某一个知识点展开讲解，并打开对应动画吗？直接说名字就行 🙂')

    return '\n'.join(lines)
