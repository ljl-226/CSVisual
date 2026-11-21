<template>
  <VisFrame title="特征值与特征向量 · 几何意义" desc="满足 A·v = λ·v 的方向：向量经变换后只被拉伸 λ 倍、方向不变。幂迭代会自然收敛到主特征向量" :player="player" :status-text="statusText" back-to="/knowledge/26">
    <template #extra>
      <el-select v-model="presetKey" size="small" style="width:200px" @change="applyPreset">
        <el-option v-for="p in PRESETS" :key="p.key" :value="p.key" :label="p.label" />
      </el-select>
    </template>

    <div class="ev-wrap">
      <svg :width="W" :height="H" class="ev-svg">
        <defs><clipPath id="evClip"><rect :x="0" :y="0" :width="W" :height="H" /></clipPath></defs>
        <g clip-path="url(#evClip)">
          <!-- 单位圆 -->
          <circle :cx="O.x" :cy="O.y" :r="U" fill="none" stroke="#c8d3e6" stroke-dasharray="4 4" />
          <text :x="O.x + U + 4" :y="O.y - 6" font-size="11" fill="#8b95a3">单位圆 |v|=1</text>

          <!-- 单位圆经 A 变换后的椭圆 -->
          <path :d="ellipsePath" fill="#7b61ff" fill-opacity="0.12" stroke="#7b61ff" stroke-width="2" />

          <!-- 特征方向 -->
          <template v-if="hasReal">
            <line
              v-for="(ev, i) in eigenLines" :key="'el'+i"
              :x1="ev.x1" :y1="ev.y1" :x2="ev.x2" :y2="ev.y2"
              :stroke="i === 0 ? '#e05252' : '#22a06b'" stroke-width="2.5" stroke-dasharray="7 4"
            />
            <text
              v-for="(ev, i) in eigenLines" :key="'et'+i"
              :x="ev.tx" :y="ev.ty" font-size="11" font-weight="700"
              :fill="i === 0 ? '#e05252' : '#22a06b'"
            >λ{{ i + 1 }} = {{ fmt(ev.lambda) }}</text>
          </template>

          <!-- 迭代向量 -->
          <line :x1="O.x" :y1="O.y" :x2="O.x + vec.x * U * scaleShow" :y2="O.y - vec.y * U * scaleShow"
                stroke="#f2994a" stroke-width="3" />
          <circle :cx="O.x + vec.x * U * scaleShow" :cy="O.y - vec.y * U * scaleShow" r="6" fill="#f2994a" />
          <!-- 历史轨迹 -->
          <polyline :points="trailPoints" fill="none" stroke="#f2994a" stroke-opacity="0.35" stroke-width="1.5" />
        </g>
        <text :x="12" :y="20" font-size="12" fill="#8b95a3">幂迭代第 {{ cur.k }} 步（单位圆上的点经 A 拉伸成椭圆）</text>
      </svg>

      <div class="ev-panel">
        <div class="def-box">
          <div class="small muted">定义</div>
          <code>A · v = λ · v　（v ≠ 0）—— v 方向不变，仅被拉伸 λ 倍</code>
        </div>
        <el-divider />
        <template v-if="hasReal">
          <div class="info-row"><span>特征值 λ₁（主特征值）</span><b style="color:#e05252">{{ fmt(lam[0]) }}</b></div>
          <div class="info-row"><span>对应单位特征向量 v₁</span><b>({{ fmt(v1[0]) }}, {{ fmt(v1[1]) }})</b></div>
          <div class="info-row"><span>特征值 λ₂</span><b style="color:var(--success)">{{ fmt(lam[1]) }}</b></div>
          <div class="info-row"><span>对应单位特征向量 v₂</span><b>({{ fmt(v2[0]) }}, {{ fmt(v2[1]) }})</b></div>
          <div class="info-row"><span>迹 tr(A) = λ₁ + λ₂</span><b>{{ fmt(lam[0] + lam[1]) }}</b></div>
          <div class="info-row"><span>行列式 det(A) = λ₁ · λ₂</span><b>{{ fmt(lam[0] * lam[1]) }}</b></div>
        </template>
        <div v-else class="no-real">
          <el-alert type="info" :closable="false" show-icon title="该矩阵没有实特征值（判别式 < 0）">
            <span class="small">本质是旋转变换：没有任何方向能保持不动，因此实数范围内无特征向量。</span>
          </el-alert>
        </div>
        <el-divider />
        <div class="info-row"><span>当前迭代向量 vₖ</span><b>({{ fmt(vec.x) }}, {{ fmt(vec.y) }})</b></div>
        <div class="info-row"><span>瑞利商 vₖᵀAvₖ / vₖᵀvₖ</span><b style="color:#b46a15">{{ fmt(cur.rq) }}</b></div>
        <div class="info-row" v-if="hasReal">
          <span>与 λ₁ 的差距</span>
          <el-tag size="small" :type="Math.abs(cur.rq - lam[0]) < 0.02 ? 'success' : 'warning'">{{ fmt(Math.abs(cur.rq - lam[0])) }}</el-tag>
        </div>
        <div class="tbl">
          <div class="tbl-head"><span>迭代 k</span><span>瑞利商 ≈ λ</span><span>与 v₁ 夹角</span></div>
          <div v-for="(s, i) in player.steps.value" :key="i" class="tbl-row" :class="{ active: i === player.idx.value }" @click="player.seek(i)">
            <span>{{ s.k }}</span><span>{{ fmt(s.rq) }}</span><span>{{ s.angle === null ? '-' : fmt(s.angle) + '°' }}</span>
          </div>
        </div>
        <p class="small muted tip">幂迭代：反复左乘 A 并归一化，向量方向会转向绝对值最大的特征值对应的特征向量（这就是 PageRank 的原理）。</p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#7b61ff"></i> 单位圆 → 椭圆（A 的作用）</span>
      <span><i class="dot" style="background:#e05252"></i> λ₁ 特征方向</span>
      <span><i class="dot" style="background:#22a06b"></i> λ₂ 特征方向</span>
      <span><i class="dot" style="background:#f2994a"></i> 迭代向量 vₖ</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const PRESETS = [
  { key: 'sym', label: 'A = [[2,1],[1,2]]', m: [2, 1, 1, 2] },
  { key: 'upper', label: 'A = [[3,1],[0,2]]', m: [3, 1, 0, 2] },
  { key: 'markov', label: 'A = [[0.8,0.3],[0.2,0.7]]', m: [0.8, 0.3, 0.2, 0.7] },
  { key: 'big', label: 'A = [[4,1],[2,3]]', m: [4, 1, 2, 3] },
  { key: 'rot', label: 'A = 旋转 60°（无实特征值）', m: [0.5, -0.866, 0.866, 0.5] }
]
const presetKey = ref('sym')
const mRaw = reactive([2, 1, 1, 2])
function applyPreset() {
  const p = PRESETS.find(x => x.key === presetKey.value)
  if (p) { mRaw[0] = p.m[0]; mRaw[1] = p.m[1]; mRaw[2] = p.m[2]; mRaw[3] = p.m[3] }
  player.reset()
}

