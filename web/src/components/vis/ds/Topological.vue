<template>
  <VisFrame title="拓扑排序 · 关键路径" desc="AOV 网：反复输出入度为 0 的顶点并删去其出边；若输出顶点数少于 n，则图中存在环" :player="player" :status-text="statusText" back-to="/knowledge/39">
    <template #extra>
      <el-input v-model="edgeInput" size="small" style="width:290px" placeholder="A->B:3, B->C:2（:后为权值，可省略）" />
      <el-button size="small" @click="applyEdges">应用</el-button>
      <el-button size="small" plain @click="resetAll">重置</el-button>
    </template>

    <div class="tp-wrap">
      <svg :width="svgW" :height="svgH" class="tp-svg">
        <defs><marker id="tp-ar" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 z" fill="#8b95a3" /></marker></defs>
        <line v-for="(e, i) in drawEdges" :key="'e' + i" :x1="e.x1" :y1="e.y1" :x2="e.x2" :y2="e.y2"
          stroke="#c8d3e6" stroke-width="1.6" marker-end="url(#tp-ar)" />
        <text v-for="(e, i) in drawEdges" :key="'w' + i" :x="(e.x1 + e.x2) / 2 + 6" :y="(e.y1 + e.y2) / 2" font-size="11" fill="#8b95a3">{{ e.w }}</text>
        <g v-for="n in layout" :key="n.id" :transform="`translate(${n.x}, ${n.y})`">
          <rect x="-27" y="-17" width="54" height="34" rx="6" :fill="fillOf(n.id)" :stroke="strokeOf(n.id)" stroke-width="2" />
          <text y="6" text-anchor="middle" font-size="14" font-weight="600" :fill="textOf(n.id)">{{ n.id }}</text>
          <circle cx="27" cy="-17" r="9" :fill="badgeFill(n.id)" stroke="#fff" stroke-width="1.5" />
          <text x="27" y="-13" text-anchor="middle" font-size="10" fill="#fff">{{ indeg[n.id] }}</text>
        </g>
        <text x="4" :y="svgH - 62" font-size="12" fill="#5a6472">入度为 0 的顶点队列：</text>
        <g v-for="(id, i) in queue" :key="'q' + i" :transform="`translate(${130 + i * 44}, ${svgH - 74})`">
          <rect width="38" height="28" rx="5" fill="#eef3ff" stroke="#3b6ef6" />
          <text x="19" y="19" text-anchor="middle" font-size="13" fill="#3b6ef6">{{ id }}</text>
        </g>
        <text v-if="!queue.length" x="134" :y="svgH - 55" font-size="12" fill="#8b95a3">（队空）</text>
      </svg>

      <div class="tp-panel">
        <div class="info-row"><span>顶点数 / 弧数</span><b>{{ g.nodes.length }} / {{ g.edges.length }}</b></div>
        <div class="info-row"><span>当前出队顶点</span><b style="color:var(--warning)">{{ cur.cur || '-' }}</b></div>
        <div class="info-row"><span>拓扑序列</span><b>{{ order.join(' → ') || '—' }}</b></div>
        <div class="info-row"><span>检测结果</span><b :style="{ color: hasCycle ? 'var(--danger)' : 'var(--success)' }">{{ hasCycle ? '存在环，无法拓扑排序' : (cur.done ? 'AOV 网，排序成功' : '进行中…') }}</b></div>
        <el-divider />
        <div class="panel-title">入度表</div>
        <table class="tp-table">
          <tbody>
            <tr><th>顶点</th><th v-for="n in g.nodes" :key="'h' + n">{{ n }}</th></tr>
            <tr><td>入度</td><td v-for="n in g.nodes" :key="'d' + n">{{ indeg[n] }}</td></tr>
          </tbody>
        </table>
        <div class="panel-title" style="margin-top:10px">关键路径（AOE 网，权值=活动时间）</div>
        <div class="small muted" v-if="!cp">图中存在环，无法求关键路径</div>
        <div v-else>
          <div class="small">ve：{{ g.nodes.map(n => n + '=' + cp.ve[n]).join(' ') }}</div>
          <div class="small">vl：{{ g.nodes.map(n => n + '=' + cp.vl[n]).join(' ') }}</div>
          <div class="small">关键活动：<b style="color:var(--danger)">{{ cp.acts.join('、') || '无' }}</b></div>
        </div>
        <div class="tip small muted">考点：拓扑排序时间 O(n+e)，结果<b>不唯一</b>；<b>有环当且仅当</b>输出顶点数 &lt; n。关键路径由 ve/vl 相等的活动组成，决定工程最短工期。</div>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#22a06b"></i> 已输出顶点</span><span><i class="dot" style="background:#e8a13a"></i> 当前出队顶点</span>
      <span><i class="dot" style="background:#3b6ef6"></i> 入度为 0（已入队）</span><span><i class="dot" style="background:#e05252"></i> 环中顶点</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const DEFAULT = 'A->B:3, A->C:2, B->D:4, C->D:3, C->E:5, D->F:2, E->F:4, F->G:1'
