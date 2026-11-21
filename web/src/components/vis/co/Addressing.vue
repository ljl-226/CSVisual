<template>
  <VisFrame title="指令格式与寻址方式 · 有效地址 EA 的计算" desc="指令 = 操作码 OP + 寻址特征 Mod + 形式地址 A；不同寻址方式把 A 加工成有效地址 EA 的方式不同，访存次数也不同" :player="player" :status-text="statusText" back-to="/knowledge/52">
    <template #extra>
      <el-select v-model="inst" size="small" style="width:96px" @change="player.reset()">
        <el-option value="LDA" label="LDA 取数" /><el-option value="ADD" label="ADD 加法" /><el-option value="STA" label="STA 存数" /><el-option value="JMP" label="JMP 转移" />
      </el-select>
      <!-- 8 种方式顺序播放要看 24 步才轮得到变址，课堂上想单独讲某一种时直接选 -->
      <el-select v-model="modeSel" size="small" style="width:124px" @change="player.reset()">
        <el-option value="all" label="全部（依次演示）" />
        <el-option v-for="m in MODES" :key="m.key" :value="m.key" :label="m.name" />
      </el-select>
      <el-select v-model="ri" size="small" style="width:88px" @change="player.reset()">
        <el-option :value="0" label="R0" /><el-option :value="1" label="R1" />
      </el-select>
      <el-input v-model="aText" size="small" style="width:88px" placeholder="形式地址 A" />
      <el-button size="small" @click="applyA">应用</el-button>
      <el-button size="small" plain @click="resetAll">重置</el-button>
    </template>
    <div class="ad-wrap">
      <svg :width="W" :height="H" class="ad-svg">
        <defs>
          <marker id="ad-arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
            <path d="M0,0 L7,3 L0,6 Z" fill="#3b6ef6" />
          </marker>
        </defs>
        <!-- 指令字：OP | Mod | A（外框高度按内容算：标题 + 字段 + 注释，别让注释压到边框线上） -->
        <rect x="14" y="14" width="300" height="66" rx="8" fill="#fff" stroke="#dfe4ec" />
        <text x="24" y="32" font-size="12" font-weight="700" fill="#1f2733">指令字（16 位）：{{ inst }} · {{ cur.modeName }}</text>
        <rect x="24" y="38" width="76" height="20" rx="3" fill="#f2ecff" stroke="#d6ccf7" />
        <text x="62" y="52" text-anchor="middle" font-size="11" fill="#8b5cf6">{{ opCode }}</text>
        <rect x="104" y="38" width="60" height="20" rx="3" fill="#e6eeff" stroke="#cfe0ff" />
        <text x="134" y="52" text-anchor="middle" font-size="11" fill="#3b6ef6">{{ cur.modCode }}</text>
        <rect x="168" y="38" width="130" height="20" rx="3" fill="#fff3e0" stroke="#f5d6a8" />
        <text x="233" y="52" text-anchor="middle" font-size="11" fill="#a5701a">{{ aBin }}</text>
        <text x="233" y="74" text-anchor="middle" font-size="9" fill="#a5701a">形式地址 A 9 位 = {{ cur.A }}</text>
        <!-- CPU 寄存器：6 行 × 17 = 102，外框留够，最后一行才不会探出框外 -->
        <rect x="14" y="88" width="300" height="126" rx="8" fill="#fff" stroke="#dfe4ec" />
        <text x="24" y="106" font-size="12" font-weight="700" fill="#1f2733">CPU 寄存器（蓝色 = 参与本次 EA 计算）</text>
        <rect v-for="(r, i) in regRows" :key="r.n" x="24" :y="112 + i * 17" width="280" height="14" rx="3" :fill="cur.use.includes(r.n) ? '#eef3ff' : '#f7f9fc'" />
        <text v-for="(r, i) in regRows" :key="'rn' + i" x="32" :y="123 + i * 17" font-size="10.5" :fill="cur.use.includes(r.n) ? '#3b6ef6' : '#5a6474'">{{ r.n }} = {{ r.v }}</text>
        <!-- 主存：格高 32 才放得下「地址 + 内容」两行字，行距随之放到 42 -->
        <rect x="336" y="14" width="310" height="194" rx="8" fill="#fff" stroke="#dfe4ec" />
        <text x="346" y="32" font-size="12" font-weight="700" fill="#1f2733">主存（按字编址，示意 0~{{ MEM.length - 1 }} 号单元）</text>
        <rect v-for="(v, i) in MEM" :key="i" :x="346 + (i % 6) * 50" :y="42 + Math.floor(i / 6) * 42" width="44" height="32" rx="3" :fill="cur.hl.includes(i) ? (i === cur.ea ? '#e6eeff' : '#fff3e0') : '#fbfcff'" :stroke="cur.hl.includes(i) ? (i === cur.ea ? '#3b6ef6' : '#e8a13a') : '#eef1f6'" stroke-width="1.4" />
        <text v-for="(v, i) in MEM" :key="'a' + i" :x="368 + (i % 6) * 50" :y="54 + Math.floor(i / 6) * 42" text-anchor="middle" font-size="9" fill="#b6bfcc">{{ i }}</text>
        <text v-for="(v, i) in MEM" :key="'v' + i" :x="368 + (i % 6) * 50" :y="69 + Math.floor(i / 6) * 42" text-anchor="middle" font-size="10.5" :fill="cur.hl.includes(i) ? '#1f2733' : '#5a6474'">{{ v }}</text>
        <!-- EA 与 操作数 -->
        <rect x="14" y="222" width="190" height="46" rx="8" :fill="cur.stage === 'ea' ? '#eef3ff' : '#fbfcff'" :stroke="cur.stage === 'ea' ? '#3b6ef6' : '#dfe4ec'" />
        <text x="24" y="240" font-size="10.5" fill="#8b95a3">有效地址 EA</text>
        <text x="24" y="258" font-size="13" font-weight="700" fill="#3b6ef6">{{ cur.eaText }}</text>
        <rect x="214" y="222" width="190" height="46" rx="8" :fill="cur.stage === 'mem' ? '#f2ecff' : '#fbfcff'" :stroke="cur.stage === 'mem' ? '#8b5cf6' : '#dfe4ec'" />
        <text x="224" y="240" font-size="10.5" fill="#8b95a3">操作数（{{ inst }}）</text>
        <text x="224" y="258" font-size="13" font-weight="700" fill="#8b5cf6">{{ cur.operandText }}</text>
        <rect x="414" y="222" width="232" height="46" rx="8" fill="#fbfcff" stroke="#dfe4ec" />
        <text x="424" y="240" font-size="10.5" fill="#8b95a3">取操作数所需访存次数</text>
        <text x="424" y="258" font-size="13" font-weight="700" fill="#e8a13a">{{ cur.accesses }} 次（另有取指 1 次）</text>
        <!-- EA 计算通路：把「形式地址 / 寄存器 → 加工 → 有效地址」画成一条带箭头的链，
             文字讲「EA = (IX) + A」不如看一眼数据从哪来、在哪加工 -->
        <text x="14" y="288" font-size="11" font-weight="700" fill="#1f2733">EA 计算通路</text>
        <text v-if="!eaChain" x="120" y="288" font-size="10.5" fill="#8b95a3">（初始状态，尚未取指译码）</text>
        <template v-else>
          <rect v-for="(n, i) in eaChain.nodes" :key="'en' + i" :x="14 + i * ew" y="294" :width="ew - 26" height="24" rx="4"
                :fill="i === eaChain.nodes.length - 1 ? '#e6eeff' : '#f7f9fc'" :stroke="i === eaChain.nodes.length - 1 ? '#3b6ef6' : '#e3e8f0'" />
          <text v-for="(n, i) in eaChain.nodes" :key="'et' + i" :x="14 + i * ew + (ew - 26) / 2" y="310" text-anchor="middle"
                font-size="10.5" :fill="i === eaChain.nodes.length - 1 ? '#3b6ef6' : '#5a6474'">{{ n }}</text>
          <line v-for="(n, i) in eaChain.nodes" v-show="i > 0" :key="'el' + i" :x1="14 + (i - 1) * ew + ew - 26 + 3" y1="306"
                :x2="14 + i * ew - 6" y2="306" stroke="#3b6ef6" stroke-width="1.4" marker-end="url(#ad-arrow)" />
          <text v-for="(o, i) in eaChain.ops" v-show="o" :key="'eo' + i" :x="14 + (i + 1) * ew - 16" y="289" text-anchor="middle"
                font-size="9" fill="#e8a13a">{{ o }}</text>
        </template>
        <!-- 本步数据通路 -->
        <text x="14" y="340" font-size="11" font-weight="700" fill="#1f2733">本步数据通路</text>
        <rect v-for="(n, i) in cur.flow" :key="'f' + i" :x="14 + i * fw" y="346" :width="fw - 12" height="24" rx="4" fill="#e6eeff" stroke="#cfe0ff" />
        <text v-for="(n, i) in cur.flow" :key="'ft' + i" :x="14 + i * fw + (fw - 12) / 2" y="362" text-anchor="middle" font-size="10.5" fill="#3b6ef6">{{ n }}{{ i < cur.flow.length - 1 ? ' ▸' : '' }}</text>
      </svg>
      <div class="ad-panel">
        <div class="info-row"><span>当前寻址方式</span><b style="color:var(--brand)">{{ cur.modeName }}（Mod = {{ cur.modCode }}）</b></div>
        <div class="info-row"><span>形式地址 A</span><b>{{ cur.A }}</b></div>
        <div class="info-row"><span>有效地址 EA</span><b>{{ cur.ea === null ? '—（无需访存）' : cur.ea }}</b></div>
        <div class="info-row"><span>操作数</span><b style="color:#8b5cf6">{{ cur.operandText }}</b></div>
        <div class="info-row"><span>访存次数</span><b style="color:var(--warning)">{{ cur.accesses }}</b></div>
        <div class="tbl">
          <div class="tbl-head"><span>寻址方式</span><span>EA 计算</span><span>访存</span></div>
          <div v-for="m in MODES" :key="m.key" class="tbl-row" :class="{ active: m.key === cur.modeKey }"><span>{{ m.name }}</span><span>{{ m.formula }}</span><span>{{ m.acc }}</span></div>
        </div>
        <p class="tip small muted">考点：① 指令的<b>寻址特征</b>字段决定如何把形式地址加工成有效地址；② <b>立即</b>与<b>寄存器</b>寻址不访存，速度最快；③ <b>间接</b>寻址需两次访存；④ <b>相对</b>寻址利于程序浮动，<b>变址</b>利于数组循环，<b>基址</b>利于多道程序重定位。</p>
      </div>
    </div>
    <template #legend>
      <span><i class="dot" style="background:#8b5cf6"></i> 操作码 OP</span>
      <span><i class="dot" style="background:#3b6ef6"></i> 寻址特征 Mod / 有效地址单元</span>
      <span><i class="dot" style="background:#e8a13a"></i> 形式地址 A / 一级间址单元</span>
      <span><i class="dot" style="background:#22a06b"></i> 参与 EA 计算的寄存器</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'
