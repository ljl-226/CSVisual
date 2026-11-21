"""管理端接口：知识点 / 可视化案例 / 题库 / 算法题 / 统计 / 用户 / 安全日志。"""

import json
import re
import secrets

from fastapi import APIRouter, Depends, Request

from app.core.audit import LOG_DIR, log as audit_log
from app.core.body import body_of
from app.core.deps import admin_user
from app.core.pagination import paginate
from app.core.response import fail, ok
from app.core.security import gen_temp_password, hash_password
from app.core.shield import ip_of
from app.db import query, query_one
from app.utils.validate import (JUDGE_OPTIONS, clamp_text, exists, is_id,
                                normalize_judge_answer, to_bool_int,
                                to_js_string)
# 字段清单从学生侧复用，避免两处各写一份、加字段时只改一边
from app.routers.feedback import FEEDBACK_COLS, FEEDBACK_FROM

router = APIRouter(dependencies=[Depends(admin_user)])

ALLOWED_TYPES = ['single', 'judge', 'multi', 'case', 'programming']
SUBJECTIVE_TYPES = ['case', 'programming']

ALLOWED_SOURCES = ['基础', '考研408', '软考', 'NCRE', '期末', '编程语言']
DEFAULT_WEIGHT = {1: 10, 2: 10, 3: 20, 4: 30, 5: 50}


def normalize_type(t):
    """题型白名单（与数据库 ENUM 保持一致），并把常见写法归一化，避免非法值导致 500"""
    if not t:
        return 'single'
    v = str(t).lower()
    if v in ALLOWED_TYPES:
        return v
    if v in ['choice', 'radio', '单选', '单选题', 'single_choice']:
        return 'single'
    if v in ['judge', '判断题', '判断', 'tf', 'truefalse', 'boolean']:
        return 'judge'
    if v in ['multi', 'multiple', '多选', '多选题', 'checkbox']:
        return 'multi'
    if v in ['案例', '案例分析', '案例分析题', 'case_analysis']:
        return 'case'
    if v in ['编程', '编程题', '程序', 'code', 'coding']:
        return 'programming'
    return None


def normalize_points(raw):
    """校验并规范化评分要点：必须是 [{point, score}] 形式的数组"""
    if raw is None or raw == '':
        return {'ok': True, 'value': ''}
    arr = raw
    if isinstance(raw, str):
        try:
            arr = json.loads(raw)
        except Exception:
            return {'ok': False, 'why': '评分要点不是合法 JSON'}
    if not isinstance(arr, list):
        return {'ok': False, 'why': '评分要点必须是数组'}
    clean = []
    for p in arr:
        if not isinstance(p, dict):
            continue
        point = str(p.get('point') or p.get('text') or '').strip()
        try:
            score = float(p.get('score'))
        except (TypeError, ValueError):
            score = 0
        if point and score > 0:
            clean.append({'point': point, 'score': score})
    if not clean:
        return {'ok': False, 'why': '评分要点为空或缺少 point/score'}
    return {'ok': True, 'value': json.dumps(clean, ensure_ascii=False)}


def normalize_source(s):
    v = str(s or '基础').strip()
    return v if v in ALLOWED_SOURCES else '基础'


def build_update(mapping, body, transform=None):
    """构造「局部更新」SQL：只更新本次实际传入的字段。

    若把未传字段一并 SET，值会变成 NULL 覆盖原有数据。
    """
    transform = transform or {}
    sets = []
    params = []
    for key, col in mapping.items():
        if key not in body:
            continue
        val = body[key]
        sets.append(f'{col} = ?')
        params.append(transform[key](val) if key in transform else val)
    return {'sets': sets, 'params': params}


def check_id(id_value, table, label):
    """ID 合法性统一校验（管理端所有 :id 路由都要先过这道闸）"""
    if not is_id(id_value):
        return fail(400, f'{label}ID 不合法')
    if not exists(table, id_value):
        return fail(404, f'{label}不存在')
    return None


def current_type(id_value):
    row = query_one('SELECT type FROM question WHERE id = ?', [id_value])
    return row['type'] if row else None


# ================= 知识点管理 =================
# 列表分页骨架已抽到 app/core/pagination.py（learn 个人中心三个列表也共用）


@router.get('/knowledge')
def knowledge_list(courseId: str = None, keyword: str = None,
                   page: int = 0, pageSize: int = 0):
    where = (' FROM knowledge k JOIN course c ON c.id = k.course_id WHERE 1=1')
    params = []
    if courseId:
        where += ' AND k.course_id = ?'
        params.append(courseId)
    if keyword:
        where += ' AND (k.name LIKE ? OR k.summary LIKE ?)'
        params.extend([f'%{keyword}%', f'%{keyword}%'])
    return paginate(where, params,
                    'SELECT k.*, c.name AS course_name',
                    ' ORDER BY k.course_id, k.sort_no, k.id',
                    page, pageSize)


