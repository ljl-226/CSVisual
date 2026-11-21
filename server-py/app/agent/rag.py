"""
轻量 RAG 检索：以 MySQL knowledge 表为知识库，
使用「别名表 + 关键词命中 + 文本覆盖度」打分，无需向量库即可运行。
"""

import re

from app.db import query

# 知识点别名 / 同义词表，提升中文自然语言命中率
ALIAS = {
    '链表': ['单链表', '线性表', 'linked list', '结点', '节点插入', '头插法', '尾插法'],
    '栈': ['stack', '入栈', '出栈', '压栈', '弹栈', '后缀表达式', '括号匹配'],
    '队列': ['queue', '入队', '出队', '循环队列', '双端队列', 'deque', '生产者消费者'],
    '二叉树': ['binary tree', '前序', '中序', '后序', '层序', '遍历', '结点'],
    'B+树': ['b+tree', 'b树', 'btree', '索引', '数据库索引', '叶子节点', '分裂'],
    '快速排序': ['quicksort', '快排', '分区', 'pivot', '基准', '划分'],
    '归并排序': ['mergesort', '归并', '二路归并', '分治', '合并有序表'],
    'BFS': ['广度优先', 'bfs', '层次遍历', '队列实现'],
    'DFS': ['深度优先', 'dfs', '回溯', '递归遍历'],
    'TCP三次握手': ['三次握手', 'syn', 'ack', '建立连接', 'handshake', '半连接'],
    'TCP四次挥手': ['四次挥手', '断开连接', 'fin', 'time_wait', '关闭连接'],
    'IP路由': ['路由', '路由表', '下一跳', '最长前缀匹配', '分组转发', 'rip', 'ospf'],
    'ARP协议': ['arp', '地址解析', 'mac地址', 'ip到mac', 'arp缓存'],
    '拥塞控制': ['拥塞', '滑动窗口', '慢开始', '拥塞避免', '快重传', '快恢复', 'cwnd', 'ssthresh'],
    '进程状态': ['进程状态', '就绪', '阻塞', '运行', '状态转换', '五态模型', '挂起'],
    '进程调度': ['调度', 'fcfs', 'sjf', '时间片轮转', 'rr', '先来先服务', '短作业优先', '周转时间'],
    '页面置换': ['页面置换', 'lru', 'fifo', '缺页', '缺页中断', '内存分配', '最佳置换', 'opt'],
    '死锁': ['死锁', 'deadlock', '银行家算法', '资源分配图', '环路等待', '预防死锁'],
    '指令流水线': ['流水线', 'pipeline', '取指', '译码', '执行', '写回', '冒险', '数据相关'],
    '存储器层次': ['存储层次', 'cache', '缓存', '主存', '辅存', '命中率', '局部性'],
    'ALU运算': ['alu', '运算器', '补码', '加法器', '算术逻辑单元', '溢出'],
    '寄存器数据传输': ['寄存器', '数据通路', '总线', '传送', '微操作', 'load', 'store'],
}


def tokenize(text):
    """中英文关键词抽取（简单切分，够用且零依赖）"""
    t = str(text or '').lower()
    words = re.findall(r'[a-z0-9+#]+', t)
    for seg in re.findall(r'[\u4e00-\u9fa5]+', t):
        for i in range(len(seg)):
            words.append(seg[i:i + 2])
            if i + 3 <= len(seg):
                words.append(seg[i:i + 3])
    return list(dict.fromkeys(words))


# 疑问词 / 口语虚词：它们几乎出现在每道题里，也几乎出现在每篇长正文里。
# 不剔除的话，「导数是什么意思」里的「什么/意思」会给所有知识点各加一分，
# 长正文（几千字）凑齐六七个虚词就能反超真正命中「导数」的那一条 ——
# 这正是「问导数却命中编译原理」的原因。
STOPWORDS = {
    '什么', '意思', '怎么', '怎样', '如何', '为什', '为啥', '哪些', '哪个', '是否',
    '可以', '能否', '请问', '一下', '详细', '解释', '说明', '举例', '举个例子',
    '是什', '么意', '么样', '数的', '地里', '帮我', '讲讲', '介绍', '有没', '是不',
    '的是', '了什', '啥意', '求教', '请教', '问问', '不懂', '不太', '明白',
}


