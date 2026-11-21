<template>
  <VisFrame
    title="多元函数微分学与重积分"
    desc="为什么看这个动画：把偏导、梯度、切平面和二重积分放在同一幅图里，直观看见“局部线性化”与“小体积累加”。"
    :player="player"
    :status-text="statusText"
    back-to="/knowledge/86"
  >
    <template #extra>
      <el-select v-model="surfaceKey" size="small" style="width: 150px" @change="resetView">
        <el-option v-for="item in SURFACES" :key="item.key" :label="item.label" :value="item.key" />
      </el-select>
      <span class="small muted">旋转 {{ rotation }}°</span>
      <el-slider v-model="rotation" :min="-180" :max="180" :step="5" style="width: 105px" :show-tooltip="false" />
      <span class="small muted">俯视 {{ tilt }}°</span>
      <el-slider v-model="tilt" :min="15" :max="75" :step="5" style="width: 95px" :show-tooltip="false" />
    </template>

    <div class="mv-wrap">
      <div ref="plotHost" class="plot-host">
        <svg viewBox="0 0 680 560" class="mv-svg" role="img" aria-label="多元函数曲面、切平面和极坐标二重积分动画">
          <rect x="1" y="1" width="678" height="558" rx="10" fill="#fcfdff" stroke="#e4e8ef" />
          <text x="18" y="25" class="section-title">z = {{ surface.label }}：曲面、切平面与梯度</text>
          <text v-if="!compact" x="662" y="25" text-anchor="end" class="hint">拖动上方滑块改变观察角度</text>

          <!-- 网格线把二维参数网格映射到三维曲面，弯曲程度就是函数变化率。 -->
          <path v-for="(line, i) in surfaceMesh" :key="'mesh' + i" :d="line" fill="none" :stroke="i % 2 ? '#94b3f7' : '#7298ee'" stroke-width="1.1" opacity="0.72" />
          <polygon :points="planePoints" fill="#f7b955" fill-opacity="0.32" stroke="#dc8b20" stroke-width="1.6" />
          <line :x1="pointScreen.x" :y1="pointScreen.y" :x2="gradientEnd.x" :y2="gradientEnd.y" stroke="#e05252" stroke-width="3" marker-end="url(#mv-arrow)" />
          <circle :cx="pointScreen.x" :cy="pointScreen.y" r="5.5" fill="#22a06b" stroke="#fff" stroke-width="2" />
          <text :x="pointScreen.x + 8" :y="pointScreen.y - 8" font-size="11" fill="#176b49">P({{ x0.toFixed(1) }}, {{ y0.toFixed(1) }})</text>
          <text :x="gradientEnd.x + 7" :y="gradientEnd.y - 4" font-size="11" fill="#c53d3d">∇f</text>
          <defs>
            <marker id="mv-arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 Z" fill="#e05252" /></marker>
          </defs>

          <line x1="18" y1="326" x2="662" y2="326" stroke="#e4e8ef" />
          <text x="18" y="352" class="section-title">极坐标分割：∬ᴰ(1+x²+y²)dA，D: x²+y²≤1</text>
          <text x="18" y="374" class="hint">每个扇环柱体贡献 (1+r²)·rΔrΔθ；高亮表示已累加</text>
          <g>
            <path v-for="(cell, i) in polarCells" :key="'side' + i" :d="cell.side" :fill="cell.active ? '#c8d8fb' : '#f0f2f6'" stroke="#d5dbe6" stroke-width="0.6" />
            <path v-for="(cell, i) in polarCells" :key="'top' + i" :d="cell.top" :fill="cell.active ? cell.fill : '#f7f8fa'" :fill-opacity="cell.active ? 0.82 : 0.75" stroke="#fff" stroke-width="0.8" />
          </g>
          <text x="495" y="425" text-anchor="middle" font-size="13" fill="#526071">已累加 {{ cur.k }} / {{ polarCells.length }} 柱</text>
          <text x="495" y="450" text-anchor="middle" font-size="18" font-weight="700" fill="#3b6ef6">近似值 {{ fmt(cur.sum) }}</text>
          <text x="495" y="474" text-anchor="middle" font-size="12" fill="#22a06b">精确值 3π/2 = {{ fmt(exactIntegral) }}</text>
          <text x="495" y="496" text-anchor="middle" font-size="12" fill="#e05252">误差 {{ fmt(Math.abs(cur.sum - exactIntegral)) }}</text>
        </svg>
      </div>

      <div class="mv-panel">
        <div class="formula"><code>{{ surface.formula }}</code></div>
        <div class="param-row">
          <span>x₀ = {{ x0.toFixed(1) }}</span>
          <el-slider v-model="x0" :min="-1.5" :max="1.5" :step="0.1" :show-tooltip="false" @input="player.reset()" />
        </div>
        <div class="param-row">
          <span>y₀ = {{ y0.toFixed(1) }}</span>
          <el-slider v-model="y0" :min="-1.5" :max="1.5" :step="0.1" :show-tooltip="false" @input="player.reset()" />
        </div>
        <div class="param-row">
          <span>径向分割 {{ radialN }}</span>
          <el-slider v-model="radialN" :min="3" :max="8" :step="1" :show-tooltip="false" @change="player.reset()" />
        </div>
        <el-divider />
        <div class="info-row"><span>当前点 z₀</span><b>{{ fmt(z0) }}</b></div>
        <div class="info-row"><span>偏导 ∂f/∂x</span><b style="color: #3b6ef6">{{ fmt(fx) }}</b></div>
        <div class="info-row"><span>偏导 ∂f/∂y</span><b style="color: #8b5cf6">{{ fmt(fy) }}</b></div>
        <div class="info-row"><span>梯度 |∇f|</span><b style="color: #e05252">{{ fmt(gradNorm) }}</b></div>
        <div class="info-row"><span>切平面</span><b class="plane-text">z={{ fmt(z0) }}+{{ fmt(fx) }}(x-x₀)+{{ fmt(fy) }}(y-y₀)</b></div>
        <div class="info-row"><span>极坐标当前采样</span><b>r={{ fmt(cur.r) }}, θ={{ fmt(cur.theta) }}</b></div>
        <p class="small muted tip">梯度指向函数增长最快的方向，且垂直于等高线；二重积分则把每个小区域上的“高度 × 底面积”相加。</p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot surface"></i> 曲面网格</span>
      <span><i class="dot plane"></i> 切平面</span>
      <span><i class="dot gradient"></i> 梯度方向</span>
      <span><i class="dot integral"></i> 已累加小柱体</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const SURFACES = [
  { key: 'bowl', label: '椭圆抛物面', formula: 'f(x,y)=0.45x²+0.25y²', f: (x, y) => 0.45 * x * x + 0.25 * y * y, dx: x => 0.9 * x, dy: (_, y) => 0.5 * y },
  { key: 'saddle', label: '马鞍面', formula: 'f(x,y)=0.45(x²-y²)', f: (x, y) => 0.45 * (x * x - y * y), dx: x => 0.9 * x, dy: (_, y) => -0.9 * y },
  { key: 'wave', label: '正弦曲面', formula: 'f(x,y)=sin(x)cos(y)', f: (x, y) => Math.sin(x) * Math.cos(y), dx: (x, y) => Math.cos(x) * Math.cos(y), dy: (x, y) => -Math.sin(x) * Math.sin(y) }
]

