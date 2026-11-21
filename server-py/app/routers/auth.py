"""认证相关接口：注册 / 登录 / 登出 / 当前用户 / 改密码 / 找回密码 / 头像。"""

import math
import os
import re
import secrets

from fastapi import APIRouter, Depends, File, Request, Response, UploadFile

from app.core import audit
from app.core.body import body_of
from app.core.config import COOKIE_NAME
from app.core.deps import check_timestamp, current_user
from app.core.errors import ApiError
from app.core.response import fail, ok
from app.core.security import (check_password, cookie_kwargs, gen_temp_password,
                               gen_ticket, hash_password, sign_token)
from app.core.shield import clear_login_fail, ip_of, login_locked, note_login_fail
from app.db import query, query_one

router = APIRouter()

# 头像上传目录（与 main.py 挂载的 /uploads 静态目录一致）
AVATAR_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'uploads', 'avatars',
)
# 手机随手拍一张就有 3-5MB，前端会先压到 ≤512px 再传，2MB 是给压缩兜底的
AVATAR_MAX_SIZE = 2 * 1024 * 1024


def _sniff_image_ext(head: bytes):
    """看文件头认图片类型。扩展名和 Content-Type 都由客户端说了算，
    谁都能填；只有魔数骗不了人 —— 不认的一律拒收。"""
    if head.startswith(b'\xff\xd8\xff'):
        return 'jpg'
    if head.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'
    if head.startswith((b'GIF87a', b'GIF89a')):
        return 'gif'
    if head[:4] == b'RIFF' and head[8:12] == b'WEBP':
        return 'webp'
    return None


def _delete_old_avatar(avatar_path: str):
    """删掉被替换的旧头像文件。只处理 /uploads/avatars/ 下、文件名形如
    avatar-{数字}-{hex}.{ext} 的记录值 —— 万一将来 avatar 存了外链或别的目录，
    不能顺着字段值把别人的文件删了。"""
    if not avatar_path or not avatar_path.startswith('/uploads/avatars/'):
        return
    name = os.path.basename(avatar_path)
    if not re.match(r'^avatar-\d+-[0-9a-f]{16}\.[a-z]+$', name):
        return
    try:
        path = os.path.join(AVATAR_DIR, name)
        if os.path.realpath(os.path.dirname(path)) == os.path.realpath(AVATAR_DIR):
            os.remove(path)
    except (OSError, SystemExit):
        # OSError：文件已被删/占用，留着当孤儿文件即可；
        # SystemExit：某些托管环境会给 os.remove 挂「删除守卫」垫片，
        # 拦截时抛的是 SystemExit（BaseException，不是 OSError），不接住的话
        # 置空记录都已入库了却在最后一步炸成 500 —— 用户看到的就是这个 bug。
        # 删不掉只影响磁盘空间，不影响「恢复默认头像」功能本身。
        pass

# 账号与姓名对不上时统一回这一句。分两种说法就成了免费的用户枚举接口：
# 说「账号不存在」= 存在性探测；说「姓名不对」= 确认账号存在、再把姓名交给你暴力试。
BAD_IDENTITY_MSG = '账号与姓名不匹配，无法重置密码'


def _check_real_name(name):
    """姓名是找回密码的唯一凭证，注册 / 修改 / 找回三处共用这一套校验。"""
    n = str(name or '').strip()
    if not n:
        return None, '请填写姓名'
    if len(n) < 2 or len(n) > 20:
        return None, '姓名长度应为 2-20 个字符'
    return n, None


def _norm_name(name):
    """比对用：压掉内部空白，「张 三」与「张三」应当算同一个人。"""
    return re.sub(r'\s+', '', str(name or ''))



