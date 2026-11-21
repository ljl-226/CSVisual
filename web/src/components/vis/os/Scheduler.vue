<template>
  <VisFrame :title="`进程调度算法 · ${algoName}`" :desc="algoDesc" :player="player" :status-text="statusText" back-to="/knowledge/15">
    <template #extra>
      <el-select v-model="algo" size="small" style="width:150px" @change="player.reset()">
        <el-option value="fcfs" label="FCFS 先来先服务" />
        <el-option value="sjf" label="SJF 短作业优先" />
        <el-option value="rr" label="RR 时间片轮转" />
      </el-select>
      <el-input-number v-if="algo === 'rr'" v-model="quantum" size="small" :min="1" :max="5" style="width:90px" @change="player.reset()" />
      <el-button size="small" plain @click="player.reset()">重播</el-button>
    </template>

    <!-- 甘特图 -->
    <svg :width="svgW" height="120" class="sc-svg">
      <line x1="40" y1="70" :x2="svgW - 20" y2="70" stroke="#c8d3e6" stroke-width="1.5" />
      <g v-for="(g, i) in gantt" :key="i">
        <rect
          :x="40 + g.start * UNIT" y="40" :width="Math.max(2, (g.end - g.start) * UNIT)" height="34" rx="4"
          :fill="colorOf(g.name)" :stroke="'#fff'" stroke-width="1"
        />
        <text :x="40 + (g.start + (g.end - g.start) / 2) * UNIT" y="61" text-anchor="middle" font-size="11" fill="#fff" font-weight="600">
          {{ g.name }}
        </text>
      </g>
      <!-- 当前时间指针 -->
      <line :x1="40 + time * UNIT" y1="30" :x2="40 + time * UNIT" y2="82" stroke="#e05252" stroke-width="2" />
      <text :x="40 + time * UNIT" y="24" text-anchor="middle" font-size="11" fill="#e05252" font-weight="600">t={{ time }}</text>
      <text v-for="t in tickList" :key="t" :x="40 + t * UNIT" y="96" text-anchor="middle" font-size="10" fill="#8b95a3">{{ t }}</text>
    </svg>

    <el-row :gutter="16" style="margin-top:4px">
      <el-col :span="12">
        <div class="panel-title">进程状态</div>
        <table class="ptable">
          <thead><tr><th>进程</th><th>到达</th><th>服务</th><th>剩余</th><th>状态</th></tr></thead>
          <tbody>
            <tr v-for="p in procList" :key="p.name">
              <td><b :style="{ color: colorOf(p.name) }">{{ p.name }}</b></td>
              <td>{{ p.arrive }}</td>
              <td>{{ p.service }}</td>
              <td>{{ remain[p.name] ?? p.service }}</td>
              <td>
                <el-tag size="small" :type="stateTag(p.name).type" effect="light">{{ stateTag(p.name).text }}</el-tag>
              </td>
            </tr>
          </tbody>
        </table>
      </el-col>
      <el-col :span="12">
        <div class="panel-title">就绪队列 <span class="muted small">（队头 → 队尾）</span></div>
        <div class="queue-row">
          <span v-for="(q, i) in readyQueue" :key="i" class="q-chip" :style="{ background: colorOf(q) }">{{ q }}</span>
          <span v-if="!readyQueue.length" class="small muted">（空）</span>
        </div>

        <div class="panel-title" style="margin-top:14px">周转时间统计</div>
        <div class="stat-row">
          <div class="stat-box"><div class="sv small-sv">{{ avgTurn }}</div><div class="sl">平均周转时间</div></div>
          <div class="stat-box"><div class="sv small-sv">{{ avgWeighted }}</div><div class="sl">平均带权周转</div></div>
        </div>
        <div class="tip small muted">
          周转时间 = 完成时间 − 到达时间；带权周转时间 = 周转时间 ÷ 服务时间。
          <b>SJF</b> 平均周转时间最小，但可能导致长作业饥饿。
        </div>
      </el-col>
    </el-row>

    <template #legend>
      <span v-for="p in procList" :key="'l' + p.name"><i class="dot" :style="{ background: colorOf(p.name) }"></i> {{ p.name }}</span>
      <span><i class="dot" style="background:#e05252"></i> 当前时间</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const UNIT = 34
const algo = ref('fcfs')
const quantum = ref(2)
const procList = [
  { name: 'P1', arrive: 0, service: 4 },
  { name: 'P2', arrive: 1, service: 3 },
  { name: 'P3', arrive: 2, service: 5 },
  { name: 'P4', arrive: 3, service: 2 }
]
const COLORS = { P1: '#3b6ef6', P2: '#22a06b', P3: '#e8a13a', P4: '#8b5cf6', P5: '#e05252' }

const algoName = computed(() => ({ fcfs: 'FCFS 先来先服务', sjf: 'SJF 短作业优先（非抢占）', rr: 'RR 时间片轮转' }[algo.value]))
const algoDesc = computed(() => ({
  fcfs: '按到达先后顺序执行，非抢占；有利于长作业，短作业可能等待很久（护航效应）',
  sjf: '每次从已到达进程中选服务时间最短的执行，平均周转时间最小',
  rr: '每个进程轮流获得一个时间片，用完则剥夺 CPU 回到队尾，响应及时'
}[algo.value]))

