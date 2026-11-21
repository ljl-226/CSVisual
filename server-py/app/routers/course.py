"""课程与知识点接口。"""

from fastapi import APIRouter, Depends, Request

from app.core.deps import current_user
from app.core.response import fail, ok
from app.db import query, query_one
from app.utils.validate import is_id

router = APIRouter()


@router.get('')
@router.get('/')
def course_list():
    r = query(
        'SELECT c.*, (SELECT COUNT(*) FROM knowledge k WHERE k.course_id = c.id) AS knowledge_count '
        'FROM course c ORDER BY c.sort_no, c.id'
    )
    return ok(list(r.rows))


@router.get('/{cid}')
def course_detail(cid: str):
    if not is_id(cid):
        return fail(400, '课程参数不合法')
    course = query_one('SELECT * FROM course WHERE id = ?', [cid])
    if not course:
        return fail(404, '课程不存在')
    rows = query('SELECT * FROM knowledge WHERE course_id = ? ORDER BY sort_no, id', [course['id']])
    return ok({'course': course, 'knowledge': list(rows.rows)})


@router.get('/knowledge/{kid}')
def knowledge_detail(kid: str):
    if not is_id(kid):
        return fail(400, '知识点参数不合法')
    k = query_one(
        'SELECT k.*, c.name AS course_name, c.category '
        'FROM knowledge k JOIN course c ON c.id = k.course_id WHERE k.id = ?',
        [kid],
    )
    if not k:
        return fail(404, '知识点不存在')

    visuals = query(
        'SELECT id, title, description, config FROM visualization WHERE knowledge_id = ?',
        [k['id']],
    )
    import json

    parsed = []
    for v in visuals.rows:
        item = dict(v)
        try:
            item['config'] = json.loads(item['config']) if item.get('config') else {}
        except Exception:
            item['config'] = {}
        parsed.append(item)

    return ok({'knowledge': k, 'visualizations': parsed, 'progress': None})


@router.post('/knowledge/{kid}/view')
def knowledge_view(request: Request, kid: str, user: dict = Depends(current_user)):
    if not is_id(kid):
        return fail(400, '知识点参数不合法')
    k = query_one('SELECT id FROM knowledge WHERE id = ?', [kid])
    if not k:
        return fail(404, '知识点不存在')
    query(
        'INSERT INTO study_record (user_id, knowledge_id, event_type, duration) '
        "VALUES (?, ?, 'view', ?) "
        'ON DUPLICATE KEY UPDATE visit_count = visit_count + 1, last_time = NOW()',
        [user['id'], kid, 0],
    )
    return ok(message='ok')
