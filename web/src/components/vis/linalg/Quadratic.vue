<template>
  <VisFrame
    title="二次型与合同对角化"
    desc="为什么看这个动画：等高线的开合方向由特征值决定，旋转坐标轴后交叉项消失，正定性便能从标准形一眼读出。"
    :player="player"
    :status-text="statusText"
    back-to="/knowledge/88"
  >
    <template #extra>
      <el-tag :type="kind.tag">{{ kind.text }}</el-tag>
      <span class="small muted">旋转进度 {{ Math.round(cur.progress * 100) }}%</span>
    </template>

    <div class="qd-wrap">
      <div ref="plotHost" class="plot-host">
        <svg viewBox="0 0 720 380" class="qd-svg" role="img" aria-label="二次型等高线和曲面">
          <rect x="1" y="1" width="718" height="378" rx="10" fill="#fcfdff" stroke="#e4e8ef" />
          <text x="18" y="25" class="section-title">等高线与正交旋转</text>
          <text x="382" y="25" class="section-title">曲面 z=ax²+2bxy+cy²</text>

          <!-- 色块按 f(x,y) 的正负和大小分层，边界近似等高线。 -->
          <g>
            <rect v-for="(cell, i) in heatCells" :key="'h' + i" :x="cell.x" :y="cell.y" :width="cell.w + 0.3" :height="cell.h + 0.3" :fill="cell.fill" />
            <path v-for="(line, i) in contours" :key="'c' + i" :d="line.d" fill="none" :stroke="line.zero ? '#243247' : '#ffffff'" :stroke-width="line.zero ? 2.2 : 1.05" :opacity="line.zero ? 0.9 : 0.8" />
          </g>
          <line x1="32" y1="190" x2="338" y2="190" stroke="#667085" stroke-width="1.2" />
          <line x1="185" y1="38" x2="185" y2="342" stroke="#667085" stroke-width="1.2" />
          <!-- 动画把原坐标轴旋转到特征向量方向；此时二次型没有 uv 交叉项。 -->
          <line :x1="axis1.x1" :y1="axis1.y1" :x2="axis1.x2" :y2="axis1.y2" stroke="#e05252" stroke-width="3" marker-end="url(#qd-arrow-red)" />
          <line :x1="axis2.x1" :y1="axis2.y1" :x2="axis2.x2" :y2="axis2.y2" stroke="#22a06b" stroke-width="3" marker-end="url(#qd-arrow-green)" />
          <text :x="axis1.x2 - 5" :y="axis1.y2 - 7" fill="#c53d3d" font-size="12">u</text>
          <text :x="axis2.x2 + 5" :y="axis2.y2 - 4" fill="#1a7a52" font-size="12">v</text>

          <path v-for="(line, i) in surfaceMesh" :key="'s' + i" :d="line" fill="none" :stroke="i % 2 ? '#7799e9' : '#8b5cf6'" stroke-width="1.15" opacity="0.78" />
          <line x1="380" y1="312" x2="692" y2="312" stroke="#8b95a3" />
          <text v-if="!compact" x="535" y="355" text-anchor="middle" font-size="11" fill="#8b95a3">曲率方向与红/绿特征向量一致</text>
          <defs>
            <marker id="qd-arrow-red" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 Z" fill="#e05252" /></marker>
            <marker id="qd-arrow-green" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 Z" fill="#22a06b" /></marker>
          </defs>
        </svg>
      </div>

      <div class="qd-panel">
        <div class="coefficient">
          <span>a={{ a.toFixed(1) }}</span>
          <el-slider v-model="a" :min="-3" :max="3" :step="0.1" :show-tooltip="false" @input="player.reset()" />
        </div>
        <div class="coefficient">
          <span>b={{ b.toFixed(1) }}</span>
          <el-slider v-model="b" :min="-3" :max="3" :step="0.1" :show-tooltip="false" @input="player.reset()" />
        </div>
        <div class="coefficient">
          <span>c={{ c.toFixed(1) }}</span>
          <el-slider v-model="c" :min="-3" :max="3" :step="0.1" :show-tooltip="false" @input="player.reset()" />
        </div>
        <div class="formula"><code>f(x,y)={{ signedFormula }}</code></div>
        <el-divider />
        <div class="info-row"><span>矩阵 A</span><b>[[{{ fmt(a) }}, {{ fmt(b) }}], [{{ fmt(b) }}, {{ fmt(c) }}]]</b></div>
        <div class="info-row"><span>λ₁</span><b style="color: #e05252">{{ fmt(lambda1) }}</b></div>
        <div class="info-row"><span>λ₂</span><b style="color: #22a06b">{{ fmt(lambda2) }}</b></div>
        <div class="info-row"><span>行列式 ac-b²</span><b>{{ fmt(determinant) }}</b></div>
        <div class="info-row"><span>正交旋转角 θ</span><b>{{ fmt(thetaDeg) }}°</b></div>
        <div class="standard"><span>标准形</span><code>{{ fmt(lambda1) }}u² {{ lambda2 >= 0 ? '+' : '-' }} {{ fmt(Math.abs(lambda2)) }}v²</code></div>
        <p class="small muted tip">合同变换保持正、负平方项的个数不变（惯性定律）。当两个特征值同正/同负时等高线封闭；异号时出现双曲线鞍面。</p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot positive"></i> f&gt;0</span>
      <span><i class="dot negative"></i> f&lt;0</span>
      <span><i class="dot axis-u"></i> λ₁ 特征方向</span>
      <span><i class="dot axis-v"></i> λ₂ 特征方向</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const a = ref(2)