@router.post('/knowledge')
def knowledge_create(request: Request):
    body = body_of(request)
    course_id = body.get('courseId')
    name = body.get('name')
    summary = body.get('summary')
    content = body.get('content')
    route = body.get('route')
    sort_no = body.get('sortNo')
    if not course_id or not name:
        return fail(400, '课程和知识点名称必填')
    if not exists('course', course_id):
        return fail(404, '所属课程不存在')
    r = query(
        'INSERT INTO knowledge (course_id, name, summary, content, route, sort_no) VALUES (?, ?, ?, ?, ?, ?)',
        [course_id, name, summary or '', content or '', route or '', sort_no or 0],
    )
    return ok({'id': r.insert_id}, message='新增成功')


@router.put('/knowledge/{kid}')
def knowledge_update(kid: str, request: Request):
    err = check_id(kid, 'knowledge', '知识点')
    if err:
        return err
    body = body_of(request)
    if 'courseId' in body and not exists('course', body['courseId']):
        return fail(404, '所属课程不存在')
    upd = build_update({
        'courseId': 'course_id',
        'name': 'name',
        'summary': 'summary',
        'content': 'content',
        'route': 'route',
        'sortNo': 'sort_no',
    }, body)
    if not upd['sets']:
        return fail(400, '没有需要更新的字段')
    query(f"UPDATE knowledge SET {', '.join(upd['sets'])} WHERE id = ?", upd['params'] + [kid])
    return ok(message='保存成功')


@router.delete('/knowledge/{kid}')
def knowledge_delete(kid: str):
    err = check_id(kid, 'knowledge', '知识点')
    if err:
        return err
    # 级联清理：题目 → 错题/答题记录；可视化；收藏；学习记录
    qs = query('SELECT id FROM question WHERE knowledge_id = ?', [kid])
    qids = [q['id'] for q in qs.rows]
    if qids:
        placeholders = ','.join(['?'] * len(qids))
        query(f'DELETE FROM wrong_question WHERE question_id IN ({placeholders})', qids)
        query(f'DELETE FROM answer_record WHERE question_id IN ({placeholders})', qids)
        query('DELETE FROM question WHERE knowledge_id = ?', [kid])
    query('DELETE FROM visualization WHERE knowledge_id = ?', [kid])
    query('DELETE FROM favorite WHERE knowledge_id = ?', [kid])
    query('DELETE FROM study_record WHERE knowledge_id = ?', [kid])
    query('DELETE FROM knowledge WHERE id = ?', [kid])
    return ok(message='删除成功（已级联清理关联数据）')


# ================= 可视化案例管理 =================
@router.get('/visualization')
def visualization_list(page: int = 0, pageSize: int = 0):
    return paginate(' FROM visualization v LEFT JOIN knowledge k ON k.id = v.knowledge_id WHERE 1=1',
                    [],
                    'SELECT v.*, k.name AS knowledge_name',
                    ' ORDER BY v.id DESC',
                    page, pageSize)


@router.post('/visualization')
def visualization_create(request: Request):
    body = body_of(request)
    knowledge_id = body.get('knowledgeId')
    title = body.get('title')
    description = body.get('description')
    config = body.get('config')
    if not knowledge_id:
        return fail(400, '所属知识点必填')
    if not exists('knowledge', knowledge_id):
        return fail(404, '所属知识点不存在')
    if not title:
        return fail(400, '案例标题必填')
    r = query(
        'INSERT INTO visualization (knowledge_id, title, description, config) VALUES (?, ?, ?, ?)',
        [knowledge_id, title, description or '', json.dumps(config or {}, ensure_ascii=False)],
    )
    return ok({'id': r.insert_id}, message='新增成功')


@router.put('/visualization/{vid}')
def visualization_update(vid: str, request: Request):
    err = check_id(vid, 'visualization', '可视化案例')
    if err:
        return err
    body = body_of(request)
    if 'knowledgeId' in body and not exists('knowledge', body['knowledgeId']):
        return fail(404, '所属知识点不存在')
    upd = build_update({
        'knowledgeId': 'knowledge_id',
        'title': 'title',
        'description': 'description',
        'config': 'config',
    }, body, {'config': lambda v: json.dumps(v or {}, ensure_ascii=False)})
    if not upd['sets']:
        return fail(400, '没有需要更新的字段')
    query(f"UPDATE visualization SET {', '.join(upd['sets'])} WHERE id = ?", upd['params'] + [vid])
    return ok(message='保存成功')


@router.delete('/visualization/{vid}')
def visualization_delete(vid: str):
    query('DELETE FROM visualization WHERE id = ?', [vid])
    return ok(message='删除成功')


# ================= 题库管理 =================
@router.get('/question')
def question_list(courseId: str = None, knowledgeId: str = None, keyword: str = None,
                  page: int = 0, pageSize: int = 0):
    # 题库扩容到 1000+ 道后，写死的 LIMIT 500 会让管理员只看到「最新导入的 500 道」，
    # 早期导入的考研/软考/NCRE 真题在后台彻底搜不到。改为默认全量 + 可选分页，
    # 并把 total 一并返回（与 Node 后端保持一致）。
    where = (' FROM question q JOIN knowledge k ON k.id = q.knowledge_id '
             'JOIN course c ON c.id = k.course_id WHERE 1=1')
    params = []
    if knowledgeId:
        where += ' AND q.knowledge_id = ?'
        params.append(knowledgeId)
    if courseId:
        where += ' AND k.course_id = ?'
        params.append(courseId)
    if keyword:
        where += ' AND q.title LIKE ?'
        params.append(f'%{keyword}%')

    total = int(query_one('SELECT COUNT(*) AS total' + where, params)['total'] or 0)
    size = max(0, min(int(pageSize or 0), 2000))
    cur = max(1, int(page or 1))
    sql = ('SELECT q.*, k.name AS knowledge_name, c.name AS course_name' + where
           + ' ORDER BY q.id DESC')
    if size > 0:
        sql += ' LIMIT ? OFFSET ?'
        params = params + [size, (cur - 1) * size]
    rows = list(query(sql, params).rows)
    # data 仍是数组（与 Node 端、前端保持一致），分页信息平铺在顶层
    body = ok(rows)
    body['total'] = total
    body['page'] = cur
    body['pageSize'] = size or total
    return body


