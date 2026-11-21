<template>
  <VisFrame title="概率分布 · 理论与频率的对照" desc="随着抽样次数增加，随机样本的频率直方图会逐渐逼近理论分布 —— 这就是频率学派对概率的理解" :player="player" :status-text="statusText" back-to="/knowledge/27">
    <template #extra>
      <el-select v-model="type" size="small" style="width:150px" @change="player.reset()">
        <el-option value="binom" label="二项分布 B(n,p)" />
        <el-option value="poisson" label="泊松分布 P(λ)" />
        <el-option value="normal" label="正态分布 N(μ,σ²)" />
        <el-option value="uniform" label="均匀分布 U(a,b)" />
        <el-option value="exp" label="指数分布 E(λ)" />
      </el-select>
      <el-button size="small" plain @click="reseed">换一批样本</el-button>
    </template>

    <div class="pd-wrap">
      <div class="pd-params">
        <label v-if="type === 'binom'">n <el-slider v-model="n" :min="2" :max="40" :step="1" style="width:150px" @input="player.reset()" /></label>
        <label v-if="type === 'binom'">p <el-slider v-model="p" :min="0.05" :max="0.95" :step="0.05" style="width:150px" @input="player.reset()" /></label>
        <label v-if="type === 'poisson'">λ <el-slider v-model="lam" :min="0.5" :max="15" :step="0.5" style="width:150px" @input="player.reset()" /></label>
        <label v-if="type === 'normal'">μ <el-slider v-model="mu" :min="-4" :max="4" :step="0.5" style="width:150px" @input="player.reset()" /></label>
        <label v-if="type === 'normal'">σ <el-slider v-model="sigma" :min="0.2" :max="4" :step="0.1" style="width:150px" @input="player.reset()" /></label>
        <label v-if="type === 'uniform'">a <el-slider v-model="ua" :min="-5" :max="2" :step="0.5" style="width:150px" @input="player.reset()" /></label>
        <label v-if="type === 'uniform'">b <el-slider v-model="ub" :min="0" :max="8" :step="0.5" style="width:150px" @input="player.reset()" /></label>
        <label v-if="type === 'exp'">λ <el-slider v-model="elam" :min="0.2" :max="3" :step="0.1" style="width:150px" @input="player.reset()" /></label>
      </div>

      <svg :width="W" :height="H" class="pd-svg">
        <line v-for="(g, i) in axisTicks" :key="'t'+i" :x1="mapX(g.v)" :y1="mapY(0)" :x2="mapX(g.v)" :y2="mapY(yMax)" stroke="#eef1f6" />
        <line :x1="mapX(x0)" :y1="mapY(0)" :x2="mapX(x1)" :y2="mapY(0)" stroke="#8b95a3" stroke-width="1.5" />
        <line :x1="mapX(x0)" :y1="mapY(0)" :x2="mapX(x0)" :y2="mapY(yMax)" stroke="#8b95a3" stroke-width="1.5" />
        <text v-for="(g, i) in axisTicks" :key="'tx'+i" :x="mapX(g.v)" :y="mapY(0) + 16" text-anchor="middle" font-size="10" fill="#8b95a3">{{ g.label }}</text>

        <!-- 理论分布 -->
        <template v-if="discrete">
          <g v-for="(b, i) in theoBars" :key="'tb'+i">
            <line :x1="b.x" :y1="mapY(b.p)" :x2="b.x" :y2="mapY(0)" stroke="#3b6ef6" stroke-width="3" />
            <circle :cx="b.x" :cy="mapY(b.p)" r="3.5" fill="#3b6ef6" />
          </g>
        </template>
        <path v-else :d="pdfPath" fill="none" stroke="#3b6ef6" stroke-width="2.5" />

        <!-- 经验直方图 -->
        <rect
          v-for="(b, i) in empBars" :key="'eb'+i"
          :x="b.x" :y="mapY(b.h)" :width="b.w" :height="Math.max(0, mapY(0) - mapY(b.h))"
          fill="#f2994a" fill-opacity="0.55" stroke="#f2994a"
        />
        <text :x="12" :y="18" font-size="12" fill="#8b95a3">样本数 N = {{ cur.N }}</text>
      </svg>

      <div class="pd-panel">
        <div class="info-row"><span>分布</span><b>{{ distName }}</b></div>
        <div class="info-row"><span>理论期望 E(X)</span><b style="color:var(--brand)">{{ fmt(theoMean) }}</b></div>
        <div class="info-row"><span>样本均值 x̄</span><b style="color:#b46a15">{{ fmt(empMean) }}</b></div>
        <div class="info-row"><span>理论方差 D(X)</span><b style="color:var(--brand)">{{ fmt(theoVar) }}</b></div>
        <div class="info-row"><span>样本方差 s²</span><b style="color:#b46a15">{{ fmt(empVar) }}</b></div>
        <div class="info-row">
          <span>均值相对误差</span>
          <el-tag size="small" :type="meanErr < 0.05 ? 'success' : 'warning'">{{ (meanErr * 100).toFixed(2) }}%</el-tag>
        </div>
        <el-divider />
        <div class="tbl">
          <div class="tbl-head"><span>N</span><span>样本均值</span><span>样本方差</span></div>
          <div v-for="(s, i) in player.steps.value" :key="i" class="tbl-row" :class="{ active: i === player.idx.value }" @click="player.seek(i)">
            <span>{{ s.N }}</span><span>{{ fmt(s.mean) }}</span><span>{{ fmt(s.var) }}</span>
          </div>
        </div>
        <p class="small muted tip">{{ note }}</p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> 理论分布</span>
      <span><i class="dot" style="background:#f2994a"></i> 样本频率直方图</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const type = ref('binom')
