<template>
  <VisFrame
    title="机械振动与机械波"
    desc="为什么看这个动画：旋转矢量的投影产生简谐振动；两列波逐点相加后，会由频率与相位关系形成干涉、拍频或驻波。"
    :player="player"
    :status-text="statusText"
    back-to="/knowledge/92"
  >
    <template #extra>
      <el-select v-model="mode" size="small" style="width: 145px" @change="player.reset()">
        <el-option v-for="item in MODES" :key="item.key" :label="item.label" :value="item.key" />
      </el-select>
      <span class="small muted">相位差 Δφ={{ phaseDiff }}°</span>
      <el-slider v-model="phaseDiff" :min="0" :max="360" :step="15" style="width: 120px" :show-tooltip="false" @input="player.reset()" />
    </template>

    <div class="wv-wrap">
      <div ref="plotHost" class="plot-host">
        <svg viewBox="0 0 760 410" class="wv-svg" role="img" aria-label="简谐振动与机械波叠加动画">
          <rect x="1" y="1" width="758" height="408" rx="10" fill="#fcfdff" stroke="#e4e8ef" />
          <text x="18" y="27" class="section-title">{{ modeInfo.title }}</text>
          <line x1="48" y1="210" x2="548" y2="210" stroke="#8b95a3" stroke-width="1.2" />
          <line x1="48" y1="62" x2="48" y2="350" stroke="#8b95a3" stroke-width="1.2" />

          <template v-if="mode === 'shm'">
            <path :d="primaryPath" fill="none" stroke="#3b6ef6" stroke-width="2.7" />
            <line :x1="cursorX" y1="62" :x2="cursorX" y2="350" stroke="#e05252" stroke-width="1.7" stroke-dasharray="5 4" />
            <circle :cx="cursorX" :cy="mapY(cur.value)" r="5.5" fill="#e05252" />
            <!-- 匀速旋转矢量在竖直轴上的投影，数值恰等于简谐位移。 -->
            <circle cx="650" cy="205" r="76" fill="#f7f9fc" stroke="#cbd5e1" stroke-width="2" />
            <line x1="574" y1="205" x2="726" y2="205" stroke="#e4e8ef" />
            <line x1="650" y1="129" x2="650" y2="281" stroke="#e4e8ef" />
            <line x1="650" y1="205" :x2="vectorEnd.x" :y2="vectorEnd.y" stroke="#8b5cf6" stroke-width="3" marker-end="url(#wv-arrow)" />
            <line :x1="vectorEnd.x" :y1="vectorEnd.y" x2="650" :y2="vectorEnd.y" stroke="#e05252" stroke-width="2" stroke-dasharray="5 4" />
            <circle cx="650" :cy="vectorEnd.y" r="5" fill="#e05252" />
            <text x="650" y="308" text-anchor="middle" font-size="12" fill="#526071">竖直投影 x={{ fmt(cur.value) }} m</text>
            <text v-if="!compact" x="298" y="382" text-anchor="middle" font-size="11" fill="#657184">时间 t（显示 3 个周期）</text>
          </template>

          <template v-else>
            <!-- 绿色合成波的每一点都等于蓝、紫两列波在该点位移的代数和。 -->
            <path v-if="mode !== 'standing'" :d="primaryPath" fill="none" stroke="#3b6ef6" stroke-width="1.8" opacity="0.75" />
            <path v-if="mode !== 'standing'" :d="secondaryPath" fill="none" stroke="#8b5cf6" stroke-width="1.8" opacity="0.75" />
            <path :d="sumPath" fill="none" stroke="#22a06b" stroke-width="3" />
            <path v-if="mode === 'beats'" :d="upperEnvelope" fill="none" stroke="#e05252" stroke-width="1.8" stroke-dasharray="6 4" />
            <path v-if="mode === 'beats'" :d="lowerEnvelope" fill="none" stroke="#e05252" stroke-width="1.8" stroke-dasharray="6 4" />
            <line v-if="mode === 'beats'" :x1="cursorX" y1="62" :x2="cursorX" y2="350" stroke="#1f2733" stroke-width="1.5" />
            <circle v-else :cx="probeX" :cy="mapY(cur.value)" r="5.5" fill="#e05252" />
            <g v-if="mode === 'standing'">
              <circle v-for="node in standingNodes" :key="node" :cx="spaceX(node)" cy="210" r="5" fill="#e05252" />
              <text x="535" y="335" text-anchor="end" font-size="11" fill="#e05252">红点：波节</text>
            </g>
            <text x="298" y="382" text-anchor="middle" font-size="11" fill="#657184">{{ mode === 'beats' ? '时间 t' : '位置 x' }}</text>
          </template>

          <text x="55" y="78" font-size="11" fill="#8b95a3">+{{ fmt(verticalLimit) }} m</text>
          <text x="55" y="344" font-size="11" fill="#8b95a3">-{{ fmt(verticalLimit) }} m</text>
          <defs><marker id="wv-arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 Z" fill="#8b5cf6" /></marker></defs>
        </svg>
      </div>

      <div class="wv-panel">
        <div class="param-row">
          <span>振幅 A₁={{ amp1.toFixed(1) }} m</span>
          <el-slider v-model="amp1" :min="0.2" :max="2" :step="0.1" :show-tooltip="false" @input="player.reset()" />
        </div>
        <div class="param-row">
          <span>振幅 A₂={{ amp2.toFixed(1) }} m</span>
          <el-slider v-model="amp2" :min="0.2" :max="2" :step="0.1" :disabled="mode === 'shm'" :show-tooltip="false" @input="player.reset()" />
        </div>
        <div class="param-row">
          <span>频率 f₁={{ freq1.toFixed(1) }} Hz</span>
          <el-slider v-model="freq1" :min="0.5" :max="3" :step="0.1" :show-tooltip="false" @input="player.reset()" />
        </div>
        <div class="param-row">
          <span>频率 f₂={{ freq2.toFixed(1) }} Hz</span>
          <el-slider v-model="freq2" :min="0.5" :max="3" :step="0.1" :disabled="mode === 'shm' || mode === 'standing'" :show-tooltip="false" @input="player.reset()" />
        </div>
        <div class="formula"><code>{{ modeInfo.formula }}</code></div>
        <el-divider />
        <div class="info-row"><span>当前时刻 t</span><b>{{ fmt(cur.time) }} s</b></div>
        <div class="info-row"><span>当前位移 y</span><b style="color: #e05252">{{ fmt(cur.value) }} m</b></div>
        <div class="info-row"><span>角频率 ω₁=2πf₁</span><b>{{ fmt(omega1) }} rad/s</b></div>
        <div v-if="mode === 'superposition'" class="info-row"><span>同频合振幅</span><b style="color: #22a06b">{{ fmt(resultantAmplitude) }} m</b></div>
        <div v-if="mode === 'beats'" class="info-row"><span>拍频 |f₁-f₂|</span><b style="color: #8b5cf6">{{ fmt(beatFrequency) }} Hz</b></div>
        <div v-if="mode === 'beats'" class="info-row"><span>拍周期</span><b>{{ beatFrequency < 0.001 ? '∞' : fmt(1 / beatFrequency) + ' s' }}</b></div>
        <div v-if="mode === 'standing'" class="info-row"><span>波长 λ=v/f₁</span><b>{{ fmt(wavelength) }} m</b></div>
        <div v-if="mode === 'standing'" class="info-row"><span>相邻波节间距 λ/2</span><b>{{ fmt(wavelength / 2) }} m</b></div>
        <div class="state-note">{{ phenomenon }}</div>
        <p class="small muted tip">叠加原理只做位移的代数相加：同频同相加强、反相相消；频率接近产生慢包络拍频；同频反向传播形成位置固定的波节。</p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot wave1-dot"></i> 波 1</span>
      <span><i class="dot wave2-dot"></i> 波 2</span>
      <span><i class="dot sum-dot"></i> 合成波</span>
      <span><i class="dot marker-dot"></i> 当前值/包络/波节</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const MODES = [
  { key: 'shm', label: '简谐振动', title: '位移—时间曲线与旋转矢量', formula: 'x(t)=A₁cos(2πf₁t+φ)' },
  { key: 'superposition', label: '波的叠加', title: '两列同向波的逐点叠加', formula: 'y=y₁+y₂=A₁sin(k₁x-ω₁t)+A₂sin(k₂x-ω₂t+Δφ)' },
  { key: 'beats', label: '拍频', title: '频率接近时的振幅包络', formula: 'f拍=|f₁-f₂|；同振幅时 y=2Acos(πΔft)sin(2πf̄t)' },
  { key: 'standing', label: '驻波', title: '两列反向波叠加形成固定波节', formula: 'y=2A₁sin(kx)cos(ωt+Δφ)' }
]

