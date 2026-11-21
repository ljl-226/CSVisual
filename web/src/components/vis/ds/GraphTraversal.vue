<template>
  <VisFrame :title="`图的遍历 · ${algo === 'bfs' ? 'BFS 广度优先' : 'DFS 深度优先'}`" :desc="algo === 'bfs' ? '借助队列，先访问完一层再访问下一层' : '借助递归栈，一路走到底再回溯'" :player="player" :status-text="statusText" back-to="/knowledge/8">
    <template #extra>
      <el-radio-group v-model="algo" size="small">
        <el-radio-button value="bfs">BFS</el-radio-button>
        <el-radio-button value="dfs">DFS</el-radio-button>
      </el-radio-group>
      <span class="small muted">起点</span>
      <el-select v-model="start" size="small" style="width:70px">
        <el-option v-for="n in nodes" :key="n" :value="n" :label="'v' + n" />
      </el-select>
      <el-button size="small" plain @click="player.reset()">重置</el-button>
    </template>

    <!-- 自定义图：边列表不再写死，学生想研究哪张图的遍历就画哪张 -->
    <div class="init-bar">
      <span class="init-label">图的边（u-v）</span>
      <el-input v-model="edgeInput" size="small" class="init-input"
        placeholder="如 0-1,0-2,1-3（逗号或空格分隔，顶点最多 10 个）"
        @keyup.enter="applyEdges" />
      <el-button size="small" type="primary" plain @click="applyEdges">生成图</el-button>
    </div>

    <div class="gt-wrap">
      <svg width="360" height="360" class="gt-svg">
        <line
          v-for="(e, i) in edgeList" :key="i"
          :x1="pos(e[0]).x" :y1="pos(e[0]).y" :x2="pos(e[1]).x" :y2="pos(e[1]).y"
          :stroke="edgeStroke(e)" :stroke-width="edgeWidth(e)"
        />
        <g v-for="n in nodes" :key="n" :transform="`translate(${pos(n).x}, ${pos(n).y})`">
          <circle r="22" :fill="fillOf(n)" :stroke="strokeOf(n)" stroke-width="2" />
          <circle v-if="n === scanTarget()" r="28" fill="none" :stroke="scanKind === 'skip' ? '#e05252' : '#e8a13a'" stroke-width="2" stroke-dasharray="4 3" />
          <text y="5" text-anchor="middle" font-size="13" font-weight="600" :fill="textOf(n)">v{{ n }}</text>
          <text y="-28" text-anchor="middle" font-size="10" :fill="n === current ? '#3b6ef6' : '#8b95a3'">
            {{ depthOf(n) !== null ? 'd=' + depthOf(n) : '' }}
          </text>
        </g>
      </svg>

      <div class="gt-panel">
        <div class="panel-title">{{ algo === 'bfs' ? '辅助队列（队头 → 队尾）' : '递归调用栈（栈底 → 栈顶）' }}</div>
        <div class="aux-queue">
          <span v-for="(v, i) in auxList" :key="i" class="q-item">v{{ v }}</span>
          <span v-if="!auxList.length" class="small muted">（空）</span>
        </div>

        <div class="panel-title" style="margin-top:14px">访问序列</div>
        <div class="seq">
          <span v-for="(v, i) in visited" :key="i" class="seq-item">{{ 'v' + v }}</span>
          <span v-if="current !== null" class="seq-item seq-cur">v{{ current }}</span>
        </div>

        <el-divider />
        <div class="info-row"><span>已访问顶点</span><b>{{ visited.length }} / {{ nodes.length }}</b></div>
        <div class="info-row"><span>访问边数</span><b>{{ edgeCount }}</b></div>
        <div class="info-row">
          <span>时间复杂度（邻接表）</span><b>O(V + E)</b>
        </div>
        <div class="tip small muted">
          BFS 常用于求解<b>无权图单源最短路径</b>；DFS 常用于<b>拓扑排序、连通分量</b>判断。
        </div>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> 当前访问顶点</span>
      <span><i class="dot" style="background:#22a06b"></i> 已访问</span>
      <span><i class="dot" style="background:#fdf3e2"></i> 在队列/栈中待访问</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

// 图由学生自己定 —— 以前 8 个顶点和邻接表写死，想换张图研究遍历只能干瞪眼。
// 输入是无向边列表：0-1,0-2,1-3（逗号或空格分隔），顶点集从边里提取。
const MAX_NODES = 10
const MAX_EDGES = 20
const DEFAULT_EDGES = '0-1,0-2,1-3,1-4,2-5,2-6,3-7,4-7,5-7,6-7'
const edgeInput = ref(DEFAULT_EDGES)

