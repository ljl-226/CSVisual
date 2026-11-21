<template>
  <VisFrame
    title="参数估计 · 抽样分布与置信区间"
    desc="为什么看这个动画：重复抽样会让估计量形成新的分布；增大样本量后分布变窄，95% 置信区间也能用覆盖次数直接验证。"
    :player="player"
    :status-text="statusText"
    back-to="/knowledge/89"
  >
    <template #extra>
      <el-select v-model="distKey" size="small" style="width: 170px" @change="player.reset()">
        <el-option value="normal" label="正态 N(2, 1.5²)" />
        <el-option value="uniform" label="均匀 U(0, 4)" />
      </el-select>
      <span class="small muted">样本量 n={{ sampleSize }}</span>
      <el-slider v-model="sampleSize" :min="5" :max="80" :step="5" style="width: 135px" :show-tooltip="false" @change="player.reset()" />
    </template>

    <div class="es-wrap">
      <div ref="plotHost" class="plot-host">
        <svg viewBox="0 0 740 430" class="es-svg" role="img" aria-label="参数估计抽样分布与置信区间覆盖动画">
          <rect x="1" y="1" width="738" height="428" rx="10" fill="#fcfdff" stroke="#e4e8ef" />
          <text x="18" y="25" class="section-title">{{ cur.count }} 次重复实验得到的样本均值分布</text>
          <line x1="48" y1="292" x2="440" y2="292" stroke="#8b95a3" stroke-width="1.3" />
          <rect v-for="(bar, i) in histogram" :key="'bar' + i" :x="bar.x" :y="bar.y" :width="bar.w" :height="bar.h" rx="2" fill="#7ea1f1" />
          <line :x1="histX(trueMean)" y1="48" :x2="histX(trueMean)" y2="292" stroke="#e05252" stroke-width="2.2" stroke-dasharray="6 4" />
          <path :d="normalCurve" fill="none" stroke="#22a06b" stroke-width="2" />
          <text :x="histX(trueMean) + 6" y="60" font-size="11" fill="#c53d3d">真均值 μ={{ fmt(trueMean) }}</text>
          <text v-for="tick in histTicks" :key="'tick' + tick" :x="histX(tick)" y="309" text-anchor="middle" font-size="10" fill="#8b95a3">{{ fmt(tick) }}</text>
          <text x="244" y="331" text-anchor="middle" font-size="11" fill="#657184">样本均值 x̄</text>

          <text x="470" y="25" class="section-title">最近置信区间（红线未覆盖）</text>
          <line :x1="ciX(trueMean)" y1="48" :x2="ciX(trueMean)" y2="360" stroke="#e05252" stroke-width="2" stroke-dasharray="6 4" />
          <g v-for="(item, i) in recentIntervals" :key="'ci' + item.index">
            <line :x1="ciX(item.low)" :y1="58 + i * 16" :x2="ciX(item.high)" :y2="58 + i * 16" :stroke="item.cover ? '#3b6ef6' : '#e05252'" stroke-width="2.4" />
            <circle :cx="ciX(item.mean)" :cy="58 + i * 16" r="2.8" :fill="item.cover ? '#3b6ef6' : '#e05252'" />
          </g>
          <text x="596" y="385" text-anchor="middle" font-size="12" fill="#526071">覆盖率 {{ fmtPercent(coverage) }}</text>
          <text x="596" y="405" text-anchor="middle" font-size="11" fill="#8b95a3">理论目标 95%</text>
          <text v-if="compact" x="18" y="407" font-size="10" fill="#8b95a3">蓝柱：经验分布　绿线：理论近似</text>
        </svg>
      </div>

      <div class="es-panel">
        <div class="formula"><code>E(x̄)=μ，Var(x̄)=σ²/n；CI₉₅=x̄±1.96·σ/√n</code></div>
        <el-divider />
        <div class="info-row"><span>本次样本均值 x̄</span><b style="color: #3b6ef6">{{ fmt(currentExperiment.mean) }}</b></div>
        <div class="info-row"><span>真均值 μ</span><b>{{ fmt(trueMean) }}</b></div>
        <div class="info-row"><span>真参数 {{ parameterSymbol }}</span><b>{{ fmt(trueParameter) }}</b></div>
        <div class="info-row"><span>理论标准误 σ/√n</span><b>{{ fmt(theoreticalSE) }}</b></div>
        <div class="info-row"><span>经验标准差</span><b>{{ fmt(empiricalSd) }}</b></div>
        <div class="info-row"><span>矩估计</span><b style="color: #8b5cf6">{{ parameterSymbol }}̂={{ fmt(currentExperiment.mom) }}</b></div>
        <div class="info-row"><span>最大似然估计 MLE</span><b style="color: #b46a15">{{ parameterSymbol }}̂={{ fmt(currentExperiment.mle) }}</b></div>
        <div class="info-row"><span>本次 95% CI</span><b>[{{ fmt(currentExperiment.low) }}, {{ fmt(currentExperiment.high) }}]</b></div>
        <div class="info-row"><span>累计覆盖</span><el-tag size="small" :type="currentExperiment.cover ? 'success' : 'danger'">{{ coveredCount }}/{{ cur.count }}</el-tag></div>
        <div class="sample-box"><span>本次采样点（前 8 个）</span><code>{{ samplePreview }}</code></div>
        <p class="small muted tip">{{ estimateNote }} 样本量变为 4 倍时，标准误约缩小为原来的 1/2，这就是估计量“越来越稳定”的定量含义。</p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot histogram-dot"></i> 样本均值经验分布</span>
      <span><i class="dot theory-dot"></i> 理论正态近似</span>
      <span><i class="dot true-dot"></i> 真均值</span>
      <span><i class="dot miss-dot"></i> 未覆盖区间</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const distKey = ref('normal')
