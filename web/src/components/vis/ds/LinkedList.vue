<template>
  <VisFrame title="单链表 · 插入与删除" desc="观察结点指针（next）在插入、删除时如何改变" :player="player" :status-text="statusText" back-to="/knowledge/1">
    <template #extra>
      <el-input v-model="newValue" size="small" style="width:80px" placeholder="值" />
      <el-button size="small" @click="addOp('head')">头插</el-button>
      <el-button size="small" @click="addOp('tail')">尾插</el-button>
      <el-input-number v-model="pos" size="small" :min="1" :max="20" style="width:90px" />
      <el-button size="small" @click="addOp('insert')">按位插</el-button>
      <el-button size="small" type="danger" plain @click="addOp('delete')">删除</el-button>
      <el-button size="small" plain @click="resetOps">重置操作</el-button>
    </template>

    <!-- 自定义初始链表：默认链表不再写死，学生想研究哪条链就生成哪条 -->
    <div class="init-bar">
      <span class="init-label">初始链表</span>
      <el-input
        v-model="initInput" size="small" class="init-input"
        placeholder="如 7,12,25（逗号或空格分隔，最多 10 个）"
        @keyup.enter="applyInit"
      />
      <el-button size="small" type="primary" plain @click="applyInit">生成链表</el-button>
    </div>

    <svg :width="svgWidth" :height="150" class="vis-svg">
      <!-- 头指针 head -->
      <g>
        <rect x="10" y="58" width="52" height="34" rx="6" fill="#eef3ff" stroke="#3b6ef6" />
        <text x="36" y="80" text-anchor="middle" font-size="13" fill="#3b6ef6">head</text>
        <!-- 结点从 x=90 开始，箭头到 86 停住：以前画到 92，直接穿进结点边框里 -->
        <line x1="62" y1="75" x2="86" y2="75" stroke="#3b6ef6" stroke-width="1.6" marker-end="url(#arrow-b)" />
      </g>

      <g v-for="(n, i) in nodes" :key="n.id" :transform="`translate(${90 + i * 100}, 45)`">
        <!-- next 指针箭头：下一结点从 +100 开始，箭头到 97 停住，别顶住边框 -->
        <line v-if="i < nodes.length - 1" x1="72" y1="23" x2="97" y2="23" stroke="#8b95a3" stroke-width="1.6" marker-end="url(#arrow-g)" />
        <!-- NULL 居中写在 next 格（44..72，中心 58）里；以前 x=70 左对齐，文字从格右缘往外溢 -->
        <text v-else x="58" y="28" text-anchor="middle" font-size="11" fill="#8b95a3">NULL</text>

        <rect
          width="44" height="46" rx="6"
          :fill="fillOf(i)" :stroke="strokeOf(i)" stroke-width="1.6"
        />
        <rect x="44" width="28" height="46" rx="6" :fill="fillOf(i, true)" :stroke="strokeOf(i)" stroke-width="1.6" />
        <line x1="44" y1="0" x2="44" y2="46" :stroke="strokeOf(i)" stroke-width="1.4" />
        <circle v-if="i < nodes.length - 1" cx="58" cy="23" r="4" :fill="strokeOf(i)" />
        <text x="22" y="29" text-anchor="middle" font-size="14" :fill="textOf(i)" font-weight="600">{{ n.v }}</text>
        <text x="22" y="-10" text-anchor="middle" font-size="11" fill="#8b95a3">结点{{ i + 1 }}</text>
      </g>

      <defs>
        <marker id="arrow-b" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
          <path d="M0,0 L7,3 L0,6 z" fill="#3b6ef6" />
        </marker>
        <marker id="arrow-g" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
          <path d="M0,0 L7,3 L0,6 z" fill="#8b95a3" />
        </marker>
      </defs>
      <text v-if="!nodes.length" x="160" y="80" font-size="13" fill="#8b95a3">空链表（head → NULL）</text>
    </svg>

    <template #legend>
      <span><i class="dot" style="background:#22a06b"></i> 新插入结点</span>
      <span><i class="dot" style="background:#3b6ef6"></i> 当前操作位置</span>
      <span><i class="dot" style="background:#e05252"></i> 待删除结点</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const newValue = ref(9)
const pos = ref(2)

// 初始链表由学生自己定 —— 以前的演示序列（头插3、按位插18、删除2）是写死的，
// 想换个链表研究只能干瞪眼。现在：输入一串数 -> 生成 -> 所有插入删除都基于它。
const MAX_NODES = 10
const initInput = ref('7,12,25')
const initVals = ref([7, 12, 25])

/** 把「初始链表」翻译成操作序列：init 清空 + 逐个尾插 */
function buildOps(vals) {
  return [{ type: 'init', value: null }, ...vals.map(v => ({ type: 'tail', value: v }))]
}

const ops = ref(buildOps(initVals.value))

