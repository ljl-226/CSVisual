<template>
  <VisFrame title="泰勒公式 · 用多项式逼近函数" desc="在展开点 x₀ 处逐阶增加多项式项，n 阶泰勒多项式 Pₙ 越来越贴合 f(x)，拉格朗日余项 Rₙ 随之快速下降" :player="player" :status-text="statusText" back-to="/knowledge/55">
    <template #extra>
      <el-select v-model="presetKey" size="small" style="width:170px" @change="onPreset">
        <el-option v-for="p in PRESETS" :key="p.key" :value="p.key" :label="p.label" />
      </el-select>
      <span class="small muted">展开点</span>
      <el-slider v-model="x0" :min="x0Min" :max="x0Max" :step="0.25" style="width:110px" :show-tooltip="false" @change="player.reset()" />
      <span class="small muted">x₀ = {{ x0 }}</span>
      <span class="small muted">最高阶</span>
      <el-slider v-model="maxN" :min="2" :max="10" :step="1" style="width:100px" :show-tooltip="false" @change="player.reset()" />
    </template>

    <div class="ty-wrap">
      <svg :width="W" :height="H" class="ty-svg">
        <line v-for="g in xGrid" :key="'gx' + g" :x1="mapX(g)" :y1="mapY(rg0)" :x2="mapX(g)" :y2="mapY(rg1)" stroke="#eef1f6" />
        <line v-for="g in yGrid" :key="'gy' + g" :x1="mapX(dm0)" :y1="mapY(g)" :x2="mapX(dm1)" :y2="mapY(g)" stroke="#eef1f6" />
        <line :x1="mapX(dm0)" :y1="mapY(0)" :x2="mapX(dm1)" :y2="mapY(0)" stroke="#8b95a3" stroke-width="1.5" />
        <line :x1="mapX(0)" :y1="mapY(rg0)" :x2="mapX(0)" :y2="mapY(rg1)" stroke="#8b95a3" stroke-width="1.5" />

        <!-- 原函数 f(x) -->
        <path :d="curveF" fill="none" stroke="#1f2733" stroke-width="2.2" />
        <!-- n 阶泰勒多项式 Pₙ(x) -->
        <path :d="curveP" fill="none" stroke="#3b6ef6" stroke-width="2.2" />

        <!-- 余项（误差最大处） -->
        <line :x1="mapX(cur.argX)" :y1="mapY(fv)" :x2="mapX(cur.argX)" :y2="mapY(pv)" stroke="#e05252" stroke-width="2.5" />
        <circle :cx="mapX(cur.argX)" :cy="mapY(pv)" r="4.5" fill="#3b6ef6" />
        <circle :cx="mapX(cur.argX)" :cy="mapY(fv)" r="4.5" fill="#1f2733" />
        <!-- 展开点 -->
        <circle :cx="mapX(x0)" :cy="mapY(fvx0)" r="5.5" fill="#22a06b" />
        <text :x="mapX(x0) + 8" :y="mapY(fvx0) - 8" font-size="11" fill="#1a7a52">x₀</text>
        <text :x="mapX(cur.argX) + 6" :y="(mapY(fv) + mapY(pv)) / 2" font-size="11" fill="#e05252">Rₙ = {{ fmtE(errGap) }}</text>
        <text :x="12" :y="18" font-size="12" fill="#8b95a3">P{{ cur.n }}(x) 在 x₀ = {{ x0 }} 处 {{ cur.n }} 阶展开</text>
      </svg>

      <div class="ty-panel">
        <div class="def-box">
          <div class="small muted">泰勒公式（带拉格朗日余项）</div>
          <code>f(x) = Σ f⁽ᵏ⁾(x₀)/k! ·(x-x₀)ᵏ + Rₙ，Rₙ = f⁽ⁿ⁺¹⁾(ξ)/(n+1)! ·(x-x₀)ⁿ⁺¹</code>
        </div>
        <el-divider />
        <div class="info-row"><span>当前阶数 n</span><b style="color:var(--brand)">{{ cur.n }}</b></div>
        <div class="info-row"><span>本步新增项</span><b class="term">{{ cur.termTxt }}</b></div>
        <div class="info-row"><span>定义域内最大误差 max|Rₙ|</span>
          <el-tag size="small" :type="cur.maxErr < 0.01 ? 'success' : 'warning'">{{ fmtE(cur.maxErr) }}</el-tag>
        </div>
        <div class="info-row"><span>拉格朗日余项上界</span><b style="color:#8b5cf6">{{ fmtE(cur.bound) }}</b></div>
        <div class="info-row"><span>定义域最大偏差 h = max|x-x₀|</span><b>{{ fmtE(hMax) }}</b></div>
        <el-divider />
        <div class="tbl">
          <div class="tbl-head"><span>n</span><span>最大误差</span><span>余项上界</span></div>
          <div v-for="(s, i) in player.steps.value" :key="i" class="tbl-row" :class="{ active: i === player.idx.value }" @click="player.seek(i)">
            <span>{{ s.n }}</span><span>{{ fmtE(s.maxErr) }}</span><span>{{ fmtE(s.bound) }}</span>
          </div>
        </div>
        <p class="small muted tip">考点：泰勒公式用多项式局部逼近函数；阶数越高逼近区间越宽。ln(1+x) 在 x₀=0 处的收敛半径为 1，超出后阶数再高也会发散。</p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#1f2733"></i> 原函数 f(x)</span>
      <span><i class="dot" style="background:#3b6ef6"></i> n 阶泰勒多项式 Pₙ(x)</span>
      <span><i class="dot" style="background:#e05252"></i> 余项 Rₙ（误差）</span>
      <span><i class="dot" style="background:#22a06b"></i> 展开点 x₀</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

