"""Agent 对话接口：意图识别 → 思考链 → 多工具检索 → 回答。"""

import json
import os
import re
import time

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.agent import guard, rag, report as report_mod
from app.agent import memory as memory_mod
from app.agent import memory_vec
from app.agent import planner, tools as tools_mod, trace, verifier
from app.agent import vector
from app.agent.llm import SYSTEM_PROMPT, call_llm, fallback_answer, stream_llm
from app.agent.reasoning import build_reasoning
from app.core.body import body_of
from app.core.deps import current_user
from app.core.response import fail, ok
from app.db import query, query_one

router = APIRouter()

# 检索入口已统一收敛到 app/agent/tools.py 的注册表（7 个工具之一），
# 这里保留同名别名，避免其它模块的历史调用方式突然失效。
tool_search_knowledge = tools_mod.search_knowledge


# ==================== Agent 工具 ====================
def tool_diagnose(user_id):
    """工具2：学习诊断（读取错题薄弱点）"""
    rows = query(
        'SELECT k.id, k.name, k.route, c.name AS course_name, SUM(w.wrong_count) AS wrong_count '
        'FROM wrong_question w JOIN question q ON q.id = w.question_id '
        'JOIN knowledge k ON k.id = q.knowledge_id JOIN course c ON c.id = k.course_id '
        'WHERE w.user_id = ? '
        'GROUP BY k.id, k.name, k.route, c.name ORDER BY wrong_count DESC LIMIT 5',
        [user_id],
    )
    return list(rows.rows)


def tool_parse_code(text):
    """工具3：代码解析"""
    if not rag.detect_code(text):
        return None
    algo = rag.detect_algo_from_code(text)
    return {'isCode': True, 'algo': algo or None}


def ensure_session(user_id, session_id):
    """取（或创建）会话"""
    if session_id:
        s = query_one('SELECT * FROM chat_session WHERE id = ? AND user_id = ?', [session_id, user_id])
        if s:
            return s['id']
    r = query('INSERT INTO chat_session (user_id, title) VALUES (?, ?)', [user_id, '新对话'])
    return r.insert_id


def load_history(session_id, limit: int = 8):
    """读取历史对话（多轮追问上下文）"""
    if not session_id:
        return []
    rows = query(
        'SELECT question, answer, knowledge_id FROM chat_record '
        'WHERE session_id = ? ORDER BY id DESC LIMIT ?',
        [session_id, limit],
    )
    return list(reversed(rows.rows))


def as_history(v):
    """客户端传来的 history 未必是列表 —— 手一抖写成字符串、数字、null 都会到这儿。

    直接 `for h in x` 会逐字符遍历，接着 h.get() 抛 AttributeError，
    接口退化成 500「服务暂时不可用」。历史消息缺失只影响上下文，
    不该让它吃掉整次提问，所以一律归一成空列表。
    """
    return v if isinstance(v, list) else []


def resolve_context(question, history, last_knowledge):
    """指代消解：用户说"那它的复杂度呢""再讲详细点"时把上一轮知识点带进来。"""
    q = str(question or '').strip()
    pronoun = bool(re.match(
        r'^(那|它|这个|这个呢|再|还有|然后|接着|继续|详细点|再详细|为什么|什么意思|举个例子|为什么这样|它的)', q
    )) and len(q) <= 20
    if pronoun or (re.search(r'(复杂度|时间复杂|空间复杂|详细|再讲|再说说|举个例子)', q) and len(q) <= 24):
        if last_knowledge:
            return {'text': f"{last_knowledge['name']} {q}", 'carried': last_knowledge, 'isFollowUp': True}
        hist = as_history(history)
        if hist:
            last = hist[-1]
            if last.get('question'):
                return {'text': f"{last['question']} {q}", 'carried': None, 'isFollowUp': True}
    return {'text': q, 'carried': None, 'isFollowUp': False}


def save_record(user_id, session_id, question, answer, knowledge_id, mode, intent):
    r = query(
        'INSERT INTO chat_record (user_id, session_id, question, answer, knowledge_id, mode, intent) '
        'VALUES (?, ?, ?, ?, ?, ?, ?)',
        [user_id, session_id, question, answer, knowledge_id, mode, intent or None],
    )
    # 顺手给语义记忆留一条：只记落在具体知识点上的问答，闲聊不记（记了也是噪音）。
    # 这样过几个月再问同一个点，助手还找得到"你当时问的是这个"。
    if knowledge_id:
        try:
            k = query_one('SELECT name FROM knowledge WHERE id = ?', [knowledge_id])
            memory_vec.add(
                user_id, 'chat',
                '【我问过】%s\n【当时的回答】%s' % (str(question)[:300], str(answer)[:500]),
                ref_id=getattr(r, 'insert_id', None),
                knowledge_id=knowledge_id,
                title=(k or {}).get('name') or str(question)[:60],
            )
        except Exception:
            pass


def touch_title(session_id, question):
    query(
        "UPDATE chat_session SET title = ? WHERE id = ? AND (title IS NULL OR title = '' OR title = '新对话')",
        [str(question)[:30], session_id],
    )


