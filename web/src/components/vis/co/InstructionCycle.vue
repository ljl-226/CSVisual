<template>
  <VisFrame title="指令周期与微程序 · 取指 / 间址 / 执行 / 中断" desc="一个指令周期由若干机器周期（取指、间址、执行、中断）组成，每个机器周期又含若干节拍；每个节拍对应一条微指令，发出若干微命令完成数据传送" :player="player" :status-text="statusText" back-to="/knowledge/54">
    <template #extra>
      <el-select v-model="inst" size="small" style="width:110px" @change="player.reset()">
        <el-option value="LDA" label="LDA 取数" />
        <el-option value="ADD" label="ADD 加法" />
        <el-option value="STA" label="STA 存数" />
        <el-option value="JMP" label="JMP 转移" />
      </el-select>
      <el-select v-model="addrMode" size="small" style="width:108px" @change="player.reset()">
        <el-option value="dir" label="直接寻址" />
        <el-option value="ind" label="间接寻址" />
      </el-select>
      <el-select v-model="irq" size="small" style="width:116px" @change="player.reset()">
        <el-option :value="0" label="无中断请求" />
        <el-option :value="1" label="有中断请求" />
      </el-select>
      <el-button size="small" plain @click="player.reset()">重置</el-button>
    </template>
    <div class="ic-wrap">
      <svg :width="W" :height="H" class="ic-svg">
        <g v-for="(n, k) in NODES" :key="k">
          <rect :x="n.x" :y="n.y" :width="n.w" :height="n.h" rx="6"
                :fill="cur.active.includes(k) ? '#eef3ff' : '#fff'"
                :stroke="cur.active.includes(k) ? '#3b6ef6' : '#dfe4ec'" stroke-width="1.6" />
          <text :x="n.x + 8" :y="n.y + 16" font-size="11" font-weight="700" :fill="cur.active.includes(k) ? '#3b6ef6' : '#1f2733'">{{ n.t }}</text>
          <text v-for="(line, li) in nodeText(k)" :key="li" :x="n.x + 8" :y="n.y + 32 + li * 15" font-size="10" fill="#5a6474">{{ line }}</text>
        </g>

        <!-- 当前节拍的数据流 -->
        <g v-if="cur.flow">
          <line :x1="cur.flow.x1" :y1="cur.flow.y1" :x2="cur.flow.x2" :y2="cur.flow.y2" stroke="#3b6ef6" stroke-width="2.4" marker-end="url(#ic-a)" />
          <text :x="(cur.flow.x1 + cur.flow.x2) / 2" :y="(cur.flow.y1 + cur.flow.y2) / 2 - 5" text-anchor="middle" font-size="10.5" font-weight="700" fill="#3b6ef6">{{ cur.flowLabel }}</text>
        </g>
        <g v-if="cur.flow2">
          <line :x1="cur.flow2.x1" :y1="cur.flow2.y1" :x2="cur.flow2.x2" :y2="cur.flow2.y2" stroke="#22a06b" stroke-width="2.4" stroke-dasharray="5,3" marker-end="url(#ic-a2)" />
          <text :x="(cur.flow2.x1 + cur.flow2.x2) / 2" :y="(cur.flow2.y1 + cur.flow2.y2) / 2 - 5" text-anchor="middle" font-size="10.5" font-weight="700" fill="#22a06b">{{ cur.flow2Label }}</text>
        </g>
        <defs><marker id="ic-a" markerWidth="9" markerHeight="9" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#3b6ef6" /></marker><marker id="ic-a2" markerWidth="9" markerHeight="9" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#22a06b" /></marker></defs>
      </svg>
      <div class="ic-panel">
        <div class="info-row"><span>当前机器周期</span><b style="color:var(--brand)">{{ cur.phase || '—' }}</b></div>
        <div class="info-row"><span>当前节拍</span><b>{{ cur.beat || '—' }}</b></div>
        <div class="info-row"><span>本拍微操作</span><b style="color:var(--success)">{{ cur.microOp || '—' }}</b></div>
        <el-divider />
        <div class="tbl">
          <div class="tbl-head"><span>微地址</span><span>微指令（微命令）</span></div>
          <div v-for="(m, i) in cur.micro" :key="i" class="tbl-row" :class="{ active: i === cur.microNo }">
            <span>{{ m.addr }}</span><span>{{ m.cmd }}</span>
          </div>
          <div v-if="!cur.micro.length" class="tbl-row"><span>—</span><span>（尚未开始）</span></div>
        </div>
        <p class="tip small muted">
          考点：① <b>取指周期</b>是所有指令公有的：PC → MAR → 存储器 → MDR → IR，同时 PC+1；
          ② 只有<b>间接寻址</b>的指令才有间址周期；③ 中断周期只在有中断请求且开中断时插入，负责<b>断点（PC 内容）入栈</b>并转向中断服务程序；
          ④ 一条机器指令对应一段微程序，微指令存放在<b>控制存储器</b>中，逐条读出并发出微命令。
        </p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> 本拍参与的数据流（实线箭头）</span>
      <span><i class="dot" style="background:#22a06b"></i> 本拍并行完成的第二个微操作（虚线）</span>
      <span><i class="dot" style="background:#e8a13a"></i> 当前选中的部件</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'
