<template>
  <VisFrame title="循环队列 · 入队与出队（FIFO）" desc="队尾插入、队头删除；取模运算把数组首尾相连，解决假溢出" :player="player" :status-text="statusText" back-to="/knowledge/3">
    <template #extra>
      <el-button size="small" @click="addOp('en')">enqueue {{ enqLabel }}</el-button>
      <el-button size="small" type="danger" plain @click="addOp('de')">dequeue</el-button>
      <el-button size="small" plain @click="rebuild">重置</el-button>
    </template>

    <!-- 自定义初始队列：入队序列不再写死，学生想研究哪条队列就生成哪条 -->
    <div class="init-bar">
      <span class="init-label">初始队列（入队顺序）</span>
      <el-input v-model="initInput" size="small" class="init-input"
        placeholder="如 A,B,C（逗号或空格分隔，最多 5 个）"
        @keyup.enter="applyInit" />
      <el-button size="small" type="primary" plain @click="applyInit">生成队列</el-button>
    </div>

    <div class="q-wrap">
      <svg width="300" height="300" class="q-ring">
        <circle cx="150" cy="150" r="104" fill="none" stroke="#e3e8f0" stroke-width="2" />
        <g v-for="(slot, i) in ring" :key="i">
          <g :transform="`translate(${slot.x}, ${slot.y})`">
            <circle
              r="30" :fill="fillOf(i)" :stroke="strokeOf(i)" stroke-width="2"
            />
            <text y="5" text-anchor="middle" font-size="15" font-weight="600" :fill="textOf(i)">
              {{ queue[i] !== undefined && queue[i] !== null ? queue[i] : '' }}
            </text>
            <text y="-38" text-anchor="middle" font-size="11" fill="#8b95a3">[{{ i }}]</text>
          </g>
        </g>
        <!-- front 指针 -->
        <g :transform="`translate(${pointerPos('front').x}, ${pointerPos('front').y})`">
          <circle r="8" fill="#3b6ef6" />
          <text y="-14" text-anchor="middle" font-size="12" fill="#3b6ef6" font-weight="700">front</text>
        </g>
        <!-- rear 指针 -->
        <g :transform="`translate(${pointerPos('rear').x}, ${pointerPos('rear').y})`">
          <circle r="8" fill="#22a06b" />
          <text y="24" text-anchor="middle" font-size="12" fill="#22a06b" font-weight="700">rear</text>
        </g>
        <text x="150" y="150" text-anchor="middle" font-size="12" fill="#8b95a3">循环队列</text>
        <text x="150" y="168" text-anchor="middle" font-size="12" fill="#8b95a3">MaxSize={{ maxSize }}</text>
      </svg>

      <div class="q-panel">
        <div class="info-row"><span>队头指针 front</span><b style="color:var(--brand)">{{ front }}</b></div>
        <div class="info-row"><span>队尾指针 rear</span><b style="color:var(--success)">{{ rear }}</b></div>
        <div class="info-row"><span>队列长度</span><b>{{ length }}</b></div>
        <div class="info-row">
          <span>队空判定 (rear==front)</span>
          <el-tag size="small" :type="isEmpty ? 'danger' : 'info'">{{ isEmpty ? '空' : '非空' }}</el-tag>
        </div>
        <div class="info-row">
          <span>队满判定 (rear+1)%M==front</span>
          <el-tag size="small" :type="isFull ? 'danger' : 'info'">{{ isFull ? '满' : '未满' }}</el-tag>
        </div>
        <el-divider />
        <div class="formula">
          <div class="small muted">元素个数公式</div>
          <code>(rear - front + MaxSize) % MaxSize = ({{ rear }} - {{ front }} + {{ maxSize }}) % {{ maxSize }} = <b>{{ length }}</b></code>
        </div>
        <div class="queue-list">
          <div class="small muted" style="margin-bottom:6px">队列内容（队头 → 队尾）</div>
          <div class="chip-row">
            <el-tag v-for="(v, i) in orderedItems" :key="i" size="small" :type="i === 0 ? 'primary' : 'success'">{{ v }}</el-tag>
            <span v-if="!orderedItems.length" class="small muted">空队列</span>
          </div>
        </div>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> front 队头</span>
      <span><i class="dot" style="background:#22a06b"></i> rear 队尾（下一个入队位置）</span>
      <span><i class="dot" style="background:#f7c9c9"></i> 刚出队（逻辑删除）</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const maxSize = 6
const nextVal = ref(4) // A,B,C 已被初始队列占用，enqueue 按钮从 D 继续
const enqLabel = computed(() => String.fromCharCode(64 + nextVal.value)) // 按钮显示实际要入队的字母

// 初始队列由学生自己定 —— 以前的演示序列（en ABC、de、en DEFG…）是写死的，
// 想换条队列研究只能干瞪眼。现在：输入入队顺序 -> 生成 -> 入队出队都基于它。
// 循环队列牺牲一个单元区分空满，实际最多存 maxSize-1 个。
const MAX_INIT = maxSize - 1
const initInput = ref('A,B,C')
const initVals = ref(['A', 'B', 'C'])

/** 把「初始队列」翻译成操作序列：从空队列逐个 enqueue（队头 → 队尾） */
function buildOps(vals) {
  return vals.map(v => ({ op: 'en', v }))
}

const ops = ref(buildOps(initVals.value))