const steps = computed(() => {
  let nodes = []
  let id = 0
  const out = []
  for (const op of ops.value) {
    if (op.type === 'init') {
      nodes = []
      out.push({ nodes: [], hl: -1, danger: -1, desc: '初始化空链表：head 指向 NULL' })
      continue
    }
    if (op.type === 'head') {
      nodes = [{ v: op.value, id: id++ }, ...nodes]
      out.push({ nodes: nodes.map(n => ({ ...n })), hl: 0, danger: -1, desc: `头插 ${op.value}：新结点 next 指向原首元结点，再更新 head` })
    } else if (op.type === 'tail') {
      nodes = [...nodes, { v: op.value, id: id++ }]
      out.push({ nodes: nodes.map(n => ({ ...n })), hl: nodes.length - 1, danger: -1, desc: `尾插 ${op.value}：遍历到表尾，令尾结点 next 指向新结点` })
    } else if (op.type === 'insert') {
      const p = Math.min(Math.max(1, op.pos), nodes.length + 1)
      const before = nodes.map(n => ({ ...n }))
      const danger = p - 1 < nodes.length ? p - 1 : -1
      nodes = [...nodes.slice(0, p - 1), { v: op.value, id: id++ }, ...nodes.slice(p - 1)]
      out.push({ nodes: nodes.map(n => ({ ...n })), hl: p - 1, danger: -1, desc: `在第 ${p} 位插入 ${op.value}：先找到第 ${p - 1} 个结点（前驱），再改指针` })
    } else if (op.type === 'delete') {
      const p = Math.min(Math.max(1, op.pos), nodes.length)
      const removed = nodes[p - 1]
      out.push({ nodes: nodes.map(n => ({ ...n })), hl: -1, danger: p - 1, desc: `删除第 ${p} 位结点（值 ${removed ? removed.v : '-'}）：前驱 next 直接指向其后继` })
      nodes = nodes.filter((_, i) => i !== p - 1)
      out.push({ nodes: nodes.map(n => ({ ...n })), hl: -1, danger: -1, desc: `结点已摘除，释放空间，链表长度减 1` })
    }
  }
  return out
})

const player = usePlayer(steps)
const current = computed(() => player.current.value || { nodes: [], hl: -1, danger: -1, desc: '' })
const nodes = computed(() => current.value.nodes)
const statusText = computed(() => current.value.desc)
const svgWidth = computed(() => Math.max(560, nodes.value.length * 100 + 140))

function fillOf(i, isNext) {
  if (i === current.value.danger) return isNext ? '#fbdada' : '#f7c9c9'
  if (i === current.value.hl) return isNext ? '#cfe0ff' : '#a9c6ff'
  return isNext ? '#f4f6fa' : '#ffffff'
}
function strokeOf(i) {
  if (i === current.value.danger) return '#e05252'
  if (i === current.value.hl) return '#3b6ef6'
  return '#c8d3e6'
}
function textOf(i) {
  if (i === current.value.danger) return '#a32c2c'
  if (i === current.value.hl) return '#1a47b8'
  return '#1f2733'
}

function addOp(type) {
  const v = Number(newValue.value)
  if (isNaN(v) && type !== 'delete') return
  const prevTotal = player.total.value
  if (type === 'delete') ops.value.push({ type: 'delete', pos: pos.value })
  else if (type === 'insert') ops.value.push({ type: 'insert', value: v, pos: pos.value })
  else ops.value.push({ type, value: v })
  newValue.value = Number(newValue.value) + 1
  // 从旧末尾播新过程：不加这句，按钮点了画面停在第一帧，像坏了一样
  player.playAppended(prevTotal)
}
function resetOps() {
  // 回到「当前初始链表」的生成过程，而不是某条写死的演示序列
  ops.value = buildOps(initVals.value)
  player.reset()
}

function applyInit() {
  const raw = String(initInput.value || '')
  const vals = raw
    .split(/[,，、\s]+/)
    .map(s => s.trim())
    .filter(Boolean)
    .map(Number)
  if (!vals.length || vals.some(isNaN)) {
    ElMessage.warning('初始链表要是数字，用逗号或空格分隔，例如 7,12,25')
    return
  }
  if (vals.length > MAX_NODES) {
    ElMessage.warning(`结点最多 ${MAX_NODES} 个，再多画布就摆不下了`)
    return
  }
  initVals.value = vals
  ops.value = buildOps(vals)
  player.reset()
  // 自动播一遍生成过程：结点一个一个接上，比直接看到成品更能建立直觉
  player.play()
}
</script>

<style scoped>
.vis-svg { display: block; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }

/* 自定义初始链表工具行：跟画布放在一起，语义上属于「配置这条链」 */
.init-bar {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 12px; flex-wrap: wrap;
}
.init-label { font-size: 12px; color: var(--text-2); white-space: nowrap; }
.init-input { width: 260px; }
</style>
