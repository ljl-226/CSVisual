<template>
  <VisFrame title="中心极限定理 · 样本均值的正态化" desc="无论总体是什么形状，只要 n 足够大，样本均值 X̄ 都近似服从 N(μ, σ²/n) —— 这是统计推断的基石" :player="player" :status-text="statusText" back-to="/knowledge/28">
    <template #extra>
      <el-select v-model="pop" size="small" style="width:150px" @change="player.reset()">
        <el-option value="uniform" label="总体：均匀分布" />
        <el-option value="exp" label="总体：指数分布（右偏）" />
        <el-option value="bern" label="总体：伯努利（0/1）" />
        <el-option value="dice" label="总体：掷骰子 1~6" />
        <el-option value="bi" label="总体：双峰分布" />
      </el-select>
      <span class="small muted">样本容量 n</span>
      <el-slider v-model="nIdx" :min="0" :max="5" :step="1" style="width:120px" :show-tooltip="false" @input="player.reset()" />
      <b class="small">n = {{ N_OPTIONS[nIdx] }}</b>
    </template>

    <div class="cl-wrap">
      <svg :width="W" :height="H" class="cl-svg">
        <line :x1="mapX(x0)" :y1="mapY(0)" :x2="mapX(x1)" :y2="mapY(0)" stroke="#8b95a3" stroke-width="1.5" />
        <text v-for="(g, i) in axisTicks" :key="'t'+i" :x="mapX(g)" :y="mapY(0) + 16" text-anchor="middle" font-size="10" fill="#8b95a3">{{ fmt1(g) }}</text>

        <!-- 样本均值直方图 -->
        <rect
          v-for="(b, i) in empBars" :key="'b'+i"
          :x="b.x" :y="mapY(b.h)" :width="b.w" :height="Math.max(0, mapY(0) - mapY(b.h))"
          fill="#f2994a" fill-opacity="0.6" stroke="#f2994a"
        />
        <!-- 理论正态曲线 -->
        <path :d="normalPath" fill="none" stroke="#3b6ef6" stroke-width="2.5" />
        <!-- 总体均值位置 -->
        <line :x1="mapX(popMean)" :y1="mapY(0)" :x2="mapX(popMean)" :y2="mapY(yMax)" stroke="#e05252" stroke-dasharray="5 4" />
        <text :x="mapX(popMean) + 4" :y="mapY(yMax) + 12" font-size="11" fill="#e05252">μ = {{ fmt1(popMean) }}</text>
        <text :x="12" :y="18" font-size="12" fill="#8b95a3">已抽取 {{ cur.count }} 组样本，每组 n = {{ n }}</text>
      </svg>

      <!-- 总体形状对照 -->
      <div class="pop-strip">
        <span class="small muted">总体分布形状（与上面完全不同的形状）</span>
        <svg :width="W" :height="86" class="pop-svg">
          <rect
            v-for="(b, i) in popBars" :key="'p'+i"
            :x="b.x" :y="b.y" :width="b.w" :height="b.h"
            fill="#8b95a3" fill-opacity="0.45"
          />
        </svg>
      </div>

      <div class="cl-panel">
        <div class="formula">
          <code>X̄ ~ N( μ , σ²/n )　　即　( X̄ - μ ) / (σ/√n) → N(0,1)</code>
        </div>
        <el-divider />
        <div class="info-row"><span>总体均值 μ</span><b style="color:#e05252">{{ fmt(popMean) }}</b></div>
        <div class="info-row"><span>总体标准差 σ</span><b>{{ fmt(Math.sqrt(popVar)) }}</b></div>
        <div class="info-row"><span>标准误 σ/√n（理论）</span><b style="color:var(--brand)">{{ fmt(Math.sqrt(popVar / n)) }}</b></div>
        <div class="info-row"><span>样本均值的均值</span><b>{{ fmt(cur.mean) }}</b></div>
        <div class="info-row"><span>样本均值的标准差（实测）</span><b style="color:#b46a15">{{ fmt(cur.sd) }}</b></div>
        <div class="info-row">
          <span>实测 / 理论 标准误</span>
          <el-tag size="small" :type="Math.abs(cur.sd / Math.sqrt(popVar / n) - 1) < 0.08 ? 'success' : 'warning'">
            {{ fmt(cur.sd / Math.sqrt(popVar / n)) }}
          </el-tag>
        </div>
        <el-divider />
        <div class="tbl">
          <div class="tbl-head"><span>样本组数</span><span>均值之均值</span><span>实测标准误</span></div>
          <div v-for="(s, i) in player.steps.value" :key="i" class="tbl-row" :class="{ active: i === player.idx.value }" @click="player.seek(i)">
            <span>{{ s.count }}</span><span>{{ fmt(s.mean) }}</span><span>{{ fmt(s.sd) }}</span>
          </div>
        </div>
        <p class="small muted tip">把 n 从 1 调到 30：直方图会先失去总体原有的偏斜/双峰形状，逐渐变成钟形，同时宽度按 1/√n 收窄——这就是中心极限定理。</p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#f2994a"></i> 样本均值的频率直方图</span>
      <span><i class="dot" style="background:#3b6ef6"></i> 理论正态曲线 N(μ, σ²/n)</span>
      <span><i class="dot" style="background:#e05252"></i> 总体均值 μ</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const N_OPTIONS = [1, 2, 5, 10, 30, 50]
