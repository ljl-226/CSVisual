<template>
  <VisFrame
    title="TCP 可靠传输 · 滑动窗口"
    desc="以字节（此处简化为报文段）为单位的发送窗口不断前移：确认到来才滑动，超时或未确认则触发重传"
    :player="player" :status-text="statusText" back-to="/knowledge/44"
  >
    <template #extra>
      <el-select v-model="winSize" size="small" style="width:110px">
        <el-option v-for="w in [2, 3, 4, 5, 6]" :key="w" :value="w" :label="`窗口 ${w}`" />
      </el-select>
      <el-select v-model="lostIdx" size="small" style="width:120px">
        <el-option :value="-1" label="不丢包" />
        <el-option v-for="s in N" :key="s" :value="s - 1" :label="`丢失第 ${s - 1} 段`" />
      </el-select>
      <el-select v-model="ackMode" size="small" style="width:120px">
        <el-option value="cum" label="累积确认 GBN" />
        <el-option value="sack" label="选择确认 SACK" />
      </el-select>
      <el-button size="small" plain @click="resetAll">重置</el-button>
    </template>

    <div class="sw-wrap">
      <svg width="660" height="300" class="sw-svg">
        <!-- 发送方：发送窗口 -->
        <text x="30" y="26" font-size="12" font-weight="600" fill="#1f2733">发送方（主机 A）· 发送窗口</text>
        <text x="206" y="26" font-size="11" fill="#3b6ef6">窗口 [{{ cur.base }}, {{ winEnd }}]</text>
        <rect :x="30 + cur.base * CW" :y="34" :width="Math.min(cur.W, N - cur.base) * CW - 6" height="68" rx="8"
          fill="#eef3ff" stroke="#3b6ef6" stroke-width="1.6" />
        <g v-for="(s, i) in cur.st" :key="'s' + i">
          <rect :x="30 + i * CW" y="42" width="62" height="52" rx="6" :fill="styleOf(s, i).fill" :stroke="styleOf(s, i).stroke"
            stroke-width="1.5" :stroke-dasharray="s === 'unsent' ? '5 3' : ''" />
          <text :x="30 + i * CW + 31" y="66" text-anchor="middle" font-size="15" font-weight="700" :fill="styleOf(s, i).text">{{ i }}</text>
          <text :x="30 + i * CW + 31" y="84" text-anchor="middle" font-size="10" :fill="styleOf(s, i).text">{{ styleOf(s, i).label }}</text>
        </g>

        <!-- 接收方：按序交付 / 失序暂存 -->
        <text x="30" y="150" font-size="12" font-weight="600" fill="#1f2733">接收方（主机 B）· 接收窗口</text>
        <g v-for="(r, i) in cur.rcv" :key="'r' + i">
          <rect :x="30 + i * CW" y="160" width="62" height="48" rx="6" :fill="rStyle(r).fill" :stroke="rStyle(r).stroke"
            stroke-width="1.5" :stroke-dasharray="r === 0 ? '5 3' : ''" />
          <text :x="30 + i * CW + 31" y="182" text-anchor="middle" font-size="15" font-weight="700" :fill="rStyle(r).stroke">{{ i }}</text>
          <text :x="30 + i * CW + 31" y="198" text-anchor="middle" font-size="10" :fill="rStyle(r).stroke">{{ r === 0 ? '未收到' : r === 1 ? '失序丢弃' : '已缓存' }}</text>
        </g>
        <!-- 期望序号（序号越大越靠右，末尾几格会顶出画布，故按文字宽度夹边并对齐方式翻边） -->
        <text :x="expectLabel.x" y="228" font-size="11" fill="#e8a13a" :text-anchor="expectLabel.anchor">{{ expectLabel.text }}</text>
        <text x="30" y="262" font-size="11" fill="#8b95a3">发送窗口内的三类序号：已发送未确认（蓝）、允许发送但未发（虚线框）、暂不允许发送（窗口右侧）</text>
        <text v-if="cur.timer >= 0" x="400" y="26" font-size="11" fill="#e05252">第 {{ cur.timer }} 段 RTO 倒计时 {{ cur.rtoVal }}</text>
      </svg>

      <div class="sw-panel">
        <div class="info-row"><span>发送窗口范围</span><b style="color:var(--brand)">[{{ cur.base }}, {{ winEnd }}]</b></div>
        <div class="info-row"><span>已发送未确认</span><b>{{ sentNotAck }}</b></div>
        <div class="info-row"><span>可立即发送</span><b>{{ canSend }}</b></div>
        <div class="info-row"><span>暂不可发送</span><b>{{ noSend }}</b></div>
        <div class="info-row"><span>接收方 ACK</span><b style="color:var(--success)">{{ expectSeq }}</b></div>
        <div class="info-row"><span>重复确认数</span><b :style="{ color: cur.dupAck >= 3 ? 'var(--danger)' : 'inherit' }">{{ cur.dupAck }}</b></div>
        <div class="info-row"><span>重传 / 丢弃段数</span><b>{{ cur.retrans }} / {{ cur.discards }}</b></div>
        <div class="info-row"><span>SACK 报告块</span><b>{{ cur.sackBlocks.length ? cur.sackBlocks.map(v => '[' + v + ']').join(' ') : '—' }}</b></div>
        <el-divider />
        <div class="panel-title">教材要点</div>
        <ul class="points">
          <li>发送窗口 = min(拥塞窗口 cwnd, 接收窗口 rwnd)；只有收到确认窗口才前移</li>
          <li>累积确认：ACK=n 表示 n 以前全部正确收到，因此丢失时须回退 N 步重传（Go-Back-N）</li>
          <li>选择确认 SACK 在选项中报告失序块，发送方只补发缺失部分，效率更高</li>
          <li>超时重传时间 RTO 略大于加权平均 RTT，超时后需按 Karn 算法退避</li>
        </ul>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#22a06b"></i> 已确认 / 已按序收到</span>
      <span><i class="dot" style="background:#3b6ef6"></i> 已发送未确认（或已缓存）</span>
      <span><i class="dot" style="background:#e05252"></i> 丢失待重传</span>
      <span><i class="dot" style="background:#e8a13a"></i> 失序被丢弃 / 期望序号</span>
      <span><i class="dot" style="background:#c8d3e6"></i> 窗口外暂不可发送</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const N = 8        // 待发送的报文段数（教材中窗口以字节为单位，此处按报文段简化）