def build_actions(primary, weak_points=None):
    actions = []
    if primary:
        actions.append({
            'type': 'navigate',
            'label': f"打开「{primary['name']}」可视化",
            'route': primary['route'],
            'knowledgeId': primary['id'],
        })
        actions.append({
            'type': 'practice',
            'label': f"练习「{primary['name']}」配套习题",
            'route': f"/practice/{primary['id']}",
            'knowledgeId': primary['id'],
        })
    for w in (weak_points or [])[:3]:
        if not primary or w.get('id') != primary.get('id'):
            actions.append({
                'type': 'navigate',
                'label': f"复习「{w['name']}」",
                'route': w.get('route'),
                'knowledgeId': w.get('id'),
            })
    if not primary and not weak_points:
        actions.append({'type': 'navigate', 'label': '去课程中心看看', 'route': '/courses'})
    return actions


# ==================== 工具结果附录 ====================
def _appendix(prep):
    """把工具产出的确定性内容直接拼进答案末尾。

    流程图 / 练习题是工具算出来的，不该让大模型再复述一遍 ——
    复述就可能编造不存在的步骤或题目。让模型只讲思路，工具产物原样附上。
    """
    parts = []
    d = prep.get('diagram')
    if d and d.get('code'):
        steps = d.get('steps') or []
        steps_md = '\n'.join([f'{i + 1}. {s}' for i, s in enumerate(steps)])
        parts.append('### 流程图\n\n' + d['code'] + ('\n\n' + steps_md if steps_md else ''))

    quiz = prep.get('quiz') or []
    if quiz:
        lines = ['### 配套练习（先自己想，做完再对答案）']
        for i, it in enumerate(quiz):
            lines.append(f"{i + 1}. {it.get('title')}")
            if it.get('options'):
                lines.append('   ' + str(it['options'])[:240])
        parts.append('\n'.join(lines))

    sp = prep.get('studyPlan')
    if sp and sp.get('markdown') and prep['intent']['type'] != 'plan':
        parts.append(sp['markdown'])

    return '\n\n' + '\n\n'.join(parts) if parts else ''


def _finalize(prep, answer):
    """输出校验（安全兜底 + 幻觉标注 + 来源脚注），返回 (最终文本, 校验结果)"""
    checked = verifier.check(answer, {
        'docs': prep['docs'],
        # 闲聊类本就没有知识库依据，不该被扣上"可能幻觉"的帽子
        'allowGeneral': prep['intent']['type'] in ('greeting', 'chitchat', 'encourage'),
    })
    text = checked['answer'] + _appendix(prep) + verifier.footnote(checked['sources'])
    return text, checked