def _lcs_len(a, b):
    """最长公共子串长度：用来衡量问题与知识点名称的字面重合度"""
    if not a or not b:
        return 0
    prev = [0] * (len(b) + 1)
    best = 0
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best = cur[j]
        prev = cur
    return best


def load_knowledge():
    r = query(
        'SELECT k.id, k.name, k.summary, k.content, k.route, c.name AS course_name '
        'FROM knowledge k JOIN course c ON c.id = k.course_id'
    )
    return list(r.rows)


def search(question, top_k: int = 3):
    docs = load_knowledge()
    qs = str(question or '').lower()
    # 先去掉疑问虚词，再参与打分
    tokens = [t for t in tokenize(question) if len(t) >= 2 and t not in STOPWORDS]

    # 逆文档频率：同一个词在越多知识点的「名称 + 摘要」里出现，它对区分度贡献越小。
    # 「导数」只属于一两条知识点，而「意义」「几何」散落在很多条里 ——
    # 不做这一步，通用词会把真正相关的知识点压下去。
    df = {}
    for d in docs:
        head = (str(d.get('name') or '') + ' ' + str(d.get('summary') or '')).lower()
        for tk in tokens:
            if tk in head:
                df[tk] = df.get(tk, 0) + 1
    idf = {tk: 1.0 / (df.get(tk, 1) ** 0.5) for tk in tokens}

    scored = []
    for doc in docs:
        score = 0.0
        name = str(doc.get('name') or '').lower()
        summary = str(doc.get('summary') or '').lower()
        content = str(doc.get('content') or '').lower()

        # 1. 名称直接命中（权重最高）
        if name and len(name) > 1 and name in qs:
            score += 50

        # 2. 别名命中
        for a in ALIAS.get(doc.get('name'), []):
            if str(a).lower() in qs:
                score += 20

        # 3. 名称与问题的字面重合度（"导数是什么意思" 也能认出"导数"）
        common = _lcs_len(name, qs)
        if common >= 2:
            score += common * 10

        # 4. 关键词覆盖度（按 IDF 加权，正文命中设上限，避免长文靠字数取胜）
        hit_summary = 0.0
        hit_content = 0.0
        for tk in tokens:
            w = idf[tk]
            if tk in name:
                score += 25 * w
            if tk in summary:
                hit_summary += 6 * w
            if tk in content:
                hit_content += 1.5 * w
        score += min(hit_summary, 18) + min(hit_content, 8)

        scored.append(dict(doc, score=score))

    scored = [d for d in scored if d['score'] > 0]
    scored.sort(key=lambda x: x['score'], reverse=True)
    return scored[:top_k]


CODE_SIGNALS = [';', '{', '}', '#include', 'def ', 'function', 'void ', 'int ', 'for (', 'for(', 'while (', 'return ']


def detect_code(text):
    s = str(text or '')
    hit = [sig for sig in CODE_SIGNALS if sig in s]
    if len(hit) < 2:
        return None
    return {'isCode': True, 'signals': hit}


CODE_ALGO_MAP = [
    {'keys': ['quicksort', 'partition', 'pivot', '快速排序', '快排'], 'name': '快速排序'},
    {'keys': ['mergesort', 'merge', '归并'], 'name': '归并排序'},
    {'keys': ['bfs', 'queue', '广度优先', '层次遍历'], 'name': 'BFS'},
    {'keys': ['dfs', 'visited', '深度优先', '递归遍历'], 'name': 'DFS'},
    {'keys': ['stack', 'push', 'pop', '栈'], 'name': '栈'},
    {'keys': ['queue', 'enqueue', 'dequeue', '队列'], 'name': '队列'},
    {'keys': ['linkedlist', 'node', 'next', '链表'], 'name': '链表'},
    {'keys': ['lru', '页面置换', '缺页'], 'name': '页面置换'},
]


def detect_algo_from_code(code):
    t = str(code or '').lower()
    for item in CODE_ALGO_MAP:
        if any(k.lower() in t for k in item['keys']):
            return item['name']
    return None
