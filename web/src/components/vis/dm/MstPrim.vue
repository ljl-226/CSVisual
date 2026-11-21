<template>
  <VisFrame title="最小生成树 · Prim 与 Kruskal" desc="Prim 每次选跨越割的最小边（贪心 + 割性质）；Kruskal 按权值从小到大选边并避开回路（贪心 + 并查集）" :player="player" :status-text="statusText" back-to="/knowledge/32">
    <template #extra>
      <el-radio-group v-model="algo" size="small" @change="player.reset()">
        <el-radio-button value="prim">Prim</el-radio-button>
        <el-radio-button value="kruskal">Kruskal</el-radio-button>
      </el-radio-group>
      <el-select v-model="graphKey" size="small" style="width:140px" @change="onPresetChange">
        <el-option value="g1" label="图 1（6 点）" />
        <el-option value="g2" label="图 2（7 点）" />
      </el-select>
      <el-select v-if="algo === 'prim'" v-model="startIdx" size="small" style="width:110px" @change="player.reset()">
        <el-option v-for="(nd, i) in nodes" :key="nd.id" :value="i" :label="'起点 ' + nd.id" />
      </el-select>
    </template>

    <!-- 自定义带权图：边列表 u-v-w，顶点自动环形排布（与 Dijkstra 组件同一套交互） -->
    <div class="init-bar">
      <span class="init-label">带权边（u-v-w）</span>
      <el-input v-model="edgeInput" size="small" class="init-input"
        placeholder="如 A-B-4,A-D-3,B-D-2（逗号分隔，顶点 2~10 个）"
        @keyup.enter="applyEdges" />
      <el-button size="small" type="primary" plain @click="applyEdges">生成图</el-button>
    </div>

    <div class="ms-wrap">
      <svg :width="W" :height="H" class="ms-svg">
        <!-- 边 -->
        <g>
          <line
            v-for="(e, i) in edges" :key="'e'+i"
            :x1="pos(e.u).x" :y1="pos(e.u).y" :x2="pos(e.v).x" :y2="pos(e.v).y"
            :stroke="edgeColor(e)" :stroke-width="edgeWidth(e)" :stroke-dasharray="edgeDash(e)"
          />
          <text
            v-for="(e, i) in edges" :key="'w'+i"
            :x="(pos(e.u).x + pos(e.v).x) / 2" :y="(pos(e.u).y + pos(e.v).y) / 2 - 5"
            text-anchor="middle" font-size="11" :fill="edgeColor(e)" font-weight="600"
          >{{ e.w }}</text>
        </g>
        <!-- 顶点 -->
        <g>
          <g v-for="nd in nodes" :key="nd.id">
            <circle :cx="nd.x" :cy="nd.y" :r="19" :fill="nodeFill(nd.id)" :stroke="nodeStroke(nd.id)" stroke-width="2" />
            <text :x="nd.x" :y="nd.y + 5" text-anchor="middle" font-size="13" font-weight="700" :fill="nodeText(nd.id)">{{ nd.id }}</text>
          </g>
        </g>
        <text :x="12" :y="18" font-size="12" fill="#8b95a3">
          {{ algo === 'prim' ? '已选集合 S' : '连通分量' }}：{{ setText || '—' }}　|　树权值合计 {{ totalW }}
        </text>
      </svg>

      <div class="ms-panel">
        <div class="info-row"><span>算法</span><b>{{ algo === 'prim' ? 'Prim（加点法）' : 'Kruskal（加边法）' }}</b></div>
        <div class="info-row"><span>顶点数 / 边数</span><b>{{ nodes.length }} / {{ edges.length }}</b></div>
        <div class="info-row"><span>已选边数（需 {{ nodes.length - 1 }} 条）</span><b style="color:var(--success)">{{ tree.length }}</b></div>
        <div class="info-row"><span>当前生成树权值</span><b style="color:var(--brand)">{{ totalW }}</b></div>
        <div class="info-row" v-if="algo === 'prim'">
          <span>候选边（跨越割的边）</span><b>{{ candText || '—' }}</b>
        </div>
        <div class="info-row" v-else>
          <span>当前考察边</span><b :style="{ color: cur.action === 'accept' ? '#22a06b' : '#e05252' }">{{ cur.edgeText || '—' }}</b>
        </div>
        <div class="info-row">
          <span>本步判定</span>
          <el-tag size="small" :type="cur.action === 'reject' ? 'danger' : (cur.action === 'start' ? 'info' : 'success')">
            {{ actionText }}
          </el-tag>
        </div>
        <el-divider />
        <div class="tbl">
          <div class="tbl-head"><span>步骤</span><span>操作</span><span>累计权值</span></div>
          <div v-for="(s, i) in player.steps.value" :key="i" class="tbl-row" :class="{ active: i === player.idx.value }" @click="player.seek(i)">
            <span>{{ s.k }}</span>
            <span :style="{ color: s.action === 'reject' ? '#e05252' : '#22a06b' }">{{ s.short }}</span>
            <span>{{ s.totalW }}</span>
          </div>
        </div>
        <p class="small muted tip">{{ algoNote }}</p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#22a06b"></i> 已选入生成树的边</span>
      <span><i class="dot" style="background:#f2994a"></i> 当前候选 / 考察边</span>
      <span><i class="dot" style="background:#e05252"></i> 被舍弃（会成回路）</span>
      <span><i class="dot" style="background:#3b6ef6"></i> 已在集合中的顶点</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const GRAPHS = {
  g1: {
    nodes: [{ id: 'A', x: 80, y: 90 }, { id: 'B', x: 220, y: 60 }, { id: 'C', x: 360, y: 100 },
            { id: 'D', x: 70, y: 230 }, { id: 'E', x: 220, y: 215 }, { id: 'F', x: 370, y: 235 }],
    edges: [
      { u: 'A', v: 'B', w: 4 }, { u: 'A', v: 'D', w: 3 }, { u: 'B', v: 'C', w: 5 },
      { u: 'B', v: 'D', w: 2 }, { u: 'B', v: 'E', w: 6 }, { u: 'C', v: 'E', w: 3 },
      { u: 'C', v: 'F', w: 4 }, { u: 'D', v: 'E', w: 7 }, { u: 'E', v: 'F', w: 5 }
    ]
  },
  g2: {
    nodes: [
      { id: 'A', x: 300, y: 55 }, { id: 'B', x: 150, y: 110 }, { id: 'C', x: 450, y: 110 },
      { id: 'D', x: 90, y: 215 }, { id: 'E', x: 300, y: 190 }, { id: 'F', x: 500, y: 215 },
      { id: 'G', x: 300, y: 285 }
    ],
    edges: [
      { u: 'A', v: 'B', w: 7 }, { u: 'A', v: 'C', w: 8 }, { u: 'A', v: 'E', w: 5 },
      { u: 'B', v: 'D', w: 6 }, { u: 'B', v: 'E', w: 3 }, { u: 'C', v: 'E', w: 4 },
      { u: 'C', v: 'F', w: 2 }, { u: 'D', v: 'E', w: 9 }, { u: 'E', v: 'F', w: 6 },
      { u: 'E', v: 'G', w: 8 }, { u: 'D', v: 'G', w: 11 }, { u: 'F', v: 'G', w: 10 }
    ]
  }
}
const graphKey = ref('g1')
const algo = ref('prim')
const startIdx = ref(0)

