<template>
  <VisFrame title="斜面受力 · 牛顿第二定律" desc="把重力正交分解为沿斜面 mg sinθ 与垂直斜面 mg cosθ：当 tanθ ≤ μ 时可自锁静止，越过临界角后按 a = g(sinθ - μ cosθ) 匀加速下滑" :player="player" :status-text="statusText" back-to="/knowledge/62">
    <template #extra>
      <span class="small muted">倾角 {{ theta }}°</span>
      <el-slider v-model="theta" :min="0" :max="50" :step="1" style="width:100px" :show-tooltip="false" @change="player.reset()" />
      <span class="small muted">质量 {{ mass }}kg</span>
      <el-slider v-model="mass" :min="0.5" :max="10" :step="0.5" style="width:90px" :show-tooltip="false" @change="player.reset()" />
      <span class="small muted">摩擦系数 μ = {{ mu }}</span>
      <el-slider v-model="mu" :min="0" :max="0.9" :step="0.05" style="width:90px" :show-tooltip="false" @change="player.reset()" />
    </template>

    <div class="in-wrap">
      <svg :width="W" :height="H" class="in-svg">
        <!-- 斜面与地面 -->
        <polygon :points="rampPoints" fill="#eef1f6" stroke="#8b95a3" stroke-width="1.5" />
        <text :x="apex.x - 26" :y="apex.y - 8" font-size="12" fill="#8b95a3">θ = {{ theta }}°</text>
        <!-- 物体（沿斜面摆放的方块） -->
        <polygon :points="blockPoints" fill="#dbe6ff" stroke="#3b6ef6" stroke-width="2" />
        <circle :cx="center.x" :cy="center.y" r="3.5" fill="#3b6ef6" />

        <!-- 受力：重力、正交分解的两个分量、支持力、摩擦力、合力 -->
        <line :x1="center.x" :y1="center.y" :x2="center.x + gV.dx" :y2="center.y + gV.dy" stroke="#1f2733" stroke-width="2.5" />
        <text :x="center.x + gV.dx - 4" :y="center.y + gV.dy + 16" font-size="11" fill="#1f2733">mg = {{ fmt(mg) }} N</text>
        <line :x1="center.x" :y1="center.y" :x2="center.x + parV.dx" :y2="center.y + parV.dy" stroke="#3b6ef6" stroke-width="2" stroke-dasharray="4 3" />
        <text :x="center.x + parV.dx - 4" :y="center.y + parV.dy - 6" font-size="11" fill="#2a55c4">mg sinθ = {{ fmt(mgSin) }} N</text>
        <line :x1="center.x" :y1="center.y" :x2="center.x + perV.dx" :y2="center.y + perV.dy" stroke="#8b95a3" stroke-width="2" stroke-dasharray="4 3" />
        <line :x1="center.x" :y1="center.y" :x2="center.x + nV.dx" :y2="center.y + nV.dy" stroke="#22a06b" stroke-width="2.5" />
        <text :x="center.x + nV.dx - 4" :y="center.y + nV.dy - 6" font-size="11" fill="#14764e">N = {{ fmt(N) }} N</text>
        <line :x1="center.x" :y1="center.y" :x2="center.x + fV.dx" :y2="center.y + fV.dy" stroke="#e8a13a" stroke-width="2.5" />
        <text :x="center.x + fV.dx + 4" :y="center.y + fV.dy - 6" font-size="11" fill="#a5701a">f = {{ fmt(fric) }} N</text>
        <line v-if="cur.state === 'slide'" :x1="center.x" :y1="center.y" :x2="center.x + netV.dx" :y2="center.y + netV.dy" stroke="#e05252" stroke-width="3" />
        <text v-if="cur.state === 'slide'" :x="center.x + netV.dx + 4" :y="center.y + netV.dy + 14" font-size="11" fill="#c02b2b">F合 = {{ fmt(netForce) }} N</text>
        <text :x="12" :y="18" font-size="12" fill="#8b95a3">{{ cur.state === 'slide' ? '沿斜面下滑：匀加速运动' : '静止：静摩擦自动调节至与沿斜面分量平衡' }}</text>
      </svg>

      <div class="in-panel">
        <div class="def-box">
          <div class="small muted">教材公式（《大学物理》牛顿定律）</div>
          <code>沿斜面：mg sinθ - f = ma　垂直斜面：N - mg cosθ = 0
