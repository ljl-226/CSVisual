<template>
  <VisFrame title="双向链表与循环链表" desc="插入遵循「先接新结点、后改前驱」；删除先改前驱/后继指针再摘除；循环表尾结点必须回指头结点" :player="player" :status-text="statusText" back-to="/knowledge/35">
    <template #extra>
      <el-select v-model="mode" size="small" style="width:118px">
        <el-option value="double" label="双向链表" /><el-option value="csingle" label="循环单链表" /><el-option value="cdouble" label="循环双链表" />
      </el-select>
      <el-input v-model="newValue" size="small" style="width:70px" placeholder="值" />
      <el-button size="small" @click="addOp('head')">头插</el-button>
      <el-button size="small" @click="addOp('tail')">尾插</el-button>
      <el-input-number v-model="pos" :min="1" :max="20" size="small" style="width:86px" />
      <el-button size="small" @click="addOp('insert')">按位插</el-button>
      <el-button size="small" type="danger" plain @click="addOp('delete')">删除</el-button>
      <el-button size="small" plain @click="resetOps">重置</el-button>
    </template>

    <!-- 自定义初始链表：结点序列不再写死，学生想研究哪条链就生成哪条 -->
    <div class="init-bar">
      <span class="init-label">初始链表</span>
      <el-input v-model="initInput" size="small" class="init-input"
        placeholder="如 12,25,37（逗号或空格分隔，最多 10 个）"
        @keyup.enter="applyInit" />
      <el-button size="small" type="primary" plain @click="applyInit">生成链表</el-button>
    </div>

    <div class="dl-wrap">
      <svg :width="svgW" height="208" class="dl-svg">
        <defs>
          <marker id="dl-g" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 z" fill="#8b95a3" /></marker>
          <marker id="dl-b" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 z" fill="#3b6ef6" /></marker>
        </defs>
        <!-- 头指针 head -->
        <rect x="10" y="70" width="56" height="34" rx="6" fill="#eef3ff" stroke="#3b6ef6" stroke-width="1.6" />
        <text x="38" y="92" text-anchor="middle" font-size="13" fill="#3b6ef6">head</text>
        <line v-if="nodes.length" x1="66" y1="87" :x2="nx(0) - 9" y2="87" :stroke="headFlash ? '#e8a13a' : '#3b6ef6'" :stroke-width="headFlash ? 2.6 : 1.6" marker-end="url(#dl-b)" />
        <text v-else x="76" y="92" font-size="12" fill="#8b95a3">→ {{ cyc ? 'head(空表)' : 'NULL' }}</text>
        <!-- prior 域指针（下方弧：i → i-1）与循环表头结点的 prior → 尾结点 -->
        <template v-if="hasPrior">
          <path v-for="i in priorArcs" :key="'p' + i" :d="priorPath(i)" fill="none" :stroke="hc(i, i - 1, 'prior')" :stroke-width="hw(i, i - 1, 'prior')" :marker-end="hm(i, i - 1, 'prior')" />
          <path v-if="cyc && nodes.length > 1" :d="wrapPriorPath()" fill="none" :stroke="hc(0, nodes.length - 1, 'prior')" :stroke-width="hw(0, nodes.length - 1, 'prior')" :marker-end="hm(0, nodes.length - 1, 'prior')" />
        </template>
        <path v-if="hotArc && hotArc.kind === 'prior'" :d="hotArc.path" fill="none" stroke="#e05252" stroke-width="2.4" stroke-dasharray="5 3" marker-end="url(#dl-g)" />
        <!-- 结点：prior | data | next -->
        <g v-for="(n, i) in nodes" :key="n.id" :transform="`translate(${nx(i)}, 64)`">
          <text :x="W / 2" y="-8" text-anchor="middle" font-size="11" fill="#8b95a3">结点{{ i + 1 }}</text>
          <rect v-if="hasPrior" width="26" height="46" rx="4" :fill="cellFill(i, 0)" :stroke="strokeOf(i)" stroke-width="1.6" :stroke-dasharray="dashOf(i)" />
          <rect :x="pw" :width="dw" height="46" rx="4" :fill="cellFill(i, 1)" :stroke="strokeOf(i)" stroke-width="1.6" :stroke-dasharray="dashOf(i)" />
          <rect :x="pw + dw" :width="nw" height="46" rx="4" :fill="cellFill(i, 2)" :stroke="strokeOf(i)" stroke-width="1.6" :stroke-dasharray="dashOf(i)" />
          <line v-if="hasPrior" x1="26" y1="0" x2="26" y2="46" :stroke="strokeOf(i)" /><line :x1="pw + dw" y1="0" :x2="pw + dw" y2="46" :stroke="strokeOf(i)" />
          <circle v-if="hasPrior && (i > 0 || cyc)" cx="13" cy="23" r="3.6" :fill="strokeOf(i)" opacity="0.8" />
          <circle v-if="i < nodes.length - 1 || cyc" :cx="pw + dw + nw / 2" cy="23" r="3.6" :fill="strokeOf(i)" opacity="0.8" />
          <text :x="pw + dw / 2" y="30" text-anchor="middle" font-size="14" font-weight="600" :fill="textOf(i)">{{ n.v }}</text>
        </g>
        <!-- next 域指针（直线 i → i+1）与循环表尾结点 → 头结点 -->
        <line v-for="i in nextLines" :key="'n' + i" :x1="nx(i) + W" y1="87" :x2="nx(i + 1) - 8" y2="87" :stroke="hc(i, i + 1, 'next')" :stroke-width="hw(i, i + 1, 'next')" :marker-end="hm(i, i + 1, 'next')" />
        <path v-if="cyc && nodes.length > 1" :d="wrapNextPath()" fill="none" :stroke="hc(nodes.length - 1, 0, 'next')" :stroke-width="hw(nodes.length - 1, 0, 'next')" :marker-end="hm(nodes.length - 1, 0, 'next')" />
        <path v-if="hotArc && hotArc.kind === 'next'" :d="hotArc.path" fill="none" stroke="#3b6ef6" stroke-width="2.4" marker-end="url(#dl-b)" />
      </svg>

      <div class="dl-panel">
        <div class="info-row"><span>链表形态</span><b>{{ modeName }}</b></div>
        <div class="info-row"><span>表长 / 序列</span><b>{{ nodes.length }} · {{ nodes.map(n => n.v).join(' ⇄ ') || '空' }}</b></div>
        <el-divider />
        <div class="panel-title">本次指针改接顺序</div>
        <ol class="op-log"><li v-for="(s, i) in cur.log" :key="i">{{ s }}</li><li v-if="!cur.log.length" class="small muted">（本步未改指针）</li></ol>
        <div class="tip small muted">结点含 prior/data/next 三域：插入改 4 个指针、删除改 2 个，且必须<b>先接新链再断旧链</b>。循环表判空为 head-&gt;next==head；只设尾指针时头尾查找均 O(1)。</div>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#22a06b"></i> 新插入结点</span><span><i class="dot" style="background:#e05252"></i> 待删除结点</span>
      <span><i class="dot" style="background:#3b6ef6"></i> 本步改接的指针</span><span><i class="dot" style="background:#e8a13a"></i> head 变化</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const X0 = 96, NY = 64
