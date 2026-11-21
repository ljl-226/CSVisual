"""
程序设计算法题模块

1. 题目列表 / 详情（详情只给样例用例，隐藏用例用于判分）
2. 在线判题：真实编译运行，逐用例比对标准输出
3. 权值排名：每题带 weight（难度越高权值越大），总分为已通过题目权值之和
4. 算法小助手：先思考再讲解，可针对题目讲思路、讲复杂度、帮你看代码
"""

import json
import os
import random
import re
import shutil
import tempfile
import time

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.agent.llm import call_llm, stream_llm
from app.agent.reasoning import brief, build_algo_reasoning
from app.core.body import body_of
from app.core.deps import current_user, optional_user
from app.core.response import fail, ok
from app.db import query, query_one
from app.routers.code import IS_WINDOWS, detect_env, run, with_bin_dir
from app.utils.num import round_half_up
from app.utils.remote_run import NOTICE, is_env_error, remote_run
from app.utils.validate import clamp_text, is_id, to_int
from app.utils.num import round_half_up

router = APIRouter()

JUDGE_ROOT = os.path.join(tempfile.gettempdir(), 'csvisual-judge')
CASE_TIMEOUT = 5000
COMPILE_TIMEOUT = 20000
MAX_CODE = 20000
MAX_CASES = 12
MAX_INPUT = 20000  # 控制台自定义输入上限（与 /code/run 的 stdin 一致）

LANGS = {
    'python': {'ext': 'py', 'label': 'Python'},
    'c': {'ext': 'c', 'label': 'C'},
    'cpp': {'ext': 'cpp', 'label': 'C++'},
    'java': {'ext': 'java', 'label': 'Java'},
    'javascript': {'ext': 'js', 'label': 'JavaScript'},
}

DIFF_TEXT = {1: '入门', 2: '容易', 3: '中等', 4: '较难', 5: '困难'}


def _ensure_dir(d):
    os.makedirs(d, exist_ok=True)


def _cleanup(d):
    try:
        shutil.rmtree(d, ignore_errors=True)
    except Exception:
        pass


def normalize_out(s):
    """判题输出比对：忽略行尾空白与末尾换行差异，其余必须逐字符一致"""
    text = str(s if s is not None else '').replace('\r\n', '\n')
    lines = [l.rstrip() for l in text.split('\n')]
    return re.sub(r'\n+$', '', '\n'.join(lines))


def to_list(v):
    if isinstance(v, list):
        return [str(x) for x in v if x]
    return [x for x in re.split(r'[,，\s]+', str(v or '')) if x]


def remote_judge(cases, language, code, t0, free=False):
    """云端兜底判题：本机没有编译器/子进程被限制（EBUSY）时，
    逐用例把代码交给云端沙箱执行。结果结构与本地 judge() 完全一致，
    上层（运行/提交/记分）无需任何改动；控制台会注明结果来自云端。
    free=True 为「自定义输入」模式：不比对答案，只把程序输出原样带回。"""
    results = []
    passed = 0
    first_fail = ''
    for cs in cases:
        rr = remote_run(language, code, cs.get('stdin') or '')
        if not rr['ok']:
            if rr.get('compileError'):
                return {'status': 'compile_error', 'passed': 0, 'total': len(cases), 'results': [],
                        'consoleLog': '', 'message': '编译失败：\n' + str(rr.get('stderr') or '')[:1200],
                        'runtime': int(time.time() * 1000) - t0}
            return {'status': 'runtime_error', 'passed': 0, 'total': len(cases), 'results': [],
                    'consoleLog': '', 'message': '本机与云端均无法执行：' + rr.get('reason', ''),
                    'runtime': int(time.time() * 1000) - t0}
        out = rr['stdout'] or ''
        ok_case = rr['exitCode'] == 0 and (free or normalize_out(out) == normalize_out(cs.get('expected')))
        if ok_case:
            passed += 1
        elif not free and not first_fail:
            if rr['exitCode'] != 0:
                first_fail = f"程序异常退出（退出码 {rr['exitCode']}）：{str(rr['stderr'] or '')[:300]}"
            else:
                first_fail = (f"输出不正确。期望：\n{str(cs.get('expected'))[:200]}\n"
                              f"实际：\n{str(out)[:200]}")
        results.append({
            'stdin': str(cs.get('stdin') or '')[:300],
            'expected': str(cs.get('expected') or '')[:300],
            'actual': str(out)[:300],
            'stdout': str(out)[:1500],
            'stderr': str(rr['stderr'] or '')[:600],
            'spawnError': '',
            'ok': ok_case,
        })

    console_lines = [NOTICE]
    for i, r in enumerate(results[:3], 1):
        parts = []
        if r.get('stdout'):
            parts.append(str(r['stdout']).rstrip('\n'))
        if r.get('stderr'):
            parts.append('[stderr] ' + str(r['stderr']).rstrip('\n'))
        # 自定义输入只有一组数据，再看「[用例 1]」就是噪音 —— 直接给裸输出
        body = ('\n'.join(parts) + '\n') if parts else '(程序没有输出)\n'
        console_lines.append(body if free else f"[用例 {i}]\n" + body)

    all_empty = all((not r['ok']) and (not r['actual']) for r in results)
    if free:
        status = 'custom'
    elif passed == len(cases):
        status = 'accepted'
    elif passed == 0 and all_empty:
        status = 'runtime_error'
    else:
        status = 'wrong_answer'
    return {
        'status': status,
        'passed': passed,
        'total': len(cases),
        'results': results,
        'consoleLog': '\n'.join(console_lines),
        'message': '' if free else (f'全部 {len(cases)} 个用例通过' if status == 'accepted' else (first_fail or '未通过')),
        'runtime': int(time.time() * 1000) - t0,
    }