@router.post('/question')
def question_create(request: Request):
    body = body_of(request)
    knowledge_id = body.get('knowledgeId')
    qtype = body.get('type')
    title = body.get('title')
    options = body.get('options')
    answer = body.get('answer')
    analysis = body.get('analysis')
    score = body.get('score')
    source = body.get('source')
    difficulty = body.get('difficulty')
    reference_answer = body.get('referenceAnswer')
    grading_points = body.get('gradingPoints')

    if not knowledge_id or not title:
        return fail(400, '知识点、题干必填')
    normalized_type = normalize_type(qtype)
    if not normalized_type:
        return fail(400, f'题型不合法，可选：{" / ".join(ALLOWED_TYPES)}')

    # 主观题没有单一标准答案，判分依据是「参考答案 + 评分要点」
    is_subjective = normalized_type in SUBJECTIVE_TYPES
    points_text = ''
    if is_subjective:
        if grading_points is not None and grading_points != '':
            pts = normalize_points(grading_points)
            if not pts['ok']:
                return fail(400, '评分要点格式不正确：' + pts['why'])
            points_text = pts['value']
        if not str(reference_answer or '').strip() and not points_text:
            return fail(400, '案例分析题/编程题需要填写参考答案或评分要点，否则 Agent 无法判分')
    elif not answer:
        return fail(400, '客观题必须填写正确答案')

    if not exists('knowledge', knowledge_id):
        return fail(404, '所属知识点不存在')

    try:
        diff = int(difficulty)
    except (TypeError, ValueError):
        diff = None

    # 判断题统一为 A(正确)/B(错误) 并自动补选项，避免出现「判断题却没有选项可点」
    # 与 question.py 保持一致：数组答案按 JS 语义摊平成 'A,B'
    final_answer = to_js_string(answer or '').strip()
    final_options = json.dumps(options or [], ensure_ascii=False)
    if is_subjective:
        final_answer = ''
        final_options = '[]'
    elif normalized_type == 'judge':
        norm = normalize_judge_answer(answer)
        if not norm:
            return fail(400, '判断题答案应为：A/正确/T 或 B/错误/F')
        final_answer = norm
        final_options = JUDGE_OPTIONS

    try:
        final_score = int(score)
    except (TypeError, ValueError):
        final_score = None

    r = query(
        'INSERT INTO question (knowledge_id, source, difficulty, type, title, options, answer, analysis, '
        'reference_answer, grading_points, score) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        [
            knowledge_id,
            normalize_source(source),
            diff if (diff is not None and 1 <= diff <= 5) else 3,
            normalized_type,
            title,
            final_options,
            final_answer,
            analysis or '',
            str(reference_answer or ''),
            points_text,
            final_score if (final_score is not None and final_score > 0) else (10 if is_subjective else 5),
        ],
    )
    return ok({'id': r.insert_id}, message='新增成功')


@router.put('/question/{qid}')
def question_update(qid: str, request: Request):
    err = check_id(qid, 'question', '题目')
    if err:
        return err
    body = body_of(request)
    if 'knowledgeId' in body and not exists('knowledge', body['knowledgeId']):
        return fail(404, '所属知识点不存在')

    # 评分要点先校验再用：格式不对要给出明确原因，而不是写进库里让判分失灵
    points_text = ''
    if 'gradingPoints' in body:
        pts = normalize_points(body['gradingPoints'])
        if not pts['ok']:
            return fail(400, '评分要点格式不正确：' + pts['why'])
        points_text = pts['value']

    upd = build_update({
        'knowledgeId': 'knowledge_id',
        'source': 'source',
        'difficulty': 'difficulty',
        'type': 'type',
        'title': 'title',
        'options': 'options',
        'answer': 'answer',
        'analysis': 'analysis',
        'referenceAnswer': 'reference_answer',
        'gradingPoints': 'grading_points',
        'score': 'score',
    }, body, {
        'options': lambda v: json.dumps(v if isinstance(v, list) else [], ensure_ascii=False),
        'source': normalize_source,
        'gradingPoints': lambda v: points_text,
        'difficulty': lambda v: (int(v) if str(v).isdigit() and 1 <= int(v) <= 5 else 3),
    })
    if not upd['sets']:
        return fail(400, '没有需要更新的字段')

    final_type = None
    if 'type' in body:
        nt = normalize_type(body['type'])
        if not nt:
            return fail(400, f'题型不合法，可选：{" / ".join(ALLOWED_TYPES)}')
        final_type = nt
        idx = upd['sets'].index('type = ?')
        upd['params'][idx] = nt

    # 改成判断题 / 修改判断题答案时，同步规范答案与选项
    if (final_type or current_type(qid)) == 'judge' and 'answer' in body:
        norm = normalize_judge_answer(body['answer'])
        if not norm:
            return fail(400, '判断题答案应为：A/正确/T 或 B/错误/F')
        ai = upd['sets'].index('answer = ?')
        upd['params'][ai] = norm
        if 'options = ?' in upd['sets']:
            oi = upd['sets'].index('options = ?')
            upd['params'][oi] = JUDGE_OPTIONS
        else:
            upd['sets'].append('options = ?')
            upd['params'].append(JUDGE_OPTIONS)

    query(f"UPDATE question SET {', '.join(upd['sets'])} WHERE id = ?", upd['params'] + [qid])
    return ok(message='保存成功')


