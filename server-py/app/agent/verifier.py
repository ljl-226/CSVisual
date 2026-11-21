"""输出校验器（Verifier）：回答发出去之前的最后一道闸。

三件事：
  1. 安全兜底 —— 模型万一被绕过去，输出里出现了密码/密钥/破坏性语句，在这里拦下；
  2. 幻觉抑制 —— 知识库没命中时明确标注，不许把通用讲解伪装成"教材原话"；
  3. 来源标注 —— 回答依据哪几个知识点，随答案一起返回，学生能点回去核对。
"""

import re

# 输出里不该出现的东西（模型被绕过后兜底）。
# 与 guard.py 的入参规则对应：guard 管"用户说什么"，verifier 管"助手答什么"。
LEAK_RULES = [
    (re.compile(r'(密码|口令)\s*[:：是]\s*\S{3,}', re.I), '疑似泄露密码'),
    (re.compile(r'(api[_\- ]?key|secret|token|jwt)\s*[:：]\s*[A-Za-z0-9_\-\.]{8,}', re.I), '疑似泄露系统凭据'),
    (re.compile(r'\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.'), '疑似泄露 JWT'),
    (re.compile(r'(drop\s+table|truncate\s+table|delete\s+from\s+\w+\s*;|rm\s+-rf)\b', re.I), '疑似输出破坏性指令'),
    (re.compile(r'(身份证号|银行卡号)\s*[:：]?\s*\d{15,}', re.I), '疑似泄露身份信息'),
]

# 代写 / 直接要答案：前者坚决拒，后者改成引导式讲解
HOMEWORK_RULES = re.compile(
    r'(帮我写|代写|替我写|直接给我写)[^。？]{0,12}(作业|论文|实验报告|课程设计|大作业|毕业论文)'
    r'|(作业|试卷|考试)[^。？]{0,8}(答案|标准答案)发?(我|给我|一下)'
)
ANSWER_DEMAND_RULES = re.compile(r'(答案是什么|正确答案是|选哪一个|选哪个|直接告诉我答案|给我答案|这题选啥)')

SAFE_REFUSE = ('抱歉，这类请求我不能帮忙 —— 直接给作业/试卷答案属于学术不端，'
               '而且抄完了知识点还是没进脑子。\n\n'
               '我可以换个方式帮你：告诉我这道题考的是哪个知识点，'
               '我给你讲清楚原理，再配几道同类题让你自己练，卡在哪一步我们随时拆开看。')

GUIDE_HINT = (
    '【答案政策】这道问题用户想要现成答案。请不要直接给出最终答案或选项。\n'
    '改成引导式讲解：① 先说明这道题考的是哪个知识点；② 给出解题的第一个提示（不是结论）；'
    '③ 让用户先说出自己的思路，你再往下提示一步。必要时给一个同类的小例子作类比。'
)

HALLUCINATION_NOTE = ('\n\n> 提示：这次没有命中课程知识库，下面是通用讲解，'
                      '具体表述请以你的教材和课件为准。')


def policy(question: str, quiz_hit: bool = False) -> dict:
    """回答前的政策判定：normal / guide / refuse"""
    q = str(question or '')
    if HOMEWORK_RULES.search(q):
        return {'mode': 'refuse', 'hint': '', 'reason': '作业/试卷代写与索要答案'}
    if ANSWER_DEMAND_RULES.search(q) or quiz_hit:
        return {'mode': 'guide', 'hint': GUIDE_HINT, 'reason': '直接索要答案，改为引导式讲解'}
    return {'mode': 'normal', 'hint': '', 'reason': ''}


def sources_of(docs, limit: int = 5):
    """把命中的知识点整理成可点击的来源（前端渲染成 chips）"""
    out = []
    for d in (docs or [])[:limit]:
        if not d:
            continue
        out.append({
            'knowledgeId': d.get('id'),
            'name': d.get('name'),
            'course': d.get('course_name') or '',
            'route': d.get('route') or '',
            'score': round(float(d.get('score') or 0), 3),
        })
    return out


def footnote(sources) -> str:
    """来源脚注：写进答案正文，历史会话回看时也还在（可追溯）"""
    if not sources:
        return ''
    items = []
    for s in sources[:3]:
        label = ('%s / %s' % (s['course'], s['name'])) if s.get('course') else (s.get('name') or '')
        if label:
            items.append(label)
    if not items:
        return ''
    return '\n\n---\n*参考知识点：%s*' % '；'.join(items)


def check(answer: str, ctx: dict = None):
    """校验一条回答。返回 {'answer','issues','sources','blocked'}"""
    ctx = ctx or {}
    text = str(answer or '')
    issues = []

    for rx, why in LEAK_RULES:
        if rx.search(text):
            issues.append(why)
    if issues:
        # 命中即整段替换：留着"半句安全半句泄露"比直接给拒绝话术更危险。
        return {
            'answer': '抱歉，这条回答包含不安全内容，已被系统拦截。换个问法试试？',
            'issues': issues,
            'sources': [],
            'blocked': True,
        }

    docs = ctx.get('docs') or []
    sources = sources_of(docs)

    if not docs and not ctx.get('allowGeneral'):
        # 知识库没命中却给了确定结论，是最典型的幻觉场景 —— 明确标注而不是假装权威
        text += HALLUCINATION_NOTE
        issues.append('知识库未命中，已追加"通用讲解"标注')

    if len(text.strip()) < 12:
        issues.append('回答过短，可能是空响应')

    return {'answer': text, 'issues': issues, 'sources': sources, 'blocked': False}
