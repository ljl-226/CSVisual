<template>
  <VisFrame
    title="刚体定轴转动"
    desc="为什么看这个动画：同一力矩下转动惯量越大越难加速；无外力矩时收拢质量会减小 I，并迫使角速度增大以守恒角动量。"
    :player="player"
    :status-text="statusText"
    back-to="/knowledge/91"
  >
    <template #extra>
      <el-select v-model="objectKey" size="small" style="width: 145px" @change="player.reset()">
        <el-option v-for="item in OBJECTS" :key="item.key" :label="item.label" :value="item.key" />
      </el-select>
      <el-select v-model="mode" size="small" style="width: 145px" @change="player.reset()">
        <el-option value="torque" label="恒力矩对比" />
        <el-option value="momentum" label="收拢手臂" />
      </el-select>
    </template>

    <div class="rb-wrap">
      <div ref="plotHost" class="plot-host">
        <svg viewBox="0 0 720 420" class="rb-svg" role="img" aria-label="刚体转动惯量和角动量守恒动画">
          <rect x="1" y="1" width="718" height="418" rx="10" fill="#fcfdff" stroke="#e4e8ef" />

          <g v-if="mode === 'torque'">
            <text x="20" y="28" class="section-title">相同力矩 τ={{ torque.toFixed(1) }} N·m：偏心轴与中心轴对比</text>
            <line x1="360" y1="46" x2="360" y2="355" stroke="#e4e8ef" />
            <text x="180" y="62" text-anchor="middle" font-size="13" fill="#526071">偏心轴 I=I꜀+Md²</text>
            <text x="540" y="62" text-anchor="middle" font-size="13" fill="#526071">中心轴 I꜀</text>

            <!-- 物体质心偏离转轴 d 后绕固定轴公转，体现平行轴定理增加的 Md²。 -->
            <g :transform="`rotate(${cur.angleDeg} 180 205)`">
              <line x1="180" y1="205" :x2="180 + offsetPx" y2="205" stroke="#8b95a3" stroke-width="2" stroke-dasharray="5 4" />
              <g :transform="`translate(${180 + offsetPx} 205)`">
                <rect v-if="objectKey === 'rod'" x="-92" y="-10" width="184" height="20" rx="8" fill="#7ea1f1" stroke="#3b6ef6" stroke-width="2" />
                <circle v-else-if="objectKey === 'ring'" cx="0" cy="0" r="72" fill="none" stroke="#8b5cf6" stroke-width="13" />
                <ellipse v-else-if="objectKey === 'cylinder'" cx="0" cy="0" rx="76" ry="52" fill="#d7e3ff" stroke="#3b6ef6" stroke-width="3" />
                <circle v-else cx="0" cy="0" r="70" fill="#d7e3ff" stroke="#3b6ef6" stroke-width="3" />
                <line x1="0" y1="0" x2="68" y2="0" stroke="#e05252" stroke-width="3" />
              </g>
            </g>
            <circle cx="180" cy="205" r="6" fill="#1f2733" />
            <text x="180" y="321" text-anchor="middle" font-size="12" fill="#3b6ef6">α={{ fmt(alphaCurrent) }} rad/s²</text>
            <text x="180" y="343" text-anchor="middle" font-size="12" fill="#526071">θ={{ fmt(cur.angle) }} rad</text>

            <g :transform="`rotate(${cur.referenceAngleDeg} 540 205)`">
              <rect v-if="objectKey === 'rod'" x="448" y="195" width="184" height="20" rx="8" fill="#bcead2" stroke="#22a06b" stroke-width="2" />
              <circle v-else-if="objectKey === 'ring'" cx="540" cy="205" r="72" fill="none" stroke="#22a06b" stroke-width="13" />
              <ellipse v-else-if="objectKey === 'cylinder'" cx="540" cy="205" rx="76" ry="52" fill="#d8f3e5" stroke="#22a06b" stroke-width="3" />
              <circle v-else cx="540" cy="205" r="70" fill="#d8f3e5" stroke="#22a06b" stroke-width="3" />
              <line x1="540" y1="205" x2="608" y2="205" stroke="#e05252" stroke-width="3" />
            </g>
            <circle cx="540" cy="205" r="6" fill="#1f2733" />
            <text x="540" y="321" text-anchor="middle" font-size="12" fill="#22a06b">α꜀={{ fmt(alphaCenter) }} rad/s²</text>
            <text x="540" y="343" text-anchor="middle" font-size="12" fill="#526071">θ꜀={{ fmt(cur.referenceAngle) }} rad</text>
            <text v-if="!compact" x="360" y="390" text-anchor="middle" font-size="13" font-weight="700" fill="#b46a15">偏心后角加速度变为中心轴的 {{ fmt(alphaCurrent / alphaCenter * 100) }}%</text>
          </g>

          <g v-else>
            <text x="20" y="28" class="section-title">无外力矩：L=Iω 守恒，收拢手臂使角速度上升</text>
            <circle cx="360" cy="215" r="104" fill="none" stroke="#edf0f5" stroke-width="2" stroke-dasharray="6 5" />
            <g :transform="`rotate(${cur.angleDeg} 360 215)`">
              <circle cx="360" cy="215" r="31" fill="#d7e3ff" stroke="#3b6ef6" stroke-width="3" />
              <line :x1="360 - armRadius" y1="215" :x2="360 + armRadius" y2="215" stroke="#8b5cf6" stroke-width="9" stroke-linecap="round" />
              <circle :cx="360 - armRadius" cy="215" r="16" fill="#f2994a" stroke="#b46a15" stroke-width="2" />
              <circle :cx="360 + armRadius" cy="215" r="16" fill="#f2994a" stroke="#b46a15" stroke-width="2" />
              <line x1="360" y1="215" x2="360" y2="128" stroke="#e05252" stroke-width="3" marker-end="url(#rb-arrow)" />
            </g>
            <circle cx="360" cy="215" r="6" fill="#1f2733" />
            <text x="115" y="120" font-size="13" fill="#526071">初态 I₀={{ fmt(momentumInitialI) }}</text>
            <text x="115" y="145" font-size="13" fill="#526071">ω₀={{ fmt(initialOmega) }} rad/s</text>
            <text x="115" y="170" font-size="13" fill="#8b5cf6">L=I₀ω₀={{ fmt(angularMomentum) }}</text>
            <text x="505" y="120" font-size="13" fill="#526071">当前 I={{ fmt(cur.dynamicI) }}</text>
            <text x="505" y="145" font-size="13" fill="#e05252">ω={{ fmt(cur.omega) }} rad/s</text>
            <text x="505" y="170" font-size="13" fill="#8b5cf6">Iω={{ fmt(cur.dynamicI * cur.omega) }}</text>
            <text x="360" y="365" text-anchor="middle" font-size="13" fill="#526071">手臂半径 {{ fmt(cur.armScale * radius) }} m（初始 {{ fmt(radius) }} m）</text>
            <defs><marker id="rb-arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 Z" fill="#e05252" /></marker></defs>
          </g>
        </svg>
      </div>

      <div class="rb-panel">
        <div class="param-row">
          <span>质量 M={{ mass.toFixed(1) }} kg</span>
          <el-slider v-model="mass" :min="0.5" :max="10" :step="0.5" :show-tooltip="false" @input="player.reset()" />
        </div>
        <div class="param-row">
          <span>尺寸 R={{ radius.toFixed(1) }} m</span>
          <el-slider v-model="radius" :min="0.5" :max="3" :step="0.1" :show-tooltip="false" @input="player.reset()" />
        </div>
        <div class="param-row">
          <span>轴距 d={{ offset.toFixed(1) }} m</span>
          <el-slider v-model="offset" :min="0" :max="2" :step="0.1" :disabled="mode === 'momentum'" :show-tooltip="false" @input="player.reset()" />
        </div>
        <div class="formula"><code>{{ object.formula }}；I=I꜀+Md²</code></div>
        <el-divider />
        <div class="info-row"><span>质心轴转动惯量 I꜀</span><b>{{ fmt(centerInertia) }} kg·m²</b></div>
        <div class="info-row"><span>平行轴增量 Md²</span><b>{{ fmt(parallelTerm) }} kg·m²</b></div>
        <div class="info-row"><span>当前转动惯量 I</span><b style="color: #3b6ef6">{{ fmt(currentInertia) }} kg·m²</b></div>
        <template v-if="mode === 'torque'">
          <div class="info-row"><span>角加速度 α=τ/I</span><b style="color: #e05252">{{ fmt(alphaCurrent) }} rad/s²</b></div>
          <div class="info-row"><span>当前角速度 αt</span><b>{{ fmt(alphaCurrent * cur.time) }} rad/s</b></div>
        </template>
        <template v-else>
          <div class="info-row"><span>当前角速度 ω=L/I</span><b style="color: #e05252">{{ fmt(cur.omega) }} rad/s</b></div>
          <div class="info-row"><span>角动量校验 Iω</span><b style="color: #8b5cf6">{{ fmt(cur.dynamicI * cur.omega) }} kg·m²/s</b></div>
        </template>
        <p class="small muted tip">{{ object.note }} 平行轴定理中的 d 是新转轴到质心轴的垂直距离，质量离轴越远，对 I 的贡献按距离平方增长。</p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot body-dot"></i> 当前刚体/偏心轴</span>
      <span><i class="dot ref-dot"></i> 中心轴参考</span>
      <span><i class="dot omega-dot"></i> 角速度方向</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const OBJECTS = [
  { key: 'rod', label: '细杆（长 2R）', factor: 1 / 3, formula: 'I꜀=(1/12)M(2R)²=(1/3)MR²', note: '细杆绕垂直于杆且过中心的轴转动。' },
  { key: 'disk', label: '圆盘', factor: 1 / 2, formula: 'I꜀=(1/2)MR²', note: '圆盘质量分布在 0 到 R 的各个半径上。' },
  { key: 'ring', label: '圆环', factor: 1, formula: 'I꜀=MR²', note: '圆环质量都集中在最远的 R 处，所以同 M、R 下 I 最大。' },
  { key: 'cylinder', label: '圆柱（长 2R）', factor: 7 / 12, formula: 'I꜀=(1/12)M(3R²+(2R)²)=7MR²/12', note: '圆柱绕过质心且垂直于轴线的横轴转动。' }
]