@router.delete('/question/{qid}')
def question_delete(qid: str):
    if not is_id(qid):
        return fail(400, '题目ID 不合法')
    # 先清错题本与答题记录，避免留下指向已删题目的孤儿数据
    query('DELETE FROM wrong_question WHERE question_id = ?', [qid])
    query('DELETE FROM answer_record WHERE question_id = ?', [qid])
    query('DELETE FROM question WHERE id = ?', [qid])
    return ok(message='删除成功')


# ================= 数据统计 =================
@router.get('/stats')
def stats():
    user_count = query_one('SELECT COUNT(*) AS c FROM user WHERE role = "student"')
    knowledge_count = query_one('SELECT COUNT(*) AS c FROM knowledge')
    question_count = query_one('SELECT COUNT(*) AS c FROM question')
    answer_stat = query_one('SELECT COUNT(*) AS total, SUM(is_correct) AS correct FROM answer_record')
    chat_count = query_one('SELECT COUNT(*) AS c FROM chat_record')
    by_course = query(
        'SELECT c.name, '
        '(SELECT COUNT(*) FROM knowledge k WHERE k.course_id = c.id) AS knowledge_count, '
        '(SELECT COUNT(*) FROM question q JOIN knowledge k2 ON k2.id = q.knowledge_id WHERE k2.course_id = c.id) AS question_count '
        'FROM course c ORDER BY c.sort_no'
    )
    top_wrong = query(
        'SELECT k.name, COUNT(*) AS c FROM wrong_question w '
        'JOIN question q ON q.id = w.question_id JOIN knowledge k ON k.id = q.knowledge_id '
        'GROUP BY k.id, k.name ORDER BY c DESC LIMIT 8'
    )
    active_users = query(
        'SELECT u.username, u.real_name, COUNT(DISTINCT sr.knowledge_id) AS studied, '
        '(SELECT COUNT(*) FROM answer_record a WHERE a.user_id = u.id) AS answers '
        "FROM user u LEFT JOIN study_record sr ON sr.user_id = u.id WHERE u.role = 'student' "
        'GROUP BY u.id ORDER BY answers DESC LIMIT 10'
    )

    return ok({
        'userCount': int(user_count['c'] or 0) if user_count else 0,
        'knowledgeCount': int(knowledge_count['c'] or 0) if knowledge_count else 0,
        'questionCount': int(question_count['c'] or 0) if question_count else 0,
        'answerTotal': int(answer_stat['total'] or 0) if answer_stat else 0,
        'answerCorrect': int(answer_stat['correct'] or 0) if answer_stat else 0,
        'chatCount': int(chat_count['c'] or 0) if chat_count else 0,
        'byCourse': list(by_course.rows),
        'topWrong': list(top_wrong.rows),
        'activeUsers': list(active_users.rows),
    })


# ================= 用户管理 =================
@router.get('/users')
def users(page: int = 0, pageSize: int = 0, q: str = ''):
    """q：按账号或姓名模糊搜索（后台用户多了以后翻页找人不现实）。"""
    where = ' FROM user u WHERE 1=1'
    args = []
    kw = str(q or '').strip()
    if kw:
        where += ' AND (u.username LIKE ? OR u.real_name LIKE ?)'
        args += ['%' + kw + '%', '%' + kw + '%']
    return paginate(where, args,
                    'SELECT u.id, u.username, u.real_name, u.role, u.created_at, '
                    '(SELECT COUNT(*) FROM answer_record a WHERE a.user_id = u.id) AS answer_count, '
                    '(SELECT COUNT(*) FROM wrong_question w WHERE w.user_id = u.id) AS wrong_count',
                    ' ORDER BY u.id DESC',
                    page, pageSize)


@router.post('/users/{uid}/reset-password')
def reset_user_password(request: Request, uid: int):
    """管理员帮学生重置密码：随机 8 位临时密码，返回明文由管理员线下告知。

    兜的是「姓名也忘了、自助找回走不通」的死锁 —— 自助链路的凭证只有
    姓名，兜底必须落在管理员手里。随机而不是统一重置成 123456：
    旧密码失效后若管理员忘了转告，弱默认密码等于把账号敞开。"""
    row = query_one('SELECT id, username FROM user WHERE id = ?', [uid])
    if not row:
        return fail(400, '用户不存在')
    alphabet = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    temp_pwd = ''.join(secrets.choice(alphabet) for _ in range(8))
    query('UPDATE user SET password = ? WHERE id = ?', [hash_password(temp_pwd), uid])
    audit_log('admin_reset_pwd', username=row.get('username'), id=uid,
              target=row.get('username'), ip=ip_of(request))
    return ok({'password': temp_pwd}, message='已重置密码')