// 自定义图：学生输入自己的带权边，顶点自动环形排布 —— 以前只能看两张示例图
const MAX_CUSTOM_NODES = 10
const MAX_CUSTOM_EDGES = 24
const edgeInput = ref('A-B-4,A-D-3,B-C-5,B-D-2,B-E-6,C-E-3,C-F-4,D-E-7,E-F-5')
const customGraph = ref(null) // null = 用预置示例图

function parseWeightedEdges(raw) {
  const parts = String(raw || '').split(/[,，、\s]+/).map(s => s.trim()).filter(Boolean)
  const vtx = new Set()
  const edges = []
  for (const p of parts) {
    const seg = p.split('-')
    if (seg.length !== 3) return { err: `「${p}」要写成 u-v-w 三段形式，例如 A-B-4` }
    const [a, b, wRaw] = seg
    const w = Number(wRaw)
    if (!a || a.length > 3 || !b || b.length > 3) return { err: `「${p}」顶点名要是 1~3 个字符` }
    if (a === b) return { err: `边「${p}」两端相同（不支持自环）` }
    if (isNaN(w) || w < 0) return { err: `「${p}」的权重要是非负数字` }
    vtx.add(a); vtx.add(b)
    edges.push({ u: a, v: b, w })
  }
  if (!edges.length) return { err: '至少要有一条边，例如 A-B-4' }
  if (vtx.size < 2) return { err: '至少要 2 个顶点' }
  if (vtx.size > MAX_CUSTOM_NODES) return { err: `顶点最多 ${MAX_CUSTOM_NODES} 个，现在有 ${vtx.size} 个` }
  if (edges.length > MAX_CUSTOM_EDGES) return { err: `边最多 ${MAX_CUSTOM_EDGES} 条，现在有 ${edges.length} 条` }
  // 环形布局：画布 560x330，椭圆轨道
  const idList = [...vtx].sort()
  const n = idList.length
  const cx = 280; const cy = 172; const rx = 205; const ry = 108
  const nodesArr = idList.map((id, i) => {
    if (n === 2) return { id, x: i === 0 ? 90 : 470, y: 172 }
    const ang = (Math.PI * 2 * i) / n - Math.PI / 2
    return { id, x: Math.round(cx + rx * Math.cos(ang)), y: Math.round(cy + ry * Math.sin(ang)) }
  })
  return { graph: { nodes: nodesArr, edges } }
}

