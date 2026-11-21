"""Agent 长期记忆的语义层：把「错过的题 / 问过的问题」变成能按意思召回的笔记。

为什么要有这一层：
  memory.long_term() 现在是 SQL 聚合统计（按知识点 GROUP BY 数 wrong_count），
  它只能回答「哪个知识点错得最多」，回答不了：
    · 你现在问的这道题，和你以前错过的哪道题**是一个毛病**；
    · 你上次到底**卡在哪一步**（错因，不是次数）；
    · 三个月前问过类似的问题，当时没听懂。
  这些都是「按意思相近找回来」的问题，不是「按次数排序」的问题。

怎么做的：
  1) 写入：判错时把「题干 + 你的答案 + 正确答案要点」存成一条笔记；
     有知识点的问答也存一条（这样"你问过什么"同样能被想起）。
  2) 检索：把笔记和当前问题都变成向量，按余弦相似度召回最相关的几条。
     向量来源两条路，配了 EMBEDDING_API_KEY 就走远程 embedding（语义更准，结果落库缓存），
     否则在「这个用户的笔记集合」里现算 TF-IDF —— 零配置、零外部依赖，量也小（几百条）。

笔记为什么只存原文不落向量（本地模式）：
  本地 TF-IDF 的 idf 是相对当前笔记集合算的，笔记一增删就得重算，
  存下来的向量第二天就失真了；而这个量级（几百条）实时算只要几毫秒。
  只有远程模式才值得缓存 —— 那是要花钱、要等网络的。
"""

import json
import os

from app.agent import rag, vector
from app.db import query, query_one

# 每个用户的笔记上限：错题笔记比问答笔记留得多，问答太容易膨胀
LIMIT = {'wrong': 300, 'chat': 100}


def _model_name():
    return os.getenv('EMBEDDING_MODEL') or 'text-embedding-3-small'


def _has_remote():
    return bool(os.getenv('EMBEDDING_API_KEY'))


# ==================== 写入 ====================
def add(user_id, kind: str, content: str, ref_id=None, knowledge_id=None, title: str = ''):
    """记一条笔记。同一来源（kind + ref_id）重复记只累加权重，不堆重复条目。

    任何异常都不许冒泡：记忆是增强，写不进去最多是这次没记住，不能让提交答题失败。
    """
    try:
        content = (content or '').strip()
        if not content or not user_id:
            return None
        kind = kind if kind in LIMIT else 'chat'
        row = None
        if ref_id:
            row = query_one(
                'SELECT id, weight FROM memory_note WHERE user_id = ? AND kind = ? AND ref_id = ?',
                [user_id, kind, ref_id],
            )
        if row:
            query(
                'UPDATE memory_note SET weight = weight + 1, content = ?, title = ?, '
                'knowledge_id = ?, updated_at = NOW() WHERE id = ?',
                [content[:4000], (title or '')[:200], knowledge_id, row['id']],
            )
            note_id = row['id']
        else:
            r = query(
                'INSERT INTO memory_note (user_id, kind, ref_id, knowledge_id, title, content) '
                'VALUES (?, ?, ?, ?, ?, ?)',
                [user_id, kind, ref_id, knowledge_id, (title or '')[:200], content[:4000]],
            )
            # db.query 返回 Result：写操作用 insert_id（与 Node 版对齐的字段名）
            note_id = getattr(r, 'insert_id', None)
        _trim(user_id, kind)
        return note_id
    except Exception:
        return None


def _trim(user_id, kind: str):
    """超出上限就删最旧的，避免笔记无限膨胀拖慢检索"""
    limit = LIMIT.get(kind, 100)
    r = query_one('SELECT COUNT(*) AS c FROM memory_note WHERE user_id = ? AND kind = ?', [user_id, kind])
    over = int((r or {}).get('c') or 0) - limit
    if over <= 0:
        return
    query(
        'DELETE FROM memory_note WHERE user_id = ? AND kind = ? ORDER BY updated_at ASC LIMIT ?',
        [user_id, kind, over],
    )


def remove_ref(user_id, kind: str, ref_id):
    """某来源不再需要记忆（比如错题攻克了）"""
    try:
        query('DELETE FROM memory_note WHERE user_id = ? AND kind = ? AND ref_id = ?', [user_id, kind, ref_id])
    except Exception:
        pass


# ==================== 向量 ====================
def _concepts(question):
    """把问题归到若干知识点上（返回 知识点名集合 / 知识点 id 集合）。

    为什么需要这一步：纯字面相似解决不了口语问法 ——
    "进程之间互相等待资源，系统卡住不动了怎么办" 和 "银行家算法" 一个字都不重叠，
    但它们在同一个人脑子里就是同一个毛病。
    所以先用项目已有的检索（含同义词表）把这句话归到「死锁」这类知识点上，
    再让属于该知识点的旧笔记拿到加权 —— 召回靠"是不是同一个点"，不只是"像不像"。
    """
    names, ids = set(), set()
    for fn in (vector.search, rag.search):
        try:
            for d in (fn(question, 3) or []):
                if d.get('name'):
                    names.add(str(d['name']))
                if d.get('id'):
                    ids.add(int(d['id']))
        except Exception:
            continue
    return names, ids


def _concept_bonus(note, names, ids):
    """笔记与当前问题是否落在同一个知识点上"""
    bonus = 0.0
    try:
        if note.get('knowledge_id') and int(note['knowledge_id']) in ids:
            bonus += 0.55
    except Exception:
        pass
    title = str(note.get('title') or '')
    if title and title in names:
        bonus += 0.45
    if any(name and name in (note.get('content') or '') for name in names):
        bonus += 0.2
    return bonus