const b = ref(1.2)
const c = ref(1)
const plotHost = ref(null)
const viewportWidth = ref(720)
let resizeObserver = null

const compact = computed(() => viewportWidth.value < 540)
const determinant = computed(() => a.value * c.value - b.value * b.value)
const discriminant = computed(() => Math.hypot(a.value - c.value, 2 * b.value))
const lambda1 = computed(() => (a.value + c.value + discriminant.value) / 2)
const lambda2 = computed(() => (a.value + c.value - discriminant.value) / 2)
const theta = computed(() => 0.5 * Math.atan2(2 * b.value, a.value - c.value))
const thetaDeg = computed(() => theta.value * 180 / Math.PI)
const kind = computed(() => {
  const eps = 1e-7
  if (lambda2.value > eps) return { text: '正定', tag: 'success' }
  if (lambda1.value < -eps) return { text: '负定', tag: 'danger' }
  if (lambda1.value > eps && lambda2.value < -eps) return { text: '不定', tag: 'warning' }
  if (Math.abs(lambda1.value) <= eps && Math.abs(lambda2.value) <= eps) return { text: '零二次型', tag: 'info' }
  return { text: '半正定/半负定', tag: 'info' }
})
const signedFormula = computed(() => `${fmt(a.value)}x² ${b.value >= 0 ? '+' : '-'} ${fmt(Math.abs(2 * b.value))}xy ${c.value >= 0 ? '+' : '-'} ${fmt(Math.abs(c.value))}y²`)
function quadratic(x, y) { return a.value * x * x + 2 * b.value * x * y + c.value * y * y }

const steps = computed(() => Array.from({ length: 31 }, (_, i) => {
  const progress = i / 30
  const angle = thetaDeg.value * progress
  return {
    progress,
    angle,
    desc: i === 0
      ? `原坐标下交叉项系数为 2b=${fmt(2 * b.value)}，开始寻找主轴。`
      : i === 30
        ? `旋转 ${fmt(thetaDeg.value)}° 后交叉项消失，得到 ${fmt(lambda1.value)}u² ${lambda2.value >= 0 ? '+' : '-'} ${fmt(Math.abs(lambda2.value))}v²，判定为${kind.value.text}。`
        : `正交坐标轴已旋转 ${fmt(angle)}°：特征方向逐渐与等高线主轴重合。`
  }
}))
const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)

function map2X(x) { return 185 + x / 2 * 153 }
function map2Y(y) { return 190 - y / 2 * 152 }
const heatCells = computed(() => {
  const cells = []
  const n = compact.value ? 22 : 30
  const step = 4 / n
  const maxAbs = Math.max(0.1, ...[-2, 2].flatMap(x => [-2, 2].map(y => Math.abs(quadratic(x, y)))))
  for (let iy = 0; iy < n; iy++) {
    for (let ix = 0; ix < n; ix++) {
      const x = -2 + (ix + 0.5) * step
      const y = -2 + (iy + 0.5) * step
      const value = quadratic(x, y) / maxAbs
      const strength = Math.min(1, Math.abs(value))
      cells.push({
        x: map2X(x - step / 2),
        y: map2Y(y + step / 2),
        w: 306 / n,
        h: 304 / n,
        fill: value >= 0 ? `rgba(59,110,246,${0.1 + 0.58 * strength})` : `rgba(242,153,74,${0.1 + 0.62 * strength})`
      })
    }
  }
  return cells
})

