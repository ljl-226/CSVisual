<template>
  <VisFrame title="行列式的几何意义 · 有向面积与有向体积" desc="二阶行列式 = 两列向量张成的平行四边形的有向面积；三阶行列式 = 三列向量张成的平行六面体的有向体积，det 的符号反映定向是否被翻转" :player="player" :status-text="statusText" back-to="/knowledge/59">
    <template #extra>
      <el-radio-group v-model="mode" size="small" @change="applyPreset">
        <el-radio-button value="2d">二阶（面积）</el-radio-button>
        <el-radio-button value="3d">三阶（体积）</el-radio-button>
      </el-radio-group>
      <el-select v-model="presetKey" size="small" style="width:170px" @change="applyPreset">
        <el-option v-for="p in presets" :key="p.key" :value="p.key" :label="p.label" />
      </el-select>
    </template>
    <div class="dt-wrap">
      <svg :width="W" :height="H" class="dt-svg">
        <defs><clipPath id="dtClip"><rect x="0" y="0" :width="W" :height="H" /></clipPath></defs>
        <g clip-path="url(#dtClip)">
        <!-- 单位正方形 / 单位立方体：面积、体积均为 1，作为对照 -->
        <polygon v-if="n === 2" :points="unitPoly" fill="none" stroke="#8b95a3" stroke-dasharray="5 4" stroke-width="1.5" />
        <g v-else>
          <polygon v-for="(f, i) in unitFaces" :key="'uf' + i" :points="f" fill="none" stroke="#8b95a3" stroke-dasharray="5 4" stroke-width="1.2" />
        </g>
        <!-- 2D：列向量 a、b 张成的平行四边形（有向面积） -->
        <template v-if="n === 2">
          <polygon :points="paraPoints" :fill="fillColor" fill-opacity="0.35" :stroke="lineColor" stroke-width="2.5" />
          <line v-for="(c, i) in cols2d" :key="'v' + i" :x1="ox" :y1="oy" :x2="c.px" :y2="c.py" :stroke="i === 0 ? '#3b6ef6' : '#22a06b'" stroke-width="2.5" />
          <text :x="cols2d[0].px + 6" :y="cols2d[0].py - 4" font-size="11" fill="#2a55c4">a = ({{ fmt(cols[0][0]) }}, {{ fmt(cols[0][1]) }})</text>
          <text :x="cols2d[1].px + 6" :y="cols2d[1].py - 4" font-size="11" fill="#14764e">b = ({{ fmt(cols[1][0]) }}, {{ fmt(cols[1][1]) }})</text>
        </template>
        <!-- 3D：6 个面 + 12 条棱（平行六面体经轴测投影画出） -->
        <template v-else>
          <polygon v-for="(f, i) in faces" :key="'f' + i" :points="f.pts" :fill="fillColor" fill-opacity="0.28" :stroke="lineColor" stroke-width="1.8" />
          <line v-for="(e, i) in edges" :key="'e' + i" :x1="e.x1" :y1="e.y1" :x2="e.x2" :y2="e.y2" :stroke="lineColor" stroke-width="2.2" />
          <line v-for="(c, i) in cols3d" :key="'v3' + i" :x1="ox2" :y1="oy2" :x2="c.px" :y2="c.py" :stroke="['#3b6ef6', '#22a06b', '#e8a13a'][i]" stroke-width="2.8" />
        </template>
        <circle :cx="n === 2 ? ox : ox2" :cy="n === 2 ? oy : oy2" r="4.5" fill="#1f2733" />
        <text :x="12" :y="18" font-size="12" fill="#8b95a3">t = {{ cur.t.toFixed(2) }}：从单位阵连续变形到目标矩阵（面积 / 体积 = |det|）</text>
        </g>
      </svg>
      <div class="dt-panel">
        <div class="def-box"><div class="small muted">教材公式（同济《线性代数》行列式）</div><code v-if="n === 2">|a₁ a₂; b₁ b₂| = a₁b₂ - a₂b₁ = |a||b|sinθ（有向面积）</code><code v-else>det(A) = u · (v × w)（混合积 = 有向体积）</code></div>
        <el-divider />
        <div class="info-row"><span>当前列向量</span><b class="vec">{{ colText }}</b></div>
        <div class="info-row"><span>行列式 det(A) / 定向</span><b><span :style="{ color: detColor }">{{ fmt(cur.det) }}</span> · {{ signText }}</b></div>
        <div class="info-row"><span>{{ n === 2 ? '平行四边形面积 |det|' : '平行六面体体积 |det|' }}</span><el-tag size="small" type="primary">{{ fmt(Math.abs(cur.det)) }}</el-tag></div>
        <div class="info-row"><span>目标矩阵行列式 / 是否奇异</span><b :style="{ color: Math.abs(cur.det) < 1e-6 ? '#c02b2b' : 'var(--success)' }">{{ fmt(targetDet) }} · {{ Math.abs(cur.det) < 1e-6 ? '奇异（列向量线性相关，图形降维）' : '非奇异' }}</b></div>
        <p class="small muted tip">考点：|AB| = |A|·|B|，|Aᵀ| = |A|，交换两行（列）行列式变号；det = 0 ⟺ 列向量线性相关 ⟺ 方阵不可逆。2D 中 det < 0 表示从 a 到 b 的有向翻转。</p>
      </div>
    </div>
    <template #legend>
      <span><i class="dot" :style="{ background: lineColor }"></i> {{ n === 2 ? '列向量张成的平行四边形' : '列向量张成的平行六面体' }}</span>
      <span><i class="dot" style="background:#8b95a3"></i> {{ n === 2 ? '单位正方形（面积 1）' : '单位立方体（体积 1）' }}</span>
      <span><i class="dot" style="background:#3b6ef6"></i> 第 1 列向量</span>
      <span><i class="dot" style="background:#22a06b"></i> 第 2 列向量</span>
      <span v-if="n === 3"><i class="dot" style="background:#e8a13a"></i> 第 3 列向量</span>
    </template>
  </VisFrame>