const W = 660
const H = 262
const X = 8          // 指令中的形式地址
const INST_ADDR = 3  // 指令所在主存单元
const NODES = {
  PC: { x: 14, y: 16, w: 104, h: 40, t: 'PC 程序计数器' }, MAR: { x: 14, y: 74, w: 104, h: 40, t: 'MAR 地址寄存器' },
  MDR: { x: 14, y: 132, w: 104, h: 40, t: 'MDR 数据寄存器' }, IR: { x: 14, y: 190, w: 104, h: 56, t: 'IR 指令寄存器' },
  MEM: { x: 226, y: 16, w: 180, h: 116, t: '主存储器' }, CM: { x: 226, y: 150, w: 180, h: 96, t: '控制存储器（微程序）' },
  ACC: { x: 526, y: 16, w: 120, h: 40, t: 'ACC 累加器' }, ALU: { x: 526, y: 74, w: 120, h: 40, t: 'ALU 算术逻辑单元' },
  CU: { x: 526, y: 132, w: 120, h: 40, t: 'CU 控制单元' }, SP: { x: 526, y: 190, w: 120, h: 56, t: 'SP 栈顶指针' }
}
const inst = ref('LDA')
const addrMode = ref('dir')
const irq = ref(1)
// 计算两个部件边框之间的连线端点（避免箭头穿过方框）
function edge(a, b) {
  const A = NODES[a], B = NODES[b]
  const ax = A.x + A.w / 2, ay = A.y + A.h / 2, bx = B.x + B.w / 2, by = B.y + B.h / 2
  const dx = bx - ax, dy = by - ay
  const cut = (r, sign) => {
    const sx = dx === 0 ? Infinity : (r.w / 2 + 3) / Math.abs(dx)
    const sy = dy === 0 ? Infinity : (r.h / 2 + 3) / Math.abs(dy)
    const s = Math.min(sx, sy)
    return { x: (sign > 0 ? ax : bx) + sign * dx * s, y: (sign > 0 ? ay : by) + sign * dy * s }
  }
  const p = cut(A, 1), q = cut(B, -1)
  return { x1: p.x, y1: p.y, x2: q.x, y2: q.y }  // 端点落在方框边框上
}
const steps = computed(() => {
  const out = []
  const ind = addrMode.value === 'ind'
  const mem = { [INST_ADDR]: `${inst.value} 指令字`, [X]: ind ? 12 : 20, 12: 20, 99: '空闲栈单元', 100: '空闲栈单元' }
  const regs = { PC: INST_ADDR, MAR: 0, MDR: 0, IR: '—', ACC: 8, SP: 100 }
  const micro = []
  let microNo = -1
  function snap(desc, extra = {}) {
    out.push({ regs: { ...regs }, mem: { ...mem }, micro: micro.map(m => ({ ...m })), microNo, phase: '', beat: '', microOp: '', flow: null, flow2: null, active: [], ...extra, desc })
  }
  // 一个节拍 = 一条微指令：记录微命令并画出本拍的数据流
  function beat(phase, t, op, nodes, f, f2) {
    microNo++
    micro.push({ addr: 'μ' + String(microNo).padStart(2, '0'), cmd: op })
    snap(`${phase} · ${t}：${op}`, { phase, beat: t, microOp: op, active: nodes,
      flow: f ? { ...edge(f[0], f[1]) } : null, flowLabel: f ? f[2] : '',
      flow2: f2 ? { ...edge(f2[0], f2[1]) } : null, flow2Label: f2 ? f2[2] : '' })
  }
  snap(`初始：${inst.value} 指令存放在主存 ${INST_ADDR} 号单元（${addrMode.value === 'ind' ? '间接' : '直接'}寻址，形式地址 X = ${X}），(PC) = ${INST_ADDR}，(ACC) = ${regs.ACC}，(SP) = ${regs.SP}`)
  // ① 取指周期（所有指令公有）
  regs.MAR = regs.PC
  beat('取指周期', 'T0', '(PC) → MAR；1 → R（向主存发读命令）', ['PC', 'MAR'], ['PC', 'MAR', '(PC)→MAR'])
  regs.MDR = `${inst.value} 指令字`
  regs.PC = INST_ADDR + 1
  beat('取指周期', 'T1', 'M(MAR) → MDR；(PC) + 1 → PC', ['MEM', 'MDR', 'PC', 'ALU'], ['MEM', 'MDR', 'M(MAR)→MDR'], ['PC', 'ALU', '(PC)+1→PC'])
  regs.IR = `${inst.value} X=${X}`
  beat('取指周期', 'T2', '(MDR) → IR；OP(IR) → CU 译码', ['MDR', 'IR', 'CU'], ['MDR', 'IR', '(MDR)→IR'])
  // ② 间址周期（仅间接寻址指令）
  if (ind) {
    regs.MAR = X
    beat('间址周期', 'T0', 'Ad(IR) → MAR；1 → R', ['IR', 'MAR'], ['IR', 'MAR', 'Ad(IR)→MAR'])
    regs.MDR = 12
    beat('间址周期', 'T1', 'M(MAR) → MDR（取到的是有效地址 12）', ['MEM', 'MDR'], ['MEM', 'MDR', 'M(MAR)→MDR'])
    beat('间址周期', 'T2', '(MDR) → Ad(IR)：把形式地址改写为有效地址 12', ['MDR', 'IR'], ['MDR', 'IR', '(MDR)→Ad(IR)'])
  }
  // ③ 执行周期（随指令而异）
  const ea = ind ? 12 : X
  if (inst.value === 'JMP') {
    regs.PC = ea
    beat('执行周期', 'T0', `Ad(IR) → PC：把转移目标地址 ${ea} 送入 PC，下一条指令从 ${ea} 号单元取`, ['IR', 'PC'], ['IR', 'PC', 'Ad(IR)→PC'])
  } else if (inst.value === 'STA') {
    regs.MAR = ea
    beat('执行周期', 'T0', 'Ad(IR) → MAR；1 → W（向主存发写命令）', ['IR', 'MAR'], ['IR', 'MAR', 'Ad(IR)→MAR'])
    regs.MDR = regs.ACC
    beat('执行周期', 'T1', '(ACC) → MDR', ['ACC', 'MDR'], ['ACC', 'MDR', '(ACC)→MDR'])
    mem[ea] = regs.ACC
    beat('执行周期', 'T2', `(MDR) → M(MAR)：把 ${regs.ACC} 写入主存 ${ea} 号单元`, ['MDR', 'MEM'], ['MDR', 'MEM', '(MDR)→M(MAR)'])
  } else {
    regs.MAR = ea
    beat('执行周期', 'T0', 'Ad(IR) → MAR；1 → R', ['IR', 'MAR'], ['IR', 'MAR', 'Ad(IR)→MAR'])
    regs.MDR = 20
    beat('执行周期', 'T1', `M(MAR) → MDR：从 ${ea} 号单元读出操作数 20`, ['MEM', 'MDR'], ['MEM', 'MDR', 'M(MAR)→MDR'])
    if (inst.value === 'LDA') {
      regs.ACC = 20
      beat('执行周期', 'T2', '(MDR) → ACC：操作数送入累加器', ['MDR', 'ACC'], ['MDR', 'ACC', '(MDR)→ACC'])
    } else {
      regs.ACC = regs.ACC + 20
      beat('执行周期', 'T2', `(ACC) + (MDR) → ACC = ${regs.ACC}：ALU 完成加法并送回累加器`, ['MDR', 'ALU', 'ACC'], ['MDR', 'ALU', '(MDR)→ALU'], ['ALU', 'ACC', '(ALU)→ACC'])
    }
  }
  // ④ 中断周期（执行周期末尾，有中断请求且允许中断时插入）
  if (irq.value === 1) {
    regs.SP = 99; regs.MAR = 99
    beat('中断周期', 'T0', '(SP) − 1 → MAR；1 → W：栈顶下移一个单元准备保存断点', ['SP', 'MAR'], ['SP', 'MAR', '(SP)-1→MAR'])
    regs.MDR = regs.PC
    beat('中断周期', 'T1', `(PC) → MDR：把断点 ${regs.PC} 送入 MDR 准备入栈`, ['PC', 'MDR'], ['PC', 'MDR', '(PC)→MDR'])
    mem[99] = `断点 ${regs.PC}`
    beat('中断周期', 'T2', '(MDR) → M(MAR)：断点压栈保存；中断向量地址 → PC，转向中断服务程序', ['MDR', 'MEM'], ['MDR', 'MEM', '(MDR)→M(MAR)'])
  }
  snap(`指令周期结束：${inst.value} 执行完毕，(ACC) = ${regs.ACC}，(PC) = ${regs.PC}${irq.value === 1 ? '（已转入中断服务程序入口）' : ''}。本条指令共执行 ${micro.length} 条微指令`)
  return out
})
const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
function nodeText(k) {
  const c = cur.value
  const m = c.micro[c.microNo]
  if (k === 'MEM') return [`M(${INST_ADDR}) = ${c.mem[INST_ADDR]}`, `M(${X}) = ${c.mem[X]}`, `M(12) = ${c.mem[12]}`, `M(99) = ${c.mem[99]}`]
  if (k === 'CM') return [`当前微地址：${m ? m.addr : '—'}`, `微命令：${m ? m.cmd : '—'}`]
  if (k === 'IR') return [`(IR) =`, `${c.regs.IR}`]
  const t = { PC: `(${k}) = ${c.regs.PC}`, MAR: `(${k}) = ${c.regs.MAR}`, MDR: `(${k}) = ${c.regs.MDR}`, ACC: `(${k}) = ${c.regs.ACC}`, SP: `(${k}) = ${c.regs.SP}`, ALU: '完成算术/逻辑运算', CU: '译码并发出微命令' }[k]
  return t ? [t] : []
}
</script>

<style scoped>
.ic-wrap { display: flex; gap: 18px; align-items: flex-start; flex-wrap: wrap; }
.ic-svg { background: #fbfcff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.ic-panel { flex: 1; min-width: 280px; }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.tbl { font-size: 12px; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
.tbl-head { display: grid; grid-template-columns: 0.7fr 2.3fr; background: #f6f8fb; padding: 7px 10px; font-weight: 600; }
.tbl-row { display: grid; grid-template-columns: 0.7fr 2.3fr; padding: 6px 10px; border-top: 1px solid #f0f2f6; }
.tbl-row.active { background: var(--brand-light); color: var(--brand); font-weight: 600; }
.tip { margin-top: 10px; line-height: 1.8; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