const objectKey = ref('disk')
const mode = ref('torque')
const mass = ref(3)
const radius = ref(1.5)
const offset = ref(0.8)
const torque = ref(4)
const initialOmega = ref(2)
const plotHost = ref(null)
const viewportWidth = ref(720)
let resizeObserver = null

const compact = computed(() => viewportWidth.value < 540)
const object = computed(() => OBJECTS.find(item => item.key === objectKey.value) || OBJECTS[0])
const centerInertia = computed(() => object.value.factor * mass.value * radius.value * radius.value)
const parallelTerm = computed(() => mass.value * offset.value * offset.value)
const currentInertia = computed(() => centerInertia.value + parallelTerm.value)
const alphaCurrent = computed(() => torque.value / Math.max(0.001, currentInertia.value))
const alphaCenter = computed(() => torque.value / Math.max(0.001, centerInertia.value))
const offsetPx = computed(() => Math.min(58, offset.value / 2 * 58))

const momentumInitialI = computed(() => centerInertia.value)
const angularMomentum = computed(() => momentumInitialI.value * initialOmega.value)

const steps = computed(() => {
  if (mode.value === 'torque') {
    return Array.from({ length: 41 }, (_, i) => {
      const time = i * 0.1
      const angle = 0.5 * alphaCurrent.value * time * time
      const referenceAngle = 0.5 * alphaCenter.value * time * time
      return {
        time,
        angle,
        referenceAngle,
        angleDeg: angle * 180 / Math.PI,
        referenceAngleDeg: referenceAngle * 180 / Math.PI,
        dynamicI: currentInertia.value,
        omega: alphaCurrent.value * time,
        armScale: 1,
        desc: `t=${time.toFixed(1)} s：偏心轴 I=${fmt(currentInertia.value)}、α=${fmt(alphaCurrent.value)}，中心轴 I꜀=${fmt(centerInertia.value)}、α꜀=${fmt(alphaCenter.value)}；同一力矩下 I 越大，转得越慢。`
      }
    })
  }
  const out = []
  let angle = 0
  for (let i = 0; i <= 40; i++) {
    const progress = i / 40
    const armScale = 1 - 0.58 * progress
    // 把惯量拆成躯干的 25% 和手臂端质量的 75%，后者按半径平方缩小。
    const dynamicI = momentumInitialI.value * (0.25 + 0.75 * armScale * armScale)
    const omega = angularMomentum.value / dynamicI
    if (i > 0) angle += omega * 0.1
    out.push({
      time: i * 0.1,
      angle,
      referenceAngle: 0,
      angleDeg: angle * 180 / Math.PI,
      referenceAngleDeg: 0,
      dynamicI,
      omega,
      armScale,
      desc: `手臂收至初始半径的 ${(armScale * 100).toFixed(1)}%：I=${fmt(dynamicI)}，ω=${fmt(omega)}；Iω=${fmt(dynamicI * omega)} 与初始角动量 ${fmt(angularMomentum.value)} 一致。`
    })
  }
  return out
})
const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const armRadius = computed(() => 25 + 83 * cur.value.armScale)

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
.rb-wrap { display: flex; gap: 18px; align-items: flex-start; flex-wrap: wrap; }
.plot-host { flex: 2 1 590px; min-width: 0; }
.rb-svg { display: block; width: 100%; height: auto; min-height: 330px; }
.rb-panel { flex: 1 1 290px; min-width: 270px; }
.section-title { font-size: 13px; font-weight: 700; fill: #334155; }
.param-row { display: grid; grid-template-columns: 135px 1fr; gap: 10px; align-items: center; margin-bottom: 5px; font-size: 12px; }
.formula code { display: block; padding: 9px 10px; background: #f2f4f8; border-radius: 7px; font-size: 12px; line-height: 1.65; }
.info-row { display: flex; justify-content: space-between; gap: 10px; padding: 6px 0; border-bottom: 1px dashed #edf0f5; font-size: 12px; }
.info-row b { text-align: right; }
.tip { line-height: 1.75; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; }
.body-dot { background: #3b6ef6; }
.ref-dot { background: #22a06b; }
.omega-dot { background: #e05252; }
@media (max-width: 640px) {
  .rb-panel { min-width: 100%; }
  .rb-svg { min-height: 260px; }
}
</style>
