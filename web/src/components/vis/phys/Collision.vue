<template>
  <VisFrame title="碰撞 · 动量守恒与能量损失" desc="碰撞过程内力远大于外力，系统总动量守恒；动能是否守恒取决于恢复系数 e：完全弹性 e = 1 无损失，完全非弹性 e = 0 共速且动能损失最大" :player="player" :status-text="statusText" back-to="/knowledge/63">
    <template #extra>
      <el-radio-group v-model="mode" size="small" @change="player.reset()">
        <el-radio-button value="1d">一维正碰</el-radio-button>
        <el-radio-button value="2d">二维斜碰</el-radio-button>
      </el-radio-group>
      <el-select v-model="typeKey" size="small" style="width:130px" @change="player.reset()">
        <el-option v-for="t in TYPES" :key="t.key" :value="t.key" :label="t.label" />
      </el-select>
      <span class="small muted">m₁ {{ m1 }}kg</span>
      <el-slider v-model="m1" :min="0.5" :max="5" :step="0.5" style="width:80px" :show-tooltip="false" @change="player.reset()" />
      <span class="small muted">m₂ {{ m2 }}kg</span>
      <el-slider v-model="m2" :min="0.5" :max="5" :step="0.5" style="width:80px" :show-tooltip="false" @change="player.reset()" />
      <span class="small muted">v₁ {{ v1x }}m/s</span>
      <el-slider v-model="v1x" :min="-6" :max="8" :step="0.5" style="width:80px" :show-tooltip="false" @change="player.reset()" />
      <span class="small muted">v₂ {{ v2x }}m/s</span>
      <el-slider v-model="v2x" :min="-8" :max="6" :step="0.5" style="width:80px" :show-tooltip="false" @change="player.reset()" />
    </template>
    <div class="cl-wrap">
      <svg :width="W" :height="H" class="cl-svg">
        <line x1="20" :y1="OY" :x2="W - 20" :y2="OY" stroke="#c8d3e6" stroke-dasharray="4 4" />
        <!-- 碰撞瞬间（t ≥ tc）画出连心线，即法向 n -->
        <line v-if="cur.hit <= cur.t" :x1="px(cur.p1[0])" :y1="py(cur.p1[1])" :x2="px(cur.p2[0])" :y2="py(cur.p2[1])" stroke="#8b95a3" stroke-width="1.5" stroke-dasharray="6 4" />
        <g v-for="(b, i) in bodies" :key="'b' + i">
          <line :x1="px(b.p[0])" :y1="py(b.p[1])" :x2="px(b.p[0]) + b.v[0] * VPX" :y2="py(b.p[1]) - b.v[1] * VPX" :stroke="b.color" stroke-width="2.5" />
          <circle :cx="px(b.p[0])" :cy="py(b.p[1])" :r="R * SCALE" :fill="b.fill" :stroke="b.color" stroke-width="2.5" />
          <text :x="px(b.p[0])" :y="py(b.p[1]) + 4" font-size="11" text-anchor="middle" :fill="b.color" font-weight="700">m{{ i + 1 }}</text>
        </g>
        <!-- 动能条：外框为碰前基准，实心为当前总动能 -->
        <text x="20" y="286" font-size="11" fill="#8b95a3">系统总动能（亮色为碰前基准）</text>
        <rect x="20" y="294" :width="Math.max(2, (K0 / 60) * 420)" height="14" fill="#cfe0ff" stroke="#3b6ef6" />
        <rect x="20" y="294" :width="Math.max(2, (cur.K / 60) * 420)" height="14" :fill="eVal === 1 ? '#22a06b' : '#e8a13a'" />
        <text x="20" y="326" font-size="11.5" fill="#5b6472">Ek：{{ fmt(cur.K) }} J / 初始 {{ fmt(K0) }} J（损失 {{ lossPct }}%）</text>
      </svg>
      <div class="cl-panel">
        <div class="def-box"><div class="small muted">教材公式（《大学物理》动量与碰撞）</div><code>动量守恒：m₁v₁ + m₂v₂ = m₁v₁' + m₂v₂'
