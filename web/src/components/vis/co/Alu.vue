<template>
  <VisFrame :title="`ALU 运算器 · ${opName}`" desc="补码加减法：符号位参与运算；溢出可用单符号位、双符号位或进位异或判断" :player="player" :status-text="statusText" back-to="/knowledge/20">
    <template #extra>
      <el-select v-model="op" size="small" style="width:110px" @change="player.reset()">
        <el-option value="add" label="加法 A+B" />
        <el-option value="sub" label="减法 A−B" />
        <el-option value="and" label="与 AND" />
        <el-option value="or" label="或 OR" />
        <el-option value="xor" label="异或 XOR" />
      </el-select>
      <span class="small muted">A</span>
      <el-input-number v-model="a" size="small" :min="-128" :max="127" style="width:110px" @change="player.reset()" />
      <span class="small muted">B</span>
      <el-input-number v-model="b" size="small" :min="-128" :max="127" style="width:110px" @change="player.reset()" />
      <el-button size="small" plain @click="player.reset()">重播</el-button>
    </template>

    <div class="alu-wrap">
      <!-- 位级运算展示 -->
      <div class="bit-area">
        <div class="bit-row">
          <span class="bit-label">[A]补</span>
          <span v-for="(bit, i) in aBits" :key="'a' + i" class="bit" :class="{ sign: i === 0 }">{{ bit }}</span>
          <span class="bit-dec">= {{ a }}</span>
        </div>
        <div class="bit-row" v-if="op === 'sub'">
          <span class="bit-label">[B]补</span>
          <span v-for="(bit, i) in bBits" :key="'b' + i" class="bit" :class="{ sign: i === 0 }">{{ bit }}</span>
          <span class="bit-dec">= {{ b }}</span>
        </div>
        <div class="bit-row" v-if="op === 'sub'">
          <span class="bit-label">[−B]补</span>
          <span v-for="(bit, i) in nbBits" :key="'nb' + i" class="bit hl-bit" :class="{ sign: i === 0 }">{{ bit }}</span>
          <span class="bit-dec">= {{ -b }}</span>
        </div>
        <div class="bit-row" v-else>
          <span class="bit-label">[B]补</span>
          <span v-for="(bit, i) in bBits" :key="'b2' + i" class="bit" :class="{ sign: i === 0 }">{{ bit }}</span>
          <span class="bit-dec">= {{ b }}</span>
        </div>
        <div class="bit-divider" />
        <div class="bit-row">
          <span class="bit-label">结果</span>
          <span v-for="(bit, i) in resultBits" :key="'r' + i" class="bit result-bit" :class="{ sign: i === 0, active: showResult }">{{ showResult ? bit : '·' }}</span>
          <span class="bit-dec" v-if="showResult">= {{ resultDec }}</span>
          <span class="bit-dec muted" v-else>（待运算）</span>
        </div>
        <div class="carry-row" v-if="isArith">
          <span class="bit-label">进位</span>
          <span v-for="(c, i) in carryBits" :key="'c' + i" class="bit carry-bit" :class="{ active: showResult }">{{ showResult ? c : '·' }}</span>
          <span class="bit-dec small muted">Cf（符号位进位） / Cn（最高数值位进位）</span>
        </div>
      </div>

      <!-- ALU 示意 -->
      <div class="alu-diagram">
        <div class="alu-box" :class="{ running: showExec }">
          <div class="alu-title">ALU</div>
          <div class="alu-op">{{ opSymbol }}</div>
        </div>
        <div class="alu-flags">
          <div class="flag"><span>ZF 零标志</span><b :class="{ on: resultDec === 0 && showResult }">{{ showResult ? (resultDec === 0 ? 1 : 0) : '-' }}</b></div>
          <div class="flag"><span>SF 符号标志</span><b :class="{ on: showResult && resultBits[0] === '1' }">{{ showResult ? resultBits[0] : '-' }}</b></div>
          <div class="flag"><span>OF 溢出标志</span><b :class="{ on: overflow && showResult }">{{ showResult ? (overflow ? 1 : 0) : '-' }}</b></div>
          <div class="flag"><span>CF 进位标志</span><b :class="{ on: cf && showResult }">{{ showResult ? cf : '-' }}</b></div>
        </div>
      </div>
    </div>

    <el-alert v-if="showResult && overflow && isArith" type="error" :closable="false" show-icon style="margin-top:12px">
      <b>溢出（OF = 1）</b>：{{ overflowReason }} —— 运算结果超出 8 位补码表示范围（−128 ~ +127），结果无效。
    </el-alert>
    <el-alert v-else-if="showResult && isArith" type="success" :closable="false" show-icon style="margin-top:12px">
      <b>无溢出</b>：{{ overflowReason }}，结果 {{ resultDec }} 有效。
    </el-alert>

    <el-row :gutter="16" style="margin-top:12px">
      <el-col :span="12">
        <div class="panel-title">溢出判断方法（8 位补码）</div>
        <ul class="rules">
          <li><b>单符号位法</b>：两个同号数相加，结果符号与操作数相反 → 溢出</li>
          <li><b>双符号位法（变形补码）</b>：结果两位符号位不同（01 正溢 / 10 负溢）→ 溢出</li>
          <li><b>进位判断法</b>：符号位进位 Cf 与最高数值位进位 Cn 相异（Cf ⊕ Cn = 1）→ 溢出</li>
        </ul>
      </el-col>
      <el-col :span="12">
        <div class="panel-title">本次计算依据</div>
        <div class="calc-box">
          <code>{{ formulaText }}</code>
          <code v-if="isArith">Cf = {{ cf }}，Cn = {{ cn }}，Cf ⊕ Cn = {{ cf ^ cn }} → {{ overflow ? '溢出' : '无溢出' }}</code>
        </div>
      </el-col>
    </el-row>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> 符号位</span>
      <span><i class="dot" style="background:#22a06b"></i> 运算结果位</span>
      <span><i class="dot" style="background:#e05252"></i> 溢出</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const op = ref('add')