def _local_scores(notes, question):
    """本地 TF-IDF：在这个用户的笔记集合内现算，不需要任何外部服务。

    标题拼进正文一起向量化（名称重复加权），让"死锁"这类专有名词更有分量。
    """
    try:
        idx = vector.build_tf_idf_index(
            [{'id': n['id'], 'text': '%s %s %s' % (
                n.get('title') or '', n.get('title') or '', n.get('content') or '')} for n in notes]
        )
    except Exception:
        return {}
    qv = vector.vectorize(str(question or ''), idx['idf'])
    out = {}
    for n in notes:
        dv = idx['docVectors'].get(n['id']) or {'vec': {}, 'norm': 1}
        out[n['id']] = vector.cosine(qv, dv)
    return out


def _remote_scores(notes, question):
    """远程 embedding：笔记向量落库缓存，只对新笔记 / 换模型时真正调用接口"""
    model = _model_name()
    ids = [n['id'] for n in notes]
    cached = {}
    if ids:
        ph = ','.join(['?'] * len(ids))
        rows = query(
            'SELECT note_id, vec FROM memory_vector WHERE note_id IN (%s) AND model = ?' % ph,
            ids + [model],
        ).rows
        for r in rows:
            try:
                cached[r['note_id']] = json.loads(r['vec'])
            except Exception:
                pass

    missing = [n for n in notes if n['id'] not in cached]
    if missing:
        try:
            vecs = vector.remote_embed([n['content'][:1500] for n in missing])
            for n, v in zip(missing, vecs):
                cached[n['id']] = v
                query(
                    'INSERT INTO memory_vector (note_id, model, dim, vec) VALUES (?, ?, ?, ?) '
                    'ON DUPLICATE KEY UPDATE model = VALUES(model), dim = VALUES(dim), vec = VALUES(vec)',
                    [n['id'], model, len(v), json.dumps(v)],
                )
        except Exception:
            # 远程不可用：本次退回本地，缓存里已有的仍然可用
            if not cached:
                return None

    try:
        qv = vector.remote_embed([str(question or '')[:1500]])[0]
    except Exception:
        return None
    return {n['id']: vector.dense_cosine(qv, cached.get(n['id']) or []) for n in notes}


# ==================== 检索 ====================
def recall(user_id, question: str, top_k: int = 5, kind: str = None):
    """按语义相似度召回与当前问题相关的历史笔记。

    排序 = 语义相似度 × 权重加成：同一处反复错的（weight 大）在同等相似度下排前面，
    但相似度仍是主导 —— 不能让"错得多的"霸占"问得相关的"。
    """
    try:
        sql = ('SELECT id, kind, ref_id, knowledge_id, title, content, weight, created_at '
               'FROM memory_note WHERE user_id = ?')
        args = [user_id]
        if kind:
            sql += ' AND kind = ?'
            args.append(kind)
        sql += ' ORDER BY updated_at DESC LIMIT 400'
        notes = query(sql, args).rows
    except Exception:
        return []
    notes = [dict(n) for n in notes]
    if not notes or not str(question or '').strip():
        return []

    scores = None
    mode = 'local-tfidf'
    if _has_remote():
        scores = _remote_scores(notes, question)
        if scores:
            mode = 'remote-embedding'
    if not scores:
        scores = _local_scores(notes, question)
        mode = 'local-tfidf'
    if not scores:
        return []

    # 概念锚定：把「同一个知识点」的旧笔记拉上来（字面不重叠也认）
    names, ids = _concepts(question)

    out = []
    for n in notes:
        s = float(scores.get(n['id']) or 0) + _concept_bonus(n, names, ids)
        if s <= 0.05:
            continue
        w = int(n.get('weight') or 1)
        out.append({
            'id': n['id'],
            'kind': n['kind'],
            'refId': n.get('ref_id'),
            'knowledgeId': n.get('knowledge_id'),
            'title': n.get('title') or '',
            'excerpt': (n.get('content') or '')[:160],
            'weight': w,
            'score': round(s * (1 + min(w - 1, 5) * 0.08), 4),
            'createdAt': str(n.get('created_at') or ''),
        })
    out.sort(key=lambda x: x['score'], reverse=True)
    return out[:top_k]


def stats(user_id):
    """给「记忆与设置」面板用：记了多少条、现在用的哪种向量"""
    try:
        rows = query(
            'SELECT kind, COUNT(*) AS c FROM memory_note WHERE user_id = ? GROUP BY kind', [user_id]
        ).rows
        counts = {r['kind']: int(r['c'] or 0) for r in rows}
    except Exception:
        counts = {}
    return {
        'mode': 'remote-embedding' if _has_remote() else 'local-tfidf',
        'noteCount': sum(counts.values()),
        'byKind': counts,
    }


def remove_kind(user_id, kind: str):
    """只清某一类笔记（清空对话记忆时用）"""
    try:
        query('DELETE FROM memory_vector WHERE note_id IN '
              '(SELECT id FROM memory_note WHERE user_id = ? AND kind = ?)', [user_id, kind])
        query('DELETE FROM memory_note WHERE user_id = ? AND kind = ?', [user_id, kind])
    except Exception:
        pass


def clear(user_id):
    try:
        query('DELETE FROM memory_vector WHERE note_id IN '
              '(SELECT id FROM memory_note WHERE user_id = ?)', [user_id])
        query('DELETE FROM memory_note WHERE user_id = ?', [user_id])
    except Exception:
        pass
