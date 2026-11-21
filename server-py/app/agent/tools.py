"""Agent 工具层（Tool Layer）：7 个标配工具的统一注册表。

为什么要收敛成注册表：
  之前每加一种能力就在 routers/agent.py 里手写一个 tool_xxx()，
  调用点散落在 _prepare_chat 各处 —— 前端既拿不到"这次到底用了哪些工具"，
  也没法单独触发某个工具，更统计不了成功率。
  注册表把「能做什么 / 怎么调 / 调得怎么样」收敛到一处，
  前端的能力清单、工具时间线、可观测统计都从同一份定义生成。

工具返回统一结构（前端时间线直接渲染）：
  {'name','label','ok','ms','summary','data','error'}
"""

import os
import re
import time
from concurrent.futures import ThreadPoolExecutor

from app.agent import rag, vector
from app.db import query, query_one

# ==================== 工具依赖表 ====================
# 声明式写清楚「谁要用谁的结果」，run_tools 据此分层并发。
# 只有真读了上游结果的才需要登记（写工具时顺手登记，别凭直觉填）：
#   draw_diagram 会复用 kb_search 命中的知识点来画步骤图，
#   没有也能自己再查一次，所以是「软依赖」——有就省一次检索，没有也不出错。
# 其余工具各自查库，谁都不等谁。
TOOL_DEPENDS = {
    'draw_diagram': ['kb_search'],
}

# 并发上限：一次提问最多 7 个工具，给 8 个槽位足够，不抢数据库连接。
MAX_WORKERS = 8


# ==================== 工具 1：知识库检索（RAG） ====================
def search_knowledge(question: str, top_k: int = 5):
    """向量检索 + 关键词检索融合（量纲归一化后加权）。"""
    try:
        vec_docs = vector.search(question, top_k)
    except Exception:
        vec_docs = []
    try:
        kw_docs = rag.search(question, top_k)
    except Exception:
        kw_docs = []

    def normalize(ls):
        """量纲归一化：向量检索返回 0~1 余弦值，关键词检索返回命中次数，
        直接相加会让关键词碾压余弦（曾导致"内存不够了怎么换页"被判给 malloc）。"""
        mx = max([float(d.get('score') or 0) for d in (ls or [])] or [0]) or 1e-9
        return [dict(d, score=(float(d.get('score') or 0)) / mx) for d in (ls or [])]

    fused = {}

    def push(ls, weight):
        for i, d in enumerate(ls or []):
            rank_bonus = (len(ls) - i) * 0.05
            cur = fused.get(d.get('id')) or {'doc': d, 'score': 0}
            cur['score'] += (float(d.get('score') or 0)) * weight + rank_bonus
            fused[d.get('id')] = cur

    push(normalize(vec_docs), 1.0)
    push(normalize(kw_docs), 0.6)
    ranked = sorted(fused.values(), key=lambda x: x['score'], reverse=True)
    return [x['doc'] for x in ranked[:top_k]]


def _t_kb_search(args, ctx):
    q = str(args.get('query') or ctx.get('question') or '').strip()
    if not q:
        return {'summary': '没有可检索的内容', 'data': {'docs': []}}
    top_k = max(1, min(int(args.get('topK') or 5), 10))
    docs = search_knowledge(q, top_k)
    names = [d.get('name') for d in docs[:3] if d.get('name')]
    return {
        'summary': ('命中 %d 个知识点：%s' % (len(docs), '、'.join(names))) if docs else '知识库未命中',
        'data': {'docs': docs},
    }


# ==================== 工具 2：代码执行 ====================
LANG_HINT = [
    (r'#include\s*<iostream>|std::|cout\s*<<', 'cpp'),
    (r'#include\s*<stdio\.h>|printf\s*\(|int\s+main\s*\(', 'c'),
    (r'\bdef\s+\w+|import\s+\w+|print\s*\(', 'python'),
    (r'\bpublic\s+class\b|System\.out\.print', 'java'),
    (r'\bfunction\b|\bconst\b|\blet\b|console\.log|=>', 'javascript'),
]

