<template>
  <VisFrame title="高斯消元法 · 解线性方程组" desc="对增广矩阵做初等行变换化为上三角形再回代：先按列选主元（避免小主元放大误差），再逐行消元，最后由秩判别唯一解 / 无解 / 无穷多解" :player="player" :status-text="statusText" back-to="/knowledge/58">
    <template #extra>
      <el-select v-model="presetKey" size="small" style="width:190px" @change="applyPreset">
        <el-option v-for="p in PRESETS" :key="p.key" :value="p.key" :label="p.label" />
      </el-select>
      <el-input v-model="raw" size="small" style="width:230px" placeholder="每行 a,b,c,d，行间用 ; 分隔" />
      <el-button size="small" @click="applyRaw">应用矩阵</el-button>
    </template>
    <div class="gs-wrap">
      <svg :width="SW" :height="SH" class="gs-svg">
        <text :x="14" :y="18" font-size="12" fill="#8b95a3">增广矩阵 [A | b]{{ cur.pc >= 0 ? `　正在处理第 ${cur.pc + 1} 列` : '' }}</text>
        <!-- 行底色：高亮当前操作行；再叠加主元列底纹与增广矩阵的竖分隔线 -->
        <rect v-for="(r, i) in matrix" :key="'bg' + i" :x="10" :y="my(i) - 16" :width="(N + 1) * CW + 10" :height="32" rx="6"
              :fill="i === cur.pr ? '#e6eeff' : '#f8fafc'" :stroke="i === cur.pr ? '#3b6ef6' : '#e6eaf2'" />
        <!-- 主元列底纹 + 增广矩阵的竖分隔线 -->        <rect v-if="cur.pc >= 0" :x="mx(cur.pc) - CW / 2 + 6" :y="22" :width="CW - 12" height="N * RH" rx="5" fill="#fff4e0" />
        <line :x1="mx(N - 1) + CW / 2" :y1="22" :x2="mx(N - 1) + CW / 2" :y2="24 + N * RH" stroke="#8b95a3" stroke-width="1.5" />
        <g v-for="(rv, i) in matrix" :key="'r' + i">
          <text v-for="(v, j) in rv" :key="i + '-' + j" :x="mx(j)" :y="my(i)" text-anchor="middle" font-size="14"
                :font-weight="i === cur.pr && j === cur.pc ? 700 : 400"
                :fill="j === cur.pc ? '#a5701a' : (v === 0 ? '#b7bfcc' : '#1f2733')">{{ fmt(v) }}</text>
        </g>
        <text v-if="cur.pc >= 0" :x="mx(cur.pc)" :y="30 + N * RH" text-anchor="middle" font-size="11" fill="#a5701a">主元列 ↑</text>
        <text :x="mx(0) - CW / 2 + 2" :y="34 + N * RH + 16" font-size="11" fill="#8b95a3">未知量：x₁　x₂　x₃ ｜ 常数项</text>
      </svg>
      <div class="gs-panel">
        <div class="info-row"><span>当前操作</span><el-tag size="small" :type="phaseType">{{ phaseName }}</el-tag></div>
        <div class="info-row"><span>系数矩阵秩 r(A)</span><b>{{ rankText }}</b></div>
        <div class="info-row"><span>方程组解的类型</span><el-tag size="small" :type="kindType">{{ kindName }}</el-tag></div>
        <div class="panel-title">当前方程形态</div>
        <code v-for="(e, i) in equations" :key="i" class="eq-line">{{ e }}</code>
        <el-divider />
        <div class="panel-title">回代结果</div>
        <div class="sol-row"><span v-for="(v, i) in solution" :key="i" class="sol-item">x{{ i + 1 }} = <b :style="{ color: v === null ? '#8b95a3' : 'var(--brand)' }">{{ v === null ? '待回代' : fmt(v) }}</b></span></div>
        <p v-if="freeText" class="small muted param">{{ freeText }}</p>
        <p class="small muted tip">考点：r(A) = r(A|b) = n 有唯一解；r(A) = r(A|b) < n 有无穷多解（n - r 个自由未知量）；r(A) < r(A|b) 出现 0 = 非零 的矛盾行，方程组无解。</p>
      </div>
    </div>
    <template #legend>
      <span><i class="dot" style="background:#e6eeff;border:1px solid #3b6ef6"></i> 当前操作行</span>
      <span><i class="dot" style="background:#fff4e0;border:1px solid #e8a13a"></i> 当前主元列</span>
      <span><i class="dot" style="background:#1f2733"></i> 参与消元的非零元素</span>
      <span><i class="dot" style="background:#b7bfcc"></i> 已化为 0 的元素</span>
    </template>
  </VisFrame>
