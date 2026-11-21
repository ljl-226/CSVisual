<template>
  <VisFrame
    title="假设检验 · 拒绝域、两类错误与 p 值"
    desc="为什么看这个动画：显著性水平不是“结论正确率”，它通过移动临界值在 α 与 β 之间取舍，而 p 值刻画当前样本有多极端。"
    :player="player"
    :status-text="statusText"
    back-to="/knowledge/90"
  >
    <template #extra>
      <el-select v-model="testType" size="small" style="width: 125px" @change="player.reset()">
        <el-option value="right" label="右侧检验" />
        <el-option value="two" label="双侧检验" />
      </el-select>
      <span class="small muted">显著水平 α={{ alpha.toFixed(2) }}</span>
      <el-slider v-model="alpha" :min="0.01" :max="0.1" :step="0.01" style="width: 120px" :show-tooltip="false" @input="player.reset()" />
    </template>

    <div class="ht-wrap">
      <div ref="plotHost" class="plot-host">
        <svg viewBox="0 0 720 390" class="ht-svg" role="img" aria-label="假设检验拒绝域与两类错误图">
          <rect x="1" y="1" width="718" height="388" rx="10" fill="#fcfdff" stroke="#e4e8ef" />
          <text x="18" y="25" class="section-title">H₀: μ=0 与 H₁: μ={{ delta.toFixed(1) }} 下的统计量分布</text>
          <line x1="50" y1="322" x2="695" y2="322" stroke="#8b95a3" stroke-width="1.4" />
          <line v-for="tick in xTicks" :key="tick" :x1="mapX(tick)" y1="322" :x2="mapX(tick)" y2="328" stroke="#8b95a3" />
          <text v-for="tick in xTicks" :key="'t' + tick" :x="mapX(tick)" y="344" text-anchor="middle" font-size="10" fill="#8b95a3">{{ tick }}</text>

          <!-- 红色面积是 H₀ 为真却落入拒绝域的概率，其总面积正好等于 α。 -->
          <path v-for="(path, i) in alphaAreas" :key="'alpha' + i" :d="path" fill="#e05252" fill-opacity="0.3" stroke="none" />
          <!-- 橙色面积是 H₁ 为真却没有拒绝 H₀ 的概率 β。 -->
          <path :d="betaArea" fill="#f2994a" fill-opacity="0.28" stroke="none" />
          <path :d="nullCurve" fill="none" stroke="#3b6ef6" stroke-width="2.7" />
          <path :d="altCurve" fill="none" stroke="#8b5cf6" stroke-width="2.4" />
          <line v-for="critical in criticals" :key="critical" :x1="mapX(critical)" y1="54" :x2="mapX(critical)" y2="322" stroke="#e05252" stroke-width="1.8" stroke-dasharray="6 4" />
          <text v-for="critical in criticals" :key="'c' + critical" :x="mapX(critical)" y="48" text-anchor="middle" font-size="11" fill="#c53d3d">临界值 {{ fmt(critical) }}</text>

          <line :x1="mapX(currentZ)" y1="72" :x2="mapX(currentZ)" y2="322" stroke="#1f2733" stroke-width="2.6" />
          <circle :cx="mapX(currentZ)" :cy="mapY(normalPdf(currentZ, 0))" r="5" fill="#1f2733" />
          <text :x="Math.min(650, Math.max(75, mapX(currentZ)))" y="92" text-anchor="middle" font-size="12" fill="#1f2733">当前 z={{ fmt(currentZ) }}</text>
          <text x="115" y="72" font-size="12" fill="#3b6ef6">H₀ 分布</text>
          <text :x="mapX(delta)" y="116" text-anchor="middle" font-size="12" fill="#8b5cf6">H₁ 分布</text>
          <text x="64" y="305" font-size="11" fill="#c53d3d">红色：α 拒绝域</text>
          <text v-if="!compact" x="240" y="305" font-size="11" fill="#b46a15">橙色：β（漏判 H₁）</text>
        </svg>
      </div>

      <div class="ht-panel">
        <div class="param-row">
          <span>真实效应 δ={{ delta.toFixed(1) }}</span>
          <el-slider v-model="delta" :min="0.2" :max="3" :step="0.1" :show-tooltip="false" @input="player.reset()" />
        </div>
        <div class="param-row">
          <span>观测统计量 z={{ observedZ.toFixed(1) }}</span>
          <el-slider v-model="observedZ" :min="-4" :max="5" :step="0.1" :show-tooltip="false" @input="player.reset()" />
        </div>
        <div class="formula"><code>{{ hypothesisFormula }}</code></div>
        <el-divider />
        <div class="info-row"><span>临界值</span><b>{{ criticalText }}</b></div>
        <div class="info-row"><span>第一类错误 α</span><b style="color: #e05252">{{ fmtPercent(alpha) }}</b></div>
        <div class="info-row"><span>第二类错误 β</span><b style="color: #b46a15">{{ fmtPercent(beta) }}</b></div>
        <div class="info-row"><span>检验功效 1-β</span><b style="color: #8b5cf6">{{ fmtPercent(1 - beta) }}</b></div>
        <div class="info-row"><span>当前 p 值</span><b style="color: #3b6ef6">{{ fmtP(pValue) }}</b></div>
        <div class="decision" :class="reject ? 'reject' : 'accept'">
          {{ reject ? `p<α，拒绝 H₀` : `p≥α，暂不拒绝 H₀` }}
        </div>
        <p class="small muted tip">减小 α 会缩小拒绝域、降低误拒风险，但在效应 δ 不变时通常增大 β；增大样本量则可让 H₁ 分布远离 H₀，从而同时控制两类错误。</p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot null-dot"></i> H₀ 分布</span>
      <span><i class="dot alt-dot"></i> H₁ 分布</span>
      <span><i class="dot alpha-dot"></i> α 拒绝域</span>
      <span><i class="dot beta-dot"></i> β 接受域</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const testType = ref('two')