const sampleSize = ref(20)
const plotHost = ref(null)
const viewportWidth = ref(740)
let resizeObserver = null

const compact = computed(() => viewportWidth.value < 560)
const trueMean = computed(() => 2)
const trueSigma = computed(() => distKey.value === 'normal' ? 1.5 : 4 / Math.sqrt(12))
const trueParameter = computed(() => distKey.value === 'normal' ? 2 : 4)
const parameterSymbol = computed(() => distKey.value === 'normal' ? 'μ' : 'θ')
const theoreticalSE = computed(() => trueSigma.value / Math.sqrt(sampleSize.value))
const estimateNote = computed(() => distKey.value === 'normal'
  ? '正态均值的矩估计与 MLE 都是 x̄，因此两者在本例重合。'
  : '对 U(0,θ)，矩估计 θ̂=2x̄；MLE θ̂=max(Xᵢ)，两者会给出不同数字。')

function mulberry32(seed) {
  return () => {
    seed |= 0
    seed = seed + 0x6D2B79F5 | 0
    let t = Math.imul(seed ^ seed >>> 15, 1 | seed)
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t
    return ((t ^ t >>> 14) >>> 0) / 4294967296
  }
}
function normalSample(random) {
  const u = Math.max(1e-9, random())
  const v = random()
  return 2 + 1.5 * Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v)
}

// 固定种子让同一组参数下的动画可复现，便于学生比较不同 n 的方差。
const experiments = computed(() => {
  const random = mulberry32(8900 + sampleSize.value * 17 + (distKey.value === 'normal' ? 1 : 2))
  const out = []
  for (let k = 0; k < 100; k++) {
    const sample = []
    for (let i = 0; i < sampleSize.value; i++) sample.push(distKey.value === 'normal' ? normalSample(random) : 4 * random())
    const mean = sample.reduce((sum, value) => sum + value, 0) / sample.length
    const mom = distKey.value === 'normal' ? mean : 2 * mean
    const mle = distKey.value === 'normal' ? mean : Math.max(...sample)
    const margin = 1.96 * theoreticalSE.value
    const low = mean - margin
    const high = mean + margin
    out.push({ index: k + 1, sample, mean, mom, mle, low, high, cover: low <= trueMean.value && high >= trueMean.value })
  }
  return out
})

