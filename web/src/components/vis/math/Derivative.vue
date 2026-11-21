<template>
  <VisFrame title="导数 · 从割线到切线" desc="当 h→0 时，割线斜率 [f(a+h)-f(a)]/h 趋近于切线斜率 f'(a) —— 这就是导数的几何意义" :player="player" :status-text="statusText" back-to="/knowledge/23">
    <template #extra>
      <el-select v-model="presetKey" size="small" style="width:190px" @change="player.reset()">
        <el-option v-for="p in PRESETS" :key="p.key" :value="p.key" :label="p.label" />
      </el-select>
      <el-slider v-model="aIdx" :min="0" :max="4" :step="1" style="width:120px" :show-tooltip="false" @input="player.reset()" />
      <span class="small muted">a = {{ a }}</span>
    </template>

    <div class="dv-wrap">
      <svg :width="W" :height="H" class="dv-svg">
        <line v-for="g in xGrid" :key="'gx'+g" :x1="mapX(g)" :y1="mapY(r1)" :x2="mapX(g)" :y2="mapY(r0)" stroke="#eef1f6" />
        <line v-for="g in yGrid" :key="'gy'+g" :x1="mapX(d0)" :y1="mapY(g)" :x2="mapX(d1)" :y2="mapY(g)" stroke="#eef1f6" />
        <line :x1="mapX(d0)" :y1="mapY(0)" :x2="mapX(d1)" :y2="mapY(0)" stroke="#8b95a3" stroke-width="1.5" />
        <line :x1="mapX(0)" :y1="mapY(r0)" :x2="mapX(0)" :y2="mapY(r1)" stroke="#8b95a3" stroke-width="1.5" />

        <path :d="curvePath" fill="none" stroke="#1f2733" stroke-width="2" />

        <!-- 左侧割线（a-h） -->
        <line :x1="mapX(ax - h)" :y1="mapY(f(ax - h))" :x2="mapX(ax + h)" :y2="mapY(f(ax + h))" stroke="#22a06b" stroke-width="2" />
        <!-- 切线 -->
        <line :x1="mapX(tanX0)" :y1="mapY(tanY0)" :x2="mapX(tanX1)" :y2="mapY(tanY1)" stroke="#e05252" stroke-width="2.5" />

        <!-- h 的标注（x 轴上的区间） -->
        <rect :x="mapX(ax)" :y="mapY(0) - 4" :width="mapX(ax + h) - mapX(ax)" height="8" fill="#3b6ef6" fill-opacity="0.5" />
        <text :x="(mapX(ax) + mapX(ax + h)) / 2" :y="mapY(0) + 22" text-anchor="middle" font-size="11" fill="#3b6ef6">h = {{ fmt(h) }}</text>

        <!-- 三点 -->
        <circle :cx="mapX(ax - h)" :cy="mapY(f(ax - h))" r="5" fill="#22a06b" />
        <circle :cx="mapX(ax + h)" :cy="mapY(f(ax + h))" r="5" fill="#22a06b" />
        <circle :cx="mapX(ax)" :cy="mapY(f(ax))" r="6.5" fill="#e05252" />
        <text :x="mapX(ax) + 10" :y="mapY(f(ax)) - 10" font-size="11" fill="#e05252">A(a, f(a)) = ({{ fmt(ax) }}, {{ fmt(f(ax)) }})</text>
      </svg>

      <div class="dv-panel">
        <div class="def-box">
          <div class="small muted">导数定义（差商的极限）</div>
          <code>f'(a) = lim(h→0) [ f(a+h) - f(a) ] / h</code>
        </div>
        <el-divider />
        <div class="info-row"><span>当前步长 h</span><b style="color:var(--brand)">{{ fmt(h) }}</b></div>
        <div class="info-row"><span>割线斜率（差商）</span><b style="color:var(--success)">{{ fmt(secant) }}</b></div>
        <div class="info-row"><span>切线斜率 f'(a)</span><b style="color:#e05252">{{ fmt(deriv) }}</b></div>
        <div class="info-row">
          <span>绝对误差</span>
          <el-tag size="small" :type="err < 0.01 ? 'success' : 'warning'">{{ fmt(err) }}</el-tag>
        </div>
        <el-divider />
        <div class="tbl">
          <div class="tbl-head"><span>h</span><span>割线斜率</span><span>误差</span></div>
          <div
            v-for="(s, i) in player.steps.value" :key="i"
            class="tbl-row" :class="{ active: i === player.idx.value }" @click="player.seek(i)"
          >
            <span>{{ s.h }}</span><span>{{ fmt(s.secant) }}</span><span>{{ fmt(s.err) }}</span>
          </div>
        </div>
        <p class="small muted tip">h 越小，割线越贴近切线；当 h→0 时割线的极限位置就是切线，其斜率即导数。</p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#e05252"></i> 切线（斜率 = 导数）</span>
      <span><i class="dot" style="background:#22a06b"></i> 割线（斜率 = 差商）</span>
      <span><i class="dot" style="background:#3b6ef6"></i> 步长 h</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const PRESETS = [
  { key: 'sin', label: 'f(x) = sin x', f: x => Math.sin(x), df: x => Math.cos(x), domain: [-1, 7], range: [-1.6, 1.6] },
  { key: 'sq', label: 'f(x) = x²', f: x => x * x, df: x => 2 * x, domain: [-2, 6], range: [-2, 12] },
  { key: 'cube', label: 'f(x) = x³ - 3x', f: x => x * x * x - 3 * x, df: x => 3 * x * x - 3, domain: [-3, 5], range: [-8, 14] },
  { key: 'exp', label: 'f(x) = e^x', f: x => Math.exp(x), df: x => Math.exp(x), domain: [-2, 4], range: [-1, 22] }
]
const A_VALUES = [-1.5, -0.5, 0, 1, 2]

