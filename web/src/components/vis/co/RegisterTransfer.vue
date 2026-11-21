<template>
  <VisFrame title="寄存器与数据通路 · 微操作序列" desc="CPU 内部寄存器通过总线互连，控制器发出的微操作控制信号决定每一拍数据的流向" :player="player" :status-text="statusText" back-to="/knowledge/21">
    <template #extra>
      <el-button size="small" plain @click="player.reset()">重播</el-button>
    </template>

    <svg width="700" height="330" class="rt-svg">
      <!-- 总线 -->
      <line x1="50" y1="165" x2="650" y2="165" stroke="#8b95a3" stroke-width="6" />
      <text x="350" y="158" text-anchor="middle" font-size="11" fill="#5a6472" font-weight="600">CPU 内部总线 BUS</text>

      <!-- 控制线 -->
      <line v-for="(r, i) in regs" :key="'c' + i" :x1="r.x" :y1="r.y + (r.side === 'up' ? 34 : -34)" :x2="r.x" y2="165"
        :stroke="isActive(r.key) ? '#3b6ef6' : '#dde3ec'" :stroke-width="isActive(r.key) ? 3 : 1.5" />

      <!-- 寄存器框 -->
      <g v-for="r in regs" :key="r.key">
        <rect :x="r.x - 48" :y="r.side === 'up' ? r.y - 18 : r.y - 18" width="96" height="36" rx="6"
          :fill="isActive(r.key) ? '#eef3ff' : '#fff'" :stroke="isActive(r.key) ? '#3b6ef6' : '#c8d3e6'" stroke-width="2" />
        <text :x="r.x" :y="r.side === 'up' ? r.y + 5 : r.y + 5" text-anchor="middle" font-size="13" font-weight="600"
          :fill="isActive(r.key) ? '#1a47b8' : '#1f2733'">{{ r.name }}</text>
        <text :x="r.x" :y="r.side === 'up' ? r.y - 24 : r.y + 32" text-anchor="middle" font-size="11" fill="#8b95a3">{{ values[r.key] }}</text>
        <text v-if="isActive(r.key)" :x="r.x + 52" :y="r.y + 4" font-size="11" :fill="roleOf(r.key) === 'out' ? '#22a06b' : '#e05252'" font-weight="700">
          {{ roleOf(r.key) }}
        </text>
      </g>

      <!-- 流动的数据包 -->
      <g v-if="flow" :transform="`translate(${flow.x}, ${flow.y})`" style="transition: transform .5s ease">
        <circle r="14" fill="#e8a13a" stroke="#c9821f" stroke-width="2" />
        <text y="4" text-anchor="middle" font-size="10" fill="#fff" font-weight="700">{{ flow.data }}</text>
      </g>

      <defs>
        <marker id="rt-arrow" markerWidth="9" markerHeight="9" refX="8" refY="3" orient="auto">
          <path d="M0,0 L8,3 L0,6 z" fill="#3b6ef6" />
        </marker>
      </defs>
    </svg>

    <el-row :gutter="16">
      <el-col :span="14">
        <div class="panel-title">微操作序列</div>
        <div class="uop-list">
          <div v-for="(u, i) in uops" :key="i" class="uop-item" :class="{ done: i < uopIndex, cur: i === uopIndex }">
            <span class="uop-no">{{ i + 1 }}</span>
            <code>{{ u.text }}</code>
            <span class="uop-note small muted">{{ u.note }}</span>
          </div>
        </div>
      </el-col>
      <el-col :span="10">
        <div class="panel-title">当前控制信号</div>
        <div class="signal-row">
          <span v-for="(s, i) in signals" :key="i" class="sig-chip" :class="{ on: s.on }">{{ s.name }}</span>
        </div>
        <el-divider />
        <div class="panel-title">要点</div>
        <ul class="rules">
          <li>同一节拍内<b>只能有一个部件向总线输出</b>数据，否则发生冲突</li>
          <li>寄存器输入/输出由控制信号（如 PC<sub>out</sub>、MAR<sub>in</sub>）控制</li>
          <li>取指周期是<b>所有指令公共</b>的第一步，之后进入执行周期</li>
        </ul>
      </el-col>
    </el-row>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> 当前节拍参与传输的部件</span>
      <span><i class="dot" style="background:#22a06b"></i> 数据输出到总线（out）</span>
      <span><i class="dot" style="background:#e05252"></i> 从总线读入（in）</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const regs = [
  { key: 'pc', name: 'PC', side: 'up', x: 110, y: 70 },
  { key: 'mar', name: 'MAR', side: 'up', x: 250, y: 70 },
  { key: 'mdr', name: 'MDR', side: 'up', x: 390, y: 70 },
  { key: 'ir', name: 'IR', side: 'up', x: 530, y: 70 },
  { key: 'acc', name: 'ACC', side: 'down', x: 150, y: 260 },
  { key: 'alu', name: 'ALU', side: 'down', x: 350, y: 260 },
  { key: 'mem', name: '主存 M', side: 'down', x: 560, y: 260 }
]