const nIdx = ref(3)
const n = computed(() => N_OPTIONS[nIdx.value])
const pop = ref('exp')

const POPS = {
  uniform: { name: 'U(0,1)', mean: 0.5, var: 1 / 12, lo: 0, hi: 1 },
  exp: { name: 'E(1)', mean: 1, var: 1, lo: 0, hi: 6 },
  bern: { name: 'Bern(0.3)', mean: 0.3, var: 0.21, lo: 0, hi: 1 },
  dice: { name: '骰子 1~6', mean: 3.5, var: 35 / 12, lo: 1, hi: 6 },
  bi: { name: '双峰', mean: 0.8, var: 3.72, lo: -5, hi: 6 }
}
const popMean = computed(() => POPS[pop.value].mean)
const popVar = computed(() => POPS[pop.value].var)

function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}
function drawOne(rnd) {
  if (pop.value === 'uniform') return rnd()
  if (pop.value === 'exp') return -Math.log(1 - rnd())
  if (pop.value === 'bern') return rnd() < 0.3 ? 1 : 0
  if (pop.value === 'dice') return 1 + Math.floor(rnd() * 6)
  // 双峰：0.3·N(-2,0.6²) + 0.7·N(2,0.6²)
  let u = 0, v = 0
  while (u === 0) u = rnd()
  while (v === 0) v = rnd()
  const g = Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v)
  return rnd() < 0.3 ? -2 + 0.6 * g : 2 + 0.6 * g
}

const GROUPS = 3600
// 预生成：GROUPS 组，每组最多 50 个样本
const rawSamples = computed(() => {
  const rnd = mulberry32(20240928)
  const maxN = 50
  const out = []
  for (let g = 0; g < GROUPS; g++) {
    const row = []
    for (let i = 0; i < maxN; i++) row.push(drawOne(rnd))
    out.push(row)
  }
  return out
})

const means = computed(() => rawSamples.value.map(row => {
  let s = 0
  for (let i = 0; i < n.value; i++) s += row[i]
  return s / n.value
}))

const x0 = computed(() => popMean.value - 3.5 * Math.sqrt(popVar.value))
const x1 = computed(() => popMean.value + 3.5 * Math.sqrt(popVar.value))
const yMax = computed(() => {
  const sd = Math.sqrt(popVar.value / n.value)
  const peak = 1 / (sd * Math.sqrt(2 * Math.PI))
  return Math.max(0.2, peak * 1.25)
})

const W = 620, H = 300, padL = 44, padR = 16, padT = 26, padB = 34
function mapX(x) { return padL + ((x - x0.value) / (x1.value - x0.value)) * (W - padL - padR) }
function mapY(y) { return padT + ((yMax.value - y) / yMax.value) * (H - padT - padB) }

const axisTicks = computed(() => {
  const out = []
  for (let i = 0; i <= 8; i++) out.push(x0.value + ((x1.value - x0.value) * i) / 8)
  return out
})

