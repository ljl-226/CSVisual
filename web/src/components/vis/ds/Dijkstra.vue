<template>
  <VisFrame title="最短路径 · Dijkstra 算法" desc="按路径长度递增次序产生最短路径：每轮从 V-S 中取 dist 最小者并入 S，再松弛它的所有出边" :player="player" :status-text="statusText" back-to="/knowledge/38">
    <template #extra>
      <el-select v-model="gi" size="small" style="width:130px" @change="onGraphChange">
        <el-option v-for="(g, i) in GRAPHS" :key="i" :value="i" :label="g.name" />
      </el-select>
      <el-button size="small" @click="switchGraph">切换示例图</el-button>
      <el-select v-model="src" size="small" style="width:92px">
        <el-option v-for="id in ids" :key="id" :value="id" :label="'源点 ' + id" />
      </el-select>
    </template>

    <!-- 自定义带权图：边列表 u-v-w，顶点自动环形排布 -->
    <div class="init-bar">
      <span class="init-label">带权边（u-v-w）</span>
      <el-input v-model="edgeInput" size="small" class="init-input"
        placeholder="如 A-B-6,A-C-3,B-C-2（逗号分隔，顶点 2~8 个）"
        @keyup.enter="applyEdges" />
      <el-button size="small" type="primary" plain @click="applyEdges">生成图</el-button>
    </div>

    <div class="dj-wrap">
      <svg width="620" height="240" class="dj-svg">
        <line v-for="(e, i) in edges" :key="'e' + i" :x1="e.x1" :y1="e.y1" :x2="e.x2" :y2="e.y2"
          :stroke="edgeColor(e)" :stroke-width="edgeW(e)" />
        <g v-for="e in edges" :key="'w' + e.a + e.b">
          <rect :x="e.mx - 11" :y="e.my - 9" width="22" height="18" rx="4" fill="#ffffff" stroke="#e3e8f0" />
          <text :x="e.mx" :y="e.my + 4" text-anchor="middle" font-size="11" fill="#5a6472">{{ e.w }}</text>
        </g>
        <g v-for="n in nodes" :key="n.id" :transform="`translate(${n.x}, ${n.y})`">
          <circle r="21" :fill="fillOf(n.id)" :stroke="strokeOf(n.id)" stroke-width="2" />
          <text y="5" text-anchor="middle" font-size="13" font-weight="600" :fill="textOf(n.id)">{{ n.id }}</text>
          <text y="36" text-anchor="middle" font-size="11" :fill="strokeOf(n.id)">dist={{ fmt(dist[n.id]) }}</text>
        </g>
      </svg>

      <div class="dj-panel">
        <div class="info-row"><span>源点</span><b style="color:var(--brand)">{{ src }}</b></div>
        <div class="info-row"><span>集合 S</span><b style="color:var(--success)">{{ S.join(', ') || '∅' }}</b></div>
        <div class="info-row"><span>本轮 u</span><b style="color:var(--warning)">{{ cur.u || '-' }}</b></div>
        <div class="info-row"><span>松弛检查次数</span><b>{{ relaxCount }}</b></div>
        <el-divider />
        <table class="dj-table">
          <tbody>
            <tr><th>顶点</th><th>dist</th><th>前驱</th><th>∈S</th></tr>
            <tr v-for="id in ids" :key="id">
              <td>{{ id }}</td><td>{{ fmt(dist[id]) }}</td><td>{{ prev[id] || '—' }}</td><td>{{ S.includes(id) ? '√' : '' }}</td>
            </tr>
          </tbody>
        </table>
        <div class="tip small muted">
          <b>考点：</b>Dijkstra 要求边权非负，时间 O(n²)（邻接矩阵/选最小）或 O((n+e)log n)（堆优化）；
          Floyd 求任意点对、Bellman-Ford 可处理负权。最小生成树的 Prim 与之思想相似。
        </div>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#e8a13a"></i> 本轮选中的 u</span><span><i class="dot" style="background:#22a06b"></i> 已在集合 S 中</span>
      <span><i class="dot" style="background:#3b6ef6"></i> 正在松弛的边</span><span><i class="dot" style="background:#c8d3e6"></i> 未确定顶点/边</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const GRAPHS = [
  {
    name: '示例图 1（6 点）',
    nodes: [{ id: 'v1', x: 60, y: 60 }, { id: 'v2', x: 205, y: 40 }, { id: 'v3', x: 205, y: 165 },
      { id: 'v4', x: 355, y: 100 }, { id: 'v5', x: 505, y: 45 }, { id: 'v6', x: 505, y: 180 }],
    edges: [['v1', 'v2', 6], ['v1', 'v3', 3], ['v2', 'v3', 2], ['v2', 'v4', 5], ['v3', 'v4', 3],
      ['v3', 'v5', 6], ['v4', 'v5', 2], ['v4', 'v6', 4], ['v5', 'v6', 3]]
  },
  {
    name: '示例图 2（5 点）',
    nodes: [{ id: 'a', x: 70, y: 110 }, { id: 'b', x: 225, y: 50 }, { id: 'c', x: 225, y: 180 },
      { id: 'd', x: 395, y: 110 }, { id: 'e', x: 545, y: 110 }],
    edges: [['a', 'b', 10], ['a', 'c', 5], ['b', 'c', 3], ['b', 'd', 1], ['c', 'd', 8], ['c', 'e', 2], ['d', 'e', 4]]
  }
]