@router.post('/register')
def register(request: Request):
    check_timestamp(request)
    body = body_of(request)
    username = body.get('username')
    password = body.get('password')
    real_name = body.get('realName')

    if not username or not password:
        return fail(400, '账号和密码不能为空')
    if not re.match(r'^[A-Za-z0-9_]{3,20}$', str(username)):
        return fail(400, '账号需为 3-20 位字母、数字或下划线')
    if str(username).lower() == 'admin':
        return fail(400, '该账号为系统保留账号')
    if len(str(password)) < 6 or len(str(password)) > 64:
        return fail(400, '密码长度应为 6-64 位')

    # 找回密码只认「账号 + 姓名」，姓名不再是可选项：空着等于这个账号永远找不回密码
    real_name, err = _check_real_name(real_name)
    if err:
        return fail(400, err)

    if query_one('SELECT id FROM user WHERE username = ?', [username]):
        return fail(400, '该账号已存在')

    hashed = hash_password(str(password))
    r = query(
        'INSERT INTO user (username, password, real_name, role) VALUES (?, ?, ?, ?)',
        [username, hashed, real_name, 'student'],
    )
    audit.log('register', username=username, id=r.insert_id, ip=ip_of(request))
    return ok({'id': r.insert_id, 'username': username, 'realName': real_name, 'role': 'student'},
              message='注册成功')


@router.post('/login')
def login(request: Request, response: Response):
    body = body_of(request)
    username = body.get('username')
    password = body.get('password')
    ip = ip_of(request)

    # 先看有没有被锁：锁定判断必须在查库之前，否则爆破照样能打满数据库
    left = login_locked(username or '', ip)
    if left:
        audit.log('login_blocked', username=username, ip=ip, seconds=left)
        # 429 用真实 HTTP 状态码：它是限流语义，不是普通业务失败
        raise ApiError(429, 429, f'登录失败次数过多，请 {math.ceil(left / 60)} 分钟后再试')

    user = query_one('SELECT * FROM user WHERE username = ?', [username])
    if not user or not check_password(password or '', user.get('password')):
        # 账号不存在与密码错误返回同一句：分开说就等于免费的用户名枚举接口
        lock = note_login_fail(username or '', ip)
        audit.log('login_fail', username=username, ip=ip,
                  locked=lock or None, exists=bool(user))
        if lock:
            raise ApiError(429, 429, f'登录失败次数过多，账号已锁定 {lock} 分钟')
        return fail(400, '账号或密码错误')

    clear_login_fail(username or '', ip)
    # 登录用的若是某张工单发出的临时密码，说明用户已经拿到并改回了自己的密码，
    # 那份明文留着毫无用处 —— 立刻销毁
    _consume_temp_password(user['id'], str(password or ''))
    token = sign_token(user)
    # 令牌同时写进 HttpOnly Cookie：前端不再需要把它塞进 localStorage
    response.set_cookie(value=token, **cookie_kwargs())
    audit.log('login_ok', username=user['username'], id=user['id'], ip=ip)
    return ok({
        'token': token,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'realName': user.get('real_name'),
            'role': user['role'],
            'avatar': user.get('avatar') or '',
        },
    }, message='登录成功')


@router.post('/logout')
def logout(request: Request, response: Response, user: dict = Depends(current_user)):
    """退出登录：清掉 Cookie。

    JWT 本身无状态，服务端没法让它「立刻失效」，只能让浏览器不再持有它。
    要真正做到登出即失效需要维护 token 黑名单，对本项目属于过度设计 ——
    7 天有效期 + 前端不落盘 + 登出即清 Cookie，实际暴露窗口已经很小。
    """
    response.delete_cookie(COOKIE_NAME, path='/')
    audit.log('logout', username=user.get('username'), id=user.get('id'), ip=ip_of(request))
    return ok(message='已退出登录')


@router.get('/me')
def me(user: dict = Depends(current_user)):
    row = query_one(
        'SELECT id, username, real_name, role, avatar, created_at FROM user WHERE id = ?',
        [user['id']],
    )
    if not row:
        return ok(row)
    row = dict(row)
    # 个人中心读的是驼峰 realName，库字段是 real_name，两个都给（与 Node 侧一致），
    # 免得前端拿 undefined 还得自己记哪边返回的哪种写法
    row['realName'] = row.get('real_name') or ''
    row['avatar'] = row.get('avatar') or ''
    return ok(row)


@router.post('/profile')
def update_profile(request: Request, user: dict = Depends(current_user)):
    """修改个人资料：目前只放开姓名 —— 它是找回密码的唯一凭证，必须能自己更正。"""
    body = body_of(request)
    real_name, err = _check_real_name(body.get('realName'))
    if err:
        return fail(400, err)
    query('UPDATE user SET real_name = ? WHERE id = ?', [real_name, user['id']])
    return ok({'realName': real_name}, message='资料已保存')