const W = 660
const H = 376
// 主存示意；8 号单元存放"指针"20，用于间接寻址演示
const MEM = [100, 200, 300, 400, 500, 600, 700, 800, 20, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 900, 2200, 2300, 2400]
const REG = [5, 12]
const IX = 6    // 变址寄存器
const BR = 2    // 基址寄存器
const PC0 = 3   // 本条指令所在地址，取指后 PC 自动 +1 → 4
const OPC = { LDA: '0001', ADD: '0010', STA: '0100', JMP: '0011' }
const MODES = [
  { key: 'imm', code: '000', name: '立即寻址', formula: '操作数 = A', acc: 0 },
  { key: 'dir', code: '001', name: '直接寻址', formula: 'EA = A', acc: 1 },
  { key: 'ind', code: '010', name: '间接寻址', formula: 'EA = (A)', acc: 2 },
  { key: 'reg', code: '011', name: '寄存器寻址', formula: '操作数 = (Ri)', acc: 0 },
  { key: 'regInd', code: '100', name: '寄存器间接', formula: 'EA = (Ri)', acc: 1 },
  { key: 'rel', code: '101', name: '相对寻址', formula: 'EA = (PC) + A', acc: 1 },
  { key: 'idx', code: '110', name: '变址寻址', formula: 'EA = (IX) + A', acc: 1 },
  { key: 'base', code: '111', name: '基址寻址', formula: 'EA = (BR) + A', acc: 1 }]
