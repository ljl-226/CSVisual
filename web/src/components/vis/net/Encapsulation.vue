<template>
  <VisFrame
    title="数据封装与 OSI / TCP-IP 模型"
    desc="上层数据逐层加上首部（或尾部）成为本层 PDU，到达端系统后再逐层剥去，实现对等层的逻辑通信"
    :player="player" :status-text="statusText" back-to="/knowledge/45"
  >
    <template #extra>
      <el-select v-model="proto" size="small" style="width:100px">
        <el-option value="TCP" label="TCP" />
        <el-option value="UDP" label="UDP" />
      </el-select>
      <el-button size="small" plain @click="player.reset()">重播</el-button>
    </template>

    <div class="ep-wrap">
      <svg width="640" height="340" class="ep-svg">
        <g v-for="(r, i) in boxes" :key="'b' + i">
          <rect
            :x="r.x" :y="r.y" :width="r.w" :height="r.h" rx="10"
            :fill="r.present ? r.bg : '#f7f8fb'" :stroke="r.stroke" :stroke-width="i === cur.active ? 2.6 : 1.4"
            :stroke-dasharray="r.present ? '' : '6 4'"
          />
          <text :x="r.x + 10" :y="r.y + 20" font-size="12" font-weight="600" :fill="r.present ? r.color : '#8b95a3'">{{ r.name }}</text>
          <text :x="r.x + 10" :y="r.y + 36" font-size="11" :fill="r.present ? r.color : '#8b95a3'">{{ r.present ? r.pdu : r.hint }}</text>
        </g>

        <!-- 中心数据 -->
        <text x="320" y="188" text-anchor="middle" font-size="14" font-weight="700" fill="#8b5cf6">{{ dataText }}</text>
        <text x="320" y="208" text-anchor="middle" font-size="11" fill="#8b95a3">应用层数据（对等层看起来在「水平」通信）</text>

        <!-- 物理层比特流 -->
        <g v-if="cur.phase === 'wire'">
          <text x="320" y="316" text-anchor="middle" font-size="13" font-family="monospace" fill="#e05252">{{ bitStream }}</text>
          <text x="320" y="332" text-anchor="middle" font-size="11" fill="#8b95a3">物理层：只负责透明地传送比特流</text>
        </g>
      </svg>

      <div class="ep-panel">
        <div class="info-row"><span>当前处理层</span><b :style="{ color: curLayer.color }">{{ curLayer.name }}</b></div>
        <div class="info-row"><span>该层 PDU 名称</span><b>{{ curLayer.pdu }}</b></div>
        <div class="info-row"><span>传输层协议</span><b style="color:var(--brand)">{{ proto }}</b></div>
        <div class="info-row"><span>当前阶段</span><b>{{ phaseText }}</b></div>
        <el-divider />
        <div class="panel-title">本层首部关键字段</div>
        <ul class="points">
          <li v-for="(f, i) in curLayer.fields" :key="i">{{ f }}</li>
        </ul>
        <div class="panel-title" style="margin-top:10px">TCP/IP 四层 ⇄ OSI 七层</div>
        <div v-for="(m, i) in modelRows" :key="i" class="model-row" :class="{ active: m.key === curLayer.key }">
          <b>{{ m.tcpip }}</b><span>{{ m.osi }}</span>
        </div>
        <div class="tip small muted">
          以太网 MTU = 1500 字节，IP 数据报超过则分片（标识、标志、片偏移）；TCP 以 MSS 约束报文段大小以避免 IP 分片。
        </div>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#8b5cf6"></i> 应用层数据</span>
      <span><i class="dot" style="background:#3b6ef6"></i> 运输层首部</span>
      <span><i class="dot" style="background:#e8a13a"></i> 网际层 IP 首部</span>
      <span><i class="dot" style="background:#22a06b"></i> 链路层首部 / FCS</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const proto = ref('TCP')
const dataText = 'HTTP 请求：GET /index.html'
const bitStream = '10101100 01101101 11010010 00101110 10101100 11100101'

const modelRows = [
  { key: 'app', tcpip: '应用层', osi: 'OSI：应用层 + 表示层 + 会话层（第 5~7 层）' },
  { key: 'tcp', tcpip: '运输层', osi: 'OSI：运输层（第 4 层）' },
  { key: 'ip', tcpip: '网际层 IP', osi: 'OSI：网络层（第 3 层）' },
  { key: 'link', tcpip: '网络接口层', osi: 'OSI：数据链路层 + 物理层（第 1~2 层）' }
]

