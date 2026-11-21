"""
思考链引擎：让 Agent「先想清楚，再作答」，并把思考过程一并输出给用户。

设计原则：
  1. 步骤要真实反映本系统实际做的事（检索到哪条知识点、命中了哪些要点），
     而不是编造一段"看起来在思考"的套话——假思考比不思考更有害。
  2. 每步都短（一句话），可快速扫读；细节放在 detail 里按需展开。
  3. 纯函数，无副作用，便于测试。
"""

import re

# 中文虚词/套话：滑窗切出来的这些碎片没有区分度，参与匹配只会稀释命中率
STOP_WORDS = set([
    '的', '了', '是', '在', '和', '与', '对', '将', '把', '被', '并', '或', '等', '中', '为',
    '其', '这', '那', '有', '无', '不', '要', '能', '会', '可', '及', '则', '若', '如', '从',
    '到', '以', '所', '而', '且', '之', '于', '上', '下', '内', '外', '时', '用', '个', '说明',
    '指出', '分析', '解释', '正确', '错误', '什么', '怎么', '如何', '因为', '所以', '但是',
    '可以', '需要', '应该', '通过', '进行', '一个', '这个', '那个', '就是', '不是'
])


def keywords_of(text, limit: int = 6):
    """从文本里抽出便于展示的关键词（英文术语 + 中文 2~4 字滑窗词）"""
    t = str(text or '')
    en = [w.lower() for w in re.findall(r'[A-Za-z_][A-Za-z0-9_]{1,}', t) if len(w) >= 2]
    cn_words = []
    cn = re.sub(r'[^\u4e00-\u9fa5]', ' ', t)
    for seg in cn.split():
        for length in range(2, 5):
            for i in range(0, max(0, len(seg) - length + 1)):
                w = seg[i:i + length]
                if w not in STOP_WORDS:
                    cn_words.append(w)
    all_words = list(dict.fromkeys(en + cn_words))
    scored = [
        {'w': w, 'n': max(1, t.lower().count(w)), 'len': len(w)}
        for w in all_words
    ]
    scored.sort(key=lambda x: (x['len'] * x['n']), reverse=True)
    return [x['w'] for x in scored[:limit]]


def brief(s, n: int = 42) -> str:
    """截断长文本用于展示"""
    t = re.sub(r'\s+', ' ', str(s or '')).strip()
    return t[:n] + '…' if len(t) > n else t


TYPE_TEXT = {
    'injection': '这个请求涉及越权或破坏性操作，属于安全红线，应当拒绝',
    'privacy': '这个问题索要他人或系统的敏感信息，属于隐私红线，应当拒绝',
    'greeting': '这是打招呼，不需要检索知识库，直接引导即可',
    'chitchat': '这是闲聊，聊完顺手把话题引回学习',
    'encourage': '你表达的是挫败感，先接住情绪，再给可执行的下一步',
    'report': '你要的是学习报告，需要汇总你的答题数据',
    'diagnose': '你要的是诊断，需要从错题与答题记录里找薄弱点',
    'code': '里面有代码，需要按程序结构逐段解析',
    'knowledge': '这是一个知识点问题，需要到知识库里找依据',
}


def build_reasoning(params: dict = None):
    """生成一次问答的思考步骤。"""
    p = params or {}
    question = p.get('question', '') or ''
    intent = p.get('intent', {}) or {}
    docs = p.get('docs', []) or []
    has_code = bool(p.get('hasCode'))
    history = p.get('history', []) or []
    steps = []
    kind = intent.get('type') or 'knowledge'

    steps.append({
        'phase': 'understand',
        'title': '理解你的问题',
        'detail': f'你问的是「{brief(question, 36)}」，我先确认它的真正指向，而不是只看表面用词。'
    })

    steps.append({
        'phase': 'classify',
        'title': '判断问题类型',
        'detail': TYPE_TEXT.get(kind, '按知识点问题处理')
    })

    # 安全类到此为止：后面不需要检索与作答
    if kind in ('injection', 'privacy'):
        steps.append({
            'phase': 'refuse',
            'title': '给出拒绝',
            'detail': (f'拒绝理由：{intent.get("why")}。同时说明我能帮你做什么，避免对话中断。'
                       if intent.get('why') else '按安全策略拒绝该请求。')
        })
        return steps

    if history:
        steps.append({
            'phase': 'context',
            'title': '结合上文',
            'detail': f'这是同一会话的第 {len(history) + 1} 轮，我要避免重复已讲过的内容，只讲你追问的那一层。'
        })

    if kind in ('knowledge', 'code') or has_code:
        if docs:
            names = '、'.join([str(d.get('name', '')) for d in docs[:3]])
            steps.append({
                'phase': 'retrieve',
                'title': '检索知识库',
                'detail': f'命中 {len(docs)} 条资料，最相关的是「{brief(names, 40)}」，以它的正文作为回答依据。'
            })
            top = docs[0]
            if top and top.get('summary'):
                steps.append({
                    'phase': 'ground',
                    'title': '定位关键结论',
                    'detail': f'从该知识点摘出与你问题直接相关的部分：{brief(top.get("summary"), 60)}'
                })
        else:
            steps.append({
                'phase': 'retrieve',
                'title': '检索知识库',
                'detail': '知识库里没有高度匹配的条目，我会基于通用计算机知识回答，并明确告诉你这一点，避免让你误以为有教材依据。'
            })

    steps.append({
        'phase': 'compose',
        'title': '组织回答',
        'detail': '按「一句话结论 → 展开讲解 → 怎么学/怎么练」的顺序输出，让你先拿到答案，再看细节。'
    })
    return steps