const alpha = ref(0.05)
const delta = ref(1.5)
const observedZ = ref(2.1)
const plotHost = ref(null)
const viewportWidth = ref(720)
let resizeObserver = null

const compact = computed(() => viewportWidth.value < 540)
function normalPdf(x, mean = 0) { return Math.exp(-0.5 * (x - mean) ** 2) / Math.sqrt(2 * Math.PI) }
function erf(x) {
  const sign = x < 0 ? -1 : 1
  const value = Math.abs(x)
  const t = 1 / (1 + 0.3275911 * value)
  const y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-value * value)
  return sign * y
}
function normalCdf(x) { return 0.5 * (1 + erf(x / Math.sqrt(2))) }
function normalQuantile(probability) {
  let low = -8, high = 8
  for (let i = 0; i < 60; i++) {
    const mid = (low + high) / 2
    if (normalCdf(mid) < probability) low = mid
    else high = mid
  }
  return (low + high) / 2
}

const critical = computed(() => normalQuantile(testType.value === 'two' ? 1 - alpha.value / 2 : 1 - alpha.value))
const criticals = computed(() => testType.value === 'two' ? [-critical.value, critical.value] : [critical.value])
const beta = computed(() => testType.value === 'two'
  ? normalCdf(critical.value - delta.value) - normalCdf(-critical.value - delta.value)
  : normalCdf(critical.value - delta.value))
const hypothesisFormula = computed(() => testType.value === 'two' ? 'H₀: μ=0；H₁: μ≠0；拒绝域 |Z|≥z₁₋α/₂' : 'H₀: μ=0；H₁: μ>0；拒绝域 Z≥z₁₋α')
const criticalText = computed(() => testType.value === 'two' ? `±${fmt(critical.value)}` : fmt(critical.value))

const steps = computed(() => Array.from({ length: 41 }, (_, i) => {
  const progress = i / 40
  const z = delta.value + (observedZ.value - delta.value) * progress
  const p = testType.value === 'two' ? Math.min(1, 2 * (1 - normalCdf(Math.abs(z)))) : 1 - normalCdf(z)
  const isReject = p < alpha.value
  return {
    progress,
    z,
    p,
    reject: isReject,
    desc: `统计量移动到 z=${fmt(z)}：p=${fmtP(p)}，与 α=${alpha.value.toFixed(2)} 比较，结论为“${isReject ? '拒绝 H₀' : '暂不拒绝 H₀'}”；当前 β=${fmtPercent(beta.value)}。`
  }
}))
const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const currentZ = computed(() => cur.value.z)
const pValue = computed(() => cur.value.p)
const reject = computed(() => cur.value.reject)
const statusText = computed(() => cur.value.desc)

