<template>
  <VisFrame title="矩阵线性变换 · 基向量的舞蹈" desc="矩阵 A 把基向量 i=(1,0)、j=(0,1) 映射到 A 的列向量，整个平面随之变形；行列式 det(A) 即面积伸缩倍数" :player="player" :status-text="statusText" back-to="/knowledge/25">
    <template #extra>
      <el-select v-model="presetKey" size="small" style="width:170px" @change="applyPreset">
        <el-option v-for="p in PRESETS" :key="p.key" :value="p.key" :label="p.label" />
      </el-select>
      <el-button size="small" plain @click="toggleShape">{{ shape === 'square' ? '看单位圆' : '看单位方格' }}</el-button>
    </template>

    <div class="mt-wrap">
      <svg :width="W" :height="H" class="mt-svg">
        <defs>
          <clipPath id="mtClip"><rect :x="0" :y="0" :width="W" :height="H" /></clipPath>
        </defs>
        <g clip-path="url(#mtClip)">
          <!-- 原始网格（虚线，参考） -->
          <g opacity="0.28">
            <line v-for="(l, i) in baseGrid" :key="'bg'+i" :x1="l.x1" :y1="l.y1" :x2="l.x2" :y2="l.y2" stroke="#8b95a3" stroke-dasharray="3 4" />
          </g>
          <!-- 变换后的网格线 -->
          <g>
            <line v-for="(l, i) in gridLines" :key="'g'+i" :x1="l.x1" :y1="l.y1" :x2="l.x2" :y2="l.y2" :stroke="l.color" stroke-width="1.2" />
          </g>
          <path :d="shapePath" :fill="shape === 'square' ? '#3b6ef6' : 'none'" fill-opacity="0.16"
                :stroke="shape === 'square' ? '#3b6ef6' : '#7b61ff'" stroke-width="2" />
          <!-- 基向量 -->
          <g>
            <line :x1="O.x" :y1="O.y" :x2="O.x + iHat.x" :y2="O.y - iHat.y" stroke="#e05252" stroke-width="3" />
            <polygon :points="arrow(O.x + iHat.x, O.y - iHat.y, angleOf(iHat.x, -iHat.y))" fill="#e05252" />
            <text :x="O.x + iHat.x + 8" :y="O.y - iHat.y - 6" font-size="12" fill="#e05252" font-weight="700">i'</text>

            <line :x1="O.x" :y1="O.y" :x2="O.x + jHat.x" :y2="O.y - jHat.y" stroke="#22a06b" stroke-width="3" />
            <polygon :points="arrow(O.x + jHat.x, O.y - jHat.y, angleOf(jHat.x, -jHat.y))" fill="#22a06b" />
            <text :x="O.x + jHat.x + 8" :y="O.y - jHat.y - 6" font-size="12" fill="#22a06b" font-weight="700">j'</text>
          </g>
        </g>
        <text :x="12" :y="20" font-size="12" fill="#8b95a3">t = {{ t.toFixed(2) }}（0 = 原状，1 = 完全变换）</text>
      </svg>

      <div class="mt-panel">
        <div class="matrix-box">
          <div class="small muted">变换矩阵 A</div>
          <div class="matrix">
            <span class="brk">[</span>
            <div class="mcol"><b>{{ fmt(m[0]) }}</b><b>{{ fmt(m[2]) }}</b></div>
            <div class="mcol"><b>{{ fmt(m[1]) }}</b><b>{{ fmt(m[3]) }}</b></div>
            <span class="brk">]</span>
          </div>
          <div class="sliders">
            <label>a <el-slider v-model="mRaw[0]" :min="-3" :max="3" :step="0.1" @input="onSlide" /></label>
            <label>b <el-slider v-model="mRaw[1]" :min="-3" :max="3" :step="0.1" @input="onSlide" /></label>
            <label>c <el-slider v-model="mRaw[2]" :min="-3" :max="3" :step="0.1" @input="onSlide" /></label>
            <label>d <el-slider v-model="mRaw[3]" :min="-3" :max="3" :step="0.1" @input="onSlide" /></label>
          </div>
        </div>
        <el-divider />
        <div class="info-row"><span>i = (1,0) → A 的第 1 列</span><b style="color:#e05252">({{ fmt(m[0]) }}, {{ fmt(m[2]) }})</b></div>
        <div class="info-row"><span>j = (0,1) → A 的第 2 列</span><b style="color:var(--success)">({{ fmt(m[1]) }}, {{ fmt(m[3]) }})</b></div>
        <div class="info-row"><span>行列式 det(A) = ad - bc</span><b>{{ fmt(det) }}</b></div>
        <div class="info-row"><span>面积伸缩倍数 |det(A)|</span><b>{{ fmt(Math.abs(det)) }}</b></div>
        <div class="info-row">
          <span>是否可逆</span>
          <el-tag size="small" :type="Math.abs(det) < 1e-6 ? 'danger' : 'success'">
            {{ Math.abs(det) < 1e-6 ? '不可逆（降维压缩）' : '可逆' }}
          </el-tag>
        </div>
        <div class="info-row" v-if="Math.abs(det) < 1e-6"><span>压缩到</span><b>一条直线 / 一个点</b></div>
        <p class="small muted tip">{{ presetNote }}</p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#e05252"></i> i' = A·(1,0)，A 的第 1 列</span>
      <span><i class="dot" style="background:#22a06b"></i> j' = A·(0,1)，A 的第 2 列</span>
      <span><i class="dot" style="background:#3b6ef6"></i> 单位方格 → 平行四边形</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const PRESETS = [
  { key: 'identity', label: '单位矩阵 I', m: [1, 0, 0, 1], note: '不做任何变换，i、j 保持原位，面积不变（det=1）。' },
  { key: 'scale', label: '缩放 (2, 1.5)', m: [2, 0, 0, 1.5], note: '对角矩阵：只做坐标轴方向的拉伸，面积放大 3 倍（det=3）。' },
  { key: 'rotate', label: '旋转 45°', m: [0.707, -0.707, 0.707, 0.707], note: '旋转矩阵：保持长度与面积不变，det=1，属于正交变换。' },
  { key: 'shear', label: '剪切 (x 方向)', m: [1, 1, 0, 1], note: '剪切：j 被推斜而 i 不动，面积不变（det=1），形状改变。' },
  { key: 'reflect', label: '关于 x 轴反射', m: [1, 0, 0, -1], note: '反射：det=-1，面积大小不变但定向翻转（手性改变）。' },
  { key: 'project', label: '投影到 x 轴', m: [1, 0, 0, 0], note: '投影：det=0，整个平面被压成一条直线，信息丢失，不可逆。' }
]
const presetKey = ref('shear')
const mRaw = reactive([1, 1, 0, 1])
const shape = ref('square')