临界条件：tanθ = μ（自锁）；滑动时 f = μN，a = g(sinθ - μ cosθ)</code>
        </div>
        <el-divider />
        <div class="info-row"><span>倾角 θ / tanθ</span><b>{{ cur.theta }}° / {{ fmt(Math.tan(rad), 3) }}</b></div>
        <div class="info-row"><span>摩擦系数 μ / 临界角 arctan μ</span><b>{{ mu }} / {{ fmt((Math.atan(mu) * 180) / Math.PI, 1) }}°</b></div>
        <div class="info-row"><span>运动状态</span>
          <el-tag size="small" :type="cur.state === 'slide' ? 'danger' : 'success'">{{ cur.state === 'slide' ? '匀加速下滑' : '静止（自锁）' }}</el-tag>
        </div>
        <div class="info-row"><span>重力 mg</span><b>{{ fmt(mg) }} N</b></div>
        <div class="info-row"><span>沿斜面分量 mg sinθ</span><b style="color:var(--brand)">{{ fmt(mgSin) }} N</b></div>
        <div class="info-row"><span>垂直分量 mg cosθ = N</span><b style="color:var(--success)">{{ fmt(N) }} N</b></div>
        <div class="info-row"><span>摩擦力 f</span><b style="color:#a5701a">{{ fmt(fric) }} N</b></div>
        <div class="info-row"><span>沿斜面合力</span><b style="color:var(--danger)">{{ fmt(netForce) }} N</b></div>
        <div class="info-row"><span>加速度 a</span><b>{{ fmt(cur.a) }} m/s²</b></div>
        <div class="info-row"><span>速度 v / 位移 s</span><b>{{ fmt(cur.v) }} m/s / {{ fmt(cur.s) }} m</b></div>
        <p class="small muted tip">考点：摩擦角 φ = arctan μ 决定自锁；临界角前静摩擦是被动力（大小随 mg sinθ 自动变化，0 ≤ f ≤ μN），一旦 tanθ > μ 才开始滑动，此后 f = μN 且方向与相对运动相反。</p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#1f2733"></i> 重力 mg</span>
      <span><i class="dot" style="background:#3b6ef6"></i> 沿斜面分量 mg sinθ</span>
      <span><i class="dot" style="background:#8b95a3"></i> 垂直分量 mg cosθ</span>
      <span><i class="dot" style="background:#22a06b"></i> 支持力 N</span>
      <span><i class="dot" style="background:#e8a13a"></i> 摩擦力 f</span>
      <span><i class="dot" style="background:#e05252"></i> 合力 ma</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const G = 9.8
const theta = ref(30)
const mass = ref(2)
const mu = ref(0.3)

const W = 520, H = 340
const OX = 70, OY = 300, PPM = 88 // 每米对应的像素数
const LEN = 3 // 斜面长度（米）
const S0 = 0.28 // 物体初始位置到顶端距离（米）

const mg = computed(() => mass.value * G)