# ==================== 主对话接口 ====================
def _prepare_chat(uid, raw_q, client_history, session_id, options=None):
    """对话前置处理：会话、意图、任务规划、工具调用、上下文组装。

    /chat（一次性返回）与 /chat/stream（逐字流式）共用这一段，
    避免两条链路各写一份、改一边漏一边。

    options: {'style': 'concise'|'detailed', 'useMemory': bool, 'latex': str}
    """
    options = options or {}
    t0 = time.time()
    sid = ensure_session(uid, session_id)
    # useMemory 显式关闭时不读历史：学生想"从头问一遍"时不该被上文牵着走
    history = [] if options.get('useMemory') is False else load_history(sid)

    last_rec = query_one(
        'SELECT k.id, k.name, k.route FROM chat_record cr '
        'JOIN knowledge k ON k.id = cr.knowledge_id '
        'WHERE cr.session_id = ? AND cr.knowledge_id IS NOT NULL ORDER BY cr.id DESC LIMIT 1',
        [sid],
    )
    ctx = resolve_context(raw_q, history, last_rec)
    q = ctx['text']

    intent = guard.classify_intent(raw_q)
    reasoning = build_reasoning({'question': raw_q, 'intent': intent, 'history': history})
    plan = planner.build_plan(intent, q, {'primary': ctx['carried'] or None})

    prep = {
        'sid': sid,
        'history': history,
        'intent': intent,
        'reasoning': reasoning,
        'plan': plan,
        'isFollowUp': bool(ctx['isFollowUp']),
        'primary': ctx['carried'] or None,
        'weakPoints': [],
        'related': [],
        'docs': [],
        'codeInfo': None,
        'codeKnowledge': None,
        'codeRun': None,
        'quiz': [],
        'diagram': None,
        'studyPlan': None,
        'formula': None,
        'toolCalls': [],
        'kind': 'llm',
        'localAnswer': '',
        'llmMessages': None,
        'clientHistory': client_history or [],
        'userPrompt': '',
        'report': None,
        'policy': 'normal',
        'guideHint': '',
        'options': options,
    }

    # 答案政策先于检索判定：代写作业/索要答案直接拒，省得白跑一轮工具
    pol = verifier.policy(raw_q)
    prep['policy'] = pol['mode']
    if pol['mode'] == 'refuse':
        prep['kind'] = 'guard'
        prep['localAnswer'] = verifier.SAFE_REFUSE
        return prep
    if pol['mode'] == 'guide':
        prep['guideHint'] = pol['hint']

    if intent['type'] in ('privacy', 'injection'):
        prep['kind'] = 'guard'
        prep['localAnswer'] = guard.render_local_reply(intent)
        return prep

    if intent['type'] in ('greeting', 'chitchat', 'encourage'):
        prep['kind'] = 'local'
        prep['localAnswer'] = guard.render_local_reply(intent)
        prep['llmMessages'] = [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'system', 'content': guard.build_system_directive(intent)},
            {'role': 'user', 'content': raw_q},
        ]
        return prep

    code_info = tool_parse_code(q)
    need_diagnose = intent['type'] in ('diagnose', 'report')

    # ---- 按计划依次调用工具（前端时间线展示的就是这一串） ----
    docs = []
    weak_points = []
    tool_ctx = {
        'user_id': uid,
        'question': q,
        'code': raw_q if code_info else '',
        'language': '',
        'docs': [],
    }
    specs = planner.plan_tools(plan, q, {'primary': prep['primary']})
    # 先把参数补齐，再一次性交给 run_tools：它内部按依赖分层并发，
    # 返回的调用记录顺序与 specs 一致（前端时间线依赖这个顺序）。
    fixed = []
    for name, args in specs:
        args = dict(args or {})
        if name == 'kb_search':
            args['query'] = q
        if name == 'render_formula':
            args['latex'] = str(options.get('latex') or '')
        fixed.append((name, args))
    for call in tools_mod.run_tools(fixed, tool_ctx):
        name = call.get('name')
        prep['toolCalls'].append(call)
        if not call.get('ok'):
            continue
        data = call.get('data') or {}
        if name == 'kb_search':
            docs = data.get('docs') or []
        elif name == 'wrong_record':
            weak_points = data.get('items') or []
        elif name == 'code_run':
            prep['codeRun'] = data
        elif name == 'quiz_generate':
            prep['quiz'] = data.get('questions') or []
        elif name == 'draw_diagram':
            prep['diagram'] = data
        elif name == 'study_plan':
            prep['studyPlan'] = data
        elif name == 'render_formula':
            prep['formula'] = data

    # 计划里没排检索但确实需要依据时兜底一次（如 wrong_review / 追问类）
    ran_search = any(c.get('name') == 'kb_search' for c in prep['toolCalls'])
    if not ran_search and intent['type'] in ('knowledge', 'code', 'diagnose', 'formula', 'wrong_review', 'encourage'):
        call = tools_mod.run_tool('kb_search', {'query': q, 'topK': 5}, tool_ctx)
        prep['toolCalls'].append(call)
        docs = (call.get('data') or {}).get('docs') or []

    if need_diagnose and not weak_points:
        weak_points = tool_diagnose(uid)

    # ---- 语义记忆召回：把「以前栽过的类似坑」翻出来，一并喂给大模型 ----
    # 聚合统计只说得出错得多不多，这里说得出来错的是哪个类似的点。
    # 只对真需要讲知识的意图做（闲聊/打招呼召回没意义，还多一次计算）。
    if intent['type'] not in ('greeting', 'chitchat', 'privacy', 'injection'):
        try:
            prep['related'] = memory_vec.recall(uid, raw_q, 4)
        except Exception:
            prep['related'] = []

    # 检索有了真实结果，重建思考过程，避免"展示的推理"与"实际依据"脱节
    reasoning = build_reasoning({
        'question': raw_q,
        'intent': intent,
        'docs': docs,
        'hasCode': bool(code_info and code_info.get('algo')),
        'history': history,
    })
    prep['docs'] = docs
    prep['weakPoints'] = weak_points
    prep['reasoning'] = reasoning
    prep['codeInfo'] = code_info
    prep['plan'] = planner.mark_status(plan, prep['toolCalls'])

    if intent['type'] == 'report':
        rep = report_mod.generate(uid)
        prep['kind'] = 'report'
        prep['report'] = rep
        prep['localAnswer'] = report_mod.render_markdown(rep)
        return prep

    code_knowledge = None
    if code_info and code_info.get('algo'):
        code_knowledge = query_one(
            'SELECT k.id, k.name, k.route, c.name AS course_name '
            'FROM knowledge k JOIN course c ON c.id = k.course_id WHERE k.name LIKE ? LIMIT 1',
            [f"%{code_info['algo']}%"],
        )
    prep['codeKnowledge'] = code_knowledge

    if not prep['primary']:
        prep['primary'] = code_knowledge or (docs[0] if docs else None)

    # 学习计划由错题数据直接生成，不再让模型自由发挥 —— 计划里出现
    # "每天学 3 小时"这种空话还不如不给，直接返回工具算出来的版本。
    if intent['type'] == 'plan' and (prep.get('studyPlan') or {}).get('markdown'):
        prep['kind'] = 'plan'
        prep['localAnswer'] = prep['studyPlan']['markdown']
        return prep

    context = '\n\n'.join([
        f"### {d.get('course_name') or ''} / {d.get('name')}\n{d.get('summary') or ''}\n{str(d.get('content') or '')[:1500]}"
        for d in docs
    ])

    parts = [
        f'【知识库检索结果】\n{context}' if context else '（知识库未命中相关知识点）',
        ('\n【该用户薄弱知识点】(来自错题统计)\n'
         + '\n'.join([f"- {w['course_name']}/{w['name']}：错 {w['wrong_count']} 次（路由 {w['route']}）" for w in weak_points]))
        if weak_points else '',
        f"\n【用户提交了代码】疑似算法：{code_info.get('algo') or '未识别'}，请解释代码逻辑与复杂度。" if code_info else '',
        f"\n【说明】这是多轮对话的追问，请结合上文语境回答。\"{raw_q}\"" if ctx['isFollowUp'] else '',
        # 语义记忆：以前错过的 / 问过的相似内容。这是"记住这个学生"的关键输入
        ('\n【该用户以前栽过的类似坑】(按语义相似度召回，不是按次数排名)\n'
         + '\n'.join([f"- [{r['title'] or r['kind']}] {r['excerpt']}" for r in (prep.get('related') or [])]))
        if prep.get('related') else '',
    ]

    # 工具已经产出了确定性内容，明确告诉模型"别再编一遍"
    if prep.get('diagram') and (prep['diagram'].get('steps') or []):
        parts.append('\n【已生成流程图】步骤为：' + ' → '.join(prep['diagram']['steps'])
                     + '。图会单独展示，你只需围绕这些步骤讲解，不要重复画图代码。')
    if prep.get('quiz'):
        parts.append('\n【已挑好练习题】题目会附在回答末尾，正文里只讲思路，**不要给出答案**。')
    if prep.get('codeRun'):
        cr = prep['codeRun']
        tail = ('运行结果：\n' + str(cr.get('output') or '')[:600]) if cr.get('executed') and cr.get('output') else ''
        parts.append('\n【代码工具】语言：%s，行数：%s，复杂度提示：%s。%s'
                     % (cr.get('language'), cr.get('lines'), '；'.join(cr.get('complexityHints') or []) or '无', tail))

    parts.append(f'\n【用户提问】{raw_q}')
    prep['userPrompt'] = '\n'.join([p for p in parts if p])
    prep['prepMs'] = int((time.time() - t0) * 1000)
    return prep


