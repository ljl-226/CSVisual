<template>
  <VisFrame title="函数极限 · ε-δ 语言可视化" desc="任给 ε>0，找 δ>0，使得 0<|x-a|<δ 时恒有 |f(x)-L|<ε —— 直观理解极限的严格定义" :player="player" :status-text="statusText" back-to="/knowledge/22">
    <template #extra>
      <el-select v-model="presetKey" size="small" style="width:210px" @change="player.reset()">
        <el-option v-for="p in PRESETS" :key="p.key" :value="p.key" :label="p.label" />
      </el-select>
    </template>

    <div class="lim-wrap">
      <svg :width="W" :height="H" class="lim-svg">
        <!-- 网格 -->
        <g class="grid">
          <line v-for="g in xGrid" :key="'gx'+g" :x1="mapX(g)" :y1="mapY(r1)" :x2="mapX(g)" :y2="mapY(r0)" />
          <line v-for="g in yGrid" :key="'gy'+g" :x1="mapX(d0)" :y1="mapY(g)" :x2="mapX(d1)" :y2="mapY(g)" />
        </g>
        <!-- 坐标轴 -->
        <line :x1="mapX(d0)" :y1="mapY(0)" :x2="mapX(d1)" :y2="mapY(0)" stroke="#8b95a3" stroke-width="1.5" />
        <line :x1="mapX(0)" :y1="mapY(r0)" :x2="mapX(0)" :y2="mapY(r1)" stroke="#8b95a3" stroke-width="1.5" />
        <text v-for="g in xGrid" :key="'tx'+g" :x="mapX(g)" :y="mapY(0)+16" text-anchor="middle" font-size="10" fill="#8b95a3">{{ g }}</text>
        <text v-for="g in yGrid" :key="'ty'+g" :x="mapX(0)-6" :y="mapY(g)+3" text-anchor="end" font-size="10" fill="#8b95a3">{{ g }}</text>

        <!-- ε 带（横向） -->
        <rect
          :x="mapX(d0)" :y="mapY(L + eps)" :width="mapX(d1) - mapX(d0)"
          :height="Math.abs(mapY(L - eps) - mapY(L + eps))"
          fill="#3b6ef6" fill-opacity="0.10"
        />
        <line :x1="mapX(d0)" :y1="mapY(L + eps)" :x2="mapX(d1)" :y2="mapY(L + eps)" stroke="#3b6ef6" stroke-dasharray="4 3" />
        <line :x1="mapX(d0)" :y1="mapY(L - eps)" :x2="mapX(d1)" :y2="mapY(L - eps)" stroke="#3b6ef6" stroke-dasharray="4 3" />
        <text :x="mapX(d1) - 6" :y="mapY(L + eps) - 4" text-anchor="end" font-size="11" fill="#3b6ef6">L+ε = {{ fmt(L + eps) }}</text>
        <text :x="mapX(d1) - 6" :y="mapY(L - eps) + 12" text-anchor="end" font-size="11" fill="#3b6ef6">L-ε = {{ fmt(L - eps) }}</text>

        <!-- δ 带（纵向） -->
        <rect
          :x="mapX(a - delta)" :y="mapY(r1)" :width="Math.abs(mapX(a + delta) - mapX(a - delta))"
          :height="mapY(r0) - mapY(r1)"
          fill="#22a06b" fill-opacity="0.12"
        />
        <line :x1="mapX(a - delta)" :y1="mapY(r0)" :x2="mapX(a - delta)" :y2="mapY(r1)" stroke="#22a06b" stroke-dasharray="4 3" />
        <line :x1="mapX(a + delta)" :y1="mapY(r0)" :x2="mapX(a + delta)" :y2="mapY(r1)" stroke="#22a06b" stroke-dasharray="4 3" />

        <!-- 极限值 L -->
        <line :x1="mapX(d0)" :y1="mapY(L)" :x2="mapX(d1)" :y2="mapY(L)" stroke="#e05252" stroke-width="1.2" stroke-dasharray="6 4" />
        <text :x="mapX(d0) + 6" :y="mapY(L) - 5" font-size="11" fill="#e05252">L = {{ fmt(L) }}</text>

        <!-- 函数曲线 -->
        <path v-for="(seg, i) in curvePaths" :key="'c'+i" :d="seg" fill="none" stroke="#1f2733" stroke-width="2" />

        <!-- 间断点空心圆 -->
        <circle v-if="preset.hole" :cx="mapX(a)" :cy="mapY(L)" r="4.5" fill="#fff" stroke="#e05252" stroke-width="2" />

        <!-- 逼近点 -->
        <line :x1="mapX(px)" :y1="mapY(py)" :x2="mapX(px)" :y2="mapY(0)" stroke="#f2994a" stroke-dasharray="3 3" />
        <line :x1="mapX(px)" :y1="mapY(py)" :x2="mapX(0)" :y2="mapY(py)" stroke="#f2994a" stroke-dasharray="3 3" />
        <circle :cx="mapX(px)" :cy="mapY(py)" r="6" fill="#f2994a" />
        <text :x="mapX(px) + 10" :y="mapY(py) - 8" font-size="11" fill="#b46a15">f({{ fmt(px) }}) = {{ fmt(py) }}</text>
        <circle :cx="mapX(a)" :cy="mapY(0)" r="4" fill="#8b95a3" />
        <text :x="mapX(a)" :y="mapY(0) + 30" text-anchor="middle" font-size="11" fill="#8b95a3">a = {{ a }}</text>
      </svg>

      <div class="lim-panel">
        <div class="def-box">
          <div class="small muted">极限的严格定义（ε-δ）</div>
          <code>∀ε&gt;0, ∃δ&gt;0, 当 0&lt;|x-a|&lt;δ 时，恒有 |f(x)-L|&lt;ε</code>
        </div>
        <el-divider />
        <div class="info-row"><span>当前 ε（误差容限）</span><b style="color:var(--brand)">{{ eps }}</b></div>
        <div class="info-row"><span>找到的 δ（x 的邻域半径）</span><b style="color:var(--success)">{{ fmt(delta) }}</b></div>
        <div class="info-row"><span>检验点 x = a + δ</span><b>{{ fmt(px) }}</b></div>
        <div class="info-row"><span>f(x)</span><b>{{ fmt(py) }}</b></div>
        <div class="info-row">
          <span>|f(x) - L| &lt; ε ?</span>
          <el-tag size="small" :type="ok ? 'success' : 'danger'">{{ ok ? '成立 ✓' : '不成立 ✗' }}</el-tag>
        </div>
        <el-divider />
        <div class="tbl">
          <div class="tbl-head"><span>ε</span><span>δ</span><span>|f(a+δ)-L|</span></div>
          <div
            v-for="(s, i) in player.steps.value" :key="i"
            class="tbl-row" :class="{ active: i === player.idx.value }"
            @click="player.seek(i)"
          >
            <span>{{ s.eps }}</span><span>{{ fmt(s.delta) }}</span><span>{{ fmt(s.diff) }}</span>
          </div>
        </div>
        <p class="small muted tip">规律：ε 缩小 → δ 同步缩小，但无论 ε 多小都能找到 δ，故极限为 L。</p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#1f2733"></i> 函数曲线</span>
      <span><i class="dot" style="background:#3b6ef6"></i> ε 带（允许的误差范围）</span>
      <span><i class="dot" style="background:#22a06b"></i> δ 带（x 的邻域）</span>
      <span><i class="dot" style="background:#f2994a"></i> 检验点</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const PRESETS = [
  {
    key: 'sinc', label: 'f(x)=sin(x)/x，x→0',
    f: x => (x === 0 ? NaN : Math.sin(x) / x),
    a: 0, L: 1, domain: [-6, 6], range: [-0.4, 1.4], hole: true
  },
  {
    key: 'hole', label: 'f(x)=(x²-1)/(x-1)，x→1',
    f: x => (x === 1 ? NaN : (x * x - 1) / (x - 1)),
    a: 1, L: 2, domain: [-2, 4], range: [0, 4.2], hole: true
  },
  {
    key: 'sq', label: 'f(x)=x²，x→2',
    f: x => x * x,
    a: 2, L: 4, domain: [-1, 5], range: [-1, 9], hole: false
  }
]
const presetKey = ref('sinc')
const preset = computed(() => PRESETS.find(p => p.key === presetKey.value) || PRESETS[0])