恢复系数：e = |v₂' - v₁'| / |v₁ - v₂|（e = 1 完全弹性，e = 0 完全非弹性共速）</code></div>
        <el-divider />
        <div class="info-row"><span>碰撞类型 / 恢复系数 e</span><b>{{ typeName }} / {{ eVal }}</b></div>
        <div class="info-row"><span>碰前速度 v₁ , v₂</span><b>({{ fmtVec(v1) }}, {{ fmtVec(v2) }}) m/s</b></div>
        <div class="info-row"><span>碰后速度 v₁' , v₂'</span><b style="color:var(--brand)">({{ fmtVec(cur.w1) }}, {{ fmtVec(cur.w2) }}) m/s</b></div>
        <div class="info-row"><span>系统总动量 p = Σmv</span><b style="color:var(--success)">({{ fmt(mom[0], 3) }}, {{ fmt(mom[1], 3) }}) kg·m/s</b></div>
        <div class="info-row"><span>动量是否守恒</span><el-tag size="small" type="success">是（{{ Math.abs(momErr) < 1e-6 ? '误差 0' : '数值舍入内' }}）</el-tag></div>
        <div class="info-row"><span>碰前动能 Ek</span><b>{{ fmt(K0) }} J</b></div>
        <div class="info-row"><span>碰后动能 Ek'</span><b style="color:#a5701a">{{ fmt(cur.K) }} J</b></div>
        <div class="info-row"><span>动能损失</span><el-tag size="small" :type="K0 - cur.K < 1e-6 ? 'success' : 'warning'">{{ fmt(K0 - cur.K) }} J（{{ lossPct }}%）</el-tag></div>
        <p class="small muted tip">考点：完全弹性碰撞动能守恒，可联立动量守恒与动能守恒求解；完全非弹性碰撞后两物共速（等于质心速度），此时动能损失最大；二维碰撞只在连心线（法向）上交换动量，切向分量保持不变。</p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> 物体 m₁（含速度矢量）</span>
      <span><i class="dot" style="background:#e05252"></i> 物体 m₂（含速度矢量）</span>
      <span><i class="dot" style="background:#8b95a3"></i> 碰撞瞬间连心线（法向 n）</span>
      <span><i class="dot" style="background:#cfe0ff"></i> 碰前动能基准</span>
    </template>
  </VisFrame>