const STEP_N = 12
const PER = Math.floor(GROUPS / STEP_N)
const steps = computed(() => {
  const all = means.value
  const out = []
  for (let s = 1; s <= STEP_N; s++) {
    const count = s * PER
    const list = all.slice(0, count)
    let sum = 0
    for (const v of list) sum += v
    const mean = sum / list.length
    let vs = 0
    for (const v of list) vs += (v - mean) * (v - mean)
    const sd = Math.sqrt(vs / Math.max(1, list.length - 1))
    out.push({
      count, list, mean, sd,
      desc: `n = ${n.value}，${count} 组样本：均值之均值 = ${mean.toFixed(4)}（总体 μ = ${popMean.value.toFixed(4)}），标准误实测 ${sd.toFixed(4)} vs 理论 ${Math.sqrt(popVar.value / n.value).toFixed(4)}`
    })
  }
  return out
})
const player = usePlayer(steps)
const cur = computed(() => player.current.value || { count: 0, list: [], mean: 0, sd: 0, desc: '' })
const statusText = computed(() => cur.value.desc)

const NB = 46
const empBars = computed(() => {
  const list = cur.value.list
  if (!list.length) return []
  const w = (x1.value - x0.value) / NB
  const counts = new Array(NB).fill(0)
  for (const v of list) {
    let i = Math.floor((v - x0.value) / w)
    if (i < 0) i = 0
    if (i >= NB) i = NB - 1
    counts[i]++
  }
  return counts.map((c, i) => ({
    x: mapX(x0.value + i * w),
    w: Math.max(1, mapX(x0.value + (i + 1) * w) - mapX(x0.value + i * w) - 1),
    h: c / (list.length * w)
  }))
})

const normalPath = computed(() => {
  const sd = Math.sqrt(popVar.value / n.value)
  let d = ''
  const N = 200
  for (let i = 0; i <= N; i++) {
    const x = x0.value + ((x1.value - x0.value) * i) / N
    const y = Math.exp(-Math.pow(x - popMean.value, 2) / (2 * sd * sd)) / (sd * Math.sqrt(2 * Math.PI))
    d += (i === 0 ? 'M' : 'L') + mapX(x).toFixed(2) + ' ' + Math.min(H, mapY(y)).toFixed(2) + ' '
  }
  return d
})

// 总体形状（小图）
const popBars = computed(() => {
  const rnd = mulberry32(777)
  const vals = []
  for (let i = 0; i < 4000; i++) vals.push(drawOne(rnd))
  const plo = POPS[pop.value].lo, phi = POPS[pop.value].hi
  const nb = 60
  const w = (phi - plo) / nb
  const counts = new Array(nb).fill(0)
  for (const v of vals) {
    let i = Math.floor((v - plo) / w)
    if (i < 0) i = 0
    if (i >= nb) i = nb - 1
    counts[i]++
  }
  const mx = Math.max(...counts) || 1
  const bw = (W - 20) / nb
  return counts.map((c, i) => {
    const h = (c / mx) * 66
    return { x: 10 + i * bw, w: Math.max(1, bw - 1), y: 74 - h, h }
  })
})

function fmt(v) { return isFinite(v) ? Number(v).toFixed(4).toString() : '-' }
function fmt1(v) { return Number(v).toFixed(1).toString() }
</script>

<style scoped>
.cl-wrap { display: flex; gap: 18px; align-items: flex-start; flex-wrap: wrap; }
.cl-svg { background: #fcfdff; border: 1px solid var(--border); border-radius: 10px; }
.pop-strip { width: 100%; }
.pop-strip .small { display: block; margin-bottom: 2px; }
.pop-svg { background: #f7f9fc; border: 1px solid var(--border); border-radius: 8px; }
.cl-panel { flex: 1; min-width: 300px; }
.formula code { background: #f2f4f8; padding: 8px 10px; border-radius: 6px; display: block; font-size: 12px; line-height: 1.7; }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.tbl { font-size: 12px; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
.tbl-head { display: grid; grid-template-columns: 1fr 1.2fr 1.2fr; background: #f6f8fb; padding: 7px 10px; font-weight: 600; }
.tbl-row { display: grid; grid-template-columns: 1fr 1.2fr 1.2fr; padding: 6px 10px; border-top: 1px solid #f0f2f6; cursor: pointer; }
.tbl-row:hover { background: #f6f8fb; }
.tbl-row.active { background: var(--brand-light); color: var(--brand); font-weight: 600; }
.tip { margin-top: 10px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