def judge(cases, language, code, free=False):
    """把用户代码跑在一组测试用例上。
    free=True 为「自定义输入」模式：不比对答案，只看程序打印了什么。"""
    t0 = int(time.time() * 1000)
    lang = language if language in LANGS else 'python'
    env = detect_env()
    d = os.path.join(JUDGE_ROOT, f"{int(time.time() * 1000)}-{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))}")
    _ensure_dir(d)

    def run_one(cmd, args, stdin, timeout, extra_env=None):
        r = run(cmd, args, {
            'stdin': stdin or '',
            'timeout': timeout,
            'cwd': d,
            'env': extra_env,
        })
        return r

    try:
        exec_plan = None
        extra_env = None

        if lang in ('c', 'cpp'):
            bin_path = env.get(lang, {}).get('bin')
            if not bin_path:
                return remote_judge(cases, lang, code, t0, free)
            src = os.path.join(d, f"main.{LANGS[lang]['ext']}")
            with open(src, 'w', encoding='utf-8') as f:
                f.write(code)
            exe = os.path.join(d, 'main.exe' if IS_WINDOWS else 'main')
            args = [src, '-o', exe, '-std=c++17'] if lang == 'cpp' else [src, '-o', exe]
            c = run(bin_path, args, {'timeout': COMPILE_TIMEOUT, 'cwd': d, 'env': with_bin_dir(bin_path)})
            # 编译器根本拉不起来（EBUSY/受限环境）→ 云端兜底；status!=0 才是真编译错误
            if c['spawnError'] and is_env_error(c['spawnError']):
                return remote_judge(cases, lang, code, t0, free)
            if c['spawnError'] or c['status'] != 0:
                return {
                    'status': 'compile_error', 'passed': 0, 'total': len(cases), 'results': [],
                    'message': '编译失败：\n' + str(c['spawnError'] or c['stderr'] or '')[:1200],
                    'runtime': int(time.time() * 1000) - t0,
                }
            extra_env = with_bin_dir(bin_path)
            exec_plan = (exe, [])
        elif lang == 'python':
            bin_path = env.get('python', {}).get('bin')
            if not bin_path:
                return remote_judge(cases, lang, code, t0, free)
            file_path = os.path.join(d, 'main.py')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            # -X utf8 + PYTHONUTF8：print 输出强制 UTF-8，不随机器 ANSI 代码页漂移
            from app.routers.code import utf8_env

            extra_env = utf8_env()
            exec_plan = (bin_path, ['-X', 'utf8', file_path])
        elif lang == 'java':
            javac = env.get('java', {}).get('bin')
            java_bin = env.get('java', {}).get('javaBin')
            if not javac:
                return remote_judge(cases, lang, code, t0, free)
            cls_match = re.search(r'public\s+class\s+([A-Za-z_]\w*)', code)
            cls = cls_match.group(1) if cls_match else None
            src_text = re.sub(r'\b' + cls + r'\b', 'Main', code) if (cls and cls != 'Main') else code
            with open(os.path.join(d, 'Main.java'), 'w', encoding='utf-8') as f:
                f.write(src_text)
            c = run(javac, ['-encoding', 'UTF-8', os.path.join(d, 'Main.java')],
                    {'timeout': COMPILE_TIMEOUT, 'cwd': d})
            if c['spawnError'] and is_env_error(c['spawnError']):
                return remote_judge(cases, lang, code, t0, free)
            if c['spawnError'] or c['status'] != 0:
                return {
                    'status': 'compile_error', 'passed': 0, 'total': len(cases), 'results': [],
                    'message': '编译失败：\n' + str(c['spawnError'] or c['stderr'] or '')[:1200],
                    'runtime': int(time.time() * 1000) - t0,
                }
            # -Dstdout/-Dstderr.encoding 盖新 JDK，-Dfile.encoding 盖老 JDK
            exec_plan = (java_bin or 'java',
                         ['-Dfile.encoding=UTF-8', '-Dstdout.encoding=UTF-8', '-Dstderr.encoding=UTF-8',
                          '-cp', d, 'Main'])
        else:
            # JavaScript
            from app.routers.code import find_node

            bin_path = env.get('javascript', {}).get('bin') or find_node() or 'node'
            file_path = os.path.join(d, 'main.js')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            exec_plan = (bin_path, [file_path])

        results = []
        passed = 0
        first_fail = ''
        for cs in cases:
            r = run_one(exec_plan[0], exec_plan[1], cs.get('stdin') or '', CASE_TIMEOUT, extra_env)
            # 编译能过但运行时子进程被限制（EBUSY/EPERM）——
            # 剩余用例本地必然全挂，直接整批转云端沙箱，别让用户盯着满屏 EBUSY
            if r['spawnError'] and is_env_error(r['spawnError']):
                return remote_judge(cases, lang, code, t0, free)
            out = r['stdout'] or ''
            # free（自定义输入）时不比对答案：用户敲什么就跑什么，结果原样回显
            ok_case = (not r['spawnError']) and r['status'] == 0 and (free or normalize_out(out) == normalize_out(cs.get('expected')))
            if ok_case:
                passed += 1
            elif not free and not first_fail:
                if r['spawnError']:
                    first_fail = f"运行失败（{r['spawnError']}）"
                elif r['status'] != 0:
                    first_fail = f"程序异常退出（退出码 {r['status']}）：{str(r['stderr'])[:300]}"
                else:
                    first_fail = (f"输出不正确。期望：\n{str(cs.get('expected'))[:200]}\n"
                                  f"实际：\n{str(out)[:200]}")
            results.append({
                'stdin': str(cs.get('stdin') or '')[:300],
                'expected': str(cs.get('expected') or '')[:300],
                'actual': str(out)[:300],
                # 控制台面板：程序 stdout / stderr 原样透出（截断防爆）
                'stdout': str(out)[:1500],
                'stderr': str(r['stderr'] or '')[:600],
                'spawnError': str(r['spawnError'] or ''),
                'ok': ok_case,
            })

        all_empty = all((not r['ok']) and (not r['actual']) for r in results)
        if free:
            status = 'custom'
        elif passed == len(cases):
            status = 'accepted'
        elif passed == 0 and all_empty:
            status = 'runtime_error'
        else:
            status = 'wrong_answer'

        # 控制台面板：前 3 个用例的程序输出原样拼出（与失败用例表格同一披露范围）
        console_lines = []
        for i, r in enumerate(results[:3], 1):
            parts = []
            if r.get('stdout'):
                parts.append(str(r['stdout']).rstrip('\n'))
            if r.get('stderr'):
                parts.append('[stderr] ' + str(r['stderr']).rstrip('\n'))
            if r.get('spawnError'):
                parts.append('[运行环境] ' + str(r['spawnError'])
                             + '，已自动重试仍失败。常见原因：\n'
                             '1. 杀毒软件短暂占用编译器 —— 等 1 分钟重试即可；\n'
                             '2. 后端不是通过 start.bat 启动的 —— 请关闭当前后端，回项目根目录双击 start.bat 重新启动。')
            # 自定义输入只有一组数据，加「[用例 1]」前缀纯属噪音 —— 直接裸输出
            body = ('\n'.join(parts) + '\n') if parts else '(程序没有输出)\n'
            console_lines.append(body if free else f"[用例 {i}]\n" + body)
        console_log = '\n'.join(console_lines)

        return {
            'status': status,
            'passed': passed,
            'total': len(cases),
            'results': results,
            'consoleLog': console_log,
            'message': '' if free else (f'全部 {len(cases)} 个用例通过' if status == 'accepted' else (first_fail or '未通过')),
            'runtime': int(time.time() * 1000) - t0,
        }
    finally:
        _cleanup(d)


