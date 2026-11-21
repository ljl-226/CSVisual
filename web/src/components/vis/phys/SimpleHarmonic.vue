<template>
  <VisFrame title="简谐振动 · 旋转矢量法与弹簧振子" desc="匀速转动的矢量在 x 轴上的投影，正是简谐振动的位移 x = A·cos(ωt+φ)" :player="player" :status-text="statusText" back-to="/knowledge/30">
    <template #extra>
      <span class="small muted">A</span>
      <el-slider v-model="amp" :min="0.4" :max="2" :step="0.1" style="width:100px" :show-tooltip="false" @input="player.reset()" />
      <span class="small muted">ω</span>
      <el-slider v-model="omega" :min="0.5" :max="3" :step="0.1" style="width:100px" :show-tooltip="false" @input="player.reset()" />
      <span class="small muted">φ</span>
      <el-slider v-model="phi" :min="0" :max="6.28" :step="0.1" style="width:100px" :show-tooltip="false" @input="player.reset()" />
    </template>

    <div class="sh-wrap">
      <svg :width="W" :height="H" class="sh-svg">
        <!-- ===== 左：参考圆 ===== -->
        <g>
          <text :x="20" :y="20" font-size="12" fill="#8b95a3">参考圆（旋转矢量法）</text>
          <circle :cx="cx" :cy="cy" :r="R" fill="none" stroke="#c8d3e6" stroke-width="1.5" />
          <line :x1="cx - R - 14" :y1="cy" :x2="cx + R + 14" :y2="cy" stroke="#8b95a3" stroke-width="1" />
          <line :x1="cx" :y1="cy - R - 12" :x2="cx" :y2="cy + R + 12" stroke="#8b95a3" stroke-width="1" />
          <!-- 相位角扇形 -->
          <path :d="arcPath" fill="#3b6ef6" fill-opacity="0.12" />
          <!-- 旋转矢量 -->
          <line :x1="cx" :y1="cy" :x2="cx + R * Math.cos(cur.phase)" :y2="cy - R * Math.sin(cur.phase)" stroke="#3b6ef6" stroke-width="3" />
          <circle :cx="cx + R * Math.cos(cur.phase)" :cy="cy - R * Math.sin(cur.phase)" r="6" fill="#3b6ef6" />
          <!-- 投影线 -->
          <line :x1="cx + R * Math.cos(cur.phase)" :y1="cy - R * Math.sin(cur.phase)" :x2="cx + R * Math.cos(cur.phase)" :y2="cy" stroke="#e05252" stroke-dasharray="4 3" />
          <circle :cx="cx + R * Math.cos(cur.phase)" :cy="cy" r="5" fill="#e05252" />
          <text :x="cx + 12" :y="cy + 26" font-size="11" fill="#e05252">x = {{ fmt(cur.x) }} m</text>
          <text :x="cx + R * Math.cos(cur.phase) + 8" :y="cy - R * Math.sin(cur.phase) - 8" font-size="11" fill="#3b6ef6">A</text>
          <text :x="cx + 16" :y="cy - 14" font-size="11" fill="#3b6ef6">ωt+φ = {{ fmt(cur.phase) }} rad</text>
        </g>

        <!-- ===== 右：x-t 曲线 ===== -->
        <g>
          <text :x="gx0" :y="20" font-size="12" fill="#8b95a3">位移—时间曲线</text>
          <line :x1="gx0" :y1="gyc" :x2="gx1" :y2="gyc" stroke="#8b95a3" stroke-width="1" />
          <line :x1="gx0" :y1="gyc - ampPx - 6" :x2="gx0" :y2="gyc + ampPx + 6" stroke="#8b95a3" stroke-width="1" />
          <path :d="xtPath" fill="none" stroke="#22a06b" stroke-width="2" />
          <path :d="xtFlown" fill="none" stroke="#f2994a" stroke-width="3" />
          <circle :cx="gmapT(cur.t)" :cy="gmapX(cur.x)" r="6" fill="#f2994a" />
          <text :x="gx1 - 4" :y="gyc - ampPx - 10" text-anchor="end" font-size="10" fill="#8b95a3">+A = {{ fmt(amp) }}</text>
          <text :x="gx1 - 4" :y="gyc + ampPx + 18" text-anchor="end" font-size="10" fill="#8b95a3">-A</text>
          <text :x="gx1 - 4" :y="gyc - 8" text-anchor="end" font-size="10" fill="#8b95a3">t / s（共 {{ fmt(2 * period) }} s = 2 个周期）</text>
        </g>

        <!-- ===== 下：弹簧振子 ===== -->
        <g>
          <rect :x="wallX - 10" :y="springY - 22" width="10" height="44" fill="#8b95a3" />
          <path :d="springPath" fill="none" stroke="#8b95a3" stroke-width="2" />
          <rect :x="massX" :y="springY - 18" width="32" height="36" rx="4" fill="#3b6ef6" />
          <text :x="massX + 16" :y="springY + 5" text-anchor="middle" font-size="12" fill="#fff" font-weight="700">m</text>
          <line :x1="eqX" :y1="springY + 26" :x2="eqX" :y2="springY + 34" stroke="#8b95a3" stroke-dasharray="3 3" />
          <text :x="eqX" :y="springY + 44" text-anchor="middle" font-size="10" fill="#8b95a3">平衡位置</text>
          <line :x1="massX + 16" :y1="springY + 24" :x2="eqX" :y2="springY + 24" stroke="#e05252" stroke-width="2" />
        </g>
      </svg>

      <div class="sh-panel">
        <div class="formula"><code>x = A·cos(ωt+φ)　v = -Aω·sin(ωt+φ)　a = -ω²x</code></div>
        <el-divider />
        <div class="info-row"><span>周期 T = 2π/ω</span><b>{{ fmt(period) }} s</b></div>
        <div class="info-row"><span>频率 f = 1/T</span><b>{{ fmt(1 / period) }} Hz</b></div>
        <div class="info-row"><span>当前时间 t</span><b>{{ fmt(cur.t) }} s</b></div>
        <div class="info-row"><span>位移 x</span><b style="color:#e05252">{{ fmt(cur.x) }} m</b></div>
        <div class="info-row"><span>速度 v</span><b style="color:var(--success)">{{ fmt(cur.v) }} m/s</b></div>
        <div class="info-row"><span>加速度 a = -ω²x</span><b>{{ fmt(cur.a) }} m/s²</b></div>
        <el-divider />
        <div class="info-row"><span>总能量 E = ½mω²A²</span><b>{{ fmt(totalE) }} J</b></div>
        <div class="info-row"><span>动能 Eₖ = ½mv²</span><b>{{ fmt(ke) }} J</b></div>
        <div class="info-row"><span>势能 Eₚ = E - Eₖ</span><b>{{ fmt(totalE - ke) }} J</b></div>
        <div class="ebar">
          <div class="ebar-k" :style="{ width: (ke / Math.max(1e-9, totalE) * 100) + '%' }">动能</div>
          <div class="ebar-p" :style="{ width: ((totalE - ke) / Math.max(1e-9, totalE) * 100) + '%' }">势能</div>
        </div>
        <p class="small muted tip">关键特征：a 与 x 总是反向且成正比（a = -ω²x），这是判断简谐振动的判据；x 最大时 v=0，x=0 时 v 最大。</p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> 旋转矢量 A（匀速转动）</span>
      <span><i class="dot" style="background:#e05252"></i> 位移 x（矢量在 x 轴投影）</span>
      <span><i class="dot" style="background:#f2994a"></i> 已走过的 x-t 曲线</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const amp = ref(1.4)