const n = ref(20), p = ref(0.5)
const lam = ref(5)
const mu = ref(0), sigma = ref(1)
const ua = ref(-2), ub = ref(3)
const elam = ref(1)
const seed = ref(20240928)

const discrete = computed(() => type.value === 'binom' || type.value === 'poisson')
const distName = computed(() => ({
  binom: `二项分布 B(${n.value}, ${p.value})`,
  poisson: `泊松分布 P(${lam.value})`,
  normal: `正态分布 N(${mu.value}, ${sigma.value}²)`,
  uniform: `均匀分布 U(${ua.value}, ${ub.value})`,
  exp: `指数分布 E(${elam.value})`
})[type.value])

const note = computed(() => ({
  binom: `n 次独立伯努利试验的成功次数：E=np=${fmt((n.value * p.value).toFixed(2))}，D=np(1-p)。n 大 p 小时可用泊松近似，n 大时可用正态近似。`,
  poisson: '描述单位时间/空间内稀有事件发生次数，期望与方差都等于 λ。λ 越大越接近正态。',
  normal: '钟形对称曲线，μ 决定中心位置，σ 决定胖瘦。约 68% 落在 μ±σ，95% 落在 μ±2σ。',
  uniform: '区间内等可能，密度恒为 1/(b-a)。',
  exp: '描述泊松过程中事件间隔时间，具有无记忆性：P(X>s+t|X>s)=P(X>t)。'
})[type.value])

// ---- 随机数（可复现） ----
function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}
function reseed() { seed.value = Math.floor(Math.random() * 1e9); player.reset() }

const TOTAL = 3600
const samples = computed(() => {
  const rnd = mulberry32(seed.value)
  const out = []
  const gauss = () => {
    let u = 0, v = 0
    while (u === 0) u = rnd()
    while (v === 0) v = rnd()
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v)
  }
  for (let i = 0; i < TOTAL; i++) {
    let v = 0
    if (type.value === 'binom') {
      for (let k = 0; k < n.value; k++) if (rnd() < p.value) v++
    } else if (type.value === 'poisson') {
      const L = Math.exp(-lam.value)
      let k = 0, pr = 1
      do { k++; pr *= rnd() } while (pr > L)
      v = k - 1
    } else if (type.value === 'normal') {
      v = mu.value + sigma.value * gauss()
    } else if (type.value === 'uniform') {
      v = ua.value + (ub.value - ua.value) * rnd()
    } else {
      v = -Math.log(1 - rnd()) / elam.value
    }
    out.push(v)
  }
  return out
})