const xRange = computed(() => [-4.5, Math.max(4.5, delta.value + 3.8)])
function mapX(x) { return 50 + (x - xRange.value[0]) / (xRange.value[1] - xRange.value[0]) * 645 }
function mapY(density) { return 322 - density / 0.42 * 250 }
const xTicks = computed(() => {
  const low = Math.ceil(xRange.value[0])
  const high = Math.floor(xRange.value[1])
  const step = compact.value ? 2 : 1
  const ticks = []
  for (let value = low; value <= high; value += step) ticks.push(value)
  return ticks
})
function densityPath(mean) {
  const points = []
  for (let i = 0; i <= 180; i++) {
    const x = xRange.value[0] + (xRange.value[1] - xRange.value[0]) * i / 180
    points.push({ x: mapX(x), y: mapY(normalPdf(x, mean)) })
  }
  return points.map((point, i) => `${i ? 'L' : 'M'}${point.x.toFixed(1)},${point.y.toFixed(1)}`).join(' ')
}
function densityArea(mean, from, to) {
  const low = Math.max(xRange.value[0], from)
  const high = Math.min(xRange.value[1], to)
  if (low >= high) return ''
  const points = [{ x: mapX(low), y: 322 }]
  for (let i = 0; i <= 100; i++) {
    const x = low + (high - low) * i / 100
    points.push({ x: mapX(x), y: mapY(normalPdf(x, mean)) })
  }
  points.push({ x: mapX(high), y: 322 })
  return `${points.map((point, i) => `${i ? 'L' : 'M'}${point.x.toFixed(1)},${point.y.toFixed(1)}`).join(' ')} Z`
}
const nullCurve = computed(() => densityPath(0))
const altCurve = computed(() => densityPath(delta.value))
const alphaAreas = computed(() => testType.value === 'two'
  ? [densityArea(0, xRange.value[0], -critical.value), densityArea(0, critical.value, xRange.value[1])]
  : [densityArea(0, critical.value, xRange.value[1])])
const betaArea = computed(() => testType.value === 'two'
  ? densityArea(delta.value, -critical.value, critical.value)
  : densityArea(delta.value, xRange.value[0], critical.value))

function fmt(value) { return Number.isFinite(value) ? Number(value).toFixed(3) : '—' }
function fmtPercent(value) { return `${(value * 100).toFixed(2)}%` }
function fmtP(value) { return value < 0.0001 ? '<0.0001' : value.toFixed(4) }

onMounted(() => {
  resizeObserver = new ResizeObserver(entries => {
    viewportWidth.value = Math.max(280, Math.floor(entries[0].contentRect.width))
  })
  if (plotHost.value) resizeObserver.observe(plotHost.value)
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  player.pause()
})
</script>

<style scoped>
.ht-wrap { display: flex; gap: 18px; align-items: flex-start; flex-wrap: wrap; }
.plot-host { flex: 2 1 590px; min-width: 0; }
.ht-svg { display: block; width: 100%; height: auto; min-height: 320px; }
.ht-panel { flex: 1 1 290px; min-width: 270px; }
.section-title { font-size: 13px; font-weight: 700; fill: #334155; }
.param-row { display: grid; grid-template-columns: 135px 1fr; gap: 10px; align-items: center; margin-bottom: 5px; font-size: 12px; }
.formula code { display: block; padding: 9px 10px; background: #f2f4f8; border-radius: 7px; font-size: 12px; line-height: 1.6; }
.info-row { display: flex; justify-content: space-between; gap: 10px; padding: 6px 0; border-bottom: 1px dashed #edf0f5; font-size: 13px; }
.decision { margin-top: 12px; padding: 10px; border-radius: 8px; text-align: center; font-size: 13px; font-weight: 700; }
.decision.reject { color: #b42318; background: #fff1f0; border: 1px solid #ffd0cc; }
.decision.accept { color: #176b49; background: #eefbf4; border: 1px solid #c7efda; }
.tip { line-height: 1.75; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; }
.null-dot { background: #3b6ef6; }
.alt-dot { background: #8b5cf6; }
.alpha-dot { background: #e05252; }
.beta-dot { background: #f2994a; }
@media (max-width: 640px) {
  .ht-panel { min-width: 100%; }
  .ht-svg { min-height: 255px; }
}
</style>