# 两条路径都注册：Express 对尾部斜杠是可选匹配的，前端一直调 /api/algorithm，
# 只注册 '/' 会让 FastAPI 发 307 重定向，跨域时存在丢失鉴权头的风险。
@router.get('')
@router.get('/')
def algorithm_list(difficulty: str = None, tag: str = None, source: str = None,
                   keyword: str = None, page: str = None, size: str = None,
                   user: dict = Depends(optional_user)):
    page_n = to_int(page, 1, 9999, 1)
    size_n = to_int(size, 1, 50, 12)

    conds = ['status = 1']
    params = []
    try:
        d = int(difficulty) if difficulty is not None and str(difficulty).strip() != '' else None
    except ValueError:
        d = None
    if d is not None and 1 <= d <= 5:
        conds.append('difficulty = ?')
        params.append(d)
    if tag and tag != 'all':
        conds.append('tags LIKE ?')
        params.append('%' + str(tag)[:32] + '%')
    if source and source != 'all':
        conds.append('source = ?')
        params.append(str(source)[:32])
    kw = clamp_text(keyword, 40).strip()
    if kw:
        conds.append('(title LIKE ? OR tags LIKE ?)')
        params.extend([f'%{kw}%', f'%{kw}%'])

    where = ' WHERE ' + ' AND '.join(conds)
    cnt = query('SELECT COUNT(*) AS c FROM algorithm' + where, params)
    total = int(cnt.rows[0]['c'] or 0) if cnt.rows else 0

    rows = query(
        'SELECT id, title, difficulty, weight, tags, source, knowledge_id, '
        'submit_count, accepted_count, sample_input, sample_output, input_desc, output_desc '
        'FROM algorithm' + where + ' ORDER BY difficulty ASC, id ASC '
        f'LIMIT {(page_n - 1) * size_n}, {size_n}',
        params,
    )

    solved_map = {}
    if user and user.get('id'):
        subs = query(
            "SELECT algorithm_id, MAX(score) AS best FROM algorithm_submit "
            "WHERE user_id = ? AND status = 'accepted' GROUP BY algorithm_id",
            [user['id']],
        )
        for s in subs.rows:
            solved_map[s['algorithm_id']] = int(s['best'] or 0)

    lst = []
    for r in rows.rows:
        item = dict(r)
        item['difficultyText'] = DIFF_TEXT.get(item.get('difficulty'), '中等')
        item['solved'] = item['id'] in solved_map
        item['bestScore'] = solved_map.get(item['id'], 0)
        lst.append(item)

    return ok({'list': lst, 'total': total, 'page': page_n, 'size': size_n})


