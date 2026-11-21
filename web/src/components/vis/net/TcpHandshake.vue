<template>
  <VisFrame
    :title="isWaves ? 'TCP 四次挥手 · 连接释放' : 'TCP 三次握手 · 连接建立'"
    :desc="isWaves ? '全双工通信，每个方向必须单独关闭；主动方需等待 2MSL' : '通过 SYN / SYN+ACK / ACK 三次交互确认双方收发能力与初始序列号'"
    :player="player" :status-text="statusText" back-to="/knowledge/9"
  >
    <template #extra>
      <el-button size="small" plain @click="player.reset()">重播</el-button>
    </template>

    <div class="tcp-wrap">
      <svg width="640" height="400" class="tcp-svg">
        <!-- 端点生命线 -->
        <line x1="130" y1="40" x2="130" y2="370" stroke="#c8d3e6" stroke-width="2" stroke-dasharray="5 4" />
        <line x1="470" y1="40" x2="470" y2="370" stroke="#c8d3e6" stroke-width="2" stroke-dasharray="5 4" />
        <text x="130" y="28" text-anchor="middle" font-size="13" font-weight="600" fill="#1f2733">客户端 Client</text>
        <text x="470" y="28" text-anchor="middle" font-size="13" font-weight="600" fill="#1f2733">服务端 Server</text>

        <!-- 状态柱（宽度按最长状态名 ESTABLISHED 取 72，否则文字会撑出方框） -->
        <g v-for="(s, i) in clientTimeline" :key="'c' + i">
          <rect x="94" :y="s.y" width="72" height="52" rx="6" :fill="s.fill" :stroke="s.stroke" stroke-width="1.5" />
          <text x="130" :y="s.y + 32" text-anchor="middle" font-size="10" :fill="s.color" font-weight="600">{{ s.state }}</text>
        </g>
        <g v-for="(s, i) in serverTimeline" :key="'s' + i">
          <rect x="434" :y="s.y" width="72" height="52" rx="6" :fill="s.fill" :stroke="s.stroke" stroke-width="1.5" />
          <text x="470" :y="s.y + 32" text-anchor="middle" font-size="10" :fill="s.color" font-weight="600">{{ s.state }}</text>
        </g>

        <!-- 报文（箭头画到状态柱边缘为止，不再伸进柱子里压住状态文字） -->
        <g v-for="(m, i) in visibleMsgs" :key="'m' + i">
          <line
            :x1="m.from === 'c' ? 170 : 430" :y1="m.y"
            :x2="m.from === 'c' ? 430 : 170" :y2="m.y"
            :stroke="m.color" stroke-width="2.4" marker-end="url(#tcp-arrow)"
          />
          <rect
            :x="m.lx" :y="m.y - 20" :width="m.w" height="24" rx="5"
            :fill="m.bg" :stroke="m.color" stroke-width="1.2"
          />
          <text :x="m.lx + m.w / 2" :y="m.y - 3" text-anchor="middle" font-size="11" :fill="m.color" font-weight="600">{{ m.label }}</text>
          <text :x="m.lx + m.w / 2" :y="m.y + 18" text-anchor="middle" font-size="10" fill="#8b95a3">{{ m.detail }}</text>
          <text x="300" :y="m.y - 24" text-anchor="middle" font-size="10" fill="#8b95a3">第 {{ i + 1 }} 步</text>
        </g>

        <defs>
          <marker id="tcp-arrow" markerWidth="9" markerHeight="9" refX="8" refY="3" orient="auto">
            <path d="M0,0 L8,3 L0,6 z" :fill="lastColor" />
          </marker>
        </defs>
      </svg>

      <div class="tcp-panel">
        <div class="panel-title">关键字段</div>
        <div class="info-row"><span>客户端状态</span><b style="color:var(--brand)">{{ clientState }}</b></div>
        <div class="info-row"><span>服务端状态</span><b style="color:var(--success)">{{ serverState }}</b></div>
        <div class="info-row"><span>客户端 seq</span><b>{{ clientSeq }}</b></div>
        <div class="info-row"><span>服务端 seq</span><b>{{ serverSeq }}</b></div>
        <el-divider />
        <div class="panel-title">要点解析</div>
        <ul class="points">
          <li v-for="(p, i) in pointsList" :key="i">{{ p }}</li>
        </ul>
        <el-tag v-if="finished" :type="isWaves ? 'success' : 'primary'" effect="dark" size="small" style="margin-top:8px">
          {{ isWaves ? '连接已完全关闭' : '连接建立成功，开始传输数据' }}
        </el-tag>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> 客户端 → 服务端</span>
      <span><i class="dot" style="background:#22a06b"></i> 服务端 → 客户端</span>
      <span><i class="dot" style="background:#e8a13a"></i> 等待计时（2MSL）</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const props = defineProps({ mode: { type: String, default: 'handshake' } })