@router.post('/password')
def change_password(request: Request, user: dict = Depends(current_user)):
    check_timestamp(request)  # 改密码被重放 = 账号被接管，必须带时间戳
    body = body_of(request)
    old_pwd = body.get('oldPassword')
    new_pwd = body.get('newPassword')
    if not old_pwd or not new_pwd:
        return fail(400, '原密码和新密码不能为空')
    if len(str(new_pwd)) < 6 or len(str(new_pwd)) > 64:
        return fail(400, '新密码长度应为 6-64 位')

    row = query_one('SELECT * FROM user WHERE id = ?', [user['id']])
    if not row or not check_password(str(old_pwd), row.get('password')):
        return fail(400, '原密码不正确')

    query('UPDATE user SET password = ? WHERE id = ?', [hash_password(new_pwd), user['id']])
    audit.log('change_password', username=user.get('username'), id=user['id'], ip=ip_of(request))
    return ok(message='密码修改成功')


# --------------------------------------------------------------------------
# 找回密码：不经过管理员，用户自己走完「自证身份 -> 重设密码」
#
#   POST /auth/forgot/confirm  { username, realName, newPassword }
#
# 唯一凭证是「注册时填写的姓名」：账号 + 姓名对上就直接重设，不依赖邮件、
# 也不需要额外去设置密保问题。早期版本走过邮箱验证码和密保问题，
# 两步流程加上「还得先去设置一遍」，实际没人能找回 —— 已整体移除。
#
# 姓名提示（GET /auth/forgot/hint）：自证的唯一凭证是姓名，姓名本身忘了
# 就死锁了。给一个「脱敏提示」（首字 + 掩码 + 末字 + 长度）帮用户回忆 ——
# 泄露的信息量很小（知道账号的人本来也猜得到是个中文名），却足够让人
# 认出「哦对，我叫这个」。账号不存在时不给出与存在时不同的响应，
# 避免被拿来枚举有效账号。
# --------------------------------------------------------------------------

def _mask_name(name: str):
    """"张三" -> "张*"，"欧阳文文" -> "欧**文"；单字名不提示末字。"""
    n = (name or '').strip()
    if not n:
        return None
    if len(n) == 1:
        return n + '*'
    return n[0] + '*' * (len(n) - 2) + n[-1]


@router.get('/forgot/hint')
def forgot_hint(request: Request, username: str = ''):
    check_timestamp(request)
    uname = str(username or '').strip()
    if not uname:
        return fail(400, '请先填写账号')
    u = query_one('SELECT real_name FROM user WHERE username = ?', [uname])
    masked = _mask_name((u or {}).get('real_name') or '')
    if not masked:
        # 与「账号不存在」同响应：不帮攻击者确认某个账号有没有注册
        return ok({'masked': None})
    audit.log('forgot_hint', username=uname, ip=ip_of(request))
    return ok({'masked': masked, 'length': len((u.get('real_name') or '').strip())})


@router.post('/forgot/confirm')
def forgot_confirm(request: Request):
    """校验账号 + 姓名，通过后直接重设密码。"""
    check_timestamp(request)
    body = body_of(request)
    username = str(body.get('username') or '').strip()
    real_name = str(body.get('realName') or '').strip()
    new_pwd = body.get('newPassword')
    if not username or not real_name:
        return fail(400, '请填写账号和姓名')
    if not new_pwd or len(str(new_pwd)) < 6 or len(str(new_pwd)) > 64:
        return fail(400, '新密码长度应为 6-64 位')

    u = query_one('SELECT id, real_name FROM user WHERE username = ?', [username])
    if not u:
        return fail(400, BAD_IDENTITY_MSG)
    stored = _norm_name(u.get('real_name'))
    if not stored or stored != _norm_name(real_name):
        return fail(400, BAD_IDENTITY_MSG)

    query('UPDATE user SET password = ? WHERE id = ?', [hash_password(new_pwd), u['id']])
    audit.log('forgot_reset', username=username, id=u['id'], ip=ip_of(request))
    return ok(message='重置成功，请用新密码登录')


