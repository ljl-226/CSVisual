<template>
  <VisFrame title="ARP 地址解析协议" desc="广播 ARP 请求 → 目标主机单播响应 → 写入 ARP 缓存，完成 IP 到 MAC 的映射" :player="player" :status-text="statusText" back-to="/knowledge/12">
    <template #extra>
      <span class="small muted">目标 IP</span>
      <el-select v-model="targetIp" size="small" style="width:130px" @change="player.reset()">
        <el-option v-for="h in hosts" :key="h.ip" :value="h.ip" :label="h.name + ' ' + h.ip" />
      </el-select>
      <el-button size="small" plain @click="player.reset()">重播</el-button>
    </template>

    <svg width="700" height="300" class="arp-svg">
      <!-- 总线 -->
      <line x1="60" y1="150" x2="640" y2="150" stroke="#8b95a3" stroke-width="4" />
      <text x="350" y="138" text-anchor="middle" font-size="11" fill="#8b95a3">以太网总线（广播域）</text>

      <!-- 广播波纹 -->
      <circle v-if="showBroadcast" :cx="hosts[0].x" cy="150" r="40" fill="none" stroke="#e8a13a" stroke-width="2" opacity="0.7">
        <animate attributeName="r" from="30" to="260" dur="1.1s" repeatCount="indefinite" />
        <animate attributeName="opacity" from="0.8" to="0" dur="1.1s" repeatCount="indefinite" />
      </circle>

      <!-- 主机 -->
      <g v-for="(h, i) in hosts" :key="h.ip">
        <line :x1="h.x" y1="150" :x2="h.x" y2="196" stroke="#c8d3e6" stroke-width="2" />
        <rect :x="h.x - 46" y="196" width="92" height="62" rx="8"
          :fill="hostFill(i)" :stroke="hostStroke(i)" stroke-width="2" />
        <text :x="h.x" y="216" text-anchor="middle" font-size="12" font-weight="600">{{ h.name }}</text>
        <text :x="h.x" y="232" text-anchor="middle" font-size="10" fill="#5a6472">{{ h.ip }}</text>
        <text :x="h.x" y="247" text-anchor="middle" font-size="10" fill="#8b95a3">{{ h.mac }}</text>
        <circle :cx="h.x" cy="196" r="4" :fill="hostStroke(i)" />
      </g>

      <!-- 报文 -->
      <g v-for="(p, i) in visiblePackets" :key="'p' + i">
        <line :x1="p.x1" :y1="110" :x2="p.x2" :y2="110" :stroke="p.color" stroke-width="2.4" marker-end="url(#arp-arrow)" />
        <rect :x="(p.x1 + p.x2) / 2 - 80" y="80" width="160" height="22" rx="5" :fill="p.bg" :stroke="p.color" />
        <text :x="(p.x1 + p.x2) / 2" y="95" text-anchor="middle" font-size="11" :fill="p.color" font-weight="600">{{ p.label }}</text>
      </g>
      <!-- 丢弃标记 -->
      <g v-for="(d, i) in drops" :key="'d' + i">
        <text :x="d.x" y="186" text-anchor="middle" font-size="14" fill="#e05252">✕</text>
      </g>
      <defs>
        <marker id="arp-arrow" markerWidth="9" markerHeight="9" refX="8" refY="3" orient="auto">
          <path d="M0,0 L8,3 L0,6 z" fill="#8b95a3" />
        </marker>
      </defs>
    </svg>

    <div class="arp-panel">
      <div class="panel-title">主机 A 的 ARP 高速缓存</div>
      <table class="atable">
        <thead><tr><th>IP 地址</th><th>MAC 地址</th><th>类型</th><th>TTL</th></tr></thead>
        <tbody>
          <tr v-for="(c, i) in cache" :key="i" :class="{ fresh: c.fresh }">
            <td>{{ c.ip }}</td><td>{{ c.mac }}</td><td>{{ c.type }}</td><td>{{ c.ttl }}</td>
          </tr>
          <tr v-if="!cache.length"><td colspan="4" class="muted">（缓存为空，需要发起 ARP 请求）</td></tr>
        </tbody>
      </table>
      <div class="tip small muted">
        要点：ARP 请求是<b>广播帧</b>（目的 MAC 全 F），ARP 响应是<b>单播帧</b>；跨网段时解析的是<b>默认网关</b>的 MAC。
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#e8a13a"></i> 广播 ARP 请求</span>
      <span><i class="dot" style="background:#22a06b"></i> 单播 ARP 响应</span>
      <span><i class="dot" style="background:#e05252"></i> 非目标主机丢弃</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const hosts = ref([
  { name: '主机 A', ip: '192.168.1.1', mac: 'AA-AA-AA-AA-AA-AA', x: 130 },
  { name: '主机 B', ip: '192.168.1.2', mac: 'BB-BB-BB-BB-BB-BB', x: 290 },
  { name: '主机 C', ip: '192.168.1.3', mac: 'CC-CC-CC-CC-CC-CC', x: 450 },
  { name: '主机 D', ip: '192.168.1.4', mac: 'DD-DD-DD-DD-DD-DD', x: 600 }
])
const targetIp = ref('192.168.1.2')
// 注意：targetIndex 必须声明在 steps 之前 —— steps 的 getter 里要用它，
// 以前声明在 usePlayer(steps) 之后，首次求值直接 TDZ 崩溃，整个动画页渲染成空白
const targetIndex = computed(() => hosts.value.findIndex(h => h.ip === targetIp.value))

