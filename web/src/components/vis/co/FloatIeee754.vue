<template>
  <VisFrame title="IEEE 754 浮点数 · 符号位 / 阶码移码 / 尾数" desc="规格化真值 = (−1)^S × 1.M × 2^(E−偏置)；阶码用移码便于比较大小，尾数最高位恒为 1 故隐含不存" :player="player" :status-text="statusText" back-to="/knowledge/51">
    <template #extra>
      <el-select v-model="prec" size="small" style="width:110px" @change="player.reset()">
        <el-option :value="32" label="单精度 32 位" /><el-option :value="64" label="双精度 64 位" />
      </el-select>
      <el-select v-model="preset" size="small" style="width:120px" @change="usePreset">
        <el-option value="-12.375" label="-12.375 规格化" /><el-option value="0.1" label="0.1 无限循环" /><el-option value="0" label="0 机器零" /><el-option value="1e-45" label="1e-45 非规格化" /><el-option value="1e40" label="1e40 上溢" />
      </el-select>
      <el-input v-model="inputText" size="small" style="width:120px" placeholder="十进制实数" />
      <el-button size="small" @click="applyInput">应用</el-button>
      <el-button size="small" plain @click="resetAll">重置</el-button>
    </template>
    <div class="fl-wrap">
      <svg :width="W" :height="H" class="fl-svg">
        <text x="12" y="14" font-size="12" font-weight="700" fill="#1f2733">{{ prec === 32 ? '单精度 float（32 位）' : '双精度 double（64 位）' }} 二进制布局</text>
        <!-- 逐位单元格 -->
        <rect v-for="(c, i) in bitsArr" :key="'b' + i" :x="bx + i * cw" y="24" :width="cw - 1.4" height="20" rx="2" :fill="fieldFill(i)" :stroke="fieldStroke(i)" stroke-width="0.8" />
        <text v-for="(c, i) in bitsArr" :key="'t' + i" :x="bx + i * cw + (cw - 1.4) / 2" y="38" text-anchor="middle" :font-size="cw < 12 ? 8 : 10.5" :fill="fieldText(i)">{{ c }}</text>
        <!-- 三段大括号 -->
        <g v-for="(g, k) in groups" :key="k">
          <line :x1="g.x" :y1="20" :x2="g.x + g.w" :y2="20" :stroke="g.color" stroke-width="1.6" />
          <line :x1="g.x" :y1="16" :x2="g.x" :y2="20" :stroke="g.color" stroke-width="1.6" />
          <line :x1="g.x + g.w" :y1="16" :x2="g.x + g.w" :y2="20" :stroke="g.color" stroke-width="1.6" />
          <text :x="g.x + g.w / 2" y="12" text-anchor="middle" font-size="10.5" font-weight="700" :fill="g.color">{{ g.label }}</text>
        </g>
        <!-- 三个字段卡片 -->
        <rect v-for="(c, i) in cards" :key="'c' + i" :x="14 + i * 216" y="58" width="204" height="52" rx="8" :fill="c.bg" :stroke="c.color" :stroke-width="c.active ? 2.6 : 1.2" />
        <text v-for="(c, i) in cards" :key="'t1' + i" :x="26 + i * 216" :y="76" font-size="11" :font-weight="c.active ? 800 : 600" :fill="c.color">{{ c.title }}</text>
        <text v-for="(c, i) in cards" :key="'t2' + i" :x="26 + i * 216" :y="92" font-size="12" :fill="c.color">{{ c.line1 }}</text>
        <text v-for="(c, i) in cards" :key="'t3' + i" :x="26 + i * 216" :y="105" font-size="10" fill="#8b95a3">{{ c.line2 }}</text>
        <!-- 还原公式 -->
        <rect x="14" y="120" width="632" height="40" rx="8" :fill="cur.stage === 'verify' ? '#f2ecff' : '#fbfcff'" stroke="#dfe4ec" />
        <text x="26" y="138" font-size="11" fill="#8b95a3">还原真值：</text>
        <text x="26" y="154" font-size="12" font-weight="700" fill="#1f2733">{{ restoreText }}</text>
        <!-- 分类与特殊用途 -->
        <rect x="14" y="170" width="308" height="54" rx="8" :fill="kindBg" :stroke="kindColor" stroke-width="1.5" />
        <text x="26" y="190" font-size="11" fill="#8b95a3">类型判定</text>
        <text x="26" y="208" font-size="13" font-weight="700" :fill="kindColor">{{ cur.kindText }}</text>
        <rect x="338" y="170" width="308" height="54" rx="8" fill="#fbfcff" stroke="#dfe4ec" />
        <text x="350" y="190" font-size="11" fill="#8b95a3">阶码全 0 / 全 1 的特殊用途</text>
        <text x="350" y="206" font-size="10.5" fill="#5a6474">E = 0 且 M = 0 → 机器零；E = 0 且 M ≠ 0 → 非规格化数</text>
        <text x="350" y="220" font-size="10.5" fill="#5a6474">E 全 1 且 M = 0 → ±∞；E 全 1 且 M ≠ 0 → NaN</text>
      </svg>
      <div class="fl-panel">
        <div class="info-row"><span>符号位 S</span><b style="color:#8b5cf6">{{ cur.s }}（{{ cur.s ? '负数' : '正数' }}）</b></div>
        <div class="info-row"><span>阶码移码 E（{{ cur.eb }} 位）</span><b style="color:var(--brand)">{{ cur.E }}（真值 e = {{ cur.e }}）</b></div>
        <div class="info-row"><span>偏置值 bias</span><b>{{ cur.bias }}</b></div>
        <div class="info-row"><span>尾数域 M（{{ cur.mb }} 位）</span><b style="color:var(--warning)">{{ mantissaShort }}</b></div>
        <div class="info-row"><span>十六进制</span><b>{{ hexText }}</b></div>
        <div class="info-row"><span>还原真值</span><b style="color:var(--success)">{{ cur.valueText }}</b></div>
        <p class="tip small muted">考点：① 阶码用移码（真值 + 偏置）表示，所有阶码都当无符号数比较，便于对阶与判零；② 规格化尾数最高位恒为 1，隐含存储，故单精度虽只存 23 位尾数却有 24 位精度；③ 阶码全 0 / 全 1 留作非规格化数与 ∞、NaN 等特殊用途。</p>
      </div>
    </div>
    <template #legend>
      <span><i class="dot" style="background:#8b5cf6"></i> 符号位 S（1 位）</span>
      <span><i class="dot" style="background:#3b6ef6"></i> 阶码 E（移码，8 / 11 位）</span>
      <span><i class="dot" style="background:#e8a13a"></i> 尾数 M（23 / 52 位，隐含最高位 1）</span>
      <span><i class="dot" style="background:#e05252"></i> 上溢 / 非规格化 / 特殊值</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'