// sin 的各阶导数呈 [sin, cos, -sin, -cos] 循环
const CYCLE = [Math.sin, Math.cos, x => -Math.sin(x), x => -Math.cos(x)]
function fact(n) { let r = 1; for (let i = 2; i <= n; i++) r *= i; return r }

const PRESETS = [
  { key: 'sin', label: 'f(x) = sin x', domain: [-6.5, 6.5], range: [-2, 2], x0r: [-3, 3], f: x => Math.sin(x), coef: (n, x0) => CYCLE[n % 4](x0) / fact(n), bound: () => 1 },
  { key: 'exp', label: 'f(x) = e^x', domain: [-2.5, 3.5], range: [-1.5, 22], x0r: [-1.5, 1.5], f: x => Math.exp(x), coef: (n, x0) => Math.exp(x0) / fact(n), bound: () => Math.exp(3.5) },
  { key: 'ln', label: 'f(x) = ln(1+x)', domain: [-0.85, 3.2], range: [-2.6, 2.6], x0r: [0, 1.5], f: x => Math.log(1 + x), coef: (n, x0) => (n === 0 ? Math.log(1 + x0) : Math.pow(-1, n - 1) / (n * Math.pow(1 + x0, n))), bound: n => fact(n) / Math.pow(0.15, n + 1) }
]

const presetKey = ref('sin')
const x0 = ref(0)
const maxN = ref(6)
const preset = computed(() => PRESETS.find(p => p.key === presetKey.value) || PRESETS[0])
const x0Min = computed(() => preset.value.x0r[0])
const x0Max = computed(() => preset.value.x0r[1])
function onPreset() { x0.value = Math.min(Math.max(x0.value, x0Min.value), x0Max.value); player.reset() }

const W = 560, H = 340, padL = 46, padR = 16, padT = 18, padB = 34
const dm0 = computed(() => preset.value.domain[0])
const dm1 = computed(() => preset.value.domain[1])
const rg0 = computed(() => preset.value.range[0])
const rg1 = computed(() => preset.value.range[1])
function mapX(x) { return padL + ((x - dm0.value) / (dm1.value - dm0.value)) * (W - padL - padR) }
function mapY(y) { return padT + ((rg1.value - y) / (rg1.value - rg0.value)) * (H - padT - padB) }

const xGrid = computed(() => ticks(dm0.value, dm1.value))
const yGrid = computed(() => ticks(rg0.value, rg1.value))
function ticks(lo, hi) {
  const out = []
  for (let i = 0; i <= 8; i++) { const v = Number((lo + ((hi - lo) * i) / 8).toFixed(2)); if (out.indexOf(v) === -1) out.push(v) }
  return out
}

// 多项式求值：P(x) = Σ cₖ (x-x₀)ᵏ
function poly(coefs, x, X0) {
  let s = 0, p = 1
  for (let k = 0; k < coefs.length; k++) { s += coefs[k] * p; p *= x - X0 }
  return s
}
// 生成某一项的文字说明，如 "-0.1667(x-x₀)³"
function termText(c, n) {
  if (n === 0) return `f(x₀) = ${Number(c.toFixed(4))}`
  const mag = Number(Math.abs(c).toFixed(4))
  if (mag < 1e-8) return `第 ${n} 次项系数为 0（sin 的偶次项全为 0）`
  return `${c >= 0 ? '+' : '-'} ${mag}(x-x₀)${['', '', '²', '³', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹', '¹⁰'][n]}`
}

// 判定「逼近有效」的误差容限
const TOL = 0.01

