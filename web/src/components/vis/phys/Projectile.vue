<template>
  <VisFrame title="抛体运动 · 运动的合成与分解" desc="水平方向匀速、竖直方向匀变速，两个独立运动叠加成一条抛物线轨迹" :player="player" :status-text="statusText" back-to="/knowledge/29">
    <template #extra>
      <span class="small muted">v₀</span>
      <el-slider v-model="v0" :min="5" :max="40" :step="1" style="width:130px" :show-tooltip="false" @input="player.reset()" />
      <b class="small">{{ v0 }} m/s</b>
      <span class="small muted">θ</span>
      <el-slider v-model="theta" :min="5" :max="85" :step="1" style="width:130px" :show-tooltip="false" @input="player.reset()" />
      <b class="small">{{ theta }}°</b>
    </template>

    <div class="pj-wrap">
      <svg :width="W" :height="H" class="pj-svg">
        <!-- 地面 -->
        <rect :x="0" :y="groundY" :width="W" :height="H - groundY" fill="#eef3e9" />
        <line :x1="20" :y1="groundY" :x2="W - 10" :y2="groundY" stroke="#8b95a3" stroke-width="2" />

        <!-- 完整轨迹（虚线） -->
        <path :d="fullPath" fill="none" stroke="#c8d3e6" stroke-width="1.5" stroke-dasharray="5 4" />
        <!-- 已飞行轨迹 -->
        <path :d="flownPath" fill="none" stroke="#3b6ef6" stroke-width="3" />

        <!-- 最高点标记 -->
        <g v-if="cur.t >= tTop">
          <circle :cx="sx(range / 2)" :cy="sy(maxH)" r="4" fill="#22a06b" />
          <text :x="sx(range / 2)" :y="sy(maxH) - 10" text-anchor="middle" font-size="11" fill="#22a06b">最高点 H = {{ fmt(maxH) }} m</text>
        </g>
        <!-- 落点 -->
        <g v-if="player.finished.value">
          <circle :cx="sx(range)" :cy="groundY" r="4" fill="#e05252" />
          <text :x="sx(range)" :y="groundY - 10" text-anchor="middle" font-size="11" fill="#e05252">射程 R = {{ fmt(range) }} m</text>
        </g>

        <!-- 小球 -->
        <circle :cx="sx(cur.x)" :cy="sy(cur.y)" r="8" fill="#f2994a" stroke="#b46a15" stroke-width="2" />

        <!-- 速度分解 -->
        <g>
          <line :x1="sx(cur.x)" :y1="sy(cur.y)" :x2="sx(cur.x) + vx * vs" :y2="sy(cur.y)" stroke="#3b6ef6" stroke-width="2.5" />
          <line :x1="sx(cur.x)" :y1="sy(cur.y)" :x2="sx(cur.x)" :y2="sy(cur.y) - cur.vy * vs" stroke="#22a06b" stroke-width="2.5" />
          <line :x1="sx(cur.x)" :y1="sy(cur.y)" :x2="sx(cur.x) + vx * vs" :y2="sy(cur.y) - cur.vy * vs" stroke="#e05252" stroke-width="2.5" />
          <text :x="sx(cur.x) + vx * vs / 2" :y="sy(cur.y) + 18" font-size="10" fill="#3b6ef6" text-anchor="middle">vₓ = {{ fmt(vx) }}</text>
          <text :x="sx(cur.x) + 6" :y="sy(cur.y) - (cur.vy * vs) / 2" font-size="10" fill="#22a06b">v_y = {{ fmt(cur.vy) }}</text>
        </g>
        <text :x="12" :y="20" font-size="12" fill="#8b95a3">t = {{ fmt(cur.t) }} s　（g = 9.8 m/s²，忽略空气阻力）</text>
      </svg>

      <div class="pj-panel">
        <div class="formula">
          <code>x = v₀cosθ · t　　y = v₀sinθ · t - ½gt²</code>
        </div>
        <el-divider />
        <div class="info-row"><span>水平分速度 v₀cosθ</span><b style="color:var(--brand)">{{ fmt(vx) }} m/s（恒定）</b></div>
        <div class="info-row"><span>竖直初速度 v₀sinθ</span><b style="color:var(--success)">{{ fmt(vy0) }} m/s</b></div>
        <div class="info-row"><span>当前竖直速度 v_y</span><b>{{ fmt(cur.vy) }} m/s</b></div>
        <div class="info-row"><span>合速度大小 |v|</span><b style="color:#e05252">{{ fmt(Math.hypot(vx, cur.vy)) }} m/s</b></div>
        <div class="info-row"><span>飞行时间 T = 2v₀sinθ/g</span><b>{{ fmt(T) }} s</b></div>
        <div class="info-row"><span>最大高度 H = v₀²sin²θ/(2g)</span><b>{{ fmt(maxH) }} m</b></div>
        <div class="info-row"><span>射程 R = v₀²sin2θ/g</span><b>{{ fmt(range) }} m</b></div>
        <el-divider />
        <p class="small muted tip">
          要点：水平方向不受力 → 匀速；竖直方向只受重力 → 匀变速。二者互不影响（独立性原理）。
          当 θ = 45° 时射程最大；当前 θ = {{ theta }}°，
          <b>{{ rangeNote }}</b>
        </p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> vₓ 水平分量（不变）</span>
      <span><i class="dot" style="background:#22a06b"></i> v_y 竖直分量（匀减速）</span>
      <span><i class="dot" style="background:#e05252"></i> 合速度 v</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const G = 9.8