STYLE_DIRECTIVE = {
    'concise': '【篇幅】用户选择了「简洁」模式：控制在 150 字以内，只给结论和关键点，不要展开。',
    'detailed': '【篇幅】用户选择了「详细」模式：可以展开讲，给完整推导与多个例子，但不要注水重复。',
}


def _llm_messages(prep):
    """把 prepare 的结果拼成完整 messages（历史 + 客户端补传的上下文 + 本轮提问）"""
    messages = [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'system', 'content': guard.build_system_directive(prep['intent'])},
    ]
    if prep.get('guideHint'):
        messages.append({'role': 'system', 'content': prep['guideHint']})
    style = str((prep.get('options') or {}).get('style') or '').lower()
    if style in STYLE_DIRECTIVE:
        messages.append({'role': 'system', 'content': STYLE_DIRECTIVE[style]})
    for h in prep['history']:
        if not h.get('answer'):
            continue
        messages.append({'role': 'user', 'content': h['question']})
        messages.append({'role': 'assistant', 'content': h['answer']})
    for h in (prep['clientHistory'] or [])[-4:]:
        if h.get('content'):
            messages.append({'role': h.get('role') or 'user', 'content': h.get('content')})
    messages.append({'role': 'user', 'content': prep['userPrompt']})
    return messages


def _fallback_of(prep, raw_q):
    """大模型不可用时的本地降级回答（含代码解析与薄弱点补充）"""
    answer = fallback_answer(raw_q, prep['docs'], prep['intent'], {
        'isFollowUp': bool(prep['isFollowUp']),
        'prevName': prep['primary']['name'] if prep['primary'] else '',
    })
    code_info = prep.get('codeInfo')
    if code_info:
        answer += f"\n\n【代码解析】识别到疑似算法：{code_info.get('algo') or '未识别'}。"
        if prep.get('codeKnowledge'):
            answer += f"已为你定位到「{prep['codeKnowledge']['name']}」可视化动画。"
    if prep['weakPoints']:
        answer += '\n\n【薄弱点诊断】你在以下知识点错误较多：' + '、'.join(
            [f"{w['name']}({w['wrong_count']}次)" for w in prep['weakPoints']]
        ) + '。建议先看动画再回头刷题。'
    if prep['intent']['type'] == 'encourage':
        answer = guard.ENCOURAGE_TEMPLATE + '\n\n---\n\n' + answer
    return answer


def _call_brief(c):
    """工具调用记录：只回传前端时间线需要的字段，data 可能很大不随响应下发"""
    return {'name': c.get('name'), 'label': c.get('label'), 'ok': bool(c.get('ok')),
            'ms': int(c.get('ms') or 0), 'summary': c.get('summary') or ''}