const W = 520, H = 380
const O = { x: 250, y: 190 }
const U = 62

const eigen = computed(() => {
  const [a, b, c, d] = mRaw
  const tr = a + d
  const det = a * d - b * c
  const disc = tr * tr - 4 * det
  if (disc < -1e-9) return { real: false }
  const s = Math.sqrt(Math.max(0, disc))
  let l1 = (tr + s) / 2
  let l2 = (tr - s) / 2
  const vecFor = lam => {
    let v
    if (Math.abs(b) > 1e-9) v = [b, lam - a]
    else if (Math.abs(c) > 1e-9) v = [lam - d, c]
    else v = Math.abs(lam - a) < 1e-9 ? [1, 0] : [0, 1]
    const n = Math.hypot(v[0], v[1]) || 1
    return [v[0] / n, v[1] / n]
  }
  let v1 = vecFor(l1)
  let v2 = vecFor(l2)
  // 保证 λ1 是主特征值（绝对值最大）
  if (Math.abs(l2) > Math.abs(l1)) {
    const tl = l1; l1 = l2; l2 = tl
    const tv = v1; v1 = v2; v2 = tv
  }
  return { real: true, l1, l2, v1, v2 }
})
const hasReal = computed(() => eigen.value.real)
const lam = computed(() => (hasReal.value ? [eigen.value.l1, eigen.value.l2] : [0, 0]))
const v1 = computed(() => (hasReal.value ? eigen.value.v1 : [1, 0]))
const v2 = computed(() => (hasReal.value ? eigen.value.v2 : [0, 1]))

