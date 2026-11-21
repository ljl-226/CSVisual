<template>
  <VisFrame title="图的连通性与欧拉回路" desc="先按各顶点度数的奇偶性判定存在性，再用 Fleury 算法逐边走一遍：每步优先走非桥边，只有别无选择时才走桥" :player="player" :status-text="statusText" back-to="/knowledge/65">
    <template #extra>
      <el-select v-model="presetKey" size="small" style="width:250px" @change="onPresetChange">
        <el-option v-for="p in PRESETS" :key="p.key" :value="p.key" :label="p.label" />
      </el-select>
      <el-button size="small" plain @click="resetAll">重置</el-button>
    </template>

    <!-- 自定义图：用顶点编号输入边（无向），自动判定连通性 / 度数 / 欧拉性 -->
    <div class="init-bar">
      <span class="init-label">无向边（u-v）</span>
      <el-input v-model="edgeInput" size="small" class="init-input"
        placeholder="如 1-2,2-3,3-1,2-4,4-5,5-2（逗号分隔，顶点 2~10 个）"
        @keyup.enter="applyEdges" />
      <el-button size="small" type="primary" plain @click="applyEdges">生成图</el-button>
    </div>

    <div class="eu-wrap">
      <svg :width="W" :height="H" class="eu-svg">
        <rect x="4" y="4" :width="W - 8" :height="H - 8" rx="10" fill="#fcfdff" stroke="#c8d3e6" />
        <text x="14" y="24" font-size="12" fill="#8b95a3">无向图 G：n = {{ G.n }} 个顶点，m = {{ G.edges.length }} 条边</text>
        <!-- 边：绿 = 已走过，橙 = 本步选中，红虚线 = 桥（本步要避开） -->
        <line v-for="(e, i) in edgeView" :key="'e' + i" :x1="e.x1" :y1="e.y1" :x2="e.x2" :y2="e.y2"
              :stroke="estyle(i).stroke" :stroke-width="estyle(i).w" :stroke-dasharray="estyle(i).dash" stroke-linecap="round" />
        <g v-for="v in nodes" :key="'v' + v.i">
          <circle :cx="v.x" :cy="v.y" :r="v.cur ? 20 : 17" :fill="v.cur ? '#3b6ef6' : '#fff'"
                  :stroke="v.odd ? '#e8a13a' : '#8b5cf6'" :stroke-width="v.odd ? 3 : 1.8" />
          <text :x="v.x" :y="v.y + 4" text-anchor="middle" font-size="12" font-weight="700" :fill="v.cur ? '#fff' : '#1f2733'">v{{ v.i + 1 }}</text>
          <text :x="v.x" :y="v.y + 34" text-anchor="middle" font-size="11" :fill="v.odd ? '#e8a13a' : '#8b5cf6'">d={{ v.deg }}</text>
        </g>
      </svg>

      <div class="eu-panel">
        <div class="info-row"><span>判定结果</span><el-tag size="small" :type="verdict.tag">{{ verdict.text }}</el-tag></div>
        <div class="info-row"><span>连通性</span><b :style="{ color: conn ? '#22a06b' : '#e05252' }">{{ conn ? '连通 ✓' : '不连通 ✗' }}</b></div>
        <div class="info-row"><span>当前顶点</span><b style="color:var(--brand)">{{ atTxt }}</b></div>
        <div class="info-row"><span>奇度顶点集合</span><b :style="{ color: odd.length ? '#e8a13a' : '#22a06b' }">{{ oddTxt }}（{{ odd.length }} 个）</b></div>
        <div class="info-row"><span>剩余边数</span><b>{{ cur.remain }} / {{ G.edges.length }}</b></div>
        <div class="info-row"><span>已走边数</span><b style="color:#22a06b">{{ cur.used.length }}</b></div>
        <div class="seq">
          <div class="small muted">走过的顶点序列</div>
          <code>{{ pathTxt }}</code>
        </div>
        <p class="small muted tip">{{ TIP }}</p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> 当前所在顶点</span>
      <span><i class="dot" style="background:#e8a13a"></i> 奇度顶点 / 本步选中的边</span>
      <span><i class="dot" style="background:#8b5cf6"></i> 偶度顶点</span>
      <span><i class="dot" style="background:#22a06b"></i> 已走过的边</span>
      <span><i class="dot" style="background:#e05252"></i> 桥（除非别无选择，否则不走）</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const W = 380, H = 300, CX = 190, CY = 152, R = 100