const theoMean = computed(() => {
  if (type.value === 'binom') return n.value * p.value
  if (type.value === 'poisson') return lam.value
  if (type.value === 'normal') return mu.value
  if (type.value === 'uniform') return (ua.value + ub.value) / 2
  return 1 / elam.value
})
const theoVar = computed(() => {
  if (type.value === 'binom') return n.value * p.value * (1 - p.value)
  if (type.value === 'poisson') return lam.value
  if (type.value === 'normal') return sigma.value * sigma.value
  if (type.value === 'uniform') return Math.pow(ub.value - ua.value, 2) / 12
  return 1 / (elam.value * elam.value)
})

const x0 = computed(() => {
  if (type.value === 'binom') return -0.5
  if (type.value === 'poisson') return -0.5
  if (type.value === 'normal') return mu.value - 4 * sigma.value
  if (type.value === 'uniform') return ua.value - 0.5
  return 0
})
const x1 = computed(() => {
  if (type.value === 'binom') return n.value + 0.5
  if (type.value === 'poisson') return lam.value + 4 * Math.sqrt(lam.value) + 0.5
  if (type.value === 'normal') return mu.value + 4 * sigma.value
  if (type.value === 'uniform') return ub.value + 0.5
  return 5 / elam.value
})

// 概率质量 / 密度
function pmf(k) {
  if (type.value === 'binom') {
    const nn = n.value, pp = p.value
    let lf = 0
    for (let i = 1; i <= nn; i++) lf += Math.log(i)
    const lchoose = lf - logFact(k) - logFact(nn - k)
    return Math.exp(lchoose + k * Math.log(pp) + (nn - k) * Math.log(1 - pp))
  }
  if (type.value === 'poisson') return Math.exp(-lam.value + k * Math.log(lam.value) - logFact(k))
  return 0
}
function logFact(k) { let s = 0; for (let i = 1; i <= k; i++) s += Math.log(i); return s }
function pdf(x) {
  if (type.value === 'normal') {
    const s = sigma.value
    return Math.exp(-Math.pow(x - mu.value, 2) / (2 * s * s)) / (s * Math.sqrt(2 * Math.PI))
  }
  if (type.value === 'uniform') {
    return x >= ua.value && x <= ub.value ? 1 / Math.max(1e-9, ub.value - ua.value) : 0
  }
  if (type.value === 'exp') return x >= 0 ? elam.value * Math.exp(-elam.value * x) : 0
  return 0
}

const yMax = computed(() => {
  if (discrete.value) {
    let mx = 0
    for (let k = Math.max(0, Math.ceil(x0.value)); k <= Math.floor(x1.value); k++) mx = Math.max(mx, pmf(k))
    return Math.max(0.05, mx * 1.15)
  }
  let mx = 0
  for (let i = 0; i <= 100; i++) mx = Math.max(mx, pdf(x0.value + ((x1.value - x0.value) * i) / 100))
  return Math.max(0.05, mx * 1.15)
})

const W = 620, H = 300, padL = 42, padR = 16, padT = 26, padB = 34
function mapX(x) { return padL + ((x - x0.value) / (x1.value - x0.value)) * (W - padL - padR) }
function mapY(y) { return padT + ((yMax.value - y) / yMax.value) * (H - padT - padB) }

const axisTicks = computed(() => {
  const out = []
  const cnt = 8
  for (let i = 0; i <= cnt; i++) {
    const v = x0.value + ((x1.value - x0.value) * i) / cnt
    out.push({ v, label: Number(v.toFixed(discrete.value ? 0 : 1)).toString() })
  }
  return out
})