@router.get('/ranking')
def ranking(size: str = None, user: dict = Depends(optional_user)):
    size_n = to_int(size, 1, 100, 50)
    rows = query(
        'SELECT u.id AS user_id, u.username, u.real_name, '
        'COALESCE(SUM(b.best_score), 0) AS total_score, '
        'COUNT(b.algorithm_id) AS solved_count, '
        'COALESCE(SUM(b.weight), 0) AS total_weight '
        'FROM user u LEFT JOIN ( '
        "  SELECT s.user_id, s.algorithm_id, MAX(s.score) AS best_score, MAX(s.max_score) AS weight "
        "  FROM algorithm_submit s WHERE s.status = 'accepted' GROUP BY s.user_id, s.algorithm_id "
        ') b ON b.user_id = u.id '
        'GROUP BY u.id, u.username, u.real_name '
        'HAVING total_score > 0 '
        f'ORDER BY total_score DESC, solved_count DESC, u.id ASC LIMIT {size_n}'
    )

    ranked = [{
        'rank': i + 1,
        'userId': r['user_id'],
        'username': r['username'],
        'realName': r['real_name'] or r['username'],
        'totalScore': int(r['total_score'] or 0),
        'solvedCount': int(r['solved_count'] or 0),
        'totalWeight': int(r['total_weight'] or 0),
    } for i, r in enumerate(rows.rows)]

    me = None
    if user and user.get('id'):
        hit = next((x for x in ranked if x['userId'] == user['id']), None)
        if hit:
            me = hit
        else:
            row = query_one(
                'SELECT COALESCE(SUM(b.best_score), 0) AS total_score, COUNT(b.algorithm_id) AS solved_count '
                'FROM (SELECT user_id, algorithm_id, MAX(score) AS best_score '
                "      FROM algorithm_submit WHERE status='accepted' GROUP BY user_id, algorithm_id) b "
                'WHERE b.user_id = ?',
                [user['id']],
            )
            my_score = int(row['total_score'] or 0) if row else 0
            better = query_one(
                'SELECT COUNT(*) AS c FROM ( '
                '  SELECT user_id, SUM(best_score) AS s FROM ( '
                '    SELECT user_id, algorithm_id, MAX(score) AS best_score '
                "    FROM algorithm_submit WHERE status='accepted' GROUP BY user_id, algorithm_id "
                '  ) t GROUP BY user_id '
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
                'totalWeight': 0,
            }

    return ok({'list': ranked, 'me': me})


@router.get('/{aid}')
def algorithm_detail(aid: str, user: dict = Depends(optional_user)):
    if not is_id(aid):
        return fail(400, '题目参数不合法')
    algo = query_one('SELECT * FROM algorithm WHERE id = ? AND status = 1', [aid])
    if not algo:
        return fail(404, '题目不存在或已下架')

    cases = query(
        'SELECT id, stdin, expected, is_sample, sort_no FROM algorithm_case '
        'WHERE algorithm_id = ? AND is_sample = 1 ORDER BY sort_no, id',
        [aid],
    )
    kd = query_one('SELECT id, name, route FROM knowledge WHERE id = ?', [algo['knowledge_id']]) \
        if algo.get('knowledge_id') else None

    my_best = None
    if user and user.get('id'):
        # 注意：这里不能写成 SELECT status, MAX(score) ... —— 裸列 status 既违反
        # MySQL 默认的 ONLY_FULL_GROUP_BY（错误 1140），又返回哪一行完全不确定。
        # 明确「优先取通过的、其次分高的、再其次最新的」那一次提交，语义才站得住。
        row = query_one(
            'SELECT status, score AS best, max_score AS max_score '
            'FROM algorithm_submit WHERE user_id = ? AND algorithm_id = ? '
            "ORDER BY (status = 'accepted') DESC, score DESC, id DESC LIMIT 1",
            [user['id'], aid],
        )
        if row:
            my_best = {
                'status': row['status'],
                'score': int(row['best'] or 0),
                'maxScore': int(row['max_score'] or 0),
            }

    return ok({
        'id': algo['id'],
        'title': algo['title'],
        'difficulty': algo['difficulty'],
        'difficultyText': DIFF_TEXT.get(algo['difficulty'], '中等'),
        'weight': algo['weight'],
        'description': algo['description'],
        'inputDesc': algo['input_desc'],
        'outputDesc': algo['output_desc'],
        'sampleInput': algo['sample_input'],
        'sampleOutput': algo['sample_output'],
        'hints': algo['hints'],
        'tags': to_list(algo['tags']),
        'source': algo['source'],
        'submitCount': algo['submit_count'],
        'acceptedCount': algo['accepted_count'],
        'samples': list(cases.rows),
        'knowledge': kd or None,
        'myBest': my_best,
    })