const mode = ref('shm')
const amp1 = ref(1.2)
const amp2 = ref(1)
const freq1 = ref(1.2)
const freq2 = ref(1.5)
const phaseDiff = ref(0)
const waveSpeed = 4
const plotHost = ref(null)
const viewportWidth = ref(760)
let resizeObserver = null

const compact = computed(() => viewportWidth.value < 560)
const modeInfo = computed(() => MODES.find(item => item.key === mode.value) || MODES[0])
const phaseRad = computed(() => phaseDiff.value * Math.PI / 180)
const omega1 = computed(() => 2 * Math.PI * freq1.value)
const omega2 = computed(() => 2 * Math.PI * freq2.value)
const beatFrequency = computed(() => Math.abs(freq1.value - freq2.value))
const wavelength = computed(() => waveSpeed / freq1.value)
const resultantAmplitude = computed(() => Math.sqrt(amp1.value ** 2 + amp2.value ** 2 + 2 * amp1.value * amp2.value * Math.cos(phaseRad.value)))
const verticalLimit = computed(() => {
  if (mode.value === 'shm') return amp1.value * 1.2
  if (mode.value === 'standing') return 2 * amp1.value * 1.15
  return (amp1.value + amp2.value) * 1.15
})
const duration = computed(() => {
  if (mode.value === 'shm') return 3 / freq1.value
  if (mode.value === 'beats') return Math.min(10, beatFrequency.value < 0.05 ? 6 : 2.5 / beatFrequency.value)
  return 2 / freq1.value
})
const phenomenon = computed(() => {
  if (mode.value === 'shm') return `旋转一周用时 T=1/f=${fmt(1 / freq1.value)} s，投影完成一次往复振动。`
  if (mode.value === 'beats') return beatFrequency.value < 0.05 ? '两频率几乎相同，拍频接近 0。' : `包络每 ${fmt(1 / beatFrequency.value)} s 强弱重复一次。`
  if (mode.value === 'standing') return `波节位置始终不动，相邻波节相距 λ/2=${fmt(wavelength.value / 2)} m。`
  if (Math.abs(freq1.value - freq2.value) > 0.02) return '频率不同，相位关系不断漂移，合振幅随时间变化。'
  if (Math.abs((phaseDiff.value % 360)) < 15 || Math.abs(phaseDiff.value - 360) < 15) return '两波近似同相，发生干涉加强。'
  if (Math.abs(phaseDiff.value - 180) < 15) return '两波近似反相；振幅相等时会完全相消。'
  return `同频固定相位差，合振幅为 ${fmt(resultantAmplitude.value)} m。`
})

