# -*- coding: utf-8 -*-
"""算法题数据构造辅助：用结构化字段拼出洛谷风格题面，避免每题重复写 Markdown 骨架"""


def build_desc(body, inp, outp, sample_in, sample_out, hint=None, scope=None):
    s = '## 【题目描述】\n\n' + body
    s += '\n\n## 【输入格式】\n\n' + inp
    s += '\n\n## 【输出格式】\n\n' + outp
    s += '\n\n## 【样例】\n\n输入：\n\n```\n' + sample_in + '\n```\n\n输出：\n\n```\n' + sample_out + '\n```'
    if scope:
        s += '\n\n## 【数据范围】\n\n' + scope
    if hint:
        s += '\n\n## 【提示】\n\n' + hint
    return s


def P(title, diff, body, inp, outp, sin, sout, ref, gen,
      hint=None, scope=None, tags='', source='洛谷', kid=None):
    """构造一道题的数据字典

    gen: 函数，接收 random.Random 实例，返回一个测试输入字符串（可含换行）
    """
    return {
        'title': title,
        'difficulty': diff,
        'tags': tags,
        'source': source,
        'kid': kid,
        'desc': build_desc(body, inp, outp, sin, sout, hint, scope),
        'in': inp,
        'out': outp,
        'sample_in': sin,
        'sample_out': sout,
        'hint': hint or '',
        'ref': ref,
        'gen': gen,
    }