COMPLEXITY_HINT = [
    (r'\bfor\b.*\bfor\b|\bwhile\b.*\bwhile\b', '存在嵌套循环，复杂度通常不低于 O(n²)'),
    (r'\bquickSort\b|\bbinarySearch\b|\bmergeSort\b', '疑似分治/二分，复杂度常见 O(n log n) 或 O(log n)'),
    (r'\brecursive\b|return\s+\w+\s*\(', '存在递归调用，注意递归深度与重复子问题'),
]


def guess_lang(code: str):
    for pattern, lang in LANG_HINT:
        if re.search(pattern, code):
            return lang
    return 'c'


def _t_code_run(args, ctx):
    code = str(args.get('code') or '').strip()
    if not code:
        return {'summary': '未提供代码', 'data': None}
    if len(code) > 8000:
        return {'summary': '代码过长（上限 8000 字符）', 'data': None}

    lang = str(args.get('language') or '').lower() or guess_lang(code)
    algo = rag.detect_algo_from_code(code) or None
    lines = [l for l in code.splitlines() if l.strip()]
    hints = [h for p, h in COMPLEXITY_HINT if re.search(p, code, re.I | re.S)]

    data = {
        'language': lang,
        'algo': algo,
        'lines': len(lines),
        'charCount': len(code),
        'complexityHints': hints,
        'executed': False,
        'output': '',
        'error': None,
    }

    # 真正执行受 CODE_RUN 开关控制（与 /code/run 同一开关）：
    # 关闭时只做静态解析，绝不偷偷起子进程。
    if os.getenv('CODE_RUN') == '0':
        data['reason'] = '在线运行已由管理员关闭，仅做静态解析'
    else:
        try:
            from app.routers import code as code_mod
            if lang not in code_mod.LANGS:
                data['reason'] = '暂不支持运行该语言，仅做静态解析'
            else:
                r = code_mod.execute(lang, code, (ctx.get('user_id') or 0))
                data.update({
                    'executed': True,
                    'output': (r.get('output') or '')[:2000],
                    'stderr': (r.get('stderr') or '')[:800],
                    'error': bool(r.get('error')),
                    'runMs': r.get('time'),
                    'unsupported': bool(r.get('unsupported')),
                })
        except Exception as e:  # 执行环境异常不能拖垮整次对话
            data['reason'] = '运行环境不可用：' + str(e)[:120]

    summary = '识别为 %s 代码（%d 行）' % (lang, len(lines))
    if algo:
        summary += '，疑似算法：' + algo
    if data.get('executed'):
        summary += '，已运行：' + ('成功' if not data.get('error') else '报错')
    return {'summary': summary, 'data': data}


# ==================== 工具 3：公式渲染（LaTeX 校验） ====================
# 只做「结构校验 + 归一化」，真正的排版交给前端 KaTeX：
# 后端拼 HTML 再塞进 v-html 会绕过 DOMPurify 的既定清洗链路。
DANGEROUS_TEX = re.compile(r'\\(href|url|includegraphics|input|write18|immediate|openout|catcode)', re.I)


def _t_render_formula(args, ctx):
    latex = str(args.get('latex') or '').strip()
    if not latex:
        m = re.search(r'\$\$(.+?)\$\$', str(ctx.get('question') or ''), re.S)
        if m:
            latex = m.group(1).strip()
            display = True
        else:
            m = re.search(r'(?<!\$)\$(?!\$)([^$\n]+?)\$', str(ctx.get('question') or ''))
            latex = m.group(1).strip() if m else ''
            display = False
    else:
        display = str(args.get('display') or 'block') != 'inline'

    if not latex:
        return {'summary': '没有检测到公式', 'data': None}
    if len(latex) > 500:
        return {'summary': '公式过长（上限 500 字符）', 'data': None}
    if DANGEROUS_TEX.search(latex):
        # \href / \includegraphics 之类会被 KaTeX 渲染成可点击链接或外链图片，
        # 公式又来自大模型输出，属于不可信内容，一律拦掉。
        return {'summary': '公式包含不安全的宏（如 \\href、\\includegraphics），已拒绝渲染', 'data': None}

    if latex.count('{') != latex.count('}'):
        return {'summary': '公式括号不配对，无法渲染', 'data': None}
    if latex.count('\\left') != latex.count('\\right'):
        return {'summary': '\\left 与 \\right 不配对，无法渲染', 'data': None}

    return {
        'summary': '公式合法，可由前端 KaTeX 渲染',
        'data': {'latex': latex, 'display': display},
    }