const N_ITER = 12
const steps = computed(() => {
  const [a, b, c, d] = mRaw
  let vx = 1, vy = 0.45
  const n0 = Math.hypot(vx, vy)
  vx /= n0; vy /= n0
  const out = []
  const push = (k, x, y, note) => {
    const rq = (x * (a * x + b * y) + y * (c * x + d * y)) / (x * x + y * y)
    let angle = null
    if (hasReal.value) {
      const [e1x, e1y] = eigen.value.v1
      let dot = Math.abs(x * e1x + y * e1y)
      dot = Math.min(1, Math.max(-1, dot))
      angle = (Math.acos(dot) * 180) / Math.PI
    }
    out.push({ k, x, y, rq, angle, desc: note })
  }
  push(0, vx, vy, '取初始向量 v₀ = (0.912, 0.410)，反复左乘 A 并归一化，观察它的方向变化')
  for (let k = 1; k <= N_ITER; k++) {
    const nx = a * vx + b * vy
    const ny = c * vx + d * vy
    const n = Math.hypot(nx, ny) || 1
    vx = nx / n; vy = ny / n
    push(k, vx, vy, `第 ${k} 次迭代：A·v₍${k - 1}₎ 归一化得 v₍${k}₎，瑞利商 ≈ ${((vx * (a * vx + b * vy) + vy * (c * vx + d * vy)) / (vx * vx + vy * vy)).toFixed(4)}，方向正转向主特征向量`)
  }
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const vec = computed(() => ({ x: cur.value.x, y: cur.value.y }))

// 展示缩放：把迭代向量画在单位圆尺度附近
const scaleShow = computed(() => {
  const n = Math.hypot(cur.value.x, cur.value.y) || 1
  return 1 / n
})

const trailPoints = computed(() => {
  const pts = []
  for (let i = 0; i <= player.idx.value; i++) {
    const s = player.steps.value[i]
    if (!s) continue
    const n = Math.hypot(s.x, s.y) || 1
    pts.push((O.x + (s.x / n) * U).toFixed(1) + ',' + (O.y - (s.y / n) * U).toFixed(1))
  }
  return pts.join(' ')
})

const ellipsePath = computed(() => {
  const [a, b, c, d] = mRaw
  const n = 96
  let p = ''
  for (let i = 0; i <= n; i++) {
    const ang = (Math.PI * 2 * i) / n
    const x = Math.cos(ang), y = Math.sin(ang)
    const tx = a * x + b * y
    const ty = c * x + d * y
    p += (i === 0 ? 'M' : 'L') + (O.x + tx * U * 0.5).toFixed(2) + ' ' + (O.y - ty * U * 0.5).toFixed(2) + ' '
  }
  return p + 'Z'
})

const eigenLines = computed(() => {
  if (!hasReal.value) return []
  return [eigen.value.v1, eigen.value.v2].map((v, i) => {
    const L = 300
    const x1 = O.x - v[0] * L, y1 = O.y + v[1] * L
    const x2 = O.x + v[0] * L, y2 = O.y - v[1] * L
    return {
      x1, y1, x2, y2,
      tx: O.x + v[0] * (U + 34) + 4,
      ty: O.y - v[1] * (U + 34),
      lambda: i === 0 ? eigen.value.l1 : eigen.value.l2
    }
  })
})

function fmt(v) {
  if (v === null || v === undefined || !isFinite(v)) return '-'
  return Number(v.toFixed(4)).toString()
}
</script>

<style scoped>
.ev-wrap { display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap; }
.ev-svg { background: #fcfdff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.ev-panel { flex: 1; min-width: 300px; }
.def-box code { background: #f2f4f8; padding: 8px 10px; border-radius: 6px; display: block; font-size: 12px; line-height: 1.7; }
.info-row { display: flex; justify: space-between; align-items: center; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.tbl { font-size: 12px; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; margin-top: 8px; }
.tbl-head { display: grid; grid-template-columns: 1fr 1.2fr 1fr; background: #f6f8fb; padding: 7px 10px; font-weight: 600; }
.tbl-row { display: grid; grid-template-columns: 1fr 1.2fr 1fr; padding: 6px 10px; border-top: 1px solid #f0f2f6; cursor: pointer; }
.tbl-row:hover { background: #f6f8fb; }
.tbl-row.active { background: var(--brand-light); color: var(--brand); font-weight: 600; }
.tip { margin-top: 10px; line-height: 1.7; }
.no-real { margin: 6px 0; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