function applyEdges() {
  const r = parseWeightedEdges(edgeInput.value)
  if (r.err) { ElMessage.warning(r.err); return }
  customGraph.value = r.graph
  startIdx.value = 0
  player.reset()
}

const nodes = computed(() => (customGraph.value || GRAPHS[graphKey.value]).nodes)
const edges = computed(() => (customGraph.value || GRAPHS[graphKey.value]).edges)
const W = 560, H = 330
function pos(id) { return nodes.value.find(n => n.id === id) || { x: 0, y: 0 } }
const algoNote = computed(() => algo.value === 'prim'
  ? 'Prim：维护一棵不断长大的树，每步在所有「一端在树内、一端在树外」的边中取权值最小者（割性质保证最优）。时间复杂度 O(n²)，适合稠密图。'
  : 'Kruskal：把所有边按权值排序，依次尝试加入，若两端已连通则舍弃（否则成回路）。用并查集判连通，时间 O(m log m)，适合稀疏图。')

function buildPrim() {
  const ns = nodes.value, es = edges.value
  const start = ns[startIdx.value].id
  const inS = new Set([start])
  const tree = []
  const out = [{
    k: 0, action: 'start', tree: [], cand: [], inS: [start], totalW: 0,
    short: `起点 ${start}`, edgeText: '',
    desc: `从顶点 ${start} 出发，集合 S = {${start}}，此时还没有边`
  }]
  let k = 1
  while (inS.size < ns.length) {
    const cand = es.filter(e => (inS.has(e.u) && !inS.has(e.v)) || (inS.has(e.v) && !inS.has(e.u)))
    if (!cand.length) break
    cand.sort((a, b) => a.w - b.w)
    const best = cand[0]
    const newNode = inS.has(best.u) ? best.v : best.u
    inS.add(newNode)
    tree.push(best)
    const totalW = tree.reduce((s, e) => s + e.w, 0)
    out.push({
      k, action: 'accept', tree: [...tree], cand: [...cand], inS: Array.from(inS), totalW,
      edge: best,
      edgeText: `(${best.u}-${best.v}) w=${best.w}`,
      short: `加入 ${best.u}-${best.v} (${best.w})`,
      desc: `第 ${k} 步：跨越割的边有 ${cand.map(e => `${e.u}${e.v}:${e.w}`).join('、')}，最小的是 (${best.u}, ${best.v}) 权 ${best.w}；把 ${newNode} 加入 S = {${Array.from(inS).join(',')}}，累计权值 ${totalW}`
    })
    k++
  }
  return out
}

function buildKruskal() {
  const ns = nodes.value, es = edges.value
  const sorted = [...es].sort((a, b) => a.w - b.w)
  const parent = {}
  ns.forEach(n => { parent[n.id] = n.id })
  const find = x => { while (parent[x] !== x) { parent[x] = parent[parent[x]]; x = parent[x] } return x }
  const union = (a, b) => { const ra = find(a), rb = find(b); if (ra === rb) return false; parent[ra] = rb; return true }
  const tree = []
  const out = [{
    k: 0, action: 'start', tree: [], inS: [], comp: { ...parent }, totalW: 0,
    short: '按权值排序', edgeText: '',
    desc: `把所有边按权值从小到大排序：${sorted.map(e => `${e.u}${e.v}:${e.w}`).join('、')}`
  }]
  sorted.forEach((e, i) => {
    const ok = union(e.u, e.v)
    if (ok) tree.push(e)
    const totalW = tree.reduce((s, x) => s + x.w, 0)
    out.push({
      k: i + 1, action: ok ? 'accept' : 'reject', tree: [...tree], inS: [], comp: { ...parent }, totalW,
      edge: e,
      edgeText: `(${e.u}-${e.v}) w=${e.w}`,
      short: ok ? `加入 ${e.u}-${e.v} (${e.w})` : `舍弃 ${e.u}-${e.v} (${e.w})`,
      desc: ok
        ? `考察边 (${e.u}, ${e.v}) 权 ${e.w}：两端属于不同连通分量，加入生成树，累计权值 ${totalW}`
        : `考察边 (${e.u}, ${e.v}) 权 ${e.w}：两端已连通，加入会形成回路，舍弃`
    })
  })
  return out
}