# ==================== 工具 4：绘图（Mermaid） ====================
NUM_STEP = re.compile(r'^\s*[（(]?\d{1,2}[)）、.。]\s*(.+)$')
CN_STEP = re.compile(r'^\s*[一二三四五六七八九]{1,2}[、.]\s*(.+)$')


def _clean_node(text, limit=22):
    """Mermaid 节点文本：去掉 markdown 记号与会破坏语法的引号/括号。"""
    t = re.sub(r'[*_`#>|\[\]{}()]', '', str(text or ''))
    t = re.sub(r'\s+', ' ', t).strip()
    return (t[:limit] + '…') if len(t) > limit else t


def _extract_steps(text, limit=6):
    steps = []
    for line in str(text or '').splitlines():
        m = NUM_STEP.match(line) or CN_STEP.match(line)
        if m:
            node = _clean_node(m.group(1))
            if node and node not in steps:
                steps.append(node)
        if len(steps) >= limit:
            break
    return steps


def _t_draw_diagram(args, ctx):
    topic = str(args.get('topic') or ctx.get('question') or '').strip()
    if not topic:
        return {'summary': '没有可绘图的主题', 'data': None}

    docs = (ctx.get('docs') or []) or search_knowledge(topic, 3)
    primary = docs[0] if docs else None
    title = _clean_node(primary.get('name') if primary else topic, 18) or _clean_node(topic, 18)

    steps = []
    for d in docs[:2]:
        steps = _extract_steps(str(d.get('content') or ''))
        if len(steps) >= 2:
            break
    if len(steps) < 2:
        # 知识库没有分步骤写法时退回「按句号切分摘要」，绝不凭空编流程节点
        summary = str((primary or {}).get('summary') or '')
        steps = [_clean_node(s) for s in re.split(r'[。；;]', summary) if s.strip()][:4]

    if len(steps) < 2:
        return {'summary': '知识库内容不足以生成流程图，已跳过绘图', 'data': None}

    nodes = ['  S%d["%d. %s"]' % (i, i + 1, s) for i, s in enumerate(steps)]
    edges = '\n'.join(['  S%d --> S%d' % (i, i + 1) for i in range(len(steps) - 1)])
    code = '\n'.join(['flowchart LR'] + nodes + [edges])
    return {
        'summary': '已生成「%s」流程图（%d 步）' % (title, len(steps)),
        'data': {
            'type': 'mermaid',
            'title': title,
            'code': '```mermaid\n%s\n```' % code,
            'steps': steps,
        },
    }


# ==================== 工具 5：习题生成 ====================
def _t_quiz_generate(args, ctx):
    try:
        count = max(1, min(int(args.get('count') or 3), 10))
    except (TypeError, ValueError):
        count = 3
    kid = args.get('knowledgeId') or (ctx.get('primary') or {}).get('id')
    course_id = args.get('courseId')

    where = ['q.id IS NOT NULL']
    params = []
    if kid:
        where.append('q.knowledge_id = ?')
        params.append(kid)
    if course_id:
        where.append('k.course_id = ?')
        params.append(course_id)
    elif not kid:
        # 没指定范围时，优先出「用户错过的知识点」的题 —— 这才是量身定制
        weak = query_one(
            'SELECT q.knowledge_id AS kid FROM wrong_question w JOIN question q ON q.id = w.question_id '
            'WHERE w.user_id = ? ORDER BY w.wrong_count DESC LIMIT 1',
            [ctx.get('user_id') or 0],
        )
        if weak and weak.get('kid'):
            where.append('q.knowledge_id = ?')
            params.append(weak['kid'])

    rows = query(
        'SELECT q.id, q.title, q.type, q.options, q.difficulty, q.knowledge_id, '
        'k.name AS knowledge_name, c.name AS course_name '
        'FROM question q JOIN knowledge k ON k.id = q.knowledge_id '
        'JOIN course c ON c.id = k.course_id '
        'WHERE ' + ' AND '.join(where) + ' ORDER BY RAND() LIMIT ?',
        params + [count],
    )
    items = []
    for r in rows.rows:
        # 刻意不带 answer：助手直接给答案会让学生跳过思考，也不符合"引导式讲解"定位
        items.append({
            'id': r['id'],
            'title': r['title'],
            'type': r['type'],
            'options': r['options'],
            'difficulty': r['difficulty'],
            'knowledgeId': r['knowledge_id'],
            'knowledgeName': r['knowledge_name'],
            'courseName': r['course_name'],
        })
    if not items:
        return {'summary': '题库里暂时没有匹配的题目', 'data': {'questions': []}}
    k_name = items[0].get('knowledgeName')
    return {
        'summary': '已挑 %d 道%s的题' % (len(items), ('「%s」' % k_name) if k_name else ''),
        'data': {'questions': items},
    }