@router.get('/{aid}/solution')
def solution(aid: str, request: Request, user: dict = Depends(current_user)):
    """参考答案。支持 ?lang= 指定语言。

    一题可能只有 Python 的参考代码（库里 200 道题原本都是 Python），
    这时返回 available 列表告诉前端哪些语言有、哪些没有 —— 如实说没有，
    别拿 Python 的代码顶着 C 的标签显示。
    """
    if not is_id(aid):
        return fail(400, '题目参数不合法')
    algo = query_one('SELECT id, title, reference_code, reference_language FROM algorithm WHERE id = ?', [aid])
    if not algo:
        return fail(404, '题目不存在')
    rows = query(
        'SELECT language, code FROM algorithm_reference_lang WHERE algorithm_id = ?', [aid]
    ).rows
    by_lang = {r['language']: r['code'] for r in rows}
    want = (request.query_params.get('lang') or '').strip().lower()
    base_lang = (algo['reference_language'] or 'python').lower()
    base_code = algo['reference_code'] or ''
    # 合并：独立表里的多语言答案 + 原字段（主语言），原字段优先级更低
    merged = dict(by_lang)
    if base_code and base_lang not in merged:
        merged[base_lang] = base_code
    # available 的排序与前端 utils/codeTemplates.js 的 LANG_ORDER 一致：
    # C → C++ → Java → Python → JavaScript。抽成常量是为了和 Node 端 (server/src/routes/algorithm.js
    # 的 SOL_LANG_ORDER) 对齐 —— 两边不同序的话前端再排一次就会打架。
    _ORDER = ['c', 'cpp', 'java', 'python', 'javascript']
    available = sorted(merged.keys(), key=lambda l: _ORDER.index(l) if l in _ORDER else 99)
    lang = want if want in merged else (base_lang if base_lang in merged else (available[0] if available else ''))
    return ok({
        'title': algo['title'],
        'code': merged.get(lang, ''),
        'language': lang or base_lang,
        'available': available,
        'tip': '建议先自己写一遍再对照；重点看思路差异，而不是背代码。',
    })


# ==================== 题解（模仿洛谷的「题解区」） ====================
MAX_SOLUTION = 20000


@router.get('/{aid}/solutions')
def list_solutions(aid: str, user: dict = Depends(optional_user)):
    if not is_id(aid):
        return fail(400, '题目参数不合法')
    rows = query(
        'SELECT s.id, s.user_id, s.title, s.content, s.language, s.likes, s.created_at, s.updated_at, '
        'u.username, u.real_name '
        'FROM algorithm_solution s JOIN user u ON u.id = s.user_id '
        'WHERE s.algorithm_id = ? ORDER BY s.likes DESC, s.id DESC LIMIT 50',
        [aid],
    )
    liked = set()
    if user and user.get('id'):
        lk = query('SELECT solution_id FROM algorithm_solution_like WHERE user_id = ?', [user['id']])
        liked = {int(r['solution_id']) for r in lk.rows}
    out = []
    for r in rows.rows:
        out.append({
            'id': r['id'],
            'title': r['title'] or ('题解 #' + str(r['id'])),
            'content': r['content'],
            'language': r['language'],
            'likes': int(r['likes'] or 0),
            'author': r['real_name'] or r['username'] or '匿名',
            'isMine': bool(user and r['user_id'] == user['id']),
            'liked': int(r['id']) in liked,
            'createdAt': r['created_at'],
        })
    return ok(out)


@router.post('/{aid}/solutions')
def add_solution(aid: str, request: Request, user: dict = Depends(current_user)):
    if not is_id(aid):
        return fail(400, '题目参数不合法')
    algo = query_one('SELECT id FROM algorithm WHERE id = ? AND status = 1', [aid])
    if not algo:
        return fail(404, '题目不存在或已下架')
    body = body_of(request)
    content = clamp_text(body.get('content'), MAX_SOLUTION).strip()
    if len(content) < 10:
        return fail(400, '题解内容太短了，至少写 10 个字说明思路')
    title = clamp_text(body.get('title'), 200).strip() or content.split('\n')[0][:40]
    lang = str(body.get('language') or 'python').lower()
    if lang not in LANGS:
        lang = 'python'
    r = query(
        'INSERT INTO algorithm_solution (algorithm_id, user_id, title, content, language) VALUES (?, ?, ?, ?, ?)',
        [algo['id'], user['id'], title, content, lang],
    )
    return ok({'id': r.insert_id}, message='题解已发布')


@router.delete('/solutions/{sid}')
def delete_solution(sid: str, user: dict = Depends(current_user)):
    if not is_id(sid):
        return fail(400, '参数不合法')
    row = query_one('SELECT id, user_id FROM algorithm_solution WHERE id = ?', [sid])
    if not row:
        return fail(404, '题解不存在')
    if row['user_id'] != user['id'] and user.get('role') != 'admin':
        return fail(403, '只能删除自己发布的题解')
    query('DELETE FROM algorithm_solution_like WHERE solution_id = ?', [sid])
    query('DELETE FROM algorithm_solution WHERE id = ?', [sid])
    return ok(message='已删除')


@router.post('/solutions/{sid}/like')
def like_solution(sid: str, user: dict = Depends(current_user)):
    if not is_id(sid):
        return fail(400, '参数不合法')
    row = query_one('SELECT id FROM algorithm_solution WHERE id = ?', [sid])
    if not row:
        return fail(404, '题解不存在')
    hit = query_one(
        'SELECT id FROM algorithm_solution_like WHERE solution_id = ? AND user_id = ?',
        [sid, user['id']],
    )
    if hit:
        query('DELETE FROM algorithm_solution_like WHERE id = ?', [hit['id']])
        liked = False
    else:
        query('INSERT INTO algorithm_solution_like (solution_id, user_id) VALUES (?, ?)', [sid, user['id']])
        liked = True
    cnt = query_one('SELECT COUNT(*) AS c FROM algorithm_solution_like WHERE solution_id = ?', [sid])
    likes = int(cnt['c'] or 0) if cnt else 0
    query('UPDATE algorithm_solution SET likes = ? WHERE id = ?', [likes, sid])
    return ok({'liked': liked, 'likes': likes})