// 四层首部（由内到外）：应用数据 → 运输层 → 网际层 → 链路层
const layers = computed(() => [
  {
    key: 'app', name: '应用层数据 DATA', pdu: '报文 message', color: '#8b5cf6', bg: '#f5f1ff',
    fields: [dataText, '进程到进程的端到端数据（逻辑通信）']
  },
  {
    key: 'tcp', name: `${proto.value} 首部`, pdu: proto.value === 'TCP' ? '报文段 segment' : '用户数据报 UDP', color: '#3b6ef6', bg: '#eef3ff',
    fields: proto.value === 'TCP'
      ? ['源端口 54321 / 目的端口 80', '序号 seq、确认号 ack、数据偏移', '窗口 rwnd、检验和、控制位 SYN/ACK/FIN']
      : ['源端口 / 目的端口', '长度、检验和（UDP 8 字节首部，无连接不可靠）']
  },
  {
    key: 'ip', name: 'IP 首部', pdu: 'IP 数据报 datagram', color: '#e8a13a', bg: '#fdf3e2',
    fields: ['版本 4、首部长度、区分服务、总长度', '标识 / 标志 MF、DF / 片偏移（分片用）', 'TTL（每经一个路由器减 1）、协议 = 6 / 17', '源 IP 10.0.0.1、目的 IP 93.184.216.34']
  },
  {
    key: 'link', name: '以太网首部 + FCS', pdu: '帧 frame', color: '#22a06b', bg: '#e6f6ee',
    fields: ['目的 MAC / 源 MAC / 类型 0x0800', '尾部 FCS：CRC 循环冗余检验', '以太网 MTU = 1500 字节']
  }
])

const steps = computed(() => {
  const p = proto.value
  const out = []
  function snap(desc, top, phase, active, stripped = [], extra = {}) {
    out.push({ top, phase, active, stripped: [...stripped], desc, ...extra })
  }
  snap('起点：应用进程把要交换的数据交给应用层，应用层的数据单元叫「报文 message」', 0, 'encap', 0)
  snap(`运输层加上 ${p} 首部实现端到端的进程通信：${p === 'TCP' ? '面向连接、可靠、有流量与拥塞控制' : '无连接、尽最大努力交付'}，形成「报文段」`, 1, 'encap', 1)
  snap('网际层加上 IP 首部（固定部分 20 字节），带上源/目的 IP、TTL 和协议字段，形成「IP 数据报」', 2, 'encap', 2)
  snap('数据链路层把 IP 数据报封装成「帧」：加上目的/源 MAC 与类型字段，尾部加 FCS 供 CRC 检错', 3, 'encap', 3)
  snap('物理层把帧变成比特流在传输媒体上传送，它不认识也不处理任何首部', 3, 'wire', 3)
  snap('帧到达路由器：路由器只上到第 3 层——剥去帧首部查目的 IP 并查路由表，再重新封装成新帧转发（MAC 变了，IP 不变）', 3, 'decap', 3, [3])
  snap('帧到达目的主机的数据链路层：CRC 检验无误后剥去帧首部与尾部，把 IP 数据报上交给网际层', 2, 'decap', 2, [3])
  snap(`网际层检验首部无误且目的 IP 是本机，剥去 IP 首部，按协议字段把报文段交给 ${p}`, 1, 'decap', 1, [3, 2])
  snap(`运输层按目的端口找到套接字：剥去 ${p} 首部，剩下应用层数据`, 0, 'decap', 0, [3, 2, 1])
  // 收尾这句是纯总结，数据与上一步完全一致（画面卡住不动）。
  // 补一个 done 标记把它与上一步区分开，同时给模板明确的完成态
  snap('完成：对等层之间只是逻辑上的水平通信，实际数据只在端系统逐层封装/解封装，中间路由器最多到网际层', 0, 'decap', 0, [3, 2, 1], { done: true })
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)

const curLayer = computed(() => layers.value[cur.value.active] || layers.value[0])
const phaseText = computed(() => ({ encap: '封装（自上而下）', wire: '比特流传输', decap: '解封装（自下而上）' }[cur.value.phase] || '—'))

// 由内到外的四个矩形：每向外一层左右各扩 56、上下各扩 34
const boxes = computed(() => layers.value.map((l, i) => ({
  ...l,
  w: 220 + 112 * i,
  h: 70 + 68 * i,
  x: 320 - (220 + 112 * i) / 2,
  y: 190 - (70 + 68 * i) / 2,
  present: i <= cur.value.top,
  hint: cur.value.stripped.includes(i) ? '（已剥去）' : '（尚未封装）',
  stroke: i <= cur.value.top ? l.color : '#c8d3e6'
})))
</script>

<style scoped>
.ep-wrap { display: flex; gap: 24px; align-items: flex-start; flex-wrap: wrap; }
.ep-svg { background: #fbfcff; border-radius: 8px; flex-shrink: 0; }
.ep-panel { flex: 1; min-width: 260px; }
.panel-title { font-size: 13px; font-weight: 600; margin-bottom: 6px; color: var(--text-2); }
.info-row { display: flex; justify-content: space-between; gap: 10px; padding: 4px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.points { padding-left: 18px; margin: 0; }
.points li { font-size: 12px; line-height: 1.85; color: var(--text-2); }
.model-row { display: flex; justify-content: space-between; gap: 10px; font-size: 12px; padding: 4px 8px; border-radius: 6px; }
.model-row span { color: var(--text-2); }
.model-row.active { background: var(--brand-light); }
.model-row.active b { color: var(--brand); }
.tip { margin-top: 10px; line-height: 1.8; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