# ==================== 工具 6：错题记录 ====================
def _t_wrong_record(args, ctx):
    uid = ctx.get('user_id') or 0
    action = str(args.get('action') or 'list').lower()

    if action == 'add':
        qid = args.get('questionId')
        if not qid:
            return {'summary': '缺少题目 id', 'data': None}
        exists = query_one('SELECT id, title FROM question WHERE id = ?', [qid])
        if not exists:
            return {'summary': '题目不存在', 'data': None}
        query(
            'INSERT INTO wrong_question (user_id, question_id, wrong_count, last_wrong_time) '
            'VALUES (?, ?, 1, NOW()) '
            'ON DUPLICATE KEY UPDATE wrong_count = wrong_count + 1, last_wrong_time = NOW()',
            [uid, qid],
        )
        return {'summary': '已记入错题本：%s' % str(exists['title'])[:20], 'data': {'questionId': qid}}

    if action == 'remove':
        qid = args.get('questionId')
        if qid:
            query('DELETE FROM wrong_question WHERE user_id = ? AND question_id = ?', [uid, qid])
            return {'summary': '已从错题本移除', 'data': {'questionId': qid}}
        query('DELETE FROM wrong_question WHERE user_id = ?', [uid])
        return {'summary': '已清空错题本', 'data': None}

    limit = max(1, min(int(args.get('limit') or 5), 20))
    rows = query(
        'SELECT k.id, k.name, k.route, c.name AS course_name, w.wrong_count, w.last_wrong_time '
        'FROM wrong_question w JOIN question q ON q.id = w.question_id '
        'JOIN knowledge k ON k.id = q.knowledge_id JOIN course c ON c.id = k.course_id '
        'WHERE w.user_id = ? ORDER BY w.wrong_count DESC, w.last_wrong_time DESC LIMIT ?',
        [uid, limit],
    )
    items = [dict(r) for r in rows.rows]
    if not items:
        return {'summary': '错题本是空的，继续保持', 'data': {'items': []}}
    return {
        'summary': '错题集中在：' + '、'.join([i['name'] for i in items[:3]]),
        'data': {'items': items},
    }