@router.post('/chat')
def chat(request: Request, user: dict = Depends(current_user)):
    body = body_of(request)
    question = body.get('question')
    client_history = as_history(body.get('history'))
    session_id = body.get('sessionId')
    options = {
        'style': body.get('style'),
        'useMemory': body.get('useMemory'),
        'latex': body.get('latex'),
    }

    if not question or not str(question).strip():
        return fail(400, '请输入你的问题')

    uid = user['id']
    raw_q = str(question).strip()
    if len(raw_q) > 4000:
        return fail(400, '问题太长了，请精简后再提问（上限 4000 字）')

    t0 = time.time()
    prep = _prepare_chat(uid, raw_q, client_history, session_id, options)
    sid = prep['sid']
    intent = prep['intent']
    primary = prep['primary']
    weak_points = prep['weakPoints']
    reasoning = prep['reasoning']

    def reply(answer, mode, checked=None, extra=None):
        """统一收口：答案落库 + 轨迹落盘 + 字段拼装，避免每个分支各写一份"""
        elapsed = int((time.time() - t0) * 1000)
        payload = {
            'answer': answer,
            'mode': mode,
            'intent': intent['type'],
            'refused': mode == 'guard',
            'isFollowUp': prep['isFollowUp'],
            'reasoning': reasoning,
            'plan': prep['plan'],
            'toolCalls': [_call_brief(c) for c in prep['toolCalls']],
            'sources': (checked or {}).get('sources') or verifier.sources_of(prep['docs']),
            'knowledge': {'id': primary['id'], 'name': primary['name'], 'route': primary['route']} if primary else None,
            'related': [{'id': d['id'], 'name': d['name'], 'route': d['route']} for d in prep['docs']],
            'weakPoints': weak_points,
            # 语义记忆召回：以前错过的 / 问过的相似内容（前端可展示"我记得你栽过这里"）
            'relatedMemory': prep.get('related') or [],
            'actions': build_actions(primary, weak_points),
            'sessionId': sid,
            'elapsedMs': elapsed,
        }
        if (checked or {}).get('issues'):
            payload['issues'] = checked['issues']
        if extra:
            payload.update(extra)
        save_record(uid, sid, raw_q, answer, primary['id'] if primary else None, mode, intent['type'])
        touch_title(sid, raw_q)
        trace.log_turn(uid, sid, raw_q, intent['type'], mode, elapsed, prep['toolCalls'],
                       len(answer), len(prep['plan']), bool((checked or {}).get('blocked')),
                       (checked or {}).get('issues'))
        return ok(payload)

    if prep['kind'] == 'guard':
        return reply(prep['localAnswer'], 'guard',
                     extra={'knowledge': None, 'related': [], 'weakPoints': [], 'actions': []})

    if prep['kind'] == 'local':
        answer = prep['localAnswer']
        mode = 'local'
        if os.getenv('LLM_API_KEY'):
            try:
                got = call_llm(prep['llmMessages'])
                if got:
                    answer = got
                    mode = 'llm'
            except Exception:
                answer = prep['localAnswer']
                mode = 'local'
        return reply(answer, mode, extra={'knowledge': None, 'related': [], 'weakPoints': [], 'actions': []})

    if prep['kind'] == 'report':
        rep = prep['report']
        md = prep['localAnswer']
        extra = {
            'reasoning': reasoning + [{
                'phase': 'aggregate',
                'title': '汇总你的学习数据',
                'detail': '统计答题记录、正确率、错题分布与连续学习天数，再按薄弱程度排序给出建议。',
            }],
            'report': rep,
            'knowledge': None,
            'related': [],
            'weakPoints': rep['weakPoints'],
            'actions': build_actions(rep['weakPoints'][0] if rep['weakPoints'] else None, rep['weakPoints']),
        }
        return reply(md, 'report', extra=extra)

    if prep['kind'] == 'plan':
        # 学习计划由错题数据直接生成，不经过大模型 —— 免得被润色成正确的废话
        return reply(prep['localAnswer'], 'plan',
                     extra={'studyPlan': prep.get('studyPlan'),
                            'actions': build_actions(weak_points[0] if weak_points else None, weak_points)})

    mode = 'llm'
    try:
        answer = call_llm(_llm_messages(prep))
        if not answer:
            raise RuntimeError('EMPTY_ANSWER')
    except Exception:
        mode = 'fallback'
        answer = _fallback_of(prep, raw_q)

    answer, checked = _finalize(prep, answer)
    return reply(answer, mode, checked)


# ==================== 流式对话（逐字输出） ====================
def _sse(payload):
    """把一条消息编码成 SSE 帧"""
    return 'data: ' + json.dumps(payload, ensure_ascii=False) + '\n\n'