function parseEdges(raw) {
  const parts = String(raw || '').split(/[,，、\s]+/).map(s => s.trim()).filter(Boolean)
  const seen = new Set()
  const edges = []
  const vtx = new Set()
  for (const p of parts) {
    const m = p.match(/^(\d+)-(\d+)$/)
    if (!m) return { err: `「${p}」不是合法的边，要写成 u-v 形式，例如 0-1` }
    const a = Number(m[1]); const b = Number(m[2])
    if (a === b) return { err: `边「${p}」两端相同（不支持自环）` }
    vtx.add(a); vtx.add(b)
    const key = [Math.min(a, b), Math.max(a, b)].join('-')
    if (!seen.has(key)) { seen.add(key); edges.push([a, b]) }
  }
  if (!edges.length) return { err: '至少要有一条边，例如 0-1' }
  if (vtx.size > MAX_NODES) return { err: `顶点最多 ${MAX_NODES} 个，现在有 ${vtx.size} 个，环形布局摆不下` }
  if (edges.length > MAX_EDGES) return { err: `边最多 ${MAX_EDGES} 条，现在有 ${edges.length} 条` }
  return { edges, nodesList: [...vtx].sort((a, b) => a - b) }
}

function buildAdj(edgeArr) {
  const adj = {}
  edgeArr.forEach(([a, b]) => {
    ;(adj[a] = adj[a] || []).push(b)
    ;(adj[b] = adj[b] || []).push(a)
  })
  return adj
}

const parsed = parseEdges(DEFAULT_EDGES)
const nodes = ref(parsed.nodesList)
const adj = ref(buildAdj(parsed.edges))

function applyEdges() {
  const r = parseEdges(edgeInput.value)
  if (r.err) { ElMessage.warning(r.err); return }
  nodes.value = r.nodesList
  adj.value = buildAdj(r.edges)
  start.value = r.nodesList[0]
  player.reset()
  // 自动播一遍遍历过程：从起点出发把整张图走一遍
  player.play()
}

const algo = ref('bfs')
const start = ref(0)

const edgeList = computed(() => {
  const set = new Set()
  const out = []
  nodes.value.forEach(u => {
    ;(adj.value[u] || []).forEach(v => {
      const key = [Math.min(u, v), Math.max(u, v)].join('-')
      if (!set.has(key)) { set.add(key); out.push([u, v]) }
    })
  })
  return out
})

function pos(n) {
  const list = nodes.value
  if (list.length === 1) return { x: 180, y: 180 }
  const angle = (Math.PI * 2 * list.indexOf(n)) / list.length - Math.PI / 2
  return { x: 180 + 118 * Math.cos(angle), y: 180 + 118 * Math.sin(angle) }
}