const isWaves = computed(() => props.mode === 'waves')

const HANDSHAKE = [
  {
    from: 'c', label: 'SYN=1, seq=x', detail: '不携带数据，消耗 1 个序号',
    clientState: 'SYN-SENT', serverState: 'LISTEN',
    clientSeq: 'x', serverSeq: '—',
    desc: '第一次握手：客户端发送连接请求报文，SYN=1，携带自己的初始序列号 x，进入 SYN-SENT 状态'
  },
  {
    from: 's', label: 'SYN=1, ACK=1, seq=y, ack=x+1', detail: '确认客户端的 SYN',
    clientState: 'SYN-SENT', serverState: 'SYN-RCVD',
    clientSeq: 'x', serverSeq: 'y',
    desc: '第二次握手：服务端同意建立连接，回 SYN=1, ACK=1，给出自己的初始序列号 y 并确认 ack=x+1'
  },
  {
    from: 'c', label: 'ACK=1, seq=x+1, ack=y+1', detail: '可携带数据',
    clientState: 'ESTABLISHED', serverState: 'ESTABLISHED',
    clientSeq: 'x+1', serverSeq: 'y+1',
    desc: '第三次握手：客户端确认服务端的 SYN，连接建立完成，双方进入 ESTABLISHED 状态'
  }
]

const WAVES = [
  {
    from: 'c', label: 'FIN=1, seq=u', detail: '主动方停止发送数据',
    clientState: 'FIN-WAIT-1', serverState: 'ESTABLISHED',
    clientSeq: 'u', serverSeq: 'v',
    desc: '第一次挥手：主动关闭方发送 FIN=1，进入 FIN-WAIT-1，表示本方不再发送数据'
  },
  {
    from: 's', label: 'ACK=1, seq=v, ack=u+1', detail: '半关闭状态，仍可发数据',
    clientState: 'FIN-WAIT-2', serverState: 'CLOSE-WAIT',
    clientSeq: 'u+1', serverSeq: 'v',
    desc: '第二次挥手：被动方回 ACK 确认，进入 CLOSE-WAIT；此时为半关闭状态，被动方仍可发送剩余数据'
  },
  {
    from: 's', label: 'FIN=1, ACK=1, seq=w, ack=u+1', detail: '数据发送完毕',
    clientState: 'FIN-WAIT-2', serverState: 'LAST-ACK',
    clientSeq: 'u+1', serverSeq: 'w',
    desc: '第三次挥手：被动方数据发送完毕后发送 FIN=1，进入 LAST-ACK，等待最后的确认'
  },
  {
    from: 'c', label: 'ACK=1, seq=u+1, ack=w+1', detail: '进入 TIME-WAIT（2MSL）',
    clientState: 'TIME-WAIT', serverState: 'CLOSED',
    clientSeq: 'u+1', serverSeq: 'w+1',
    desc: '第四次挥手：主动方发回最终 ACK，进入 TIME-WAIT，需等待 2MSL 后才进入 CLOSED'
  },
  {
    from: 'c', label: '等待 2MSL 后关闭', detail: '确保最后 ACK 到达 + 旧报文消散',
    clientState: 'CLOSED', serverState: 'CLOSED',
    clientSeq: '—', serverSeq: '—',
    desc: '2MSL 计时结束：客户端进入 CLOSED，连接彻底释放'
  }
]

const messages = computed(() => (isWaves.value ? WAVES : HANDSHAKE))

const steps = computed(() =>
  messages.value.map((m, i) => ({ ...m, upto: i + 1 }))
)

const player = usePlayer(steps)
const cur = computed(() => player.current.value || { upto: 0, desc: '点击播放开始演示', clientState: 'CLOSED', serverState: 'LISTEN', clientSeq: '—', serverSeq: '—' })
const statusText = computed(() => cur.value.desc)
const finished = computed(() => player.finished.value)