// 预设示例图：顶点下标 0..n-1（显示为 v1..vn），edges 为无向边 [u, v]
const PRESETS = [
  { key: 'bow', label: '欧拉回路图 · 双三角（全偶度）', n: 5, edges: [[0, 1], [1, 2], [2, 0], [2, 3], [3, 4], [4, 2]] },
  { key: 'k5', label: '欧拉回路图 · K5（每点 4 度）', n: 5, edges: [[0, 1], [0, 2], [0, 3], [0, 4], [1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]] },
  { key: 'path', label: '欧拉通路（非回路）· 两三角 + 一座桥', n: 6, edges: [[0, 1], [1, 2], [2, 0], [2, 3], [3, 4], [4, 5], [5, 3]] },
  { key: 'k4', label: '非欧拉图 · K4（4 个奇度顶点）', n: 4, edges: [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]] },
  { key: 'disc', label: '非欧拉图 · 不连通（三角形 + 一条边）', n: 5, edges: [[0, 1], [1, 2], [2, 0], [3, 4]] }
]
const presetKey = ref('bow')

// 自定义图：学生输入自己的边（顶点用编号 1..n），以前只能看五个预设
const MAX_CUSTOM_NODES = 10
const MAX_CUSTOM_EDGES = 24
const edgeInput = ref('1-2,2-3,3-1,2-4,4-5,5-2')
const customG = ref(null) // null = 用预设图

function parseEdges(raw) {
  const parts = String(raw || '').split(/[,，、\s]+/).map(s => s.trim()).filter(Boolean)
  let maxV = 0
  const seen = new Set()
  const edges = []
  for (const p of parts) {
    const seg = p.split('-')
    if (seg.length !== 2) return { err: `「${p}」要写成 u-v 两段形式，例如 1-2` }
    const a = Number(seg[0]), b = Number(seg[1])
    if (!Number.isInteger(a) || !Number.isInteger(b) || a < 1 || b < 1) return { err: `「${p}」顶点要用 1 开始的整数编号` }
    if (a === b) return { err: `边「${p}」两端相同（不支持自环）` }
    maxV = Math.max(maxV, a, b)
    const key = a < b ? a + '-' + b : b + '-' + a
    if (seen.has(key)) continue // 重复边自动去重
    seen.add(key)
    edges.push([a - 1, b - 1]) // 内部下标从 0 开始，显示时仍为 v1..vn
  }
  if (!edges.length) return { err: '至少要有一条边，例如 1-2' }
  if (maxV > MAX_CUSTOM_NODES) return { err: `顶点最多 ${MAX_CUSTOM_NODES} 个（编号 1~${MAX_CUSTOM_NODES}）` }
  if (edges.length > MAX_CUSTOM_EDGES) return { err: `边最多 ${MAX_CUSTOM_EDGES} 条，现在有 ${edges.length} 条` }
  return { graph: { n: maxV, edges } }
}

function applyEdges() {
  const r = parseEdges(edgeInput.value)
  if (r.err) { ElMessage.warning(r.err); return }
  customG.value = r.graph
  player.reset()
}

// 兜底：顶点数至少 2，非法边（越界 / 自环）直接丢弃，保证不崩
const G = computed(() => {
  if (customG.value) return customG.value
  const p = PRESETS.find(x => x.key === presetKey.value) || PRESETS[0]
  const n = Math.max(2, p.n | 0)
  const edges = (p.edges || []).filter(e => Array.isArray(e) && e[0] >= 0 && e[1] >= 0 && e[0] < n && e[1] < n && e[0] !== e[1])
  return { n, edges }
})
function resetAll() { customG.value = null; presetKey.value = 'bow'; player.reset() }

function onPresetChange() { customG.value = null; player.reset() }