@router.post('/{aid}/run')
def run_code(aid: str, request: Request, user: dict = Depends(current_user)):
    """运行代码：只跑样例用例，不计提交、不计分数（「运行」与「提交」分离）"""
    body = body_of(request)
    if not is_id(aid):
        return fail(400, '题目参数不合法')
    language = body.get('language') or 'python'
    code_src = body.get('code')
    lang = str(language).lower()
    if lang not in LANGS:
        return fail(400, f"不支持的语言：{language}，可选 {' / '.join(LANGS.keys())}")

    src = clamp_text(code_src, MAX_CODE)
    if not src.strip():
        return fail(400, '代码不能为空')
    if len(src.strip()) < 5:
        return fail(400, '代码太短了，请写出完整解法')

    # 控制台里敲的输入：自动补末尾换行（等价于终端里敲完再按回车），长度同上限位
    stdin_text = body.get('stdin') if isinstance(body.get('stdin'), str) else ''
    if len(stdin_text) > MAX_INPUT:
        return fail(400, f'自定义输入过长（{len(stdin_text)} 字符），上限 {MAX_INPUT}')
    feed = (stdin_text + '\n') if (stdin_text and not stdin_text.endswith('\n')) else stdin_text

    algo = query_one('SELECT id, title FROM algorithm WHERE id = ? AND status = 1', [aid])
    if not algo:
        return fail(404, '题目不存在或已下架')

    try:
        if feed.strip():
            # 自定义输入：只跑这一组、不比对答案，题目配没配用例都不影响
            result = judge([{'stdin': feed, 'expected': ''}], lang, src, free=True)
        else:
            # 没输入就按老规矩跑样例用例（题面展示的那组）；没有标记样例时退化为前 3 个用例
            cases = query(
                'SELECT stdin, expected FROM algorithm_case WHERE algorithm_id = ? AND is_sample = 1 ORDER BY sort_no, id LIMIT ?',
                [aid, MAX_CASES],
            )
            if not cases.rows:
                cases = query(
                    'SELECT stdin, expected FROM algorithm_case WHERE algorithm_id = ? ORDER BY sort_no, id LIMIT 3',
                    [aid],
                )
            if not cases.rows:
                return fail(500, '这道题目还没有配置测试用例，暂时无法运行')
            result = judge(list(cases.rows), lang, src)
    except Exception as e:
        return fail(500, '运行执行失败：' + str(e))

    free_mode = result['status'] == 'custom'
    # 注意：不写 algorithm_submit、不累加 submit_count / accepted_count
    return ok({
        'sample': True,
        'custom': free_mode,
        'status': result['status'],
        'passed': 0 if free_mode else result['passed'],
        'total': 0 if free_mode else result['total'],
        'runtime': result['runtime'],
        'message': result['message'],
        'consoleLog': result.get('consoleLog', ''),
        # 自定义输入时不给失败用例表 —— 那套「输入/期望/实际」是判题口径，这里没有标准答案
        'cases': [] if free_mode else [r for r in result['results'] if not r['ok']][:3],
    })


@router.post('/{aid}/submit')
def submit(aid: str, request: Request, user: dict = Depends(current_user)):
    body = body_of(request)
    if not is_id(aid):
        return fail(400, '题目参数不合法')
    language = body.get('language') or 'python'
    code_src = body.get('code')
    lang = str(language).lower()
    if lang not in LANGS:
        return fail(400, f"不支持的语言：{language}，可选 {' / '.join(LANGS.keys())}")

    src = clamp_text(code_src, MAX_CODE)
    if not src.strip():
        return fail(400, '代码不能为空')
    if len(src.strip()) < 5:
        return fail(400, '代码太短了，请写出完整解法')

    algo = query_one('SELECT id, title, weight FROM algorithm WHERE id = ? AND status = 1', [aid])
    if not algo:
        return fail(404, '题目不存在或已下架')

    cases = query(
        'SELECT stdin, expected FROM algorithm_case WHERE algorithm_id = ? ORDER BY sort_no, id LIMIT ?',
        [aid, MAX_CASES],
    )
    if not cases.rows:
        return fail(500, '这道题目还没有配置测试用例，暂时无法判题')

    try:
        result = judge(list(cases.rows), lang, src)
    except Exception as e:
        return fail(500, '判题执行失败：' + str(e))

    weight = int(algo['weight'] or 0) or 10
    score = weight if result['status'] == 'accepted' else round_half_up(weight * result['passed'] / (result['total'] or 1))

    query(
        'INSERT INTO algorithm_submit '
        '(user_id, algorithm_id, language, code, status, passed, total, score, max_score, runtime, message) '
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        [user['id'], algo['id'], lang, src[:20000], result['status'], result['passed'], result['total'],
         score, weight, result['runtime'], str(result['message'] or '')[:2000]],
    )
    query('UPDATE algorithm SET submit_count = submit_count + 1 WHERE id = ?', [algo['id']])
    if result['status'] == 'accepted':
        done = query_one(
            "SELECT COUNT(*) AS c FROM algorithm_submit WHERE user_id = ? AND algorithm_id = ? AND status = 'accepted'",
            [user['id'], algo['id']],
        )
        # 首次通过才 +1，避免重复计数
        if int(done['c'] or 0) == 1:
            query('UPDATE algorithm SET accepted_count = accepted_count + 1 WHERE id = ?', [algo['id']])

    return ok({
        'status': result['status'],
        'passed': result['passed'],
        'total': result['total'],
        'score': score,
        'maxScore': weight,
        'runtime': result['runtime'],
        'message': result['message'],
        'consoleLog': result.get('consoleLog', ''),
        # 只回传前 3 个失败用例的细节，避免一次刷屏
        'cases': [r for r in result['results'] if not r['ok']][:3],
    })