# --------------------------------------------------------------------------
# 申请临时密码：账号 + 联系电话 → 管理员后台工单 → 通过后用户凭单号自取
#
#   POST /auth/temp-password/apply   { username, phone, reason? }
#   GET  /auth/temp-password/status?ticket=&username=
#
# 自助找回的唯一凭证是姓名，姓名忘了就走不通。这一步把「自证身份」从姓名换成
# 「管理员人工核身」：工单里留着账号、姓名快照和电话，管理员照着电话联系本人
# 确认后点「通过」—— 密码当场重置，临时密码既在管理员弹窗里出现一次，
# 也留在工单里等用户凭单号取走。本项目既没有邮件也没有短信通道，
# 「留凭可取」是唯一能闭环的送达方式。
#
# 取件凭证用随机单号而不是「账号 + 电话」：电话是半公开信息，拿它当口令
# 等于让知道手机号的人都能取走别人的临时密码。单号必须配上账号一起出示，
# 两者都对上才算数。
# --------------------------------------------------------------------------

TEMP_PWD_STATUS_TEXT = {
    'pending': '管理员正在核实，请稍后再来查看',
    'approved': '已通过',
    'rejected': '已被驳回',
    'used': '已使用',
}


def _check_phone(phone):
    """电话必须是 11 位中国大陆手机号。

    场景是管理员照着号码打电话核身，座机、乱填的数字都联系不上人。
    书写形式放行 +86 / 0086 / 空格 / 连字符 / 括号，但存库统一归一成裸号，
    管理员复制到拨号盘即可拨打。规则与前端 utils/phone.js 保持一致。
    """
    p = str(phone or '').strip()
    if not p:
        return None, '请填写联系电话'
    if not re.fullmatch(r'[\d+\-()\s]{6,20}', p) or len(p) > 20:
        # 字母、中文这类字符必须挡掉：只剥数字校验的话 "abc13800138000" 会被误放行
        return None, '联系电话只能包含数字和 + - 空格'
    digits = re.sub(r'\D', '', p)
    if re.fullmatch(r'0{0,2}86\d{11}', digits):
        digits = digits[digits.index('86') + 2:]
    if not re.fullmatch(r'1[3-9]\d{9}', digits):
        return None, '请填写正确的 11 位手机号，例如 13812345678'
    return digits, None


def _ticket_row(tk: str, uname: str):
    return query_one(
        'SELECT * FROM password_request WHERE ticket = ? AND username = ?', [tk, uname])


def _unique_ticket():
    tk = gen_ticket()
    while query_one('SELECT id FROM password_request WHERE ticket = ?', [tk]):
        tk = gen_ticket()
    return tk


@router.post('/temp-password/apply')
def apply_temp_password(request: Request):
    check_timestamp(request)  # 被重放 = 后台多一张重复工单
    body = body_of(request)
    username = str(body.get('username') or '').strip()
    phone, err = _check_phone(body.get('phone'))
    if not re.match(r'^[A-Za-z0-9_]{3,20}$', username):
        return fail(400, '账号需为 3-20 位字母、数字或下划线')
    if err:
        return fail(400, err)
    reason = str(body.get('reason') or '').strip()[:200]

    u = query_one('SELECT id, username, real_name FROM user WHERE username = ?', [username])
    if not u:
        # 注册接口本来就会提示账号是否存在，这里再藏着也就没意义了
        return fail(400, '账号不存在，请确认后重试')

    # 重复提交不新开工单：还在排队的工单把原单号交回去就行，
    # 否则一个心急的学生能在后台堆出一屏待处理
    pending = query_one(
        "SELECT ticket, created_at FROM password_request "
        "WHERE user_id = ? AND status = 'pending' ORDER BY id DESC LIMIT 1", [u['id']])
    if pending:
        return ok({'ticket': pending['ticket'], 'username': username, 'status': 'pending',
                   'createdAt': pending['created_at'], 'messageText': TEMP_PWD_STATUS_TEXT['pending']},
                  message='你已提交过申请，请耐心等待管理员处理')

    ticket = _unique_ticket()
    query(
        'INSERT INTO password_request (ticket, user_id, username, real_name, phone, reason) '
        'VALUES (?, ?, ?, ?, ?, ?)',
        [ticket, u['id'], u['username'], u.get('real_name') or '', phone, reason],
    )
    audit.log('temp_pwd_apply', username=username, id=u['id'], ip=ip_of(request))
    return ok({'ticket': ticket, 'username': username, 'status': 'pending',
               'createdAt': None, 'messageText': TEMP_PWD_STATUS_TEXT['pending']},
              message='申请已提交，管理员核实后会联系你')