const W = 660
const H = 234
const prec = ref(32)
const preset = ref('-12.375')
const inputText = ref('-12.375')
const value = ref(-12.375)
// 把十进制小数化成二进制字符串（整数部 + 小数部，最多 24 位小数）
function toBinStr(v) {
  if (!Number.isFinite(v) || v === 0) return '0'
  const ip = Math.floor(v)
  let fp = v - ip
  let s = ip.toString(2) + (fp > 0 ? '.' : '')
  let n = 0
  while (fp > 0 && n++ < 24) { fp *= 2; const bit = Math.floor(fp); s += bit; fp -= bit }
  return s
}
// 用 DataView 读取真正的 IEEE 754 位模式，保证展示的比特位完全准确
function rawBits(x, p) {
  const dv = new DataView(new ArrayBuffer(8))
  if (p === 32) { dv.setFloat32(0, x); const u = dv.getUint32(0); return { s: u >>> 31, E: (u >>> 23) & 0xFF, M: u & 0x7FFFFF } }
  dv.setFloat64(0, x)
  const hi = dv.getUint32(0), lo = dv.getUint32(4)
  return { s: hi >>> 31, E: (hi >>> 20) & 0x7FF, M: (hi & 0xFFFFF) * 4294967296 + lo }
}
const bin = (v, n) => (v >>> 0).toString(2).padStart(n, '0').slice(-n)
const steps = computed(() => {
  const out = []
  const p = prec.value
  const eb = p === 32 ? 8 : 11
  const mb = p === 32 ? 23 : 52
  const bias = (1 << (eb - 1)) - 1
  const x = value.value
  const ax = Math.abs(x)
  const r = rawBits(x, p)
  const s = Number.isFinite(x) ? (x < 0 ? 1 : 0) : r.s
  let e = r.E - bias
  if (ax > 0 && Number.isFinite(ax)) e = Math.floor(Math.log2(ax))   // 阶码真值（教学推导用）
  const EMBig = (1 << eb) - 1
  let kind, kindText
  if (!Number.isFinite(x)) { kind = Number.isNaN(x) ? 'nan' : 'inf'; kindText = Number.isNaN(x) ? 'NaN（阶码全 1、尾数非 0）' : '±∞ 上溢（阶码全 1、尾数全 0）' }
  else if (ax === 0) { kind = 'zero'; kindText = '机器零（阶码全 0 且尾数全 0）' }
  else if (r.E >= EMBig) { kind = 'over'; kindText = `正/负上溢 → ±∞（阶码真值 ${e} 超出 [${1 - bias}, ${bias}]）` }
  else if (r.E === 0) { kind = 'under'; kindText = '非规格化数（阶码全 0，尾数最高位为 0，真值 = (−1)^S × 0.M × 2^(1−偏置)）' }
  else { kind = 'norm'; kindText = `规格化数（1 ≤ E ≤ ${EMBig - 1}，尾数最高位隐含为 1）` }
  const mBin = r.M.toString(2).padStart(mb, '0')
  const bitStr = String(s) + bin(r.E, eb) + mBin
  const mVal = kind === 'norm' ? 1 + r.M / Math.pow(2, mb) : r.M / Math.pow(2, mb)
  const valueText = !Number.isFinite(x) ? String(x) : (ax === 0 ? (Object.is(x, -0) ? '-0' : '0') : String((s ? -1 : 1) * mVal * Math.pow(2, kind === 'under' ? 1 - bias : e)))
  const base = { x, p, eb, mb, bias, s, e, E: r.E, M: r.M, bitStr, kind, kindText, valueText }
  function snap(desc, extra = {}) { out.push({ ...base, stage: '', ...extra, desc }) }
  snap(`初始：输入十进制实数 x = ${x}，选${p === 32 ? '单精度' : '双精度'}：符号 1 位 + 阶码 ${eb} 位（偏置 ${bias}）+ 尾数 ${mb} 位`, { stage: 'init' })
  snap(`① 定符号位 S：x ${x < 0 ? '< 0，S = 1，表示负数' : (Object.is(x, -0) ? '= −0，S = 1' : '≥ 0，S = 0，表示正数')}；符号位只管正负，与数值大小无关`, { stage: 'sign' })
  snap(`② 化二进制并规格化：|x| = ${ax} = ${toBinStr(ax)}₂，把小数点移到最高位 1 之后得 1.${mBin.slice(0, 8)}… × 2^${e}，故阶码真值 e = ${e}`, { stage: 'exp' })
  snap(`③ 求阶码移码 E = e + 偏置 = ${e} + ${bias} = ${r.E} = ${bin(r.E, eb)}₂。用移码后阶码全为正数，比较大小与对阶都变得简单`, { stage: 'bias' })
  snap(`④ 取尾数域：规格化数最高位必为 1，这一位${kind === 'norm' ? '不存储（隐含）' : '实际为 0'}，尾数域只存小数点后的 ${mb} 位 → M = ${mBin.slice(0, 24)}${mb > 24 ? '…' : ''}₂`, { stage: 'mant' })
  snap(`⑤ 拼装 ${p} 位布局：S(${String(s)}) | E(${bin(r.E, eb)}) | M(${mb} 位) = ${bitStr.slice(0, 32)}${p > 32 ? ' …' : ''}`, { stage: 'bits' })
  snap(`⑥ 类型判定：${kindText}`, { stage: 'kind' })
  snap(`⑦ 还原验证：真值 = (−1)^${s} × ${kind === 'norm' ? '1' : '0'}.M × 2^${kind === 'under' ? 1 - bias : e} = ${valueText}。可见浮点数是离散的，只能近似表示实数`, { stage: 'verify' })
  return out
})
const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const bitsArr = computed(() => cur.value.bitStr.split(''))
const cw = computed(() => Math.min(19, 620 / cur.value.p))
const bx = computed(() => (W - cur.value.p * cw.value) / 2)
const FCOLOR = ['#8b5cf6', '#3b6ef6', '#e8a13a']
const FBG = ['#f2ecff', '#e6eeff', '#fff3e0']
const fieldOf = i => (i === 0 ? 0 : i <= cur.value.eb ? 1 : 2)