const omega = ref(1.6)
const phi = ref(0)

const period = computed(() => (2 * Math.PI) / omega.value)

const W = 620, H = 350
const cx = 130, cy = 150, R = 92

const gx0 = 280, gx1 = 600, gyc = 150
const ampPx = 78
const T_TOTAL = computed(() => 2 * period.value)
function gmapT(t) { return gx0 + (t / T_TOTAL.value) * (gx1 - gx0) }
function gmapX(x) { return gyc - (x / 2) * ampPx }

const springY = 292
const eqX = 310
const massX = computed(() => eqX + cur.value.x * 62)
const wallX = 150
const springPath = computed(() => {
  const x1 = wallX
  const x2 = massX.value
  const n = 12
  const seg = (x2 - x1) / n
  let d = `M ${x1} ${springY}`
  for (let i = 1; i <= n; i++) {
    const y = springY + (i % 2 === 0 ? 0 : (i % 4 === 1 ? -9 : 9))
    d += ` L ${(x1 + seg * i).toFixed(1)} ${y}`
  }
  return d + ` L ${x2} ${springY}`
})

const N_STEPS = 48
const steps = computed(() => {
  const out = []
  for (let i = 0; i <= N_STEPS; i++) {
    const t = (T_TOTAL.value * i) / N_STEPS
    const phase = omega.value * t + phi.value
    const x = amp.value * Math.cos(phase)
    const v = -amp.value * omega.value * Math.sin(phase)
    const a = -omega.value * omega.value * x
    let desc
    if (Math.abs(x - amp.value) < 1e-6 || Math.abs(x + amp.value) < 1e-6) {
      desc = `t = ${t.toFixed(2)} s：到达端点 x = ${x.toFixed(3)} m，速度为 0，加速度最大（${a.toFixed(3)}），势能全部最大`
    } else if (Math.abs(x) < 0.02) {
      desc = `t = ${t.toFixed(2)} s：经过平衡位置 x ≈ 0，速度达到最大 ${Math.abs(v).toFixed(3)} m/s，加速度为 0`
    } else {
      desc = `t = ${t.toFixed(2)} s：相位 ωt+φ = ${phase.toFixed(3)}，x = ${x.toFixed(3)} m，v = ${v.toFixed(3)} m/s，a = ${a.toFixed(3)} m/s²`
    }
    out.push({ t, phase, x, v, a, desc })
  }
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)

const xtPath = computed(() => {
  let d = ''
  const N = 200
  for (let i = 0; i <= N; i++) {
    const t = (T_TOTAL.value * i) / N
    const x = amp.value * Math.cos(omega.value * t + phi.value)
    d += (i === 0 ? 'M' : 'L') + gmapT(t).toFixed(2) + ' ' + gmapX(x).toFixed(2) + ' '
  }
  return d
})
const xtFlown = computed(() => {
  let d = ''
  const N = 200
  for (let i = 0; i <= N; i++) {
    const t = (cur.value.t * i) / N
    const x = amp.value * Math.cos(omega.value * t + phi.value)
    d += (i === 0 ? 'M' : 'L') + gmapT(t).toFixed(2) + ' ' + gmapX(x).toFixed(2) + ' '
  }
  return d
})

const arcPath = computed(() => {
  const p = cur.value.phase
  const p0 = phi.value % (2 * Math.PI)
  const norm = ((p % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI)
  const start = Math.min(norm, 0)
  const r = 34
  const x1 = cx + r * Math.cos(0), y1 = cy - r * Math.sin(0)
  const x2 = cx + r * Math.cos(norm), y2 = cy - r * Math.sin(norm)
  return `M ${cx} ${cy} L ${x1.toFixed(1)} ${y1.toFixed(1)} A ${r} ${r} 0 ${norm > Math.PI ? 1 : 0} 0 ${x2.toFixed(1)} ${y2.toFixed(1)} Z`
})

const totalE = computed(() => 0.5 * omega.value * omega.value * amp.value * amp.value)
const ke = computed(() => 0.5 * cur.value.v * cur.value.v)

function fmt(v) { return isFinite(v) ? Number(v.toFixed(3)).toString() : '-' }
</script>

<style scoped>
.sh-wrap { display: flex; gap: 18px; align-items: flex-start; flex-wrap: wrap; }
.sh-svg { background: #fcfdff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.sh-panel { flex: 1; min-width: 300px; }
.formula code { background: #f2f4f8; padding: 8px 10px; border-radius: 6px; display: block; font-size: 12px; line-height: 1.7; }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.ebar { display: flex; height: 22px; border-radius: 6px; overflow: hidden; margin-top: 10px; font-size: 11px; color: #fff; }
.ebar-k { background: #f2994a; display: flex; align-items: center; justify-content: center; transition: width .2s; }
.ebar-p { background: #22a06b; display: flex; align-items: center; justify-content: center; transition: width .2s; }
.tip { margin-top: 10px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