# ================= 临时密码申请 =================
#
# 学生端在登录页提交「账号 + 电话」申请临时密码，到这里是一张待办工单。
# 管理员照着电话联系本人核身，点通过即完成两件事：密码当场重置为随机临时密码、
# 临时密码留在工单里等学生凭单号自取（弹窗同时展示一次，供线下转告）。
# 之所以要人工这一步：自助找回的凭证是姓名，姓名忘了就没有任何东西能证明
# 「你是这个账号的主人」了 —— 能兜住这件事的只有真人。
TEMP_PWD_STATUS = {'pending': '待处理', 'approved': '已通过', 'rejected': '已驳回', 'used': '已使用'}

# 处理完的自动关闭同一账号的其他待办：工单可能提交了多次，
# 只办最新一张就够了，其余留着只是让后台永远清不空
_AUTO_CLOSE_NOTE = '已由同一账号的其他申请处理完'


@router.get('/password-requests')
def admin_password_requests(status: str = None, q: str = None,
                            page: int = 0, pageSize: int = 0):
    """工单列表。搜索覆盖单号 / 账号 / 姓名 / 电话 —— 管理员手上往往只有其中一项。"""
    kw = str(q or '').strip()
    st = str(status or '').strip()
    where = ' FROM password_request r WHERE 1=1'
    params = []
    if st in TEMP_PWD_STATUS:
        where += ' AND r.status = ?'
        params.append(st)
    if kw:
        where += ' AND (r.ticket LIKE ? OR r.username LIKE ? OR r.real_name LIKE ? OR r.phone LIKE ?)'
        params += ['%' + kw + '%'] * 4
    select = ('SELECT r.id, r.ticket, r.user_id, r.username, r.real_name, r.phone, r.reason, '
              'r.status, r.temp_password, r.admin_id, r.admin_name, r.reject_reason, '
              'r.handled_at, r.created_at')
    # 待处理的排最前：管理员每天先要看到的是还没办的单子，不是办结的历史
    order = ' ORDER BY IF(r.status = \'pending\', 0, 1), r.created_at DESC'
    body = paginate(where, params, select, order, page, pageSize)
    # 临时密码明文只对「已通过」的工单有意义，其余一律不给前端，
    # 免得列表接口变成一份可读凭证清单
    for row in body['data']:
        if row.get('status') != 'approved':
            row['temp_password'] = ''
    body['pendingCount'] = int(
        query_one("SELECT COUNT(*) AS c FROM password_request WHERE status = 'pending'")['c'] or 0)
    return body


@router.post('/password-requests/{rid}/approve')
def approve_password_request(request: Request, rid: int, admin: dict = Depends(admin_user)):
    """通过：重置密码 + 把临时密码同时留给弹窗和「凭单号自取」。"""
    row = query_one(
        'SELECT r.id, r.ticket, r.user_id, r.username, r.status FROM password_request r WHERE r.id = ?', [rid])
    if not row:
        return fail(404, '申请不存在')
    # 一张工单只处理一次：用过了、驳回过的都是终态，要再发一份就该重新提交申请 ——
    # 否则翻看历史工单时误点一下，就把别人的密码又重置了一遍
    if row['status'] != 'pending':
        return fail(400, '该申请已处理过了')
    user = query_one('SELECT id FROM user WHERE id = ?', [row['user_id']])
    if not user:
        # 申请提交后账号被删了：与其报错让管理员干瞪眼，直接结单
        query("UPDATE password_request SET status = 'rejected', reject_reason = ?, "
              "admin_id = ?, admin_name = ?, handled_at = NOW() WHERE id = ?",
              ['账号已不存在', admin.get('id'), admin.get('username') or '', rid])
        return fail(400, '账号已不存在，申请已自动驳回')

    temp_pwd = gen_temp_password()
    query('UPDATE user SET password = ? WHERE id = ?', [hash_password(temp_pwd), row['user_id']])
    query('UPDATE password_request SET status = ?, temp_password = ?, admin_id = ?, '
          'admin_name = ?, reject_reason = \'\', handled_at = NOW() WHERE id = ?',
          ['approved', temp_pwd, admin.get('id'), admin.get('username') or '', rid])
    query("UPDATE password_request SET status = 'rejected', reject_reason = ?, "
          'admin_id = ?, admin_name = ?, handled_at = NOW() '
          "WHERE user_id = ? AND status = 'pending' AND id <> ?",
          [_AUTO_CLOSE_NOTE, admin.get('id'), admin.get('username') or '', row['user_id'], rid])
    audit_log('temp_pwd_approve', username=admin.get('username'), id=admin.get('id'),
              target=row['username'], ticket=row.get('ticket'), ip=ip_of(request))
    return ok({'password': temp_pwd, 'ticket': row.get('ticket')}, message='已通过并重置密码')


