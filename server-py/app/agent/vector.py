"""
轻量向量检索（语义检索）

设计目标：不依赖任何外部服务与向量数据库即可跑出「语义相似度」效果。
三种模式：
  1) local-tfidf（默认）：中文 2~3gram + 英文词切分，TF-IDF 加权，余弦相似度。
  2) remote-embedding：配置 EMBEDDING_API_KEY 后调用 OpenAI 兼容 /embeddings，
     失败自动回退本地模式。
另外融合「知识点名称 / 别名」的精确命中信号，弥补纯统计方法对专有名词的短板。
"""

import datetime
import math
import os
import re
import time

import re

import httpx

from app.db import query

STOPWORDS = set([
    '的', '了', '是', '在', '和', '与', '及', '有', '我', '你', '他', '它', '这', '那',
    '吗', '呢', '吧', '啊', '请问', '帮我', '什么', '怎么', '如何', '为什么', '讲讲',
    '介绍', '说说', '解释', '一下', '个', '请', '想', '要', '会', '能', '可以',
])

# 领域同义词表：把「口语说法 / 易混淆词」锚定到具体知识点名称。
# 纯 TF-IDF 对多义词无能为力（例如"内存不够了怎么换页"会被 malloc 挤掉），
# 这里用显式同义词加权做多义词消歧。只收录有区分度的词。
SYNONYMS = [
    {'name': '页面置换', 'words': ['换页', '缺页', '页面淘汰', '淘汰页面', '内存不够', '内存不足', '内存满了', '驻留集', 'page replacement']},
    {'name': '动态内存 malloc/free', 'words': ['malloc', 'calloc', 'realloc', '动态内存', '堆内存分配', '动态分配', '内存泄漏', '悬空指针']},
    {'name': '指针与地址运算', 'words': ['野指针', '取地址', '解引用', '指针算术', '地址运算']},
    {'name': '函数调用与栈帧', 'words': ['栈帧', '调用栈', '函数调用栈', '递归调用', 'stack frame']},
    {'name': '结构体与内存对齐', 'words': ['内存对齐', '字节对齐', '填充字节', 'padding', 'offsetof']},
    {'name': '虚函数与运行时多态', 'words': ['虚函数', '虚表', 'vtable', '动态绑定', '运行时多态', '虚析构']},
    {'name': '引用、移动语义与 RAII', 'words': ['shared_ptr', 'unique_ptr', 'weak_ptr', '引用计数', '循环引用', '移动语义', '智能指针']},
    {'name': '类、对象与 JVM 内存', 'words': ['jvm', '垃圾回收', 'gc roots', 'gcroot', '常量池', '元空间']},
    {'name': '集合框架 Collection', 'words': ['hashmap', 'arraylist', 'hashset', 'treemap', '集合框架', '迭代器删除']},
    {'name': '多线程与并发', 'words': ['多线程', '线程安全', 'synchronized', 'volatile', '线程状态', '线程同步']},
    {'name': '泛型与反射', 'words': ['类型擦除', '泛型擦除', 'pecs', '反射机制', 'setaccessible']},
    {'name': '列表、切片与推导式', 'words': ['切片', '列表推导', '深拷贝', '浅拷贝', 'list comprehension']},
    {'name': '函数、参数与装饰器', 'words': ['装饰器', '闭包', 'functools.wraps', 'nonlocal']},
    {'name': '面向对象与魔术方法', 'words': ['魔术方法', '魔法方法', '__str__', '__repr__', 'mro', '类属性']},
    {'name': '迭代器与生成器', 'words': ['生成器', 'yield', '迭代器协议', '惰性求值', '生成器表达式']},
]


def tokenize(text):
    """中文 2~3gram + 英文/数字词切分"""
    t = str(text or '').lower()
    terms = re.findall(r'[a-z][a-z0-9+#.]{1,}', t)
    cn = re.findall(r'[\u4e00-\u9fa5]+', t)
    for seg in cn:
        if seg in STOPWORDS and len(seg) <= 2:
            continue
        for i in range(len(seg)):
            if i + 2 <= len(seg):
                w = seg[i:i + 2]
                if w not in STOPWORDS:
                    terms.append(w)
            if i + 3 <= len(seg):
                w = seg[i:i + 3]
                if w not in STOPWORDS:
                    terms.append(w)
    return terms


def term_freq(terms):
    tf = {}
    for t in terms:
        tf[t] = tf.get(t, 0) + 1
    return tf


def build_tf_idf_index(docs):
    """基于语料构建 TF-IDF 向量空间。docs: [{id, text}]"""
    df = {}
    doc_tfs = []
    for d in docs:
        tf = term_freq(tokenize(d['text']))
        doc_tfs.append({'id': d['id'], 'tf': tf})
        for term in tf:
            df[term] = df.get(term, 0) + 1
    n = len(docs) or 1
    idf = {term: math.log((n + 1) / (c + 1)) + 1 for term, c in df.items()}
    doc_vectors = {}
    for item in doc_tfs:
        vec = {}
        norm = 0.0
        for term, c in item['tf'].items():
            w = (1 + math.log(c)) * idf.get(term, 1)
            vec[term] = w
            norm += w * w
        doc_vectors[item['id']] = {'vec': vec, 'norm': math.sqrt(norm) or 1}
    return {'idf': idf, 'docVectors': doc_vectors}