@router.post('/chat/stream')
def chat_stream(request: Request, user: dict = Depends(current_user)):
    """逐字流式返回：像豆包一样一个字一个字往外冒。

    事件格式（统一走 SSE 的 data 字段，前端按 type 分发）：
      {"type":"meta", ...}            会话号 / 意图 / 思考链 / 相关知识（先渲染骨架）
      {"type":"delta","content":"..."}  正文增量（字段名与 Node 侧、前端 sse.js 一致）
      {"type":"done","mode":"...","actions":[...]}  收尾（此时记录已落库）
      {"type":"error","message":"..."}
    """
    body = body_of(request)
    question = body.get('question')
    client_history = as_history(body.get('history'))
    session_id = body.get('sessionId')
    options = {
        'style': body.get('style'),
        'useMemory': body.get('useMemory'),
        'latex': body.get('latex'),
    }

    if not question or not str(question).strip():
        return fail(400, '请输入你的问题')
    uid = user['id']
    raw_q = str(question).strip()
    if len(raw_q) > 4000:
        return fail(400, '问题太长了，请精简后再提问（上限 4000 字）')

    t0 = time.time()

    def gen():
        try:
            prep = _prepare_chat(uid, raw_q, client_history, session_id, options)
        except Exception as e:
            yield _sse({'type': 'error', 'message': '服务异常：' + str(e)[:200]})
            return

        sid = prep['sid']
        intent = prep['intent']
        primary = prep['primary']
        weak_points = prep['weakPoints']

        def meta(mode, extra=None):
            base = {
                'type': 'meta',
                'mode': mode,
                'intent': intent['type'],
                'refused': prep['kind'] == 'guard',
                'reasoning': prep['reasoning'],
                'plan': prep['plan'],
                # 工具调用先于正文到达：前端可以先画出时间线，再等正文逐字冒出来
                'toolCalls': [_call_brief(c) for c in prep['toolCalls']],
                'sources': verifier.sources_of(prep['docs']),
                'sessionId': sid,
                'knowledge': {'id': primary['id'], 'name': primary['name'], 'route': primary['route']} if primary else None,
                'related': [{'id': d['id'], 'name': d['name'], 'route': d['route']} for d in prep['docs']],
                'weakPoints': weak_points,
                # 语义记忆召回：以前错过的 / 问过的相似内容
                'relatedMemory': prep.get('related') or [],
            }
            if extra:
                base.update(extra)
            return _sse(base)

        def finish(mode, text, checked=None, actions=None):
            elapsed = int((time.time() - t0) * 1000)
            save_record(uid, sid, raw_q, text, primary['id'] if primary else None, mode, intent['type'])
            touch_title(sid, raw_q)
            trace.log_turn(uid, sid, raw_q, intent['type'], mode, elapsed, prep['toolCalls'],
                           len(text), len(prep['plan']), bool((checked or {}).get('blocked')),
                           (checked or {}).get('issues'))
            ev = {'type': 'done', 'mode': mode, 'elapsedMs': elapsed}
            if actions:
                ev['actions'] = actions
            if (checked or {}).get('issues'):
                ev['issues'] = checked['issues']
            yield _sse(ev)

        # ---- 护栏 / 学习报告：内容本就瞬时可得，整段下发（前端仍逐字展开） ----
        if prep['kind'] in ('guard', 'report', 'plan'):
            mode = prep['kind'] if prep['kind'] != 'guard' else 'guard'
            if prep['kind'] == 'report':
                rep = prep['report']
                yield meta(mode, {
                    'report': rep,
                    'weakPoints': rep['weakPoints'],
                    'actions': build_actions(
                        rep['weakPoints'][0] if rep['weakPoints'] else None, rep['weakPoints']),
                })
            elif prep['kind'] == 'plan':
                yield meta(mode, {
                    'studyPlan': prep.get('studyPlan'),
                    'actions': build_actions(weak_points[0] if weak_points else None, weak_points),
                })
            else:
                yield meta(mode)
            text = prep['localAnswer'] or ''
            yield _sse({'type': 'delta', 'content': text})
            for ev in finish(mode, text):
                yield ev
            return

        # ---- 闲聊：先尝试真流式，失败才退回本地固定回复 ----
        if prep['kind'] == 'local':
            text = prep['localAnswer'] or ''
            mode = 'local'
            streamed = False
            if os.getenv('LLM_API_KEY'):
                acc = ''
                try:
                    for piece in stream_llm(prep['llmMessages']):
                        if not streamed:
                            streamed = True
                            yield meta('llm')
                        acc += piece
                        yield _sse({'type': 'delta', 'content': piece})
                    if not streamed:
                        raise RuntimeError('EMPTY_STREAM')
                    text = acc
                    mode = 'llm'
                except Exception:
                    streamed = False
                    text = prep['localAnswer'] or ''
                    mode = 'local'
            if not streamed:
                yield meta(mode)
                yield _sse({'type': 'delta', 'content': text})
            for ev in finish(mode, text):
                yield ev
            return

        # ---- 正常问答：真实流式，首个片段到达即推送 ----
        mode = 'llm'
        acc = ''
        started = False
        if os.getenv('LLM_API_KEY'):
            try:
                for piece in stream_llm(_llm_messages(prep)):
                    if not started:
                        started = True
                        yield meta('llm')
                    acc += piece
                    yield _sse({'type': 'delta', 'content': piece})
                if not started:
                    raise RuntimeError('EMPTY_STREAM')
            except Exception:
                mode = 'fallback'

        # 没配 LLM_API_KEY 时上面整段会被跳过，mode 仍是初始的 'llm'、acc 仍是 ''，
        # 若不在这里兜住就会静默返回「空回答」（frontend AgentChat 走的就是这个流式接口）。
        if not started:
            mode = 'fallback'

        if mode == 'fallback':
            acc = _fallback_of(prep, raw_q)
            if not started:
                yield meta('fallback')
            yield _sse({'type': 'delta', 'content': acc})

        # ---- 输出校验：安全兜底 / 幻觉标注 / 来源脚注 / 工具产物附录 ----
        checked = verifier.check(acc, {
            'docs': prep['docs'],
            'allowGeneral': intent['type'] in ('greeting', 'chitchat', 'encourage'),
        })
        if checked['blocked']:
            # 内容已经吐出去了，收不回来 —— 用 replace 让前端整体覆盖成安全话术
            yield _sse({'type': 'replace', 'content': checked['answer'], 'issues': checked['issues']})
            acc = checked['answer']
        else:
            tail = checked['answer'][len(acc):] + _appendix(prep) + verifier.footnote(checked['sources'])
            if tail:
                yield _sse({'type': 'delta', 'content': tail})
                acc = checked['answer'] + _appendix(prep) + verifier.footnote(checked['sources'])

        for ev in finish(mode, acc, checked, build_actions(primary, weak_points)):
            yield ev

    return StreamingResponse(gen(), media_type='text/event-stream', headers={
        'Cache-Control': 'no-cache, no-transform',
        'X-Accel-Buffering': 'no',
    })


