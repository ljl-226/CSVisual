<template>
  <VisFrame title="大数定律 · 频率的稳定性" desc="独立重复试验中，样本均值依概率收敛到数学期望 E(X)：试验次数越大，样本均值偏离期望超过 ε 的概率趋于 0" :player="player" :status-text="statusText" back-to="/knowledge/61">
    <template #extra>
      <el-select v-model="distKey" size="small" style="width:170px" @change="resample">
        <el-option v-for="d in DISTS" :key="d.key" :value="d.key" :label="d.label" />
      </el-select>
      <el-select v-model="nMax" size="small" style="width:100px" @change="resample">
        <el-option :value="500" label="500 次" />
        <el-option :value="2000" label="2000 次" />
        <el-option :value="5000" label="5000 次" />
      </el-select>
      <el-button size="small" plain @click="resample">重新抽样</el-button>
    </template>

    <div class="ll-wrap">
      <svg :width="W" :height="H" class="ll-svg">
        <defs><clipPath id="llClip"><rect :x="padL" :y="padT" :width="W - padL - padR" :height="H - padT - padB" /></clipPath></defs>
        <g clip-path="url(#llClip)">
          <line v-for="g in yTicks" :key="'t' + g" :x1="padL" :y1="mapY(g)" :x2="W - padR" :y2="mapY(g)" stroke="#eef1f6" />
          <!-- 95% 置信带：μ ± 1.96σ/√n -->
          <path :d="bandPath" fill="#3b6ef6" fill-opacity="0.1" stroke="none" />
          <!-- 期望 μ 基准线 -->
          <line :x1="padL" :y1="mapY(mu)" :x2="W - padR" :y2="mapY(mu)" stroke="#22a06b" stroke-width="2" />
          <!-- 样本均值收敛曲线 -->
          <polyline :points="meanLine" fill="none" stroke="#3b6ef6" stroke-width="2.2" />
          <circle v-for="(p, i) in shownPoints" :key="'p' + i" :cx="p.x" :cy="p.y" r="3" fill="#3b6ef6" fill-opacity="0.45" />
          <circle :cx="mapX(Math.max(1, cur.n))" :cy="mapY(cur.mean)" r="6" fill="#3b6ef6" stroke="#fff" stroke-width="2" />
        </g>
        <text :x="padL" :y="padT - 6" font-size="12" fill="#8b95a3">样本均值 X̄ₙ（横轴为试验次数 n，对数刻度）</text>
        <text :x="W - padR" :y="mapY(mu) - 6" text-anchor="end" font-size="11" fill="#14764e">期望 μ = {{ fmt(mu, 3) }}</text>
        <text v-for="g in yTicks" :key="'ty' + g" :x="padL - 8" :y="mapY(g) + 4" text-anchor="end" font-size="10.5" fill="#8b95a3">{{ fmt(g, 2) }}</text>
        <text v-for="c in checkpoints" :key="'tx' + c" :x="mapX(c)" :y="H - padB + 16" text-anchor="middle" font-size="10" fill="#8b95a3">{{ c }}</text>
      </svg>

      <div class="ll-panel">
        <div class="def-box">
          <div class="small muted">教材公式（浙大《概率论与数理统计》）</div>
          <code>切比雪夫大数定律：∀ε>0，lim P{|X̄ₙ - μ| ≥ ε} = 0
伯努利大数定律：频率 fₙ(A) → P(A)（依概率收敛）</code>
        </div>
        <el-divider />
        <div class="info-row"><span>理论期望 E(X) = μ</span><b style="color:var(--success)">{{ fmt(mu, 4) }}</b></div>
        <div class="info-row"><span>理论标准差 σ</span><b>{{ fmt(sigma, 4) }}</b></div>
        <div class="info-row"><span>已抽样次数 n</span><b>{{ cur.n }}</b></div>
        <div class="info-row"><span>样本均值 X̄ₙ</span><b style="color:var(--brand)">{{ fmt(cur.mean, 4) }}</b></div>
        <div class="info-row"><span>绝对偏差 |X̄ₙ - μ|</span><b style="color:var(--danger)">{{ fmt(cur.err, 4) }}</b></div>
        <div class="info-row"><span>理论标准误 σ/√n</span><b>{{ fmt(sigma / Math.sqrt(Math.max(1, cur.n)), 4) }}</b></div>
        <div class="info-row"><span>是否落在 95% 置信带内</span>
          <el-tag size="small" :type="cur.err <= 1.96 * sigma / Math.sqrt(Math.max(1, cur.n)) ? 'success' : 'warning'">
            {{ cur.err <= 1.96 * sigma / Math.sqrt(Math.max(1, cur.n)) ? '是' : '否' }}
          </el-tag>
        </div>
        <p class="small muted tip">考点：大数定律保证频率（样本均值）稳定于概率（期望）；中心极限定理进一步给出偏差的分布形态 N(0, σ²/n)，故 95% 的样本应落在 μ ± 1.96σ/√n 带内，带的宽度按 1/√n 收缩。</p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> 样本均值 X̄ₙ 收敛曲线</span>
      <span><i class="dot" style="background:#22a06b"></i> 理论期望 μ</span>
      <span><i class="dot" style="background:#cfe0ff"></i> μ ± 1.96σ/√n（95% 置信带）</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const DISTS = [
  { key: 'coin', label: '掷硬币正面次数（p = 0.5）', mu: 0.5, sigma: 0.5, rand: r => (r() < 0.5 ? 0 : 1) },
  { key: 'bern', label: '不均匀硬币（p = 0.3）', mu: 0.3, sigma: Math.sqrt(0.21), rand: r => (r() < 0.3 ? 0 : 1) },
  { key: 'dice', label: '掷均匀骰子（1~6 点）', mu: 3.5, sigma: Math.sqrt(35 / 12), rand: r => 1 + Math.floor(r() * 6) },
  { key: 'exp', label: '指数分布 Exp(1)（重尾）', mu: 1, sigma: 1, rand: r => -Math.log(1 - r()) }
]