const steps = computed(() => {
  const out = []
  const visited = []
  const depth = {}
  const inQueue = []
  const visitedSet = new Set()
  const treeEdges = []

  if (algo.value === 'bfs') {
    const queue = [start.value]
    depth[start.value] = 0
    out.push({ visited: [], cur: null, aux: [...queue], depth: { ...depth }, treeEdges: [], desc: `起点 v${start.value} 入队，开始广度优先遍历` })
    while (queue.length) {
      const u = queue.shift()
      visited.push(u)
      visitedSet.add(u)
      out.push({
        visited: [...visited], cur: u, aux: [...queue], depth: { ...depth },
        treeEdges: treeEdges.map(e => [...e]),
        desc: `队首 v${u} 出队并访问（距起点 ${depth[u]} 层）`
      })
      adj.value[u].forEach(v => {
        if (!visitedSet.has(v) && !queue.includes(v)) {
          queue.push(v)
          depth[v] = depth[u] + 1
          treeEdges.push([u, v])
          out.push({
            visited: [...visited], cur: null, aux: [...queue], depth: { ...depth },
            scan: [u, v], scanKind: 'enqueue', treeEdges: treeEdges.map(e => [...e]),
            desc: `检查边 v${u}→v${v}：邻接点 v${v} 未访问 → 入队（第 ${depth[v]} 层）`
          })
        } else {
          out.push({
            visited: [...visited], cur: null, aux: [...queue], depth: { ...depth },
            scan: [u, v], scanKind: 'skip', treeEdges: treeEdges.map(e => [...e]),
            desc: `检查边 v${u}→v${v}：邻接点 v${v} 已访问或已在队列中，跳过`
          })
        }
      })
    }
  } else {
    const stack = []
    function dfs(u, d) {
      visited.push(u)
      visitedSet.add(u)
      depth[u] = d
      stack.push(u)
      out.push({
        visited: [...visited], cur: u, aux: [...stack], depth: { ...depth },
        treeEdges: treeEdges.map(e => [...e]),
        desc: `访问 v${u}（深度 ${d}），压入递归栈`
      })
      for (const v of adj.value[u]) {
        if (!visitedSet.has(v)) {
          treeEdges.push([u, v])
          out.push({
            visited: [...visited], cur: null, aux: [...stack], depth: { ...depth },
            scan: [u, v], scanKind: 'descend', treeEdges: treeEdges.map(e => [...e]),
            desc: `检查边 v${u}→v${v}：未访问 → 沿此边深入`
          })
          dfs(v, d + 1)
        } else {
          out.push({
            visited: [...visited], cur: null, aux: [...stack], depth: { ...depth },
            scan: [u, v], scanKind: 'skip', treeEdges: treeEdges.map(e => [...e]),
            desc: `检查边 v${u}→v${v}：邻接点 v${v} 已访问，跳过`
          })
        }
      }
      stack.pop()
      out.push({
        visited: [...visited], cur: null, aux: [...stack], depth: { ...depth },
        treeEdges: treeEdges.map(e => [...e]),
        desc: `v${u} 的所有邻接点处理完毕 → 回溯`
      })
    }
    out.push({ visited: [], cur: null, aux: [], depth: {}, treeEdges: [], desc: `从起点 v${start.value} 开始深度优先遍历` })
    dfs(start.value, 0)
  }
  out.push({ visited: [...visited], cur: null, aux: [], depth: { ...depth }, desc: `遍历结束，访问序列：[${visited.map(v => 'v' + v).join(' → ')}]` })
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || { visited: [], cur: null, aux: [], depth: {}, desc: '' })
const statusText = computed(() => cur.value.desc)
const visited = computed(() => cur.value.visited || [])
const auxList = computed(() => cur.value.aux || [])
const current = computed(() => cur.value.cur ?? null)

watch([algo, start], () => player.reset())

// 正在检查的边：让「跳过邻接点」这类步骤也有画面变化，
// 否则连续几步画面完全静止，用户只看到文案在跳。
const scanEdge = computed(() => cur.value.scan || null)
const scanKind = computed(() => cur.value.scanKind || null)
// 树边 = 首次访问某顶点所经过的边，这才是遍历真正「走过」的边
const edgeCount = computed(() => (cur.value.treeEdges || []).length)

function depthOf(n) {
  const d = cur.value.depth || {}
  return d[n] !== undefined ? d[n] : null
}
function fillOf(n) {
  if (n === current.value) return '#3b6ef6'
  if (visited.value.includes(n)) return '#dcf3e7'
  if (auxList.value.includes(n)) return '#fdf3e2'
  return '#fff'
}
function strokeOf(n) {
  if (n === current.value) return '#3b6ef6'
  if (visited.value.includes(n)) return '#22a06b'
  if (auxList.value.includes(n)) return '#e8a13a'
  return '#c8d3e6'
}
function textOf(n) {
  if (n === current.value) return '#fff'
  if (visited.value.includes(n)) return '#176b48'
  return '#1f2733'
}
function isScan(e) {
  const s = scanEdge.value
  if (!s) return false
  return (s[0] === e[0] && s[1] === e[1]) || (s[0] === e[1] && s[1] === e[0])
}
function isTree(e) {
  return (cur.value.treeEdges || []).some(t =>
    (t[0] === e[0] && t[1] === e[1]) || (t[0] === e[1] && t[1] === e[0]))
}
function edgeActive(e) {
  return isScan(e) || e[0] === current.value || e[1] === current.value
}
function edgeStroke(e) {
  if (isScan(e)) return scanKind.value === 'skip' ? '#e05252' : '#e8a13a'
  if (isTree(e)) return '#22a06b'
  if (e[0] === current.value || e[1] === current.value) return '#3b6ef6'
  if (visited.value.includes(e[0]) && visited.value.includes(e[1])) return '#a9dcc2'
  return '#dde3ec'
}
function edgeWidth(e) {
  return isScan(e) ? 3.4 : (isTree(e) ? 2.6 : 1.6)
}
/** 当前扫描的目标邻接点：给它加个圈，指明注意力落点 */
function scanTarget() {
  const s = scanEdge.value
  return s ? s[1] : null
}
</script>

<style scoped>
.gt-wrap { display: flex; gap: 24px; align-items: flex-start; flex-wrap: wrap; }

/* 自定义图工具行 */
.init-bar {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 12px; flex-wrap: wrap;
}
.init-label { font-size: 12px; color: var(--text-2); white-space: nowrap; }
.init-input { width: 320px; }
.gt-svg { background: #fbfcff; border-radius: 8px; flex-shrink: 0; }
.gt-panel { flex: 1; min-width: 260px; }
.panel-title { font-size: 13px; font-weight: 600; margin-bottom: 6px; color: var(--text-2); }
.aux-queue { display: flex; gap: 6px; flex-wrap: wrap; border: 1px dashed var(--border); border-radius: 8px; padding: 8px; min-height: 40px; background: #fbfcff; }
.q-item {
  min-width: 34px; height: 28px; line-height: 28px; text-align: center; border-radius: 4px;
  background: #fdf3e2; border: 1px solid #f0d9ae; font-size: 12px; font-weight: 600;
}
.seq { display: flex; gap: 6px; flex-wrap: wrap; min-height: 30px; }
.seq-item {
  min-width: 34px; height: 28px; line-height: 28px; text-align: center; border-radius: 4px;
  background: #dcf3e7; border: 1px solid var(--success); font-size: 12px; font-weight: 600; color: #176b48;
}
.seq-cur { background: var(--brand); border-color: var(--brand); color: #fff; }
.info-row { display: flex; justify-content: space-between; padding: 4px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.tip { margin-top: 10px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
