<template>
  <VisFrame title="常微分方程 · 斜率场与欧拉法" desc="斜率场给出每点的 dy/dx，数值解沿箭头前进：欧拉法每步用起点斜率直线外推，改进欧拉再取终点斜率做梯形校正" :player="player" :status-text="statusText" back-to="/knowledge/56">
    <template #extra>
      <el-select v-model="presetKey" size="small" style="width:170px" @change="onPreset">
        <el-option v-for="p in PRESETS" :key="p.key" :value="p.key" :label="p.label" />
      </el-select>
      <span class="small muted">初值 y₀</span>
      <el-input-number v-model="y0" :min="-3" :max="5" :step="0.1" size="small" controls-position="right" style="width:100px" @change="player.reset()" />
      <span class="small muted">步数</span>
      <el-select v-model="nSteps" size="small" style="width:88px" @change="player.reset()">
        <el-option :value="6" label="6 步" />
        <el-option :value="12" label="12 步" />
        <el-option :value="24" label="24 步" />
        <el-option :value="48" label="48 步" />
      </el-select>
    </template>

    <div class="od-wrap">
      <svg :width="W" :height="H" class="od-svg">
        <defs><clipPath id="odClip"><rect x="0" y="0" :width="W" :height="H" /></clipPath></defs>
        <g clip-path="url(#odClip)">
          <line v-for="g in yGrid" :key="'g' + g" :x1="mapX(dm0)" :y1="mapY(g)" :x2="mapX(dm1)" :y2="mapY(g)" stroke="#f0f2f7" />
          <!-- 方向场：每个网格点画一小段指向 dy/dx 的箭头 -->
          <g v-for="(a, i) in arrows" :key="'a' + i">
            <line :x1="a.x1" :y1="a.y1" :x2="a.x2" :y2="a.y2" stroke="#c8d3e6" stroke-width="1.4" />
            <polygon :points="a.tip" fill="#c8d3e6" />
          </g>
          <line :x1="mapX(dm0)" :y1="mapY(0)" :x2="mapX(dm1)" :y2="mapY(0)" stroke="#8b95a3" stroke-width="1.5" />
          <line :x1="mapX(0)" :y1="mapY(rg0)" :x2="mapX(0)" :y2="mapY(rg1)" stroke="#8b95a3" stroke-width="1.5" />

          <!-- 欧拉法 / 改进欧拉法的数值解逐步延伸，再与精确解对比 -->
          <path :d="exactPath" fill="none" stroke="#22a06b" stroke-width="2" stroke-dasharray="6 4" />
          <path :d="eulerPath" fill="none" stroke="#e05252" stroke-width="2.2" />
          <path :d="heunPath" fill="none" stroke="#3b6ef6" stroke-width="2.2" />
          <circle :cx="mapX(dm0)" :cy="mapY(y0)" r="5" fill="#8b5cf6" />
          <text :x="mapX(dm0) + 8" :y="mapY(y0) - 8" font-size="11" fill="#8b5cf6">初值 (x₀, y₀)</text>
          <circle :cx="mapX(cur.x)" :cy="mapY(cur.ye)" r="5" fill="#e05252" />
          <circle :cx="mapX(cur.x)" :cy="mapY(cur.yh)" r="5" fill="#3b6ef6" />
          <text :x="12" :y="18" font-size="12" fill="#8b95a3">第 {{ cur.k }} / {{ nSteps }} 步，步长 h = {{ fmt(hEff) }}</text>
        </g>
      </svg>

      <div class="od-panel">
        <div class="def-box">
          <div class="small muted">数值积分格式（同济《高数》常微分方程数值解）</div>
          <code>欧拉：yₙ₊₁ = yₙ + h·f(xₙ, yₙ)