const steps = computed(() => {
  const out = []
  const M = mg.value, muv = mu.value
  const radT = (theta.value * Math.PI) / 180
  const slideNow = Math.tan(radT) > muv + 1e-9
  const aNow = slideNow ? G * (Math.sin(radT) - muv * Math.cos(radT)) : 0
  const push = (phase, th, t, desc) => {
    const r = (th * Math.PI) / 180
    const ms = mg.value * Math.sin(r)
    const nv = mg.value * Math.cos(r)
    const sl = Math.tan(r) > mu.value + 1e-9
    const a = sl ? G * (Math.sin(r) - mu.value * Math.cos(r)) : 0
    const s = sl ? Math.min(LEN - 2 * S0, 0.5 * a * t * t) : 0
    const v = sl ? Math.min(a * t, Math.sqrt(2 * a * (LEN - 2 * S0) + 1e-9)) : 0
    out.push({ phase, theta: th, t, s, v, a, state: sl ? 'slide' : 'static', ms, nv, desc })
  }
  // 阶段一：从 0° 缓慢抬到目标倾角，观察 tanθ 与 μ 的临界关系
  for (let i = 1; i <= 8; i++) {
    const th = Number(((theta.value * i) / 8).toFixed(1))
    const r = (th * Math.PI) / 180
    const sl = Math.tan(r) > mu.value + 1e-9
    const crit = ((Math.atan(mu.value) * 180) / Math.PI).toFixed(1)
    push('lift', th, 0, sl
      ? `θ = ${th}°：tanθ = ${Math.tan(r).toFixed(3)} > μ = ${mu.value} → 超过临界角 ${crit}°，重力沿斜面分量压过最大静摩擦，开始下滑`
      : `θ = ${th}°：tanθ = ${Math.tan(r).toFixed(3)} ≤ μ = ${mu.value} → 自锁，静摩擦自动调节到 f = mg sinθ = ${(mg.value * Math.sin(r)).toFixed(2)} N 保持平衡`)
  }
  const crit = ((Math.atan(muv) * 180) / Math.PI).toFixed(1)
  for (let j = 1; j <= 10; j++) {
    const t = Number((j * 0.12).toFixed(2))
    if (!slideNow) {
      push('move', theta.value, t, `保持静止：tanθ = ${Math.tan(radT).toFixed(3)} ≤ μ = ${muv}（临界角 ${crit}°），合力为 0，a = 0，v = 0`)
    } else {
      const reached = 0.5 * aNow * t * t >= LEN - 2 * S0
      push('move', theta.value, t, reached
        ? `已滑到斜面底端（用时 ${t} s），全程匀加速 a = ${aNow.toFixed(2)} m/s²`
        : `下滑第 ${j} 帧：t = ${t} s，a = g(sinθ - μcosθ) = ${aNow.toFixed(2)} m/s²，v = ${(aNow * t).toFixed(2)} m/s，位移 s = ${(0.5 * aNow * t * t).toFixed(2)} m`)
    }
  }
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)

// —— 以下量均跟随「当前步骤」的倾角与状态，保证画面与解说一致 ——
const rad = computed(() => (cur.value.theta * Math.PI) / 180)
const mgSin = computed(() => mg.value * Math.sin(rad.value))
const N = computed(() => mg.value * Math.cos(rad.value))
// 静、动摩擦系数取同一 μ：未滑动时 f 为被动静摩擦（随需增减）；滑动后 f = μN
const fric = computed(() => (cur.value.state === 'slide' ? mu.value * N.value : mgSin.value))
const netForce = computed(() => mgSin.value - fric.value)

// 几何：斜面端点、物体中心与四个角（世界坐标 → 屏幕坐标，y 轴翻转）
const apex = computed(() => ({ x: OX + LEN * PPM * Math.cos(rad.value), y: OY - LEN * PPM * Math.sin(rad.value) }))
const rampPoints = computed(() => `${OX},${OY} ${apex.value.x},${apex.value.y} ${apex.value.x},${OY}`)
const uVec = computed(() => ({ x: Math.cos(rad.value), y: -Math.sin(rad.value) }))
const nVec = computed(() => ({ x: -Math.sin(rad.value), y: -Math.cos(rad.value) }))
const center = computed(() => {
  // 沿斜面离开顶点的距离 = 初始偏移 + 已滑下的位移
  const alongPx = (S0 + cur.value.s) * PPM
  const x = apex.value.x - uVec.value.x * alongPx + nVec.value.x * 17
  const y = apex.value.y - uVec.value.y * alongPx + nVec.value.y * 17
  return { x, y }
})
const blockPoints = computed(() => {
  const c = center.value, u = uVec.value, n = nVec.value
  const aw = 22, ah = 17
  const corner = (du, dn) => `${(c.x + u.x * du + n.x * dn).toFixed(1)},${(c.y + u.y * du + n.y * dn).toFixed(1)}`
  return `${corner(aw, ah)} ${corner(-aw, ah)} ${corner(-aw, -ah)} ${corner(aw, -ah)}`
})
// 受力向量转屏幕偏移（每牛顿 PF 像素）
const PF = 2.4
function vec(fx, fy) { return { dx: fx * PF, dy: -fy * PF } }
const gV = computed(() => vec(0, -mg.value))
const parV = computed(() => vec(-mgSin.value * Math.cos(rad.value), -mgSin.value * Math.sin(rad.value)))
const perV = computed(() => vec(N.value * Math.sin(rad.value), -N.value * Math.cos(rad.value)))
const nV = computed(() => vec(-N.value * Math.sin(rad.value), N.value * Math.cos(rad.value)))
const fV = computed(() => vec(fric.value * Math.cos(rad.value), fric.value * Math.sin(rad.value)))
// 合力方向必须与 parV（重力沿斜面分量）一致 —— 都是「沿斜面向下」。
// 曾经这里取的是 (+cos, +sin)，屏幕上画成沿斜面向上，
// 而旁边摩擦力明明已经正确地朝上、物块也正在下滑，三个箭头自相矛盾。
// 取负号后，netForce 为负（摩擦占优）时会自动反向，无需额外分支。
const netV = computed(() => vec(-netForce.value * Math.cos(rad.value), -netForce.value * Math.sin(rad.value)))

function fmt(v) {
  if (v === null || v === undefined || !isFinite(v)) return '-'
  return Number(v.toFixed(2)).toString()
}
</script>

<style scoped>
.in-wrap { display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap; }
.in-svg { background: #fcfdff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.in-panel { flex: 1; min-width: 300px; }
.def-box code { background: #f2f4f8; padding: 8px 10px; border-radius: 6px; display: block; font-size: 12px; line-height: 1.7; white-space: pre-wrap; }
.info-row { display: flex; justify-content: space-between; align-items: center; gap: 10px; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.tip { margin-top: 10px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