/* ---------------- 图论基本工具 ---------------- */
// 顶点均匀排在圆周上
function posOf(n, i) {
  const a = -Math.PI / 2 + i * 2 * Math.PI / n
  return { x: CX + R * Math.cos(a), y: CY + R * Math.sin(a) }
}
const degOf = (n, edges) => { const d = Array.from({ length: n }, () => 0); edges.forEach(([u, v]) => { d[u]++; d[v]++ }); return d }
// 从 from 出发沿 edgeIdx 中的边（可排除 without）做 BFS，返回可达顶点集合
function reachable(edgeIdx, edges, from, without = -1) {
  const seen = new Set([from]), st = [from]
  while (st.length) {
    const x = st.pop()
    for (const i of edgeIdx) {
      if (i === without) continue
      const [u, v] = edges[i]
      if (u === x && !seen.has(v)) { seen.add(v); st.push(v) }
      else if (v === x && !seen.has(u)) { seen.add(u); st.push(u) }
    }
  }
  return seen
}
// 桥：在剩余边集 rem 中删掉边 k 后，其两端不再连通
const isBridge = (rem, k, edges) => !reachable(rem, edges, edges[k][0], k).has(edges[k][1])
const connected = (n, edges) => {
  const d = degOf(n, edges), s = d.findIndex(x => x > 0)
  if (s < 0 || !edges.length) return false
  const seen = reachable(edges.map((_, i) => i), edges, s)
  return d.every((x, i) => x === 0 || seen.has(i))
}

const deg = computed(() => degOf(G.value.n, G.value.edges))
const odd = computed(() => deg.value.map((d, i) => (d % 2 ? i : -1)).filter(i => i >= 0))
const conn = computed(() => connected(G.value.n, G.value.edges))
const vtx = i => 'v' + (i + 1)

/* ---------------- 步骤快照：判定 + Fleury 逐边走 ---------------- */
const steps = computed(() => {
  const { n, edges } = G.value
  const out = [], m = edges.length, d = deg.value, od = odd.value
  const vt = od.map(vtx).join('、')
  let rem = edges.map((_, i) => i), usedEdge = [], path = [], at = -1
  // 每帧快照：已走过的边、顶点序列、当前顶点、剩余度、本步选中边与桥
  function snap(desc, extra = {}) {
    const rd = Array.from({ length: n }, () => 0)
    rem.forEach(i => { rd[edges[i][0]]++; rd[edges[i][1]]++ })
    out.push({ used: [...usedEdge], path: [...path], at, deg: d, odd: od, remain: rem.length, remDeg: rd, pick: -1, bridges: [], desc, ...extra })
  }
  if (!m || !conn.value) {
    snap(`该图${m ? '不连通' : '没有边'}，不满足「连通」这个前提 → 既无欧拉回路，也无欧拉通路`, { dead: true })
    return out
  }
  at = od.length === 2 ? od[0] : d.findIndex(x => x > 0) // 有奇度顶点则必须从奇度顶点出发
  path = [at]
  snap(`统计度数：${d.map((x, i) => `d(${vtx(i)})=${x}`).join('，')}；奇度顶点 ${od.length} 个${od.length ? `（${vt}）` : ''} → ${
    od.length === 0 ? '全为偶度，存在欧拉回路' : od.length === 2 ? `恰 2 个，存在欧拉通路（端点 ${vt}）` : `${od.length} 个，不存在欧拉通路/回路`}`)
  while (rem.length) {
    const cands = edges.map((e, i) => ({ e, i }))
      .filter(({ e, i }) => rem.includes(i) && (e[0] === at || e[1] === at))
      .map(({ e, i }) => ({ i, to: e[0] === at ? e[1] : e[0] }))
    if (!cands.length) {
      snap(`走到 ${vtx(at)} 已无未走过的边，但还剩 ${rem.length} 条边 → 一笔画不完，此图不是欧拉图（至少需 ${Math.max(1, od.length / 2)} 笔）`, { stuck: true })
      break
    }
    const bridges = cands.filter(c => isBridge(rem, c.i, edges)).map(c => c.i)
    const safe = cands.find(c => !bridges.includes(c.i))
    const pick = safe || cands[0] // 全是桥时别无选择，只能走桥
    const why = safe
      ? `在 ${vtx(at)} 有 ${cands.length} 条未走过的边，选中边 e(${vtx(at)}→${vtx(pick.to)})，去掉它剩余图仍连通，它不是桥，可以安全走过`
      : `在 ${vtx(at)} 的 ${cands.length} 条边全是桥（${bridges.map(i => `e(${vtx(edges[i][0])}→${vtx(edges[i][1])})`).join('、')}），别无选择，只能走 e(${vtx(at)}→${vtx(pick.to)})`
    usedEdge = [...usedEdge, pick.i]
    rem = rem.filter(x => x !== pick.i)
    at = pick.to
    path = [...path, at]
    snap(why, { pick: pick.i, bridges })
  }
  if (!rem.length) {
    const back = path[0] === path[path.length - 1]
    const ok = od.length === 0 ? back : od.length === 2
    snap(`走完全部 ${m} 条边且每条恰好一次：${path.map(vtx).join('→')} → ${
      ok ? (od.length === 0 ? '回到起点，是一条欧拉回路 ✓' : '两端恰为两个奇度顶点，是一条欧拉通路（无回路）✓') : '不构成欧拉通路 ✗'}`, { done: true })
  }
  return out
})
const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)