// 各寻址方式的教材结论
const NOTE = {
  imm: '取数时不访存，速度最快，但 A 的位数限制了数据大小',
  dir: '形式地址就是有效地址，一次访存即可取到操作数',
  ind: '需两次访存：第一次取地址，第二次才取到操作数',
  reg: '不访存，寄存器在 CPU 内速度最快，但个数有限',
  regInd: '改寄存器值即可访问不同单元，适合指针与数组遍历',
  rel: '程序整体搬家时相对位移不变，有利于程序浮动',
  idx: 'IX 由用户程序设定、A 作位移量，改 IX 即可访问下一元素，适合数组循环',
  base: 'BR 由操作系统设定、A 作位移量，换程序只需改 BR，适合多道程序重定位'
}
const inst = ref('LDA')
const ri = ref(0)
const aText = ref('8')
const A = ref(8)
// 'all' = 8 种方式依次演示；也可只挑一种，步骤从 24 步缩到 4 步
const modeSel = ref('all')
const opCode = computed(() => OPC[inst.value])
// 注意声明位置：steps 在构造快照时就要读它，而 usePlayer(steps) 会在 setup 阶段
// 立刻取 steps.value —— 若这个 computed 声明在 steps 之后，就会撞 TDZ
// （Cannot access 'instNote' before initialization），整个组件直接渲染不出来
const instNote = computed(() => ({ LDA: '把操作数送入累加器 ACC', ADD: '把操作数与 ACC 相加后送回 ACC', STA: '把 ACC 内容写入该地址', JMP: '把该地址送入 PC 实现转移' }[inst.value]))
const aBin = computed(() => (cur.value.A >>> 0).toString(2).padStart(9, '0').slice(-9))
const regRows = computed(() => [
  { n: 'PC', v: PC0 + 1 }, { n: 'IR', v: `${inst.value} ${cur.value.modeName}` }, { n: 'R0', v: REG[0] },
  { n: 'R1', v: REG[1] }, { n: 'IX', v: IX }, { n: 'BR', v: BR }])