function applyPreset() {
  const p = PRESETS.find(x => x.key === presetKey.value)
  if (p) { mRaw[0] = p.m[0]; mRaw[1] = p.m[1]; mRaw[2] = p.m[2]; mRaw[3] = p.m[3] }
  player.reset()
}
function onSlide() { presetKey.value = 'custom'; player.reset() }
function toggleShape() { shape.value = shape.value === 'square' ? 'circle' : 'square' }

const W = 520, H = 380
const O = { x: 250, y: 190 }
const U = 52 // 每单位像素
const presetNote = computed(() => {
  const p = PRESETS.find(x => x.key === presetKey.value)
  return p ? p.note : '自定义矩阵：拖动滑块观察基向量与网格的变化。'
})

const STEPS_N = 24
const steps = computed(() => {
  const [a, b, c, d] = mRaw
  const out = []
  for (let i = 0; i <= STEPS_N; i++) {
    const t = i / STEPS_N
    const m = [1 + (a - 1) * t, b * t, c * t, 1 + (d - 1) * t]
    out.push({ t, m, desc: describe(t, m) })
  }
  return out
})
function describe(t, m) {
  if (t === 0) return '初始状态：A = I，i=(1,0)、j=(0,1)，单位方格面积为 1'
  if (t >= 1) {
    const det = m[0] * m[3] - m[1] * m[2]
    return `变换完成：det(A) = ${det.toFixed(3)}，面积变为原来的 ${Math.abs(det).toFixed(3)} 倍${Math.abs(det) < 1e-6 ? '（被压缩，不可逆）' : ''}`
  }
  return `过渡中 t = ${t.toFixed(2)}：i → (${m[0].toFixed(2)}, ${m[2].toFixed(2)})，j → (${m[1].toFixed(2)}, ${m[3].toFixed(2)})`
}

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const m = computed(() => cur.value.m)
const t = computed(() => cur.value.t)
const det = computed(() => m.value[0] * m.value[3] - m.value[1] * m.value[2])
const statusText = computed(() => cur.value.desc)