const surfaceKey = ref('bowl')
const rotation = ref(-35)
const tilt = ref(42)
const x0 = ref(0.7)
const y0 = ref(-0.5)
const radialN = ref(5)
const plotHost = ref(null)
const viewportWidth = ref(680)
let resizeObserver = null

const compact = computed(() => viewportWidth.value < 520)
const surface = computed(() => SURFACES.find(item => item.key === surfaceKey.value) || SURFACES[0])
const z0 = computed(() => surface.value.f(x0.value, y0.value))
const fx = computed(() => surface.value.dx(x0.value, y0.value))
const fy = computed(() => surface.value.dy(x0.value, y0.value))
const gradNorm = computed(() => Math.hypot(fx.value, fy.value))
const exactIntegral = 1.5 * Math.PI

// 先绕 z 轴旋转，再按俯视角压缩 y 方向；z 越大，屏幕坐标越靠上。
function project(x, y, z) {
  const a = rotation.value * Math.PI / 180
  const t = tilt.value * Math.PI / 180
  const xr = x * Math.cos(a) - y * Math.sin(a)
  const yr = x * Math.sin(a) + y * Math.cos(a)
  return { x: 340 + xr * 72, y: 184 + yr * 42 * Math.sin(t) - z * 48 * Math.cos(t) }
}

