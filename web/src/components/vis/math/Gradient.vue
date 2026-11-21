<template>
  <VisFrame title="偏导数与梯度 · 等高线上的方向导数" desc="∂z/∂x、∂z/∂y 是沿坐标轴的方向导数；梯度 ∇z = (∂z/∂x, ∂z/∂y) 指向函数值增长最快的方向，反方向即最速下降方向" :player="player" :status-text="statusText" back-to="/knowledge/57">
    <template #extra>
      <el-select v-model="presetKey" size="small" style="width:180px" @change="player.reset()">
        <el-option v-for="p in PRESETS" :key="p.key" :value="p.key" :label="p.label" />
      </el-select>
      <span class="small muted">步长 η</span>
      <el-slider v-model="eta" :min="0.02" :max="0.45" :step="0.01" style="width:100px" :show-tooltip="false" @change="player.reset()" />
      <span class="small muted">方向角 α</span>
      <el-slider v-model="alpha" :min="0" :max="345" :step="15" style="width:100px" :show-tooltip="false" />
    </template>

    <div class="gr-wrap">
      <svg :width="W" :height="H" class="gr-svg">
        <rect v-for="(c, i) in field.heat" :key="'h' + i" :x="c.x" :y="c.y" :width="c.w" :height="c.h" :fill="c.fill" />
        <path v-for="(d, i) in contours" :key="'c' + i" :d="d" fill="none" stroke="#5b6472" stroke-opacity="0.45" stroke-width="1" />
        <polyline :points="trail" fill="none" stroke="#8b5cf6" stroke-width="2" stroke-opacity="0.7" />
        <!-- 偏导方向（沿 +x / +y 单位方向）与任意方向的方向导数 -->
        <line :x1="cx" :y1="cy" :x2="cx + 1 * ARROW" :y2="cy" stroke="#3b6ef6" stroke-width="2.5" />
        <polygon :points="arrowTip(1, 0)" fill="#3b6ef6" />
        <text :x="cx + ARROW + 4" :y="cy - 6" font-size="11" fill="#2a55c4">∂z/∂x = {{ fmt(cur.gx) }}</text>
        <line :x1="cx" :y1="cy" :x2="cx" :y2="cy - 1 * ARROW" stroke="#22a06b" stroke-width="2.5" />
        <polygon :points="arrowTip(0, -1)" fill="#22a06b" />
        <text :x="cx + 4" :y="cy - ARROW - 6" font-size="11" fill="#14764e">∂z/∂y = {{ fmt(cur.gy) }}</text>
        <line :x1="cx" :y1="cy" :x2="cx + ux * ARROW * dirSign" :y2="cy - uy * ARROW * dirSign" stroke="#e8a13a" stroke-width="2" stroke-dasharray="5 3" />
        <circle :cx="cx + ux * ARROW * 0.85 * dirSign" :cy="cy - uy * ARROW * 0.85 * dirSign" r="4" fill="#e8a13a" />
        <!-- 梯度方向（上升）与最速下降方向 -->
        <line :x1="cx" :y1="cy" :x2="cx + gux * ARROW * 1.25" :y2="cy - guy * ARROW * 1.25" stroke="#8b5cf6" stroke-width="3" />
        <text :x="cx + gux * ARROW * 1.25" :y="cy - guy * ARROW * 1.25" font-size="11" font-weight="700" fill="#7c3aed">∇z</text>
        <line :x1="cx" :y1="cy" :x2="cx - gux * ARROW * 1.25" :y2="cy + guy * ARROW * 1.25" stroke="#e05252" stroke-width="3" stroke-dasharray="6 4" />
        <text :x="cx - gux * ARROW * 1.25" :y="cy + guy * ARROW * 1.25" font-size="11" font-weight="700" fill="#c02b2b">-∇z</text>
        <circle :cx="cx" :cy="cy" r="6.5" fill="#fff" stroke="#1f2733" stroke-width="2" />
        <text :x="12" :y="18" font-size="12" fill="#1f2733">第 {{ cur.k }} 次下降：z = {{ fmt(cur.z) }}，|∇z| = {{ fmt(cur.gn) }}</text>
      </svg>

      <div class="gr-panel">
        <div class="def-box"><div class="small muted">教材公式（同济《高数》多元函数微分学）</div><code>方向导数  ∂z/∂l = ∂z/∂x·cosα + ∂z/∂y·cosβ = ∇z · e
