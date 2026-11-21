<template>
  <VisFrame
    title="无穷级数与幂级数"
    desc="为什么看这个动画：逐项累加能直接区分“部分和趋近有限值”和“项虽趋零但总和仍发散”，并用余项数字检验误差。"
    :player="player"
    :status-text="statusText"
    back-to="/knowledge/87"
  >
    <template #extra>
      <el-select v-model="seriesKey" size="small" style="width: 175px" @change="player.reset()">
        <el-option v-for="item in SERIES" :key="item.key" :label="item.label" :value="item.key" />
      </el-select>
      <span class="small muted">最高项 N={{ maxN }}</span>
      <el-slider v-model="maxN" :min="12" :max="60" :step="4" style="width: 110px" :show-tooltip="false" @change="player.reset()" />
    </template>

    <div class="sr-wrap">
      <div ref="chartHost" class="chart-host">
        <svg viewBox="0 0 680 370" class="sr-svg" role="img" aria-label="无穷级数部分和收敛过程图">
          <rect x="1" y="1" width="678" height="368" rx="10" fill="#fcfdff" stroke="#e4e8ef" />
          <line v-for="tick in yTicks" :key="'gy' + tick" x1="54" :y1="mapY(tick)" x2="660" :y2="mapY(tick)" stroke="#edf0f5" />
          <text v-for="tick in yTicks" :key="'ty' + tick" x="47" :y="mapY(tick) + 4" text-anchor="end" font-size="10" fill="#8b95a3">{{ short(tick) }}</text>
          <line x1="54" y1="326" x2="660" y2="326" stroke="#8b95a3" stroke-width="1.4" />
          <line x1="54" y1="24" x2="54" y2="326" stroke="#8b95a3" stroke-width="1.4" />
          <text v-for="tick in nTicks" :key="'tn' + tick" :x="mapX(tick)" y="345" text-anchor="middle" font-size="10" fill="#8b95a3">{{ tick }}</text>
          <text x="657" y="345" text-anchor="end" font-size="11" fill="#657184">项数 n</text>

          <!-- 收敛级数的极限是一条固定水平线，部分和折线应逐渐贴近它。 -->
          <line v-if="target !== null" x1="54" :y1="mapY(target)" x2="660" :y2="mapY(target)" stroke="#22a06b" stroke-width="2" stroke-dasharray="7 5" />
          <text v-if="target !== null" x="657" :y="mapY(target) - 7" text-anchor="end" font-size="11" fill="#1a7a52">极限 S={{ fmt(target) }}</text>
          <path :d="fullPath" fill="none" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="4 4" />
          <path :d="currentPath" fill="none" stroke="#3b6ef6" stroke-width="2.8" />
          <circle v-for="point in visiblePoints" :key="point.n" :cx="mapX(point.n)" :cy="mapY(point.sum)" :r="point.n === cur.n ? 5 : 2.2" :fill="point.n === cur.n ? '#e05252' : '#3b6ef6'" />
          <line v-if="target !== null" :x1="mapX(cur.n)" :y1="mapY(cur.sum)" :x2="mapX(cur.n)" :y2="mapY(target)" stroke="#e05252" stroke-width="2" />
          <text x="66" y="43" font-size="12" fill="#526071">{{ preset.formula }}</text>
          <text v-if="compact" x="66" y="62" font-size="10" fill="#8b95a3">蓝线：Sₙ　绿虚线：极限</text>
        </svg>
      </div>

      <div class="sr-panel">
        <div class="power-control">
          <div class="control-title">幂级数参数 x</div>
          <el-slider v-model="powerX" :min="-1.25" :max="1.25" :step="0.05" :disabled="seriesKey !== 'power'" :show-tooltip="false" @input="player.reset()" />
          <div class="interval" :class="powerState.type">x={{ powerX.toFixed(2) }}；{{ powerState.text }}</div>
        </div>
        <el-divider />
        <div class="info-row"><span>当前项数 n</span><b style="color: var(--brand)">{{ cur.n }}</b></div>
        <div class="info-row"><span>当前项 aₙ</span><b>{{ fmt(cur.term) }}</b></div>
        <div class="info-row"><span>部分和 Sₙ</span><b style="color: #3b6ef6">{{ fmt(cur.sum) }}</b></div>
        <div class="info-row"><span>理论极限 S</span><b style="color: #22a06b">{{ target === null ? '不存在有限极限' : fmt(target) }}</b></div>
        <div class="info-row"><span>当前误差 |S-Sₙ|</span><b style="color: #e05252">{{ target === null ? '—' : fmt(Math.abs(target - cur.sum)) }}</b></div>
        <div class="info-row"><span>余项上界</span><el-tag size="small" :type="cur.bound === null ? 'info' : 'success'">{{ boundText }}</el-tag></div>
        <div class="formula"><code>{{ preset.note }}</code></div>
        <p class="small muted tip">幂级数 Σxᵏ 的收敛半径 R=1：|x|&lt;1 时余项按几何速度缩小；|x|≥1 时通项不趋于 0，因此不可能收敛。</p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot sum"></i> 部分和 Sₙ</span>
      <span><i class="dot target"></i> 理论极限</span>
      <span><i class="dot error"></i> 当前误差</span>
      <span><i class="dot future"></i> 尚未播放的部分和</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const SERIES = [
  { key: 'harmonic', label: '调和级数 Σ1/n', formula: 'Σ 1/n', note: 'aₙ→0 只是收敛的必要条件；调和级数的 Sₙ≈ln n+γ，仍缓慢趋向无穷。' },
  { key: 'geometric', label: '几何级数 Σ0.6ⁿ', formula: 'Σₙ₌₀∞ 0.6ⁿ', note: 'Sₙ=(1-qⁿ)/(1-q)，余项恰为 qⁿ/(1-q)。' },
  { key: 'p', label: 'p 级数 Σ1/n²', formula: 'Σ 1/n²', note: 'p=2>1，所以收敛；积分判别给出 Rₙ≤∫ₙ∞x⁻²dx=1/n。' },
  { key: 'alternating', label: '交错级数 Σ(-1)ⁿ⁺¹/n', formula: 'Σ (-1)ⁿ⁺¹/n', note: '正负项交替夹逼 ln2，莱布尼茨估计保证 |Rₙ|≤1/(n+1)。' },
  { key: 'power', label: '幂级数 Σxᵏ', formula: 'Σₖ₌₀∞ xᵏ', note: '当 |x|<1 时和为 1/(1-x)；越靠近边界，收敛越慢。' }
]

