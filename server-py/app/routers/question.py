"""题库接口：按知识点取题 / 随机组卷 / 提交判分 / 主观题 Agent 判分。"""

import json

from fastapi import APIRouter, Depends, Request

from app.agent.grading import grade
from app.agent import memory_vec
from app.core.body import body_of
from app.core.deps import current_user, optional_user
from app.core.response import fail, ok
from app.db import query, query_one
from app.utils.num import round_half_up
from app.utils.validate import (clamp_text, is_answer_correct, is_id, to_array,
                                to_int, to_js_string)

router = APIRouter()

ALLOWED_TYPES = ['single', 'judge', 'multi', 'case', 'programming']


def _parse_options(raw):
    try:
        return json.loads(raw) if raw else []
    except Exception:
        return []


def note_wrong(user_id, q: dict, answer: str, correct: bool):
    """判分后给 Agent 的长期记忆留一条语义笔记。

    错了才记：题干 + 你的答案 + 正确答案 + 解析一起存，
    以后问到类似的点，助手能按"意思相近"把这条翻出来 —— 记住的是毛病，不是次数。
    答对了反而要把旧的删掉：已经攻克了，就不该再被当成薄弱点。

    记忆是增强项，这里任何异常都不许冒泡到判分流程。
    """
    try:
        if correct:
            memory_vec.remove_ref(user_id, 'wrong', q.get('id'))
            return
        k = query_one('SELECT name FROM knowledge WHERE id = ?', [q.get('knowledge_id')])
        parts = [
            '【题干】' + str(q.get('title') or q.get('content') or '')[:600],
            '【我的答案】' + str(answer or '')[:200],
            '【正确答案】' + str(q.get('answer') or '')[:200],
        ]
        if q.get('analysis'):
            parts.append('【解析】' + str(q['analysis'])[:400])
        memory_vec.add(
            user_id, 'wrong', '\n'.join(parts),
            ref_id=q.get('id'),
            knowledge_id=q.get('knowledge_id'),
            title=(k or {}).get('name') or '',
        )
    except Exception:
        pass


@router.get('/by-knowledge/{kid}')
def by_knowledge(request: Request, kid: str, source: str = None, difficulty: str = None,
                 type: str = None, mastery: str = None,
                 user: dict = Depends(optional_user)):
    if not is_id(kid):
        return fail(400, '知识点参数不合法')

    sql = ('SELECT id, knowledge_id, source, difficulty, type, title, options, score '
           'FROM question WHERE knowledge_id = ?')
    params = [kid]
    if source and source != 'all':
        sql += ' AND source = ?'
        params.append(str(source)[:32])
    try:
        diff = int(difficulty)
    except (TypeError, ValueError):
        diff = None
    if diff is not None and 1 <= diff <= 5 and str(difficulty).strip() != '':
        sql += ' AND difficulty = ?'
        params.append(diff)
    # 题型白名单：避免把任意字符串拼进查询
    if type and type != 'all' and str(type) in ALLOWED_TYPES:
        sql += ' AND type = ?'
        params.append(str(type))
    # 掌握状态筛选：把「这套题里还有哪些不会」变成一次点击。
    # 未登录时 user 为 None —— 没有答题记录就谈不上掌握，忽略该条件返回全部。
    if user and user.get('id'):
        if mastery == 'wrong':
            # 只看错题本里的题
            sql += ' AND id IN (SELECT question_id FROM wrong_question WHERE user_id = ?)'
            params.append(user['id'])
        elif mastery == 'unmastered':
            # 只看未掌握：从来没有答对过的题 = 错题 + 还没做过的题
            sql += (' AND id NOT IN (SELECT question_id FROM answer_record '
                    'WHERE user_id = ? AND is_correct = 1)')
            params.append(user['id'])
    sql += ' ORDER BY id'

    rows = query(sql, params)
    return ok([dict(q, options=_parse_options(q.get('options'))) for q in rows.rows])