const fw = computed(() => 632 / Math.max(1, cur.value.flow.length))
const memAt = i => (i >= 0 && i < MEM.length ? MEM[i] : null)
// 越界地址（尤其间接寻址 A 指向的内容可能超出示意主存）不能显示成 null / undefined
const opTextOf = v => (v === null || v === undefined ? '越界（无此单元）' : String(v))
// EA 计算通路：文字讲「EA = (IX) + A」还是抽象的，画成链才能看清数据从哪来、在哪加工
const eaChain = computed(() => {
  const c = cur.value
  if (c.stage === 'init') return null
  const a = A.value
  const r = ri.value
  switch (c.modeKey) {
    case 'imm': return { nodes: [`IR.A = ${a}`, `操作数 = ${a}`], ops: ['即'] }
    case 'dir': return { nodes: [`IR.A = ${a}`, `EA = ${a}`], ops: ['='] }
    case 'ind': {
      const p = memAt(a)
      return { nodes: [`IR.A = ${a}`, `读 (${a}) = ${opTextOf(p)}`, `EA = ${opTextOf(p)}`], ops: ['访存', '='] }
    }
    case 'reg': return { nodes: [`R${r} = ${REG[r]}`, `操作数 = ${REG[r]}`], ops: ['即'] }
    case 'regInd': return { nodes: [`R${r} = ${REG[r]}`, `EA = ${REG[r]}`], ops: ['='] }
    case 'rel': return { nodes: [`(PC) = ${PC0 + 1}`, `+ A = ${a}`, `EA = ${PC0 + 1 + a}`], ops: ['', 'ALU'] }
    case 'idx': return { nodes: [`(IX) = ${IX}`, `+ A = ${a}`, `EA = ${IX + a}`], ops: ['', 'ALU'] }
    case 'base': return { nodes: [`(BR) = ${BR}`, `+ A = ${a}`, `EA = ${BR + a}`], ops: ['', 'ALU'] }
    default: return null
  }
})
const ew = computed(() => 632 / Math.max(1, eaChain.value ? eaChain.value.nodes.length : 1))
// 按寻址方式求 EA、操作数、数据流与用到的寄存器
function compute(m, a, r) {
  if (m === 'imm') return { ea: null, operand: a, hl: [], use: [], flow: ['IR(A)', '操作数'], d: '形式地址 A 本身就是操作数，不产生有效地址' }
  if (m === 'dir') return { ea: a, operand: memAt(a), hl: [a], use: [], flow: ['IR(A)', 'MAR', '存储器', 'MDR', '操作数'], d: `EA = A = ${a}` }
  if (m === 'ind') {
    const p = memAt(a)
    return { ea: p, operand: memAt(p), hl: [a, p], use: [], flow: ['IR(A)', 'MAR', '存储器', `MDR=${p}`, 'MAR', '存储器', '操作数'], d: `先读 (A)=(${a})=${p} 得到地址，再以它为有效地址` }
  }
  if (m === 'reg') return { ea: null, operand: REG[r], hl: [], use: [`R${r}`], flow: [`R${r}`, '操作数'], d: `操作数就在寄存器 R${r} 中` }
  if (m === 'regInd') {
    const e = REG[r]
    return { ea: e, operand: memAt(e), hl: [e], use: [`R${r}`], flow: [`R${r}`, 'MAR', '存储器', 'MDR', '操作数'], d: `EA = (R${r}) = ${e}，寄存器内容才是地址` }
  }
  if (m === 'rel') {
    const e = PC0 + 1 + a
    return { ea: e, operand: memAt(e), hl: [e], use: ['PC'], flow: ['PC', 'ALU 加 A', 'MAR', '存储器', '操作数'], d: `EA = (PC) + A = ${PC0 + 1} + ${a} = ${e}，以 PC 为基准浮动` }
  }
  if (m === 'idx') {
    const e = IX + a
    return { ea: e, operand: memAt(e), hl: [e], use: ['IX'], flow: ['IX', 'ALU 加 A', 'MAR', '存储器', '操作数'], d: `EA = (IX) + A = ${IX} + ${a} = ${e}` }
  }
  const e = BR + a
  return { ea: e, operand: memAt(e), hl: [e], use: ['BR'], flow: ['BR', 'ALU 加 A', 'MAR', '存储器', '操作数'], d: `EA = (BR) + A = ${BR} + ${a} = ${e}` }
}
const steps = computed(() => {
  const out = []
  const a = A.value
  const r = ri.value
  const OP = opCode.value
  // 只选一种方式时，其余方式不进步骤序列 —— 否则选了「变址」还得先看完前面七种
  const list = modeSel.value === 'all' ? MODES : MODES.filter(m => m.key === modeSel.value)
  function snap(desc, extra = {}) {
    // 取指译码前 Mod 字段尚无意义，显示成 000 会让人以为已判出「立即寻址」
    out.push({ A: a, modeKey: '', modeName: '待译码', modCode: '???', ea: null, eaText: '—', operandText: '—', accesses: 0, hl: [], use: [], flow: [], stage: '', ...extra, desc })
  }
  snap(`初始：指令 ${inst.value} 存放在主存 ${PC0} 号单元，指令字 = 操作码 OP(${OP}) + 寻址特征 Mod + 形式地址 A(${a})。下面${modeSel.value === 'all' ? '逐一演示 8 种' : `演示${list[0].name}`}寻址方式`, { stage: 'init', flow: ['PC'] })
  for (const m of list) {
    snap(`【${m.name}】取指周期：(PC)=${PC0} → MAR → 存储器 → MDR → IR，(PC)+1 → PC = ${PC0 + 1}；控制单元对 OP(IR) 译码，由 Mod=${m.code} 判出采用${m.name}`,
      { modeKey: m.key, modeName: m.name, modCode: m.code, stage: 'fetch', flow: ['PC', 'MAR', '存储器', 'MDR', 'IR'], use: ['PC'] })
    const c = compute(m.key, a, r)
    const opText = c.ea === null ? `操作数 = ${opTextOf(c.operand)}` : `操作数 (${c.ea}) = ${opTextOf(c.operand)}`
    snap(`【${m.name}】${c.d}。${opText}；${NOTE[m.key]}`,
      { modeKey: m.key, modeName: m.name, modCode: m.code, ea: c.ea, eaText: c.ea === null ? '无' : `EA = ${c.ea}`, operandText: opTextOf(c.operand), accesses: m.acc, hl: c.hl, use: c.use, flow: c.flow, stage: 'ea' })
    snap(`【${m.name}】执行 ${inst.value}：${instNote.value} → 操作数 ${opTextOf(c.operand)}；本方式取操作数访存 ${m.acc} 次`,
      { modeKey: m.key, modeName: m.name, modCode: m.code, ea: c.ea, eaText: c.ea === null ? '无' : `EA = ${c.ea}`, operandText: opTextOf(c.operand), accesses: m.acc, hl: c.hl, use: c.use, flow: c.flow, stage: 'mem' })
  }
  return out
})
const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
// 输入兜底：A 必须落在主存示意范围内
function applyA() {
  const v = Number(aText.value)
  A.value = Number.isFinite(v) ? Math.min(Math.max(0, Math.round(v)), MEM.length - 1) : 8
  aText.value = String(A.value)
  player.reset()
}
function resetAll() { inst.value = 'LDA'; ri.value = 0; aText.value = '8'; A.value = 8; modeSel.value = 'all'; player.reset() }
</script>

<style scoped>
.ad-wrap { display: flex; gap: 18px; align-items: flex-start; flex-wrap: wrap; }
.ad-svg { background: #fbfcff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.ad-panel { flex: 1; min-width: 280px; }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.tbl { font-size: 12px; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
.tbl-head { display: grid; grid-template-columns: 1.2fr 1.2fr 0.6fr; background: #f6f8fb; padding: 7px 10px; font-weight: 600; }
.tbl-row { display: grid; grid-template-columns: 1.2fr 1.2fr 0.6fr; padding: 6px 10px; border-top: 1px solid #f0f2f6; }
.tbl-row.active { background: var(--brand-light); color: var(--brand); font-weight: 600; }
.tip { margin-top: 10px; line-height: 1.8; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
