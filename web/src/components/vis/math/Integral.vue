<template>
  <VisFrame title="定积分 · 黎曼和的逼近" desc="分割 → 近似 → 求和 → 取极限：当分割越来越细，矩形面积之和趋近曲边梯形的真实面积" :player="player" :status-text="statusText" back-to="/knowledge/24">
    <template #extra>
      <el-select v-model="fnKey" size="small" style="width:170px" @change="player.reset()">
        <el-option v-for="f in FNS" :key="f.key" :value="f.key" :label="f.label" />
      </el-select>
      <el-select v-model="method" size="small" style="width:120px" @change="player.reset()">
        <el-option value="left" label="左矩形" />
        <el-option value="mid" label="中矩形" />
        <el-option value="right" label="右矩形" />
        <el-option value="trap" label="梯形" />
      </el-select>
    </template>

    <div class="ig-wrap">
      <svg :width="W" :height="H" class="ig-svg">
        <!-- 真实面积（浅色） -->
        <path :d="areaPath" fill="#22a06b" fill-opacity="0.14" />
        <!-- 黎曼矩形 -->
        <g>
          <template v-if="method === 'trap'">
            <path
              v-for="(p, i) in shapes" :key="'s'+i" :d="p"
              fill="#3b6ef6" fill-opacity="0.35" stroke="#3b6ef6" stroke-width="1.5"
            />
          </template>
          <rect
            v-else v-for="(r, i) in shapes" :key="'r'+i"
            :x="r.x" :y="r.y" :width="r.w" :height="r.h"
            fill="#3b6ef6" fill-opacity="0.35" stroke="#3b6ef6" stroke-width="1.5"
          />
        </g>
        <!-- 曲线 -->
        <path :d="curvePath" fill="none" stroke="#e05252" stroke-width="2.5" />
        <!-- 坐标轴 -->
        <line :x1="mapX(a0)" :y1="mapY(0)" :x2="mapX(a1)" :y2="mapY(0)" stroke="#8b95a3" stroke-width="1.5" />
        <line :x1="mapX(a0)" :y1="mapY(yLo)" :x2="mapX(a0)" :y2="mapY(yHi)" stroke="#8b95a3" stroke-width="1.5" />
        <text v-for="(t, i) in xTicks" :key="'tx'+i" :x="mapX(t)" :y="mapY(0) + 16" text-anchor="middle" font-size="10" fill="#8b95a3">{{ t }}</text>
        <text :x="mapX(a0) - 6" :y="mapY(0)" text-anchor="end" font-size="10" fill="#8b95a3">0</text>
        <text :x="12" :y="20" font-size="12" fill="#8b95a3">n = {{ cur.n }} 个小区间，Δx = {{ fmt(dx) }}</text>
      </svg>

      <div class="ig-panel">
        <div class="formula"><code>{{ integralText }}</code></div>
        <el-divider />
        <div class="info-row"><span>分割份数 n</span><b style="color:var(--brand)">{{ cur.n }}</b></div>
        <div class="info-row"><span>小区间宽度 Δx</span><b>{{ fmt(dx) }}</b></div>
        <div class="info-row"><span>黎曼和（近似值）</span><b style="color:#b46a15">{{ fmt(cur.sum) }}</b></div>
        <div class="info-row"><span>精确积分值</span><b style="color:var(--success)">{{ fmt(exact) }}</b></div>
        <div class="info-row">
          <span>绝对误差</span>
          <el-tag size="small" :type="Math.abs(cur.sum - exact) < 0.005 ? 'success' : 'warning'">{{ fmt(Math.abs(cur.sum - exact)) }}</el-tag>
        </div>
        <el-divider />
        <div class="tbl">
          <div class="tbl-head"><span>n</span><span>黎曼和</span><span>误差</span></div>
          <div v-for="(s, i) in player.steps.value" :key="i" class="tbl-row" :class="{ active: i === player.idx.value }" @click="player.seek(i)">
            <span>{{ s.n }}</span><span>{{ fmt(s.sum) }}</span><span>{{ fmt(Math.abs(s.sum - exact)) }}</span>
          </div>
        </div>
        <p class="small muted tip">n 每翻一倍，误差大约缩小到原来的 1/2（矩形法）或 1/4（梯形法）——这就是「取极限」的直观含义。</p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#22a06b"></i> 真实面积（精确积分）</span>
      <span><i class="dot" style="background:#3b6ef6"></i> 黎曼和（近似）</span>
      <span><i class="dot" style="background:#e05252"></i> 被积函数 f(x)</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const FNS = [
  { key: 'sq', label: 'f(x) = x²，[0,2]', f: x => x * x, a0: 0, a1: 2, exact: 8 / 3, tex: '∫₀² x² dx = 8/3 ≈ 2.6667' },
  { key: 'sin', label: 'f(x) = sin x，[0,π]', f: x => Math.sin(x), a0: 0, a1: Math.PI, exact: 2, tex: '∫₀^π sin x dx = 2' },
  { key: 'exp', label: 'f(x) = e^x，[0,1]', f: x => Math.exp(x), a0: 0, a1: 1, exact: Math.E - 1, tex: '∫₀¹ e^x dx = e - 1 ≈ 1.7183' },
  { key: 'lin', label: 'f(x) = 2x+1，[0,3]', f: x => 2 * x + 1, a0: 0, a1: 3, exact: 12, tex: '∫₀³ (2x+1) dx = 12' }
]
const fnKey = ref('sin')
const method = ref('mid')
const fn = computed(() => FNS.find(f => f.key === fnKey.value) || FNS[0])
const a0 = computed(() => fn.value.a0)
const a1 = computed(() => fn.value.a1)
const exact = computed(() => fn.value.exact)
const integralText = computed(() => fn.value.tex)