const steps = computed(() => experiments.value.map((item, index) => {
  const done = experiments.value.slice(0, index + 1)
  const covered = done.filter(exp => exp.cover).length
  return {
    count: index + 1,
    experiment: item,
    covered,
    desc: `第 ${index + 1} 次实验：x̄=${fmt(item.mean)}，${parameterSymbol.value} 的矩估计=${fmt(item.mom)}、MLE=${fmt(item.mle)}；置信区间${item.cover ? '覆盖' : '没有覆盖'}真均值，累计覆盖率 ${fmtPercent(covered / (index + 1))}。`
  }
}))
const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const currentExperiment = computed(() => cur.value.experiment)
const coveredCount = computed(() => cur.value.covered)
const coverage = computed(() => coveredCount.value / cur.value.count)
const statusText = computed(() => cur.value.desc)
const visibleExperiments = computed(() => experiments.value.slice(0, cur.value.count))
const samplePreview = computed(() => currentExperiment.value.sample.slice(0, 8).map(value => fmt(value)).join(', '))
const empiricalSd = computed(() => {
  const means = visibleExperiments.value.map(item => item.mean)
  if (means.length < 2) return 0
  const avg = means.reduce((sum, value) => sum + value, 0) / means.length
  return Math.sqrt(means.reduce((sum, value) => sum + (value - avg) ** 2, 0) / (means.length - 1))
})

const histRange = computed(() => [trueMean.value - 4 * theoreticalSE.value, trueMean.value + 4 * theoreticalSE.value])
function histX(value) { return 48 + (value - histRange.value[0]) / (histRange.value[1] - histRange.value[0]) * 392 }
const histTicks = computed(() => {
  const count = compact.value ? 3 : 5
  return Array.from({ length: count }, (_, i) => histRange.value[0] + (histRange.value[1] - histRange.value[0]) * i / (count - 1))
})
const histogram = computed(() => {
  const bins = 16
  const counts = Array(bins).fill(0)
  visibleExperiments.value.forEach(item => {
    const ratio = (item.mean - histRange.value[0]) / (histRange.value[1] - histRange.value[0])
    const index = Math.max(0, Math.min(bins - 1, Math.floor(ratio * bins)))
    counts[index]++
  })
  const max = Math.max(1, ...counts)
  return counts.map((count, i) => ({ x: 49 + i * 391 / bins, y: 292 - count / max * 220, w: 391 / bins - 2, h: count / max * 220 }))
})
const normalCurve = computed(() => {
  const points = []
  const sigma = theoreticalSE.value
  for (let i = 0; i <= 100; i++) {
    const x = histRange.value[0] + (histRange.value[1] - histRange.value[0]) * i / 100
    const density = Math.exp(-0.5 * ((x - trueMean.value) / sigma) ** 2)
    points.push({ x: histX(x), y: 292 - density * 205 })
  }
  return points.map((point, i) => `${i ? 'L' : 'M'}${point.x.toFixed(1)},${point.y.toFixed(1)}`).join(' ')
})

const ciRange = computed(() => [trueMean.value - 3.6 * theoreticalSE.value, trueMean.value + 3.6 * theoreticalSE.value])
function ciX(value) { return 466 + (value - ciRange.value[0]) / (ciRange.value[1] - ciRange.value[0]) * 260 }
const recentIntervals = computed(() => visibleExperiments.value.slice(-19))

function fmt(value) { return Number.isFinite(value) ? Number(value).toFixed(3) : '—' }
function fmtPercent(value) { return `${(value * 100).toFixed(1)}%` }

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
.es-wrap { display: flex; gap: 18px; align-items: flex-start; flex-wrap: wrap; }
.plot-host { flex: 2 1 600px; min-width: 0; }
.es-svg { display: block; width: 100%; height: auto; min-height: 330px; }
.es-panel { flex: 1 1 290px; min-width: 270px; }
.section-title { font-size: 13px; font-weight: 700; fill: #334155; }
.formula code, .sample-box code { display: block; padding: 9px 10px; background: #f2f4f8; border-radius: 7px; font-size: 12px; line-height: 1.6; }
.info-row { display: flex; justify-content: space-between; gap: 10px; padding: 5px 0; border-bottom: 1px dashed #edf0f5; font-size: 12px; }
.info-row b { text-align: right; }
.sample-box { margin-top: 11px; font-size: 12px; color: #657184; }
.sample-box code { margin-top: 5px; color: #334155; word-break: break-all; }
.tip { line-height: 1.75; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; }
.histogram-dot { background: #7ea1f1; }
.theory-dot { background: #22a06b; }
.true-dot, .miss-dot { background: #e05252; }
@media (max-width: 640px) {
  .es-panel { min-width: 100%; }
  .es-svg { min-height: 260px; }
}
</style>
