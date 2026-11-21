<template>
  <VisFrame title="B+ 树 · 插入与结点分裂" desc="所有数据存放在叶子结点，叶子间用链表相连；结点关键字溢出时向上分裂" :player="player" :status-text="statusText" back-to="/knowledge/5">
    <template #extra>
      <span class="small muted">阶数 m = {{ order }}（每结点最多 {{ order }} 个关键字）</span>
      <el-input v-model="newKey" size="small" style="width:80px" placeholder="关键字" />
      <el-button size="small" @click="addKey">插入</el-button>
      <el-button size="small" plain @click="rebuild">重置</el-button>
    </template>

    <!-- 自定义初始键集：插入序列不再写死，学生想研究哪组建树过程就用哪组 -->
    <div class="init-bar">
      <span class="init-label">初始键集</span>
      <el-input v-model="keysInput" size="small" class="init-input"
        placeholder="如 10,20,5,6（逗号或空格分隔，最多 12 个）"
        @keyup.enter="applyKeys" />
      <el-button size="small" type="primary" plain @click="applyKeys">重新建树</el-button>
    </div>

    <svg :width="svgW" :height="svgH" class="b-svg">
      <!-- 结点间连线 -->
      <line
        v-for="(e, i) in edges" :key="'e' + i"
        :x1="e.x1" :y1="e.y1" :x2="e.x2" :y2="e.y2"
        :stroke="e.hl ? '#3b6ef6' : '#d6dde8'" :stroke-width="e.hl ? 2.2 : 1.5"
      />
      <!-- 叶子链表 -->
      <path v-for="(l, i) in leafLinks" :key="'l' + i" :d="l.d" stroke="#22a06b" stroke-width="1.4" fill="none" marker-end="url(#arrow-green)" />
      <!-- 结点 -->
      <g v-for="n in flatNodes" :key="n.id" :transform="`translate(${n._x}, ${n._y})`">
        <rect
          :x="-n._w / 2" :y="-16" :width="n._w" height="32" rx="6"
          :fill="n.id === hlId ? '#dbe8ff' : '#fff'"
          :stroke="n.id === hlId ? '#3b6ef6' : (n.isLeaf ? '#22a06b' : '#8b95a3')"
          :stroke-width="n.id === hlId ? 2.4 : 1.6"
        />
        <g v-for="(k, ki) in n.keys" :key="ki">
          <rect
            :x="-n._w / 2 + 8 + ki * KEY_W" :y="-11" :width="KEY_W - 4" height="22" rx="4"
            :fill="n.id === hlId && ki === hlKeyIndex ? '#3b6ef6' : '#f7f9fc'"
            :stroke="n.id === hlId && ki === hlKeyIndex ? '#3b6ef6' : '#e3e8f0'"
          />
          <text
            :x="-n._w / 2 + 8 + ki * KEY_W + (KEY_W - 4) / 2" y="5" text-anchor="middle"
            font-size="12" font-weight="600"
            :fill="n.id === hlId && ki === hlKeyIndex ? '#fff' : '#1f2733'"
          >{{ k }}</text>
          <line v-if="ki > 0" :x1="-n._w / 2 + ki * KEY_W" y1="-16" :x2="-n._w / 2 + ki * KEY_W" y2="16" stroke="#e3e8f0" />
        </g>
        <text :x="-n._w / 2" y="-22" font-size="10" :fill="n.isLeaf ? '#22a06b' : '#8b95a3'">
          {{ n.isLeaf ? '叶子' : '索引' }}
        </text>
      </g>
      <defs>
        <marker id="arrow-green" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
          <path d="M0,0 L7,3 L0,6 z" fill="#22a06b" />
        </marker>
      </defs>
    </svg>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> 本次操作结点</span>
      <span><i class="dot" style="background:#22a06b"></i> 叶子结点（存放数据）+ 链表</span>
      <span><i class="dot" style="background:#8b95a3"></i> 非叶结点（只存索引）</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const order = 3
const KEY_W = 40
const PAD = 8
const GAP = 18
const LEVEL_H = 90

const newKey = ref(18)
// 初始键集由学生自己定 —— 以前 [10,20,5,...] 写死，想换组数研究分裂只能干瞪眼
const MAX_KEYS = 12
const keysInput = ref('10,20,5,6,12,30,7,17')
const initVals = ref([10, 20, 5, 6, 12, 30, 7, 17]) // 初始键集（「重新建树/重置」回到它）
const keys = ref([...initVals.value]) // 工作键集（「插入」按钮往这里追加）

function applyKeys() {
  const raw = String(keysInput.value || '')
  const vals = raw
    .split(/[,，、\s]+/)
    .map(s => s.trim())
    .filter(Boolean)
    .map(Number)
  if (!vals.length || vals.some(isNaN)) {
    ElMessage.warning('键集要是数字，用逗号或空格分隔，例如 10,20,5')
    return
  }
  if (vals.length > MAX_KEYS) {
    ElMessage.warning(`初始键集最多 ${MAX_KEYS} 个，再多树就太深了`)
    return
  }
  initVals.value = vals
  keys.value = [...vals]
  newKey.value = vals[vals.length - 1] + 1
  player.reset()
  // 自动播一遍建树过程：一个键一个键插进去，分裂时机看得清清楚楚
  player.play()
}

/* ---------- B+ 树实现 ---------- */
let nid = 0
function createNode(isLeaf) {
  return { id: nid++, isLeaf, keys: [], children: [] }
}

function clone(node) {
  return {
    id: node.id,
    isLeaf: node.isLeaf,
    keys: [...node.keys],
    children: node.children.map(clone)
  }
}