</template>
<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'
const P2 = [
  { key: 'scale2', label: '面积放大：[[2,0],[0,1.5]]', rows: [[2, 0], [0, 1.5]] },
  { key: 'shear2', label: '剪切：[[1,1],[0,1]]（面积不变）', rows: [[1, 1], [0, 1]] },
  { key: 'flip2', label: '符号翻转：[[1,0.5],[1.5,-1]]', rows: [[1, 0.5], [1.5, -1]] },
  { key: 'sing2', label: '奇异：[[1,2],[2,4]]（det = 0）', rows: [[1, 2], [2, 4]] }
]
const P3 = [
  { key: 'scale3', label: '体积放大：diag(2, 1.5, 1)', rows: [[2, 0, 0], [0, 1.5, 0], [0, 0, 1]] },
  { key: 'flip3', label: '定向翻转：diag(1, 1, -1)', rows: [[1, 0, 0], [0, 1, 0], [0, 0, -1]] },
  { key: 'shear3', label: '错切：a₃₁ = 1（体积不变）', rows: [[1, 0, 0], [0, 1, 0], [1, 0, 1]] },
  { key: 'sing3', label: '奇异：r₃ = r₁ + r₂（det = 0）', rows: [[1, 2, 3], [0, 1, 1], [1, 3, 4]] }
]
const mode = ref('2d')
const presetKey = ref('shear2')
const rows = ref([[1, 1], [0, 1]])
const presets = computed(() => (mode.value === '2d' ? P2 : P3))
function applyPreset() {
  const p = presets.value.find(x => x.key === presetKey.value) || presets.value[0]
  rows.value = p.rows.map(r => [...r])
  presetKey.value = p.key
  player.reset()
}
const n = computed(() => rows.value.length)
const W = 520, H = 400
// 2D 平面映射（原点在左下方）：单位长度换算成 U 像素
const ox = 150, oy = 320
const U = computed(() => {
  let m = 2
  rows.value.forEach(r => r.forEach(v => { m = Math.max(m, Math.abs(v)) }))
  return Math.min((W - 120) / (m * 1.6), (H - 120) / (m * 1.6), 120)
})
function eMapX(x) { return ox + x * U.value }
function eMapY(y) { return oy - y * U.value }
// 3D 斜二测投影：x 向右下、z 向左下、y 竖直向上
const ox2 = 250, oy2 = 300
function proj(v) {
  const s = U.value * 0.78
  return { x: ox2 + (v[0] - v[2]) * s * 0.9, y: oy2 - (v[1] * s + (v[0] + v[2]) * s * 0.42) }
}
function colsOf(M) {
  const out = []
  for (let c = 0; c < M.length; c++) { const v = []; for (let r = 0; r < M.length; r++) v.push(M[r][c]); out.push(v) }
  return out
}
// 二阶：有向面积的叉积形式；三阶：混合积 u·(v×w)
function detOf(cs) {
  if (cs.length === 2) return cs[0][0] * cs[1][1] - cs[0][1] * cs[1][0]
  const [u, v, w] = cs
  return u[0] * (v[1] * w[2] - v[2] * w[1]) - u[1] * (v[0] * w[2] - v[2] * w[0]) + u[2] * (v[0] * w[1] - v[1] * w[0])
}
const targetDet = computed(() => detOf(colsOf(rows.value)))