def vectorize(text, idf):
    tf = term_freq(tokenize(text))
    vec = {}
    norm = 0.0
    default_idf = math.log(100)
    for term, c in tf.items():
        w = (1 + math.log(c)) * idf.get(term, default_idf)
        vec[term] = w
        norm += w * w
    return {'vec': vec, 'norm': math.sqrt(norm) or 1}


def cosine(a, b):
    shorter, other = (a['vec'], b['vec']) if len(a['vec']) <= len(b['vec']) else (b['vec'], a['vec'])
    dot = 0.0
    for term, w in shorter.items():
        if term in other:
            dot += w * other[term]
    return dot / ((a['norm'] * b['norm']) or 1)


def dense_cosine(a, b):
    n = min(len(a), len(b))
    dot = na = nb = 0.0
    for i in range(n):
        dot += a[i] * b[i]
        na += a[i] * a[i]
        nb += b[i] * b[i]
    return dot / ((math.sqrt(na) * math.sqrt(nb)) or 1)


def _embed_url():
    # 默认不再指向 DeepSeek：DeepSeek 官方不提供 /embeddings 接口，
    # 之前只要有人填了 Key 却没填 URL，就会打到 /embeddings 拿 404，
    # 白白等一次 8 秒超时再退回本地 TF-IDF。默认改为与默认模型名匹配的 OpenAI 地址。
    return (os.getenv('EMBEDDING_BASE_URL') or 'https://api.openai.com/v1').rstrip('/')


def remote_embed(texts):
    key = os.getenv('EMBEDDING_API_KEY') or ''
    if not key:
        raise RuntimeError('EMBEDDING_NOT_CONFIGURED')
    resp = httpx.post(
        _embed_url() + '/embeddings',
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key},
        json={'model': os.getenv('EMBEDDING_MODEL') or 'text-embedding-3-small', 'input': texts},
        timeout=8.0,
    )
    if resp.status_code != 200:
        raise RuntimeError('EMBEDDING_HTTP_' + str(resp.status_code))
    data = resp.json()
    return [d['embedding'] for d in data['data']]


_cache = {'at': 0, 'docs': [], 'tfidf': None, 'dense': None, 'mode': 'local-tfidf'}
TTL = 5 * 60


def load_docs():
    r = query(
        'SELECT k.id, k.name, k.summary, k.content, k.route, c.name AS course_name, c.category '
        'FROM knowledge k JOIN course c ON c.id = k.course_id'
    )
    out = []
    for row in r.rows:
        content = row.get('content') or ''
        summary = row.get('summary') or ''
        out.append({
            'id': row['id'],
            'name': row['name'],
            'route': row.get('route'),
            'course_name': row.get('course_name'),
            'summary': summary,
            'content': content,
            # 名称重复加权，让专有名词在向量空间里更有分量
            'text': f"{row['name']} {row['name']} {row.get('course_name')} {summary} {content[:2000]}",
        })
    return out


def ensure_index(force: bool = False):
    global _cache
    now = time.time()
    if not force and _cache['docs'] and (now - _cache['at']) < TTL:
        return _cache
    docs = load_docs()
    tfidf = build_tf_idf_index([{'id': d['id'], 'text': d['text']} for d in docs])
    _cache = {'at': now, 'docs': docs, 'tfidf': tfidf, 'dense': None, 'mode': 'local-tfidf'}

    # 配置了 embedding 接口则升级为稠密向量（失败静默回退）
    if os.getenv('EMBEDDING_API_KEY'):
        try:
            vecs = remote_embed([d['text'][:1500] for d in docs])
            dense = {d['id']: vecs[i] for i, d in enumerate(docs)}
            _cache['dense'] = dense
            _cache['mode'] = 'remote-embedding'
        except Exception as e:
            _cache['mode'] = 'local-tfidf(fallback:' + str(e) + ')'
    return _cache


def search(question, top_k: int = 5):
    idx = ensure_index()
    q = str(question or '').strip()
    if not q:
        return []

    scored = []
    if idx.get('dense'):
        try:
            qv = remote_embed([q])[0]
            scored = [dict(d, score=dense_cosine(qv, idx['dense'].get(d['id']) or []),
                           matchedBy='embedding') for d in idx['docs']]
        except Exception:
            idx['dense'] = None
            idx['mode'] = 'local-tfidf'

    if not scored:
        qv = vectorize(q, idx['tfidf']['idf'])
        scored = []
        for d in idx['docs']:
            dv = idx['tfidf']['docVectors'].get(d['id']) or {'vec': {}, 'norm': 1}
            scored.append(dict(d, score=cosine(qv, dv), matchedBy='tfidf'))

    # 融合精确信号：名称 / 同义词 / 首句命中
    ql = q.lower()
    hit_syn = [item for item in SYNONYMS if any(str(w).lower() in ql for w in item['words'])]
    for s in scored:
        name = str(s.get('name') or '').lower()
        if name and name in ql:
            s['score'] += 0.6
        boost = next((i for i in hit_syn
                      if name.__contains__(i['name'].lower()) or i['name'].lower().__contains__(name)), None)
        if boost:
            s['score'] += 0.9
            s['matchedBy'] = 'synonym'
        if s.get('summary') and str(s['summary']).lower()[:8] in ql:
            s['score'] += 0.05

    scored = [s for s in scored if s['score'] > 0.02]
    scored.sort(key=lambda x: x['score'], reverse=True)
    return scored[:top_k]


def stats():
    idx = ensure_index()
    return {
        'mode': idx['mode'],
        'docCount': len(idx['docs']),
        'updatedAt': datetime.datetime.utcfromtimestamp(idx['at']).isoformat() + 'Z',
    }