const a = ref(70)
const b = ref(60)

const opName = computed(() => ({ add: '补码加法', sub: '补码减法', and: '逻辑与', or: '逻辑或', xor: '逻辑异或' }[op.value]))
const opSymbol = computed(() => ({ add: '+', sub: '−', and: '&', or: '|', xor: '⊕' }[op.value]))
const isArith = computed(() => op.value === 'add' || op.value === 'sub')

function toBits(v) {
  const u = v < 0 ? (1 << 8) + v : v
  return u.toString(2).padStart(8, '0').split('')
}
const aBits = computed(() => toBits(a.value))
const bBits = computed(() => toBits(b.value))
const nbBits = computed(() => toBits(-b.value))

const rawResult = computed(() => {
  if (op.value === 'add') return a.value + b.value
  if (op.value === 'sub') return a.value - b.value
  if (op.value === 'and') return (a.value & b.value) & 0xff
  if (op.value === 'or') return (a.value | b.value) & 0xff
  return (a.value ^ b.value) & 0xff
})
const resultBits = computed(() => {
  const u = rawResult.value < 0 ? (1 << 8) + rawResult.value : rawResult.value
  return (u & 0xff).toString(2).padStart(8, '0').split('')
})
const resultDec = computed(() => {
  const bits = resultBits.value.join('')
  const u = parseInt(bits, 2)
  return u >= 128 ? u - 256 : u
})

/* 进位计算（用于算术运算） */
const carryBits = computed(() => {
  if (!isArith.value) return new Array(8).fill('0')
  const x = op.value === 'sub' ? nbBits.value : bBits.value
  const out = []
  let carry = 0
  for (let i = 7; i >= 0; i--) {
    const sum = Number(aBits.value[i]) + Number(x[i]) + carry
    out[i] = sum >= 2 ? '1' : '0'
    carry = sum >= 2 ? 1 : 0
  }
  return out
})
const cf = computed(() => Number(carryBits.value[0])) // 符号位进位
const cn = computed(() => Number(carryBits.value[1])) // 最高数值位进位
const overflow = computed(() => (isArith.value ? (cf.value ^ cn.value) === 1 : false))

const overflowReason = computed(() => {
  if (!isArith.value) return ''
  if (overflow.value) {
    const pos = Number(aBits.value[0]) === 0 && Number((op.value === 'sub' ? nbBits.value : bBits.value)[0]) === 0
    return pos
      ? `两个正数相加结果的符号位却为 1（${resultBits.value[0]}），Cf=${cf.value} ≠ Cn=${cn.value}`
      : `两个负数相加结果的符号位却为 0（${resultBits.value[0]}），Cf=${cf.value} ≠ Cn=${cn.value}`
  }
  return `Cf=${cf.value} 与 Cn=${cn.value} 相同，符号位未发生异常变化`
})

