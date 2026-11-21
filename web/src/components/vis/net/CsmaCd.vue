<template>
  <VisFrame
    title="CSMA/CD 与以太网"
    desc="先听后发、边发边听、冲突立停、二进制指数退避；争用期 2τ=51.2μs 决定了最短帧长 64 字节"
    :player="player" :status-text="statusText" back-to="/knowledge/43"
  >
    <template #extra>
      <el-input v-model="bytesInput" size="small" style="width:110px" placeholder="帧长字节" />
      <el-button size="small" @click="applyBytes">应用</el-button>
      <el-button size="small" plain @click="resetBytes">重置</el-button>
    </template>

    <div class="cd-wrap">
      <svg :width="svgW" height="300" class="cd-svg">
        <!-- 共享总线 -->
        <line :x1="70" :y1="60" :x2="svgW - 16" :y2="60" stroke="#c8d3e6" stroke-width="4" />
        <text :x="svgW - 16" y="48" text-anchor="end" font-size="11" fill="#8b95a3">总线（多台主机共享的广播信道，10BASE-T）</text>

        <!-- 站点行 -->
        <text x="60" :y="rowA + 17" text-anchor="end" font-size="13" font-weight="600" fill="#3b6ef6">站点 A</text>
        <text x="60" :y="rowB + 17" text-anchor="end" font-size="13" font-weight="600" fill="#22a06b">站点 B</text>
        <line x1="70" :y1="rowA + 26" :x2="svgW - 16" :y2="rowA + 26" stroke="#f0f2f6" stroke-width="1" />
        <line x1="70" :y1="rowB + 26" :x2="svgW - 16" :y2="rowB + 26" stroke="#f0f2f6" stroke-width="1" />

        <!-- 信号占用条（标签按已占用区间自动错行，避免「B 发送」和「干扰信号」叠在一起） -->
        <g v-for="(it, i) in cur.items" :key="i">
          <rect
            :x="x(it.s)" :y="it.side === 'A' ? rowA : rowB"
            :width="Math.max(0, x(Math.min(it.e, cur.t)) - x(it.s))" height="24" rx="3"
            :fill="fillOf(it)" :stroke="strokeOf(it)" stroke-width="1.2" :stroke-dasharray="it.kind === 'jam' ? '4 3' : ''"
          />
          <text v-if="it.e <= cur.t" :x="x(it.s) + 4" :y="itemLabelY[i]" font-size="10" :fill="strokeOf(it)">{{ it.label }}</text>
        </g>

        <!-- 关键事件标记（多个事件时间挨得很近，按行错开） -->
        <g v-for="(mk, i) in markerList" :key="'k' + i">
          <line :x1="mk.cx" y1="64" :x2="mk.cx" :y2="mk.cy - 6" stroke="#dfe5ef" stroke-width="1" stroke-dasharray="3 3" />
          <circle :cx="mk.cx" :cy="mk.cy" r="4" :fill="mk.color" />
          <text :x="mk.cx" :y="mk.cy - 8" text-anchor="middle" font-size="10" :fill="mk.color" font-weight="600">{{ mk.text }}</text>
        </g>

        <!-- 时间轴 -->
        <line x1="70" :y1="264" :x2="svgW - 16" :y2="264" stroke="#c8d3e6" stroke-width="1.5" />
        <g v-for="(tk, i) in ticks" :key="'t' + i">
          <line :x1="x(tk.t)" y1="264" :x2="x(tk.t)" y2="270" stroke="#8b95a3" stroke-width="1.2" />
          <text :x="x(tk.t)" y="286" text-anchor="middle" font-size="11" fill="#8b95a3">{{ tk.label }}</text>
        </g>
        <!-- 当前时刻 -->
        <line :x1="x(cur.t)" y1="70" :x2="x(cur.t)" y2="264" stroke="#e05252" stroke-width="1.4" stroke-dasharray="5 4" />
        <text :x="tLabel.x" y="252" font-size="11" fill="#e05252" :text-anchor="tLabel.anchor">t = {{ cur.t.toFixed(1) }}μs</text>
      </svg>

      <div class="cd-panel">
        <div class="info-row"><span>当前时刻 t</span><b>{{ cur.t.toFixed(1) }} μs</b></div>
        <div class="info-row"><span>站点 A 状态</span><b style="color:var(--brand)">{{ cur.aState }}</b></div>
        <div class="info-row"><span>站点 B 状态</span><b style="color:var(--success)">{{ cur.bState }}</b></div>
        <div class="info-row"><span>单程时延 τ / 争用期 2τ</span><b>{{ TAU }}μs / {{ SLOT }}μs</b></div>
        <div class="info-row"><span>帧长 / 发送时间 T</span><b>{{ bytes }}B / {{ frameT.toFixed(1) }}μs</b></div>
        <div class="info-row"><span>A 退避 k / r / 推迟</span><b>k={{ cur.ak }}, r={{ cur.ar }}, {{ (cur.ar * SLOT).toFixed(1) }}μs</b></div>
        <div class="info-row"><span>B 退避 k / r / 推迟</span><b>k={{ cur.bk }}, r={{ cur.br }}, {{ (cur.br * SLOT).toFixed(1) }}μs</b></div>
        <div class="info-row"><span>碰撞次数</span><b style="color:var(--danger)">{{ cur.colls }}</b></div>
        <el-divider />
        <div class="panel-title">教材要点</div>
        <ul class="points">
          <li>最短帧长：10Mb/s × 51.2μs（争用期）= 512 bit = <b>64 字节</b>，帧长不足 64B 会被当作冲突碎片丢弃</li>
          <li>强化碰撞：检测到冲突后发 32（或 48）bit 的人为干扰信号，确保全网各站都能感知</li>
          <li>帧最小间隔 9.6μs（96bit）用于清理接收缓存；以太网不重排</li>
          <li>帧发送时间 T = 帧长 × 8 ÷ 10Mb/s；本例 T = {{ frameT.toFixed(1) }}μs{{ frameT >= SLOT ? ' ≥ 争用期，可正常检测到冲突' : ' &lt; 争用期，冲突将无法被检测到' }}</li>
        </ul>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> 站点 A 占用信道</span>
      <span><i class="dot" style="background:#22a06b"></i> 站点 B 占用信道</span>
      <span><i class="dot" style="background:#e05252"></i> 强化干扰信号 / 碰撞检测</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const TAU = 25.6      // 单程端到端传播时延 τ（教材示例值）
