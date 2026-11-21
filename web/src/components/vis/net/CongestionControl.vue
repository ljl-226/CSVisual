<template>
  <VisFrame title="TCP 拥塞控制与滑动窗口" desc="慢开始（指数增长）→ 拥塞避免（线性增长）→ 超时重传 / 快重传快恢复" :player="player" :status-text="statusText" back-to="/knowledge/13">
    <template #extra>
      <span class="small muted">初始 ssthresh</span>
      <el-input-number v-model="initSsthresh" size="small" :min="4" :max="32" style="width:100px" @change="player.reset()" />
      <el-checkbox v-model="withTimeout" size="small" @change="player.reset()">模拟超时</el-checkbox>
      <el-checkbox v-model="withDupAck" size="small" @change="player.reset()">模拟3个重复ACK</el-checkbox>
      <el-button size="small" plain @click="player.reset()">重播</el-button>
    </template>

    <!-- 滑动窗口 -->
    <div class="win-area">
      <div class="panel-title">发送窗口（cwnd = {{ cwnd }}，接收窗口 rwnd = {{ rwnd }}，实际发送窗口 = min(cwnd, rwnd) = {{ sendWindow }}）</div>
      <div class="win-row">
        <div
          v-for="i in 26" :key="i"
          class="win-cell"
          :class="cellClass(i - 1)"
        >{{ i - 1 }}</div>
      </div>
      <div class="win-legend-inline">
        <span><i class="dot" style="background:#cfe0ff"></i> 窗口内已发送未确认</span>
        <span><i class="dot" style="background:#fdeaea"></i> 丢失待重传</span>
        <span><i class="dot" style="background:#f7f9fc"></i> 窗口外，待窗口滑动才能发送</span>
      </div>
    </div>

    <!-- cwnd 曲线 -->
    <svg width="700" height="240" class="cc-svg">
      <line x1="40" y1="200" x2="680" y2="200" stroke="#c8d3e6" stroke-width="1.5" />
      <line x1="40" y1="20" x2="40" y2="200" stroke="#c8d3e6" stroke-width="1.5" />
      <text x="12" y="30" font-size="11" fill="#8b95a3">cwnd</text>
      <text x="650" y="218" font-size="11" fill="#8b95a3">RTT（轮次）</text>
      <line v-for="g in gridLines" :key="'g' + g.v" x1="40" :y1="g.y" x2="680" :y2="g.y" stroke="#f0f2f6" />
      <text v-for="g in gridLines" :key="'gt' + g.v" x="30" :y="g.y + 4" text-anchor="end" font-size="10" fill="#8b95a3">{{ g.v }}</text>

      <!-- ssthresh 虚线 -->
      <line v-if="ssthreshLine > 0" x1="40" :y1="yOf(ssthreshLine)" x2="680" :y2="yOf(ssthreshLine)"
        stroke="#e8a13a" stroke-width="1.4" stroke-dasharray="6 4" />
      <text v-if="ssthreshLine > 0" x="676" :y="yOf(ssthreshLine) - 6" text-anchor="end" font-size="11" fill="#e8a13a">
        ssthresh = {{ ssthreshLine }}
      </text>

      <polyline :points="linePoints" fill="none" stroke="#3b6ef6" stroke-width="2.4" />
      <circle
        v-for="(p, i) in visiblePoints" :key="i"
        :cx="p.x" :cy="p.y" r="4" :fill="p.event ? p.color : '#3b6ef6'"
      />
      <text
        v-for="(p, i) in visiblePoints" :key="'t' + i"
        :x="p.x" :y="p.y - 10" text-anchor="middle" font-size="10"
        :fill="p.event ? p.color : '#5a6472'"
      >{{ p.v }}</text>
    </svg>

    <div class="cc-panel">
      <div class="stat-row">
        <div class="stat-box">
          <div class="sv">{{ phaseName }}</div>
          <div class="sl">当前阶段</div>
        </div>
        <div class="stat-box">
          <div class="sv">{{ cwnd }}</div>
          <div class="sl">拥塞窗口 cwnd</div>
        </div>
        <div class="stat-box">
          <div class="sv" style="color:var(--warning)">{{ ssthresh }}</div>
          <div class="sl">门限 ssthresh</div>
        </div>
        <div class="stat-box">
          <div class="sv">{{ rtt }}</div>
          <div class="sl">传输轮次 RTT</div>
        </div>
      </div>
      <el-divider />
      <div class="panel-title">规则速查</div>
      <ul class="rules">
        <li><b>慢开始</b>：cwnd 从 1 起，每经过一个 RTT 翻倍（×2），直到 cwnd ≥ ssthresh</li>
        <li><b>拥塞避免</b>：cwnd ≥ ssthresh 后，每 RTT 只加 1（线性增长）</li>
        <li><b>超时重传</b>：ssthresh = cwnd/2，cwnd 重置为 1，重新慢开始</li>
        <li><b>快重传</b>：收到 3 个重复 ACK 立即重传丢失报文，不等超时</li>
        <li><b>快恢复</b>：ssthresh = cwnd/2，cwnd 从新的 ssthresh 开始线性增长（不回到 1）</li>
      </ul>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> cwnd 变化曲线</span>
      <span><i class="dot" style="background:#e05252"></i> 超时重传事件</span>
      <span><i class="dot" style="background:#e8a13a"></i> 快重传 / 快恢复事件</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const initSsthresh = ref(16)