const W = 560, H = 360, padL = 46, padR = 18, padT = 18, padB = 34
const d0 = computed(() => preset.value.domain[0])
const d1 = computed(() => preset.value.domain[1])
const r0 = computed(() => preset.value.range[0])
const r1 = computed(() => preset.value.range[1])
const a = computed(() => preset.value.a)
const L = computed(() => preset.value.L)

function mapX(x) { return padL + ((x - d0.value) / (d1.value - d0.value)) * (W - padL - padR) }
function mapY(y) { return padT + ((r1.value - y) / (r1.value - r0.value)) * (H - padT - padB) }

const xGrid = computed(() => ticks(d0.value, d1.value))
const yGrid = computed(() => ticks(r0.value, r1.value))
function ticks(lo, hi) {
  const out = []
  const step = (hi - lo) / 8
  for (let i = 0; i <= 8; i++) {
    const v = lo + i * step
    out.push(Math.abs(v) < 1e-9 ? 0 : Number(v.toFixed(2)))
  }
  return out.filter((v, i, arr) => arr.indexOf(v) === i)
}

// 采样曲线（遇到 NaN/∞ 断开成多段）
const curvePaths = computed(() => {
  const paths = []
  let cur = ''
  const n = 500
  for (let i = 0; i <= n; i++) {
    const x = d0.value + ((d1.value - d0.value) * i) / n
    const y = preset.value.f(x)
    if (!isFinite(y) || y < r0.value - 5 || y > r1.value + 5) {
      if (cur) { paths.push(cur); cur = '' }
      continue
    }
    cur += (cur ? 'L' : 'M') + mapX(x).toFixed(2) + ' ' + mapY(y).toFixed(2) + ' '
  }
  if (cur) paths.push(cur)
  return paths
})

