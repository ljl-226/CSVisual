"""Agent 记忆模块（Memory）：短期 / 长期 / 用户画像 + 查看与清空。

- 短期记忆：最近几轮对话（chat_record），回答追问时用来做指代消解；
- 长期记忆：错题分布与掌握较好的知识点，跨会话长期有效；
- 用户画像：学习天数、答题量、正确率、常问课程 —— 让回答能"因人而异"。
"""

from app.agent import report as report_mod
from app.agent import memory_vec
from app.db import query, query_one

SHORT_TURNS = 5


def short_term(user_id, limit: int = SHORT_TURNS):
    """最近 N 轮问答（倒序取回后正序返回）"""
    rows = query(
        'SELECT cr.id, cr.session_id, cr.question, cr.answer, cr.intent, cr.mode, cr.created_at, '
        'k.name AS knowledge_name '
        'FROM chat_record cr LEFT JOIN knowledge k ON k.id = cr.knowledge_id '
        'WHERE cr.user_id = ? ORDER BY cr.id DESC LIMIT ?',
        [user_id, max(1, min(int(limit or SHORT_TURNS), 20))],
    )
    out = []
    for r in rows.rows:
        out.append({
            'id': r['id'],
            'sessionId': r['session_id'],
            'question': str(r['question'] or '')[:80],
            'answer': str(r['answer'] or '')[:120],
            'intent': r['intent'],
            'mode': r['mode'],
            'knowledge': r['knowledge_name'],
            'createdAt': str(r['created_at'] or ''),
        })
    return list(reversed(out))


def long_term(user_id, question: str = None):
    """跨会话长期记忆：薄弱点 + 优势点 + 覆盖面

    传了 question 会额外做一次语义召回（related）—— 聚合表按次数排，
    语义层按"和现在问的像不像"排，两者互补。
    """
    weak = query(
        'SELECT k.id, k.name, k.route, c.name AS course_name, SUM(w.wrong_count) AS wrong_count '
        'FROM wrong_question w JOIN question q ON q.id = w.question_id '
        'JOIN knowledge k ON k.id = q.knowledge_id JOIN course c ON c.id = k.course_id '
        'WHERE w.user_id = ? GROUP BY k.id, k.name, k.route, c.name '
        'ORDER BY wrong_count DESC LIMIT 8',
        [user_id],
    )
    strong = query(
        'SELECT k.id, k.name, k.route, COUNT(*) AS correct_count '
        'FROM answer_record a JOIN question q ON q.id = a.question_id '
        'JOIN knowledge k ON k.id = q.knowledge_id '
        'WHERE a.user_id = ? AND a.is_correct = 1 '
        'GROUP BY k.id, k.name, k.route ORDER BY correct_count DESC LIMIT 5',
        [user_id],
    )
    out = {
        'weakPoints': [{
            'id': r['id'], 'name': r['name'], 'route': r['route'],
            'courseName': r['course_name'], 'wrongCount': int(r['wrong_count'] or 0),
        } for r in weak.rows],
        'strongPoints': [{
            'id': r['id'], 'name': r['name'], 'route': r['route'],
            'correctCount': int(r['correct_count'] or 0),
        } for r in strong.rows],
    }
    if question:
        out['related'] = memory_vec.recall(user_id, question)
    return out


def portrait(user_id):
    """用户画像：一次查询给全，避免各处各查一遍"""
    u = query_one('SELECT real_name, username, created_at FROM user WHERE id = ?', [user_id])
    data = report_mod.collect(user_id)
    fav = query(
        'SELECT c.name AS course_name, COUNT(*) AS c FROM chat_record cr '
        'JOIN knowledge k ON k.id = cr.knowledge_id JOIN course c ON c.id = k.course_id '
        'WHERE cr.user_id = ? AND cr.knowledge_id IS NOT NULL '
        'GROUP BY c.id, c.name ORDER BY c DESC LIMIT 3',
        [user_id],
    )
    return {
        'name': (u or {}).get('real_name') or (u or {}).get('username') or '',
        'memberSince': str((u or {}).get('created_at') or ''),
        'studyDays': data.get('studyDays'),
        'answerTotal': data.get('answerTotal'),
        'accuracy': data.get('accuracy'),
        'chatCount': data.get('chatCount'),
        'studiedKnowledge': data.get('studiedKnowledge'),
        'knowledgeTotal': data.get('knowledgeTotal'),
        'favoriteCourses': [{'courseName': r['course_name'], 'count': int(r['c'] or 0)} for r in fav.rows],
    }


def profile(user_id, question: str = None):
    return {
        'shortTerm': short_term(user_id),
        'longTerm': long_term(user_id, question),
        'portrait': portrait(user_id),
        'semantic': memory_vec.stats(user_id),
    }


def related(user_id, question: str, top_k: int = 5):
    """按语义召回与「当前问题」相关的历史笔记（错题 / 问过的题）。

    这是长期记忆里"记内容"的那一半：聚合统计只说得出错得多不多，
    这里说得出来「你以前栽在哪个类似的点上」。
    """
    return memory_vec.recall(user_id, question, top_k)


def clear(user_id, scope: str = 'chat'):
    """清空记忆。

    - chat（默认）：只清对话记忆（chat_record / chat_session），学习数据不动；
    - all：连错题本一起清。答题记录与学习时长属于真实学习档案，不在这里删，
      避免"清空记忆"变成"抹掉学习历史"。
    """
    scope = str(scope or 'chat').lower()
    query('DELETE FROM chat_record WHERE user_id = ?', [user_id])
    query('DELETE FROM chat_session WHERE user_id = ?', [user_id])
    # 语义笔记里由对话产生的那些，跟着一起清
    memory_vec.remove_kind(user_id, 'chat')
    cleared = ['chatRecord', 'chatSession', 'chatNote']
    if scope == 'all':
        query('DELETE FROM wrong_question WHERE user_id = ?', [user_id])
        memory_vec.clear(user_id)
        cleared.append('wrongQuestion')
        cleared.append('memoryNote')
    return {'scope': scope, 'cleared': cleared}