const steps = computed(() => (algo.value === 'prim' ? buildPrim() : buildKruskal()))
const player = usePlayer(steps)
const cur = computed(() => player.current.value || { tree: [], inS: [], cand: [], comp: {}, action: 'start', totalW: 0, edgeText: '', desc: '' })
const statusText = computed(() => cur.value.desc)

const tree = computed(() => cur.value.tree || [])
const totalW = computed(() => cur.value.totalW || 0)

function inTree(e) { return tree.value.some(t => t.u === e.u && t.v === e.v && t.w === e.w) }
function isCand(e) { return (cur.value.cand || []).some(c => c.u === e.u && c.v === e.v && c.w === e.w) }
function isReject(e) { return cur.value.action === 'reject' && cur.value.edge && cur.value.edge.u === e.u && cur.value.edge.v === e.v && cur.value.edge.w === e.w }

function edgeColor(e) {
  if (isReject(e)) return '#e05252'
  if (inTree(e)) return '#22a06b'
  if (isCand(e)) return '#f2994a'
  return '#c8d3e6'
}
function edgeWidth(e) { return inTree(e) ? 3.5 : isCand(e) ? 2.5 : 1.5 }
function edgeDash(e) { return isReject(e) ? '5 4' : '' }

function inSet(id) { return (cur.value.inS || []).includes(id) }
function nodeFill(id) { return inSet(id) ? '#3b6ef6' : '#fff' }
function nodeStroke(id) { return inSet(id) ? '#3b6ef6' : '#c8d3e6' }
function nodeText(id) { return inSet(id) ? '#fff' : '#1f2733' }

const setText = computed(() => {
  if (algo.value === 'prim') return (cur.value.inS || []).join(', ')
  const comp = cur.value.comp || {}
  if (!Object.keys(comp).length) return '—'
  const groups = {}
  Object.keys(comp).forEach(k => {
    const r = (function find(x) { while (comp[x] !== x) x = comp[x]; return x })(k)
    ;(groups[r] = groups[r] || []).push(k)
  })
  return Object.values(groups).map(g => `{${g.join('')}}`).join(' ')
})
const candText = computed(() => (cur.value.cand || []).map(e => `${e.u}${e.v}:${e.w}`).join('　') || '—')

// 切回预置示例图时退出自定义状态，起点也要回到合法范围
function onPresetChange() {
  customGraph.value = null
  startIdx.value = 0
  player.reset()
}
const actionText = computed(() => ({
  start: '初始化',
  accept: '加入生成树',
  reject: '舍弃（成回路）'
})[cur.value.action] || '—')
</script>

<style scoped>
.ms-wrap { display: flex; gap: 18px; align-items: flex-start; flex-wrap: wrap; }
/* 自定义带权图工具行（与 Dijkstra 组件一致） */
.init-bar { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
.init-label { font-size: 12px; color: var(--text-2); white-space: nowrap; }
.init-input { width: 340px; }
.ms-svg { background: #fcfdff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.ms-panel { flex: 1; min-width: 300px; }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; gap: 10px; }
.tbl { font-size: 12px; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
.tbl-head { display: grid; grid-template-columns: 0.6fr 2fr 0.9fr; background: #f6f8fb; padding: 7px 10px; font-weight: 600; }
.tbl-row { display: grid; grid-template-columns: 0.6fr 2fr 0.9fr; padding: 6px 10px; border-top: 1px solid #f0f2f6; cursor: pointer; }
.tbl-row:hover { background: #f6f8fb; }
.tbl-row.active { background: var(--brand-light); color: var(--brand); font-weight: 600; }
.tip { margin-top: 10px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