// 对于给定 ε，二分求出满足定义的最大 δ
function findDelta(eps) {
  const f = preset.value.f
  const aa = a.value, LL = L.value
  const holds = d => {
    const n = 240
    // 端点必须纳入检查（i 从 0 到 n）：之前漏掉 x = a±δ，
    // 于是求出的 δ 会让边界处偏差超过 ε，界面却仍宣称「恒有 |f(x)-L| < ε」。
    for (let i = 0; i <= n; i++) {
      const x = aa - d + (2 * d * i) / n
      if (Math.abs(x - aa) < 1e-12) continue
      const y = f(x)
      if (!isFinite(y) && preset.value.hole) continue
      if (!isFinite(y)) return false
      if (Math.abs(y - LL) >= eps) return false
    }
    return true
  }
  let lo = 1e-6, hi = (d1.value - d0.value) / 2
  if (!holds(hi)) hi = hi / 2
  for (let k = 0; k < 60; k++) {
    const mid = (lo + hi) / 2
    if (holds(mid)) lo = mid; else hi = mid
  }
  return { delta: lo, ok: holds(lo) }
}

const EPS_LIST = [0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005]

const steps = computed(() => {
  const f = preset.value.f
  return EPS_LIST.map(e => {
    const { delta, ok } = findDelta(e)
    const px = a.value + delta
    const py = f(px)
    const diff = Math.abs(py - L.value)
    const okText = ok
      ? `当 0<|x-${a.value}|<δ 时恒有 |f(x)-${L.value}| < ε（边界实测偏差 ${diff.toFixed(6)} ≤ ε ✓）`
      : `在绘图范围内找不到满足定义的 δ（边界实测偏差 ${diff.toFixed(6)} > ε），需缩小邻域`
    return {
      eps: e, delta, ok, px, py, diff,
      desc: `取 ε = ${e}：求得 δ = ${delta.toFixed(6)}，${okText}`
    }
  })
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const eps = computed(() => cur.value.eps)
const delta = computed(() => cur.value.delta)
const ok = computed(() => cur.value.ok)
const px = computed(() => cur.value.px)
const py = computed(() => cur.value.py)
const statusText = computed(() => cur.value.desc)

function fmt(v) {
  if (v === null || v === undefined || !isFinite(v)) return '-'
  const av = Math.abs(v)
  if (av >= 1000 || (av < 0.0001 && av > 0)) return Number(v).toExponential(2)
  return Number(v.toFixed(4)).toString()
}
</script>

<style scoped>
.lim-wrap { display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap; }
.lim-svg { background: #fcfdff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.grid line { stroke: #eef1f6; stroke-width: 1; }
.lim-panel { flex: 1; min-width: 300px; }
.def-box { margin-bottom: 6px; }
.def-box code { background: #f2f4f8; padding: 8px 10px; border-radius: 6px; display: block; font-size: 12px; line-height: 1.7; }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.tbl { font-size: 12px; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
.tbl-head { display: grid; grid-template-columns: 1fr 1fr 1.2fr; background: #f6f8fb; padding: 7px 10px; font-weight: 600; }
.tbl-row { display: grid; grid-template-columns: 1fr 1fr 1.2fr; padding: 6px 10px; border-top: 1px solid #f0f2f6; cursor: pointer; }
.tbl-row:hover { background: #f6f8fb; }
.tbl-row.active { background: var(--brand-light); color: var(--brand); font-weight: 600; }
.tip { margin-top: 10px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