const W = 560, H = 320, padL = 44, padR = 16, padT = 30, padB = 34
const yLo = -0.3
const yHi = computed(() => {
  let mx = 0
  for (let i = 0; i <= 100; i++) mx = Math.max(mx, fn.value.f(a0.value + ((a1.value - a0.value) * i) / 100))
  return mx * 1.2
})
function mapX(x) { return padL + ((x - a0.value) / (a1.value - a0.value)) * (W - padL - padR) }
function mapY(y) { return padT + ((yHi.value - y) / (yHi.value - yLo)) * (H - padT - padB) }

const xTicks = computed(() => {
  const out = []
  for (let i = 0; i <= 6; i++) out.push(Number((a0.value + ((a1.value - a0.value) * i) / 6).toFixed(2)))
  return out
})

const curvePath = computed(() => {
  let d = ''
  const N = 200
  for (let i = 0; i <= N; i++) {
    const x = a0.value + ((a1.value - a0.value) * i) / N
    d += (i === 0 ? 'M' : 'L') + mapX(x).toFixed(2) + ' ' + mapY(fn.value.f(x)).toFixed(2) + ' '
  }
  return d
})
const areaPath = computed(() => {
  let d = `M ${mapX(a0.value).toFixed(2)} ${mapY(0).toFixed(2)} `
  const N = 200
  for (let i = 0; i <= N; i++) {
    const x = a0.value + ((a1.value - a0.value) * i) / N
    d += 'L' + mapX(x).toFixed(2) + ' ' + mapY(fn.value.f(x)).toFixed(2) + ' '
  }
  return d + `L ${mapX(a1.value).toFixed(2)} ${mapY(0).toFixed(2)} Z`
})

const N_LIST = [2, 4, 8, 16, 32, 64]
const steps = computed(() => {
  const f = fn.value.f
  return N_LIST.map(n => {
    const dx = (a1.value - a0.value) / n
    let sum = 0
    for (let i = 0; i < n; i++) {
      const xl = a0.value + i * dx
      const xr = xl + dx
      if (method.value === 'left') sum += f(xl) * dx
      else if (method.value === 'right') sum += f(xr) * dx
      else if (method.value === 'mid') sum += f((xl + xr) / 2) * dx
      else sum += ((f(xl) + f(xr)) / 2) * dx
    }
    const nameMap = { left: '左矩形', mid: '中矩形', right: '右矩形', trap: '梯形' }
    return {
      n, sum,
      desc: `${nameMap[method.value]}法，n = ${n}：Δx = ${dx.toFixed(5)}，黎曼和 = ${sum.toFixed(6)}，与精确值 ${exact.value.toFixed(6)} 相差 ${Math.abs(sum - exact.value).toFixed(6)}`
    }
  })
})
const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const dx = computed(() => (a1.value - a0.value) / cur.value.n)

const shapes = computed(() => {
  const f = fn.value.f
  const n = cur.value.n
  const w = (a1.value - a0.value) / n
  const out = []
  for (let i = 0; i < n; i++) {
    const xl = a0.value + i * w
    const xr = xl + w
    const px1 = mapX(xl), px2 = mapX(xr)
    if (method.value === 'trap') {
      const d = `M ${px1.toFixed(2)} ${mapY(0).toFixed(2)} L ${px1.toFixed(2)} ${mapY(f(xl)).toFixed(2)} L ${px2.toFixed(2)} ${mapY(f(xr)).toFixed(2)} L ${px2.toFixed(2)} ${mapY(0).toFixed(2)} Z`
      out.push(d)
    } else {
      let h
      if (method.value === 'left') h = f(xl)
      else if (method.value === 'right') h = f(xr)
      else h = f((xl + xr) / 2)
      const yTop = mapY(h)
      const yBase = mapY(0)
      out.push({
        x: px1, y: Math.min(yTop, yBase),
        w: Math.max(1, px2 - px1 - 1), h: Math.abs(yBase - yTop)
      })
    }
  }
  return out
})

function fmt(v) { return isFinite(v) ? Number(v).toFixed(5).toString() : '-' }
</script>

<style scoped>
.ig-wrap { display: flex; gap: 18px; align-items: flex-start; flex-wrap: wrap; }
.ig-svg { background: #fcfdff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.ig-panel { flex: 1; min-width: 300px; }
.formula code { background: #f2f4f8; padding: 8px 10px; border-radius: 6px; display: block; font-size: 12px; line-height: 1.7; }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.tbl { font-size: 12px; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
.tbl-head { display: grid; grid-template-columns: 0.7fr 1.3fr 1fr; background: #f6f8fb; padding: 7px 10px; font-weight: 600; }
.tbl-row { display: grid; grid-template-columns: 0.7fr 1.3fr 1fr; padding: 6px 10px; border-top: 1px solid #f0f2f6; cursor: pointer; }
.tbl-row:hover { background: #f6f8fb; }
.tbl-row.active { background: var(--brand-light); color: var(--brand); font-weight: 600; }
.tip { margin-top: 10px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