// 自定义带权图由学生自己定 —— 以前只有两张示例图，想研究自己的网络拓扑只能干瞪眼。
// 输入 u-v-w 三元组：A-B-6,A-C-3（逗号或空格分隔），顶点自动环形布局。
const MAX_CUSTOM_NODES = 8
const MAX_CUSTOM_EDGES = 20
const edgeInput = ref('A-B-6,A-C-3,B-C-2,B-D-5,C-D-3,C-E-6,D-E-2,D-F-4,E-F-3')
const customGraph = ref(null) // null = 用预置示例图

function parseWeightedEdges(raw) {
  const parts = String(raw || '').split(/[,，、\s]+/).map(s => s.trim()).filter(Boolean)
  const vtx = new Set()
  const edges = []
  for (const p of parts) {
    const seg = p.split('-')
    if (seg.length !== 3) return { err: `「${p}」要写成 u-v-w 三段形式，例如 A-B-6` }
    const [a, b, wRaw] = seg
    const w = Number(wRaw)
    if (!a || a.length > 3 || !b || b.length > 3) return { err: `「${p}」顶点名要是 1~3 个字符` }
    if (a === b) return { err: `边「${p}」两端相同（不支持自环）` }
    if (isNaN(w) || w < 0) return { err: `「${p}」的权重要是非负数字（Dijkstra 不支持负权）` }
    vtx.add(a); vtx.add(b)
    edges.push([a, b, w])
  }
  if (!edges.length) return { err: '至少要有一条边，例如 A-B-6' }
  if (vtx.size < 2) return { err: '至少要 2 个顶点' }
  if (vtx.size > MAX_CUSTOM_NODES) return { err: `顶点最多 ${MAX_CUSTOM_NODES} 个，现在有 ${vtx.size} 个` }
  if (edges.length > MAX_CUSTOM_EDGES) return { err: `边最多 ${MAX_CUSTOM_EDGES} 条，现在有 ${edges.length} 条` }
  // 环形布局：画布 620x240，椭圆轨道
  const idList = [...vtx].sort()
  const n = idList.length
  const cx = 310; const cy = 120; const rx = 230; const ry = 78
  const nodesArr = idList.map((id, i) => {
    if (n === 2) return { id, x: i === 0 ? 80 : 540, y: 120 }
    const ang = (Math.PI * 2 * i) / n - Math.PI / 2
    return { id, x: Math.round(cx + rx * Math.cos(ang)), y: Math.round(cy + ry * Math.sin(ang)) }
  })
  return { graph: { name: '自定义图', nodes: nodesArr, edges } }
}

function applyEdges() {
  const r = parseWeightedEdges(edgeInput.value)
  if (r.err) { ElMessage.warning(r.err); return }
  customGraph.value = r.graph
  src.value = r.graph.nodes[0].id
  player.reset()
  // 自动播一遍最短路径计算过程
  player.play()
}

const gi = ref(0)
const src = ref('v1')
const graph = computed(() => customGraph.value || GRAPHS[gi.value])
const nodes = computed(() => graph.value.nodes)
const ids = computed(() => nodes.value.map(n => n.id))
const pos = computed(() => Object.fromEntries(nodes.value.map(n => [n.id, n])))
const edges = computed(() => graph.value.edges.map(([a, b, w]) => ({
  a, b, w, x1: pos.value[a].x, y1: pos.value[a].y, x2: pos.value[b].x, y2: pos.value[b].y,
  mx: (pos.value[a].x + pos.value[b].x) / 2, my: (pos.value[a].y + pos.value[b].y) / 2
})))