const v0 = ref(25)
const theta = ref(50)

const rad = computed(() => (theta.value * Math.PI) / 180)
const vx = computed(() => v0.value * Math.cos(rad.value))
const vy0 = computed(() => v0.value * Math.sin(rad.value))
const T = computed(() => (2 * vy0.value) / G)
const maxH = computed(() => (vy0.value * vy0.value) / (2 * G))
const range = computed(() => (v0.value * v0.value * Math.sin(2 * rad.value)) / G)
const tTop = computed(() => vy0.value / G)

const W = 620, H = 340
const groundY = 280
const scale = computed(() => {
  const sx = (W - 70) / Math.max(1, range.value * 1.12)
  const sy = (groundY - 50) / Math.max(1, maxH.value * 1.25)
  return Math.min(sx, sy)
})
const vs = computed(() => Math.min(3.2, 90 / Math.max(1, v0.value))) // 速度矢量显示比例
function sx(x) { return 30 + x * scale.value }
function sy(y) { return groundY - y * scale.value }

const N_STEPS = 30
const steps = computed(() => {
  const out = []
  for (let i = 0; i <= N_STEPS; i++) {
    const t = (T.value * i) / N_STEPS
    const x = vx.value * t
    const y = vy0.value * t - 0.5 * G * t * t
    const vy = vy0.value - G * t
    let desc
    if (i === 0) desc = `起点：v₀ = ${v0.value} m/s，θ = ${theta.value}°，水平分量 ${vx.value.toFixed(2)}、竖直分量 ${vy0.value.toFixed(2)}`
    else if (Math.abs(t - tTop.value) < T.value / N_STEPS / 2) desc = `到达最高点 t = ${tTop.value.toFixed(2)} s：竖直速度减为 0，高度 ${maxH.value.toFixed(2)} m，水平仍在前进`
    else if (i === N_STEPS) desc = `落地 t = ${T.value.toFixed(2)} s：射程 ${range.value.toFixed(2)} m，落地竖直速度 ${(-vy0.value).toFixed(2)} m/s`
    else desc = `t = ${t.toFixed(2)} s：x = ${x.toFixed(2)} m，y = ${y.toFixed(2)} m，v_y = ${vy.toFixed(2)} m/s（每秒减少 ${G}）`
    out.push({ t, x, y: Math.max(0, y), vy, desc })
  }
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)

const fullPath = computed(() => {
  let d = ''
  const N = 80
  for (let i = 0; i <= N; i++) {
    const t = (T.value * i) / N
    const x = vx.value * t
    const y = Math.max(0, vy0.value * t - 0.5 * G * t * t)
    d += (i === 0 ? 'M' : 'L') + sx(x).toFixed(2) + ' ' + sy(y).toFixed(2) + ' '
  }
  return d
})
const flownPath = computed(() => {
  let d = ''
  const N = 80
  const tEnd = cur.value.t
  for (let i = 0; i <= N; i++) {
    const t = (tEnd * i) / N
    const x = vx.value * t
    const y = Math.max(0, vy0.value * t - 0.5 * G * t * t)
    d += (i === 0 ? 'M' : 'L') + sx(x).toFixed(2) + ' ' + sy(y).toFixed(2) + ' '
  }
  return d
})

const rangeNote = computed(() => {
  const best = Math.abs(theta.value - 45) < 0.6
  if (best) return '正好取到最大射程'
  return theta.value < 45
    ? `再抬高到 45° 射程会更远（现为最大值的 ${((Math.sin(2 * rad.value) / 1) * 100).toFixed(1)}%）`
    : `角度偏高，降低到 45° 射程更远（现为最大值的 ${((Math.sin(2 * rad.value) / 1) * 100).toFixed(1)}%）`
})

function fmt(v) { return isFinite(v) ? Number(v).toFixed(2).toString() : '-' }
</script>

<style scoped>
.pj-wrap { display: flex; gap: 18px; align-items: flex-start; flex-wrap: wrap; }
.pj-svg { background: #fcfdff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.pj-panel { flex: 1; min-width: 300px; }
.formula code { background: #f2f4f8; padding: 8px 10px; border-radius: 6px; display: block; font-size: 12px; line-height: 1.7; }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.tip { line-height: 1.8; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