/** 当前阶段正在处理哪个字段：0=S 1=E 2=M，-1=无（整体/判定/还原）
 *  没有它的话，①~⑥ 六步的画面长得一模一样，只有文字在变。 */
const STAGE_FIELD = { sign: 0, exp: 1, bias: 1, mant: 2 }
const activeField = computed(() => {
  const f = STAGE_FIELD[cur.value.stage]
  return f === undefined ? -1 : f
})
const FAINT_BG = '#fafcff'
const FAINT_COLOR = '#c9d2e0'

const fieldFill = i => {
  const f = fieldOf(i)
  if (activeField.value < 0) return FBG[f]
  return f === activeField.value ? FBG[f] : FAINT_BG
}
const fieldStroke = i => {
  const f = fieldOf(i)
  if (activeField.value < 0) return FCOLOR[f]
  return f === activeField.value ? FCOLOR[f] : FAINT_COLOR
}
const fieldText = i => {
  const f = fieldOf(i)
  if (activeField.value < 0) return FCOLOR[f]
  return f === activeField.value ? FCOLOR[f] : FAINT_COLOR
}
const groups = computed(() => {
  const { eb, mb } = cur.value
  const w = i => i * cw.value
  return [{ x: bx.value, w: w(1), color: FCOLOR[0], label: 'S · 符号位 1 位' },
    { x: bx.value + w(1), w: w(eb), color: FCOLOR[1], label: `E · 阶码移码 ${eb} 位` },
    { x: bx.value + w(1 + eb), w: w(mb), color: FCOLOR[2], label: `M · 尾数 ${mb} 位` }]
})
const cards = computed(() => {
  const c = cur.value
  const a = activeField.value
  return [
    { title: '① 符号位 S', color: a === 0 ? FCOLOR[0] : FAINT_COLOR, bg: a === 0 ? FBG[0] : FAINT_BG, active: a === 0, line1: `${c.s} → ${c.s ? '负数' : '正数'}`, line2: '0 表正、1 表负，与真值分离' },
    { title: `② 阶码 E（${c.eb} 位移码）`, color: a === 1 ? FCOLOR[1] : FAINT_COLOR, bg: a === 1 ? FBG[1] : FAINT_BG, active: a === 1, line1: `${c.E} = ${bin(c.E, c.eb)}₂`, line2: `真值 e = E − ${c.bias} = ${c.e}` },
    { title: `③ 尾数 M（${c.mb} 位）`, color: a === 2 ? FCOLOR[2] : FAINT_COLOR, bg: a === 2 ? FBG[2] : FAINT_BG, active: a === 2, line1: `真尾数 = ${c.kind === 'norm' ? '1' : '0'}.${c.M.toString(2).padStart(c.mb, '0').slice(0, 10)}…₂`, line2: `规格化时最高位 1 隐含，实际精度 ${c.mb + 1} 位` }]
})
const restoreText = computed(() => {
  const c = cur.value
  if (c.kind === 'nan') return 'NaN：无效运算结果（0/0、∞−∞ 等）'
  if (c.kind === 'inf') return `(−1)^${c.s} × ∞ = ${c.valueText}`
  if (c.kind === 'zero') return `阶码与尾数全 0 → 真值 = ${c.valueText}`
  return `(−1)^${c.s} × ${c.kind === 'norm' ? '1' : '0'}.M × 2^${c.kind === 'under' ? 1 - c.bias : c.e} = ${c.valueText}`
})
const mantissaShort = computed(() => {
  const m = cur.value.M.toString(2).padStart(cur.value.mb, '0')
  return m.length > 20 ? m.slice(0, 20) + '…' : m
})
const hexText = computed(() => {
  const c = cur.value
  if (c.p === 32) return '0x' + parseInt(c.bitStr, 2).toString(16).toUpperCase().padStart(8, '0')
  const hi = parseInt(c.bitStr.slice(0, 32), 2), lo = parseInt(c.bitStr.slice(32), 2)
  return '0x' + hi.toString(16).toUpperCase().padStart(8, '0') + lo.toString(16).toUpperCase().padStart(8, '0')
})
const kindColor = computed(() => ({ norm: '#22a06b', zero: '#8b95a3', under: '#e8a13a', over: '#e05252', inf: '#e05252', nan: '#e05252' }[cur.value.kind]))
const kindBg = computed(() => ({ norm: '#f2fbf6', zero: '#f7f9fc', under: '#fff3e0', over: '#fdeaea', inf: '#fdeaea', nan: '#fdeaea' }[cur.value.kind]))
function usePreset() { inputText.value = preset.value; applyInput() }
// 输入兜底：非数字时退回上一个合法值
function applyInput() {
  const v = Number(inputText.value)
  if (!Number.isFinite(v)) { inputText.value = String(value.value); return }
  value.value = v
  player.reset()
}
function resetAll() { prec.value = 32; preset.value = '-12.375'; inputText.value = '-12.375'; value.value = -12.375; player.reset() }
</script>

<style scoped>
.fl-wrap { display: flex; gap: 18px; align-items: flex-start; flex-wrap: wrap; }
.fl-svg { background: #fbfcff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.fl-panel { flex: 1; min-width: 260px; }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.tip { margin-top: 10px; line-height: 1.8; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