function insertInto(node, key, events) {
  if (node.isLeaf) {
    node.keys.push(key)
    node.keys.sort((a, b) => a - b)
    if (node.keys.length > order) {
      const mid = Math.ceil(node.keys.length / 2)
      const right = createNode(true)
      right.keys = node.keys.slice(mid)
      node.keys = node.keys.slice(0, mid)
      events.push({ type: 'leaf-split', nodeId: node.id, newNodeId: right.id, upKey: right.keys[0] })
      return { upKey: right.keys[0], newNode: right }
    }
    return null
  }
  let i = 0
  while (i < node.keys.length && key >= node.keys[i]) i++
  const res = insertInto(node.children[i], key, events)
  if (!res) return null
  node.keys.splice(i, 0, res.upKey)
  node.children.splice(i + 1, 0, res.newNode)
  if (node.keys.length > order) {
    const mid = Math.floor(node.keys.length / 2)
    const right = createNode(false)
    right.keys = node.keys.slice(mid + 1)
    right.children = node.children.slice(mid + 1)
    const upKey = node.keys[mid]
    node.keys = node.keys.slice(0, mid)
    node.children = node.children.slice(0, mid + 1)
    events.push({ type: 'inner-split', nodeId: node.id, upKey })
    return { upKey, newNode: right }
  }
  return null
}

/* ---------- 步骤生成 ---------- */
const steps = computed(() => {
  nid = 0
  let root = createNode(true)
  const out = []
  out.push({ tree: clone(root), hl: null, hlKey: -1, desc: '初始为空树：只有一个空的叶子结点（同时是根）' })
  for (const k of keys.value) {
    const events = []
    const res = insertInto(root, k, events)
    if (res) {
      const newRoot = createNode(false)
      newRoot.keys = [res.upKey]
      newRoot.children = [root, res.newNode]
      root = newRoot
      out.push({
        tree: clone(root), hl: null, hlKey: -1,
        desc: `插入 ${k} 后根结点溢出，分裂产生新根（关键字 ${res.upKey} 上移），树高 +1`
      })
    } else {
      out.push({
        tree: clone(root), hl: null, hlKey: -1,
        desc: `插入 ${k}：沿索引逐层比较，落到叶子结点后有序插入`
      })
    }
    events.forEach(e => {
      if (e.type === 'leaf-split') {
        out.push({
          tree: clone(root), hl: e.nodeId, hlKey: -1,
          desc: `叶子结点关键字数超过 ${order}，从中间分裂：右半部分成为新叶子，关键字 ${e.upKey} 复制到父结点`
        })
      } else if (e.type === 'inner-split') {
        out.push({
          tree: clone(root), hl: e.nodeId, hlKey: -1,
          desc: `非叶结点溢出，中间关键字 ${e.upKey} 上移到父结点`
        })
      }
    })
  }
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || { tree: null, hl: null, hlKey: -1, desc: '' })
const statusText = computed(() => cur.value.desc)
const hlId = computed(() => cur.value.hl)
const hlKeyIndex = ref(-1)

/* ---------- 布局 ---------- */
const flatNodes = computed(() => {
  const root = cur.value.tree
  if (!root) return []
  const nodes = []
  function measure(n) {
    const w = n.keys.length * KEY_W + PAD * 2
    if (n.isLeaf) { n._w = w; return w }
    let cw = n.children.reduce((s, c) => s + measure(c) + GAP, 0) - GAP
    n._w = Math.max(w, cw)
    return n._w
  }
  function place(n, x, depth) {
    n._y = 34 + depth * LEVEL_H
    nodes.push(n)
    if (n.isLeaf) { n._x = x + n._w / 2; return }
    const total = n.children.reduce((s, c) => s + c._w + GAP, 0) - GAP
    let cx = x + (n._w - total) / 2
    n.children.forEach(c => { place(c, cx, depth + 1); cx += c._w + GAP })
    const first = n.children[0]
    const last = n.children[n.children.length - 1]
    n._x = (first._x + last._x) / 2
  }
  measure(root)
  place(root, 0, 0)
  return nodes
})

const edges = computed(() => {
  const out = []
  flatNodes.value.forEach(n => {
    if (n.isLeaf) return
    n.children.forEach(c => {
      out.push({ x1: n._x, y1: n._y + 16, x2: c._x, y2: c._y - 16, hl: n.id === hlId.value })
    })
  })
  return out
})

const leafLinks = computed(() => {
  const leaves = flatNodes.value.filter(n => n.isLeaf)
  const out = []
  for (let i = 0; i < leaves.length - 1; i++) {
    const a = leaves[i]
    const b = leaves[i + 1]
    const y = a._y + 26
    out.push({ d: `M${a._x + a._w / 2 - 4},${y} L${b._x - b._w / 2 + 4},${y}` })
  }
  return out
})

const svgW = computed(() => Math.max(520, Math.max(0, ...flatNodes.value.map(n => n._x + n._w / 2)) + 30))
const svgH = computed(() => Math.max(160, Math.max(0, ...flatNodes.value.map(n => n._y)) + 60))

function addKey() {
  const v = Number(newKey.value)
  if (isNaN(v)) return
  keys.value.push(v)
  newKey.value = v + 1
}
function rebuild() {
  // 回到「当前初始键集」的建树过程，而不是某组写死的键
  keys.value = [...initVals.value]
  newKey.value = initVals.value[initVals.value.length - 1] + 1
  player.reset()
}
</script>

<style scoped>
.b-svg { display: block; background: #fbfcff; border-radius: 8px; }

/* 自定义初始键集工具行 */
.init-bar {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 12px; flex-wrap: wrap;
}
.init-label { font-size: 12px; color: var(--text-2); white-space: nowrap; }
.init-input { width: 260px; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