@router.get('/{aid}/my')
def my_submits(aid: str, user: dict = Depends(current_user)):
    if not is_id(aid):
        return fail(400, '题目参数不合法')
    # 带上 code：前端「提交记录 → 载入代码」需要把历史提交回填到编辑器，
    # 这样学生可以从上次写到一半的地方继续（之前只回 id/状态，没法参考）。
    rows = query(
        'SELECT id, language, status, passed, total, score, max_score, runtime, message, code, created_at '
        'FROM algorithm_submit WHERE user_id = ? AND algorithm_id = ? ORDER BY id DESC LIMIT 20',
        [user['id'], aid],
    )
    out = []
    for r in rows.rows:
        item = dict(r)
        code = str(item.get('code') or '')
        item['codeLength'] = len(code)
        # 列表页不必把整段代码回传（20 条 × 20KB 会明显拖慢），
        # 只回前 4000 字符足以回填编辑器；超出部分提示用户。
        item['code'] = code[:4000]
        item['truncated'] = len(code) > 4000
        out.append(item)
    return ok(out)


# ==================== 算法小助手 ====================
ASSISTANT_SYSTEM = '''你是算法小助手，服务于计算机专业学生。要求：
1. 先讲清题目在求什么、输入输出是什么，再讲思路，最后给代码。
2. 讲解要给出时间与空间复杂度，并指出常见边界（空输入、n=1、重复元素、极大值）。
3. 用户贴了代码时，指出具体哪几行有问题、为什么、怎么改，不要泛泛而谈。
4. 不要直接替用户完成作业以外的请求；鼓励用户先自己写。
5. 用中文回答，条理清晰，代码要有注释。'''


@router.post('/assistant')
def assistant(request: Request, user: dict = Depends(current_user)):
    body = body_of(request)
    algorithm_id = body.get('algorithmId')
    if not (body.get('question') or body.get('code') or algorithm_id):
        return fail(400, '请描述你的问题，或选择一道题目让我讲解')

    c = _assistant_ctx(body)
    algo = c['algo']

    answer = ''
    llm_mode = 'fallback'
    if os.getenv('LLM_API_KEY'):
        try:
            answer = call_llm([
                {'role': 'system', 'content': ASSISTANT_SYSTEM},
                {'role': 'user', 'content': c['userPrompt']},
            ], 0.4)
            if answer:
                llm_mode = 'llm'
        except Exception:
            answer = ''

    # 未配置大模型时，基于题目自带的提示给出可用的讲解，而不是空着
    if not answer:
        answer = _local_explain(algo, c['q'], c['src'], c['mode'])

    return ok({
        'answer': answer,
        'reasoning': c['reasoning'],
        'mode': llm_mode,
        'algorithm': {'id': algo['id'], 'title': algo['title'], 'difficulty': algo['difficulty']} if algo else None,
    })


def _assistant_ctx(body):
    """算法小助手的公共上下文：题面 + 用户代码 + 提问 → 提示词与推理链"""
    algorithm_id = body.get('algorithmId')
    question = body.get('question') or ''
    code_src = body.get('code') or ''
    mode = body.get('mode') or 'explain'
    q = clamp_text(question, 2000).strip()
    src = clamp_text(code_src, 8000)

    algo = None
    if is_id(algorithm_id):
        algo = query_one(
            'SELECT id, title, description, hints, tags, difficulty, input_desc, output_desc, reference_code '
            'FROM algorithm WHERE id = ?',
            [algorithm_id],
        )

    reasoning = build_algo_reasoning({
        'title': algo['title'] if algo else q,
        'tags': '、'.join(to_list(algo['tags'])) if algo else '',
        'difficulty': algo['difficulty'] if algo else 3,
        'mode': 'debug' if src else mode,
    })

    ctx = []
    if algo:
        ctx.append(f"【题目】{algo['title']}")
        ctx.append(f"【难度】{DIFF_TEXT.get(algo['difficulty'], '中等')}（{algo['difficulty']}/5）")
        if algo['tags']:
            ctx.append(f"【标签】{algo['tags']}")
        if algo['description']:
            ctx.append(f"【题面】{str(algo['description'])[:1200]}")
        if algo['hints']:
            ctx.append(f"【官方提示】{algo['hints']}")
    if src:
        ctx.append(f'【用户代码】\n{src}')
    if q:
        ctx.append(f'【用户问题】{q}')

    return {
        'algo': algo, 'q': q, 'src': src, 'mode': mode,
        'reasoning': reasoning,
        'userPrompt': '\n'.join(ctx) or q,
    }