const withTimeout = ref(true)
const withDupAck = ref(true)
const rwnd = 20

const steps = computed(() => {
  const out = []
  let cwnd = 1
  let ssthresh = initSsthresh.value
  let phase = 'slow-start'
  let sentBase = 0
  const events = []
  if (withTimeout.value) events.push({ rtt: 9, type: 'timeout' })
  if (withDupAck.value) events.push({ rtt: 15, type: 'dupack' })

  for (let rtt = 1; rtt <= 20; rtt++) {
    let event = null
    let grow = null
    const ev = events.find(e => e.rtt === rtt)
    if (ev) {
      if (ev.type === 'timeout') {
        event = { type: 'timeout', color: '#e05252', text: '超时重传' }
        ssthresh = Math.max(2, Math.floor(cwnd / 2))
        cwnd = 1
        phase = 'slow-start'
      } else {
        event = { type: 'dupack', color: '#e8a13a', text: '3个重复ACK' }
        ssthresh = Math.max(2, Math.floor(cwnd / 2))
        cwnd = ssthresh
        phase = 'fast-recovery'
      }
    } else if (phase === 'slow-start') {
      // 慢开始每轮翻倍，但**不能越过 ssthresh**：到了门限就必须改线性增长。
      // 曾经先翻倍再判断门限，于是 cwnd 从 8 直接翻到 16 越过了 ssthresh=10，
      // 而 phase 此时已被改成拥塞避免，文案却说「线性 +1 = 16」——与实际行为不符。
      // 这里把「本轮到底怎么长的」单独记成 grow，文案按它如实措辞。
      const doubled = cwnd * 2
      if (doubled >= ssthresh) {
        cwnd = ssthresh        // 本轮只能涨到门限
        phase = 'congestion-avoidance'
        grow = 'clamp'
      } else {
        cwnd = doubled
        grow = 'double'
      }
    } else if (phase === 'fast-recovery') {
      cwnd = cwnd + 1
      grow = 'linear'
    } else {
      cwnd = cwnd + 1
      grow = 'linear'
    }
    sentBase += Math.min(cwnd, rwnd)
    out.push({
      rtt, cwnd, ssthresh, phase, event, grow,
      sentBase,
      lost: event ? Math.floor(Math.min(cwnd, rwnd) / 2) : -1,
      desc: describe(rtt, cwnd, ssthresh, phase, event, grow)
    })
  }
  return out
})

// grow 记录「这一轮到底用了什么规则」，文案必须按它如实措辞。
// 只看 phase 会出错：慢开始的最后一轮其实是封顶到 ssthresh，
// 而 phase 在那一轮末尾已经切成了拥塞避免。
function describe(rtt, cwnd, ssthresh, phase, event, grow) {
  if (event) {
    return event.type === 'timeout'
      ? `第 ${rtt} 轮：发生超时重传（RTO）→ ssthresh 降为 cwnd/2 = ${ssthresh}，cwnd 重置为 1，重新慢开始`
      : `第 ${rtt} 轮：收到 3 个重复 ACK → 触发快重传，执行快恢复：ssthresh = cwnd/2 = ${ssthresh}，cwnd 从 ${ssthresh} 开始线性增长`
  }
  if (grow === 'double') return `第 ${rtt} 轮：慢开始阶段，cwnd 翻倍至 ${cwnd}（指数增长）`
  if (grow === 'clamp') {
    return `第 ${rtt} 轮：慢开始阶段，cwnd 翻倍会越过门限，故只能涨到 ssthresh = ${ssthresh}；从下一轮起转入拥塞避免（线性增长）`
  }
  if (phase === 'fast-recovery') return `第 ${rtt} 轮：快恢复阶段，cwnd 线性增长至 ${cwnd}`
  return `第 ${rtt} 轮：拥塞避免阶段，cwnd 线性 +1 = ${cwnd}`
}

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const cwnd = computed(() => cur.value.cwnd)
const ssthresh = computed(() => cur.value.ssthresh)
const rtt = computed(() => cur.value.rtt)
const sendWindow = computed(() => Math.min(cwnd.value, rwnd))
const phaseName = computed(() => ({
  'slow-start': '慢开始',
  'congestion-avoidance': '拥塞避免',
  'fast-recovery': '快恢复'
}[cur.value.phase] || '慢开始'))