# ==================== 会话管理 ====================
# 早期版本的对话记录没有 session_id（只挂在 user_id 上），这些历史不该丢。
# 用一个虚拟会话 id 把它们聚起来，前端点开即可回看。
LEGACY_SID = 'legacy'


@router.get('/sessions')
def sessions(user: dict = Depends(current_user)):
    rows = query(
        'SELECT s.id, s.title, s.created_at, s.updated_at, '
        '(SELECT COUNT(*) FROM chat_record r WHERE r.session_id = s.id) AS msg_count '
        'FROM chat_session s WHERE s.user_id = ? ORDER BY s.updated_at DESC LIMIT 50',
        [user['id']],
    )
    lst = [dict(r) for r in rows.rows]

    legacy = query_one(
        'SELECT COUNT(*) AS c, MIN(created_at) AS first_at, MAX(created_at) AS last_at '
        'FROM chat_record WHERE user_id = ? AND session_id IS NULL',
        [user['id']],
    )
    if legacy and int(legacy['c'] or 0) > 0:
        lst.append({
            'id': LEGACY_SID,
            'title': '历史提问（早期记录）',
            'created_at': legacy['first_at'],
            'updated_at': legacy['last_at'],
            'msg_count': int(legacy['c'] or 0),
        })

    def sort_key(x):
        return str(x.get('updated_at') or x.get('created_at') or '')

    lst.sort(key=sort_key, reverse=True)
    return ok(lst)


@router.get('/sessions/{sid}/messages')
def session_messages(sid: str, user: dict = Depends(current_user)):
    if str(sid) == LEGACY_SID:
        rows = query(
            'SELECT id, question, answer, knowledge_id, mode, intent, created_at FROM chat_record '
            'WHERE session_id IS NULL AND user_id = ? ORDER BY id ASC',
            [user['id']],
        )
    else:
        rows = query(
            'SELECT id, question, answer, knowledge_id, mode, intent, created_at FROM chat_record '
            'WHERE session_id = ? AND user_id = ? ORDER BY id ASC',
            [sid, user['id']],
        )
    return ok([dict(r) for r in rows.rows])


@router.delete('/sessions/{sid}')
def delete_session(sid: str, user: dict = Depends(current_user)):
    if str(sid) == LEGACY_SID:
        query('DELETE FROM chat_record WHERE session_id IS NULL AND user_id = ?', [user['id']])
        return ok(message='已删除')
    query('DELETE FROM chat_record WHERE session_id = ? AND user_id = ?', [sid, user['id']])
    query('DELETE FROM chat_session WHERE id = ? AND user_id = ?', [sid, user['id']])
    return ok(message='已删除')


@router.delete('/chats')
def clear_chats(user: dict = Depends(current_user)):
    query('DELETE FROM chat_record WHERE user_id = ?', [user['id']])
    query('DELETE FROM chat_session WHERE user_id = ?', [user['id']])
    return ok(message='已清空')


# ==================== 学习报告 ====================
@router.get('/report')
def report(user: dict = Depends(current_user)):
    rep = report_mod.generate(user['id'])
    rep = dict(rep)
    rep['markdown'] = report_mod.render_markdown(rep)
    return ok(rep)