@router.post('/assistant/stream')
def assistant_stream(request: Request, user: dict = Depends(current_user)):
    """算法小助手的逐字流式版本（事件格式与 /agent/chat/stream 一致）"""
    body = body_of(request)
    algorithm_id = body.get('algorithmId')
    if not (body.get('question') or body.get('code') or algorithm_id):
        return fail(400, '请描述你的问题，或选择一道题目让我讲解')

    c = _assistant_ctx(body)

    def gen():
        yield _sse({
            'type': 'meta',
            'mode': 'llm',
            'reasoning': c['reasoning'],
            'algorithm': {'id': c['algo']['id'], 'title': c['algo']['title'], 'difficulty': c['algo']['difficulty']}
            if c['algo'] else None,
        })
        acc = ''
        started = False
        mode = 'llm'
        if os.getenv('LLM_API_KEY'):
            try:
                for piece in stream_llm([
                    {'role': 'system', 'content': ASSISTANT_SYSTEM},
                    {'role': 'user', 'content': c['userPrompt']},
                ], 0.4):
                    started = True
                    acc += piece
                    yield _sse({'type': 'delta', 'content': piece})
            except Exception:
                started = False
        if not started:
            mode = 'fallback'
            acc = _local_explain(c['algo'], c['q'], c['src'], c['mode'])
            yield _sse({'type': 'delta', 'content': acc})
        yield _sse({'type': 'done', 'mode': mode})

    return StreamingResponse(gen(), media_type='text/event-stream', headers={
        'Cache-Control': 'no-cache, no-transform',
        'X-Accel-Buffering': 'no',
    })


def _sse(payload):
    return 'data: ' + json.dumps(payload, ensure_ascii=False) + '\n\n'


def _local_explain(algo, question, code_src, mode):
    """本地降级讲解：利用题目自带的 hints / 标签 / 参考答案结构"""
    parts = []
    if mode == 'debug' and code_src:
        parts.append('我看了你贴的代码，下面按「先定位问题 → 再说怎么改」的顺序说。')
        parts.append('')
        lines = code_src.split('\n')
        suspects = []
        for i, line in enumerate(lines):
            if re.search(r'while\s*\(true\)|for\s*\(\s*;', line):
                suspects.append(f'第 {i + 1} 行：{line.strip()} —— 这种写法容易写成死循环，确认循环变量在循环体内被更新。')
            if re.search(r'\bi\s*<=?\s*\w+\.length\b|\bi\s*<=?\s*len\(', line):
                suspects.append(f'第 {i + 1} 行：{line.strip()} —— 注意是否越界，数组/字符串下标最大是 length-1。')
            if re.search(r'=\s*=\s*', line) and not re.search(r'===|==\s*null', line) \
                    and re.search(r'\b(input|next|readline)\b', line):
                suspects.append(f'第 {i + 1} 行：{line.strip()} —— 读取输入时注意类型与去空白。')
        if suspects:
            parts.append('可疑位置：')
            for s in suspects[:5]:
                parts.append('· ' + s)
        else:
            parts.append('单看代码没有发现明显的模式化错误。建议按这几点自查：')
            parts.append('· 读入是否完整（有没有漏掉某一行输入）')
            parts.append('· 边界：n=0 / n=1 / 空串 / 重复元素')
            parts.append('· 输出格式：是否多输出了提示语，行末是否有多余空格')
            parts.append('· 是否真的 return / print 了结果')
        parts.append('')
        parts.append('把报错信息或"期望输出 vs 实际输出"一起发我，我能定位得更准。')
        return '\n'.join(parts)

    if algo:
        parts.append(f"**{algo['title']}**（难度 {DIFF_TEXT.get(algo['difficulty'], '中等')}）")
        parts.append('')
        if algo.get('hints'):
            parts.append('### 解题思路')
            parts.append(str(algo['hints']))
            parts.append('')
        if algo.get('tags'):
            parts.append('### 涉及算法：' + '、'.join(to_list(algo['tags'])))
            parts.append('')
        parts.append('### 建议的做题顺序')
        parts.append('1. 先把输入读全，打印出来确认格式正确；')
        parts.append('2. 用最小样例（比如 n=1）手工推一遍你的算法；')
        parts.append('3. 再考虑边界：空输入、极大值、重复元素；')
        parts.append('4. 最后检查输出是否与要求逐字符一致（不要多打印提示语）。')
        parts.append('')
        parts.append('想看参考实现可以点「查看参考答案」，但建议先自己写一遍——写不出来时看答案的收获会小很多。')
        if question:
            parts.append('')
            parts.append(f'你问的是：{brief(question, 60)}')
            parts.append('（当前为本地知识库模式，配置 LLM_API_KEY 后我可以针对你的问题做更细的讲解。）')
        return '\n'.join(parts)

    parts.append('我可以帮你做这些：')
    parts.append('· 讲解某道算法题的思路与复杂度（先选题目再提问，我能结合题面讲得更准）')
    parts.append('· 看你贴的代码，指出错在哪、怎么改')
    parts.append('· 对比不同解法的复杂度与适用场景')
    parts.append('')
    parts.append('试试：先打开一道算法题，然后在下方把你的问题或代码发给我。')
    return '\n'.join(parts)