const seriesKey = ref('geometric')
const powerX = ref(0.75)
const maxN = ref(40)
const chartHost = ref(null)
const viewportWidth = ref(680)
let resizeObserver = null

const compact = computed(() => viewportWidth.value < 520)
const preset = computed(() => SERIES.find(item => item.key === seriesKey.value) || SERIES[0])
const target = computed(() => {
  if (seriesKey.value === 'geometric') return 1 / (1 - 0.6)
  if (seriesKey.value === 'p') return Math.PI * Math.PI / 6
  if (seriesKey.value === 'alternating') return Math.log(2)
  if (seriesKey.value === 'power' && Math.abs(powerX.value) < 1) return 1 / (1 - powerX.value)
  return null
})
const powerState = computed(() => {
  if (seriesKey.value !== 'power') return { type: 'muted-state', text: '切换到幂级数后可调' }
  if (Math.abs(powerX.value) < 1) return { type: 'inside', text: '|x|<1，在收敛区间内' }
  if (Math.abs(powerX.value) === 1) return { type: 'edge', text: '|x|=1，位于边界' }
  return { type: 'outside', text: '|x|>1，在收敛区间外' }
})

function termAt(n) {
  if (seriesKey.value === 'harmonic') return 1 / n
  if (seriesKey.value === 'geometric') return Math.pow(0.6, n - 1)
  if (seriesKey.value === 'p') return 1 / (n * n)
  if (seriesKey.value === 'alternating') return (n % 2 ? 1 : -1) / n
  return Math.pow(powerX.value, n - 1)
}
function remainderBound(n) {
  if (seriesKey.value === 'geometric') return Math.pow(0.6, n) / 0.4
  if (seriesKey.value === 'p') return 1 / n
  if (seriesKey.value === 'alternating') return 1 / (n + 1)
  if (seriesKey.value === 'power' && Math.abs(powerX.value) < 1) return Math.pow(Math.abs(powerX.value), n) / (1 - Math.abs(powerX.value))
  return null
}