const maxCwnd = computed(() => Math.max(24, ...steps.value.map(s => s.cwnd)))
const gridLines = computed(() => {
  const stepv = Math.ceil(maxCwnd.value / 5)
  const out = []
  for (let v = 0; v <= maxCwnd.value; v += stepv) out.push({ v, y: yOf(v) })
  return out
})
function yOf(v) {
  return 200 - (v / maxCwnd.value) * 170
}
function xOf(r) {
  return 40 + r * 31
}

const visiblePoints = computed(() => {
  const pts = steps.value.slice(0, (player.idx.value || 0) + 1)
  return pts.map(s => ({
    x: xOf(s.rtt), y: yOf(s.cwnd), v: s.cwnd,
    event: s.event ? s.event.type : null,
    color: s.event ? s.event.color : '#3b6ef6'
  }))
})
const linePoints = computed(() => visiblePoints.value.map(p => `${p.x},${p.y}`).join(' '))
const ssthreshLine = computed(() => cur.value.ssthresh)

/**
 * 窗口格子着色。
 *
 * 曾经用「累计发送总量 sentBase」当窗口起点：它到 20 轮时已累计 200+，
 * 而格子只有 26 个，于是 start 很快就超出全部格子，26 格一律渲染成「已确认」——
 * 画面从第 5 轮起整整 15 轮一动不动。同时 lost 分支排在 i < start 之后，
 * 「丢失待重传」这个状态在任何一步都显示不出来，图例里的红色永远是摆设。
 *
 * 改成只看「当前窗口」：格子 i 表示本窗口内的第 i 个序号，
 * 窗口大小随 cwnd 每轮变化，画面自然跟着动。
 */
function cellClass(i) {
  const win = sendWindow.value
  // lost 判断必须放在窗口判断之前，否则永远轮不到它
  if (cur.value.lost >= 0 && i === cur.value.lost) return 'cell-lost'
  if (i < win) return 'cell-sent'
  return 'cell-free'
}
</script>

<style scoped>
.win-area { margin-bottom: 14px; }
.panel-title { font-size: 13px; font-weight: 600; margin-bottom: 6px; color: var(--text-2); }
.win-row { display: flex; gap: 3px; flex-wrap: wrap; }
.win-cell {
  width: 26px; height: 26px; line-height: 26px; text-align: center; border-radius: 4px;
  font-size: 11px; border: 1px solid var(--border); background: #f7f9fc; color: var(--text-3);
}
.cell-acked { background: #dcf3e7; border-color: var(--success); color: #176b48; }
.cell-sent { background: #cfe0ff; border-color: var(--brand-2); color: #1a47b8; }
.cell-lost { background: #fdeaea; border-color: var(--danger); color: #a32c2c; font-weight: 700; }
.cell-free { background: #f7f9fc; }
.win-legend-inline { display: flex; gap: 14px; margin-top: 8px; font-size: 12px; color: var(--text-2); flex-wrap: wrap; }
.cc-svg { background: #fbfcff; border-radius: 8px; display: block; }
.cc-panel { margin-top: 14px; }
.stat-row { display: flex; gap: 12px; flex-wrap: wrap; }
.stat-box { flex: 1; min-width: 110px; background: #fbfcff; border: 1px solid var(--border); border-radius: 8px; padding: 10px; text-align: center; }
.sv { font-size: 20px; font-weight: 700; color: var(--brand); }
.sl { font-size: 12px; color: var(--text-2); margin-top: 2px; }
.rules { padding-left: 18px; margin: 0; }
.rules li { font-size: 12px; line-height: 1.9; color: var(--text-2); }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