const steps = computed(() => {
  const out = []
  const X0 = x0.value
  const P = preset.value
  const coefs = []
  // 展开点到定义域边界的距离：逼近区间不能越出定义域，
  // 也不能越过 ln(1+x) 这类函数的收敛半径。
  const reach = Math.min(Math.abs(P.domain[0] - X0), Math.abs(P.domain[1] - X0))
  // 局部评估半径。泰勒多项式本质是「局部逼近」，
  // 之前在整个绘图域（sin 是 [-6.5, 6.5]）上比误差，得到「阶数越高误差越大」
  // （n=0 误差 1.0 → n=6 误差 57.2），与「阶数越高越精确」的结论完全相反。
  const R = Math.min(1, reach)

  function errOn(cs, lo, hi, samples = 240) {
    let maxErr = 0, argX = X0
    for (let i = 0; i <= samples; i++) {
      const x = lo + ((hi - lo) * i) / samples
      const fv = P.f(x), pv = poly(cs, x, X0)
      if (!isFinite(fv) || !isFinite(pv)) continue
      const e = Math.abs(fv - pv)
      if (e > maxErr) { maxErr = e; argX = x }
    }
    return { maxErr, argX }
  }

  for (let n = 0; n <= maxN.value; n++) {
    coefs.push(P.coef(n, X0))
    const { maxErr, argX } = errOn(coefs, Math.max(P.domain[0], X0 - R), Math.min(P.domain[1], X0 + R))
    // 有效逼近半径：误差仍 < TOL 的最大半径。它随阶数单调扩大，
    // 这才是「高阶展开逼近范围更广」该有的样子。
    let lo2 = 0, hi2 = reach
    for (let k = 0; k < 40; k++) {
      const mid = (lo2 + hi2) / 2
      const e = errOn(coefs, Math.max(P.domain[0], X0 - mid), Math.min(P.domain[1], X0 + mid), 120).maxErr
      if (e < TOL) lo2 = mid; else hi2 = mid
    }
    // 拉格朗日余项上界：|Rₙ| ≤ M/(n+1)! · h^(n+1)，h 取局部半径
    const bound = (P.bound(n, X0) / fact(n + 1)) * Math.pow(R, n + 1)
    const termTxt = termText(coefs[n], n)
    const prev = out.length ? out[out.length - 1].maxErr : null
    const trend = prev === null ? '' : (maxErr < prev
      ? `（比上阶的 ${fmtE(prev)} 更小 ✓）`
      : (maxErr > prev + 1e-12 ? `（比上阶的 ${fmtE(prev)} 偏大，本项暂未带来改善）` : '（与上阶持平）'))
    out.push({
      n, coefs: [...coefs], maxErr, argX, bound, termTxt, radius: lo2, localR: R,
      desc: `加到第 ${n} 项 ${termTxt}：|x-x₀| ≤ ${Number(R.toFixed(2))} 内最大误差 = ${fmtE(maxErr)}${trend}，`
        + `有效逼近半径（误差 < ${TOL}）= ${lo2.toFixed(2)}`
    })
  }
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)

const hMax = computed(() => Math.max(Math.abs(dm0.value - x0.value), Math.abs(dm1.value - x0.value)))
const fvx0 = computed(() => preset.value.f(x0.value))
const fv = computed(() => preset.value.f(cur.value.argX))
const pv = computed(() => poly(cur.value.coefs, cur.value.argX, x0.value))
const errGap = computed(() => Math.abs(fv.value - pv.value))

function curve(coefs) {
  const P = preset.value, X0 = x0.value
  let d = ''
  for (let i = 0; i <= 320; i++) {
    const x = P.domain[0] + ((P.domain[1] - P.domain[0]) * i) / 320
    const y = coefs ? poly(coefs, x, X0) : P.f(x)
    if (isFinite(y)) d += (d === '' ? 'M' : 'L') + mapX(x).toFixed(2) + ' ' + Math.max(-60, Math.min(H + 60, mapY(y))).toFixed(2) + ' '
  }
  return d
}
const curveF = computed(() => curve(null))
const curveP = computed(() => curve(cur.value.coefs))

function fmtE(v) {
  if (!isFinite(v)) return '-'
  if (v === 0) return '0'
  if (v < 1e-4 || v >= 1e5) return v.toExponential(2)
  return Number(v.toFixed(5)).toString()
}
</script>

<style scoped>
.ty-wrap { display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap; }
.ty-svg { background: #fcfdff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.ty-panel { flex: 1; min-width: 300px; }
.def-box code { background: #f2f4f8; padding: 8px 10px; border-radius: 6px; display: block; font-size: 12px; line-height: 1.7; }
.info-row { display: flex; justify-content: space-between; align-items: center; gap: 10px; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.info-row .term { color: var(--brand); font-size: 12px; }
.tbl { font-size: 12px; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; margin-top: 6px; }
.tbl-head { display: grid; grid-template-columns: 0.6fr 1fr 1fr; background: #f6f8fb; padding: 7px 10px; font-weight: 600; }
.tbl-row { display: grid; grid-template-columns: 0.6fr 1fr 1fr; padding: 6px 10px; border-top: 1px solid #f0f2f6; cursor: pointer; }
.tbl-row:hover { background: #f6f8fb; }
.tbl-row.active { background: var(--brand-light); color: var(--brand); font-weight: 600; }
.tip { margin-top: 10px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
