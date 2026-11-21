<template>
  <VisFrame
    title="子网划分与 CIDR"
    desc="IP 地址逐位与子网掩码做 AND 运算得到网络号，剩余主机位全 1 即广播地址"
    :player="player" :status-text="statusText" back-to="/knowledge/41"
  >
    <template #extra>
      <el-input v-model="input" size="small" style="width:170px" placeholder="如 192.168.1.0/26" />
      <el-button size="small" @click="applyInput">应用</el-button>
      <el-button size="small" plain @click="resetInput">重置</el-button>
    </template>

    <div class="sn-wrap">
      <svg width="660" height="390" class="sn-svg">
        <text x="140" y="14" font-size="11" fill="#8b95a3">每格自上而下：IP 位 · 掩码位 · AND 结果（逐位演示 IP ∧ 掩码）</text>

        <g v-for="(row, r) in rows" :key="'r' + r">
          <text x="128" :y="row.y + 38" text-anchor="end" font-size="12" fill="#8b95a3">{{ row.label }}</text>
          <g v-for="(c, i) in row.cells" :key="i">
            <rect :x="c.x" :y="row.y" width="52" height="64" rx="6" :fill="c.bg" :stroke="c.stroke" stroke-width="1.4" />
            <text :x="c.x + 26" :y="row.y + 20" text-anchor="middle" font-size="15" font-weight="700" fill="#1f2733">{{ c.ip }}</text>
            <text :x="c.x + 26" :y="row.y + 38" text-anchor="middle" font-size="13" fill="#8b95a3">{{ c.mask }}</text>
            <line :x1="c.x + 6" :y1="row.y + 45" :x2="c.x + 46" :y2="row.y + 45" :stroke="c.stroke" stroke-width="1" />
            <text :x="c.x + 26" :y="row.y + 60" text-anchor="middle" font-size="15" font-weight="700" :fill="c.rc">{{ c.res }}</text>
          </g>
        </g>
        <!-- 网络号 / 主机号分界线（第 bits 位之后） -->
        <line v-if="divider" :x1="divider.x" :y1="divider.y" :x2="divider.x" :y2="divider.y + 64" stroke="#e05252" stroke-width="1.6" stroke-dasharray="4 3" />
        <text v-if="divider" :x="divider.x + 4" :y="divider.y - 4" font-size="11" fill="#e05252">网络号 | 主机号</text>
      </svg>

      <div class="sn-panel">
        <div class="info-row"><span>CIDR 前缀</span><b style="color:var(--brand)">/{{ info.bits }}</b></div>
        <div class="info-row" :class="{ 'row-focus': cur.focus === 'ip' }"><span>IP 地址</span><b>{{ info.host }}</b></div>
        <div class="info-row" :class="{ 'row-focus': cur.focus === 'mask' }"><span>子网掩码</span><b>{{ info.mask }}</b></div>
        <div class="info-row" :class="{ 'row-focus': cur.focus === 'net' }"><span>网络号（AND 结果）</span><b style="color:var(--brand)">{{ info.net }}</b></div>
        <div class="info-row" :class="{ 'row-focus': cur.focus === 'bc' }"><span>广播地址</span><b style="color:var(--danger)">{{ info.bc }}</b></div>
        <div class="info-row" :class="{ 'row-focus': cur.focus === 'range' }"><span>可用主机范围</span><b>{{ info.first }} ~ {{ info.last }}</b></div>
        <div class="info-row" :class="{ 'row-focus': cur.focus === 'avail' }"><span>子网主机数 / 可用</span><b>{{ info.size }} / {{ info.avail }}</b></div>
        <div class="info-row" :class="{ 'row-focus': cur.focus === 'range' }"><span>可划分子网数</span><b>{{ info.subnets }}</b></div>
        <div class="info-row"><span>已计算位数</span><b>{{ cur.k }} / 32</b></div>
        <el-divider />
        <div class="panel-title">教材要点</div>
        <ul class="points">
          <li>两级 IP：网络号 = IP ∧ 掩码；主机号全 0 代表本网络，全 1 为该子网广播地址</li>
          <li>/n 表示前 n 位为网络号，主机号共 {{ 32 - info.bits }} 位，可用主机 = 2<sup>{{ 32 - info.bits }}</sup> − 2</li>
          <li>子网数 = 2<sup>n − {{ info.base }}</sup>（{{ info.base }} 为该地址默认掩码位数，即分类编址的 A/B/C 类）</li>
          <li>CIDR 支持路由聚合（超网），可缩小路由表项</li>
        </ul>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> 网络号位（掩码 1）</span>
      <span><i class="dot" style="background:#e8a13a"></i> 主机号位（掩码 0）</span>
      <span><i class="dot" style="background:#e05252"></i> 网络号 / 主机号分界</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const DEFAULT = '192.168.1.0/26'
const input = ref(DEFAULT)
const cidr = ref(DEFAULT)

// 解析 CIDR 前缀，非法输入一律兜底回默认值（0~30 位保证至少 4 个地址）
function parseCidr(str) {
  const m = String(str || '').trim().match(/^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\/(\d{1,2})$/)
  let host = '192.168.1.0'
  let bits = 26
  if (m) {
    const parts = m.slice(1, 5).map(Number)
    const ok = parts.every(v => v >= 0 && v <= 255)
    const b = Number(m[5])
    if (ok && b >= 0 && b <= 30) { host = parts.join('.'); bits = b }
  }
  return { host, bits }
}
function toInt(ip) { return ip.split('.').reduce((acc, o) => ((acc << 8) | Number(o)), 0) >>> 0 }
function toStr(n) { return [(n >>> 24) & 255, (n >>> 16) & 255, (n >>> 8) & 255, n & 255].join('.') }