@router.get('/bank')
def bank(page: str = None, size: str = None, course: str = None, type: str = None,
         difficulty: str = None, keyword: str = None):
    """题库：全站练习题集中检索（题库页用）。浏览不需登录，与 by-knowledge 一致。

    返回 list + total + courses（带题量的课程分类，给筛选栏用）。与 Node 端逐条对齐。
    """
    page_n = to_int(page, 1, 10 ** 6, 1)
    size_n = to_int(size, 1, 50, 12)
    course_n = to_int(course, 0, 10 ** 6, 0)
    diff_n = to_int(difficulty, 0, 5, 0)
    kw = (keyword or '').strip()[:50]

    conds = []
    params = []
    if course_n > 0:
        conds.append('c.id = ?')
        params.append(course_n)
    if type and str(type) in ALLOWED_TYPES:
        conds.append('q.type = ?')
        params.append(str(type))
    if diff_n >= 1:
        conds.append('q.difficulty = ?')
        params.append(diff_n)
    if kw:
        conds.append('q.title LIKE ?')
        params.append('%' + kw + '%')
    where_sql = (' WHERE ' + ' AND '.join(conds)) if conds else ''
    base = (' FROM question q JOIN knowledge k ON q.knowledge_id = k.id '
            'JOIN course c ON k.course_id = c.id ')

    total_row = query_one('SELECT COUNT(*) AS n' + base + where_sql, params)
    rows = query(
        'SELECT q.id, q.type, q.title, q.source, q.difficulty, q.knowledge_id, q.score,'
        ' k.name AS knowledge_name, c.id AS course_id, c.name AS course_name, c.category'
        + base + where_sql + ' ORDER BY c.sort_no, k.sort_no, q.id LIMIT ? OFFSET ?',
        params + [size_n, (page_n - 1) * size_n],
    ).rows
    course_rows = query(
        'SELECT c.id, c.name, c.category, COUNT(q.id) AS count' + base +
        ' GROUP BY c.id, c.name, c.category, c.sort_no ORDER BY c.sort_no',
    ).rows
    return ok({
        'total': int(total_row['n']) if total_row else 0,
        'list': rows,
        'courses': course_rows,
    })


@router.get('/paper/random')
def random_paper(courseId: str = None, limit: str = None, source: str = None, difficulty: str = None):
    # limit 必须收敛为 1~100 的整数：它是唯一直接拼进 SQL 的值
    limit_n = to_int(limit, 1, 100, 10)
    sql = 'SELECT id, knowledge_id, source, difficulty, type, title, options, score FROM question'
    params = []
    conds = []
    if courseId:
        if not is_id(courseId):
            return fail(400, '课程参数不合法')
        conds.append('knowledge_id IN (SELECT id FROM knowledge WHERE course_id = ?)')
        params.append(courseId)
    if source and source != 'all':
        conds.append('source = ?')
        params.append(str(source)[:32])
    try:
        diff = int(difficulty) if difficulty is not None and str(difficulty).strip() != '' else None
    except ValueError:
        diff = None
    if diff is not None and 1 <= diff <= 5:
        conds.append('difficulty = ?')
        params.append(diff)
    if conds:
        sql += ' WHERE ' + ' AND '.join(conds)
    sql += f' ORDER BY RAND() LIMIT {limit_n}'

    rows = query(sql, params)
    return ok([dict(q, options=_parse_options(q.get('options'))) for q in rows.rows])


@router.post('/submit')
def submit(request: Request, user: dict = Depends(current_user)):
    body = body_of(request)
    question_id = body.get('questionId')
    answer = body.get('answer')
    if not question_id:
        return fail(400, '缺少题目ID')
    if not is_id(question_id):
        return fail(400, '题目参数不合法')

    # 答案先收紧：对象/数组转字符串、超长截断，避免写入时报 Data too long。
    # 必须走 to_js_string：多选题传数组，Python 的 str(['A','B']) 会得到 "['A', 'B']"，
    # 与库里的标准答案 'A,B' 对不上，会导致判分恒为错。
    answer = to_js_string(answer)
    if answer.strip() == '':
        return fail(400, '请先选择一个答案再提交')
    answer = clamp_text(answer, 100)

    q = query_one('SELECT * FROM question WHERE id = ?', [question_id])
    if not q:
        return fail(404, '题目不存在')

    # 判断题存在 A/B 与 T/F 两套历史写法，这里跨写法互认
    correct = is_answer_correct(q.get('answer'), answer, q.get('type'))

    query(
        'INSERT INTO answer_record (user_id, question_id, user_answer, is_correct) VALUES (?, ?, ?, ?)',
        [user['id'], question_id, answer, 1 if correct else 0],
    )
    if not correct:
        query(
            'INSERT INTO wrong_question (user_id, question_id, wrong_count, last_wrong_time) '
            'VALUES (?, ?, 1, NOW()) '
            'ON DUPLICATE KEY UPDATE wrong_count = wrong_count + 1, last_wrong_time = NOW()',
            [user['id'], question_id],
        )
    else:
        query('DELETE FROM wrong_question WHERE user_id = ? AND question_id = ?', [user['id'], question_id])
    note_wrong(user['id'], q, answer, correct)

    query(
        "INSERT INTO study_record (user_id, knowledge_id, event_type, visit_count) VALUES (?, ?, 'quiz', 1) "
        'ON DUPLICATE KEY UPDATE visit_count = visit_count + 1, last_time = NOW()',
        [user['id'], q['knowledge_id']],
    )

    return ok({
        'correct': correct,
        'answer': q.get('answer'),
        'analysis': q.get('analysis'),
        'options': _parse_options(q.get('options')),
        'knowledgeId': q['knowledge_id'],
    })