</template>
<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'
const TYPES = [
  { key: 'elastic', label: '完全弹性 e = 1', e: 1 },
  { key: 'partial', label: '非弹性 e = 0.5', e: 0.5 },
  { key: 'inelastic', label: '完全非弹性 e = 0', e: 0 }
]
const mode = ref('1d')
const typeKey = ref('elastic')
const m1 = ref(2)
const m2 = ref(1)
const v1x = ref(4)
const v2x = ref(-3)
const curType = computed(() => TYPES.find(t => t.key === typeKey.value) || TYPES[0])
const eVal = computed(() => curType.value.e)
const typeName = computed(() => curType.value.label.split(' ')[0])
const W = 520, H = 340, SCALE = 26, VPX = 14 // 米 → 像素；速度箭头每 m/s 的像素数
const OX = 260, OY = 150
const R = 0.5 // 半径（米）
const T_END = 1.8, NFRAME = 30
function px(X) { return OX + X * SCALE }
function py(Y) { return OY - Y * SCALE }
// 构造场景：一维正碰沿 x 轴；二维斜碰通过「反推初始间距」保证两球必定相撞
function scene() {
  const v1 = [v1x.value, 0], v2 = [v2x.value, 0]
  if (mode.value === '1d') return { p1: [-4.5, 0], p2: [2.4, 0], v1, v2 }
  const v1t = [v1x.value, 0.35 * Math.abs(v1x.value) + 1.2]
  const v2t = [v2x.value, -0.4 * Math.abs(v2x.value) - 0.8]
  const w = [v1t[0] - v2t[0], v1t[1] - v2t[1]]
  const tc = 0.45
  // 取接近方向旋转一个小角度作为碰撞法线（保证冲击参数非零，形成散射）
  const ang = Math.atan2(-w[1], -w[0]) + 0.42
  // 由期望的碰撞时刻反推初始相对位置，再平移成关于画面中心对称（平移不影响碰撞时刻）
  const d0 = [2 * R * Math.cos(ang) - w[0] * tc, 2 * R * Math.sin(ang) - w[1] * tc]
  return { p1: [d0[0] / 2, d0[1] / 2], p2: [-d0[0] / 2, -d0[1] / 2], v1: v1t, v2: v2t }
}
const v1 = computed(() => scene().v1)
const v2 = computed(() => scene().v2)
// 求解碰撞时刻：|p₁(t) - p₂(t)| = 2R 的最小正根
function hitTime(s) {
  const d = [s.p1[0] - s.p2[0], s.p1[1] - s.p2[1]]
  const w = [s.v1[0] - s.v2[0], s.v1[1] - s.v2[1]]
  const a = w[0] * w[0] + w[1] * w[1]
  if (a < 1e-9) return null
  const b = 2 * (d[0] * w[0] + d[1] * w[1])
  const c = d[0] * d[0] + d[1] * d[1] - 4 * R * R
  const disc = b * b - 4 * a * c
  if (disc < 0) return null
  const sq = Math.sqrt(disc)
  const roots = [(-b - sq) / (2 * a), (-b + sq) / (2 * a)].filter(t => t > 1e-6).sort((x, y) => x - y)
  return roots.length ? roots[0] : null
}