const steps = computed(() => {
  const g = graph.value, srcId = src.value
  const adj = {}
  g.nodes.forEach(n => { adj[n.id] = [] })
  g.edges.forEach(([a, b, w]) => { adj[a].push({ to: b, w }); adj[b].push({ to: a, w }) })
  const dist = {}, prev = {}
  g.nodes.forEach(n => { dist[n.id] = Infinity; prev[n.id] = null })
  if (!(srcId in dist)) return [{ dist, prev, S: [], desc: '源点不存在，请重新选择', u: '', hot: null, relax: 0 }]
  dist[srcId] = 0
  const S = new Set()
  const out = []
  let relax = 0
  // 快照：dist 数组 + 前驱数组 + 集合 S + 本轮 u + 正在检查的边 hot
  function snap(desc, extra = {}) { out.push({ dist: { ...dist }, prev: { ...prev }, S: [...S], desc, u: '', hot: null, relax, ...extra }) }
  snap(`初始化：dist[${srcId}] = 0，其余顶点 dist = ∞，S = ∅`, {})
  for (let k = 0; k < g.nodes.length; k++) {
    let u = null, best = Infinity
    for (const n of g.nodes) if (!S.has(n.id) && dist[n.id] < best) { best = dist[n.id]; u = n.id }
    if (u === null) { snap('剩余顶点 dist 均为 ∞（不可达），算法提前结束', {}); break }
    snap(`第 ${k + 1} 轮：在 V-S 中取 dist 最小者 u = ${u}（dist = ${dist[u]}）`, { u })
    S.add(u)
    snap(`将 ${u} 并入 S：dist[${u}] = ${dist[u]} 已成为最终最短路径长度`, { u })
    for (const e of adj[u]) {
      if (S.has(e.to)) { snap(`邻接点 ${e.to} 已在 S 中，无需松弛`, { u, hot: [u, e.to] }); continue }
      relax++
      const nd = dist[u] + e.w
      if (nd < dist[e.to]) {
        snap(`松弛 (${u},${e.to},w=${e.w})：${dist[u]} + ${e.w} = ${nd} < dist[${e.to}]，更新 dist[${e.to}] = ${nd}，前驱改为 ${u}`, { u, hot: [u, e.to] })
        dist[e.to] = nd; prev[e.to] = u
      } else {
        snap(`检查 (${u},${e.to},w=${e.w})：${nd} ≥ dist[${e.to}] = ${fmt(dist[e.to])}，保持原值`, { u, hot: [u, e.to] })
      }
    }
  }
  snap(`算法结束：得到源点 ${srcId} 的最短路径树（共松弛检查 ${relax} 次）`, {})
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const dist = computed(() => cur.value.dist || {})
const prev = computed(() => cur.value.prev || {})
const S = computed(() => cur.value.S || [])
const relaxCount = computed(() => cur.value.relax || 0)
function fmt(v) { return v === Infinity || v === undefined || v === null ? '∞' : v }
function isHotEdge(e) { const h = cur.value.hot; return !!h && ((h[0] === e.a && h[1] === e.b) || (h[0] === e.b && h[1] === e.a)) }
function isTreeEdge(e) { return prev.value[e.a] === e.b || prev.value[e.b] === e.a }
function edgeColor(e) {
  if (isHotEdge(e)) return '#3b6ef6'
  if (isTreeEdge(e)) return '#22a06b'
  return '#c8d3e6'
}
function edgeW(e) { return isHotEdge(e) || isTreeEdge(e) ? 2.6 : 1.5 }
function fillOf(id) { if (id === cur.value.u) return '#fdf3e2'; return S.value.includes(id) ? '#dcf3e7' : '#ffffff' }
function strokeOf(id) { if (id === cur.value.u) return '#e8a13a'; return S.value.includes(id) ? '#22a06b' : '#c8d3e6' }
function textOf(id) { return S.value.includes(id) || id === cur.value.u ? '#176b48' : '#1f2733' }

function onGraphChange() {
  customGraph.value = null // 切回示例图，退出自定义状态
  src.value = ids.value[0]
  player.reset()
}
function switchGraph() { gi.value = (gi.value + 1) % GRAPHS.length; onGraphChange() }
</script>

<style scoped>
.dj-wrap { display: flex; gap: 24px; align-items: flex-start; flex-wrap: wrap; }

/* 自定义带权图工具行 */
.init-bar {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 12px; flex-wrap: wrap;
}
.init-label { font-size: 12px; color: var(--text-2); white-space: nowrap; }
.init-input { width: 340px; }
.dj-svg { flex-shrink: 0; background: #fbfcff; border-radius: 8px; }
.dj-panel { flex: 1; min-width: 260px; }
.info-row { display: flex; justify-content: space-between; gap: 10px; padding: 4px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.dj-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.dj-table th, .dj-table td { border: 1px solid var(--border); padding: 3px 8px; text-align: center; }
.dj-table th { background: #f4f6fa; color: var(--text-2); font-weight: 600; }
.tip { margin-top: 10px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