# ==================== 工具 7：学习计划生成 ====================
def _t_study_plan(args, ctx):
    uid = ctx.get('user_id') or 0
    try:
        days = max(1, min(int(args.get('days') or 7), 30))
    except (TypeError, ValueError):
        days = 7

    weak = query(
        'SELECT k.id, k.name, k.route, c.name AS course_name, w.wrong_count '
        'FROM wrong_question w JOIN question q ON q.id = w.question_id '
        'JOIN knowledge k ON k.id = q.knowledge_id JOIN course c ON c.id = k.course_id '
        'WHERE w.user_id = ? ORDER BY w.wrong_count DESC, w.last_wrong_time DESC LIMIT ?',
        [uid, days],
    )
    weak_list = [dict(r) for r in weak.rows]

    # 错题不够排满计划时，用「还没学过的知识点」补齐，避免后几天空转
    rest = []
    if len(weak_list) < days:
        rows = query(
            'SELECT k.id, k.name, k.route, c.name AS course_name FROM knowledge k '
            'JOIN course c ON c.id = k.course_id '
            'WHERE k.id NOT IN (SELECT DISTINCT knowledge_id FROM study_record WHERE user_id = ?) '
            'ORDER BY c.id, k.id LIMIT ?',
            [uid, days - len(weak_list)],
        )
        rest = [dict(r) for r in rows.rows]

    plan = []
    for i in range(days):
        if i < len(weak_list):
            it = weak_list[i]
            focus = '复习薄弱点：%s（错 %s 次）' % (it['name'], it['wrong_count'])
            item = it
        elif rest:
            item = rest.pop(0)
            focus = '新知识点：%s' % item['name']
        else:
            focus = '综合复盘：重做本周错题'
            item = None
        plan.append({
            'day': i + 1,
            'focus': focus,
            'knowledgeId': item['id'] if item else None,
            'route': item.get('route') if item else None,
            'courseName': item.get('course_name') if item else '',
            'tasks': [
                '看一遍可视化动画（单步执行走完整流程）',
                '做 5 道配套题，错题自动进错题本',
                '用自己的话复述一遍核心思路',
            ],
        })

    lines = ['## %d 天学习计划' % days, '']
    for p in plan:
        lines.append('**第 %d 天** — %s' % (p['day'], p['focus']))
        for t in p['tasks']:
            lines.append('- ' + t)
        lines.append('')
    return {
        'summary': '已生成 %d 天计划（%d 个来自错题）' % (days, len(weak_list)),
        'data': {'days': days, 'plan': plan, 'markdown': '\n'.join(lines)},
    }


# ==================== 注册表 ====================
TOOLS = [
    {
        'name': 'kb_search',
        'label': '知识库检索',
        'desc': '在课程知识库里找出与你的问题最相关的知识点，再基于它作答',
        'params': [{'name': 'query', 'desc': '检索词（默认用你的提问）'}, {'name': 'topK', 'desc': '条数，默认 5'}],
    },
    {
        'name': 'code_run',
        'label': '代码执行/解析',
        'desc': '识别你贴的代码属于哪种语言与算法，开关打开时直接跑一遍看输出',
        'params': [{'name': 'code', 'desc': '代码正文'}, {'name': 'language', 'desc': '语言（可省略自动识别）'}],
    },
    {
        'name': 'render_formula',
        'label': '公式渲染',
        'desc': '校验并渲染 LaTeX 公式，危险的宏（如 \\href）会被拦下',
        'params': [{'name': 'latex', 'desc': '公式源码'}, {'name': 'display', 'desc': 'block / inline'}],
    },
    {
        'name': 'draw_diagram',
        'label': '流程图绘制',
        'desc': '把知识点的步骤抽成 Mermaid 流程图，边看边理解',
        'params': [{'name': 'topic', 'desc': '主题（默认用你的提问）'}],
    },
    {
        'name': 'quiz_generate',
        'label': '习题生成',
        'desc': '按知识点或你的错题情况挑几道题（只给题目，不直接给答案）',
        'params': [{'name': 'knowledgeId', 'desc': '知识点 id'}, {'name': 'count', 'desc': '题数，默认 3'}],
    },
    {
        'name': 'wrong_record',
        'label': '错题记录',
        'desc': '查看你的错题分布，也能把某道题加进/移出错题本',
        'params': [{'name': 'action', 'desc': 'list / add / remove'}, {'name': 'questionId', 'desc': '题目 id'}],
    },
    {
        'name': 'study_plan',
        'label': '学习计划',
        'desc': '按你的薄弱点排出一份分天推进的学习计划',
        'params': [{'name': 'days', 'desc': '天数，默认 7'}],
    },
]

_HANDLERS = {
    'kb_search': _t_kb_search,
    'code_run': _t_code_run,
    'render_formula': _t_render_formula,
    'draw_diagram': _t_draw_diagram,
    'quiz_generate': _t_quiz_generate,
    'wrong_record': _t_wrong_record,
    'study_plan': _t_study_plan,
}

_LABEL = {t['name']: t['label'] for t in TOOLS}


def capabilities():
    """前端能力清单用：只暴露说明，不暴露内部实现"""
    return [{'name': t['name'], 'label': t['label'], 'desc': t['desc'], 'params': t['params']} for t in TOOLS]