// 用 marching squares 在每个小网格内线性插值，得到真实的二次型等高线。
const contours = computed(() => {
  const maxCorner = Math.max(1, ...[-2, 2].flatMap(x => [-2, 2].map(y => Math.abs(quadratic(x, y)))))
  const levels = [-0.65, -0.3, 0, 0.3, 0.65].map(v => v * maxCorner)
  const n = 32
  const step = 4 / n
  const result = []
  const edgePoint = (p1, p2, v1, v2, level) => {
    const t = Math.abs(v2 - v1) < 1e-9 ? 0.5 : (level - v1) / (v2 - v1)
    return { x: p1.x + (p2.x - p1.x) * t, y: p1.y + (p2.y - p1.y) * t }
  }
  for (const level of levels) {
    for (let iy = 0; iy < n; iy++) {
      for (let ix = 0; ix < n; ix++) {
        const x0 = -2 + ix * step, x1 = x0 + step
        const y0 = -2 + iy * step, y1 = y0 + step
        const ps = [{ x: x0, y: y0 }, { x: x1, y: y0 }, { x: x1, y: y1 }, { x: x0, y: y1 }]
        const vs = ps.map(p => quadratic(p.x, p.y))
        const hits = []
        for (let edge = 0; edge < 4; edge++) {
          const next = (edge + 1) % 4
          if ((vs[edge] - level) * (vs[next] - level) < 0 || vs[edge] === level) hits.push(edgePoint(ps[edge], ps[next], vs[edge], vs[next], level))
        }
        if (hits.length >= 2) {
          for (let k = 0; k + 1 < hits.length; k += 2) {
            result.push({ d: `M${map2X(hits[k].x).toFixed(1)},${map2Y(hits[k].y).toFixed(1)} L${map2X(hits[k + 1].x).toFixed(1)},${map2Y(hits[k + 1].y).toFixed(1)}`, zero: Math.abs(level) < 1e-9 })
          }
        }
      }
    }
  }
  return result
})

function axisLine(angle, length = 128) {
  return { x1: 185, y1: 190, x2: 185 + length * Math.cos(angle), y2: 190 - length * Math.sin(angle) }
}
const axis1 = computed(() => axisLine(theta.value * cur.value.progress))
const axis2 = computed(() => axisLine(Math.PI / 2 + theta.value * cur.value.progress, 112))

function project3(x, y, z) {
  const xr = 0.82 * x - 0.58 * y
  const yr = 0.42 * x + 0.6 * y
  const scaleZ = Math.max(2, Math.abs(lambda1.value), Math.abs(lambda2.value))
  return { x: 535 + xr * 67, y: 205 + yr * 38 - z / scaleZ * 34 }
}
const surfaceMesh = computed(() => {
  const lines = []
  for (let axis = 0; axis < 2; axis++) {
    for (let i = 0; i < 9; i++) {
      const fixed = -1.7 + 3.4 * i / 8
      const points = []
      for (let j = 0; j <= 28; j++) {
        const moving = -1.7 + 3.4 * j / 28
        const x = axis ? fixed : moving
        const y = axis ? moving : fixed
        points.push(project3(x, y, quadratic(x, y)))
      }
      lines.push(points.map((p, k) => `${k ? 'L' : 'M'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' '))
    }
  }
  return lines
})

function fmt(value) { return Number.isFinite(Number(value)) ? Number(value).toFixed(3) : '—' }

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
.qd-wrap { display: flex; gap: 18px; align-items: flex-start; flex-wrap: wrap; }
.plot-host { flex: 2 1 580px; min-width: 0; }
.qd-svg { display: block; width: 100%; height: auto; min-height: 310px; }
.qd-panel { flex: 1 1 285px; min-width: 260px; }
.section-title { font-size: 13px; font-weight: 700; fill: #334155; }
.coefficient { display: grid; grid-template-columns: 55px 1fr; align-items: center; gap: 10px; font-size: 12px; margin-bottom: 5px; }
.formula code, .standard code { display: block; padding: 8px 10px; border-radius: 7px; background: #f2f4f8; font-size: 12px; }
.info-row { display: flex; justify-content: space-between; gap: 10px; padding: 5px 0; border-bottom: 1px dashed #edf0f5; font-size: 12px; }
.info-row b { text-align: right; }
.standard { margin-top: 12px; font-size: 12px; color: #526071; }
.standard code { margin-top: 5px; color: #8b5cf6; font-size: 14px; font-weight: 700; }
.tip { line-height: 1.75; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; }
.dot.positive { background: #3b6ef6; }
.dot.negative { background: #f2994a; }
.dot.axis-u { background: #e05252; }
.dot.axis-v { background: #22a06b; }
@media (max-width: 640px) {
  .qd-panel { min-width: 100%; }
  .qd-svg { min-height: 250px; }
}
</style>
