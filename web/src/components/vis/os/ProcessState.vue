<template>
  <VisFrame title="进程状态与转换 · 五态模型" desc="创建 → 就绪 → 运行 → 阻塞 → 终止，由调度与事件驱动状态迁移" :player="player" :status-text="statusText" back-to="/knowledge/14">
    <template #extra>
      <el-button size="small" plain @click="player.reset()">重播</el-button>
    </template>

    <svg width="700" height="330" class="ps-svg">
      <!-- 转换边 -->
      <g v-for="(e, i) in transitionList" :key="'t' + i">
        <path :d="e.d" fill="none" :stroke="e.active ? '#3b6ef6' : '#dde3ec'" :stroke-width="e.active ? 3 : 1.8" marker-end="url(#ps-arrow)" />
        <text :x="e.lx" :y="e.ly" text-anchor="middle" font-size="11" :fill="e.active ? '#3b6ef6' : '#8b95a3'" font-weight="e.active ? 700 : 400">
          {{ e.label }}
        </text>
      </g>

      <!-- 状态结点 -->
      <g v-for="s in states" :key="s.name">
        <rect
          :x="s.x - 52" :y="s.y - 24" width="104" height="48" rx="24"
          :fill="s.name === currentState ? '#3b6ef6' : '#fff'"
          :stroke="s.name === currentState ? '#3b6ef6' : '#c8d3e6'"
          stroke-width="2"
        />
        <text :x="s.x" :y="s.y + 5" text-anchor="middle" font-size="13" font-weight="600"
          :fill="s.name === currentState ? '#fff' : '#1f2733'">{{ s.name }}</text>
      </g>
      <defs>
        <marker id="ps-arrow" markerWidth="9" markerHeight="9" refX="8" refY="3" orient="auto">
          <path d="M0,0 L8,3 L0,6 z" fill="#8b95a3" />
        </marker>
      </defs>
    </svg>

    <div class="ps-panel">
      <div class="stat-row">
        <div class="stat-box">
          <div class="sv" style="font-size:16px">{{ currentState }}</div>
          <div class="sl">当前状态</div>
        </div>
        <div class="stat-box">
          <div class="sv" style="font-size:16px">{{ visited.length }}</div>
          <div class="sl">已发生转换</div>
        </div>
        <div class="stat-box">
          <div class="sv" style="font-size:16px">{{ trigger }}</div>
          <div class="sl">本次触发事件</div>
        </div>
      </div>
      <el-divider />
      <div class="panel-title">转换规则</div>
      <ul class="rules">
        <li><b>就绪 → 运行</b>：被调度程序选中，分配 CPU</li>
        <li><b>运行 → 就绪</b>：时间片用完，或被更高优先级进程抢占</li>
        <li><b>运行 → 阻塞</b>：等待某事件（I/O 请求、申请资源），进程<b>主动</b>行为</li>
        <li><b>阻塞 → 就绪</b>：等待的事件发生，由其他进程<b>被动</b>唤醒</li>
        <li><b>阻塞态不能直接变为运行态</b>，必须先回到就绪态排队</li>
      </ul>
      <div class="tip small muted">
        提示：进程是<b>动态</b>的，程序是<b>静态</b>的；PCB 是进程存在的唯一标志。
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> 当前状态 / 本次转换</span>
      <span><i class="dot" style="background:#fff"></i> 其他状态</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const states = [
  { name: '创建态', x: 90, y: 60 },
  { name: '就绪态', x: 250, y: 165 },
  { name: '运行态', x: 430, y: 60 },
  { name: '阻塞态', x: 430, y: 270 },
  { name: '终止态', x: 630, y: 165 }
]

const transitions = [
  { id: 't1', from: '创建态', to: '就绪态', label: '提交 / 创建完成', lx: 150, ly: 100, d: 'M120,80 Q170,100 200,140' },
  { id: 't2', from: '就绪态', to: '运行态', label: '被调度（分派CPU）', lx: 330, ly: 90, d: 'M295,148 Q340,90 382,72' },
  { id: 't3', from: '运行态', to: '就绪态', label: '时间片到 / 被抢占', lx: 330, ly: 150, d: 'M382,80 Q340,150 295,152' },
  { id: 't4', from: '运行态', to: '阻塞态', label: '等待事件（I/O请求）', lx: 470, ly: 175, d: 'M430,84 L430,246' },
  { id: 't5', from: '阻塞态', to: '就绪态', label: '等待事件发生', lx: 300, ly: 275, d: 'M378,272 Q300,265 302,178' },
  { id: 't6', from: '运行态', to: '终止态', label: '执行完成 / 被撤销', lx: 530, ly: 95, d: 'M480,70 Q540,90 580,145' }
]

const script = [
  { state: '创建态', edge: null, trigger: '用户提交作业', desc: '进程正在被创建：分配 PID、建立 PCB、分配资源，尚未进入就绪队列' },
  { state: '就绪态', edge: 't1', trigger: '创建完成', desc: '创建完成进入就绪态：万事俱备，只差 CPU' },
  { state: '运行态', edge: 't2', trigger: '被调度', desc: '调度程序选中该进程，分配 CPU，进程开始执行指令' },
  { state: '阻塞态', edge: 't4', trigger: '发起 I/O 请求', desc: '运行过程中需要等待 I/O 完成 → 主动放弃 CPU 进入阻塞态（注意：阻塞是进程的主动行为）' },
  { state: '就绪态', edge: 't5', trigger: 'I/O 完成中断', desc: 'I/O 完成产生中断，操作系统唤醒进程 → 阻塞态先转为就绪态，不能直接回到运行态' },
  { state: '运行态', edge: 't2', trigger: '再次被调度', desc: '重新排队后被调度，继续从断点处执行' },
  { state: '就绪态', edge: 't3', trigger: '时间片用完', desc: '时间片耗尽，时钟中断触发，进程被剥夺 CPU 回到就绪队列末尾' },
  { state: '运行态', edge: 't2', trigger: '再次被调度', desc: '时间片轮转：下一次调度再次获得 CPU' },
  { state: '终止态', edge: 't6', trigger: '进程执行完毕', desc: '进程运行结束（或异常终止），回收资源与 PCB，进入终止态' }
]

const steps = computed(() => script.map((s, i) => ({ ...s, visited: i })))

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const currentState = computed(() => cur.value.state)
const trigger = computed(() => cur.value.trigger)
const visited = computed(() => steps.value.slice(0, (player.idx.value || 0) + 1))

const transitionList = computed(() =>
  transitions.map(t => ({ ...t, active: t.id === cur.value.edge }))
)
</script>

<style scoped>
.ps-svg { background: #fbfcff; border-radius: 8px; display: block; margin-bottom: 14px; }
.ps-panel { }
.stat-row { display: flex; gap: 12px; flex-wrap: wrap; }
.stat-box { flex: 1; min-width: 130px; background: #fbfcff; border: 1px solid var(--border); border-radius: 8px; padding: 10px; text-align: center; }
.sv { font-weight: 700; color: var(--brand); }
.sl { font-size: 12px; color: var(--text-2); margin-top: 2px; }
.panel-title { font-size: 13px; font-weight: 600; margin-bottom: 6px; color: var(--text-2); }
.rules { padding-left: 18px; margin: 0; }
.rules li { font-size: 12px; line-height: 1.9; color: var(--text-2); }
.tip { margin-top: 10px; line-height: 1.8; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