const NSTEP = 24
const steps = computed(() => {
  const nn = rows.value.length, T = rows.value
  const out = []
  let prevSign = 1
  for (let k = 0; k <= NSTEP; k++) {
    const t = k / NSTEP
    // 从单位阵连续变形到目标矩阵：M(t) = I + t(A - I)，逐列取出列向量
    const cs = T.map((_, c) => T.map((row, r) => (r === c ? 1 : 0) + t * (row[c] - (r === c ? 1 : 0))))
    const d = detOf(cs)
    const sgn = d > 1e-6 ? 1 : d < -1e-6 ? -1 : 0
    const flip = k > 0 && prevSign !== 0 && sgn !== 0 && sgn !== prevSign
    if (sgn !== 0) prevSign = sgn
    out.push({
      k, t, cols: cs, det: d,
      desc: `变形 ${(t * 100).toFixed(0)}%：det = ${d.toFixed(3)}${flip ? ' ← 符号在此翻转（穿过退化状态 det = 0，图形被压扁成一条线/一个面）' : ''}，${nn === 2 ? '平行四边形面积' : '平行六面体体积'} = ${Math.abs(d).toFixed(3)}`
    })
  }
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const cols = computed(() => cur.value.cols)
const det = computed(() => cur.value.det)
const detColor = computed(() => (det.value > 1e-6 ? '#22a06b' : det.value < -1e-6 ? '#e05252' : '#e8a13a'))
const lineColor = computed(() => (det.value < -1e-6 ? '#e05252' : Math.abs(det.value) < 1e-6 ? '#e8a13a' : '#3b6ef6'))
const fillColor = computed(() => (det.value < -1e-6 ? '#f7c9c9' : Math.abs(det.value) < 1e-6 ? '#fbe6c4' : '#cfe0ff'))
const signText = computed(() => (det.value > 1e-6 ? '正向（右手系，+）' : det.value < -1e-6 ? '反向（定向被翻转，-）' : '退化（0）'))
const colText = computed(() => cols.value.map(v => '(' + v.map(x => fmt(x)).join(', ') + ')').join(' '))
const poly = pts => pts.map(p => eMapX(p[0]).toFixed(1) + ',' + eMapY(p[1]).toFixed(1)).join(' ')
const cols2d = computed(() => cols.value.map(v => ({ px: eMapX(v[0]), py: eMapY(v[1]) })))
const paraPoints = computed(() => poly([[0, 0], cols.value[0], [cols.value[0][0] + cols.value[1][0], cols.value[0][1] + cols.value[1][1]], cols.value[1]]))
const unitPoly = computed(() => poly([[0, 0], [1, 0], [1, 1], [0, 1]]))
// 3D：8 个顶点即三个列向量的全部子集和；再按投影坐标拼出面、棱
const verts3 = computed(() => {
  const cs = cols.value, out = []
  for (let mask = 0; mask < 8; mask++) {
    const v = [0, 0, 0]
    for (let b = 0; b < 3; b++) if (mask & (1 << b)) for (let r = 0; r < 3; r++) v[r] += cs[b][r]
    out.push({ v, p: proj(v) })
  }
  return out
})
const cols3d = computed(() => cols.value.map(v => proj(v)))
// 12 条棱：仅当两顶点之差恰好等于某一列向量时相连
const edges = computed(() => {
  const vs = verts3.value, cs = cols.value, out = []
  for (let i = 0; i < 8; i++) {
    for (let j = i + 1; j < 8; j++) {
      for (const c of cs) {
        if ([0, 1, 2].every(r => Math.abs(c[r] - (vs[i].v[r] - vs[j].v[r])) < 1e-9)) { out.push({ x1: vs[i].p.x, y1: vs[i].p.y, x2: vs[j].p.x, y2: vs[j].p.y }); break }
      }
    }
  }
  return out
})
// 6 个面：每对基向量张成的平行四边形（含平移后的对面）
const faces = computed(() => {
  const vs = verts3.value
  const quad = (a, b, c, d) => [a, b, c, d].map(m => vs[m].p.x.toFixed(1) + ',' + vs[m].p.y.toFixed(1)).join(' ')
  return [
    quad(0, 1, 3, 2), quad(4, 5, 7, 6), quad(0, 1, 5, 4), quad(2, 3, 7, 6), quad(0, 2, 6, 4), quad(1, 3, 7, 5)
  ].map(pts => ({ pts }))
})
const unitFaces = computed(() => {
  const quad = vs => vs.map(v => proj(v)).map(p => p.x.toFixed(1) + ',' + p.y.toFixed(1)).join(' ')
  return [
    quad([[0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1]]), quad([[0, 1, 0], [1, 1, 0], [1, 1, 1], [0, 1, 1]]),
    quad([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]), quad([[0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]])
  ]
})
function fmt(v) { return (v === null || v === undefined || !isFinite(v)) ? '-' : Number(v.toFixed(3)).toString() }
</script>

<style scoped>
.dt-wrap { display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap; }
.dt-svg { background: #fcfdff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.dt-panel { flex: 1; min-width: 300px; }
.def-box code { background: #f2f4f8; padding: 8px 10px; border-radius: 6px; display: block; font-size: 12px; line-height: 1.7; }
.info-row { display: flex; justify-content: space-between; align-items: center; gap: 10px; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.info-row .vec { font-size: 12px; color: var(--text-2); }
.tip { margin-top: 10px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