梯度    ∇z = (∂z/∂x, ∂z/∂y)，|∇z| 为最大方向导数，取得最大值的方向就是梯度方向</code></div>
        <div class="info-row"><span>当前点 / 函数值 z</span><b>({{ fmt(cur.x) }}, {{ fmt(cur.y) }}) → {{ fmt(cur.z) }}</b></div>
        <div class="info-row"><span>梯度模 |∇z|</span><b style="color:#7c3aed">{{ fmt(cur.gn) }}</b></div>
        <div class="info-row"><span>方向导数 ∂z/∂l（α = {{ alpha }}°）</span><b style="color:#a5701a">{{ fmt(dirDeriv) }}</b></div>
        <div class="info-row"><span>｜方向导数｜ / ｜梯度｜</span><el-tag size="small" type="info">{{ fmt(cur.gn > 1e-9 ? Math.abs(dirDeriv) / cur.gn : 0) }}</el-tag></div>
        <div class="info-row"><span>最速下降方向 -∇z</span><b style="color:var(--danger)">(-{{ fmt(cur.gx) }}, -{{ fmt(cur.gy) }})</b></div>
        <p class="small muted tip">考点：方向导数是梯度在方向 e 上的投影，故 ≤ |∇z|，当方向与 ∇z 同向时取最大 —— 这就是「梯度方向上升最快、-∇z 下降最快」。等高线越密处 |∇z| 越大。</p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#8b5cf6"></i> 梯度方向 ∇z（最速上升）</span>
      <span><i class="dot" style="background:#e05252"></i> -∇z（最速下降，梯度下降迭代路径）</span>
      <span><i class="dot" style="background:#3b6ef6"></i> ∂z/∂x 方向</span>
      <span><i class="dot" style="background:#22a06b"></i> ∂z/∂y 方向</span>
      <span><i class="dot" style="background:#e8a13a"></i> 任意方向 l 的方向导数</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

// 每个预设都给出解析梯度 (gx, gy)，便于画方向导数与下降到山顶/鞍点的演示
const PRESETS = [
  { key: 'bowl', label: 'z = x² + y²（抛物面）', dom: [-3, 3], start: [2.6, 2.4], f: (x, y) => x * x + y * y, gx: (x, y) => 2 * x, gy: (x, y) => 2 * y },
  { key: 'saddle', label: 'z = x² - y²（鞍点）', dom: [-3, 3], start: [2.4, 1.2], f: (x, y) => x * x - y * y, gx: (x, y) => 2 * x, gy: (x, y) => -2 * y },
  { key: 'ani', label: 'z = x² + 6y²（狭长山谷）', dom: [-3, 3], start: [2.6, 1.6], f: (x, y) => x * x + 6 * y * y, gx: (x, y) => 2 * x, gy: (x, y) => 12 * y },
  { key: 'wave', label: 'z = sin x · cos y（起伏）', dom: [-3, 3], start: [2.2, 1.5], f: (x, y) => Math.sin(x) * Math.cos(y), gx: (x, y) => Math.cos(x) * Math.cos(y), gy: (x, y) => -Math.sin(x) * Math.sin(y) }
]

const presetKey = ref('bowl')
const eta = ref(0.12)
const alpha = ref(45)
const preset = computed(() => PRESETS.find(p => p.key === presetKey.value) || PRESETS[0])

const W = 520, H = 430, pad = 26
const planW = W - pad * 2
function mapX(x) { const d = preset.value.dom[1] - preset.value.dom[0]; return pad + ((x - preset.value.dom[0]) / d) * planW }
function mapY(y) { const d = preset.value.dom[1] - preset.value.dom[0]; return H - pad - ((y - preset.value.dom[0]) / d) * planW }

// 采样网格（NG）用于等高线追踪，稀疏网格（NH）用于配色（3D 感），field 二者共享
const NG = 48, NH = 24
const field = computed(() => {
  const P = preset.value, [lo, hi] = P.dom
  const vals = []
  let vmin = Infinity, vmax = -Infinity
  for (let i = 0; i <= NG; i++) {
    const row = [], x = lo + ((hi - lo) * i) / NG
    for (let j = 0; j <= NG; j++) {
      const v = P.f(x, lo + ((hi - lo) * j) / NG)
      row.push(v)
      vmin = Math.min(vmin, v)
      vmax = Math.max(vmax, v)
    }
    vals.push(row)
  }
  // 低处蓝、高处橙，并按光源方向（-x-y）做坡面明暗，制造立体感
  const heat = [], step = NG / NH
  for (let i = 0; i < NH; i++) {
    for (let j = 0; j < NH; j++) {
      const gi = Math.round(i * step), gj = Math.round(j * step)
      const gx = lo + ((hi - lo) * gi) / NG, gy = lo + ((hi - lo) * gj) / NG
      const t = Math.pow((vals[gi][gj] - vmin) / (vmax - vmin || 1), 0.55)
      const sh = Math.max(-1, Math.min(1, -(P.gx(gx, gy) + P.gy(gx, gy)) / 40))
      heat.push({ x: mapX(lo + ((hi - lo) * i * step) / NG), y: mapY(lo + ((hi - lo) * (j + 1) * step) / NG), w: planW / NH + 1, h: planW / NH + 1, fill: `hsl(${(215 - 195 * t).toFixed(0)}, ${(38 + 42 * t).toFixed(0)}%, ${(92 - 40 * t + 9 * sh).toFixed(0)}%)` })
    }
  }
  return { vals, vmin, vmax, heat }
})
// Marching Squares：在每个格子四条边上线性插值求交点，连成等高线段
const contours = computed(() => {
  const { vals, vmin, vmax } = field.value
  const [lo, hi] = preset.value.dom
  const wx = u => lo + ((hi - lo) * u) / NG
  const out = []
  for (let k = 1; k <= 11; k++) {
    const level = vmin + (vmax - vmin) * Math.pow(k / 12, 1.5)
    let d = ''
    for (let i = 0; i < NG; i++) {
      for (let j = 0; j < NG; j++) {
        const vv = [vals[i][j], vals[i + 1][j], vals[i + 1][j + 1], vals[i][j + 1]]
        const ab = vv.map(v => v > level)
        if (ab[0] === ab[1] && ab[1] === ab[2] && ab[2] === ab[3]) continue
        const ci = [i, i + 1, i + 1, i], cj = [j, j, j + 1, j + 1]
        const hits = []
        for (let e = 0; e < 4; e++) {
          const q = (e + 1) % 4
          if (ab[e] === ab[q]) continue
          const tt = (level - vv[e]) / (vv[q] - vv[e] || 1e-9)
          hits.push([ci[e] + (ci[q] - ci[e]) * tt, cj[e] + (cj[q] - cj[e]) * tt])
        }
        const pairs = hits.length === 4 ? [[0, 1], [2, 3]] : [[0, 1]]
        for (const [a, b] of pairs) {
          if (!hits[a] || !hits[b]) continue
          d += `M${mapX(wx(hits[a][0])).toFixed(1)} ${mapY(wx(hits[a][1])).toFixed(1)}` +
               `L${mapX(wx(hits[b][0])).toFixed(1)} ${mapY(wx(hits[b][1])).toFixed(1)}`
        }
      }
    }
    if (d) out.push(d)
  }
  return out
})