const MODE_NAME = { double: '双向链表', csingle: '循环单链表', cdouble: '循环双链表' }
const mode = ref('double')
const newValue = ref(38)
const pos = ref(3)

// 初始链表由学生自己定 —— 以前的演示序列（尾插 12/25/37、头插 6…）是写死的，
// 想换条链研究只能干瞪眼。现在：输入一串数 -> 生成 -> 所有插入删除都基于它。
const MAX_NODES = 10
const initInput = ref('12,25,37')
const initVals = ref([12, 25, 37])

/** 把「初始链表」翻译成操作序列：逐个尾插 */
function buildOps(vals) {
  return vals.map(v => ({ type: 'tail', value: v }))
}

const ops = ref(buildOps(initVals.value))

const steps = computed(() => {
  const m = mode.value
  const cyc = m !== 'double'                 // 是否循环表
  const hp = m !== 'csingle'                 // 是否有 prior 域
  let nodes = [], id = 0, log = []
  const out = []
  // 快照 = 结点副本 + 高亮结点(hl/danger) + 本步改接的指针(hot) + 已完成赋值日志
  function snap(desc, extra = {}) {
    out.push({ nodes: nodes.map(n => ({ ...n })), hl: -1, danger: -1, hot: null, headFlash: false, log: [...log], desc, ...extra })
  }
  snap(`初始化空表（${MODE_NAME[m]}）：head 指向 ${cyc ? '自身' : 'NULL'}`, {})
  for (const op of ops.value) {
    const n = nodes.length
    if (op.type === 'delete') {
      const p = Math.min(Math.max(1, op.pos), n), k = p - 1
      if (!n || k >= n) { snap(n ? `第 ${p} 位超出表长 ${n}，删除失败` : '表为空，删除失败', {}); continue }
      if (n === 1) { log = ['head = NULL']; nodes = []; snap('只有一个结点：摘除后链表置空（循环表需先断开自环）', {}); continue }
      const pre = cyc ? (k - 1 + n) % n : k - 1
      const suc = cyc ? (k + 1) % n : k + 1
      const hasSuc = suc < n
      log = []
      if (pre >= 0) {
        log.push('p->prior->next = p->next')
        snap(`删除第 ${p} 位（${nodes[k].v}）：① 前驱 ${nodes[pre].v} 的 next 越过 p 指向后继`, { danger: k, hot: hasSuc ? { kind: 'next', from: pre, to: suc } : null })
      } else { log.push('head = p->next'); snap(`删除第 1 位（${nodes[k].v}）：① 无前驱，head 改指其后继 ${nodes[suc].v}`, { danger: k, headFlash: true }) }
      if (hp && hasSuc && pre >= 0) {
        log.push('p->next->prior = p->prior')
        snap(`② 后继 ${nodes[suc].v} 的 prior 改指前驱 ${nodes[pre].v}`, { danger: k, hot: { kind: 'prior', from: suc, to: pre } })
      } else if (hp && hasSuc) { log.push('p->next->prior = NULL'); snap(`② 新首元 ${nodes[suc].v} 的 prior 置为 NULL`, { danger: k }) }
      const rm = nodes[k].v
      nodes = nodes.filter((_, i) => i !== k)
      if (cyc && k === 0 && nodes.length) {
        log.push('tail->next = 新首元')
        snap(`③ 首元被删：尾结点 next 改指新首元 ${nodes[0].v}，再摘除 ${rm}`, { hot: { kind: 'next', from: nodes.length - 1, to: 0 } })
      } else { log.push('free(p)'); snap(`摘除结点 ${rm} 并释放空间，表长减 1`, {}) }
      continue
    }
    // 插入：统一为「在前驱 pre 之后插入」，pre = -1 表示插到最前
    let pre = op.type === 'head' ? -1 : (op.type === 'tail' ? n - 1 : Math.min(Math.max(1, op.pos), n + 1) - 2)
    if (cyc && n > 0 && pre === -1) pre = n - 1   // 循环表插到首元之前 → 前驱是尾结点
    const insertAt = op.type === 'head' ? 0 : pre + 1
    const s = { v: op.value, id: id++ }
    if (n === 0) {
      nodes = [s]; log = [cyc ? 's->next = s; s->prior = s' : 's->next = s->prior = NULL']
      snap(`空表插入 ${op.value}：head 指向新结点 s${cyc ? '，其指针指回自身形成环' : '，prior/next 均为 NULL'}`, { hl: 0 }); continue
    }
    const oldSuc = pre === -1 ? 0 : (cyc ? (pre + 1) % n : pre + 1)
    const succIdx = oldSuc < n ? (oldSuc >= insertAt ? oldSuc + 1 : oldSuc) : -1
    const preIdx = pre === -1 ? -1 : (pre >= insertAt ? pre + 1 : pre)
    nodes = [...nodes.slice(0, insertAt), s, ...nodes.slice(insertAt)]
    const sIdx = insertAt, hasSuc = succIdx >= 0 && succIdx < nodes.length
    log = ['s->next = p->next']
    snap(`插入 ${op.value}：① 新结点 s 的 next 指向 p 的原后继${hasSuc ? ` ${nodes[succIdx].v}` : ' NULL'}（先接新链，避免丢链）`, { hl: sIdx, hot: hasSuc ? { kind: 'next', from: sIdx, to: succIdx } : null })
    if (hp && hasSuc) { log.push('p->next->prior = s'); snap(`② 后继 ${nodes[succIdx].v} 的 prior 指回新结点 s`, { hl: sIdx, hot: { kind: 'prior', from: succIdx, to: sIdx } }) }
    if (hp) {
      log.push(preIdx >= 0 ? 's->prior = p' : 's->prior = NULL')
      snap(`③ 新结点 s 的 prior 指向前驱${preIdx >= 0 ? ` ${nodes[preIdx].v}` : ' NULL'}`, { hl: sIdx, hot: preIdx >= 0 ? { kind: 'prior', from: sIdx, to: preIdx } : null })
    }
    if (preIdx >= 0) {
      log.push('p->next = s')
      snap(`④ 前驱 ${nodes[preIdx].v} 的 next 改指 s，插入完成（共 ${log.length} 次指针赋值）`, { hl: sIdx, hot: { kind: 'next', from: preIdx, to: sIdx } })
    } else { log.push('head = s'); snap('④ 无前驱，head 指向新结点 s，插入完成', { hl: sIdx, headFlash: true }) }
  }
  return out
})
const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const nodes = computed(() => cur.value.nodes || [])
const cyc = computed(() => mode.value !== 'double')
const hasPrior = computed(() => mode.value !== 'csingle')
const modeName = computed(() => MODE_NAME[mode.value])
const pw = computed(() => (hasPrior.value ? 26 : 0))
const dw = computed(() => (hasPrior.value ? 40 : 44))
const nw = computed(() => (hasPrior.value ? 26 : 28))
const W = computed(() => pw.value + dw.value + nw.value)
const step = computed(() => W.value + 32)
const svgW = computed(() => Math.max(660, X0 + nodes.value.length * step.value + 60))
const headFlash = computed(() => !!cur.value.headFlash)
const priorArcs = computed(() => (hasPrior.value ? nodes.value.map((_, i) => i).slice(1) : []))
const nextLines = computed(() => nodes.value.map((_, i) => i).slice(0, -1))
function nx(i) { return X0 + i * step.value }
function hotOf(f, t, k) { const h = cur.value.hot; return !!(h && h.kind === k && h.from === f && h.to === t) }
function hc(f, t, k) { return hotOf(f, t, k) ? '#3b6ef6' : '#8b95a3' }
function hw(f, t, k) { return hotOf(f, t, k) ? 2.6 : 1.5 }
function hm(f, t, k) { return hotOf(f, t, k) ? 'url(#dl-b)' : 'url(#dl-g)' }
// 跨结点改接（删除时的旁路弧）：next 走上方，prior 走下方
const hotArc = computed(() => {
  const h = cur.value.hot, n = nodes.value.length
  if (!h || n < 2 || h.from < 0 || h.to < 0 || h.from >= n || h.to >= n || h.from === h.to) return null
  if (h.kind === 'next' && h.to !== h.from + 1 && !(h.from === n - 1 && h.to === 0)) {
    return { kind: 'next', path: `M ${nx(h.from) + pw.value + dw.value + nw.value / 2} ${NY} C ${nx(h.from)} ${NY - 46}, ${nx(h.to)} ${NY - 46}, ${nx(h.to) + W.value / 2} ${NY - 1}` }
  }
  if (h.kind === 'prior' && h.to !== h.from - 1 && !(h.from === 0 && h.to === n - 1)) {
    return { kind: 'prior', path: `M ${nx(h.from) + 13} ${NY + 46} C ${nx(h.from) + 13} ${NY + 120}, ${nx(h.to) + 13} ${NY + 120}, ${nx(h.to) + 13} ${NY + 46}` }
  }
  return null
})
function priorPath(i) { const a = nx(i) + 13, b = nx(i - 1) + 13, y = NY + 46; return `M ${a} ${y} C ${a} ${y + 54}, ${b} ${y + 54}, ${b} ${y}` }
function wrapPriorPath() { const n = nodes.value.length, y = NY + 46; return `M ${nx(0) + 13} ${y} C ${nx(0) + 13} ${y + 108}, ${nx(n - 1) + 13} ${y + 108}, ${nx(n - 1) + 13} ${y}` }
function wrapNextPath() { const n = nodes.value.length; const sx = nx(n - 1) + pw.value + dw.value + nw.value / 2, ex = nx(0) + W.value / 2; return `M ${sx} ${NY} C ${sx} ${NY - 48}, ${ex} ${NY - 48}, ${ex} ${NY - 1}` }