const iHat = computed(() => ({ x: m.value[0] * U, y: m.value[2] * U }))
const jHat = computed(() => ({ x: m.value[1] * U, y: m.value[3] * U }))

function tx(x, y) { const [a, b, c, d] = m.value; return a * x + b * y }
function ty(x, y) { const [a, b, c, d] = m.value; return c * x + d * y }
function px(x, y) { return O.x + tx(x, y) * U }
function py(x, y) { return O.y - ty(x, y) * U }

const baseGrid = computed(() => {
  const lines = []
  for (let k = -6; k <= 6; k++) {
    lines.push({ x1: O.x + k * U, y1: 0, x2: O.x + k * U, y2: H })
    lines.push({ x1: 0, y1: O.y - k * U, x2: W, y2: O.y - k * U })
  }
  return lines
})

const gridLines = computed(() => {
  const lines = []
  for (let k = -6; k <= 6; k++) {
    // 竖线 x = k
    lines.push({ x1: px(k, -6), y1: py(k, -6), x2: px(k, 6), y2: py(k, 6), color: '#c8d3e6' })
    // 横线 y = k
    lines.push({ x1: px(-6, k), y1: py(-6, k), x2: px(6, k), y2: py(6, k), color: '#c8d3e6' })
  }
  return lines
})

const shapePath = computed(() => {
  const n = 64
  let d = ''
  for (let i = 0; i <= n; i++) {
    const ang = (Math.PI * 2 * i) / n
    let x, y
    if (shape.value === 'circle') { x = Math.cos(ang); y = Math.sin(ang) }
    else {
      // 单位正方形周长参数化
      const p = (i / n) * 4
      if (p <= 1) { x = p; y = 0 }
      else if (p <= 2) { x = 1; y = p - 1 }
      else if (p <= 3) { x = 1 - (p - 2); y = 1 }
      else { x = 0; y = 1 - (p - 3) }
    }
    d += (i === 0 ? 'M' : 'L') + px(x, y).toFixed(2) + ' ' + py(x, y).toFixed(2) + ' '
  }
  return d + 'Z'
})

function angleOf(dx, dy) { return Math.atan2(dy, dx) }
function arrow(x, y, ang) {
  const s = 9
  const a1 = ang + Math.PI * 0.85
  const a2 = ang - Math.PI * 0.85
  return `${x},${y} ${x + s * Math.cos(a1)},${y + s * Math.sin(a1)} ${x + s * Math.cos(a2)},${y + s * Math.sin(a2)}`
}
function fmt(v) { return Number(v.toFixed(3)).toString() }
</script>

<style scoped>
.mt-wrap { display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap; }
.mt-svg { background: #fcfdff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.mt-panel { flex: 1; min-width: 300px; }
.matrix-box { display: flex; gap: 16px; align-items: flex-start; flex-wrap: wrap; }
.matrix { display: flex; align-items: center; gap: 6px; }
.brk { font-size: 34px; color: var(--text-2); font-weight: 300; }
.mcol { display: flex; flex-direction: column; gap: 8px; text-align: center; }
.mcol b { min-width: 46px; font-size: 14px; }
.sliders { flex: 1; min-width: 200px; }
.sliders label { display: grid; grid-template-columns: 18px 1fr; align-items: center; font-size: 12px; color: var(--text-2); }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.tip { margin-top: 10px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
