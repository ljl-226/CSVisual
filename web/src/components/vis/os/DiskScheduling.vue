<template>
  <VisFrame title="磁盘调度 · 磁头移动与寻道长度" desc="按算法决定磁头服务顺序：SSTF 就近、SCAN/LOOK 像电梯往复、C-SCAN 单向环扫；总移动磁道数越少，平均寻道时间越短" :player="player" :status-text="statusText" back-to="/knowledge/49">
    <template #extra>
      <el-select v-model="alg" size="small" style="width:110px" @change="player.reset()">
        <el-option value="fcfs" label="FCFS" />
        <el-option value="sstf" label="SSTF" />
        <el-option value="scan" label="SCAN 电梯" />
        <el-option value="cscan" label="C-SCAN" />
        <el-option value="look" label="LOOK" />
      </el-select>
      <el-select v-model="dir" size="small" style="width:110px" @change="player.reset()">
        <el-option :value="1" label="初始向磁道增大" />
        <el-option :value="-1" label="初始向磁道减小" />
      </el-select>
      <el-input v-model="seqText" size="small" style="width:190px" placeholder="磁道请求序列" />
      <el-input v-model="startText" size="small" style="width:80px" placeholder="起始磁道" />
      <el-button size="small" @click="applyInput">应用</el-button>
      <el-button size="small" plain @click="resetAll">重置</el-button>
    </template>
    <div class="dk-wrap">
      <svg :width="W" :height="H" class="dk-svg">
        <text x="12" y="14" font-size="11" fill="#8b95a3">磁盘磁道 0 ~ {{ MAX }}　当前算法：{{ algName }}</text>
        <!-- 磁道刻度轴 -->
        <line :x1="PAD" :y1="TRACK_Y" :x2="W - PAD" :y2="TRACK_Y" stroke="#c8d3e6" stroke-width="2" />
        <g v-for="t in ticks" :key="t">
          <line :x1="x(t)" :y1="TRACK_Y" :x2="x(t)" :y2="TRACK_Y + 8" stroke="#c8d3e6" />
          <text :x="x(t)" :y="TRACK_Y + 21" text-anchor="middle" font-size="10" fill="#8b95a3">{{ t }}</text>
        </g>
        <!-- 请求标记 -->
        <g v-for="(t, i) in requests" :key="'q' + i">
          <line :x1="x(t)" :y1="TRACK_Y - 26" :x2="x(t)" :y2="TRACK_Y - 4"
                :stroke="served.includes(t) ? '#22a06b' : '#e8a13a'" :stroke-width="served.includes(t) ? 2 : 3" />
          <circle :cx="x(t)" :cy="TRACK_Y - 32" r="7" :fill="served.includes(t) ? '#dcf3e7' : '#fff3e0'"
                  :stroke="served.includes(t) ? '#22a06b' : '#e8a13a'" stroke-width="1.5" />
        </g>
        <!-- 磁头移动轨迹（折线，越走越低） -->
        <polyline :points="pathPoints" fill="none" :stroke="colorOf(alg)" stroke-width="2" stroke-linejoin="round" />
        <g v-for="(p, i) in path" :key="'p' + i">
          <circle :cx="x(p.t)" :cy="yAt(i + 1)" r="4" :fill="i === path.length - 1 ? colorOf(alg) : '#fff'" :stroke="colorOf(alg)" stroke-width="1.5" />
          <text v-if="p.service" :x="x(p.t)" :y="yAt(i + 1) - 8" text-anchor="middle" font-size="9.5" fill="#8b95a3">{{ p.no }}</text>
        </g>
        <!-- 磁头当前位置 -->
        <g :transform="`translate(${x(cur.head)}, ${yAt(path.length)})`">
          <path d="M-7,-14 L7,-14 L0,-2 z" :fill="colorOf(alg)" />
          <text x="0" y="-18" text-anchor="middle" font-size="10" font-weight="700" :fill="colorOf(alg)">磁头 {{ cur.head }}</text>
        </g>
      </svg>
      <div class="dk-panel">
        <div class="info-row"><span>本步服务磁道</span><b :style="{ color: cur.service ? '#22a06b' : '#8b95a3' }">{{ cur.head }}{{ cur.service ? '' : '（端点/换向）' }}</b></div>
        <div class="info-row"><span>本次移动距离</span><b style="color:var(--brand)">{{ cur.dist }} 磁道</b></div>
        <div class="info-row"><span>累计移动磁道数</span><b style="color:var(--warning)">{{ cur.total }}</b></div>
        <div class="info-row"><span>平均寻道长度</span><b>{{ avg }}</b></div>
        <div class="info-row"><span>已服务 / 总请求</span><b>{{ cur.servedCount }} / {{ requests.length }}</b></div>
        <el-divider />
        <div class="tbl">
          <div class="tbl-head"><span>#</span><span>磁道</span><span>移动</span><span>累计</span></div>
          <div v-for="(s, i) in player.steps.value" :key="i" class="tbl-row" :class="{ active: i === player.idx.value }" @click="player.seek(i)">
            <span>{{ s.no || '—' }}</span><span>{{ s.head }}</span><span>{{ s.dist }}</span><span>{{ s.total }}</span>
          </div>
        </div>
        <p class="tip small muted">{{ algNote }}</p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#e8a13a"></i> 未服务的磁道请求</span>
      <span><i class="dot" style="background:#22a06b"></i> 已服务的磁道请求</span>
      <span><i class="dot" style="background:#3b6ef6"></i> 磁头移动轨迹</span>
      <span><i class="dot" style="background:#8b5cf6"></i> 换向端点（不计入服务）</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'