</template>
<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'
const N = 3
const PRESETS = [
  { key: 'uniq1', label: '唯一解（教科书例题）', rows: [[2, 1, -1, 8], [-3, -1, 2, -11], [-2, 1, 2, -3]] },
  { key: 'swap', label: '唯一解（需换行选主元）', rows: [[0, 2, 1, 1], [1, -2, -3, -4], [3, -1, 2, 7]] },
  { key: 'none', label: '无解（出现矛盾行）', rows: [[1, 1, 1, 3], [2, 2, 2, 7], [1, -1, 1, 1]] },
  { key: 'inf', label: '无穷多解（1 个自由未知量）', rows: [[1, 1, 1, 3], [2, 2, 2, 6], [1, -1, 2, 2]] }
]
const presetKey = ref('uniq1')
const rows = ref(PRESETS[0].rows.map(r => [...r]))
const raw = ref(PRESETS[0].rows.map(r => r.join(',')).join(';'))
function applyPreset() {
  const p = PRESETS.find(x => x.key === presetKey.value) || PRESETS[0]
  rows.value = p.rows.map(r => [...r])
  raw.value = p.rows.map(r => r.join(',')).join(';')
  player.reset()
}
// 解析用户输入：非法输入自动兜底（保持上一组有效数据不变）
function applyRaw() {
  const parsed = []
  for (const part of String(raw.value || '').split(';')) {
    const vals = part.split(/[,，\s]+/).map(v => Number(v.trim())).filter(v => !isNaN(v))
    if (vals.length !== N + 1) return
    parsed.push(vals)
  }
  if (parsed.length !== N) return
  rows.value = parsed
  presetKey.value = ''
  player.reset()
}
const SW = 340, SH = 210, CW = 74, RH = 44
const EPS = 1e-9
function mx(j) { return 20 + CW * (j + 0.5) }
function my(i) { return 46 + RH * i }
function cleanRow(r) { for (let j = 0; j < r.length; j++) if (Math.abs(r[j]) < EPS) r[j] = 0 }

