"""个人学习中心：学习进度 / 错题本 / 收藏 / 对话记录 / 薄弱点诊断。"""

import json

from fastapi import APIRouter, Depends

from app.core.deps import current_user
from app.core.pagination import paginate
from app.core.response import fail, ok
from app.db import query, query_one
from app.utils.validate import is_id, to_int

router = APIRouter()

# 个人中心列表分页上限：单页最多 100 条（弹窗卡片式列表，比管理表格吃渲染）
PROFILE_MAX_PAGE_SIZE = 100


@router.get('/overview')
def overview(page: int = 0, pageSize: int = 0, user: dict = Depends(current_user)):
    uid = user['id']
    knowledge_total = query_one('SELECT COUNT(*) AS c FROM knowledge')
    studied = query_one('SELECT COUNT(DISTINCT knowledge_id) AS c FROM study_record WHERE user_id = ?', [uid])
    favorites = query_one('SELECT COUNT(*) AS c FROM favorite WHERE user_id = ?', [uid])
    wrongs = query_one('SELECT COUNT(*) AS c FROM wrong_question WHERE user_id = ?', [uid])
    chats = query_one('SELECT COUNT(*) AS c FROM chat_record WHERE user_id = ?', [uid])
    answers = query_one(
        'SELECT COUNT(*) AS total, SUM(is_correct) AS correct FROM answer_record WHERE user_id = ?',
        [uid],
    )
    progress_rows = list(query(
        'SELECT c.id, c.name, c.category, '
        '(SELECT COUNT(*) FROM knowledge k WHERE k.course_id = c.id) AS total, '
        '(SELECT COUNT(DISTINCT sr.knowledge_id) FROM study_record sr '
        'JOIN knowledge k2 ON k2.id = sr.knowledge_id '
        'WHERE sr.user_id = ? AND k2.course_id = c.id) AS done '
        'FROM course c ORDER BY c.sort_no',
        [uid],
    ).rows)

    # 学习进度分页：progress 一次查全量后本地切片（课程就十几行，COUNT 反而多余）；
    # courseProgressTotal 恒回传 —— 前端分页栏要靠它算页数，与其它列表的 total 同义。
    progress_total = len(progress_rows)
    size = max(0, min(int(pageSize or 0), PROFILE_MAX_PAGE_SIZE))
    cur = max(1, int(page or 1))
    if size > 0:
        progress_rows = progress_rows[(cur - 1) * size: (cur - 1) * size + size]

    return ok({
        'knowledgeTotal': int(knowledge_total['c'] or 0) if knowledge_total else 0,
        'knowledgeStudied': int(studied['c'] or 0) if studied else 0,
        'favoriteCount': int(favorites['c'] or 0) if favorites else 0,
        'wrongCount': int(wrongs['c'] or 0) if wrongs else 0,
        'chatCount': int(chats['c'] or 0) if chats else 0,
        'answerTotal': int(answers['total'] or 0) if answers else 0,
        'answerCorrect': int(answers['correct'] or 0) if answers else 0,
        'courseProgress': progress_rows,
        'courseProgressTotal': progress_total,
    })


@router.get('/wrong')
def wrong_list(page: int = 0, pageSize: int = 0, user: dict = Depends(current_user)):
    where = (' FROM wrong_question w JOIN question q ON q.id = w.question_id '
             'JOIN knowledge k ON k.id = q.knowledge_id JOIN course c ON c.id = k.course_id '
             'WHERE w.user_id = ?')
    return paginate(
        where, [user['id']],
        'SELECT w.id, w.wrong_count, w.last_wrong_time, q.id AS question_id, q.title, q.options, '
        'q.answer, q.analysis, k.id AS knowledge_id, k.name AS knowledge_name, '
        'k.route AS knowledge_route, c.name AS course_name',
        ' ORDER BY w.last_wrong_time DESC', page, pageSize)