const SLOT = 51.2     // 争用期 2τ：以太网的基本退避时间，也是能否检测到冲突的判断依据
const DELTA = 4       // δ：B 比 A 晚一点点发送
const JAMT = 3.2      // 32bit 强化干扰信号在 10Mb/s 下的发送时间
const IFG = 9.6       // 帧间最小间隔 96bit
const rowA = 130      // 站点 A 行 y 坐标
const rowB = 190      // 站点 B 行 y 坐标

const BYTES_DEFAULT = 64
const bytesInput = ref(String(BYTES_DEFAULT))
const bytes = ref(BYTES_DEFAULT)
const frameT = computed(() => bytes.value * 8 / 10) // 10Mb/s：1 bit = 0.1μs

const steps = computed(() => {
  const T = frameT.value
  const canDetect = T >= SLOT // 只有发送时间 ≥ 争用期才能保证冲突被检测到
  const all = [
    { id: 'a1', side: 'A', s: 0, e: canDetect ? 2 * TAU - DELTA : T, kind: 'data', label: 'A 发送（失败）' },
    { id: 'b1', side: 'B', s: TAU - DELTA, e: TAU, kind: 'data', label: 'B 发送（失败）' },
    { id: 'bj', side: 'B', s: TAU, e: TAU + JAMT, kind: 'jam', label: '干扰信号' },
    canDetect ? { id: 'aj', side: 'A', s: 2 * TAU - DELTA, e: 2 * TAU - DELTA + JAMT, kind: 'jam', label: '干扰信号' } : null,
    { id: 'a2', side: 'A', s: SLOT, e: SLOT + T, kind: 're', label: `A 重传 ${bytes.value}B` },
    { id: 'b2', side: 'B', s: 112, e: 112 + T, kind: 're', label: `B 重传 ${bytes.value}B` }
  ].filter(Boolean)

  const shown = []
  const marks = []
  const out = []
  function add(id) { const it = all.find(v => v.id === id); if (it) shown.push(it) }
  function snap(desc, t, extra = {}) {
    out.push({
      t, items: shown.map(v => ({ ...v })), markers: marks.map(v => ({ ...v })),
      colls: 1, aState: '—', bState: '—', ak: 0, ar: 0, bk: 0, br: 0, desc, ...extra
    })
  }

  snap('初始：总线空闲，站点 A、B 均无数据待发（10BASE-T 使用集线器的星形拓扑，逻辑上仍是总线网）', 0, { colls: 0, aState: '空闲', bState: '空闲' })
  add('a1')
  snap('t=0μs：A 先进行载波监听，总线空闲则立即发送自己的帧', 0, { colls: 0, aState: '发送中', bState: '空闲' })
  add('b1')
  snap(`t=${(TAU - DELTA).toFixed(1)}μs（τ−δ）：B 也想发送，但 A 的信号最前端尚未到达 B，B 监听结果为空闲，于是也开始发送`, TAU - DELTA, { aState: '发送中', bState: '发送中' })
  marks.push({ t: TAU - DELTA / 2, text: '碰撞', color: '#e05252' })
  snap(`t=${(TAU - DELTA / 2).toFixed(1)}μs：两路信号在线路上叠加，电压超过门限值 → 发生碰撞，信号被破坏`, TAU - DELTA / 2, { aState: '发送中', bState: '发送中' })
  marks.push({ t: TAU, text: 'B 检测到碰撞', color: '#22a06b' })
  add('bj')
  snap(`t=${TAU}μs（τ）：B 检测到信道异常，立即停止发送，并发出 32bit 强化干扰信号让所有站点都知道`, TAU, { aState: '发送中', bState: '停止并发送干扰信号', bk: 1, br: 1 })
  snap(`t=${(TAU + JAMT).toFixed(1)}μs：B 执行二进制指数退避——第 1 次冲突 k=min(1,10)=1，在 [0,1] 中随机取 r=1，推迟 1 个争用期 ${SLOT}μs`, TAU + JAMT, { aState: '发送中', bState: '退避等待中', bk: 1, br: 1 })

  if (!canDetect) {
    snap(`注意：本帧只有 ${bytes.value} 字节，发送时间 ${T.toFixed(1)}μs < 争用期 ${SLOT}μs，A 在来得及检测到碰撞前就已发完，会误以为发送成功 —— 这正是以太网规定最短帧长 64 字节的原因`, T, { aState: '发送完毕（未发现冲突）', bState: '退避等待中', bk: 1, br: 1 })
    return out
  }

  marks.push({ t: 2 * TAU - DELTA, text: 'A 检测到碰撞', color: '#3b6ef6' })
  add('aj')
  snap(`t=${(2 * TAU - DELTA).toFixed(1)}μs（2τ−δ）：A 检测到碰撞（最迟不超过 2τ 必能检测到），同样停止发送并发出干扰信号`, 2 * TAU - DELTA, { aState: '停止并发送干扰信号', bState: '退避等待中', bk: 1, br: 1 })
  snap(`t=${(2 * TAU - DELTA + JAMT).toFixed(1)}μs：A 也执行二进制指数退避——k=1，随机取 r=0，推迟 0μs，立即准备重传`, 2 * TAU - DELTA + JAMT, { aState: '退避等待 0μs', bState: '退避等待中', ak: 1, ar: 0, bk: 1, br: 1 })
  add('a2')
  snap(`t=${SLOT}μs（争用期）：A 退避结束，重新载波监听发现总线空闲，开始重传并成功抢占信道`, SLOT, { aState: '重传中', bState: '退避等待中', ak: 1, ar: 0, bk: 1, br: 1 })
  snap(`A 的 ${bytes.value} 字节帧占用信道 ${T.toFixed(1)}μs 后发送完毕（${bytes.value} × 8bit ÷ 10Mb/s）`, SLOT + T, { aState: '发送完毕', bState: '退避等待中', ak: 1, ar: 0, bk: 1, br: 1 })
  add('b2')
  snap(`B 退避期间持续监听载波：发现总线忙便一直推迟，等到信道空闲并再等帧间隔 ${IFG}μs（96bit）后才开始发送`, 112, { aState: '已成功', bState: '重传中', ak: 1, ar: 0, bk: 1, br: 1 })
  snap(`t=${(112 + T).toFixed(1)}μs：B 重传成功。CSMA/CD 全过程 = 载波监听 + 碰撞检测 + 二进制指数退避`, 112 + T, { aState: '已成功', bState: '已成功', ak: 1, ar: 0, bk: 1, br: 1 })
  // 小结是纯文案，数据与上一步完全一致 —— 画面会停在原地不动，用户以为动画坏了。
  // 加 done 标记让它与上一步区分开，同时也给模板一个明确的收尾态
  snap(`小结：最多经过 16 次重传仍失败则丢弃该帧并向高层报告；以太网是无连接、不可靠交付的，重传由高层负责`, 112 + T, { aState: '已成功', bState: '已成功', ak: 1, ar: 0, bk: 1, br: 1, done: true })
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)

// 估算文本宽度：全角按 1 字宽，其余按 0.56 字宽
function textW(s, fs) {
  let w = 0
  for (const ch of String(s)) w += /[\u2e80-\u9fff\uff00-\uffef]/.test(ch) ? fs : fs * 0.56
  return Math.ceil(w)
}

// 先定画布宽度，再反推 时间→x 的比例（px/μs）：
// 以前比例固定 3.3，帧长填到 300B 时 maxT≈360μs，x 坐标会冲到 1258 而画布只有 1000，
// 整条时间轴都画到了画布外面
const maxT = computed(() => 112 + frameT.value + 8)
const svgW = computed(() => Math.min(1000, Math.max(660, Math.round(90 + maxT.value * 3.3))))
const PX = computed(() => Math.min(3.3, (svgW.value - 90) / maxT.value))
function x(t) { return 70 + t * PX.value }

const ticks = computed(() => {
  const out = []
  for (let i = 0; i * TAU <= maxT.value; i++) out.push({ t: i * TAU, label: i === 0 ? '0' : i === 1 ? 'τ' : i + 'τ' })
  return out
})

// 事件标记错行：τ−δ 与 τ 只差 4μs（约 13px），「碰撞」和「B 检测到碰撞」会完全叠在一起
const markerList = computed(() => {
  const rows = [84, 99, 114]
  const placed = []
  return (cur.value.markers || []).map(mk => {
    const cx = x(mk.t)
    const w = textW(mk.text, 10)
    let cy = rows.find(r => !placed.some(p => p.cy === r && Math.abs(p.cx - cx) < (p.w + w) / 2 + 8))
    if (cy == null) cy = rows[0]
    placed.push({ cx, cy, w })
    return { ...mk, cx, cy }
  })
})

// 占用条标签错行：同一站点行上先后出现的多段（如 B 发送 / 干扰信号）x 区间重叠，
// 以前都钉在 row-4 上必然叠字，这里按行上已占用的 x 区间依次让位到 上/下 两行
const itemLabelY = computed(() => {
  const placed = []
  const out = {}
  cur.value.items.forEach((it, i) => {
    if (it.e > cur.value.t) return
    const row = it.side === 'A' ? rowA : rowB
    const x1 = x(it.s) + 4
    const x2 = x1 + textW(it.label, 10)
    const cands = [row - 5, row + 37, row - 19, row + 51]
    let y = cands.find(cy => !placed.some(p => Math.abs(p.y - cy) < 12 && x1 < p.x2 + 6 && p.x1 - 6 < x2))
    if (y == null) y = cands[0]
    placed.push({ x1, x2, y })
    out[i] = y
  })
  return out
})

// 当前时刻文字贴着竖线右侧，t 接近末端时会顶出画布右边缘，改成越界就翻到左侧
const tLabel = computed(() => {
  const px = x(cur.value.t)
  const txt = `t = ${cur.value.t.toFixed(1)}μs`
  return (px + 6 + textW(txt, 11) > svgW.value - 6)
    ? { x: px - 6, anchor: 'end' }
    : { x: px + 6, anchor: 'start' }
})
function fillOf(it) { return it.side === 'A' ? '#e6eeff' : '#e6f6ee' }
function strokeOf(it) { return it.kind === 'jam' ? '#e05252' : (it.side === 'A' ? '#3b6ef6' : '#22a06b') }

function applyBytes() {
  const v = Number(String(bytesInput.value || '').trim())
  if (!isNaN(v) && v >= 1 && v <= 300) { bytes.value = Math.round(v); player.reset() }
  else { bytesInput.value = String(BYTES_DEFAULT); bytes.value = BYTES_DEFAULT; player.reset() }
}
function resetBytes() {
  bytes.value = BYTES_DEFAULT
  bytesInput.value = String(BYTES_DEFAULT)
  player.reset()
}
</script>

<style scoped>
.cd-wrap { display: flex; gap: 24px; align-items: flex-start; flex-wrap: wrap; }
.cd-svg { background: #fbfcff; border-radius: 8px; flex-shrink: 0; }
.cd-panel { flex: 1; min-width: 260px; }
.panel-title { font-size: 13px; font-weight: 600; margin-bottom: 6px; color: var(--text-2); }
.info-row { display: flex; justify-content: space-between; gap: 10px; padding: 4px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.points { padding-left: 18px; margin: 0; }
.points li { font-size: 12px; line-height: 1.9; color: var(--text-2); }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