@router.post('/submit-paper')
def submit_paper(request: Request, user: dict = Depends(current_user)):
    raw = body_of(request).get('answers')
    # [{questionId, answer}] —— 必须是数组，元素必须是对象，否则直接拒绝，不进循环
    if raw is not None and not isinstance(raw, list):
        return fail(400, '提交格式不正确，answers 应为数组')
    answers = to_array(raw or [])

    correct_count = 0
    details = []
    for item in answers:
        if not is_id(item.get('questionId')):
            continue
        q = query_one('SELECT * FROM question WHERE id = ?', [item.get('questionId')])
        if not q:
            continue
        ans = clamp_text(item.get('answer'), 100)
        correct = is_answer_correct(q.get('answer'), ans, q.get('type'))
        if correct:
            correct_count += 1
        query(
            'INSERT INTO answer_record (user_id, question_id, user_answer, is_correct) VALUES (?, ?, ?, ?)',
            [user['id'], item.get('questionId'), ans, 1 if correct else 0],
        )
        if not correct:
            query(
                'INSERT INTO wrong_question (user_id, question_id, wrong_count, last_wrong_time) '
                'VALUES (?, ?, 1, NOW()) '
                'ON DUPLICATE KEY UPDATE wrong_count = wrong_count + 1, last_wrong_time = NOW()',
                [user['id'], item.get('questionId')],
            )
        else:
            query('DELETE FROM wrong_question WHERE user_id = ? AND question_id = ?',
                  [user['id'], item.get('questionId')])
        note_wrong(user['id'], q, ans, correct)
        details.append({
            'questionId': q['id'],
            'correct': correct,
            'answer': q.get('answer'),
            'analysis': q.get('analysis'),
        })

    return ok({
        'total': len(answers),
        'correctCount': correct_count,
        'score': round_half_up(correct_count / (len(answers) or 1) * 100),
        'details': details,
    })


