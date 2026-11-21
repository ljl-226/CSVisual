<template>
  <VisFrame title="IP 路由转发 · 最长前缀匹配" desc="路由器逐跳转发：目的 IP 与掩码相与 → 匹配路由表 → 选择最长前缀的表项" :player="player" :status-text="statusText" back-to="/knowledge/11">
    <template #extra>
      <span class="small muted">目的 IP</span>
      <el-input v-model="destIp" size="small" style="width:130px" @change="player.reset()" />
      <el-button size="small" plain @click="player.reset()">重播</el-button>
    </template>

    <svg width="700" height="200" class="ip-svg">
      <!-- 链路 -->
      <line v-for="(l, i) in links" :key="i" :x1="l.x1" :y1="100" :x2="l.x2" :y2="100" stroke="#dde3ec" stroke-width="3" />
      <!-- 节点 -->
      <g v-for="(n, i) in nodes" :key="n.name">
        <rect :x="n.x - 52" y="66" width="104" height="68" rx="10"
          :fill="i === activeNode ? '#eef3ff' : '#fff'" :stroke="i === activeNode ? '#3b6ef6' : '#c8d3e6'" stroke-width="2" />
        <text :x="n.x" y="92" text-anchor="middle" font-size="13" font-weight="600" :fill="i === activeNode ? '#1a47b8' : '#1f2733'">{{ n.name }}</text>
        <text :x="n.x" y="110" text-anchor="middle" font-size="11" fill="#8b95a3">{{ n.ip }}</text>
        <text :x="n.x" y="126" text-anchor="middle" font-size="10" :fill="i === activeNode ? '#3b6ef6' : '#8b95a3'">{{ n.role }}</text>
        <!-- 网络号标签 -->
        <text :x="(n.x + (nodes[i + 1] ? nodes[i + 1].x : n.x + 60)) / 2" y="152" text-anchor="middle" font-size="10" fill="#8b95a3">
          {{ netLabel(i) }}
        </text>
      </g>
      <!-- 数据包 -->
      <g :transform="`translate(${packetX}, 100)`" style="transition: transform .5s ease">
        <circle r="18" fill="#e8a13a" stroke="#c9821f" stroke-width="2" />
        <text y="4" text-anchor="middle" font-size="10" fill="#fff" font-weight="700">IP</text>
        <text y="32" text-anchor="middle" font-size="10" fill="#8b95a3">TTL={{ ttl }}</text>
      </g>
    </svg>

    <div class="route-area">
      <div class="panel-title">当前节点路由表 <span class="muted">（{{ nodes[activeNode].name }}）</span></div>
      <table class="rtable">
        <thead>
          <tr><th>目的网络</th><th>子网掩码</th><th>下一跳</th><th>接口</th></tr>
        </thead>
        <tbody>
          <tr v-for="(r, i) in nodes[activeNode].routes" :key="i" :class="{ hit: i === hitIndex }">
            <td>{{ r.dest }}</td><td>{{ r.mask }}</td><td>{{ r.next }}</td><td>{{ r.iface }}</td>
          </tr>
        </tbody>
      </table>
      <div class="calc small" v-if="hitIndex >= 0">
        匹配结果：{{ destIp }} AND {{ nodes[activeNode].routes[hitIndex].mask }} = {{ andResult }} → 命中「{{ nodes[activeNode].routes[hitIndex].dest }}」，
        下一跳 {{ nodes[activeNode].routes[hitIndex].next }}
      </div>
      <div class="calc small muted" v-else>未命中任何具体表项 → 使用默认路由 0.0.0.0/0</div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#e8a13a"></i> IP 数据报</span>
      <span><i class="dot" style="background:#3b6ef6"></i> 当前处理节点</span>
      <span><i class="dot" style="background:#dcf3e7"></i> 命中的路由表项</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const destIp = ref('192.168.3.10')

const nodes = ref([
  {
    name: '主机 A', ip: '192.168.1.10', role: '源主机', x: 90,
    routes: [
      { dest: '192.168.1.0', mask: '255.255.255.0', next: '—（直连）', iface: 'eth0' },
      { dest: '0.0.0.0/0', mask: '0.0.0.0', next: '192.168.1.1', iface: 'eth0' }
    ]
  },
  {
    name: '路由器 R1', ip: '192.168.1.1', role: '路由器', x: 280,
    routes: [
      { dest: '192.168.1.0', mask: '255.255.255.0', next: '—（直连）', iface: 'E0' },
      { dest: '192.168.2.0', mask: '255.255.255.0', next: '—（直连）', iface: 'E1' },
      { dest: '192.168.3.0', mask: '255.255.255.0', next: '192.168.2.2', iface: 'E1' }
    ]
  },
  {
    name: '路由器 R2', ip: '192.168.2.2', role: '路由器', x: 470,
    routes: [
      { dest: '192.168.2.0', mask: '255.255.255.0', next: '—（直连）', iface: 'E0' },
      { dest: '192.168.3.0', mask: '255.255.255.0', next: '—（直连）', iface: 'E1' }
    ]
  },
  {
    name: '主机 B', ip: '192.168.3.10', role: '目的主机', x: 640,
    routes: [
      { dest: '192.168.3.0', mask: '255.255.255.0', next: '—（直连）', iface: 'eth0' },
      { dest: '0.0.0.0/0', mask: '0.0.0.0', next: '192.168.3.1', iface: 'eth0' }
    ]
  }
])