const steps = computed(() => Array.from({ length: 121 }, (_, i) => {
  const time = duration.value * i / 120
  let value
  if (mode.value === 'shm') value = amp1.value * Math.cos(omega1.value * time + phaseRad.value)
  else if (mode.value === 'beats') value = amp1.value * Math.sin(omega1.value * time) + amp2.value * Math.sin(omega2.value * time + phaseRad.value)
  else if (mode.value === 'standing') {
    const probe = wavelength.value / 4
    value = 2 * amp1.value * Math.sin(2 * Math.PI * probe / wavelength.value) * Math.cos(omega1.value * time + phaseRad.value)
  } else {
    const probe = 4
    value = amp1.value * Math.sin(2 * Math.PI * freq1.value / waveSpeed * probe - omega1.value * time)
      + amp2.value * Math.sin(2 * Math.PI * freq2.value / waveSpeed * probe - omega2.value * time + phaseRad.value)
  }
  return { time, value, phase: omega1.value * time + phaseRad.value, desc: `t=${fmt(time)} s：当前位移 ${fmt(value)} m；${phenomenon.value}` }
}))
const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)

function mapY(value) { return 210 - value / Math.max(0.2, verticalLimit.value) * 132 }
function plotX(ratio) { return 48 + ratio * 500 }
function spaceX(x) { return plotX(x / 8) }
function pathFrom(fn) {
  const points = []
  for (let i = 0; i <= 240; i++) {
    const ratio = i / 240
    points.push({ x: plotX(ratio), y: mapY(fn(ratio)) })
  }
  return points.map((point, i) => `${i ? 'L' : 'M'}${point.x.toFixed(1)},${point.y.toFixed(1)}`).join(' ')
}

