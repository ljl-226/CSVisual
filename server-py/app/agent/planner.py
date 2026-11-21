"""Agent 规划层（Planner）：把一次提问拆成若干子任务，并绑定要用的工具。

为什么要有 Planner：
  之前是「意图 → 一坨 if/else → 直接拼 prompt」，步骤隐含在代码里，
  用户只看到最终答案，既不知道助手打算怎么干，也没法解释"为什么答偏了"。
  拆成显式计划后：前端能展示任务拆解，工具按计划依次执行，
  出问题时能直接定位到是哪一步没做好。
"""

import re

# 条件触发：某些工具只在问题里出现对应诉求时才启用，
# 否则每个问题都跑 4 个工具 —— 时间线花哨但纯属浪费。
QUIZ_HINT = re.compile(r'(练习题|出几道|来几道|做几道|出题|考考我|练一练|给.*道题)')
DRAW_HINT = re.compile(r'(流程图|示意图|时序图|画个图|画一下|画张图|步骤图|关系图)')
PLAN_HINT = re.compile(r'(\d+\s*天|一周|两周|一个月)')
FORMULA_HINT = re.compile(r'(\$\$|\\frac|\\sum|\\int|\\lim|\\begin\{|(?<!\$)\$(?!\$)[\w\\^{}_{}+\-*/=()]+\$)')

STEP_TPL = {
    'understand': {'title': '理解你的问题', 'detail': '判断你在问哪个知识点，想要结论还是推导过程'},
    'search': {'title': '检索课程知识库', 'tool': 'kb_search', 'detail': '向量检索 + 关键词检索融合，找出最相关的知识点'},
    'answer': {'title': '组织讲解', 'detail': '先给结论，再讲原理，涉及算法给出复杂度'},
    'quiz': {'title': '配一套练习题', 'tool': 'quiz_generate', 'detail': '按命中的知识点挑几道题，只给题目不直接给答案'},
    'draw': {'title': '画一张流程图', 'tool': 'draw_diagram', 'detail': '把知识点步骤抽成 Mermaid 流程图'},
    'code': {'title': '解析/运行这段代码', 'tool': 'code_run', 'detail': '识别语言与算法，运行开关打开时直接跑一遍'},
    'formula': {'title': '渲染公式', 'tool': 'render_formula', 'detail': '校验 LaTeX 结构，拦掉 \\href 这类危险宏'},
    'wrong': {'title': '读取你的错题数据', 'tool': 'wrong_record', 'detail': '按错误次数排序，找出真正的薄弱点'},
    'plan': {'title': '生成分天学习计划', 'tool': 'study_plan', 'detail': '薄弱点优先，逐个给动画 + 练习 + 复述三步'},
    'encourage': {'title': '先接住情绪', 'detail': '先共情再拆步骤，不急着讲知识点'},
    'refuse': {'title': '安全护栏拦截', 'detail': '判定为隐私/越权请求，直接给出拒绝话术'},
    'chitchat': {'title': '闲聊应答', 'detail': '非业务问题，简短回应并把话题引回学习'},
    'report': {'title': '汇总你的学习数据', 'detail': '统计答题、正确率、错题分布与学习天数'},
}

INTENT_PLANS = {
    'knowledge': ['understand', 'search', 'answer'],
    'code': ['code', 'search', 'answer'],
    'diagnose': ['wrong', 'answer'],
    'report': ['report'],
    'greeting': ['chitchat'],
    'chitchat': ['chitchat'],
    'encourage': ['encourage', 'search', 'answer'],
    'privacy': ['refuse'],
    'injection': ['refuse'],
    # 新增意图
    'quiz': ['search', 'quiz'],
    'draw': ['search', 'draw'],
    'plan': ['wrong', 'plan'],
    'wrong_review': ['wrong', 'quiz'],
    'formula': ['search', 'formula', 'answer'],
}


def _days_of(question: str) -> int:
    m = re.search(r'(\d+)\s*天', question or '')
    if m:
        return max(1, min(int(m.group(1)), 30))
    if re.search(r'两周|半个月', question or ''):
        return 14
    if re.search(r'一个月|30天', question or ''):
        return 30
    return 7


def build_plan(intent: dict, question: str, ctx: dict = None):
    """生成任务拆解。返回 [{'id','title','detail','tool','status'}]"""
    ctx = ctx or {}
    t = (intent or {}).get('type') or 'knowledge'
    keys = list(INTENT_PLANS.get(t, INTENT_PLANS['knowledge']))
    q = str(question or '')

    # ---- 条件追加：诉求写在问题里才加对应步骤 ----
    if t == 'knowledge':
        if DRAW_HINT.search(q):
            keys.insert(2, 'draw')
        if FORMULA_HINT.search(q):
            keys.insert(2, 'formula')
        if QUIZ_HINT.search(q):
            keys.append('quiz')
    elif t == 'diagnose' and PLAN_HINT.search(q):
        keys.append('plan')
    elif t == 'code' and QUIZ_HINT.search(q):
        keys.append('quiz')

    steps = []
    for i, k in enumerate(keys):
        tpl = STEP_TPL.get(k)
        if not tpl:
            continue
        steps.append({
            'id': 's%d' % (i + 1),
            'title': tpl['title'],
            'detail': tpl['detail'],
            'tool': tpl.get('tool'),
            'status': 'pending',
        })
    return steps


def plan_tools(steps, question: str, ctx: dict = None):
    """把计划里的步骤翻译成 [(工具名, 参数)]，交给 tools.run_tools 执行。"""
    ctx = ctx or {}
    q = str(question or '')
    primary = ctx.get('primary') or {}
    specs = []
    for s in steps or []:
        tool = s.get('tool')
        if not tool:
            continue
        if tool == 'kb_search':
            specs.append(('kb_search', {'query': q, 'topK': 5}))
        elif tool == 'quiz_generate':
            specs.append(('quiz_generate', {'knowledgeId': primary.get('id'), 'count': 3}))
        elif tool == 'draw_diagram':
            specs.append(('draw_diagram', {'topic': q}))
        elif tool == 'code_run':
            specs.append(('code_run', {'code': ctx.get('code') or q, 'language': ctx.get('language') or ''}))
        elif tool == 'render_formula':
            specs.append(('render_formula', {'latex': ctx.get('latex') or ''}))
        elif tool == 'wrong_record':
            specs.append(('wrong_record', {'action': 'list', 'limit': 5}))
        elif tool == 'study_plan':
            specs.append(('study_plan', {'days': _days_of(q)}))
    # 去重：同一工具一次提问只跑一次
    seen = set()
    out = []
    for n, a in specs:
        if n in seen:
            continue
        seen.add(n)
        out.append((n, a))
    return out


def mark_status(steps, tool_calls):
    """按工具调用结果回填步骤状态（前端时间线用）"""
    by_name = {c.get('name'): c for c in (tool_calls or [])}
    for s in steps or []:
        c = by_name.get(s.get('tool'))
        if c:
            s['status'] = 'done' if c.get('ok') else 'failed'
            s['ms'] = c.get('ms')
            s['summary'] = c.get('summary') or ''
        elif not s.get('tool'):
            s['status'] = 'done'
    return steps