def run_tool(name: str, args: dict = None, ctx: dict = None):
    """调用单个工具，统一计时与异常兜底。

    任何一个工具炸了都不能拖垮整次对话 —— 工具是"增强"，不是"必经路径"。
    """
    t0 = time.time()
    fn = _HANDLERS.get(name)
    if not fn:
        return {'name': name, 'label': _LABEL.get(name, name), 'ok': False, 'ms': 0,
                'summary': '未注册的工具', 'data': None, 'error': 'UNKNOWN_TOOL'}
    try:
        res = fn(args or {}, ctx or {}) or {}
        out = {
            'name': name,
            'label': _LABEL.get(name, name),
            'ok': True,
            'ms': int((time.time() - t0) * 1000),
            'summary': res.get('summary') or '',
            'data': res.get('data'),
            'error': None,
        }
    except Exception as e:
        out = {
            'name': name,
            'label': _LABEL.get(name, name),
            'ok': False,
            'ms': int((time.time() - t0) * 1000),
            'summary': '工具执行失败',
            'data': None,
            'error': str(e)[:200],
        }
    return out


def _layers(specs):
    """按 TOOL_DEPENDS 把工具分层：同层互不依赖可并发，上层要等下层结果。

    层号 = max(依赖所在层) + 1；没登记依赖的一律第 0 层。
    依赖的工具没出现在本次计划里时按第 0 层算（不存在的东西不用等）。
    """
    names = [n for n, _ in specs]
    order = {}
    for name in names:
        depth = 0
        seen = set()

        def walk(n):
            nonlocal depth
            if n in seen:
                return 0
            seen.add(n)
            deps = [d for d in (TOOL_DEPENDS.get(n) or []) if d in names]
            if not deps:
                return 0
            return 1 + max(walk(d) for d in deps)

        depth = walk(name)
        order[name] = depth
    groups = {}
    for i, (name, _) in enumerate(specs):
        groups.setdefault(order.get(name, 0), []).append(i)
    return [groups[k] for k in sorted(groups)]


def _feed_ctx(ctx, call):
    """把某个工具的结果回喂给 ctx，供下游工具复用（目前只有 docs）。"""
    if not call.get('ok'):
        return
    if call.get('name') == 'kb_search':
        ctx['docs'] = (call.get('data') or {}).get('docs') or []


def run_tools(specs, ctx: dict = None):
    """按 [(name, args), ...] 执行：无依赖的并发跑，有依赖的等上游，返回按原顺序的调用记录。

    为什么要分层而不是一路 await 串行：
      一次提问常要跑 3~4 个工具（检索 / 读错题 / 出题 / 画图），它们大多各自查库、
      谁也不用谁的结果，串行等于把四次数据库往返排队等完。
      分层并发后总耗时由「最慢的一层」决定，而不是所有工具耗时之和。

    两个必须守住的点：
      1) 返回顺序与传入顺序一致 —— 前端时间线按 Planner 的步骤顺序渲染，乱序会让人看不懂；
      2) 单个工具炸了不能拖垮整次对话 —— run_tool 已兜底，这里不再额外处理。
    """
    specs = list(specs or [])
    if not specs:
        return []
    ctx = dict(ctx or {})
    groups = _layers(specs)
    # 只有一层（或仅一个工具）时没必要开线程池，直接跑省掉调度开销
    if len(groups) <= 1 and len(specs) <= 1:
        out = [run_tool(specs[0][0], specs[0][1], ctx)]
        _feed_ctx(ctx, out[0])
        return out

    results = {}
    with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, max(1, len(specs)))) as pool:
        for idxs in groups:
            if len(idxs) == 1:
                i = idxs[0]
                results[i] = run_tool(specs[i][0], specs[i][1], dict(ctx))
                continue
            # 快照 ctx：并发任务只读，避免边跑边改
            futures = {
                pool.submit(run_tool, specs[i][0], dict(specs[i][1] or {}), dict(ctx)): i
                for i in idxs
            }
            for f, i in futures.items():
                results[i] = f.result()
            # 整层跑完再回喂，保证同层工具看到的是同一份输入
            for i in idxs:
                _feed_ctx(ctx, results[i])
    return [results[i] for i in range(len(specs))]
