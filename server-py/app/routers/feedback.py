"""用户反馈建议：提交 / 我的反馈 / 撤回。

管理端的查看与处理在 admin.py（路径 /api/admin/feedback*）——
分开是因为权限模型不同：这边是「自己看自己的」，那边要管理员权限。
"""

from fastapi import APIRouter, Depends, Request

from app.core.body import body_of
from app.core.deps import current_user
from app.core.pagination import paginate
from app.core.response import fail, ok
from app.core.shield import bucket, ip_of
from app.db import query, query_one
from app.utils.validate import clamp_text, is_id

router = APIRouter()

ALLOWED_TYPES = ['bug', 'feature', 'experience', 'other']
MIN_CONTENT = 5
MAX_CONTENT = 1000

# 提交限流：3 分钟 5 条。反馈是低频动作，正常人根本碰不到上限；
# 但不设的话一个脚本就能把表写满、把管理员的待处理列表淹掉。
SUBMIT_LIMIT = 5
SUBMIT_WINDOW = 180

# 列表统一不回传 ua —— 它是排障用的原始浏览器标识，没必要出现在用户侧接口里
# 注意 paginate() 的约定：select_sql 不带 FROM，FROM 归 where_sql 所有
# （COUNT 语句是 'SELECT COUNT(*) AS total' + where_sql，借不到 select 里的表名）。
FEEDBACK_COLS = (
    'SELECT f.id, f.user_id, f.username, f.type, f.content, f.contact, f.page, '
    'f.status, f.admin_reply, f.admin_id, f.replied_at, f.created_at, f.updated_at '
)
FEEDBACK_FROM = ' FROM feedback f '


def normalize_type(t):
    """类型白名单，非法值一律归到 other —— 不让脏数据进表"""
    v = str(t or '').strip().lower()
    return v if v in ALLOWED_TYPES else 'other'


@router.post('')
def submit(request: Request, user: dict = Depends(current_user)):
    """提交一条反馈。成功后回传该条记录，前端可直接插进「我的反馈」列表顶部。"""
    body = body_of(request)
    content = str(body.get('content') or '').strip()
    if len(content) < MIN_CONTENT:
        return fail(400, f'请至少写 {MIN_CONTENT} 个字，方便我们定位问题')
    if len(content) > MAX_CONTENT:
        return fail(400, f'内容太长了，请精简到 {MAX_CONTENT} 字以内')

    ip = ip_of(request)
    if not bucket.allow(f'feedback:{user["id"]}|{ip}', SUBMIT_LIMIT, SUBMIT_WINDOW):
        return fail(429, '提交太频繁了，请稍后再试')

    fb_type = normalize_type(body.get('type'))
    contact = clamp_text(body.get('contact'), 120)
    page = clamp_text(body.get('page'), 200)
    ua = str(request.headers.get('user-agent') or '')[:255]

    insert_id = query(
        'INSERT INTO feedback (user_id, username, type, content, contact, page, ua, status) '
        'VALUES (?, ?, ?, ?, ?, ?, ?, "pending")',
        [user['id'], str(user.get('username') or ''), fb_type, content, contact, page, ua],
    ).insert_id

    row = query_one(FEEDBACK_COLS + FEEDBACK_FROM + 'WHERE f.id = ?', [insert_id])
    return ok(dict(row) if row else {'id': insert_id}, message='提交成功，感谢你的反馈')


@router.get('/mine')
def mine(page: int = 0, pageSize: int = 0, user: dict = Depends(current_user)):
    """我的反馈（含管理员回复），按提交时间倒序"""
    return paginate(
        ' FROM feedback f WHERE f.user_id = ?',
        [user['id']],
        FEEDBACK_COLS,
        ' ORDER BY f.id DESC',
        page, pageSize,
    )


@router.delete('/{fb_id}')
def remove(fb_id: int, user: dict = Depends(current_user)):
    """撤回自己的反馈。

    只放过 pending（还没人处理）—— 管理员已经在跟进的东西被悄悄删掉，
    双方都会以为对方没动静，这种"消失的反馈"比留着更难办。
    """
    if not is_id(fb_id):
        return fail(400, '参数错误')
    row = query_one('SELECT id, status FROM feedback WHERE id = ? AND user_id = ?', [fb_id, user['id']])
    if not row:
        return fail(404, '反馈不存在')
    if str(row['status']) != 'pending':
        return fail(400, '管理员已在处理，不能撤回了')
    query('DELETE FROM feedback WHERE id = ? AND user_id = ?', [fb_id, user['id']])
    return ok(message='已撤回')