@router.post('/password-requests/{rid}/reject')
def reject_password_request(request: Request, rid: int, admin: dict = Depends(admin_user)):
    body = body_of(request)
    reason = str(body.get('reason') or '').strip()[:200]
    if not reason:
        return fail(400, '请填写驳回理由，方便学生知道为什么没通过')
    row = query_one('SELECT id, ticket, username, status FROM password_request WHERE id = ?', [rid])
    if not row:
        return fail(404, '申请不存在')
    if row['status'] != 'pending':
        return fail(400, '该申请已处理过了')
    query('UPDATE password_request SET status = ?, reject_reason = ?, admin_id = ?, '
          'admin_name = ?, handled_at = NOW() WHERE id = ?',
          ['rejected', reason, admin.get('id'), admin.get('username') or '', rid])
    audit_log('temp_pwd_reject', username=admin.get('username'), id=admin.get('id'),
              target=row['username'], ip=ip_of(request))
    return ok(message='已驳回')


# ================= 程序设计算法题管理 =================
ALGO_FIELD_MAP = {
    'title': 'title',
    'difficulty': 'difficulty',
    'weight': 'weight',
    'description': 'description',
    'inputDesc': 'input_desc',
    'outputDesc': 'output_desc',
    'sampleInput': 'sample_input',
    'sampleOutput': 'sample_output',
    'hints': 'hints',
    'referenceCode': 'reference_code',
    'referenceLanguage': 'reference_language',
    'tags': 'tags',
    'source': 'source',
    'knowledgeId': 'knowledge_id',
    'status': 'status',
}


@router.get('/algorithm')
def admin_algorithm_list(keyword: str = None, difficulty: str = None,
                         page: int = 0, pageSize: int = 0):
    where = (' FROM algorithm a LEFT JOIN knowledge k ON k.id = a.knowledge_id WHERE 1=1')
    params = []
    try:
        d = int(difficulty) if difficulty is not None and str(difficulty).strip() != '' else None
    except ValueError:
        d = None
    if d is not None and 1 <= d <= 5:
        where += ' AND a.difficulty = ?'
        params.append(d)
    kw = clamp_text(keyword, 40).strip()
    if kw:
        where += ' AND (a.title LIKE ? OR a.tags LIKE ?)'
        params.extend([f'%{kw}%', f'%{kw}%'])
    # 原来 ORDER BY 后写死 LIMIT 300：算法题涨过 300 道后，管理员翻不到第 300 条以后的题。
    # 改成分页（page/pageSize 不传仍返回全量，兼容旧调用），去掉硬截断。
    return paginate(where, params,
                    'SELECT a.id, a.title, a.difficulty, a.weight, a.tags, a.source, a.knowledge_id, '
                    'a.submit_count, a.accepted_count, a.status, a.created_at, k.name AS knowledge_name, '
                    '(SELECT COUNT(*) FROM algorithm_case c WHERE c.algorithm_id = a.id) AS case_count',
                    ' ORDER BY a.id DESC',
                    page, pageSize)


@router.get('/algorithm/{aid}')
def admin_algorithm_detail(aid: str):
    err = check_id(aid, 'algorithm', '算法题')
    if err:
        return err
    a = query_one('SELECT * FROM algorithm WHERE id = ?', [aid])
    cases = query(
        'SELECT id, stdin, expected, is_sample, sort_no FROM algorithm_case '
        'WHERE algorithm_id = ? ORDER BY sort_no, id',
        [aid],
    )
    data = dict(a)
    data['cases'] = list(cases.rows)
    return ok(data)


@router.post('/algorithm')
def admin_algorithm_create(request: Request):
    b = body_of(request)
    title = clamp_text(b.get('title'), 200).strip()
    description = clamp_text(b.get('description'), 20000).strip()
    if not title:
        return fail(400, '题目标题必填')
    if not description:
        return fail(400, '题面描述必填')
    if b.get('knowledgeId') and not exists('knowledge', b.get('knowledgeId')):
        return fail(404, '所属知识点不存在')

    try:
        d = int(b.get('difficulty'))
    except (TypeError, ValueError):
        d = None
    diff = d if (d is not None and 1 <= d <= 5) else 3
    try:
        w = int(b.get('weight'))
    except (TypeError, ValueError):
        w = None
    weight = w if (w is not None and w > 0) else DEFAULT_WEIGHT.get(diff, 20)

    r = query(
        'INSERT INTO algorithm (title, difficulty, weight, description, input_desc, output_desc, '
        'sample_input, sample_output, hints, reference_code, reference_language, tags, source, knowledge_id) '
        'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
        [
            title, diff, weight, description,
            clamp_text(b.get('inputDesc'), 2000), clamp_text(b.get('outputDesc'), 2000),
            clamp_text(b.get('sampleInput'), 4000), clamp_text(b.get('sampleOutput'), 4000),
            clamp_text(b.get('hints'), 4000), clamp_text(b.get('referenceCode'), 20000),
            clamp_text(b.get('referenceLanguage'), 16) or 'python',
            clamp_text(b.get('tags'), 200), normalize_source(b.get('source')),
            b.get('knowledgeId') or None,
        ],
    )
    return ok({'id': r.insert_id, 'weight': weight}, message='新增成功')