// 估算文本宽度：全角（中日韩/全角标点）按 1 字宽，其余按 0.56 字宽
function textW(s, fs) {
  let w = 0
  for (const ch of String(s)) w += /[\u2e80-\u9fff\uff00-\uffef]/.test(ch) ? fs : fs * 0.56
  return Math.ceil(w)
}

const visibleMsgs = computed(() => {
  // 报文条数不同（握手 3 条 / 挥手 5 条），行距要跟着变：
  // 挥手以前固定 72，第 5 条 y=378，状态柱 352~404 直接被 400 高的画布裁掉
  const n = messages.value.length
  const start = n > 4 ? 78 : 92
  const gap = n > 4 ? 68 : 96
  return messages.value.slice(0, cur.value.upto || 0).map((m, i) => {
    const y = start + i * gap
    const fromC = m.from === 'c'
    const w = Math.max(120, textW(m.label, 11) + 20)
    const lx = (130 + 470) / 2 - w / 2
    return {
      ...m, y, w, lx,
      color: fromC ? '#3b6ef6' : '#22a06b',
      bg: fromC ? '#eef3ff' : '#e6f6ee'
    }
  })
})

const lastColor = computed(() => {
  const v = visibleMsgs.value[visibleMsgs.value.length - 1]
  return v ? v.color : '#8b95a3'
})

const clientTimeline = computed(() =>
  visibleMsgs.value.map(m => ({
    y: m.y - 26,
    state: m.clientState,
    fill: m.clientState === 'ESTABLISHED' ? '#dcf3e7' : m.clientState === 'TIME-WAIT' ? '#fdf3e2' : '#eef3ff',
    stroke: m.clientState === 'ESTABLISHED' ? '#22a06b' : m.clientState === 'TIME-WAIT' ? '#e8a13a' : '#3b6ef6',
    color: m.clientState === 'ESTABLISHED' ? '#176b48' : m.clientState === 'TIME-WAIT' ? '#a5701a' : '#1a47b8'
  }))
)
const serverTimeline = computed(() =>
  visibleMsgs.value.map(m => ({
    y: m.y - 26,
    state: m.serverState,
    fill: m.serverState === 'ESTABLISHED' ? '#dcf3e7' : m.serverState === 'CLOSED' ? '#f0f2f6' : '#e6f6ee',
    stroke: m.serverState === 'ESTABLISHED' ? '#22a06b' : m.serverState === 'CLOSED' ? '#c8d3e6' : '#22a06b',
    color: m.serverState === 'ESTABLISHED' ? '#176b48' : m.serverState === 'CLOSED' ? '#8b95a3' : '#176b48'
  }))
)

const clientState = computed(() => cur.value.clientState || 'CLOSED')
const serverState = computed(() => cur.value.serverState || 'LISTEN')
const clientSeq = computed(() => cur.value.clientSeq || '—')
const serverSeq = computed(() => cur.value.serverSeq || '—')

const pointsList = computed(() =>
  isWaves.value
    ? [
        'TCP 是全双工的，每个方向必须单独关闭，因此需要四次挥手',
        '收到 FIN 只表示对方不再发送数据，本方仍可继续发送',
        'TIME-WAIT = 2MSL：保证最后 ACK 到达 + 让旧报文在网络中消散',
        'CLOSE-WAIT 出现在被动关闭方，LAST-ACK 之后才真正关闭'
      ]
    : [
        '两次握手无法确认服务端初始序列号已被客户端收到',
        'SYN 报文不携带数据，但仍要消耗一个序列号',
        '第三次握手可以携带数据',
        'SYN 洪泛攻击正是利用半连接耗尽服务端资源'
      ]
)
</script>

<style scoped>
.tcp-wrap { display: flex; gap: 24px; align-items: flex-start; flex-wrap: wrap; }
.tcp-svg { background: #fbfcff; border-radius: 8px; flex-shrink: 0; }
.tcp-panel { flex: 1; min-width: 260px; }
.panel-title { font-size: 13px; font-weight: 600; margin-bottom: 6px; color: var(--text-2); }
.info-row { display: flex; justify-content: space-between; padding: 4px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.points { padding-left: 18px; margin: 0; }
.points li { font-size: 12px; line-height: 1.9; color: var(--text-2); }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