改进欧拉：ŷ = yₙ + h·f(xₙ,yₙ)；yₙ₊₁ = yₙ + h/2·[f(xₙ,yₙ) + f(xₙ₊₁,ŷ)]</code>
        </div>
        <el-divider />
        <div class="info-row"><span>积分步长 h</span><b style="color:var(--brand)">{{ fmt(hEff) }}</b></div>
        <div class="info-row"><span>当前点 xₖ</span><b>{{ fmt(cur.x) }}</b></div>
        <div class="info-row"><span>欧拉法 yₖ</span><b style="color:var(--danger)">{{ fmt(cur.ye) }}</b></div>
        <div class="info-row"><span>改进欧拉 yₖ</span><b style="color:var(--brand)">{{ fmt(cur.yh) }}</b></div>
        <div class="info-row"><span>精确解 y(xₖ)</span><b style="color:var(--success)">{{ fmt(cur.yx) }}</b></div>
        <div class="info-row"><span>欧拉法绝对误差</span>
          <el-tag size="small" :type="cur.ee < 0.02 ? 'success' : 'danger'">{{ fmt(cur.ee) }}</el-tag>
        </div>
        <div class="info-row"><span>改进欧拉绝对误差</span>
          <el-tag size="small" :type="cur.eh < 0.02 ? 'success' : 'warning'">{{ fmt(cur.eh) }}</el-tag>
        </div>
        <div class="info-row"><span>全程末端误差（欧拉 / 改进欧拉）</span><b>{{ fmt(endErr.e) }} / {{ fmt(endErr.h) }}</b></div>
        <p class="small muted tip">考点：欧拉法局部截断误差 O(h²)、整体 O(h)；改进欧拉用梯形校正使误差降到 O(h²) 量级。步长减半，欧拉误差约减半。</p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#c8d3e6"></i> 方向场（每点切线方向）</span>
      <span><i class="dot" style="background:#e05252"></i> 欧拉法</span>
      <span><i class="dot" style="background:#3b6ef6"></i> 改进欧拉法</span>
      <span><i class="dot" style="background:#22a06b"></i> 精确解曲线</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const PRESETS = [
  { key: 'exp', label: "y' = y（指数增长）", domain: [-1.5, 1.5], range: [-1, 6], y0: 0.5, f: (x, y) => y, exact: (x, x0, y0) => y0 * Math.exp(x - x0) },
  { key: 'sinx', label: "y' = sin x", domain: [-1, 7], range: [-2.5, 3.5], y0: 0, f: (x, y) => Math.sin(x), exact: (x, x0, y0) => y0 + Math.cos(x0) - Math.cos(x) },
  { key: 'xpy', label: "y' = x + y", domain: [-1.5, 1.5], range: [-2, 6], y0: 0.8, f: (x, y) => x + y, exact: (x, x0, y0) => (y0 + x0 + 1) * Math.exp(x - x0) - x - 1 },
  { key: 'logi', label: "y' = y(1-y)（logistic）", domain: [-1, 5], range: [-0.6, 2.2], y0: 0.1, f: (x, y) => y * (1 - y), exact: (x, x0, y0) => 1 / (1 + (1 / y0 - 1) * Math.exp(-(x - x0))) }
]

const presetKey = ref('exp')
const y0 = ref(0.5)
const nSteps = ref(12)
const preset = computed(() => PRESETS.find(p => p.key === presetKey.value) || PRESETS[0])
function onPreset() { y0.value = preset.value.y0; player.reset() }

const W = 560, H = 340, padL = 42, padR = 16, padT = 18, padB = 32
const dm0 = computed(() => preset.value.domain[0])
const dm1 = computed(() => preset.value.domain[1])
const rg0 = computed(() => preset.value.range[0])
const rg1 = computed(() => preset.value.range[1])
function mapX(x) { return padL + ((x - dm0.value) / (dm1.value - dm0.value)) * (W - padL - padR) }
function mapY(y) { return padT + ((rg1.value - y) / (rg1.value - rg0.value)) * (H - padT - padB) }
const yGrid = computed(() => {
  const out = []
  for (let i = 0; i <= 8; i++) out.push(Number((rg0.value + ((rg1.value - rg0.value) * i) / 8).toFixed(2)))
  return out
})
const hEff = computed(() => (dm1.value - dm0.value) / nSteps.value)

