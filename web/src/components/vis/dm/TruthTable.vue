<template>
  <VisFrame title="命题逻辑 · 真值表与逻辑等价" desc="枚举所有真值指派，逐行计算公式真值；空间中的顶点着色直观展示成真/成假赋值" :player="player" :status-text="statusText" back-to="/knowledge/31">
    <template #extra>
      <el-select v-model="presetKey" size="small" style="width:230px" @change="applyPreset">
        <el-option v-for="p in PRESETS" :key="p.key" :value="p.key" :label="p.label" />
      </el-select>
    </template>

    <div class="tt-wrap">
      <!-- 几何视图 -->
      <svg v-if="vars.length <= 3" :width="GW" :height="GH" class="tt-svg">
        <text :x="12" :y="18" font-size="12" fill="#8b95a3">真值指派空间（蓝 = 成真赋值，灰 = 成假赋值）</text>
        <line v-for="(e, i) in edges" :key="'e'+i" :x1="e.x1" :y1="e.y1" :x2="e.x2" :y2="e.y2"
              :stroke="e.active ? '#f2994a' : '#c8d3e6'" :stroke-width="e.active ? 2.5 : 1.2" />
        <g v-for="(v, i) in vertices" :key="'v'+i">
          <circle :cx="v.x" :cy="v.y" :r="v.cur ? 11 : 7" :fill="v.val ? '#3b6ef6' : '#dfe4ec'"
                  :stroke="v.cur ? '#f2994a' : '#8b95a3'" :stroke-width="v.cur ? 3 : 1.2" />
          <text :x="v.x" :y="v.y + 4" text-anchor="middle" font-size="11" :fill="v.val ? '#fff' : '#5a6577'" font-weight="600">
            {{ v.val ? 'T' : 'F' }}
          </text>
          <text :x="v.x + (v.dx || 12)" :y="v.y + (v.dy || 16)" font-size="10" fill="#8b95a3">{{ v.label }}</text>
        </g>
      </svg>

      <!-- 表达式输入 -->
      <div class="expr-box">
        <div class="expr-row">
          <span class="lbl">表达式 A</span>
          <el-input v-model="exprA" size="small" placeholder="例如 (P ∧ Q) → R" @change="player.reset()" />
        </div>
        <div class="expr-row">
          <span class="lbl">表达式 B</span>
          <el-input v-model="exprB" size="small" placeholder="用于判断等价，可留空" @change="player.reset()" />
        </div>
        <p class="small muted">运算符：¬ ! ~（非）　∧ & and（与）　∨ | or（或）　→ -> =>（蕴含）　↔ <-> ==（等价）　⊕ ^ xor（异或）</p>
        <div v-if="errA" class="err">表达式 A 解析失败：{{ errA }}</div>
        <div v-if="errB" class="err">表达式 B 解析失败：{{ errB }}</div>
      </div>

      <!-- 真值表 -->
      <div class="tbl-box">
        <table class="tt">
          <thead>
            <tr>
              <th v-for="v in vars" :key="v">{{ v }}</th>
              <th class="sep">A</th>
              <th v-if="exprB && !errB">B</th>
              <th v-if="exprB && !errB">A↔B</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(row, i) in rows" :key="i"
              :class="{ active: i === player.idx.value }"
              @click="player.seek(i)"
            >
              <td v-for="v in vars" :key="v">{{ row.env[v] ? 'T' : 'F' }}</td>
              <td class="sep" :class="row.a ? 'yes' : 'no'">{{ row.a ? 'T' : 'F' }}</td>
              <td v-if="exprB && !errB" :class="row.b ? 'yes' : 'no'">{{ row.b ? 'T' : 'F' }}</td>
              <td v-if="exprB && !errB" :class="row.eq ? 'yes' : 'no'">{{ row.eq ? 'T' : 'F' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 结论 -->
      <div class="tt-panel">
        <div class="info-row"><span>命题变元</span><b>{{ vars.join(', ') || '-' }}</b></div>
        <div class="info-row"><span>指派总数</span><b>2^{{ vars.length }} = {{ rows.length }}</b></div>
        <div class="info-row"><span>成真赋值数</span><b style="color:var(--brand)">{{ trueCount }}</b></div>
        <div class="info-row"><span>成假赋值数</span><b>{{ rows.length - trueCount }}</b></div>
        <div class="info-row">
          <span>公式 A 的类型</span>
          <el-tag size="small" :type="typeA.tag">{{ typeA.text }}</el-tag>
        </div>
        <div class="info-row" v-if="exprB && !errB">
          <span>A 与 B 是否等价</span>
          <el-tag size="small" :type="equivalent ? 'success' : 'danger'">{{ equivalent ? '等价 ✓' : '不等价 ✗' }}</el-tag>
        </div>
        <el-divider />
        <div class="calc">
          <div class="small muted">当前行的代入计算过程</div>
          <code>{{ calcText }}</code>
        </div>
        <p class="small muted tip">{{ presetNote }}</p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> 成真赋值</span>
      <span><i class="dot" style="background:#dfe4ec"></i> 成假赋值</span>
      <span><i class="dot" style="background:#f2994a"></i> 当前所指派的行</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const PRESETS = [
  { key: 'imp', label: '蕴含式 (P∧Q)→R', a: '(P ∧ Q) → R', b: '', note: '蕴含式 A→B 只有在「前件真且后件假」时才为假，这一点最容易记错。' },
  { key: 'demorgan', label: '德摩根律 ¬(P∧Q) ≡ ¬P∨¬Q', a: '¬(P ∧ Q)', b: '¬P ∨ ¬Q', note: '德摩根律：否定穿过括号时，∧ 与 ∨ 互换。两列真值完全相同即逻辑等价。' },
  { key: 'imp2', label: '蕴含等值式 P→Q ≡ ¬P∨Q', a: 'P → Q', b: '¬P ∨ Q', note: '这是把蕴含改写成「或」的常用等值式，也是归结推理的基础。' },
  { key: 'iff', label: '双条件 P↔Q ≡ (P→Q)∧(Q→P)', a: 'P ↔ Q', b: '(P → Q) ∧ (Q → P)', note: '等价当且仅当 P、Q 真值相同。' },
  { key: 'taut', label: '重言式 P∨¬P（排中律）', a: 'P ∨ ¬P', b: '', note: '无论 P 取何值都为真，这是经典逻辑的排中律。' },
  { key: 'contra', label: '矛盾式 P∧¬P', a: 'P ∧ ¬P', b: '', note: '无论 P 取何值都为假，是矛盾式。' }
]
const presetKey = ref('demorgan')
const exprA = ref('¬(P ∧ Q)')
const exprB = ref('¬P ∨ ¬Q')
function applyPreset() {
  const p = PRESETS.find(x => x.key === presetKey.value)
  if (p) { exprA.value = p.a; exprB.value = p.b }
  player.reset()
}
const presetNote = computed(() => {
  const p = PRESETS.find(x => x.key === presetKey.value)
  return p ? p.note : '自定义公式：输入后自动生成真值表。'
})

/* ---------------- 词法分析 ---------------- */
function normalize(src) {
  let s = String(src || '')
  s = s.replace(/\band\b/gi, ' ∧ ').replace(/\bor\b/gi, ' ∨ ')
  s = s.replace(/\bnot\b/gi, ' ¬ ').replace(/\bimplies\b/gi, ' → ')
  s = s.replace(/\bxor\b/gi, ' ⊕ ').replace(/\biff\b/gi, ' ↔ ')
  s = s.replace(/<->/g, ' ↔ ').replace(/->/g, ' → ').replace(/=>/g, ' → ')
  s = s.replace(/==/g, ' ↔ ').replace(/&&/g, ' ∧ ').replace(/\|\|/g, ' ∨ ')
  s = s.replace(/&/g, ' ∧ ').replace(/\|/g, ' ∨ ')
  s = s.replace(/!/g, ' ¬ ').replace(/~/g, ' ¬ ').replace(/\^/g, ' ⊕ ')
  return s
}
function tokenize(src) {
  const s = normalize(src)
  const tokens = []
  let i = 0
  while (i < s.length) {
    const c = s[i]
    if (/\s/.test(c)) { i++; continue }
    if (c === '(' || c === ')' || c === '[' || c === ']') { tokens.push({ t: c === '(' || c === '[' ? '(' : ')', v: c }); i++; continue }
    if ('∧∨¬→↔⊕'.includes(c)) { tokens.push({ t: 'op', v: c }); i++; continue }
    if (/[A-Za-z]/.test(c)) {
      let j = i
      while (j < s.length && /[A-Za-z0-9_]/.test(s[j])) j++
      const w = s.slice(i, j)
      if (w === 'true' || w === 'T' || w === '1') tokens.push({ t: 'const', v: true })
      else if (w === 'false' || w === 'F' || w === '0') tokens.push({ t: 'const', v: false })
      else tokens.push({ t: 'var', v: w.toUpperCase() })
      i = j
      continue
    }
    throw new Error('无法识别的字符：' + c)
  }
  return tokens
}

/* ---------------- 语法分析 ----------------
   优先级（低 → 高）：↔  <  →  <  ∨ ⊕  <  ∧  <  ¬           */
function parse(src) {
  const tk = tokenize(src)
  let p = 0
  const peek = () => tk[p]
  const eat = v => { if (tk[p] && tk[p].v === v) { p++; return true } return false }

  function iff() {
    let l = impl()
    while (peek() && peek().t === 'op' && peek().v === '↔') { p++; const r = impl(); l = { type: 'bin', op: '↔', l, r } }
    return l
  }
  function impl() {
    const l = or()
    if (peek() && peek().t === 'op' && peek().v === '→') { p++; const r = impl(); return { type: 'bin', op: '→', l, r } }
    return l
  }
  function or() {
    let l = and()
    while (peek() && peek().t === 'op' && (peek().v === '∨' || peek().v === '⊕')) {
      const op = peek().v; p++; const r = and(); l = { type: 'bin', op, l, r }
    }
    return l
  }
  function and() {
    let l = not()
    while (peek() && peek().t === 'op' && peek().v === '∧') { p++; const r = not(); l = { type: 'bin', op: '∧', l, r } }
    return l
  }
  function not() {
    if (peek() && peek().t === 'op' && peek().v === '¬') { p++; return { type: 'not', a: not() } }
    return prim()
  }
  function prim() {
    const t = peek()
    if (!t) throw new Error('表达式不完整')
    if (t.t === '(') { p++; const e = iff(); if (!eat(')')) throw new Error('括号不匹配'); return e }
    if (t.t === 'var') { p++; return { type: 'var', name: t.v } }
    if (t.t === 'const') { p++; return { type: 'const', value: t.v } }
    throw new Error('意外的符号：' + t.v)
  }
  const ast = iff()
  if (p < tk.length) throw new Error('尾部多余内容：' + tk[p].v)
  return ast
}

function evaluate(node, env) {
  if (node.type === 'var') return !!env[node.name]
  if (node.type === 'const') return node.value
  if (node.type === 'not') return !evaluate(node.a, env)
  const l = evaluate(node.l, env)
  const r = evaluate(node.r, env)
  switch (node.op) {
    case '∧': return l && r
    case '∨': return l || r
    case '⊕': return l !== r
    case '→': return !l || r
    case '↔': return l === r
    default: return false
  }
}
function collectVars(node, set) {
  if (node.type === 'var') set.add(node.name)
  else if (node.type === 'not') collectVars(node.a, set)
  else if (node.type === 'bin') { collectVars(node.l, set); collectVars(node.r, set) }
  return set
}
function astStr(node, env) {
  if (node.type === 'var') return env ? (env[node.name] ? 'T' : 'F') : node.name
  if (node.type === 'const') return node.value ? 'T' : 'F'
  if (node.type === 'not') {
    const inner = astStr(node.a, env)
    return needsParen(node.a) ? `¬(${inner})` : `¬${inner}`
  }
  const l = needsParen(node.l) ? `(${astStr(node.l, env)})` : astStr(node.l, env)
  const r = needsParen(node.r) ? `(${astStr(node.r, env)})` : astStr(node.r, env)
  return `${l} ${node.op} ${r}`
}
function needsParen(n) {
  return n.type === 'bin'
}

const astA = computed(() => { try { return { ok: true, node: parse(exprA.value) } } catch (e) { return { ok: false, err: e.message } } })
const astB = computed(() => {
  if (!exprB.value.trim()) return { ok: true, node: null }
  try { return { ok: true, node: parse(exprB.value) } } catch (e) { return { ok: false, err: e.message } }
})
const errA = computed(() => (astA.value.ok ? '' : astA.value.err))
const errB = computed(() => (astB.value.ok ? '' : astB.value.err))

const vars = computed(() => {
  const s = new Set()
  if (astA.value.ok) collectVars(astA.value.node, s)
  if (astB.value.ok && astB.value.node) collectVars(astB.value.node, s)
  return Array.from(s).sort()
})

const rows = computed(() => {
  const vs = vars.value
  if (!vs.length || !astA.value.ok) return []
  const out = []
  const N = 1 << vs.length
  for (let i = 0; i < N; i++) {
    const env = {}
    vs.forEach((v, k) => { env[v] = (i >> (vs.length - 1 - k)) & 1 ? true : false })
    const a = evaluate(astA.value.node, env)
    const b = astB.value.ok && astB.value.node ? evaluate(astB.value.node, env) : null
    out.push({ env, a, b, eq: b === null ? null : a === b })
  }
  return out
})

const trueCount = computed(() => rows.value.filter(r => r.a).length)
const typeA = computed(() => {
  const n = rows.value.length
  const t = trueCount.value
  if (!n) return { tag: 'info', text: '-' }
  if (t === n) return { tag: 'success', text: '重言式（永真）' }
  if (t === 0) return { tag: 'danger', text: '矛盾式（永假）' }
  return { tag: 'warning', text: '可满足式（非永真）' }
})
const equivalent = computed(() => rows.value.length > 0 && rows.value.every(r => r.eq === true))

const steps = computed(() => {
  const vs = vars.value
  return rows.value.map((r, i) => {
    const assign = vs.map(v => `${v}=${r.env[v] ? 'T' : 'F'}`).join('，')
    let desc = `第 ${i + 1} 行：${assign} ⇒ A = ${r.a ? 'T' : 'F'}`
    if (r.b !== null) desc += `，B = ${r.b ? 'T' : 'F'}（${r.eq ? '一致' : '不一致'}）`
    return { ...r, i, desc }
  })
})
const player = usePlayer(steps)
const cur = computed(() => player.current.value || null)
const statusText = computed(() => (cur.value ? cur.value.desc : '请输入合法的命题公式'))

const calcText = computed(() => {
  if (!cur.value || !astA.value.ok) return '-'
  const sub = astStr(astA.value.node, cur.value.env)
  const res = cur.value.a ? 'T' : 'F'
  let txt = `${sub} = ${res}`
  if (astB.value.ok && astB.value.node) {
    txt += `　　|　　B：${astStr(astB.value.node, cur.value.env)} = ${cur.value.b ? 'T' : 'F'}`
  }
  return txt
})

/* ---------------- 几何视图 ---------------- */
const GW = 380, GH = 300
const vertices = computed(() => {
  const vs = vars.value
  if (!vs.length || vs.length > 3 || !cur.value) return []
  const n = vs.length
  const base = { x: 90, y: 210 }
  const unit = n === 1 ? 150 : 118
  const off = { x: 46, y: -38 }
  const out = []
  const N = 1 << n
  for (let i = 0; i < N; i++) {
    const bits = []
    for (let k = 0; k < n; k++) bits.push((i >> (n - 1 - k)) & 1)
    let x, y
    if (n === 1) { x = base.x + bits[0] * unit; y = base.y }
    else if (n === 2) { x = base.x + bits[0] * unit; y = base.y - bits[1] * unit }
    else { x = base.x + bits[0] * unit + bits[2] * off.x; y = base.y - bits[1] * unit + bits[2] * off.y }
    const env = {}
    vs.forEach((v, k) => { env[v] = !!bits[k] })
    const val = astA.value.ok ? evaluate(astA.value.node, env) : false
    const label = vs.map((v, k) => `${v}${bits[k] ? 1 : 0}`).join('')
    const isCur = vs.every((v, k) => !!cur.value.env[v] === !!bits[k])
    out.push({ x, y, val, label, cur: isCur, bits, dx: bits[0] ? 12 : -30, dy: -12 })
  }
  return out
})
const edges = computed(() => {
  const vs = vertices.value
  if (vs.length < 2) return []
  const out = []
  for (let i = 0; i < vs.length; i++) {
    for (let j = i + 1; j < vs.length; j++) {
      let diff = 0
      for (let k = 0; k < vs[i].bits.length; k++) if (vs[i].bits[k] !== vs[j].bits[k]) diff++
      if (diff === 1) out.push({ x1: vs[i].x, y1: vs[i].y, x2: vs[j].x, y2: vs[j].y, active: vs[i].cur && vs[j].cur })
    }
  }
  return out
})
</script>

<style scoped>
.tt-wrap { display: flex; gap: 18px; align-items: flex-start; flex-wrap: wrap; }
.tt-svg { background: #fcfdff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.expr-box { width: 100%; }
.expr-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.expr-row .lbl { width: 66px; font-size: 13px; color: var(--text-2); flex-shrink: 0; }
.expr-box .small { margin: 2px 0 0; line-height: 1.7; }
.err { color: #e05252; font-size: 12px; margin-top: 4px; }
.tbl-box { flex-shrink: 0; }
table.tt { border-collapse: collapse; font-size: 13px; text-align: center; }
table.tt th, table.tt td { border: 1px solid var(--border); padding: 6px 14px; }
table.tt th { background: #f6f8fb; font-weight: 600; }
table.tt td.sep, table.tt th.sep { border-left: 2px solid var(--brand); }
table.tt tbody tr { cursor: pointer; }
table.tt tbody tr:hover { background: #f6f8fb; }
table.tt tbody tr.active { background: var(--brand-light); }
td.yes { color: var(--brand); font-weight: 700; }
td.no { color: #8b95a3; }
.tt-panel { flex: 1; min-width: 290px; }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.calc code { background: #f2f4f8; padding: 8px 10px; border-radius: 6px; display: block; font-size: 12px; line-height: 1.8; }
.tip { margin-top: 10px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