const steps = computed(() => {
  const out = []
  const m = rows.value.map(r => r.slice())
  const x = [null, null, null]
  const snap = (desc, extra = {}) => out.push({ m: m.map(r => r.slice()), x: x.slice(), desc, pr: -1, pc: -1, phase: 'elim', ...extra })
  const idxOf = (i, j) => `a${i + 1}${j + 1}`
  snap('初始增广矩阵 [A|b]，目标是通过初等行变换化为上三角形', { phase: 'init' })
  const pivots = []
  let rowTop = 0
  for (let col = 0; col < N && rowTop < N; col++) {
    let sel = rowTop
    for (let i = rowTop + 1; i < N; i++) if (Math.abs(m[i][col]) > Math.abs(m[sel][col])) sel = i
    if (Math.abs(m[sel][col]) < EPS) continue
    if (sel !== rowTop) {
      const t = m[sel]; m[sel] = m[rowTop]; m[rowTop] = t
      snap(`按列选主元：第 ${col + 1} 列中 |${idxOf(sel, col)}| 最大，交换 r${rowTop + 1} ↔ r${sel + 1}（防止小主元放大舍入误差）`, { pr: rowTop, pc: col, phase: 'swap' })
    }
    snap(`确定第 ${col + 1} 个主元 ${idxOf(rowTop, col)} = ${fmt(m[rowTop][col])}`, { pr: rowTop, pc: col, phase: 'pivot' })
    for (let i = rowTop + 1; i < N; i++) {
      const factor = m[i][col] / m[rowTop][col]
      if (Math.abs(factor) < EPS) continue
      for (let j = col; j <= N; j++) m[i][j] -= factor * m[rowTop][j]
      cleanRow(m[i])
      snap(`消元 r${i + 1} ← r${i + 1} - (${fmt(factor)})·r${rowTop + 1}，把第 ${col + 1} 列主元下方元素化为 0`, { pr: i, pc: col, phase: 'elim' })
    }
    pivots.push(col)
    rowTop++
  }
  // 秩与解的类型判定：出现「0 = 非零」的矛盾行即无解
  let conflictRow = -1
  for (let i = 0; i < N; i++) {
    if (m[i].slice(0, N).every(v => Math.abs(v) < EPS) && Math.abs(m[i][N]) > EPS) conflictRow = i
  }
  const kind = conflictRow >= 0 ? 'none' : (pivots.length === N ? 'unique' : 'infinite')
  snap(conflictRow >= 0
    ? `阶梯形中出现矛盾行 "0 = ${fmt(m[conflictRow][N])}"，故 r(A) < r(A|b)，方程组无解`
    : `已化为上三角形，非零行数 r(A) = ${pivots.length}${pivots.length === N ? ' = n，可回代求唯一解' : ' < n，存在自由未知量'}`,
    { phase: 'rank', kind, rankA: pivots.length })
  let freeCols = [], exprs = []
  if (kind === 'unique') {
    for (let i = N - 1; i >= 0; i--) {
      let s = m[i][N]
      const parts = []
      for (let j = i + 1; j < N; j++) { s -= m[i][j] * x[j]; if (Math.abs(m[i][j]) > EPS) parts.push(`${fmt(m[i][j])}·${fmt(x[j])}`) }
      x[i] = s / m[i][i]
      snap(`回代 x${i + 1} = (${fmt(m[i][N])} - ${parts.join(' - ') || 0}) / ${fmt(m[i][i])} = ${fmt(x[i])}`, { pr: i, pc: i, phase: 'back' })
    }
    snap(`唯一解：x₁ = ${fmt(x[0])}，x₂ = ${fmt(x[1])}，x₃ = ${fmt(x[2])}（可代回原方程验证）`, { phase: 'done', kind })
  } else if (kind === 'infinite') {
    for (let j = 0; j < N; j++) if (pivots.indexOf(j) === -1) freeCols.push(j)
    // 每个变量记成「常数项 + 各自由未知量的系数」的线性表达式
    const exprOf = {}
    for (const fc of freeCols) exprOf[fc] = { c0: 0, co: { [fc]: 1 } }   // 自由未知量自身就是参数 t
    // 必须从最后一个主元行倒着回代：靠后的基本变量要先表达出来，才能代入靠前的行。
    // 直接按主元行顺序算等价于把上三角当成对角阵，会漏掉其它基本变量的贡献
    for (let r = pivots.length - 1; r >= 0; r--) {
      const pc = pivots[r]
      const e = { c0: m[r][N] / m[r][pc], co: {} }
      for (let j = 0; j < N; j++) {
        if (j === pc || Math.abs(m[r][j]) < EPS) continue
        const ej = exprOf[j]
        if (!ej) continue
        const k = m[r][j] / m[r][pc]
        e.c0 -= k * ej.c0
        for (const fc of freeCols) e.co[fc] = (e.co[fc] || 0) - k * (ej.co[fc] || 0)
      }
      exprOf[pc] = e
      exprs.push({ pc, c0: e.c0, co: { ...e.co } })
    }
    exprs.sort((a, b) => a.pc - b.pc)   // 按未知量顺序展示通解
    snap(`无穷多解：令自由未知量 ${freeCols.map(c => 'x' + (c + 1)).join('、')} 任取参数，其余变量由主元行回代确定`, { phase: 'done', kind, freeCols, exprs })
  } else {
    snap('结论：方程组无解（矛盾方程）', { phase: 'done', kind })
  }
  return out
})
const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const verdict = computed(() => steps.value[steps.value.length - 1] || steps.value[0])
const matrix = computed(() => cur.value.m)
const PHASE = { init: '初始化', swap: '换行（列主元）', pivot: '选主元', elim: '消元', rank: '秩判别', back: '回代', done: '完成' }
const phaseName = computed(() => PHASE[cur.value.phase] || '进行中')
const phaseType = computed(() => ({ swap: 'warning', rank: 'warning', back: 'success', done: 'success' }[cur.value.phase] || 'primary'))
const kindName = computed(() => ({ unique: '唯一解', infinite: '无穷多解', none: '无解' }[verdict.value.kind] || '待判定'))
const kindType = computed(() => ({ unique: 'success', infinite: 'warning', none: 'danger' }[verdict.value.kind] || 'info'))
const solution = computed(() => cur.value.x)
const rankText = computed(() => (verdict.value.kind === 'none'
  ? `${verdict.value.rankA ?? '-'} < ${(verdict.value.rankA ?? 0) + 1} = r(A|b)`
  : `${verdict.value.rankA ?? '-'}（未知量个数 n = ${N}）`))