const links = computed(() => {
  const out = []
  for (let i = 0; i < nodes.value.length - 1; i++) {
    out.push({ x1: nodes.value[i].x + 52, x2: nodes.value[i + 1].x - 52 })
  }
  return out
})

function netLabel(i) {
  const nets = ['192.168.1.0/24', '192.168.2.0/24', '192.168.3.0/24', '']
  return nets[i] || ''
}

function ipToNum(ip) {
  return ip.split('.').map(Number)
}
function andIp(ip, mask) {
  const a = ipToNum(ip)
  const m = ipToNum(mask)
  return a.map((x, i) => x & m[i]).join('.')
}

const steps = computed(() => {
  const out = []
  const dst = destIp.value
  out.push({ node: 0, ttl: 64, hit: -1, desc: `源主机 A 构造 IP 数据报：目的 IP = ${dst}，TTL 初始值 64，查本机路由表` })
  out.push({ node: 0, ttl: 64, hit: findHit(0, dst), desc: `目的 IP 与掩码相与不在本网段 → 命中默认路由，交给默认网关 192.168.1.1（R1）` })
  out.push({ node: 1, ttl: 63, hit: -1, desc: `R1 收到数据报，TTL 减 1 变为 63，提取目的 IP 查路由表` })
  out.push({ node: 1, ttl: 63, hit: findHit(1, dst), desc: `R1 最长前缀匹配命中 192.168.3.0/24 → 下一跳 192.168.2.2（R2），从 E1 接口转发` })
  out.push({ node: 2, ttl: 62, hit: -1, desc: `R2 收到数据报，TTL 减 1 变为 62，查路由表` })
  out.push({ node: 2, ttl: 62, hit: findHit(2, dst), desc: `R2 发现 192.168.3.0/24 是直连网络 → 直接交付给目的主机 B，无需再转发` })
  out.push({ node: 3, ttl: 62, hit: -1, desc: `主机 B 收到数据报，目的 IP 与本机一致 → 接收并交给上层协议，转发完成` })
  return out
})

function findHit(nodeIndex, dst) {
  const routes = nodes.value[nodeIndex].routes
  let best = -1
  let bestLen = -1
  routes.forEach((r, i) => {
    const mask = r.mask.includes('/') ? r.mask : r.mask
    if (mask === '0.0.0.0') return
    if (andIp(dst, mask) === r.dest) {
      const len = ipToNum(mask).reduce((s, x) => s + (x === 255 ? 8 : 0), 0)
      if (len > bestLen) { bestLen = len; best = i }
    }
  })
  if (best === -1) {
    const defIdx = routes.findIndex(r => r.mask === '0.0.0.0' || r.dest === '0.0.0.0/0')
    return defIdx
  }
  return best
}

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const activeNode = computed(() => cur.value.node || 0)
const ttl = computed(() => cur.value.ttl ?? 64)
const hitIndex = computed(() => cur.value.hit ?? -1)
const packetX = computed(() => nodes.value[activeNode.value].x)

const andResult = computed(() => {
  if (hitIndex.value < 0) return '-'
  const r = nodes.value[activeNode.value].routes[hitIndex.value]
  return andIp(destIp.value, r.mask)
})
</script>

<style scoped>
.ip-svg { background: #fbfcff; border-radius: 8px; display: block; }
.route-area { margin-top: 14px; }
.panel-title { font-size: 13px; font-weight: 600; margin-bottom: 8px; color: var(--text-2); }
.rtable { width: 100%; border-collapse: collapse; font-size: 13px; }
.rtable th, .rtable td { border: 1px solid var(--border); padding: 6px 10px; text-align: left; }
.rtable th { background: #f7f9fc; font-weight: 600; }
.rtable tr.hit { background: #dcf3e7; }
.rtable tr.hit td { color: #176b48; font-weight: 600; }
.calc { margin-top: 8px; padding: 8px 10px; background: #f7f9fc; border-radius: 6px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