@router.get('/ranking')
def ranking(size: str = None, user: dict = Depends(optional_user)):
    """题库刷题排行榜。

    计分规则与算法榜对齐但换了一套口径：同一道题只算一次分（首次答对即入账），
    重复做不再加分，否则反复点提交就能刷榜。
    分值直接取 question.score —— 题目本身分值越高，榜上权重就越大。
    """
    size_n = to_int(size, 1, 100, 50)

    # best 子查询把「同一用户同一题」压成一行，只留 is_correct = 1 的记录。
    # 所以 HAVING 过滤的是 solved_count > 0（至少答对过一题），而不是答题数 > 0。
    rows = query(
        'SELECT u.id AS user_id, u.username, u.real_name, '
        'COALESCE(SUM(b.q_score), 0) AS total_score, '
        'COUNT(b.question_id) AS solved_count, '
        'COALESCE(SUM(b.q_difficulty), 0) AS total_difficulty '
        'FROM user u LEFT JOIN ( '
        '  SELECT r.user_id, r.question_id, MIN(r.created_at) AS first_at, '
        '         COALESCE(q.score, 0) AS q_score, '
        '         COALESCE(q.difficulty, 0) AS q_difficulty '
        '  FROM answer_record r JOIN question q ON q.id = r.question_id '
        "  WHERE r.is_correct = 1 GROUP BY r.user_id, r.question_id "
        ') b ON b.user_id = u.id '
        'GROUP BY u.id, u.username, u.real_name '
        'HAVING solved_count > 0 '
        f'ORDER BY total_score DESC, solved_count DESC, u.id ASC LIMIT {size_n}'
    )

    ranked = [{
        'rank': i + 1,
        'userId': r['user_id'],
        'username': r['username'],
        'realName': r['real_name'] or r['username'],
        'totalScore': int(r['total_score'] or 0),
        'solvedCount': int(r['solved_count'] or 0),
        'totalDifficulty': int(r['total_difficulty'] or 0),
    } for i, r in enumerate(rows.rows)]

    me = None
    if user and user.get('id'):
        hit = next((x for x in ranked if x['userId'] == user['id']), None)
        if hit:
            me = hit
        else:
            # 没进前 N：单独算自己的分数和「前面有几个人」，否则用户看不到自己排在哪
            row = query_one(
                'SELECT COALESCE(SUM(b.q_score), 0) AS total_score, '
                'COUNT(b.question_id) AS solved_count, '
                'COALESCE(SUM(b.q_difficulty), 0) AS total_difficulty '
                'FROM ( '
                '  SELECT r.question_id, COALESCE(q.score, 0) AS q_score, '
                '         COALESCE(q.difficulty, 0) AS q_difficulty '
                '  FROM answer_record r JOIN question q ON q.id = r.question_id '
                '  WHERE r.user_id = ? AND r.is_correct = 1 '
                '  GROUP BY r.question_id'
                ') b',
                [user['id']],
            )
            my_score = int(row['total_score'] or 0) if row else 0
            better = query_one(
                'SELECT COUNT(*) AS c FROM ( '
                '  SELECT r.user_id, SUM(q.score) AS s FROM answer_record r '
                '  JOIN question q ON q.id = r.question_id '
                '  WHERE r.is_correct = 1 GROUP BY r.user_id, r.question_id '
                ') x WHERE x.s > ?',
                [my_score],
            )
            me = {
                'rank': int(better['c'] or 0) + 1,
                'userId': user['id'],
                'username': user.get('username') or '',
                'realName': user.get('real_name') or user.get('username') or '',
                'totalScore': my_score,
                'solvedCount': int(row['solved_count'] or 0) if row else 0,
                'totalDifficulty': int(row['total_difficulty'] or 0) if row else 0,
            }

    return ok({'list': ranked, 'me': me})


@router.post('/grade')
def grade_subjective(request: Request, user: dict = Depends(current_user)):
    """主观题（案例分析 / 编程题）提交 —— 交给 Agent 智能判分。"""
    body = body_of(request)
    question_id = body.get('questionId')
    answer = body.get('answer')
    if not is_id(question_id):
        return fail(400, '题目参数不合法')

    ans = clamp_text(answer, 8000).strip()
    if not ans:
        return fail(400, '请先写下你的作答再提交')
    if len(ans) < 2:
        return fail(400, '作答太短了，至少写清楚你的思路')

    q = query_one('SELECT * FROM question WHERE id = ?', [question_id])
    if not q:
        return fail(404, '题目不存在')
    if q.get('type') not in ('case', 'programming'):
        return fail(400, '该题型为客观题，请使用普通提交方式')

    try:
        result = grade(q, ans)
    except Exception as e:
        return fail(500, '判分失败：' + str(e))

    # 得分率 60% 以上算掌握，低于则进错题本
    max_score = result.get('maxScore') or 0
    correct = max_score > 0 and (result.get('score') or 0) / max_score >= 0.6

    query(
        'INSERT INTO answer_record (user_id, question_id, user_answer, is_correct) VALUES (?, ?, ?, ?)',
        # 主观题作答要完整保存，用户需要回看自己当时写了什么；字段已扩为 TEXT
        [user['id'], question_id, ans, 1 if correct else 0],
    )
    if not correct:
        query(
            'INSERT INTO wrong_question (user_id, question_id, wrong_count, last_wrong_time) '
            'VALUES (?, ?, 1, NOW()) '
            'ON DUPLICATE KEY UPDATE wrong_count = wrong_count + 1, last_wrong_time = NOW()',
            [user['id'], question_id],
        )
    note_wrong(user['id'], q, ans, correct)

    return ok({
        'questionId': int(question_id),
        'type': result.get('type'),
        'score': result.get('score'),
        'maxScore': max_score,
        'correct': correct,
        'mode': result.get('mode'),
        'reasoning': result.get('reasoning'),
        'hits': result.get('hits'),
        'misses': result.get('misses'),
        'errors': result.get('errors'),
        'suggestions': result.get('suggestions'),
        'comment': result.get('comment'),
        'cheat': result.get('cheat'),
        # 判完后才给参考答案，避免先看答案再提交
        'referenceAnswer': q.get('reference_answer') or '',
    })