const info = computed(() => {
  const { host, bits } = parseCidr(cidr.value)
  const ipInt = toInt(host)
  const maskInt = bits === 0 ? 0 : (0xffffffff << (32 - bits)) >>> 0
  const netInt = (ipInt & maskInt) >>> 0
  const bcInt = (netInt | ((~maskInt) >>> 0)) >>> 0
  const hb = 32 - bits
  const size = Math.pow(2, hb)
  const firstOctet = Number(host.split('.')[0])
  const base = firstOctet < 128 ? 8 : firstOctet < 192 ? 16 : 24
  // 逐位拆成 32 个二进制位，供模板按位高亮
  const ipBits = []; const maskBits = []; const resBits = []
  for (let i = 0; i < 32; i++) {
    const b = 1 << (31 - i)
    ipBits.push((ipInt & b) ? 1 : 0)
    maskBits.push((maskInt & b) ? 1 : 0)
    resBits.push((netInt & b) ? 1 : 0)
  }
  return {
    host, bits, ipBits, maskBits, resBits, base,
    mask: toStr(maskInt), net: toStr(netInt), bc: toStr(bcInt),
    size, avail: size - 2,
    first: toStr((netInt + 1) >>> 0), last: toStr((bcInt - 1) >>> 0),
    subnets: bits >= base ? Math.pow(2, bits - base) : '不支持'
  }
})

const steps = computed(() => {
  const f = info.value
  const out = []
  function snap(desc, extra = {}) { out.push({ k: 0, desc, ...extra }) }

  // focus 标记当前讲解落在哪一行：这几步数据相同，靠它才能在画面上区分，
  // 否则连续 5 帧看上去一模一样。
  snap(`输入 ${f.host}/${f.bits}：开始逐位做 IP ∧ 掩码运算求网络号`, { k: 0, focus: 'ip' })
  snap(`子网掩码写成二进制：前 ${f.bits} 位全 1，后 ${32 - f.bits} 位全 0，即 ${f.mask}`, { k: 0, focus: 'mask' })
  // 逐位 AND：靠近格子的演示，每步揭示一位
  for (let i = 0; i < 32; i++) {
    const part = i < f.bits ? '网络号位（结果随 IP 位）' : '主机号位（掩码为 0，结果必为 0）'
    snap(`第 ${i + 1} 位：IP 位 ${f.ipBits[i]} ∧ 掩码位 ${f.maskBits[i]} = ${f.resBits[i]} —— ${part}`, { k: i + 1 })
  }
  snap(`32 位全部算完：网络号 = ${f.net}/${f.bits}（网络号 + 全 0 主机号）`, { k: 32, focus: 'net' })
  snap(`把主机号全部置 1：得到本子网的直接广播地址 ${f.bc}`, { k: 32, focus: 'bc' })
  snap(`主机号既非全 0 也非全 1 的地址才能分配给主机，共 2^${32 - f.bits} − 2 = ${f.avail} 个`, { k: 32, focus: 'avail' })
  snap(`可用地址范围 ${f.first} ~ ${f.last}；按 /${f.base} 默认掩码可划分出 ${f.subnets} 个子网`, { k: 32, focus: 'range' })
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)

const rows = computed(() => {
  const f = info.value
  const k = cur.value.k || 0
  const out = []
  for (let r = 0; r < 4; r++) {
    const cells = []
    for (let c = 0; c < 8; c++) {
      const idx = r * 8 + c
      const shown = idx < k
      const isNet = idx < f.bits
      cells.push({
        x: 140 + c * 56,
        ip: shown ? f.ipBits[idx] : '',
        mask: shown ? f.maskBits[idx] : '',
        res: shown ? f.resBits[idx] : '',
        bg: shown ? (isNet ? '#eef3ff' : '#fdf3e2') : '#fff',
        stroke: shown ? (isNet ? '#3b6ef6' : '#e8a13a') : '#e3e8ef',
        rc: shown ? (isNet ? '#1a47b8' : '#a5701a') : '#c8d3e6'
      })
    }
    out.push({ y: 26 + r * 78, label: `第${r + 1}字节`, cells })
  }
  return out
})

// 网络号与主机号的分界竖线（仅位于掩码过渡所在的那一字节行）
const divider = computed(() => {
  const b = info.value.bits
  if (b <= 0 || b >= 32) return null
  const idx = b - 1
  const r = Math.floor(idx / 8)
  const c = idx % 8
  return { x: 140 + c * 56 + 56, y: 26 + r * 78 }
})

function applyInput() {
  cidr.value = String(input.value || DEFAULT).trim()
  player.reset()
}
function resetInput() {
  input.value = DEFAULT
  cidr.value = DEFAULT
  player.reset()
}
</script>

<style scoped>
.sn-wrap { display: flex; gap: 24px; align-items: flex-start; flex-wrap: wrap; }
.sn-svg { background: #fbfcff; border-radius: 8px; flex-shrink: 0; }
.sn-panel { flex: 1; min-width: 260px; }
.panel-title { font-size: 13px; font-weight: 600; margin-bottom: 6px; color: var(--text-2); }
.info-row { display: flex; justify-content: space-between; gap: 10px; padding: 4px 6px; font-size: 13px; border-bottom: 1px dashed #f0f2f6; border-radius: 6px; transition: background 0.25s, box-shadow 0.25s; }
.info-row.row-focus {
  background: var(--brand-light);
  box-shadow: inset 3px 0 0 var(--brand);
  font-weight: 600;
}
.points { padding-left: 18px; margin: 0; }
.points li { font-size: 12px; line-height: 1.9; color: var(--text-2); }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