function pathFrom(points, close = false) {
  const d = points.map((p, i) => `${i ? 'L' : 'M'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ')
  return close ? `${d} Z` : d
}

const surfaceMesh = computed(() => {
  const lines = []
  const grid = 9
  for (let axis = 0; axis < 2; axis++) {
    for (let i = 0; i < grid; i++) {
      const fixed = -2 + 4 * i / (grid - 1)
      const points = []
      for (let j = 0; j <= 30; j++) {
        const moving = -2 + 4 * j / 30
        const x = axis === 0 ? moving : fixed
        const y = axis === 0 ? fixed : moving
        points.push(project(x, y, surface.value.f(x, y)))
      }
      lines.push(pathFrom(points))
    }
  }
  return lines
})

const pointScreen = computed(() => project(x0.value, y0.value, z0.value))
const planePoints = computed(() => {
  const d = 0.72
  return [[-d, -d], [d, -d], [d, d], [-d, d]].map(([u, v]) => {
    const z = z0.value + fx.value * u + fy.value * v
    return project(x0.value + u, y0.value + v, z)
  }).map(p => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ')
})
const gradientEnd = computed(() => {
  const n = Math.max(gradNorm.value, 0.001)
  return project(x0.value + fx.value / n, y0.value + fy.value / n, z0.value)
})

function polarPoint(cx, cy, r, theta, lift = 0) {
  return { x: cx + r * Math.cos(theta), y: cy + r * 0.55 * Math.sin(theta) - lift }
}
function polarPath(cx, cy, r0, r1, a0, a1, lift = 0) {
  const points = []
  const count = 4
  for (let i = 0; i <= count; i++) points.push(polarPoint(cx, cy, r1, a0 + (a1 - a0) * i / count, lift))
  for (let i = count; i >= 0; i--) points.push(polarPoint(cx, cy, r0, a0 + (a1 - a0) * i / count, lift))
  return pathFrom(points, true)
}

const polarBase = computed(() => {
  const cells = []
  const nr = radialN.value
  const nt = 12
  const dr = 1 / nr
  const dt = 2 * Math.PI / nt
  for (let ir = 0; ir < nr; ir++) {
    for (let it = 0; it < nt; it++) {
      const r0 = ir * dr
      const r1 = (ir + 1) * dr
      const r = (r0 + r1) / 2
      const theta = (it + 0.5) * dt
      const value = 1 + r * r
      const contribution = value * r * dr * dt
      cells.push({ r0, r1, a0: it * dt, a1: (it + 1) * dt, r, theta, value, contribution })
    }
  }
  return cells
})

const steps = computed(() => {
  const cells = polarBase.value
  const out = [{ k: 0, sum: 0, r: 0, theta: 0, desc: `尚未累加：把单位圆分成 ${cells.length} 个极坐标小扇环。` }]
  let sum = 0
  cells.forEach((cell, i) => {
    sum += cell.contribution
    out.push({
      k: i + 1,
      sum,
      r: cell.r,
      theta: cell.theta,
      desc: `第 ${i + 1}/${cells.length} 柱：r=${cell.r.toFixed(3)}，高度 1+r²=${cell.value.toFixed(3)}，累计 ${sum.toFixed(5)}，误差 ${Math.abs(sum - exactIntegral).toFixed(5)}。`
    })
  })
  return out
})
const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)

const polarCells = computed(() => polarBase.value.map((cell, i) => {
  const active = i < cur.value.k
  const h = active ? 10 + cell.value * 7 : 0
  const cx = 195, cy = 465, scale = 100
  const baseOuter0 = polarPoint(cx, cy, cell.r1 * scale, cell.a0)
  const topOuter0 = polarPoint(cx, cy, cell.r1 * scale, cell.a0, h)
  const topOuter1 = polarPoint(cx, cy, cell.r1 * scale, cell.a1, h)
  const baseOuter1 = polarPoint(cx, cy, cell.r1 * scale, cell.a1)
  return {
    active,
    fill: `hsl(${215 - cell.value * 24}, 72%, ${66 - cell.value * 7}%)`,
    top: polarPath(cx, cy, cell.r0 * scale, cell.r1 * scale, cell.a0, cell.a1, h),
    side: pathFrom([baseOuter0, topOuter0, topOuter1, baseOuter1], true)
  }
}))

function resetView() { player.reset() }
function fmt(v) { return Number.isFinite(v) ? Number(v).toFixed(4) : '-' }

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
.mv-wrap { display: flex; gap: 18px; align-items: flex-start; flex-wrap: wrap; }
.plot-host { flex: 2 1 560px; min-width: 0; }
.mv-svg { display: block; width: 100%; height: auto; min-height: 330px; }
.mv-panel { flex: 1 1 290px; min-width: 260px; }
.section-title { font-size: 13px; font-weight: 700; fill: #334155; }
.hint { font-size: 11px; fill: #8b95a3; }
.formula code { display: block; padding: 9px 11px; border-radius: 7px; background: #f2f4f8; color: #334155; }
.param-row { display: grid; grid-template-columns: 105px 1fr; align-items: center; gap: 10px; margin-top: 10px; font-size: 12px; }
.info-row { display: flex; justify-content: space-between; gap: 12px; padding: 6px 0; border-bottom: 1px dashed #edf0f5; font-size: 13px; }
.plane-text { max-width: 185px; text-align: right; font-size: 11px; color: #b46a15; }
.tip { margin-top: 12px; line-height: 1.75; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; }
.dot.surface { background: #7298ee; }
.dot.plane { background: #f7b955; }
.dot.gradient { background: #e05252; }
.dot.integral { background: #3b6ef6; }
@media (max-width: 640px) {
  .mv-panel { min-width: 100%; }
  .mv-svg { min-height: 260px; }
}
</style>
