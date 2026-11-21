# -*- coding: utf-8 -*-
"""第八批：图论与数据结构（16 道）"""
from common import P


def _gen_graph(r, n=None, extra=None, weighted=True, lo=1, hi=100):
    """生成保证连通的无向图：先连成一棵随机树，再随机加边"""
    n = n or r.randint(2, 9)
    edges = []
    for i in range(2, n + 1):
        p = r.randint(1, i - 1)
        edges.append((p, i))
    extra = extra if extra is not None else r.randint(0, n)
    seen = set(edges) | set((b, a) for a, b in edges)
    cnt = 0
    guard = 0
    max_edges = n * (n - 1) // 2
    while cnt < extra and len(edges) < max_edges and guard < 200:
        guard += 1
        a, b = r.randint(1, n), r.randint(1, n)
        if a == b or (a, b) in seen:
            continue
        seen.add((a, b))
        edges.append((a, b))
        cnt += 1
    if weighted:
        body = '\n'.join('%d %d %d' % (a, b, r.randint(lo, hi)) for a, b in edges)
    else:
        body = '\n'.join('%d %d' % (a, b) for a, b in edges)
    return '%d %d\n%s' % (n, len(edges), body)


def _gen_tree(r, n=None):
    n = n or r.randint(2, 9)
    edges = []
    for i in range(2, n + 1):
        edges.append((r.randint(1, i - 1), i))
    return '%d\n%s' % (n, '\n'.join('%d %d' % e for e in edges))


def _gen_dag(r):
    """生成保证无环的有向图：边只从小编号指向大编号"""
    n = r.randint(2, 9)
    edges = []
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            if r.random() < 0.25:
                edges.append((i, j))
    return '%d %d\n%s' % (n, len(edges), '\n'.join('%d %d' % e for e in edges))


def _gen_directed(r, acyclic=None):
    """生成有向图，acyclic 为 True 时保证无环，为 False 时故意加入回边"""
    s = _gen_dag(r)
    if acyclic is False:
        lines = s.split('\n')
        n = int(lines[0].split()[0])
        a, b = r.randint(2, n), r.randint(1, n - 1)
        lines[0] = '%d %d' % (n, int(lines[0].split()[1]) + 1)
        lines.append('%d %d' % (a, b))
        s = '\n'.join(lines)
    return s


def _gen_bipartite(r):
    n = r.randint(2, 10)
    color = [r.randint(0, 1) for _ in range(n + 1)]
    edges = []
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            if color[i] != color[j] and r.random() < 0.3:
                edges.append((i, j))
    bad = r.random() < 0.35
    if bad:
        same = [(i, j) for i in range(1, n + 1) for j in range(i + 1, n + 1) if color[i] == color[j]]
        if same:
            edges.append(r.choice(same))
    return '%d %d\n%s' % (n, len(edges), '\n'.join('%d %d' % e for e in edges))


def _gen_floyd(r):
    """带询问的图：n m q + m 条带权边 + q 次询问"""
    n = r.randint(2, 9)
    body = _gen_graph(r, n=n, weighted=True, extra=r.randint(0, 3))
    lines = body.split('\n')
    m = int(lines[0].split()[1])
    q = r.randint(1, 4)
    queries = ['%d %d' % (r.randint(1, n), r.randint(1, n)) for _ in range(q)]
    return '%d %d %d\n%s\n%s' % (n, m, q, '\n'.join(lines[1:1 + m]), '\n'.join(queries))


class _Node:
    __slots__ = ('v', 'l', 'r')

    def __init__(self, v):
        self.v = v
        self.l = None
        self.r = None