const presetKey = ref('sq')
const aIdx = ref(4)
const preset = computed(() => PRESETS.find(p => p.key === presetKey.value) || PRESETS[0])
const ax = computed(() => A_VALUES[aIdx.value])
const a = computed(() => ax.value)

const W = 560, H = 340, padL = 48, padR = 18, padT = 18, padB = 36
const d0 = computed(() => preset.value.domain[0])
const d1 = computed(() => preset.value.domain[1])
const r0 = computed(() => preset.value.range[0])
const r1 = computed(() => preset.value.range[1])

function mapX(x) { return padL + ((x - d0.value) / (d1.value - d0.value)) * (W - padL - padR) }
function mapY(y) { return padT + ((r1.value - y) / (r1.value - r0.value)) * (H - padT - padB) }
function f(x) { return preset.value.f(x) }

const xGrid = computed(() => grid(d0.value, d1.value))
const yGrid = computed(() => grid(r0.value, r1.value))
function grid(lo, hi) {
  const out = []
  for (let i = 0; i <= 8; i++) {
    const v = Number((lo + ((hi - lo) * i) / 8).toFixed(2))
    if (out.indexOf(v) === -1) out.push(v)
  }
  return out
}

const curvePath = computed(() => {
  let d = ''
  const n = 400
  for (let i = 0; i <= n; i++) {
    const x = d0.value + ((d1.value - d0.value) * i) / n
    const y = f(x)
    if (!isFinite(y)) continue
    d += (i === 0 ? 'M' : 'L') + mapX(x).toFixed(2) + ' ' + Math.max(-50, Math.min(H + 50, mapY(y))).toFixed(2) + ' '
  }
  return d
})

const H_LIST = [2, 1, 0.5, 0.25, 0.1, 0.05, 0.01, 0.001, 0.0001]

const steps = computed(() => {
  const A = ax.value
  const fa = f(A)
  const dv = preset.value.df(A)
  return H_LIST.map(h => {
    const secant = (f(A + h) - fa) / h
    return {
      h, secant, deriv: dv, err: Math.abs(secant - dv),
      desc: `h = ${h}：差商 = [f(${fmtN(A + h, h)}) - f(${fmtN(A, h)})] / ${h} = ${secant.toFixed(6)}，与 f'(${fmtN(A, h)}) = ${dv.toFixed(6)} 相差 ${Math.abs(secant - dv).toFixed(8)}`
    }
  })
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const h = computed(() => cur.value.h)
const secant = computed(() => cur.value.secant)
const deriv = computed(() => cur.value.deriv)
const err = computed(() => cur.value.err)
const statusText = computed(() => cur.value.desc)

const tanX0 = computed(() => ax.value - 2)
const tanX1 = computed(() => ax.value + 2)
const tanY0 = computed(() => f(ax.value) + deriv.value * (tanX0.value - ax.value))
const tanY1 = computed(() => f(ax.value) + deriv.value * (tanX1.value - ax.value))

function fmt(v) {
  if (!isFinite(v)) return '-'
  const av = Math.abs(v)
  if (av >= 1e6) return v.toExponential(2)
  if (av < 1e-4 && av > 0) return v.toExponential(2)
  return Number(v.toFixed(4)).toString()
}
/**
 * 显示自变量取值。位数必须能分辨出增量 h：
 * 固定 3 位时 h=0.0001 会把 A+h=2.0001 截成 2，
 * 描述就成了 [f(2) - f(2)] / 0.0001 = 4.0001 —— 分子看着是 0，结果却是 4。
 */
function fmtN(v, ref) {
  let d = 3
  if (ref !== undefined) {
    const m = String(ref).split('.')[1]
    if (m) d = Math.max(d, m.length)
  }
  return Number(v.toFixed(d)).toString()
}
</script>

<style scoped>
.dv-wrap { display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap; }
.dv-svg { background: #fcfdff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.dv-panel { flex: 1; min-width: 300px; }
.def-box code { background: #f2f4f8; padding: 8px 10px; border-radius: 6px; display: block; font-size: 12px; line-height: 1.7; }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.tbl { font-size: 12px; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
.tbl-head { display: grid; grid-template-columns: 1fr 1.2fr 1fr; background: #f6f8fb; padding: 7px 10px; font-weight: 600; }
.tbl-row { display: grid; grid-template-columns: 1fr 1.2fr 1fr; padding: 6px 10px; border-top: 1px solid #f0f2f6; cursor: pointer; }
.tbl-row:hover { background: #f6f8fb; }
.tbl-row.active { background: var(--brand-light); color: var(--brand); font-weight: 600; }
.tip { margin-top: 10px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