const edgeInput = ref(DEFAULT)
const src = ref(DEFAULT)
// 解析 AOV/AOE 网：A->B 或 A->B:权值
const g = computed(() => {
  const set = new Set(), edges = []
  src.value.split(/[,，;；\n]+/).map(s => s.trim()).filter(Boolean).forEach(it => {
    const m = it.match(/^([A-Za-z0-9]+)\s*->\s*([A-Za-z0-9]+)(?::(\d+))?$/)
    if (!m) return
    edges.push({ u: m[1], v: m[2], w: m[3] ? Number(m[3]) : 1 })
    set.add(m[1]); set.add(m[2])
  })
  return { nodes: [...set].sort(), edges }
})

const steps = computed(() => {
  const gg = g.value
  if (!gg.nodes.length) return [{ desc: '未解析到有效弧，请输入形如 A->B 的边', indeg: {}, queue: [], order: [], cur: '' }]
  const indeg = {}, out = {}
  gg.nodes.forEach(n => { indeg[n] = 0; out[n] = [] })
  gg.edges.forEach(e => { indeg[e.v]++; out[e.u].push(e) })
  const q = []
  const order = []
  const list = []
  // 快照：入度表副本 + 队列副本 + 已输出的拓扑序列 + 当前顶点
  function snap(desc, extra = {}) { list.push({ indeg: { ...indeg }, queue: [...q], order: [...order], cur: '', desc, ...extra }) }
  // 先拍「刚统计完入度」这一刻 —— 此时队列必须还是空的。
  // 之前在拍快照前就把入度 0 的顶点塞进了 q，于是「统计入度」那一步画面上
  // 队列里已经有 A 了，和文案自相矛盾。
  snap(`统计各顶点入度，得到入度表（共 ${gg.nodes.length} 个顶点、${gg.edges.length} 条弧）`, {})
  gg.nodes.filter(n => indeg[n] === 0).forEach(n => q.push(n))
  snap(q.length ? `入度为 0 的顶点入队：${q.join(', ')}` : '没有入度为 0 的顶点，图中必有环', {})
  while (q.length) {
    const u = q.shift()
    snap(`队首 ${u} 出队，输出到拓扑序列`, { cur: u })
    order.push(u)
    snap(`删除以 ${u} 为尾的所有弧（共 ${out[u].length} 条）`, { cur: u })
    for (const e of out[u]) {
      indeg[e.v]--
      if (indeg[e.v] === 0) {
        q.push(e.v)
        snap(`弧 ${u}→${e.v} 删去后 ${e.v} 入度变为 0，${e.v} 入队`, { cur: u, check: e.v })
      } else {
        snap(`弧 ${u}→${e.v} 删去后 ${e.v} 入度降为 ${indeg[e.v]}，暂不入队`, { cur: u, check: e.v })
      }
    }
  }
  if (order.length < gg.nodes.length) {
    snap(`输出顶点数 ${order.length} < ${gg.nodes.length}：剩余 ${gg.nodes.filter(n => !order.includes(n)).join(',')} 构成环，无法拓扑排序`, { cycle: true })
  } else {
    snap(`拓扑排序完成：${order.join(' → ')}（若同时有多个入度 0 顶点，结果不唯一）`, { done: true })
  }
  return list
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const indeg = computed(() => cur.value.indeg || {})
const queue = computed(() => cur.value.queue || [])
const order = computed(() => cur.value.order || [])
// 环只能由算法跑完后的收尾步骤来判定。中途队列为空是正常的（刚出队、尚未把后继入队），
// 若在这里补判会给出「存在环」的假结论
const hasCycle = computed(() => !!cur.value.cycle)

// 分层布局：入度 0 的顶点在第 0 层，其余取最长前驱层 +1
const levels = computed(() => {
  const lv = {}, od = {}
  g.value.nodes.forEach(n => { lv[n] = 0; od[n] = 0 })
  g.value.edges.forEach(e => od[e.v]++)
  const dq = g.value.nodes.filter(n => od[n] === 0)
  const seen = []
  while (dq.length) {
    const u = dq.shift(); seen.push(u)
    g.value.edges.filter(e => e.u === u).forEach(e => {
      lv[e.v] = Math.max(lv[e.v], lv[u] + 1)
      if (--od[e.v] === 0) dq.push(e.v)
    })
  }
  g.value.nodes.forEach(n => { if (!seen.includes(n)) lv[n] = 0 })
  return lv
})
const layout = computed(() => {
  const cnt = {}
  return g.value.nodes.map(n => {
    const L = levels.value[n] || 0
    cnt[L] = (cnt[L] || 0) + 1
    return { id: n, x: 50 + (cnt[L] - 1) * 116, y: 40 + L * 74, L }
  })
})
const pos = computed(() => Object.fromEntries(layout.value.map(n => [n.id, n])))
const drawEdges = computed(() => g.value.edges.filter(e => pos.value[e.u] && pos.value[e.v]).map(e => ({
  ...e, x1: pos.value[e.u].x, y1: pos.value[e.u].y + 17, x2: pos.value[e.v].x, y2: pos.value[e.v].y - 21
})))
const svgW = computed(() => Math.max(560, Math.max(0, ...layout.value.map(n => n.x)) + 90))
const svgH = computed(() => 40 + (Math.max(0, ...layout.value.map(n => n.L)) + 1) * 74 + 130)

// 关键路径：拓扑序求 ve，逆序求 vl，ve(u)==vl(v)-w 的活动为关键活动
const cp = computed(() => {
  const gg = g.value, od = {}, out = {}
  gg.nodes.forEach(n => { od[n] = 0; out[n] = [] })
  gg.edges.forEach(e => { od[e.v]++; out[e.u].push(e) })
  const dq = gg.nodes.filter(n => od[n] === 0), topo = []
  while (dq.length) { const u = dq.shift(); topo.push(u); out[u].forEach(e => { if (--od[e.v] === 0) dq.push(e.v) }) }
  if (topo.length < gg.nodes.length) return null
  const ve = {}, vl = {}
  gg.nodes.forEach(n => { ve[n] = 0 })
  topo.forEach(u => out[u].forEach(e => { ve[e.v] = Math.max(ve[e.v], ve[u] + e.w) }))
  const end = Math.max(...gg.nodes.map(n => ve[n]))
  gg.nodes.forEach(n => { vl[n] = end })
  topo.slice().reverse().forEach(u => out[u].forEach(e => { vl[u] = Math.min(vl[u], vl[e.v] - e.w) }))
  const acts = gg.edges.filter(e => ve[e.u] === vl[e.v] - e.w).map(e => `${e.u}→${e.v}`)
  return { ve, vl, acts }
})

function fillOf(id) {
  if (cur.value.cycle && !order.value.includes(id)) return '#fbdada'
  if (id === cur.value.cur) return '#fdf3e2'
  if (order.value.includes(id)) return '#dcf3e7'
  return indeg.value[id] === 0 ? '#e6eeff' : '#ffffff'
}
function strokeOf(id) {
  if (cur.value.cycle && !order.value.includes(id)) return '#e05252'
  if (id === cur.value.cur) return '#e8a13a'
  if (order.value.includes(id)) return '#22a06b'
  return indeg.value[id] === 0 ? '#3b6ef6' : '#c8d3e6'
}
function textOf(id) { return order.value.includes(id) ? '#176b48' : (id === cur.value.cur ? '#a5701a' : '#1f2733') }
function badgeFill(id) { return indeg.value[id] === 0 ? '#22a06b' : '#e8a13a' }

function applyEdges() { src.value = edgeInput.value || DEFAULT; player.reset() }
function resetAll() { src.value = DEFAULT; edgeInput.value = DEFAULT; player.reset() }
</script>

<style scoped>
.tp-wrap { display: flex; gap: 24px; align-items: flex-start; flex-wrap: wrap; }
.tp-svg { flex-shrink: 0; background: #fbfcff; border-radius: 8px; }
.tp-panel { flex: 1; min-width: 270px; }
.info-row { display: flex; justify-content: space-between; gap: 10px; padding: 4px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.panel-title { font-size: 13px; font-weight: 600; margin-bottom: 4px; color: var(--text-2); }
.tp-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.tp-table th, .tp-table td { border: 1px solid var(--border); padding: 3px 6px; text-align: center; }
.tp-table th { background: #f4f6fa; color: var(--text-2); font-weight: 600; }
.tip { margin-top: 10px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