@router.put('/algorithm/{aid}')
def admin_algorithm_update(aid: str, request: Request):
    err = check_id(aid, 'algorithm', '算法题')
    if err:
        return err
    body = body_of(request)
    if body.get('knowledgeId') is not None and not exists('knowledge', body['knowledgeId']):
        return fail(404, '所属知识点不存在')

    def _difficulty(v):
        n = int(v) if str(v).isdigit() else 0
        return n if 1 <= n <= 5 else 3

    def _weight(v):
        n = int(v) if str(v).lstrip('-').isdigit() else 0
        return n if n > 0 else 10

    upd = build_update(ALGO_FIELD_MAP, body, {
        'source': normalize_source,
        'difficulty': _difficulty,
        'weight': _weight,
        'status': lambda v: to_bool_int(v),
    })
    if not upd['sets']:
        return fail(400, '没有需要更新的字段')
    query(f"UPDATE algorithm SET {', '.join(upd['sets'])} WHERE id = ?", upd['params'] + [aid])
    return ok(message='保存成功')


@router.delete('/algorithm/{aid}')
def admin_algorithm_delete(aid: str):
    if not is_id(aid):
        return fail(400, '题目ID 不合法')
    # 用例与提交记录一起清，避免留下指向已删题目的孤儿数据
    query('DELETE FROM algorithm_case WHERE algorithm_id = ?', [aid])
    query('DELETE FROM algorithm_submit WHERE algorithm_id = ?', [aid])
    query('DELETE FROM algorithm WHERE id = ?', [aid])
    return ok(message='删除成功')


# ---- 测试用例（单独一组路由，避免与 /algorithm/:id 路径混淆） ----
@router.get('/algorithm-cases')
def admin_case_list(algorithmId: str = None):
    if not is_id(algorithmId):
        return fail(400, '题目ID 不合法')
    rows = query(
        'SELECT id, algorithm_id, stdin, expected, is_sample, sort_no FROM algorithm_case '
        'WHERE algorithm_id = ? ORDER BY sort_no, id',
        [algorithmId],
    )
    return ok(list(rows.rows))


@router.post('/algorithm-cases')
def admin_case_create(request: Request):
    body = body_of(request)
    algorithm_id = body.get('algorithmId')
    stdin = body.get('stdin')
    expected = body.get('expected')
    is_sample = body.get('isSample')
    sort_no = body.get('sortNo')
    if not is_id(algorithm_id):
        return fail(400, '题目ID 不合法')
    if not exists('algorithm', algorithm_id):
        return fail(404, '算法题不存在')
    exp = str(expected if expected is not None else '')
    if not exp.strip():
        return fail(400, '期望输出必填，否则无法判分')
    try:
        sort_no_n = int(sort_no)
    except (TypeError, ValueError):
        sort_no_n = 0
    r = query(
        'INSERT INTO algorithm_case (algorithm_id, stdin, expected, is_sample, sort_no) VALUES (?,?,?,?,?)',
        [algorithm_id, str(stdin or ''), exp, to_bool_int(is_sample), sort_no_n],
    )
    return ok({'id': r.insert_id}, message='新增成功')


@router.put('/algorithm-cases/{cid}')
def admin_case_update(cid: str, request: Request):
    err = check_id(cid, 'algorithm_case', '测试用例')
    if err:
        return err
    upd = build_update({
        'stdin': 'stdin',
        'expected': 'expected',
        'isSample': 'is_sample',
        'sortNo': 'sort_no',
    }, body_of(request), {
        'isSample': lambda v: to_bool_int(v),
        'sortNo': lambda v: (int(v) if str(v).lstrip('-').isdigit() else 0),
    })
    if not upd['sets']:
        return fail(400, '没有需要更新的字段')
    query(f"UPDATE algorithm_case SET {', '.join(upd['sets'])} WHERE id = ?", upd['params'] + [cid])
    return ok(message='保存成功')


@router.delete('/algorithm-cases/{cid}')
def admin_case_delete(cid: str):
    if not is_id(cid):
        return fail(400, '用例ID 不合法')
    query('DELETE FROM algorithm_case WHERE id = ?', [cid])
    return ok(message='删除成功')


# ================= 安全日志 =================
# 日志文件名整体正则匹配：只认 security-YYYY-MM-DD.log，
# 目录里就算被塞了别的文件也读不进来（防路径遍历的日志版）。
SECURITY_LOG_NAME = re.compile(r'^security-\d{4}-\d{2}-\d{2}\.log$')