const N_ITER = 22 // 梯度下降迭代次数
const steps = computed(() => {
  const P = preset.value, h = eta.value
  let [x, y] = P.start
  const out = []
  const push = (k, note) => out.push({ k, x, y, z: P.f(x, y), gx: P.gx(x, y), gy: P.gy(x, y), gn: Math.hypot(P.gx(x, y), P.gy(x, y)), desc: note })
  push(0, `起点 (${P.start[0]}, ${P.start[1]})：z = ${P.f(P.start[0], P.start[1]).toFixed(3)}，梯度 (${P.gx(x, y).toFixed(3)}, ${P.gy(x, y).toFixed(3)})`)
  for (let k = 1; k <= N_ITER; k++) {
    const gx = P.gx(x, y), gy = P.gy(x, y)
    x -= h * gx
    y -= h * gy
    if (!isFinite(x) || !isFinite(y)) { x = 0; y = 0 }
    const grew = Math.hypot(P.gx(x, y), P.gy(x, y)) > Math.hypot(gx, gy) + 1e-6
    push(k, `第 ${k} 步沿最速下降方向 -∇z 前进 η=${h}：新点 (${x.toFixed(3)}, ${y.toFixed(3)})，z = ${P.f(x, y).toFixed(4)}${grew ? '（梯度反而变大 —— 鞍点/峡谷会引起振荡发散）' : '，梯度变小，正在逼近驻点'}`)
  }
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)

const ARROW = 42
const cx = computed(() => mapX(cur.value.x))
const cy = computed(() => mapY(cur.value.y))
const gLen = computed(() => cur.value.gn || 1)
const gux = computed(() => cur.value.gx / gLen.value)
const guy = computed(() => cur.value.gy / gLen.value)
const ux = computed(() => Math.cos((alpha.value * Math.PI) / 180))
const uy = computed(() => Math.sin((alpha.value * Math.PI) / 180))
const dirDeriv = computed(() => cur.value.gx * ux.value + cur.value.gy * uy.value)
const dirSign = computed(() => (dirDeriv.value >= 0 ? 1 : -1))
const trail = computed(() => player.steps.value.slice(0, player.idx.value + 1).map(s => mapX(s.x).toFixed(1) + ',' + mapY(s.y).toFixed(1)).join(' '))

// 画一个固定长度的箭头尖端三角形
function arrowTip(dx, dy) {
  const ex = cx.value + dx * ARROW, ey = cy.value + dy * ARROW, px = -dy * 4.5, py = dx * 4.5
  return `${ex},${ey} ${ex - dx * 8 + px},${ey - dy * 8 + py} ${ex - dx * 8 - px},${ey - dy * 8 - py}`
}
function fmt(v) { return (v === null || v === undefined || !isFinite(v)) ? '-' : Number(v.toFixed(3)).toString() }
</script>

<style scoped>
.gr-wrap { display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap; }
.gr-svg { background: #fcfdff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.gr-panel { flex: 1; min-width: 300px; }
.def-box code { background: #f2f4f8; padding: 8px 10px; border-radius: 6px; display: block; font-size: 12px; line-height: 1.7; white-space: pre-wrap; }
.info-row { display: flex; justify-content: space-between; align-items: center; gap: 10px; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.tip { margin-top: 10px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