const steps = computed(() => {
  const out = []
  let q = new Array(maxSize).fill(null)
  let front = 0
  let rear = 0
  out.push({ q: [...q], front, rear, hl: -1, desc: '初始空队列：front = rear = 0' })
  for (const o of ops.value) {
    if (o.op === 'en') {
      const nextRear = (rear + 1) % maxSize
      if (nextRear === front) {
        out.push({ q: [...q], front, rear, hl: -1, desc: '队满：入队失败（牺牲一个单元以区分空满）' })
        continue
      }
      q[rear] = o.v
      const pos = rear
      rear = nextRear
      out.push({ q: [...q], front, rear, hl: pos, desc: `enqueue(${o.v})：放入 rear 位置 [${pos}]，rear = (${pos}+1)%${maxSize} = ${rear}` })
    } else {
      if (front === rear) {
        out.push({ q: [...q], front, rear, hl: -1, desc: '队空：出队失败（下溢）' })
        continue
      }
      const v = q[front]
      const pos = front
      const q2 = [...q]
      q2[pos] = null
      front = (front + 1) % maxSize
      // 快照必须拷贝：下一行 q = q2 会把同一个数组继续当当前队列用，
      // 若这里存引用，后续入队会写进历史步骤，播放时看到"尚未入队"的元素
      out.push({ q: [...q2], front, rear, hl: pos, del: true, desc: `dequeue()：取出队头元素 ${v}，front = (${pos}+1)%${maxSize} = ${front}` })
      q = q2
    }
  }
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || { q: [], front: 0, rear: 0, hl: -1, desc: '' })
const queue = computed(() => cur.value.q)
const front = computed(() => cur.value.front)
const rear = computed(() => cur.value.rear)
const statusText = computed(() => cur.value.desc)

const length = computed(() => (rear.value - front.value + maxSize) % maxSize)
const isEmpty = computed(() => front.value === rear.value)
const isFull = computed(() => (rear.value + 1) % maxSize === front.value)

const orderedItems = computed(() => {
  const res = []
  for (let i = 0; i < length.value; i++) {
    const v = queue.value[(front.value + i) % maxSize]
    if (v !== null && v !== undefined) res.push(v)
  }
  return res
})

const ring = computed(() =>
  Array.from({ length: maxSize }, (_, i) => {
    const angle = (Math.PI * 2 * i) / maxSize - Math.PI / 2
    return { x: 150 + 104 * Math.cos(angle), y: 150 + 104 * Math.sin(angle) }
  })
)

function pointerPos(type) {
  const idx = type === 'front' ? front.value : rear.value
  // 指针画在槽位外侧
  const angle = (Math.PI * 2 * idx) / maxSize - Math.PI / 2
  return { x: 150 + 104 * Math.cos(angle), y: 150 + 104 * Math.sin(angle) - 36 }
}

function fillOf(i) {
  if (i === cur.value.hl) return cur.value.del ? '#f7c9c9' : '#dcf3e7'
  if (i === front.value && !isEmpty.value) return '#eef3ff'
  return '#fff'
}
function strokeOf(i) {
  if (i === cur.value.hl) return cur.value.del ? '#e05252' : '#22a06b'
  if (i === front.value && !isEmpty.value) return '#3b6ef6'
  return '#c8d3e6'
}
function textOf(i) {
  if (i === cur.value.hl) return cur.value.del ? '#a32c2c' : '#176b48'
  return '#1f2733'
}

function addOp(type) {
  const prevTotal = player.total.value
  if (type === 'en') {
    ops.value.push({ op: 'en', v: String.fromCharCode(64 + nextVal.value) })
    nextVal.value = nextVal.value + 1
    if (nextVal.value > 26) nextVal.value = 1
  } else {
    ops.value.push({ op: 'de' })
  }
  // 从旧末尾播新过程，不然点了按钮画面不动，像坏了
  player.playAppended(prevTotal)
}
function rebuild() {
  // 回到「当前初始队列」的生成过程，而不是某条写死的演示序列
  nextVal.value = (initVals.value.length % 26) + 1
  ops.value = buildOps(initVals.value)
  player.reset()
}

function applyInit() {
  const raw = String(initInput.value || '')
  const vals = raw
    .split(/[,，、\s]+/)
    .map(s => s.trim())
    .filter(Boolean)
  if (!vals.length) {
    ElMessage.warning('初始队列要是元素，用逗号或空格分隔，例如 A,B,C')
    return
  }
  if (vals.length > MAX_INIT) {
    ElMessage.warning(`循环队列牺牲一个单元区分空满，初始队列最多 ${MAX_INIT} 个元素`)
    return
  }
  initVals.value = vals
  // enqueue 按钮的字母接在初始队列后面（A,B,C 用掉后从 D 继续）
  nextVal.value = (vals.length % 26) + 1
  ops.value = buildOps(vals)
  player.reset()
  // 自动播一遍入队过程：元素一个一个从队尾接上
  player.play()
}
</script>

<style scoped>
.q-wrap { display: flex; gap: 24px; align-items: flex-start; flex-wrap: wrap; }

/* 自定义初始队列工具行：跟画布放在一起，语义上属于「配置这条队列」 */
.init-bar {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 12px; flex-wrap: wrap;
}
.init-label { font-size: 12px; color: var(--text-2); white-space: nowrap; }
.init-input { width: 240px; }
.q-ring { flex-shrink: 0; }
.q-panel { flex: 1; min-width: 280px; }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.formula { margin: 10px 0; }
.formula code { background: #f2f4f8; padding: 8px 10px; border-radius: 6px; display: block; font-size: 12px; line-height: 1.7; }
.chip-row { display: flex; gap: 6px; flex-wrap: wrap; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
