<template>
  <VisFrame :title="`指令流水线 · ${hazard ? '存在数据冒险' : '理想流水线'}`" desc="五级流水：IF 取指 → ID 译码 → EX 执行 → MEM 访存 → WB 写回" :player="player" :status-text="statusText" back-to="/knowledge/18">
    <template #extra>
      <span class="small muted">指令数</span>
      <el-input-number v-model="instCount" size="small" :min="3" :max="8" style="width:90px" @change="player.reset()" />
      <el-checkbox v-model="hazard" size="small" @change="player.reset()">数据冒险</el-checkbox>
      <el-button size="small" plain @click="player.reset()">重播</el-button>
    </template>

    <!-- 时空图 -->
    <div class="pt-wrap">
      <table class="ptime">
        <thead>
          <tr>
            <th class="col-inst">指令</th>
            <th v-for="c in cycles" :key="c">C{{ c }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(inst, i) in instructions" :key="i">
            <td class="col-inst"><b>{{ inst.name }}</b></td>
            <td v-for="c in cycles" :key="c">
              <span v-if="cellOf(i, c)" class="cell" :class="cellClass(cellOf(i, c))">{{ cellOf(i, c) }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 流水线阶段示意 -->
    <div class="stage-row">
      <div v-for="(s, i) in stages" :key="s.key" class="stage-box" :class="{ active: activeStages.includes(i) }">
        <div class="stage-key">{{ s.key }}</div>
        <div class="stage-name">{{ s.name }}</div>
        <div class="stage-inst small">{{ stageInst[i] || '—' }}</div>
      </div>
    </div>

    <el-row :gutter="16" style="margin-top:14px">
      <el-col :span="12">
        <div class="panel-title">性能统计</div>
        <div class="stat-row">
          <div class="stat-box"><div class="sv small-sv">{{ cycles.length }}</div><div class="sl">所需时钟周期</div></div>
          <div class="stat-box"><div class="sv small-sv">{{ instCount }}</div><div class="sl">指令条数</div></div>
          <div class="stat-box"><div class="sv small-sv">{{ cpi }}</div><div class="sl">实际 CPI</div></div>
          <div class="stat-box"><div class="sv small-sv">{{ speedup }}</div><div class="sl">加速比</div></div>
        </div>
        <div class="formula-box">
          <code>k 级流水线执行 n 条指令：周期数 = k + (n − 1) + 气泡周期 = {{ stages.length }} + ({{ instCount }} − 1) + {{ bubbleCount }} = {{ totalCycles }}</code>
          <code>加速比 = n·k / 总周期数 = {{ instCount }}×{{ stages.length }} / {{ totalCycles }} = {{ speedup }}</code>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="panel-title">三种冒险（Hazard）</div>
        <ul class="rules">
          <li><b>结构冒险</b>：多条指令同时争用同一硬件资源 → 增加资源或插入停顿</li>
          <li><b>数据冒险</b>：后继指令需要前一条指令的结果 → <b>转发（旁路）技术</b>或插入气泡</li>
          <li><b>控制冒险</b>：分支指令改变 PC 流向 → 分支预测、延迟分支</li>
        </ul>
        <el-alert v-if="hazard && stallCycle > 0" type="warning" :closable="false" show-icon style="margin-top:8px">
          I2 需要 I1 的运算结果，在第 {{ stallCycle }} 周期插入气泡（stall），流水线暂停一个周期。
        </el-alert>
      </el-col>
    </el-row>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> IF 取指</span>
      <span><i class="dot" style="background:#22a06b"></i> ID 译码</span>
      <span><i class="dot" style="background:#e8a13a"></i> EX 执行</span>
      <span><i class="dot" style="background:#8b5cf6"></i> MEM 访存</span>
      <span><i class="dot" style="background:#e05252"></i> WB 写回 / 气泡</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const stages = [
  { key: 'IF', name: '取指' },
  { key: 'ID', name: '译码' },
  { key: 'EX', name: '执行' },
  { key: 'MEM', name: '访存' },
  { key: 'WB', name: '写回' }
]
const instCount = ref(6)
const hazard = ref(false)

const instructions = computed(() =>
  Array.from({ length: instCount.value }, (_, i) => ({ name: `I${i + 1}` }))
)

// 每条指令进入各阶段的周期：startCycle[i] = i（0-based），阶段 s 的周期 = i + s + 1（1-based）
const stallCycle = computed(() => (hazard.value ? 4 : 0))

const totalCycles = computed(() => stages.length + instCount.value - 1 + (hazard.value ? 1 : 0))
// 气泡（stall）周期数 = 实际周期 − 理想流水线的 k + n − 1。
// 注意别和 stallCycle 搞混：stallCycle 是「气泡插在第几个周期」，不是数量。
// 公式框曾直接用 k + n − 1 当分母，于是显示 6×5 / 10 = 2.73 —— 手算 30/10 明明是 3.00，
// 而上方「所需时钟周期」却写着 11，同一屏里两个数字对不上。
const bubbleCount = computed(() => totalCycles.value - (stages.length + instCount.value - 1))
const cycles = computed(() => Array.from({ length: totalCycles.value }, (_, i) => i + 1))

function entryCycle(instIdx, stageIdx) {
  // 指令 instIdx 在周期 (instIdx + stageIdx + 1) 处于 stageIdx
  let c = instIdx + stageIdx + 1
  if (hazard.value && instIdx >= 1 && c >= stallCycle.value) c += 1
  return c
}

const steps = computed(() => {
  const out = []
  for (let c = 1; c <= totalCycles.value; c++) {
    const active = []
    instructions.value.forEach((inst, i) => {
      stages.forEach((s, si) => {
        if (entryCycle(i, si) === c) active.push({ inst: i, stage: si })
      })
    })
    let desc = ''
    if (c === 1) desc = '第 1 周期：I1 进入取指阶段，流水线开始填充'
    else if (hazard.value && c === stallCycle.value) desc = `第 ${c} 周期：I2 需要 I1 的结果，插入气泡（bubble），流水线停顿`
    else if (c > instCount.value) desc = `第 ${c} 周期：无新指令进入，流水线逐步排空`
    else desc = `第 ${c} 周期：${active.map(a => `I${a.inst + 1} 处于 ${stages[a.stage].key}`).join('，') || '空闲'}`
    out.push({ cycle: c, active, desc })
  }
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const currentCycle = computed(() => cur.value.cycle || 1)

function cellOf(instIdx, c) {
  if (c > currentCycle.value) return null
  for (let si = 0; si < stages.length; si++) {
    if (entryCycle(instIdx, si) === c) return stages[si].key
  }
  if (hazard.value && c === stallCycle.value && instIdx >= 1 && c < entryCycle(instIdx, 0)) return null
  return null
}
function cellClass(key) {
  return 'c-' + key
}

const activeStages = computed(() => (cur.value.active || []).map(a => a.stage))
const stageInst = computed(() => {
  const arr = new Array(stages.length).fill('')
  ;(cur.value.active || []).forEach(a => { arr[a.stage] = `I${a.inst + 1}` })
  return arr
})

const cpi = computed(() => (totalCycles.value / instCount.value).toFixed(2))
const speedup = computed(() => ((instCount.value * stages.length) / totalCycles.value).toFixed(2))
</script>

<style scoped>
.panel-title { font-size: 13px; font-weight: 600; margin-bottom: 8px; color: var(--text-2); }
.pt-wrap { overflow-x: auto; }
.ptime { border-collapse: collapse; font-size: 12px; }
.ptime th, .ptime td { border: 1px solid var(--border); padding: 4px; text-align: center; min-width: 40px; height: 34px; }
.ptime th { background: #f7f9fc; }
.col-inst { width: 64px; background: #f7f9fc; }
.cell { display: block; width: 38px; line-height: 24px; border-radius: 4px; color: #fff; font-weight: 600; font-size: 11px; }
.c-IF { background: #3b6ef6; }
.c-ID { background: #22a06b; }
.c-EX { background: #e8a13a; }
.c-MEM { background: #8b5cf6; }
.c-WB { background: #e05252; }
.stage-row { display: flex; gap: 8px; margin-top: 14px; }
.stage-box {
  flex: 1; text-align: center; padding: 8px; border-radius: 8px;
  border: 1.5px solid var(--border); background: #fff; transition: all .2s;
}
.stage-box.active { border-color: var(--brand); background: var(--brand-light); }
.stage-key { font-weight: 700; font-size: 14px; color: var(--brand); }
.stage-name { font-size: 12px; color: var(--text-2); }
.stage-inst { color: var(--text-3); margin-top: 2px; }
.stat-row { display: flex; gap: 10px; flex-wrap: wrap; }
.stat-box { flex: 1; min-width: 90px; background: #fbfcff; border: 1px solid var(--border); border-radius: 8px; padding: 8px; text-align: center; }
.sv { font-size: 18px; font-weight: 700; color: var(--brand); }
.sl { font-size: 11px; color: var(--text-2); margin-top: 2px; }
.formula-box { margin-top: 10px; }
.formula-box code { display: block; background: #f2f4f8; padding: 6px 10px; border-radius: 6px; font-size: 12px; margin-bottom: 6px; }
.rules { padding-left: 18px; margin: 0; }
.rules li { font-size: 12px; line-height: 1.9; color: var(--text-2); }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