/* ---------------- 视图 ---------------- */
const nodes = computed(() => Array.from({ length: G.value.n }, (_, i) => {
  const p = posOf(G.value.n, i)
  return { i, x: p.x, y: p.y, deg: deg.value[i], odd: deg.value[i] % 2 === 1, cur: cur.value.at === i }
}))
const edgeView = computed(() => G.value.edges.map(([u, v]) => {
  const a = posOf(G.value.n, u), b = posOf(G.value.n, v)
  const dx = b.x - a.x, dy = b.y - a.y, t = 20 / (Math.hypot(dx, dy) || 1)
  return { x1: a.x + dx * t, y1: a.y + dy * t, x2: b.x - dx * t, y2: b.y - dy * t }
}))
function estyle(i) {
  const c = cur.value
  if ((c.used || []).includes(i)) return { stroke: '#22a06b', w: 3.4, dash: '0' }
  if (c.pick === i) return { stroke: '#e8a13a', w: 4.2, dash: '0' }
  if ((c.bridges || []).includes(i)) return { stroke: '#e05252', w: 2.2, dash: '5 4' }
  return { stroke: '#c8d3e6', w: 1.6, dash: '0' }
}
const verdict = computed(() => {
  if (!conn.value) return { tag: 'danger', text: '不连通 → 无欧拉通路/回路' }
  if (!odd.value.length) return { tag: 'success', text: '欧拉图：存在欧拉回路' }
  if (odd.value.length === 2) return { tag: 'warning', text: '半欧拉图：有欧拉通路、无回路' }
  return { tag: 'danger', text: `非欧拉图：奇度顶点 ${odd.value.length} 个` }
})
const pathTxt = computed(() => (cur.value.path || []).map(vtx).join(' → ') || '—')
const oddTxt = computed(() => odd.value.map(vtx).join('、') || '∅')
const atTxt = computed(() => (cur.value.at >= 0 ? `${vtx(cur.value.at)}（度 ${cur.value.deg[cur.value.at]}，剩余 ${cur.value.remDeg[cur.value.at]}）` : '—'))
const TIP = '考点：① 判定定理 —— 无向连通图 G 是欧拉图（存在欧拉回路）当且仅当所有顶点都是偶度顶点；恰有 2 个奇度顶点时是半欧拉图（存在欧拉通路但无回路，两个端点就是那 2 个奇度顶点）；奇度顶点 ≥ 4 个则一笔画不完，至少需 k/2 笔。' +
  '② 欧拉图中一定没有桥（有桥则桥的两端必为奇度）。③ Fleury 算法：每步优先选「非桥」的边走，只有别无选择时才走桥，否则会把剩余图切断而走不完。' +
  '④ 对比：哈密顿回路（经过每个顶点恰好一次）是 NP 完全问题，至今没有类似的简洁充要条件，只有 Dirac、Ore 等充分条件。'
</script>

<style scoped>
.eu-wrap { display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap; }
/* 自定义图工具行（与 Dijkstra / MST 组件一致） */
.init-bar { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
.init-label { font-size: 12px; color: var(--text-2); white-space: nowrap; }
.init-input { width: 340px; }
.eu-svg { flex-shrink: 0; background: #fcfdff; border: 1px solid var(--border); border-radius: 10px; }
.eu-panel { flex: 1; min-width: 290px; }
.info-row { display: flex; justify-content: space-between; gap: 12px; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.seq { margin-top: 10px; }
.seq code { background: #f2f4f8; padding: 8px 10px; border-radius: 6px; display: block; font-size: 12px; line-height: 1.8; word-break: break-all; }
.tip { margin-top: 10px; line-height: 1.8; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