const W = 660
const H = 250
const PAD = 30
const TRACK_Y = 60
const MAX = 199
const alg = ref('scan')
const dir = ref(1)
const seqText = ref('98,183,37,122,14,124,65,67')
const startText = ref('53')
const requests = ref([98, 183, 37, 122, 14, 124, 65, 67])
const start = ref(53)
const ticks = [0, 50, 100, 150, 199]
const x = t => PAD + (t / MAX) * (W - 2 * PAD)
// 轨迹越往后越往下画，形成"时间轴"效果
const rowH = computed(() => Math.max(14, Math.min(24, (H - TRACK_Y - 60) / Math.max(1, steps.value.length - 1))))
const yAt = i => TRACK_Y + 40 + i * rowH.value
const algName = computed(() => ({ fcfs: 'FCFS 先来先服务', sstf: 'SSTF 最短寻道优先', scan: 'SCAN 电梯算法', cscan: 'C-SCAN 循环扫描', look: 'LOOK 算法' }[alg.value]))
const colorOf = a => ({ fcfs: '#3b6ef6', sstf: '#22a06b', scan: '#e8a13a', cscan: '#8b5cf6', look: '#e05252' }[a] || '#3b6ef6')
const algNote = computed(() => ({
  fcfs: 'FCFS 按请求到达顺序服务，最公平但磁头来回乱跑，平均寻道长度最大，常用于请求较少的场合。',
  sstf: 'SSTF 每次选离当前磁头最近的请求，寻道时间最短，但远处请求可能长期得不到服务 → 产生"饥饿"现象。',
  scan: 'SCAN（电梯算法）：磁头沿一个方向扫到底（到 0 或 199）再反向，兼顾公平与效率；两端请求命中率偏低。',
  cscan: 'C-SCAN：单向扫描，到端点后直接（快速）回到另一端再继续，使各磁道的等待时间更均匀。',
  look: 'LOOK：与 SCAN 思路相同，但只走到该方向上最远的请求处就立即反向，省去跑到端点的无用行程。'
}[alg.value]))
/* 生成服务序列；含换向端点（service=false 表示不是真正的请求） */
function schedule(q, s) {
  const res = []
  const a = alg.value
  const d = dir.value
  if (a === 'fcfs') { for (const t of q) res.push({ t, service: true }) }
  else if (a === 'sstf') {
    const left = [...q]; let c = s
    while (left.length) {
      let bi = 0
      for (let i = 1; i < left.length; i++) if (Math.abs(left[i] - c) < Math.abs(left[bi] - c)) bi = i
      res.push({ t: left[bi], service: true }); c = left[bi]; left.splice(bi, 1)
    }
  } else {
    const up = q.filter(t => t >= s).sort((m, n) => m - n)
    const down = q.filter(t => t < s).sort((m, n) => n - m)
    const push = arr => arr.forEach(t => res.push({ t, service: true }))
    if (a === 'scan') {
      if (d > 0) { push(up); res.push({ t: MAX, service: false }); push(down) }
      else { push(down); res.push({ t: 0, service: false }); push(up) }
    } else if (a === 'cscan') {
      if (d > 0) { push(up); res.push({ t: MAX, service: false }); res.push({ t: 0, service: false }); push(q.filter(t => t < s).sort((m, n) => m - n)) }
      else { push(down); res.push({ t: 0, service: false }); res.push({ t: MAX, service: false }); push(q.filter(t => t >= s).sort((m, n) => n - m)) }
    } else {
      if (d > 0) push(up), push(down)
      else push(down), push(up)
    }
  }
  return res
}
const steps = computed(() => {
  const out = []
  const order = schedule(requests.value, start.value)
  let head = start.value
  let total = 0
  let no = 0
  const served = []
  out.push({ head, dist: 0, total, servedCount: 0, no: 0, service: false, served: [], desc: `初始：磁头位于磁道 ${head}，等待服务的请求序列 [${requests.value.join(', ')}]，采用 ${algName.value}` })
  order.forEach(p => {
    const prev = head
    const dist = Math.abs(p.t - prev)
    total += dist
    head = p.t
    if (p.service) { no++; served.push(p.t) }
    out.push({ head, dist, total, servedCount: served.length, no: p.service ? no : 0, service: p.service, served: [...served],
      desc: p.service
        ? `第 ${no} 个服务：磁头由磁道 ${prev} 移动到磁道 ${p.t}，移动 ${dist} 个磁道；累计 ${total}，平均寻道长度 ${(total / Math.max(1, served.length)).toFixed(1)}`
        : `磁头移动到端点磁道 ${p.t}（${alg.value.toUpperCase()} 需要到端点后${alg.value === 'cscan' ? '绕回另一端' : '反向'}），移动 ${dist} 个磁道，不计入服务次数`
    })
  })
  // 直接展开上一步的快照会让末两步数据完全相同（画面停住）。
  // 补 done 标记，给模板一个明确的「全部完成」态
  out.push({ ...out[out.length - 1], done: true, desc: `全部请求服务完毕，共移动 ${total} 个磁道，平均寻道长度 = ${total} / ${requests.value.length} = ${(total / Math.max(1, requests.value.length)).toFixed(2)} 磁道` })
  return out
})
const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const served = computed(() => cur.value.served || [])
const avg = computed(() => ((cur.value.total || 0) / Math.max(1, requests.value.length)).toFixed(2) + ' 磁道')
const path = computed(() => player.steps.value.slice(1, player.idx.value + 2).map((s, i) => ({ t: s.head, service: s.service, no: s.no })))
const pathPoints = computed(() => {
  const pts = [`${x(start.value)},${yAt(0)}`]
  path.value.forEach((p, i) => pts.push(`${x(p.t)},${yAt(i + 1)}`))
  return pts.join(' ')
})
// 输入兜底：磁道号必须落在 0~MAX，序列为空则用默认值
function applyInput() {
  const list = seqText.value.split(/[,，\s]+/).filter(Boolean).map(v => Number(v))
    .filter(v => Number.isFinite(v) && v >= 0 && v <= MAX).map(v => Math.round(v))
  const s = Number(startText.value)
  start.value = Number.isFinite(s) ? Math.round(Math.min(Math.max(s, 0), MAX)) : 53
  requests.value = list.length ? list : [98, 183, 37, 122, 14, 124, 65, 67]
  seqText.value = requests.value.join(',')
  startText.value = String(start.value)
  player.reset()
}
function resetAll() {
  seqText.value = '98,183,37,122,14,124,65,67'
  startText.value = '53'
  requests.value = [98, 183, 37, 122, 14, 124, 65, 67]
  start.value = 53
  player.reset()
}
</script>

<style scoped>
.dk-wrap { display: flex; gap: 18px; align-items: flex-start; flex-wrap: wrap; }
.dk-svg { background: #fbfcff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.dk-panel { flex: 1; min-width: 280px; }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.tbl { font-size: 12px; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
.tbl-head { display: grid; grid-template-columns: 0.6fr 1fr 1fr 1fr; background: #f6f8fb; padding: 7px 10px; font-weight: 600; }
.tbl-row { display: grid; grid-template-columns: 0.6fr 1fr 1fr 1fr; padding: 6px 10px; border-top: 1px solid #f0f2f6; cursor: pointer; }
.tbl-row:hover, .tbl-row.active { background: var(--brand-light); color: var(--brand); font-weight: 600; }
.tip { margin-top: 10px; line-height: 1.8; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