// 方向场箭头：把 (1, f(x,y)) 换算到像素方向后归一化成定长小箭头
const arrows = computed(() => {
  const kx = (W - padL - padR) / (dm1.value - dm0.value)
  const ky = (H - padT - padB) / (rg1.value - rg0.value)
  const out = []
  for (let i = 0; i < 14; i++) {
    for (let j = 0; j < 10; j++) {
      const x = dm0.value + ((dm1.value - dm0.value) * (i + 0.5)) / 14
      const y = rg0.value + ((rg1.value - rg0.value) * (j + 0.5)) / 10
      const s = preset.value.f(x, y)
      if (!isFinite(s)) continue
      const n = Math.hypot(kx, -s * ky) || 1
      const dx = (kx / n) * 13, dy = (-s * ky / n) * 13 // 定长 13px 的小箭头
      const cx = mapX(x), cy = mapY(y)
      const x1 = cx - dx / 2, y1 = cy - dy / 2, x2 = cx + dx / 2, y2 = cy + dy / 2
      const wx = (-dy / n) * 3, wy = (dx / n) * 3 // 箭头尖端的三角形
      out.push({ x1, y1, x2, y2, tip: `${x2},${y2} ${x2 - (dx / n) * 4 + wx},${y2 - (dy / n) * 4 + wy} ${x2 - (dx / n) * 4 - wx},${y2 - (dy / n) * 4 - wy}` })
    }
  }
  return out
})

// 数值解：欧拉法与改进欧拉（预估-校正）并行积分
const sol = computed(() => {
  const P = preset.value, h = hEff.value, N = nSteps.value
  let ye = y0.value, yh = y0.value
  const xs = [dm0.value], ey = [ye], hy = [yh], ex = [P.exact(dm0.value, dm0.value, y0.value)]
  for (let k = 1; k <= N; k++) {
    const px = xs[k - 1]
    ye = ye + h * P.f(px, ye)
    const pre = yh + h * P.f(px, yh)
    yh = yh + (h / 2) * (P.f(px, yh) + P.f(px + h, pre))
    const x = dm0.value + k * h
    xs.push(x); ey.push(ye); hy.push(yh); ex.push(P.exact(x, dm0.value, y0.value))
  }
  return { xs, ey, hy, ex }
})

const steps = computed(() => {
  const s = sol.value, out = []
  for (let k = 0; k <= nSteps.value; k++) {
    const yx = s.ex[k], ee = Math.abs(s.ey[k] - yx), eh = Math.abs(s.hy[k] - yx)
    out.push({
      k, x: s.xs[k], ye: s.ey[k], yh: s.hy[k], yx, ee, eh,
      desc: k === 0
        ? `初始点 (x₀=${fmt(s.xs[0])}, y₀=${fmt(y0.value)})，斜率 f(x₀,y₀)=${fmt(preset.value.f(s.xs[0], y0.value))}，开始沿方向场积分`
        : `第 ${k} 步 x=${fmt(s.xs[k])}：欧拉 ${fmt(s.ey[k])}（误差 ${fmt(ee)}），改进欧拉 ${fmt(s.hy[k])}（误差 ${fmt(eh)}），精确解 ${fmt(yx)}`
    })
  }
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const endErr = computed(() => {
  const s = sol.value, n = s.xs.length - 1
  return { e: Math.abs(s.ey[n] - s.ex[n]), h: Math.abs(s.hy[n] - s.ex[n]) }
})

function pathFrom(xs, ys) {
  let d = ''
  for (let i = 0; i < xs.length; i++) {
    if (isFinite(ys[i])) d += (i === 0 ? 'M' : 'L') + mapX(xs[i]).toFixed(2) + ' ' + mapY(ys[i]).toFixed(2) + ' '
  }
  return d
}
const eulerPath = computed(() => pathFrom(sol.value.xs.slice(0, player.idx.value + 1), sol.value.ey.slice(0, player.idx.value + 1)))
const heunPath = computed(() => pathFrom(sol.value.xs.slice(0, player.idx.value + 1), sol.value.hy.slice(0, player.idx.value + 1)))
const exactPath = computed(() => {
  // 精确解用细密采样画成光滑曲线
  const P = preset.value, xs = [], ys = []
  for (let i = 0; i <= 240; i++) {
    const x = dm0.value + ((dm1.value - dm0.value) * i) / 240
    xs.push(x); ys.push(P.exact(x, dm0.value, y0.value))
  }
  return pathFrom(xs, ys)
})

function fmt(v) { return (v === null || v === undefined || !isFinite(v)) ? '-' : Number(v.toFixed(4)).toString() }
</script>

<style scoped>
.od-wrap { display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap; }
.od-svg { background: #fcfdff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.od-panel { flex: 1; min-width: 300px; }
.def-box code { background: #f2f4f8; padding: 8px 10px; border-radius: 6px; display: block; font-size: 12px; line-height: 1.7; white-space: pre-wrap; }
.info-row { display: flex; justify-content: space-between; align-items: center; gap: 10px; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.tip { margin-top: 10px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