function cellFill(i, part) {
  if (i === cur.value.danger) return part === 1 ? '#fbdada' : '#fdecec'
  if (i === cur.value.hl) return part === 1 ? '#bfe9d3' : '#dcf3e7'
  return part === 1 ? '#ffffff' : '#f4f6fa'
}
function strokeOf(i) { return i === cur.value.danger ? '#e05252' : (i === cur.value.hl ? '#22a06b' : '#c8d3e6') }
function dashOf(i) { return i === cur.value.danger ? '5 3' : '0' }
function textOf(i) { return i === cur.value.danger ? '#a32c2c' : (i === cur.value.hl ? '#176b48' : '#1f2733') }

function addOp(type) {
  const v = Number(newValue.value)
  if (type !== 'delete' && isNaN(v)) return
  const prevTotal = player.total.value
  if (type === 'delete') ops.value.push({ type: 'delete', pos: pos.value })
  else if (type === 'insert') ops.value.push({ type: 'insert', value: v, pos: pos.value })
  else ops.value.push({ type, value: v })
  if (!isNaN(v)) newValue.value = v + 1
  // 从旧末尾播新过程，不然点了按钮画面不动，像坏了
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
    ElMessage.warning('初始链表要是数字，用逗号或空格分隔，例如 12,25,37')
    return
  }
  if (vals.length > MAX_NODES) {
    ElMessage.warning(`结点最多 ${MAX_NODES} 个，再多画布就摆不下了`)
    return
  }
  initVals.value = vals
  // 值输入框接在初始链表后面（12,25,37 用掉后从 38 继续）
  newValue.value = vals[vals.length - 1] + 1
  ops.value = buildOps(vals)
  player.reset()
  // 自动播一遍生成过程：结点一个一个接上
  player.play()
}
</script>

<style scoped>
.dl-wrap { display: flex; gap: 24px; align-items: flex-start; flex-wrap: wrap; }

/* 自定义初始链表工具行：跟画布放在一起，语义上属于「配置这条链」 */
.init-bar {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 12px; flex-wrap: wrap;
}
.init-label { font-size: 12px; color: var(--text-2); white-space: nowrap; }
.init-input { width: 260px; }
.dl-svg { flex-shrink: 0; background: #fbfcff; border-radius: 8px; }
.dl-panel { flex: 1; min-width: 250px; }
.info-row { display: flex; justify-content: space-between; gap: 10px; padding: 4px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.panel-title { font-size: 13px; font-weight: 600; margin-bottom: 6px; color: var(--text-2); }
.op-log { margin: 0; padding-left: 20px; font-size: 12px; line-height: 1.9; color: var(--text-2); }
.tip { margin-top: 10px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