const steps = computed(() => {
  const procs = procList.map(p => ({ ...p, remain: p.service, finish: -1 }))
  const gantt = []
  const out = []
  let t = 0
  let queue = []
  let running = null
  let sliceUsed = 0
  const maxT = 60

  function snap(desc) {
    out.push({
      t, running: running ? running.name : null,
      queue: [...queue],
      gantt: gantt.map(g => ({ ...g })),
      remain: Object.fromEntries(procs.map(p => [p.name, p.remain])),
      finish: Object.fromEntries(procs.map(p => [p.name, p.finish])),
      desc
    })
  }

  snap('初始时刻：所有进程尚未到达，就绪队列为空')

  while (t < maxT && procs.some(p => p.remain > 0)) {
    // 到达
    procs.forEach(p => {
      if (p.arrive === t && p.remain > 0) {
        queue.push(p.name)
        snap(`${p.name} 到达，进入就绪队列`)
      }
    })

    // 选择进程
    if (algo.value === 'rr') {
      if (running && (running.remain <= 0 || sliceUsed >= quantum.value)) {
        if (running.remain > 0) {
          queue.push(running.name)
          snap(`${running.name} 时间片用完（${quantum.value}），回到就绪队列队尾`)
        }
        running = null
        sliceUsed = 0
      }
    } else if (running && running.remain <= 0) {
      running = null
      sliceUsed = 0
    }

    if (!running && queue.length) {
      let pickName
      if (algo.value === 'fcfs') {
        pickName = queue.shift()
      } else if (algo.value === 'sjf') {
        const sorted = [...queue].sort((a, b) => {
          const pa = procs.find(p => p.name === a)
          const pb = procs.find(p => p.name === b)
          return pa.service - pb.service
        })
        pickName = sorted[0]
        queue = queue.filter(n => n !== pickName)
      } else {
        pickName = queue.shift()
      }
      const p = procs.find(x => x.name === pickName)
      running = p
      sliceUsed = 0
      const why = algo.value === 'sjf' ? `（服务时间 ${p.service} 最短）` : ''
      snap(`调度 ${pickName} 占用 CPU${why}`)
    }

    if (!running) {
      t++
      snap(`CPU 空闲（就绪队列为空），时间推进到 ${t}`)
      continue
    }

    // 执行一个时间单位
    const start = t
    running.remain -= 1
    sliceUsed++
    t++
    gantt.push({ name: running.name, start, end: t })
    if (running.remain <= 0) {
      running.finish = t
      snap(`${running.name} 在时刻 ${t} 执行完毕，周转时间 = ${t} − ${running.arrive} = ${t - running.arrive}`)
      running = null
      sliceUsed = 0
    } else {
      snap(`${running.name} 执行中，剩余 ${running.remain}`)
    }
  }
  snap('所有进程执行完毕')
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const time = computed(() => cur.value.t)
const gantt = computed(() => {
  const raw = cur.value.gantt || []
  const merged = []
  raw.forEach(g => {
    const last = merged[merged.length - 1]
    if (last && last.name === g.name && last.end === g.start) last.end = g.end
    else merged.push({ ...g })
  })
  return merged
})
const readyQueue = computed(() => cur.value.queue || [])
const remain = computed(() => cur.value.remain || {})
const finishMap = computed(() => cur.value.finish || {})
const running = computed(() => cur.value.running)

const svgW = computed(() => Math.max(560, (time.value + 2) * UNIT + 60))
const tickList = computed(() => {
  const out = []
  for (let i = 0; i <= time.value + 1; i++) out.push(i)
  return out
})

const avgTurn = computed(() => {
  const fs = procList.map(p => ({ p, f: finishMap.value[p.name] })).filter(x => x.f > 0)
  if (!fs.length) return '-'
  const avg = fs.reduce((s, x) => s + (x.f - x.p.arrive), 0) / fs.length
  return avg.toFixed(2)
})
const avgWeighted = computed(() => {
  const fs = procList.map(p => ({ p, f: finishMap.value[p.name] })).filter(x => x.f > 0)
  if (!fs.length) return '-'
  const avg = fs.reduce((s, x) => s + (x.f - x.p.arrive) / x.p.service, 0) / fs.length
  return avg.toFixed(2)
})

function colorOf(name) { return COLORS[name] || '#8b95a3' }
function stateTag(name) {
  if (running.value === name) return { text: '运行', type: 'success' }
  if (finishMap.value[name] > 0) return { text: '已完成', type: 'info' }
  if (readyQueue.value.includes(name)) return { text: '就绪', type: 'primary' }
  const p = procList.find(x => x.name === name)
  if (time.value < p.arrive) return { text: '未到达', type: 'warning' }
  return { text: '就绪', type: 'primary' }
}

watch(algo, () => player.reset())
</script>

<style scoped>
.sc-svg { background: #fbfcff; border-radius: 8px; display: block; margin-bottom: 10px; }
.panel-title { font-size: 13px; font-weight: 600; margin-bottom: 6px; color: var(--text-2); }
.ptable { width: 100%; border-collapse: collapse; font-size: 12px; }
.ptable th, .ptable td { border: 1px solid var(--border); padding: 5px 8px; text-align: center; }
.ptable th { background: #f7f9fc; }
.queue-row { display: flex; gap: 6px; flex-wrap: wrap; border: 1px dashed var(--border); border-radius: 8px; padding: 8px; min-height: 38px; background: #fbfcff; }
.q-chip { color: #fff; border-radius: 4px; padding: 3px 10px; font-size: 12px; font-weight: 600; }
.stat-row { display: flex; gap: 12px; }
.stat-box { flex: 1; background: #fbfcff; border: 1px solid var(--border); border-radius: 8px; padding: 8px; text-align: center; }
.sv { font-size: 18px; font-weight: 700; color: var(--brand); }
.sl { font-size: 11px; color: var(--text-2); margin-top: 2px; }
.tip { margin-top: 10px; line-height: 1.8; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