const primaryPath = computed(() => {
  if (mode.value === 'shm') return pathFrom(r => amp1.value * Math.cos(omega1.value * duration.value * r + phaseRad.value))
  if (mode.value === 'beats') return pathFrom(r => amp1.value * Math.sin(omega1.value * duration.value * r))
  return pathFrom(r => {
    const x = 8 * r
    return amp1.value * Math.sin(2 * Math.PI * freq1.value / waveSpeed * x - omega1.value * cur.value.time)
  })
})
const secondaryPath = computed(() => {
  if (mode.value === 'beats') return pathFrom(r => amp2.value * Math.sin(omega2.value * duration.value * r + phaseRad.value))
  return pathFrom(r => {
    const x = 8 * r
    return amp2.value * Math.sin(2 * Math.PI * freq2.value / waveSpeed * x - omega2.value * cur.value.time + phaseRad.value)
  })
})
const sumPath = computed(() => {
  if (mode.value === 'beats') return pathFrom(r => {
    const t = duration.value * r
    return amp1.value * Math.sin(omega1.value * t) + amp2.value * Math.sin(omega2.value * t + phaseRad.value)
  })
  if (mode.value === 'standing') return pathFrom(r => {
    const x = 8 * r
    return 2 * amp1.value * Math.sin(2 * Math.PI * x / wavelength.value) * Math.cos(omega1.value * cur.value.time + phaseRad.value)
  })
  return pathFrom(r => {
    const x = 8 * r
    return amp1.value * Math.sin(2 * Math.PI * freq1.value / waveSpeed * x - omega1.value * cur.value.time)
      + amp2.value * Math.sin(2 * Math.PI * freq2.value / waveSpeed * x - omega2.value * cur.value.time + phaseRad.value)
  })
})
function beatEnvelope(sign) {
  return pathFrom(r => {
    const t = duration.value * r
    const envelope = Math.sqrt(amp1.value ** 2 + amp2.value ** 2 + 2 * amp1.value * amp2.value * Math.cos((omega1.value - omega2.value) * t - phaseRad.value))
    return sign * envelope
  })
}
const upperEnvelope = computed(() => beatEnvelope(1))
const lowerEnvelope = computed(() => beatEnvelope(-1))
const cursorX = computed(() => plotX(cur.value.time / duration.value))
const probeX = computed(() => mode.value === 'standing' ? spaceX(wavelength.value / 4) : spaceX(4))
const vectorEnd = computed(() => ({ x: 650 + 70 * Math.cos(cur.value.phase), y: 205 - 70 * Math.sin(cur.value.phase) }))
const standingNodes = computed(() => {
  const nodes = []
  for (let x = 0; x <= 8.0001; x += wavelength.value / 2) nodes.push(x)
  return nodes
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
.wv-wrap { display: flex; gap: 18px; align-items: flex-start; flex-wrap: wrap; }
.plot-host { flex: 2 1 610px; min-width: 0; }
.wv-svg { display: block; width: 100%; height: auto; min-height: 330px; }
.wv-panel { flex: 1 1 300px; min-width: 280px; }
.section-title { font-size: 13px; font-weight: 700; fill: #334155; }
.param-row { display: grid; grid-template-columns: 145px 1fr; gap: 10px; align-items: center; margin-bottom: 5px; font-size: 12px; }
.formula code { display: block; padding: 9px 10px; background: #f2f4f8; border-radius: 7px; font-size: 12px; line-height: 1.65; }
.info-row { display: flex; justify-content: space-between; gap: 10px; padding: 6px 0; border-bottom: 1px dashed #edf0f5; font-size: 12px; }
.state-note { margin-top: 12px; padding: 9px 10px; border-radius: 8px; background: #eefbf4; color: #176b49; font-size: 12px; line-height: 1.6; }
.tip { line-height: 1.75; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; }
.wave1-dot { background: #3b6ef6; }
.wave2-dot { background: #8b5cf6; }
.sum-dot { background: #22a06b; }
.marker-dot { background: #e05252; }
@media (max-width: 640px) {
  .wv-panel { min-width: 100%; }
  .wv-svg { min-height: 260px; }
}
</style>