# ==================== 检索能力信息 ====================
# 这一组会直接渲染到首页「智能助手能做什么」卡片里，是学生看到的第一印象。
# 写法要求：**说人话，不用技术黑话**。
# 反例：「TF-IDF 向量空间 + 可选云端 Embedding」「别名表 + 关键词打分」——
#       学生不知道 TF-IDF 是什么，更不知道这跟问问题有什么关系。
# 目标：每条都回答「这对我意味着什么」，术语只在真的必须点出时才出现。
@router.get('/tools')
def tools():
    return ok([
        {'name': '听得懂你的问法', 'desc': '你写「快排怎么写」「排好一点的排序」，它都知道你问的是什么，不用背关键词'},
        {'name': '专有名词也不怕', 'desc': '「B+ 树」「CSMA/CD」这类缩写和全称都对得上，不会答非所问'},
        {'name': '直接跳去看动画', 'desc': '它认出你在问哪个知识点，顺手把对应的动画页面打开给你看'},
        {'name': '知道哪儿该补', 'desc': '看你做错的题，直接指出哪个知识点最薄弱'},
        {'name': '代码能拆开讲', 'desc': '把一段算法代码配上对应的动画，一步步讲它在做什么'},
        {'name': '可以一直追问', 'desc': '你接着问「那它的复杂度呢」，它记得上一句你在说什么'},
        {'name': '按你的情况出报告', 'desc': '拿你真实的学习记录，生成一份只针对你的进度与建议'},
        {'name': '不越界、不乱答', 'desc': '不会要你的密码隐私，也不会顺着你做破坏性的事'},
    ])


@router.get('/vector-stats')
def vector_stats(user: dict = Depends(current_user)):
    return ok(vector.stats())


# ==================== 工具箱（注册表 + 手动调用） ====================
@router.get('/capabilities')
def capabilities():
    """Agent 工具清单：前端「工具箱」面板用它渲染，避免能力说明写死在前端。"""
    return ok({
        'tools': tools_mod.capabilities(),
        'intents': [
            {'type': 'knowledge', 'label': '知识讲解'},
            {'type': 'code', 'label': '代码解析'},
            {'type': 'quiz', 'label': '出题练习'},
            {'type': 'draw', 'label': '流程图'},
            {'type': 'plan', 'label': '学习计划'},
            {'type': 'wrong_review', 'label': '错题整理'},
            {'type': 'formula', 'label': '公式渲染'},
            {'type': 'diagnose', 'label': '薄弱点诊断'},
            {'type': 'report', 'label': '学习报告'},
        ],
    })


@router.post('/tool')
def invoke_tool(request: Request, user: dict = Depends(current_user)):
    """手动调用一个工具（工具箱面板 / 前端按钮触发）。

    与对话链路共用 tools.run_tool，因此行为、计时、异常兜底完全一致 ——
    不另开一套"面板专用"实现，免得两边结果对不上。
    """
    body = body_of(request)
    name = str(body.get('name') or '').strip()
    args = body.get('args') if isinstance(body.get('args'), dict) else {}
    if not name:
        return fail(400, '请指定工具名')
    res = tools_mod.run_tool(name, args, {'user_id': user['id'], 'question': str(args.get('query') or '')})
    trace.log_tool(user['id'], name, res.get('ok'), res.get('ms'), res.get('summary'))
    if not res.get('ok') and res.get('error') == 'UNKNOWN_TOOL':
        return fail(400, '未注册的工具：' + name)
    return ok({'call': _call_brief(res), 'data': res.get('data')})


# ==================== 记忆模块 ====================
@router.get('/memory')
def memory_view(q: str = None, user: dict = Depends(current_user)):
    """查看 Agent 记住了什么：短期对话 + 长期薄弱点 + 用户画像。

    带 q 时会额外做一次语义召回（related），列出"和你现在问的像"的旧笔记 ——
    这是聚合统计给不出来的那一半记忆。
    """
    return ok(memory_mod.profile(user['id'], q))


@router.delete('/memory')
def memory_clear(scope: str = 'chat', user: dict = Depends(current_user)):
    """清空记忆。scope=chat（默认，只清对话）/ all（连错题本一起清）"""
    if str(scope) not in ('chat', 'all'):
        return fail(400, 'scope 只能是 chat 或 all')
    return ok(memory_mod.clear(user['id'], scope), message='已清空')


# ==================== 可观测 / 效果评估 ====================
@router.get('/stats')
def agent_stats(days: int = 7, user: dict = Depends(current_user)):
    """Agent 运行统计：提问数、平均耗时、工具成功率、意图分布。

    管理员看全站，学生只看自己 —— 轨迹里带 userId，不能把别人的提问量发出去。
    """
    d = max(1, min(int(days or 7), 30))
    if user.get('role') == 'admin':
        return ok(trace.stats(d))
    rows = [r for r in trace.recent(2000, d) if r.get('userId') == user['id']]
    return ok(trace.stats(d, rows))


@router.get('/traces')
def agent_traces(limit: int = 50, days: int = 3, user: dict = Depends(current_user)):
    """最近调用轨迹（效果评估用）。管理员看全部，学生只看自己的。"""
    rows = trace.recent(max(1, min(int(limit or 50), 200)), max(1, min(int(days or 3), 30)))
    if user.get('role') != 'admin':
        rows = [r for r in rows if r.get('userId') == user['id']]
    return ok(rows)