def _gen_tree_trav(r):
    n = r.randint(1, 9)
    vals = r.sample(range(1, 100), n)
    root = None
    for x in vals:
        if root is None:
            root = _Node(x)
            continue
        cur = root
        while True:
            if x < cur.v:
                if cur.l is None:
                    cur.l = _Node(x)
                    break
                cur = cur.l
            else:
                if cur.r is None:
                    cur.r = _Node(x)
                    break
                cur = cur.r
    pre, mid, post = [], [], []

    def walk(t):
        if not t:
            return
        pre.append(t.v)
        walk(t.l)
        mid.append(t.v)
        walk(t.r)
        post.append(t.v)

    walk(root)
    return '%s\n%s' % (' '.join(map(str, pre)), ' '.join(map(str, mid)))


PROBLEMS = [
    P('亲戚（并查集）', 2,
      '有 n 个人，给出 m 组亲戚关系（关系具有传递性）。接下来有 q 次询问，每次询问两个人是否为亲戚。',
      '第一行三个整数 n、m、q；接下来 m 行，每行两个整数 a、b，表示 a 与 b 是亲戚；接下来 q 行，每行两个整数 x、y，表示一次询问。',
      '每次询问输出一行，是亲戚输出 Yes，否则输出 No。',
      '5 3 2\n1 2\n2 3\n4 5\n1 3\n2 4', 'Yes\nNo',
      '''import sys

data = list(map(int, sys.stdin.read().split()))
n, m, q = data[0], data[1], data[2]
fa = list(range(n + 1))


def find(x):
    while fa[x] != x:
        fa[x] = fa[fa[x]]
        x = fa[x]
    return x


p = 3
for _ in range(m):
    a, b = data[p], data[p + 1]
    p += 2
    ra, rb = find(a), find(b)
    if ra != rb:
        fa[ra] = rb
out = []
for _ in range(q):
    x, y = data[p], data[p + 1]
    p += 2
    out.append('Yes' if find(x) == find(y) else 'No')
print('\\n'.join(out))
''',
      lambda r: (lambda n, m, q: '%d %d %d\n%s\n%s' % (
          n, m, q,
          '\n'.join('%d %d' % (r.randint(1, n), r.randint(1, n)) for _ in range(m)),
          '\n'.join('%d %d' % (r.randint(1, n), r.randint(1, n)) for _ in range(q))))(
          r.randint(2, 12), r.randint(1, 10), r.randint(1, 5)),
      hint='并查集模板：find 用路径压缩、union 时把一棵树的根挂到另一棵树根下；两个人在同一集合即为亲戚。',
      scope='1 ≤ n ≤ 10⁴，1 ≤ m, q ≤ 10⁴', tags='并查集,图论', kid=8),

    P('连通块计数（并查集）', 2,
      '给定一张 n 个点、m 条边的无向图，求其中连通块的个数。',
      '第一行两个整数 n、m；接下来 m 行，每行两个整数 u、v，表示一条无向边。',
      '一行，一个整数，表示连通块个数。',
      '5 2\n1 2\n3 4', '3',
      '''import sys

data = list(map(int, sys.stdin.read().split()))
n, m = data[0], data[1]
fa = list(range(n + 1))


def find(x):
    while fa[x] != x:
        fa[x] = fa[fa[x]]
        x = fa[x]
    return x


cnt = n
p = 2
for _ in range(m):
    u, v = data[p], data[p + 1]
    p += 2
    ru, rv = find(u), find(v)
    if ru != rv:
        fa[ru] = rv
        cnt -= 1
print(cnt)
''',
      lambda r: _gen_graph(r, weighted=False, extra=0),
      hint='初始连通块数为 n，每合并两个不同集合就减一；也可用 DFS/BFS  flood fill 计数。',
      scope='1 ≤ n ≤ 10⁴，0 ≤ m ≤ 10⁵', tags='并查集,图论,连通性', kid=8),

    P('最小生成树', 3,
      '给定一个 n 个点、m 条边的带权无向连通图，求其最小生成树的边权之和。',
      '第一行两个整数 n、m；接下来 m 行，每行三个整数 u、v、w，表示一条权值为 w 的无向边。',
      '一行，一个整数，表示最小生成树的权值和。',
      '4 5\n1 2 2\n1 3 3\n2 3 1\n2 4 4\n3 4 5', '7',
      '''import sys

data = list(map(int, sys.stdin.read().split()))
n, m = data[0], data[1]
edges = [(data[2 + 3 * i], data[3 + 3 * i], data[4 + 3 * i]) for i in range(m)]
edges.sort(key=lambda e: e[2])
fa = list(range(n + 1))


def find(x):
    while fa[x] != x:
        fa[x] = fa[fa[x]]
        x = fa[x]
    return x


ans = 0
cnt = 0
for u, v, w in edges:
    ru, rv = find(u), find(v)
    if ru != rv:
        fa[ru] = rv
        ans += w
        cnt += 1
        if cnt == n - 1:
            break
print(ans)
''',
      lambda r: _gen_graph(r, weighted=True),
      hint='Kruskal 算法：把边按权值升序排序，用并查集依次选取两端不在同一集合的边，选满 n-1 条即得到最小生成树。',
      scope='1 ≤ n ≤ 10⁴，1 ≤ m ≤ 10⁵', tags='图论,最小生成树,并查集', kid=8),

    P('单源最短路（Dijkstra）', 3,
      '给定一个 n 个点、m 条边的正权无向图，求 1 号点到 n 号点的最短距离；若不可达，输出 -1。',
      '第一行两个整数 n、m；接下来 m 行，每行三个整数 u、v、w，表示一条权值为 w 的无向边。',
      '一行，一个整数。',
      '4 4\n1 2 1\n2 4 5\n1 3 4\n3 4 2', '6',
      '''import sys
import heapq

data = list(map(int, sys.stdin.read().split()))
n, m = data[0], data[1]
adj = [[] for _ in range(n + 1)]
p = 2
for _ in range(m):
    u, v, w = data[p], data[p + 1], data[p + 2]
    p += 3
    adj[u].append((v, w))
    adj[v].append((u, w))
INF = 10 ** 18
dist = [INF] * (n + 1)
dist[1] = 0
pq = [(0, 1)]
while pq:
    d, x = heapq.heappop(pq)
    if d > dist[x]:
        continue
    for y, w in adj[x]:
        if dist[x] + w < dist[y]:
            dist[y] = dist[x] + w
            heapq.heappush(pq, (dist[y], y))
print(-1 if dist[n] >= INF else dist[n])
''',
      lambda r: _gen_graph(r, weighted=True),
      hint='Dijkstra + 优先队列：每次取出当前距离最小的点并松弛它的出边；边权必须非负，用堆可以把复杂度降到 O(m log n)。',
      scope='1 ≤ n ≤ 10⁴，1 ≤ m ≤ 10⁵，1 ≤ w ≤ 10⁴', tags='图论,最短路,Dijkstra'),

    P('多源最短路（Floyd）', 3,
      '给定一个 n 个点、m 条边的正权无向图和 q 次询问，每次询问两个点 u、v，求它们之间的最短距离；若不可达输出 -1。',
      '第一行三个整数 n、m、q；接下来 m 行，每行三个整数 u、v、w；接下来 q 行，每行两个整数 u、v。',
      '每次询问输出一行，一个整数。',
      '4 4 2\n1 2 1\n2 3 2\n3 4 3\n1 4 10\n1 4\n2 4', '6\n5',
      '''import sys

INF = 10 ** 15
data = list(map(int, sys.stdin.read().split()))
n, m, q = data[0], data[1], data[2]
d = [[INF] * (n + 1) for _ in range(n + 1)]
for i in range(1, n + 1):
    d[i][i] = 0
p = 3
for _ in range(m):
    u, v, w = data[p], data[p + 1], data[p + 2]
    p += 3
    if w < d[u][v]:
        d[u][v] = d[v][u] = w
for k in range(1, n + 1):
    for i in range(1, n + 1):
        dik = d[i][k]
        if dik >= INF:
            continue
        row = d[i]
        dk = d[k]
        for j in range(1, n + 1):
            v = dik + dk[j]
            if v < row[j]:
                row[j] = v
out = []
for _ in range(q):
    u, v = data[p], data[p + 1]
    p += 2
    out.append(str(-1 if d[u][v] >= INF else d[u][v]))
print('\\n'.join(out))
''',
      _gen_floyd,
      hint='Floyd 本质是动态规划：三重循环枚举中转点 k，d[i][j] = min(d[i][j], d[i][k] + d[k][j])；k 必须写在最外层。',
      scope='1 ≤ n ≤ 200，1 ≤ m ≤ 10⁴，1 ≤ q ≤ 10⁴', tags='图论,最短路,Floyd'),

    P('拓扑排序（字典序最小）', 3,
      '给定一个 n 个点、m 条边的有向图，输出它的字典序最小的拓扑序列；若图中存在环，输出 -1。',
      '第一行两个整数 n、m；接下来 m 行，每行两个整数 u、v，表示一条 u → v 的有向边。',
      '一行，若可拓扑排序则输出 n 个整数（用空格分隔），否则输出 -1。',
      '4 3\n1 2\n2 3\n1 4', '1 2 3 4',
      '''import sys
import heapq

data = list(map(int, sys.stdin.read().split()))
n, m = data[0], data[1]
indeg = [0] * (n + 1)
adj = [[] for _ in range(n + 1)]
p = 2
for _ in range(m):
    u, v = data[p], data[p + 1]
    p += 2
    adj[u].append(v)
    indeg[v] += 1
heap = [i for i in range(1, n + 1) if indeg[i] == 0]
heapq.heapify(heap)
res = []
while heap:
    x = heapq.heappop(heap)
    res.append(x)
    for y in adj[x]:
        indeg[y] -= 1
        if indeg[y] == 0:
            heapq.heappush(heap, y)
print(' '.join(map(str, res)) if len(res) == n else '-1')
''',
      lambda r: _gen_dag(r),
      hint='不断取出入度为 0 的点，删除它的出边；要得到字典序最小的序列，用**小根堆**代替普通队列即可。',
      scope='1 ≤ n ≤ 10⁴，0 ≤ m ≤ 10⁵', tags='图论,拓扑排序,DAG'),

    P('有向图判环', 3,
      '给定一个 n 个点、m 条边的有向图，判断其中是否存在环。',
      '第一行两个整数 n、m；接下来 m 行，每行两个整数 u、v，表示一条 u → v 的有向边。',
      '一行，有环输出 Yes，否则输出 No。',
      '3 3\n1 2\n2 3\n3 1', 'Yes',
      '''import sys

data = list(map(int, sys.stdin.read().split()))
n, m = data[0], data[1]
indeg = [0] * (n + 1)
adj = [[] for _ in range(n + 1)]
p = 2
for _ in range(m):
    u, v = data[p], data[p + 1]
    p += 2
    adj[u].append(v)
    indeg[v] += 1
from collections import deque
q = deque(i for i in range(1, n + 1) if indeg[i] == 0)
cnt = 0
while q:
    x = q.popleft()
    cnt += 1
    for y in adj[x]:
        indeg[y] -= 1
        if indeg[y] == 0:
            q.append(y)
print('Yes' if cnt < n else 'No')
''',
      lambda r: _gen_directed(r, acyclic=r.random() < 0.5),
      hint='拓扑排序判环：若能被全部弹出（cnt == n）说明无环；剩余点数大于 0 则一定存在环。也可用 DFS 三色标记法。',
      scope='1 ≤ n ≤ 10⁴，0 ≤ m ≤ 10⁵', tags='图论,拓扑排序,判环'),

    P('树的直径', 3,
      '给定一棵 n 个结点的树（边权均为 1），求树的直径，即树中相距最远的两个结点之间的距离（按边数计）。',
      '第一行一个整数 n；接下来 n-1 行，每行两个整数 u、v，表示一条树边。',
      '一行，一个整数，表示直径长度。',
      '5\n1 2\n1 3\n3 4\n3 5', '3',
      '''import sys
from collections import deque

data = list(map(int, sys.stdin.read().split()))
n = data[0]
adj = [[] for _ in range(n + 1)]
p = 1
for _ in range(n - 1):
    u, v = data[p], data[p + 1]
    p += 2
    adj[u].append(v)
    adj[v].append(u)


def bfs(s):
    dist = [-1] * (n + 1)
    dist[s] = 0
    q = deque([s])
    far = s
    while q:
        x = q.popleft()
        if dist[x] > dist[far]:
            far = x
        for y in adj[x]:
            if dist[y] == -1:
                dist[y] = dist[x] + 1
                q.append(y)
    return far, dist[far]


a, _ = bfs(1)
b, d = bfs(a)
print(d)
''',
      lambda r: _gen_tree(r),
      hint='两遍 BFS：先从任意点出发找到最远点 a，再从 a 出发做 BFS，得到的最大距离就是直径（树中结论成立，带权树同样适用）。',
      scope='1 ≤ n ≤ 10⁵', tags='图论,树,直径', kid=8),

    P('二叉树的遍历', 3,
      '给定一棵二叉树的先序遍历序列和中序遍历序列（结点权值互不相同），输出它的后序遍历序列。',
      '两行。第一行为先序遍历序列；第二行为中序遍历序列，结点之间用空格分隔。',
      '一行，后序遍历序列，结点之间用空格分隔。',
      '1 2 4 5 3 6\n4 2 5 1 6 3', '4 5 2 6 3 1',
      '''import sys

data = sys.stdin.read().split('\\n')
pre = list(map(int, data[0].split()))
mid = list(map(int, data[1].split()))
pos = {v: i for i, v in enumerate(mid)}
res = []


def build(pl, pr, ml, mr):
    if pl > pr:
        return
    root = pre[pl]
    k = pos[root]
    build(pl + 1, pl + k - ml, ml, k - 1)
    build(pl + k - ml + 1, pr, k + 1, mr)
    res.append(root)


build(0, len(pre) - 1, 0, len(mid) - 1)
print(' '.join(map(str, res)))
''',
      _gen_tree_trav,
      hint='先序的第一个元素就是根，在中序中找到根的位置即可划分出左右子树，再递归处理；用哈希表记录中序下标可避免线性查找。',
      scope='1 ≤ 结点数 ≤ 10⁴，权值互不相同', tags='数据结构,二叉树,遍历', kid=8),

    P('二叉搜索树查找', 2,
      '依次把 n 个整数插入到一棵初始为空的二叉搜索树中（权值相等时插入右子树），然后查找给定的值 x 是否存在于树中。',
      '第一行两个整数 n、x；第二行 n 个整数，表示插入序列。',
      '一行，存在输出 Yes，否则输出 No。',
      '6 7\n5 3 8 2 4 9', 'No',
      '''import sys

data = list(map(int, sys.stdin.read().split()))
n, x = data[0], data[1]
seq = data[2:2 + n]


class Node:
    __slots__ = ('v', 'l', 'r')

    def __init__(self, v):
        self.v = v
        self.l = None
        self.r = None


root = None
for v in seq:
    nd = Node(v)
    if root is None:
        root = nd
        continue
    cur = root
    while True:
        if v < cur.v:
            if cur.l is None:
                cur.l = nd
                break
            cur = cur.l
        else:
            if cur.r is None:
                cur.r = nd
                break
            cur = cur.r
cur = root
found = False
while cur:
    if x == cur.v:
        found = True
        break
    cur = cur.l if x < cur.v else cur.r
print('Yes' if found else 'No')
''',
      lambda r: (lambda n, seq: '%d %d\n%s' % (
          n, r.choice(seq + [r.randint(1, 200)]), ' '.join(map(str, seq))))(
          r.randint(1, 10), r.sample(range(1, 100), r.randint(1, 10))),
      hint='BST 的中序遍历是有序序列，查找时只需沿一条路径向下比较，平均 O(log n)；注意退化成链时会变成 O(n)。',
      scope='1 ≤ n ≤ 10⁵', tags='数据结构,二叉搜索树', kid=8),

    P('最小的 k 个数', 2,
      '给定 n 个整数和整数 k，输出其中最小的 k 个数（按从小到大的顺序）。',
      '第一行两个整数 n、k；第二行 n 个整数。',
      '一行，k 个整数，用空格分隔。',
      '5 3\n4 5 1 6 2', '1 2 4',
      '''import sys

data = list(map(int, sys.stdin.read().split()))
n, k = data[0], data[1]
a = data[2:2 + n]
a.sort()
print(' '.join(map(str, a[:k])))
''',
      lambda r: (lambda n: '%d %d\n%s' % (n, r.randint(1, n),
                                          ' '.join(str(r.randint(1, 1000)) for _ in range(n))))(r.randint(1, 20)),
      hint='排序取前 k 个最简单；数据量大时用大小为 k 的大根堆维护当前最小的 k 个数，可做到 O(n log k)。',
      scope='1 ≤ k ≤ n ≤ 10⁵', tags='数据结构,堆,排序', kid=8),

    P('合并果子', 3,
      '有 n 堆果子，每堆重量为 aᵢ。每次可以把任意两堆合并成一堆，耗费的体力等于两堆重量之和。求把所有果子合并成一堆的最小总体力。',
      '第一行一个整数 n；第二行 n 个整数。',
      '一行，一个整数，表示最小体力。',
      '3\n1 2 9', '15',
      '''import sys
import heapq

data = list(map(int, sys.stdin.read().split()))
n = data[0]
a = data[1:1 + n]
heapq.heapify(a)
ans = 0
while len(a) > 1:
    x = heapq.heappop(a)
    y = heapq.heappop(a)
    s = x + y
    ans += s
    heapq.heappush(a, s)
print(ans)
''',
      lambda r: (lambda n: '%d\n%s' % (n, ' '.join(str(r.randint(1, 100)) for _ in range(n))))(r.randint(1, 20)),
      hint='哈夫曼贪心：每次取最小的两堆合并，把合并结果放回堆中；用优先队列实现，复杂度 O(n log n)。',
      scope='1 ≤ n ≤ 10⁴', tags='贪心,优先队列,哈夫曼', kid=8),

    P('下一个更大元素', 3,
      '给定一个长度为 n 的整数序列，对每个元素求它右边第一个比它大的元素的值；若不存在，记为 -1。',
      '第一行一个整数 n；第二行 n 个整数。',
      '一行，n 个整数，用空格分隔。',
      '5\n2 1 2 4 3', '4 2 4 -1 -1',
      '''import sys

data = list(map(int, sys.stdin.read().split()))
n = data[0]
a = data[1:1 + n]
res = [-1] * n
st = []
for i in range(n - 1, -1, -1):
    while st and st[-1] <= a[i]:
        st.pop()
    if st:
        res[i] = st[-1]
    st.append(a[i])
print(' '.join(map(str, res)))
''',
      lambda r: (lambda n: '%d\n%s' % (n, ' '.join(str(r.randint(1, 50)) for _ in range(n))))(r.randint(1, 20)),
      hint='单调栈：从右往左扫描，维护一个严格递减的栈，栈顶就是右侧第一个更大的元素；弹出所有不大于当前元素的栈顶后再入栈。',
      scope='1 ≤ n ≤ 10⁵', tags='数据结构,单调栈', kid=8),

    P('滑动窗口最大值', 3,
      '给定一个长度为 n 的整数序列和一个窗口大小 k，求每个长度为 k 的连续子区间中的最大值，按窗口从左到右的顺序输出。',
      '第一行两个整数 n、k；第二行 n 个整数。',
      '一行，n-k+1 个整数，用空格分隔。',
      '8 3\n1 3 -1 -3 5 3 6 7', '3 3 5 5 6 7',
      '''import sys
from collections import deque

data = list(map(int, sys.stdin.read().split()))
n, k = data[0], data[1]
a = data[2:2 + n]
q = deque()
out = []
for i, x in enumerate(a):
    while q and q[-1] < x:
        q.pop()
    q.append(x)
    if i >= k and q[0] == a[i - k]:
        q.popleft()
    if i >= k - 1:
        out.append(str(q[0]))
print(' '.join(out))
''',
      lambda r: (lambda n: '%d %d\n%s' % (n, r.randint(1, n),
                                          ' '.join(str(r.randint(1, 100)) for _ in range(n))))(r.randint(1, 25)),
      hint='单调队列：队列中保持递减，队首即当前窗口最大值；元素滑出窗口时才从队首删除，整体 O(n)。',
      scope='1 ≤ k ≤ n ≤ 10⁵', tags='数据结构,单调队列,滑动窗口', kid=8),

    P('两数之和（哈希表）', 2,
      '给定一个整数序列和一个目标值 target，找出和为目标值的两个元素的下标（下标从 0 开始，答案唯一）；若不存在，输出 -1 -1。',
      '第一行两个整数 n、target；第二行 n 个整数。',
      '一行，两个整数，表示两个下标，小的在前。',
      '4 9\n2 7 11 15', '0 1',
      '''import sys

data = list(map(int, sys.stdin.read().split()))
n, target = data[0], data[1]
a = data[2:2 + n]
seen = {}
ans = (-1, -1)
for i, x in enumerate(a):
    need = target - x
    if need in seen:
        ans = (seen[need], i)
        break
    seen[x] = i
print(ans[0], ans[1])
''',
      lambda r: (lambda n: (lambda a: (lambda i, j: '%d %d\n%s' % (
          n, a[i] + a[j], ' '.join(map(str, a))))(
          r.randrange(n), r.randrange(n)))([r.randint(1, 100) for _ in range(n)]))(r.randint(2, 15)),
      hint='一边扫描一边把"值 → 下标"存入哈希表，对当前元素 x 只需查 target - x 是否已出现过，O(n) 一次遍历。',
      scope='2 ≤ n ≤ 10⁵', tags='数据结构,哈希表', kid=8),

    P('二分图判定', 3,
      '给定一个 n 个点、m 条边的无向图，判断它是否是二分图（能否把点分成两个集合，使得每条边的两个端点分属不同集合）。',
      '第一行两个整数 n、m；接下来 m 行，每行两个整数 u、v，表示一条无向边。',
      '一行，是二分图输出 Yes，否则输出 No。',
      '4 4\n1 2\n2 3\n3 4\n4 1', 'Yes',
      '''import sys
from collections import deque

data = list(map(int, sys.stdin.read().split()))
n, m = data[0], data[1]
adj = [[] for _ in range(n + 1)]
p = 2
for _ in range(m):
    u, v = data[p], data[p + 1]
    p += 2
    adj[u].append(v)
    adj[v].append(u)
color = [0] * (n + 1)
ok = True
for s in range(1, n + 1):
    if color[s]:
        continue
    color[s] = 1
    q = deque([s])
    while q and ok:
        x = q.popleft()
        for y in adj[x]:
            if color[y] == 0:
                color[y] = -color[x]
                q.append(y)
            elif color[y] == color[x]:
                ok = False
                break
print('Yes' if ok else 'No')
''',
      _gen_bipartite,
      hint='BFS/DFS 二染色：从任一点开始染成 1，相邻点必须染成相反颜色；若出现一条边两端颜色相同，说明存在奇环，不是二分图。',
      scope='1 ≤ n ≤ 10⁴，0 ≤ m ≤ 10⁵', tags='图论,二分图,染色'),
]