const freeText = computed(() => {
  const v = verdict.value
  if (!v.exprs || !v.exprs.length) return ''
  const head = '令 ' + v.freeCols.map(fc => 'x' + (fc + 1)).join(' = ') + ' = t'
  return `通解（${head}）：` + v.exprs.map(e => {
    let s = `x${e.pc + 1} = ${fmt(e.c0)}`
    for (const fc of v.freeCols) {
      if (Math.abs(e.co[fc]) < EPS) continue
      s += (e.co[fc] < 0 ? ' - ' : ' + ') + fmt(Math.abs(e.co[fc])) + 't'
    }
    return s
  }).join('；')
})
// 把矩阵行渲染成方程字符串
const equations = computed(() => matrix.value.map(rv => {
  let s = ''
  for (let j = 0; j < N; j++) {
    const v = rv[j]
    if (Math.abs(v) < EPS) continue
    s += (v < 0 ? ' - ' : (s === '' ? '' : ' + ')) + (Math.abs(v) === 1 ? '' : fmt(Math.abs(v))) + `x${j + 1}`
  }
  return s === '' ? `0 = ${fmt(rv[N])}` : `${s} = ${fmt(rv[N])}`
}))
function fmt(v) { return (v === null || v === undefined || !isFinite(v)) ? '-' : Number((Math.round(v * 1000) / 1000).toString()).toString() }
</script>

<style scoped>
.gs-wrap { display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap; }
.gs-svg { background: #fcfdff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.gs-panel { flex: 1; min-width: 300px; }
.info-row { display: flex; justify-content: space-between; align-items: center; gap: 10px; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.panel-title { font-size: 13px; font-weight: 600; margin-bottom: 6px; color: var(--text-2); }
.eq-line { display: block; background: #f6f8fb; border-radius: 6px; padding: 6px 10px; margin-bottom: 5px; font-size: 13px; }
.sol-row { display: flex; gap: 14px; flex-wrap: wrap; font-size: 13px; }
.sol-item { background: #f6f8fb; border-radius: 6px; padding: 4px 10px; }
.param { background: #fff8ec; border-radius: 6px; padding: 6px 10px; margin-top: 8px; }
.tip { margin-top: 10px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