const uops = [
  { text: '(PC) → MAR', note: 'PCout, MARin，发出读信号', from: 'pc', to: 'mar', data: '200', set: { mar: '200' }, signals: ['PCout', 'MARin'] },
  { text: 'M(MAR) → MDR', note: '存储器按 MAR 地址读出内容到 MDR', from: 'mem', to: 'mdr', data: 'LDA', set: { mdr: 'LDA 300' }, signals: ['Read', 'MDRin'] },
  { text: '(MDR) → IR', note: 'MDRout, IRin，指令进入指令寄存器', from: 'mdr', to: 'ir', data: 'LDA', set: { ir: 'LDA 300' }, signals: ['MDRout', 'IRin'] },
  { text: '(PC) + 1 → PC', note: 'ALU 完成 PC 自增，为取下一条指令做准备', from: 'alu', to: 'pc', data: '201', set: { pc: '201' }, signals: ['PCin', 'ALUout'] },
  { text: 'OP(IR) → 控制单元译码', note: '识别出操作码为 LDA（取数）', from: 'ir', to: 'alu', data: '译码', set: {}, signals: ['IRout'] },
  { text: 'Ad(IR) → MAR', note: '形式地址 300 送入 MAR，进入执行周期', from: 'ir', to: 'mar', data: '300', set: { mar: '300' }, signals: ['IRout', 'MARin'] },
  { text: 'M(MAR) → MDR', note: '按地址 300 读出操作数', from: 'mem', to: 'mdr', data: '08', set: { mdr: '08' }, signals: ['Read', 'MDRin'] },
  { text: '(MDR) → ACC', note: '操作数送入累加器，执行周期结束', from: 'mdr', to: 'acc', data: '08', set: { acc: '08' }, signals: ['MDRout', 'ACCin'] }
]

const steps = computed(() => {
  const out = []
  const vals = { pc: '200', mar: '—', mdr: '—', ir: '—', acc: '—' }
  out.push({
    uopIndex: -1, values: { ...vals }, from: null, to: null, data: '',
    signals: [], desc: '初始状态：PC = 200，其余寄存器待写入'
  })
  uops.forEach((u, i) => {
    Object.assign(vals, u.set)
    out.push({
      uopIndex: i, values: { ...vals }, from: u.from, to: u.to, data: u.data,
      signals: u.signals,
      desc: `第 ${i + 1} 拍：${u.text} —— ${u.note}`
    })
  })
  out.push({
    uopIndex: uops.length, values: { ...vals }, from: null, to: null, data: '',
    signals: [], desc: '一条指令执行完毕，控制器重新开始取指周期'
  })
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const values = computed(() => cur.value.values || {})
const uopIndex = computed(() => cur.value.uopIndex ?? -1)

function roleOf(key) {
  if (cur.value.from === key) return 'out'
  if (cur.value.to === key) return 'in'
  return ''
}
function isActive(key) {
  return cur.value.from === key || cur.value.to === key
}

const signals = computed(() => {
  const all = ['PCout', 'MARin', 'MDRin', 'MDRout', 'IRin', 'IRout', 'PCin', 'ALUout', 'ACCin', 'Read']
  const on = cur.value.signals || []
  return all.map(s => ({ name: s, on: on.includes(s) }))
})

const flow = computed(() => {
  if (!cur.value.from || !cur.value.to) return null
  const f = regs.find(r => r.key === cur.value.from)
  const t = regs.find(r => r.key === cur.value.to)
  if (!f || !t) return null
  return {
    x: (f.x + t.x) / 2,
    y: (f.y + t.y) / 2 > 165 ? Math.max(f.y, t.y) - 60 : 165,
    data: cur.value.data
  }
})
</script>

<style scoped>
.rt-svg { background: #fbfcff; border-radius: 8px; display: block; margin-bottom: 12px; }
.panel-title { font-size: 13px; font-weight: 600; margin-bottom: 8px; color: var(--text-2); }
.uop-list { display: flex; flex-direction: column; gap: 4px; }
.uop-item {
  display: flex; align-items: center; gap: 10px; padding: 6px 10px; border-radius: 6px;
  border: 1px solid var(--border); background: #fff; font-size: 12px;
}
.uop-item.done { background: #f7f9fc; color: var(--text-3); }
.uop-item.cur { border-color: var(--brand); background: var(--brand-light); }
.uop-no { width: 20px; height: 20px; line-height: 20px; text-align: center; border-radius: 50%; background: #eef3ff; color: var(--brand); font-size: 11px; font-weight: 700; flex-shrink: 0; }
.uop-item code { font-size: 12px; font-weight: 600; flex-shrink: 0; }
.uop-note { margin-left: auto; }
.signal-row { display: flex; gap: 6px; flex-wrap: wrap; }
.sig-chip {
  padding: 3px 8px; border-radius: 4px; border: 1px solid var(--border);
  background: #f7f9fc; color: var(--text-3); font-size: 11px;
}
.sig-chip.on { background: #dcf3e7; border-color: var(--success); color: #176b48; font-weight: 700; }
.rules { padding-left: 18px; margin: 0; }
.rules li { font-size: 12px; line-height: 1.9; color: var(--text-2); }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