@router.get('/wrong/questions')
def wrong_questions(ids: str = None, kid: str = None, limit: str = None,
                    user: dict = Depends(current_user)):
    """错题重做：把错题本里的题还原成完整题目，跨知识点组成一套题。

    错题本此前只有「看答案」，没有一条「再做一遍」的路径 —— 这是它的闭环。
    只返回 user_id 命中的题，ids 里混进别人的题也取不到。
    """
    # 上限 200：错题再多，一次重做也消化不完，先按最近错的来
    size = to_int(limit, 1, 200, 200)
    sql = ('SELECT q.id, q.knowledge_id, q.source, q.difficulty, q.type, q.title, q.options, '
           'q.score, w.wrong_count, w.last_wrong_time, '
           'k.name AS knowledge_name, k.route AS knowledge_route, c.name AS course_name '
           'FROM wrong_question w '
           'JOIN question q ON q.id = w.question_id '
           'JOIN knowledge k ON k.id = q.knowledge_id '
           'JOIN course c ON c.id = k.course_id '
           'WHERE w.user_id = ?')
    params = [user['id']]
    if kid and is_id(kid):
        sql += ' AND q.knowledge_id = ?'
        params.append(kid)
    if ids:
        # 「重做本页」会带上页面上的题号白名单。逐个校验成数字后再拼 IN，
        # 拼进去的只有受控数字，没有注入面；一个都不合法就返回空集而不是全量。
        id_list = [s.strip() for s in str(ids).split(',') if is_id(s.strip())]
        if not id_list:
            return ok([])
        sql += ' AND q.id IN (' + ','.join(['?'] * len(id_list)) + ')'
        params.extend(id_list)
    # 最近错的排前面：刚错过的题印象还在，这时候重做效果最好
    sql += ' ORDER BY w.last_wrong_time DESC, q.id DESC LIMIT ?'
    params.append(size)

    rows = list(query(sql, params).rows)
    out = []
    for q in rows:
        d = dict(q)
        try:
            d['options'] = json.loads(d.get('options') or '[]')
        except Exception:
            d['options'] = []
        out.append(d)
    return ok(out)


@router.delete('/wrong/{question_id}')
def remove_wrong(question_id: str, user: dict = Depends(current_user)):
    if not is_id(question_id):
        return fail(400, '题目参数不合法')
    query('DELETE FROM wrong_question WHERE user_id = ? AND question_id = ?', [user['id'], question_id])
    return ok(message='已移除')


@router.get('/favorite')
def favorite_list(page: int = 0, pageSize: int = 0, user: dict = Depends(current_user)):
    where = (' FROM favorite f JOIN knowledge k ON k.id = f.knowledge_id '
             'JOIN course c ON c.id = k.course_id WHERE f.user_id = ?')
    return paginate(
        where, [user['id']],
        'SELECT f.id, k.id AS knowledge_id, k.name, k.summary, k.route, c.name AS course_name',
        ' ORDER BY f.created_at DESC', page, pageSize)


@router.post('/favorite/{kid}')
def toggle_favorite(kid: str, user: dict = Depends(current_user)):
    if not is_id(kid):
        return fail(400, '知识点参数不合法')
    k = query_one('SELECT id FROM knowledge WHERE id = ?', [kid])
    if not k:
        return fail(404, '知识点不存在')
    exist = query_one('SELECT id FROM favorite WHERE user_id = ? AND knowledge_id = ?', [user['id'], kid])
    if exist:
        query('DELETE FROM favorite WHERE id = ?', [exist['id']])
        return ok({'favorited': False}, message='已取消收藏')
    query('INSERT INTO favorite (user_id, knowledge_id) VALUES (?, ?)', [user['id'], kid])
    return ok({'favorited': True}, message='已收藏')


@router.get('/favorite/{kid}/status')
def favorite_status(kid: str, user: dict = Depends(current_user)):
    if not is_id(kid):
        return fail(400, '知识点参数不合法')
    exist = query_one('SELECT id FROM favorite WHERE user_id = ? AND knowledge_id = ?', [user['id'], kid])
    return ok({'favorited': bool(exist)})


@router.get('/chats')
def chat_history(page: int = 0, pageSize: int = 0, user: dict = Depends(current_user)):
    # 旧版写死 LIMIT 100，对话过百后新记录看不到；改走分页，不传参时返回全量
    return paginate(
        ' FROM chat_record WHERE user_id = ?', [user['id']],
        'SELECT id, question, answer, knowledge_id, created_at',
        ' ORDER BY created_at DESC', page, pageSize)


@router.get('/weak-points')
def weak_points(user: dict = Depends(current_user)):
    rows = query(
        'SELECT k.id AS knowledge_id, k.name, k.route, c.name AS course_name, COUNT(*) AS wrong_count '
        'FROM wrong_question w JOIN question q ON q.id = w.question_id '
        'JOIN knowledge k ON k.id = q.knowledge_id JOIN course c ON c.id = k.course_id '
        'WHERE w.user_id = ? GROUP BY k.id, k.name, k.route, c.name '
        'ORDER BY wrong_count DESC LIMIT 10',
        [user['id']],
    )
    return ok(list(rows.rows))