const steps = computed(() => {
  const out = []
  let sum = 0
  for (let n = 1; n <= maxN.value; n++) {
    const term = termAt(n)
    sum += term
    const bound = remainderBound(n)
    const error = target.value === null ? null : Math.abs(target.value - sum)
    const convergence = target.value === null ? '没有有限极限' : `误差 ${error.toExponential(2)}`
    out.push({ n, term, sum, bound, desc: `累加第 ${n} 项 aₙ=${fmt(term)}，部分和 Sₙ=${fmt(sum)}；${convergence}${bound === null ? '，余项上界不适用。' : `，理论余项上界 ${fmt(bound)}。`}` })
  }
  return out
})
const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const boundText = computed(() => cur.value.bound === null ? '发散时不存在' : `≤ ${fmt(cur.value.bound)}`)

const values = computed(() => {
  const list = steps.value.map(item => item.sum)
  if (target.value !== null) list.push(target.value)
  return list.filter(Number.isFinite)
})
const yRange = computed(() => {
  const min = Math.min(...values.value)
  const max = Math.max(...values.value)
  const span = Math.max(0.2, max - min)
  return [min - span * 0.16, max + span * 0.16]
})
const yTicks = computed(() => Array.from({ length: 6 }, (_, i) => yRange.value[0] + (yRange.value[1] - yRange.value[0]) * i / 5))
const nTicks = computed(() => {
  const count = compact.value ? 4 : 6
  return Array.from({ length: count + 1 }, (_, i) => Math.max(1, Math.round(1 + (maxN.value - 1) * i / count))).filter((n, i, arr) => arr.indexOf(n) === i)
})
function mapX(n) { return 54 + (n - 1) / Math.max(1, maxN.value - 1) * 606 }
function mapY(value) { return 24 + (yRange.value[1] - value) / (yRange.value[1] - yRange.value[0]) * 302 }
function makePath(list) { return list.map((item, i) => `${i ? 'L' : 'M'}${mapX(item.n).toFixed(1)},${mapY(item.sum).toFixed(1)}`).join(' ') }
const fullPath = computed(() => makePath(steps.value))
const visiblePoints = computed(() => steps.value.slice(0, cur.value.n))
const currentPath = computed(() => makePath(visiblePoints.value))

function fmt(value) {
  if (!Number.isFinite(value)) return '—'
  const abs = Math.abs(value)
  return abs !== 0 && (abs < 0.0001 || abs > 9999) ? value.toExponential(3) : Number(value).toFixed(5)
}
function short(value) { return Math.abs(value) > 99 ? value.toExponential(1) : Number(value).toFixed(2) }

onMounted(() => {
  resizeObserver = new ResizeObserver(entries => {
    viewportWidth.value = Math.max(280, Math.floor(entries[0].contentRect.width))
  })
  if (chartHost.value) resizeObserver.observe(chartHost.value)
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  player.pause()
})
</script>

<style scoped>
.sr-wrap { display: flex; align-items: flex-start; gap: 18px; flex-wrap: wrap; }
.chart-host { flex: 2 1 560px; min-width: 0; }
.sr-svg { display: block; width: 100%; height: auto; min-height: 300px; }
.sr-panel { flex: 1 1 285px; min-width: 260px; }
.power-control { background: #f7f9fc; border: 1px solid #e5eaf2; border-radius: 9px; padding: 10px 12px; }
.control-title { font-size: 12px; font-weight: 600; color: #526071; }
.interval { margin-top: 2px; text-align: center; font-size: 12px; font-weight: 600; }
.interval.inside { color: #1a7a52; }
.interval.edge { color: #b46a15; }
.interval.outside { color: #c53d3d; }
.interval.muted-state { color: #8b95a3; }
.info-row { display: flex; justify-content: space-between; gap: 12px; padding: 6px 0; border-bottom: 1px dashed #edf0f5; font-size: 13px; }
.formula code { display: block; margin-top: 12px; padding: 9px 11px; border-radius: 7px; background: #f2f4f8; font-size: 12px; line-height: 1.65; }
.tip { line-height: 1.75; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; }
.dot.sum { background: #3b6ef6; }
.dot.target { background: #22a06b; }
.dot.error { background: #e05252; }
.dot.future { background: #cbd5e1; }
@media (max-width: 640px) {
  .sr-panel { min-width: 100%; }
  .sr-svg { min-height: 245px; }
}
</style>