def build_grading_reasoning(params: dict = None):
    """生成判分场景的思考步骤 —— 让用户看到"分数是怎么来的"。"""
    p = params or {}
    qtype = p.get('type') or 'case'
    points = p.get('points', []) or []
    answer_length = int(p.get('answerLength') or 0)
    hit_count = int(p.get('hitCount') or 0)
    refused = bool(p.get('refused'))
    label = '编程题' if qtype == 'programming' else '案例分析题'
    steps = []

    steps.append({
        'phase': 'read',
        'title': '读题与定位考点',
        'detail': f'这是一道{label}，我先明确它要考查的能力，再逐条比对评分要点。'
    })
    steps.append({
        'phase': 'scan',
        'title': '检查作答规范性',
        'detail': ('你的作答过短（不足 20 字），很可能没有展开分析，会按要点缺失处理。'
                   if answer_length < 20 else f'你的作答共 {answer_length} 字，长度正常，进入要点比对。')
    })
    if refused:
        steps.append({
            'phase': 'guard',
            'title': '安全校验',
            'detail': '我发现作答里混入了试图影响评分的指令（例如要求给满分、要求忽略评分标准）。判分必须客观，这类指令一律不采纳，并按实际作答内容评分。'
        })
        return steps

    steps.append({
        'phase': 'match',
        'title': '逐条比对评分要点',
        'detail': f'本题共 {len(points)} 个要点，我逐条检查你的作答是否覆盖。'
    })
    steps.append({
        'phase': 'score',
        'title': '汇总得分',
        'detail': f'命中 {hit_count} / {len(points)} 个要点，按各要点分值累加得出总分；未命中的要点会单独列出，作为你的改正方向。'
    })
    return steps


def build_algo_reasoning(params: dict = None):
    """算法小助手的思考步骤（讲解算法题）。"""
    p = params or {}
    title = p.get('title') or ''
    tags = p.get('tags') or ''
    difficulty = int(p.get('difficulty') or 3)
    mode = p.get('mode') or 'explain'
    steps = [{
        'phase': 'parse',
        'title': '明确你卡在哪',
        'detail': ('你贴了代码/报错，我先定位出错的那几行，再回溯到它背后的算法逻辑。'
                   if mode == 'debug' else f'这道题是「{brief(title, 30)}」，我先讲清它要做什么、输入输出是什么。')
    }, {
        'phase': 'model',
        'title': '抽象问题模型',
        'detail': (f'它属于【{tags}】类问题，这类题有固定的思考套路，我先点明套路再套到本题。'
                   if tags else '先把它归到熟悉的算法模型上，再套用对应套路。')
    }, {
        'phase': 'plan',
        'title': '设计解法',
        'detail': '从最直观的做法出发，逐步优化，并给出时间与空间复杂度。'
    }]
    if difficulty >= 4:
        steps.append({
            'phase': 'edge',
            'title': '提醒易错边界',
            'detail': '这道题难度较高，我会特别指出容易漏掉的边界情况。'
        })
    steps.append({
        'phase': 'code',
        'title': '给出可运行代码',
        'detail': '最后给一份带注释的参考实现，你可以直接粘到代码框里跑。'
    })
    return steps