const distKey = ref('dice')
const nMax = ref(2000)
const seed = ref(20240915)
const dist = computed(() => DISTS.find(d => d.key === distKey.value) || DISTS[0])
const mu = computed(() => dist.value.mu)
const sigma = computed(() => dist.value.sigma)
function resample() { seed.value = (seed.value + 7919) % 2147483647; player.reset() }

const W = 560, H = 340, padL = 52, padR = 20, padT = 26, padB = 30
// 检查点：几何增长便于同时看清前期剧烈波动与后期稳定
const ALL_CHECK = [1, 2, 3, 5, 8, 12, 20, 32, 50, 80, 125, 200, 320, 500, 800, 1250, 2000, 3200, 5000]
const checkpoints = computed(() => ALL_CHECK.filter(c => c <= nMax.value))

// 可复现的伪随机数发生器（mulberry32）
function mulberry32(a) {
  return function () {
    a = (a + 0x6D2B79F5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

// 只生成一次样本，之后所有检查点共享同一条随机序列
const samples = computed(() => {
  const rnd = mulberry32(seed.value)
  const total = checkpoints.value[checkpoints.value.length - 1] || 1
  const out = []
  for (let i = 0; i < total; i++) out.push(dist.value.rand(rnd))
  return out
})

const steps = computed(() => {
  const out = []
  const xs = samples.value
  let sum = 0, pos = 0
  for (const c of checkpoints.value) {
    while (pos < c && pos < xs.length) { sum += xs[pos]; pos++ }
    const mean = sum / Math.max(1, pos)
    const err = Math.abs(mean - mu.value)
    out.push({
      n: c, mean, err,
      desc: `试验 ${c} 次：样本均值 = ${mean.toFixed(4)}，与期望 ${mu.value} 相差 ${err.toFixed(4)}，理论标准误 σ/√n = ${(sigma.value / Math.sqrt(c)).toFixed(4)}`
    })
  }
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)

// 纵轴范围：覆盖期望 ± 若干倍标准误（以第 5 个检查点为尺度，避免前几点把纵轴拉爆）
const span = computed(() => {
  const ref = Math.max(checkpoints.value[3] || 20, 20)
  return Math.max(0.25, 2.4 * sigma.value / Math.sqrt(ref))
})
function mapX(nn) {
  const hi = checkpoints.value[checkpoints.value.length - 1] || 1
  const t = Math.log(Math.max(1, nn)) / Math.log(hi)
  return padL + t * (W - padL - padR)
}
function mapY(v) { return padT + ((mu.value + span.value - v) / (2 * span.value)) * (H - padT - padB) }
const yTicks = computed(() => {
  const out = []
  for (let i = 0; i <= 6; i++) out.push(mu.value - span.value + (2 * span.value * i) / 6)
  return out
})

const shownPoints = computed(() => steps.value.slice(0, player.idx.value + 1).map(s => ({ x: mapX(s.n), y: mapY(s.mean) })))
const meanLine = computed(() => shownPoints.value.map(p => p.x.toFixed(1) + ',' + p.y.toFixed(1)).join(' '))

// 置信带 ±1.96σ/√n，按对数刻度均匀取样画出喇叭形收缩带
const bandPath = computed(() => {
  const hi = checkpoints.value[checkpoints.value.length - 1] || 1
  const up = [], dn = []
  for (let i = 0; i <= 80; i++) {
    const nn = Math.max(1, Math.pow(hi, i / 80))
    const w = 1.96 * sigma.value / Math.sqrt(nn)
    up.push([mapX(nn), mapY(mu.value + w)])
    dn.push([mapX(nn), mapY(mu.value - w)])
  }
  let d = 'M' + up.map(p => p[0].toFixed(1) + ' ' + p[1].toFixed(1)).join('L')
  for (let i = dn.length - 1; i >= 0; i--) d += 'L' + dn[i][0].toFixed(1) + ' ' + dn[i][1].toFixed(1)
  return d + 'Z'
})

function fmt(v, d) {
  if (v === null || v === undefined || !isFinite(v)) return '-'
  return Number(v.toFixed(d || 3)).toString()
}
</script>

<style scoped>
.ll-wrap { display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap; }
.ll-svg { background: #fcfdff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.ll-panel { flex: 1; min-width: 300px; }
.def-box code { background: #f2f4f8; padding: 8px 10px; border-radius: 6px; display: block; font-size: 12px; line-height: 1.7; white-space: pre-wrap; }
.info-row { display: flex; justify-content: space-between; align-items: center; gap: 10px; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.tip { margin-top: 10px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