const steps = computed(() => {
  const target = hosts.value.find(h => h.ip === targetIp.value) || hosts.value[1]
  const others = hosts.value.filter(h => h.ip !== targetIp.value && h.name !== '主机 A')
  return [
    {
      phase: 'check', cache: [], drops: [], packets: [], broadcast: false,
      desc: `主机 A 要给 ${target.ip} 发送 IP 数据报，先查本机 ARP 缓存 → 未命中，需要发起 ARP 请求`
    },
    {
      phase: 'request', cache: [], drops: [], broadcast: true,
      packets: [{ from: 0, to: 'all', label: 'ARP 请求（广播）', color: '#e8a13a', bg: '#fdf3e2' }],
      desc: `主机 A 发送广播 ARP 请求帧：「谁的 IP 是 ${target.ip}？请回复你的 MAC」，目的 MAC 为 FF-FF-FF-FF-FF-FF`
    },
    {
      phase: 'recv', cache: [], broadcast: true,
      packets: [{ from: 0, to: 'all', label: 'ARP 请求（广播）', color: '#e8a13a', bg: '#fdf3e2' }],
      drops: others.map(h => ({ x: h.x })),
      desc: `网段内所有主机都收到该广播帧，${others.map(h => h.name).join('、')} 发现目标 IP 不是自己 → 丢弃该帧`
    },
    {
      phase: 'reply', cache: [], drops: [], broadcast: false,
      // 端点必须跟着选中的目标走。曾经硬编码 from:1/to:0（永远是主机 B），
      // 于是切换到主机 C/D 时，文案说「主机 C 响应」，箭头却仍连在主机 B 上
      packets: [{ from: targetIndex.value, to: 0, label: 'ARP 响应（单播）', color: '#22a06b', bg: '#e6f6ee' }],
      desc: `${target.name} 识别出自己的 IP，向主机 A 单播 ARP 响应：我的 MAC 是 ${target.mac}`
    },
    {
      phase: 'cache', cache: [{ ip: target.ip, mac: target.mac, type: '动态', ttl: '120s', fresh: true }], drops: [], broadcast: false,
      packets: [],
      desc: `主机 A 收到响应，将 ${target.ip} → ${target.mac} 写入 ARP 高速缓存（有生存时间）`
    },
    {
      phase: 'send', cache: [{ ip: target.ip, mac: target.mac, type: '动态', ttl: '120s', fresh: true }], drops: [], broadcast: false,
      packets: [{ from: 0, to: targetIndex.value, label: '数据帧（目的MAC已知）', color: '#3b6ef6', bg: '#eef3ff' }],
      desc: `主机 A 用 ${target.mac} 封装 MAC 帧，直接单播发送数据 → ARP 解析完成`
    }
  ]
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const cache = computed(() => cur.value.cache || [])
const drops = computed(() => cur.value.drops || [])

const visiblePackets = computed(() =>
  (cur.value.packets || []).map(p => {
    const fromX = hosts.value[typeof p.from === 'number' ? p.from : 0].x
    const toX = p.to === 'all' ? 660 : hosts.value[p.to].x
    return { ...p, x1: fromX, x2: toX }
  })
)
const showBroadcast = computed(() => cur.value.broadcast)

function hostFill(i) {
  if (i === 0) return '#eef3ff'
  if (i === targetIndex.value) return '#e6f6ee'
  return '#fff'
}
function hostStroke(i) {
  if (i === 0) return '#3b6ef6'
  if (i === targetIndex.value) return '#22a06b'
  return '#c8d3e6'
}
</script>

<style scoped>
.arp-svg { background: #fbfcff; border-radius: 8px; display: block; }
.arp-panel { margin-top: 14px; }
.panel-title { font-size: 13px; font-weight: 600; margin-bottom: 8px; color: var(--text-2); }
.atable { width: 100%; border-collapse: collapse; font-size: 13px; }
.atable th, .atable td { border: 1px solid var(--border); padding: 6px 10px; text-align: left; }
.atable th { background: #f7f9fc; }
.atable tr.fresh { background: #dcf3e7; }
.tip { margin-top: 10px; line-height: 1.8; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