@router.get('/security-logs')
def security_logs(date: str = None, event: str = None, page: int = 0, pageSize: int = 0):
    """安全审计日志查询：读 logs/security-*.log（JSONL），按时间倒序分页。

    date / event 为可选筛选；响应里额外平铺 dates（有日志的日期）与
    events（出现过的日志事件类型），供前端筛选项直接使用。
    """
    records = []
    dates = []
    events = set()
    if LOG_DIR.is_dir():
        for p in sorted(LOG_DIR.glob('security-*.log'), reverse=True):
            if not SECURITY_LOG_NAME.match(p.name):
                continue
            day = p.name[len('security-'):-len('.log')]
            dates.append(day)
            if date and day != date:
                continue
            try:
                lines = p.read_text(encoding='utf-8').splitlines()
            except OSError:
                continue
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                # 半截行 / 非对象行直接跳过，不让一条坏行弄挂整个接口
                if isinstance(rec, dict) and rec.get('event'):
                    events.add(rec['event'])
                    if event and rec['event'] != event:
                        continue
                    records.append(rec)
    records.sort(key=lambda r: str(r.get('time', '')), reverse=True)

    total = len(records)
    size = max(0, min(int(pageSize or 0), 2000))
    cur = max(1, int(page or 1))
    rows = records[(cur - 1) * size: (cur - 1) * size + size] if size > 0 else records
    body = ok(rows)
    body['total'] = total
    body['page'] = cur
    body['pageSize'] = size or total
    body['dates'] = dates
    body['events'] = sorted(events)
    return body


# ==================== 用户反馈建议 ====================
# 学生提的 bug / 建议在这里集中处理。与学生侧分开的原因：
# 权限模型不同（这边要管理员），且管理员需要跨用户筛选与统计。
FEEDBACK_TYPES = ['bug', 'feature', 'experience', 'other']
FEEDBACK_STATUS = ['pending', 'processing', 'resolved', 'closed']
# 与 feedback.py 同一份约定：paginate 的 select_sql 不带 FROM
FEEDBACK_COLS = (
    'SELECT f.id, f.user_id, f.username, f.type, f.content, f.contact, f.page, '
    'f.status, f.admin_reply, f.admin_id, f.replied_at, f.created_at, f.updated_at '
)


@router.get('/feedback')
def feedback_list(status: str = None, type: str = None, keyword: str = None,
                  page: int = 0, pageSize: int = 0):
    # 参数名必须是 type —— 前端筛选项就叫 type。写成 fb_type 的话 FastAPI
    # 收不到值、条件被静默忽略，管理员会以为「筛选坏了」其实一条都没过滤。
    """反馈列表：status / type / keyword 可选筛选，按提交时间倒序。

    status 与 type 都不在白名单里就忽略（而不是拼进 SQL）——
    筛选值来自 URL，任何拼进 SQL 的字符串都必须先过白名单。
    """
    # paginate 的 where_sql 必须自带 FROM（COUNT 借不到 select 里的表名）
    where = FEEDBACK_FROM + 'WHERE 1=1'
    params = []
    if status in FEEDBACK_STATUS:
        where += ' AND f.status = ?'
        params.append(status)
    if type in FEEDBACK_TYPES:
        where += ' AND f.type = ?'
        params.append(type)
    kw = str(keyword or '').strip()
    if kw:
        where += ' AND (f.content LIKE ? OR f.username LIKE ?)'
        params += [f'%{kw}%', f'%{kw}%']

    body = paginate(
        where,
        params,
        FEEDBACK_COLS,
        ' ORDER BY f.id DESC',
        page, pageSize,
    )
    # 各状态条数：让管理员一眼看到还有多少条没处理，不必切筛选去数
    counts = {}
    for s in FEEDBACK_STATUS:
        counts[s] = int(query_one(
            'SELECT COUNT(*) AS c FROM feedback WHERE status = ?', [s]
        )['c'] or 0)
    body['statusCount'] = counts
    body['statusList'] = FEEDBACK_STATUS
    body['typeList'] = FEEDBACK_TYPES
    return body


@router.put('/feedback/{fb_id}')
def feedback_update(fb_id: int, request: Request, user: dict = Depends(admin_user)):
    """处理反馈：改状态 + 回复。回复非空时自动落 replied_at 与处理人。"""
    if not is_id(fb_id):
        return fail(400, '参数错误')
    if not query_one('SELECT id FROM feedback WHERE id = ?', [fb_id]):
        return fail(404, '反馈不存在')

    body = body_of(request)
    status = str(body.get('status') or '').strip()
    reply = str(body.get('adminReply') or '').strip()

    sets = []
    params = []
    if status:
        if status not in FEEDBACK_STATUS:
            return fail(400, '状态不合法')
        sets.append('status = ?')
        params.append(status)
    if reply:
        # 回复按正文长度上限截断，避免一次塞进整篇小作文
        sets += ['admin_reply = ?', 'admin_id = ?', 'replied_at = NOW()']
        params += [reply[:1000], user['id']]
    elif 'adminReply' in body:
        # 显式清空回复（前端点了「清除回复」）
        sets += ['admin_reply = NULL', 'admin_id = NULL', 'replied_at = NULL']
    if not sets:
        return fail(400, '没有要更新的内容')

    query('UPDATE feedback SET ' + ', '.join(sets) + ' WHERE id = ?', params + [fb_id])
    return ok(query_one(FEEDBACK_COLS + FEEDBACK_FROM + 'WHERE f.id = ?', [fb_id]), message='已保存')


@router.delete('/feedback/{fb_id}')
def feedback_delete(fb_id: int, user: dict = Depends(admin_user)):
    """删除反馈（垃圾灌水 / 重复提交）"""
    if not is_id(fb_id):
        return fail(400, '参数错误')
    r = query('DELETE FROM feedback WHERE id = ?', [fb_id])
    if not r.affected_rows:
        return fail(404, '反馈不存在')
    return ok(message='已删除')