const CW = 74      // 每个序号框的横向步进

const DEFAULT_W = 4
const winSize = ref(DEFAULT_W)
const lostIdx = ref(2)
const ackMode = ref('cum')

const steps = computed(() => {
  const W = winSize.value
  const L = lostIdx.value                 // 丢失的报文段序号，-1 表示不丢包
  const sack = ackMode.value === 'sack'
  const out = []
  const st = Array(N).fill('unsent')      // 发送方视角：unsent / sent / acked / lost
  const rcv = Array(N).fill(0)            // 接收方视角：0 未收到 1 失序丢弃 2 已缓存(或已交付)
  let base = 0                            // 发送窗口下界：最早未确认的序号
  let next = 0                            // 下一个可以分配的发送序号
  let dupAck = 0                          // 重复确认个数
  let retrans = 0                         // 重传的段数
  let discards = 0                        // 因失序被丢弃的段数
  let sackBlocks = []                     // SACK 报告的已接收块
  let timer = -1                          // 正在倒计时的段序号
  let rtoVal = 0                          // 倒计时计数

  function snap(desc, extra = {}) {
    out.push({ st: [...st], rcv: [...rcv], base, next, W, L, dupAck, retrans, discards, sackBlocks: [...sackBlocks], timer, rtoVal, desc, ...extra })
  }
  // 只要发送窗口还有空位就继续发
  function trySend() {
    while (next < N && next < base + W) {
      const i = next++
      if (i === L) {
        st[i] = 'lost'
        snap(`发送第 ${i} 段（在途中丢失），它仍占据窗口直到被确认或超时`)
      } else {
        st[i] = 'sent'
        snap(`发送第 ${i} 段 → 变为「已发送未确认」，窗口剩余可用序号 ${Math.max(0, Math.min(N, base + W) - next)} 个`)
      }
    }
  }

  snap(`初始：共 ${N} 个报文段待发送，发送窗口 W=${W}，窗口范围 [${base}, ${base + W - 1}]`)
  trySend()
  // 纯宣告会让这一步与上一帧数据相同（画面不动）。标成 blocked，
  // 让「窗口用尽、只能等确认」这个状态在画面上可辨
  snap('发送窗口内允许发送的序号用尽，必须等待确认到来使窗口前移才能继续发送', { blocked: true })

  let i = 0
  while (i < N) {
    if (i === L) {
      // 宣告丢失时数据还没变，加 lostMark 让画面把这一段标出来（否则这帧与上一帧完全相同）
      snap(`第 ${L} 段丢失，接收方永远收不到它，因此无法给出新的累积确认`, { lostMark: L })
      for (let j = L + 1; j < next; j++) {
        if (rcv[j] === 2) continue
        dupAck++
        if (sack) {
          rcv[j] = 2
          sackBlocks = [...sackBlocks, j].sort((a, b) => a - b)
          snap(`接收方收到失序的第 ${j} 段 → 存入接收缓存，回 ACK=${L} 并携带 SACK 块 [${sackBlocks.join(' ')}]（第 ${dupAck} 个重复确认）`)
        } else {
          rcv[j] = 1
          discards++
          snap(`接收方期望第 ${L} 段，第 ${j} 段失序 → 直接丢弃并重复发送 ACK=${L}（第 ${dupAck} 个重复确认）`)
        }
      }
      timer = L
      for (let c = 3; c >= 1; c--) { rtoVal = c; snap(`第 ${L} 段的超时重传计时器（RTO）倒计时：还剩 ${c} 个时间单位`) }
      timer = -1
      rtoVal = 0
      snap(`第 ${L} 段的 RTO 到期，发送方认为该段丢失，开始重传`)
      if (sack) {
        st[L] = 'sent'
        rcv[L] = 2
        retrans++
        snap(`SACK 已告知仅缺第 ${L} 段 → 只重传第 ${L} 段（选择确认，已缓存的段无需再发）`)
      } else {
        let cnt = 0
        for (let j = L; j < next; j++) { st[j] = 'sent'; retrans++; cnt++ }
        snap(`累积确认只知道 ACK=${L} → 回退 N 步：把第 ${L} ~ ${next - 1} 段共 ${cnt} 段全部重传（Go-Back-N）`)
      }
    }
    st[i] = 'acked'
    rcv[i] = 2
    base = i + 1
    dupAck = 0
    snap(`收到 ACK=${base}：第 ${base} 号以前的数据全部到达，发送窗口前移到 [${base}, ${Math.max(base, Math.min(N - 1, base + W - 1))}]`)
    trySend()
    i++
  }
  // 结论帧同样要带 done 标记，否则与上一帧数据完全相同，看上去像卡住了
  snap(`全部 ${N} 个报文段均被正确接收：可靠传输 = 序号确认 + 超时重传 + 滑动窗口流量控制`, { done: true })
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)

const winEnd = computed(() => Math.max(cur.value.base, Math.min(N - 1, cur.value.base + cur.value.W - 1)))
// 接收方期望的下一序号：第一个尚未交付的位置
const expectSeq = computed(() => {
  const r = cur.value.rcv
  for (let i = 0; i < N; i++) if (r[i] !== 2) return i
  return N
})
// 估算文本宽度：全角按 1 字宽，其余按 0.56 字宽
function textW(s, fs) {
  let w = 0
  for (const ch of String(s)) w += /[\u2e80-\u9fff\uff00-\uffef]/.test(ch) ? fs : fs * 0.56
  return Math.ceil(w)
}

// 「↑ 期望 ACK = n」跟着序号框右移，序号 7、8 时整句会顶出 660 宽的画布被裁掉
const expectLabel = computed(() => {
  const cx = 30 + expectSeq.value * CW + 31
  const text = `↑ 期望 ACK = ${expectSeq.value}`
  const w = textW(text, 11)
  if (cx + w / 2 > 654) return { x: 654, anchor: 'end', text }
  if (cx - w / 2 < 4) return { x: 4, anchor: 'start', text }
  return { x: cx, anchor: 'middle', text }
})

// 按条件挑出序号列表用于面板显示
function idsOf(pick) {
  const ids = cur.value.st.map((s, i) => (pick(s, i) ? i : -1)).filter(v => v >= 0)
  return ids.length ? ids.join(', ') : '—'
}
const sentNotAck = computed(() => idsOf(s => s === 'sent' || s === 'lost'))
const canSend = computed(() => idsOf((s, i) => s === 'unsent' && i < cur.value.base + cur.value.W))
const noSend = computed(() => idsOf((s, i) => i >= cur.value.base + cur.value.W))

// 序号框配色：绿=已确认，蓝=已发送未确认，红=丢失，虚线=窗口内可发送，灰=窗口外不可用
function styleOf(s, i) {
  const inWin = i < cur.value.base + cur.value.W
  if (s === 'acked') return { fill: '#dcf3e7', stroke: '#22a06b', text: '#176b48', label: '已确认' }
  if (s === 'lost') return { fill: '#fdeaea', stroke: '#e05252', text: '#a32c2c', label: '丢失' }
  if (s === 'sent') return { fill: '#e6eeff', stroke: '#3b6ef6', text: '#1f2733', label: '已发送' }
  return inWin
    ? { fill: '#fff', stroke: '#3b6ef6', text: '#1f2733', label: '可发送' }
    : { fill: '#f4f6fa', stroke: '#c8d3e6', text: '#8b95a3', label: '不可用' }
}
function rStyle(r) {
  return r === 2 ? { fill: '#dcf3e7', stroke: '#22a06b' } : r === 1 ? { fill: '#fdf3e2', stroke: '#e8a13a' } : { fill: '#fff', stroke: '#c8d3e6' }
}

function resetAll() {
  winSize.value = DEFAULT_W
  lostIdx.value = 2
  ackMode.value = 'cum'
  player.reset()
}
</script>

<style scoped>
.sw-wrap { display: flex; gap: 24px; align-items: flex-start; flex-wrap: wrap; }
.sw-svg { background: #fbfcff; border-radius: 8px; flex-shrink: 0; }
.sw-panel { flex: 1; min-width: 260px; }
.panel-title { font-size: 13px; font-weight: 600; margin-bottom: 6px; color: var(--text-2); }
.info-row { display: flex; justify-content: space-between; gap: 10px; padding: 4px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.points { padding-left: 18px; margin: 0; }
.points li { font-size: 12px; line-height: 1.9; color: var(--text-2); }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