const theoBars = computed(() => {
  if (!discrete.value) return []
  const out = []
  for (let k = Math.max(0, Math.ceil(x0.value)); k <= Math.floor(x1.value); k++) {
    out.push({ k, x: mapX(k), p: pmf(k) })
  }
  return out
})
const pdfPath = computed(() => {
  if (discrete.value) return ''
  let d = ''
  const N = 240
  for (let i = 0; i <= N; i++) {
    const x = x0.value + ((x1.value - x0.value) * i) / N
    d += (i === 0 ? 'M' : 'L') + mapX(x).toFixed(2) + ' ' + mapY(pdf(x)).toFixed(2) + ' '
  }
  return d
})

const BIN_N = discrete.value ? 1 : 40
const empBars = computed(() => {
  const arr = cur.value.list
  if (!arr.length) return []
  if (discrete.value) {
    const counts = {}
    for (const v of arr) { const k = Math.round(v); counts[k] = (counts[k] || 0) + 1 }
    return Object.keys(counts).map(k => ({
      x: mapX(Number(k)) - 9, w: 18, h: counts[k] / arr.length
    }))
  }
  const nb = 40
  const w = (x1.value - x0.value) / nb
  const counts = new Array(nb).fill(0)
  for (const v of arr) {
    let idx = Math.floor((v - x0.value) / w)
    if (idx < 0) idx = 0
    if (idx >= nb) idx = nb - 1
    counts[idx]++
  }
  return counts.map((c, i) => ({
    x: mapX(x0.value + i * w),
    w: Math.max(1, mapX(x0.value + (i + 1) * w) - mapX(x0.value + i * w) - 1),
    h: c / (arr.length * w)
  }))
})

const STEP_N = 12
const PER = Math.floor(TOTAL / STEP_N)
const steps = computed(() => {
  const all = samples.value
  const out = []
  for (let s = 1; s <= STEP_N; s++) {
    const N = s * PER
    const list = all.slice(0, N)
    let sum = 0
    for (const v of list) sum += v
    const mean = sum / list.length
    let vs = 0
    for (const v of list) vs += (v - mean) * (v - mean)
    const vari = list.length > 1 ? vs / (list.length - 1) : 0
    out.push({
      N, list, mean, var: vari,
      desc: `已抽 ${N} 个样本：样本均值 = ${mean.toFixed(4)}（理论 ${theoMean.value.toFixed(4)}），样本方差 = ${vari.toFixed(4)}（理论 ${theoVar.value.toFixed(4)}）`
    })
  }
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || { N: 0, list: [], mean: 0, var: 0, desc: '' })
const statusText = computed(() => cur.value.desc)
const empMean = computed(() => cur.value.mean)
const empVar = computed(() => cur.value.var)
const meanErr = computed(() => (Math.abs(theoMean.value) < 1e-9 ? Math.abs(empMean.value) : Math.abs((empMean.value - theoMean.value) / theoMean.value)))

function fmt(v) {
  if (v === null || v === undefined || !isFinite(v)) return '-'
  return Number(v).toFixed(4).toString()
}
</script>

<style scoped>
.pd-wrap { display: flex; gap: 18px; align-items: flex-start; flex-wrap: wrap; }
.pd-params { width: 100%; display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 4px; }
.pd-params label { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text-2); }
.pd-svg { background: #fcfdff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.pd-panel { flex: 1; min-width: 290px; }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.tbl { font-size: 12px; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
.tbl-head { display: grid; grid-template-columns: 1fr 1.2fr 1.2fr; background: #f6f8fb; padding: 7px 10px; font-weight: 600; }
.tbl-row { display: grid; grid-template-columns: 1fr 1.2fr 1.2fr; padding: 6px 10px; border-top: 1px solid #f0f2f6; cursor: pointer; }
.tbl-row:hover { background: #f6f8fb; }
.tbl-row.active { background: var(--brand-light); color: var(--brand); font-weight: 600; }
.tip { margin-top: 10px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