const formulaText = computed(() => {
  if (op.value === 'add') return `[A]补 + [B]补 = ${aBits.value.join('')} + ${bBits.value.join('')} = ${resultBits.value.join('')}`
  if (op.value === 'sub') return `[A]补 + [−B]补 = ${aBits.value.join('')} + ${nbBits.value.join('')} = ${resultBits.value.join('')}`
  return `${aBits.value.join('')} ${opSymbol.value} ${bBits.value.join('')} = ${resultBits.value.join('')}（逐位逻辑运算）`
})

const steps = computed(() => {
  const out = []
  out.push({ phase: 'fetch', desc: `取操作数：A = ${a.value}（补码 ${aBits.value.join('')}），B = ${b.value}（补码 ${bBits.value.join('')}）` })
  if (op.value === 'sub') {
    out.push({ phase: 'neg', desc: `减法转加法：[−B]补 = [B]补 连同符号位取反加一 = ${nbBits.value.join('')}` })
  }
  out.push({ phase: 'exec', desc: `ALU 执行 ${opName.value}：${formulaText.value}` })
  if (isArith.value) {
    out.push({ phase: 'carry', desc: `分析进位：符号位进位 Cf = ${cf.value}，最高数值位进位 Cn = ${cn.value}` })
    out.push({
      phase: 'overflow',
      desc: overflow.value
        ? `Cf ⊕ Cn = 1 → 溢出！结果 ${resultDec.value} 超出 8 位补码范围（−128 ~ +127）`
        : `Cf ⊕ Cn = 0 → 无溢出，结果 ${resultDec.value} 有效`
    })
  }
  out.push({ phase: 'wb', desc: `结果写回寄存器，并置标志位：ZF=${resultDec.value === 0 ? 1 : 0}，SF=${resultBits.value[0]}，OF=${overflow.value ? 1 : 0}` })
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const phase = computed(() => cur.value.phase)
const showResult = computed(() => ['exec', 'carry', 'overflow', 'wb'].includes(phase.value))
const showExec = computed(() => phase.value === 'exec')
</script>

<style scoped>
.panel-title { font-size: 13px; font-weight: 600; margin-bottom: 8px; color: var(--text-2); }
.alu-wrap { display: flex; gap: 24px; align-items: flex-start; flex-wrap: wrap; }
.bit-area { flex: 1; min-width: 380px; }
.bit-row { display: flex; align-items: center; gap: 3px; margin-bottom: 6px; }
.bit-label { width: 62px; font-size: 12px; color: var(--text-2); flex-shrink: 0; }
.bit {
  width: 26px; height: 26px; line-height: 26px; text-align: center; border-radius: 4px;
  border: 1px solid var(--border); background: #fff; font-size: 13px; font-family: monospace; font-weight: 600;
}
.bit.sign { border-color: var(--brand); color: var(--brand); background: var(--brand-light); }
.hl-bit { background: #fdf3e2; border-color: #f0d9ae; }
.result-bit { background: #dcf3e7; border-color: var(--success); color: #176b48; }
.bit-dec { margin-left: 10px; font-size: 13px; font-weight: 600; }
.bit-divider { height: 1px; background: var(--border); margin: 8px 0; }
.carry-row { display: flex; align-items: center; gap: 3px; }
.carry-bit { background: #f7f9fc; font-size: 11px; color: var(--text-2); }
.alu-diagram { width: 200px; flex-shrink: 0; }
.alu-box {
  border: 2px solid var(--border); border-radius: 10px; padding: 14px; text-align: center; background: #fff;
  transition: all .3s;
}
.alu-box.running { border-color: var(--brand); background: var(--brand-light); box-shadow: 0 4px 14px rgba(59,110,246,.15); }
.alu-title { font-weight: 700; font-size: 14px; color: var(--brand); }
.alu-op { font-size: 30px; font-weight: 700; color: var(--text); line-height: 1.2; }
.alu-flags { margin-top: 10px; }
.flag { display: flex; justify-content: space-between; padding: 4px 8px; border: 1px solid var(--border); border-radius: 6px; margin-bottom: 4px; font-size: 12px; background: #fbfcff; }
.flag b { color: var(--text-3); }
.flag b.on { color: var(--danger); }
.rules { padding-left: 18px; margin: 0; }
.rules li { font-size: 12px; line-height: 1.9; color: var(--text-2); }
.calc-box code { display: block; background: #f2f4f8; padding: 8px 10px; border-radius: 6px; font-size: 12px; margin-bottom: 6px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