// 碰撞后的速度：法向上按恢复系数重分配，切向分量不变（e = 0 时整体共速）
function postVel(s, nrm) {
  const M = m1.value + m2.value
  const dot = (v, n) => v[0] * n[0] + v[1] * n[1]
  // e = 0：完全非弹性，碰后共速（等于质心速度），此时动能损失最大
  const com = [(m1.value * s.v1[0] + m2.value * s.v2[0]) / M, (m1.value * s.v1[1] + m2.value * s.v2[1]) / M]
  if (eVal.value === 0) return [com[0], com[1], com[0], com[1]]
  const u1 = dot(s.v1, nrm), u2 = dot(s.v2, nrm)
  const u1p = ((m1.value - eVal.value * m2.value) * u1 + m2.value * (1 + eVal.value) * u2) / M
  const u2p = ((m2.value - eVal.value * m1.value) * u2 + m1.value * (1 + eVal.value) * u1) / M
  return [
    s.v1[0] + (u1p - u1) * nrm[0], s.v1[1] + (u1p - u1) * nrm[1],
    s.v2[0] + (u2p - u2) * nrm[0], s.v2[1] + (u2p - u2) * nrm[1]
  ]
}
function kinetic(a, b) { return 0.5 * m1.value * (a[0] * a[0] + a[1] * a[1]) + 0.5 * m2.value * (b[0] * b[0] + b[1] * b[1]) }
const K0 = computed(() => kinetic(v1.value, v2.value))
const mom = computed(() => [m1.value * v1.value[0] + m2.value * v2.value[0], m1.value * v1.value[1] + m2.value * v2.value[1]])
const steps = computed(() => {
  const s = scene()
  const tc = hitTime(s)
  const out = []
  const dt = T_END / NFRAME
  let w1v = s.v1, w2v = s.v2, np1 = null, np2 = null, nc = null
  if (tc !== null) {
    np1 = [s.p1[0] + s.v1[0] * tc, s.p1[1] + s.v1[1] * tc]
    np2 = [s.p2[0] + s.v2[0] * tc, s.p2[1] + s.v2[1] * tc]
    // 碰撞法线 = 接触瞬间的连心线方向
    const nrm = [(np1[0] - np2[0]) / (2 * R), (np1[1] - np2[1]) / (2 * R)]
    const post = postVel(s, nrm)
    w1v = [post[0], post[1]]; w2v = [post[2], post[3]]; nc = tc
  }
  for (let j = 0; j <= NFRAME; j++) {
    const t = Number((j * dt).toFixed(3))
    let p1, p2, cv1, cv2, note
    if (nc !== null && t >= nc) {
      p1 = [np1[0] + w1v[0] * (t - nc), np1[1] + w1v[1] * (t - nc)]
      p2 = [np2[0] + w2v[0] * (t - nc), np2[1] + w2v[1] * (t - nc)]
      cv1 = w1v; cv2 = w2v
      note = t - nc < dt + 1e-9
        ? `碰撞完成（t = ${t}s）：恢复系数 e = ${eVal.value}，碰后 v₁' = (${w1v[0].toFixed(2)}, ${w1v[1].toFixed(2)})，v₂' = (${w2v[0].toFixed(2)}, ${w2v[1].toFixed(2)})，动能 ${K0.value.toFixed(2)} → ${kinetic(w1v, w2v).toFixed(2)} J`
        : `碰后分离（t = ${t}s）：系统总动量仍为 (${mom.value[0].toFixed(2)}, ${mom.value[1].toFixed(2)}) kg·m/s，动能保持 ${kinetic(w1v, w2v).toFixed(2)} J`
    } else {
      p1 = [s.p1[0] + s.v1[0] * t, s.p1[1] + s.v1[1] * t]
      p2 = [s.p2[0] + s.v2[0] * t, s.p2[1] + s.v2[1] * t]
      cv1 = s.v1; cv2 = s.v2
      note = j === 0
        ? `初始状态：p = (${mom.value[0].toFixed(2)}, ${mom.value[1].toFixed(2)}) kg·m/s，Ek = ${K0.value.toFixed(2)} J${nc === null ? '，两球在本时段内不会相遇' : ''}`
        : `碰撞前（t = ${t}s）：两球各自匀速，间距缩小，总动量守恒不变`
    }
    out.push({ j, t, p1, p2, w1: cv1, w2: cv2, K: kinetic(cv1, cv2), hit: nc === null ? Infinity : nc, desc: note })
  }
  return out
})
const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const lossPct = computed(() => (K0.value > 0 ? (((K0.value - cur.value.K) / K0.value) * 100).toFixed(1) : '0.0'))
const momErr = computed(() => Math.hypot(m1.value * cur.value.w1[0] + m2.value * cur.value.w2[0] - mom.value[0], m1.value * cur.value.w1[1] + m2.value * cur.value.w2[1] - mom.value[1]))
const bodies = computed(() => [
  { p: cur.value.p1, v: cur.value.w1, color: '#3b6ef6', fill: '#dbe6ff' },
  { p: cur.value.p2, v: cur.value.w2, color: '#e05252', fill: '#fdeaea' }
])
function fmt(v, d) { return (v === null || v === undefined || !isFinite(v)) ? '-' : Number(v.toFixed(d === undefined ? 2 : d)).toString() }
function fmtVec(v) { return `(${v.map(x => Number(x.toFixed(2))).join(', ')})` }
</script>

<style scoped>
.cl-wrap { display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap; }
.cl-svg { background: #fcfdff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.cl-panel { flex: 1; min-width: 300px; }
.def-box code { background: #f2f4f8; padding: 8px 10px; border-radius: 6px; display: block; font-size: 12px; line-height: 1.7; white-space: pre-wrap; }
.info-row { display: flex; justify-content: space-between; align-items: center; gap: 10px; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.tip { margin-top: 10px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