@router.get('/temp-password/status')
def temp_password_status(request: Request, ticket: str = '', username: str = ''):
    check_timestamp(request)
    tk = str(ticket or '').strip().upper()
    uname = str(username or '').strip()
    if not tk or not uname:
        return fail(400, '请填写申请单号和账号')
    row = _ticket_row(tk, uname)
    if not row:
        return fail(400, '没有查到对应申请，请核对单号与账号')

    # 临时密码只在「已通过且还没被用过」时给出：用过的已经销毁，
    # 驳回 / 待处理的给出来也没意义，还可能把流程绕过去
    pwd = ''
    if row['status'] == 'approved':
        pwd = row.get('temp_password') or ''
    return ok({
        'ticket': row['ticket'],
        'username': row['username'],
        'status': row['status'],
        'statusText': TEMP_PWD_STATUS_TEXT.get(row['status'], row['status']),
        'password': pwd,
        'rejectReason': row.get('reject_reason') or '',
        'createdAt': row.get('created_at'),
        'handledAt': row.get('handled_at'),
    })


def _consume_temp_password(user_id: int, password: str):
    """用临时密码登录成功 → 立刻销毁明文。

    临时密码明文必须落库（没有邮件短信，用户只能凭单号回来取），
    但它的生命周期越短越好：一旦它被用来登录，说明持有者就是用户本人，
    再留在表里只是给拖库多送一份可用凭据。"""
    rows = query(
        "SELECT id, temp_password FROM password_request "
        "WHERE user_id = ? AND status = 'approved' AND temp_password <> ''", [user_id]).rows
    for row in rows:
        if (row.get('temp_password') or '') == password:
            query("UPDATE password_request SET status = 'used', temp_password = '' WHERE id = ?",
                  [row['id']])


# --------------------------------------------------------------------------
# 头像：POST /auth/avatar  (multipart, 字段名 file)
#
# 前端选完图先在本地用 canvas 压到 ≤512px 再传 —— 一张头像而已，没必要把
# 3MB 的原图原样传上来。这里 2MB 限制是给「压缩失败/直接传原图」兜底的。
# 类型校验只认文件头魔数：扩展名和 Content-Type 是客户端随便填的，不作数。
# --------------------------------------------------------------------------

@router.post('/avatar')
def upload_avatar(request: Request, file: UploadFile = File(...),
                  user: dict = Depends(current_user)):
    data = file.file.read(AVATAR_MAX_SIZE + 1)
    if not data:
        return fail(400, '请选择要上传的图片')
    if len(data) > AVATAR_MAX_SIZE:
        return fail(400, '图片不能超过 2MB，请压缩后再试')
    ext = _sniff_image_ext(data[:16])
    if not ext:
        return fail(400, '仅支持 jpg / png / webp / gif 格式的图片')

    os.makedirs(AVATAR_DIR, exist_ok=True)
    # 文件名带随机段：同一用户反复换头像也不会命中浏览器缓存的旧图
    filename = f"avatar-{user['id']}-{secrets.token_hex(8)}.{ext}"
    with open(os.path.join(AVATAR_DIR, filename), 'wb') as f:
        f.write(data)

    old = query_one('SELECT avatar FROM user WHERE id = ?', [user['id']])
    _delete_old_avatar((old or {}).get('avatar') or '')
    query('UPDATE user SET avatar = ? WHERE id = ?', ['/uploads/avatars/' + filename, user['id']])
    audit.log('avatar_update', username=user.get('username'), id=user['id'], ip=ip_of(request))
    return ok({'avatar': '/uploads/avatars/' + filename}, message='头像已更新')


@router.delete('/avatar')
def reset_avatar(request: Request, user: dict = Depends(current_user)):
    """"恢复默认头像"。

    默认头像不是某张固定的图片 —— 前端在 avatar 为空时回退显示「姓名首字」，
    所以这里要做的是把 avatar 置空，并顺手删掉那张已经没人引用的旧图
    （不删就是个孤儿文件，白占磁盘）。用户之后随时能再传一张新的。"""
    old = query_one('SELECT avatar FROM user WHERE id = ?', [user['id']])
    query('UPDATE user SET avatar = ? WHERE id = ?', ['', user['id']])
    _delete_old_avatar((old or {}).get('avatar') or '')
    audit.log('avatar_reset', username=user.get('username'), id=user['id'], ip=ip_of(request))
    return ok({'avatar': ''}, message='已恢复默认头像')
