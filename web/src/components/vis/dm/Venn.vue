<template>
  <VisFrame title="集合运算 · 文氏图与计数" desc="全集按「属于哪些集合」切成互斥区域，任何运算结果都是若干区域的并：逐区域染色即可读出结果集" :player="player" :status-text="statusText" back-to="/knowledge/64">
    <template #extra>
      <el-select v-model="mode" size="small" style="width:120px" @change="player.reset()">
        <el-option value="op" label="基本运算" />
        <el-option value="demorgan" label="德摩根律" />
        <el-option value="inclusion" label="容斥原理" />
      </el-select>
      <el-select v-if="mode === 'op'" v-model="op" size="small" style="width:118px" @change="player.reset()">
        <el-option v-for="o in OP_LIST" :key="o.k" :value="o.k" :label="o.label" />
      </el-select>
      <el-radio-group v-model="nSet" size="small" @change="player.reset()">
        <el-radio-button :value="2">2 集</el-radio-button>
        <el-radio-button :value="3">3 集</el-radio-button>
      </el-radio-group>
    </template>

    <div class="vn-wrap">
      <svg :width="W" :height="H" class="vn-svg">
        <defs>
          <!-- in-k = 圆内，out-k = 全集挖去圆 k（evenodd 求补），all = 全集 -->
          <clipPath v-for="c in circles" :key="'i' + c.k" :id="'vn-in-' + c.k"><circle :cx="c.x" :cy="c.y" :r="c.r" /></clipPath>
          <clipPath v-for="c in circles" :key="'o' + c.k" :id="'vn-out-' + c.k"><path :d="donut(c)" clip-rule="evenodd" fill-rule="evenodd" /></clipPath>
          <clipPath id="vn-all"><rect x="0" y="0" :width="W" :height="H" /></clipPath>
        </defs>
        <rect x="5" y="5" :width="W - 10" :height="H - 10" rx="10" fill="#fbfcff" stroke="#c8d3e6" />
        <text x="16" y="26" font-size="12" fill="#8b95a3">U（全集，|U| = {{ U.length }}）</text>
        <!-- 三层裁剪嵌套求交 = 「属于 A? ∩ 属于 B? ∩ 属于 C?」这唯一一块区域 -->
        <g v-for="c in cur.colored" :key="'c' + c.m">
          <g :clip-path="`url(#vn-${cond(c.m, 0)})`"><g :clip-path="`url(#vn-${cond(c.m, 1)})`"><g :clip-path="`url(#vn-${cond(c.m, 2)})`">
            <rect x="0" y="0" :width="W" :height="H" :fill="c.color" :opacity="c.m === cur.curM ? 0.55 : 0.26" />
          </g></g></g>
        </g>
        <circle v-for="c in circles" :key="'r' + c.k" :cx="c.x" :cy="c.y" :r="c.r" fill="none" :stroke="c.color" stroke-width="2.2" />
        <text v-for="c in circles" :key="'t' + c.k" :x="c.x" :y="c.y - c.r + 20" text-anchor="middle" font-size="15" font-weight="700" :fill="c.color">{{ c.k }}</text>
        <text v-for="r in regions" :key="'e' + r.m" :x="pt(r.m).x" :y="pt(r.m).y" text-anchor="middle" font-size="11" font-weight="600" :fill="regFill(r.m)">{{ r.els.join(',') || '∅' }}</text>
      </svg>

      <div class="vn-panel">
        <div class="info-row"><span>全集 U</span><b>{{ U.join(' ') }}</b></div>
        <div class="info-row"><span>当前区域</span><b style="color:var(--brand)">{{ curExpr || '—' }}</b></div>
        <div class="info-row"><span>当前目标式</span><b>{{ cur.label || '—' }}</b></div>
        <div class="info-row"><span>结果集合</span><b style="color:var(--success)">{ {{ (cur.result || []).join(', ') }} } · {{ (cur.result || []).length }} 个</b></div>
        <div class="vn-inputs">
          <span class="lbl">A</span><el-input v-model="inA" size="small" @change="player.reset()" />
          <span class="lbl">B</span><el-input v-model="inB" size="small" @change="player.reset()" />
          <span class="lbl" v-if="nSet === 3">C</span><el-input v-if="nSet === 3" v-model="inC" size="small" @change="player.reset()" />
          <el-button size="small" plain @click="resetAll">重置</el-button>
        </div>
        <p class="small muted tip">{{ tip }}</p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> 命中的结果区域</span>
      <span><i class="dot" style="background:#e05252"></i> 德摩根左式 / 容斥减项</span>
      <span><i class="dot" style="background:#8b5cf6"></i> 德摩根右式</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const W = 420, H = 300
const BASE = ['1', '2', '3', '4', '5', '6', '7', '8', '9'] // 默认全集：8、9 故意落在所有集合之外，便于演示补集与容斥
const SET_COLOR = { A: '#3b6ef6', B: '#22a06b', C: '#e8a13a' }
// 三圆圆心成等边三角形 → 保证 2^3 = 8 个区域都存在；2 集时只画 A、B 两圆
const LAYOUT = {
  2: [{ k: 'A', x: 150, y: 155, r: 100 }, { k: 'B', x: 272, y: 155, r: 100 }],
  3: [{ k: 'A', x: 186, y: 118, r: 92 }, { k: 'B', x: 256, y: 118, r: 92 }, { k: 'C', x: 221, y: 196, r: 92 }]
}
// 各区域的文字锚点，下标 = 掩码（bit0=A, bit1=B, bit2=C）
const PT3 = [[42, 36], [126, 96], [316, 96], [221, 68], [221, 272], [148, 192], [294, 192], [221, 150]]
const PT2 = [[42, 34], [96, 158], [326, 158], [211, 158]]
const DEFAULTS = { A: '1,4,5,7', B: '2,4,6,7', C: '3,5,6,7' }

const mode = ref('op')
const op = ref('union')
const nSet = ref(3)
const inA = ref(DEFAULTS.A), inB = ref(DEFAULTS.B), inC = ref(DEFAULTS.C)

// 输入兜底：任意分隔符均可拆分，空输入 / 非法输入退化为空集，不会抛错
const parse = s => String(s || '').split(/[,，;；\s]+/).map(t => t.trim()).filter(Boolean)
const setA = computed(() => new Set(parse(inA.value)))
const setB = computed(() => new Set(parse(inB.value)))
const setC = computed(() => new Set(parse(inC.value)))
const U = computed(() => Array.from(new Set([...BASE, ...parse(inA.value), ...parse(inB.value), ...parse(inC.value)])).sort((a, b) => (isNaN(a) || isNaN(b)) ? String(a).localeCompare(String(b)) : Number(a) - Number(b)))
const circles = computed(() => LAYOUT[nSet.value].map(c => ({ ...c, color: SET_COLOR[c.k] })))
const MASK = computed(() => (nSet.value === 2 ? 3 : 7))

// 元素 → 区域掩码：属于 A 记 1、B 记 2、C 记 4，同掩码的元素落在同一区域
const maskOf = el => (setA.value.has(el) ? 1 : 0) | (setB.value.has(el) ? 2 : 0) | (nSet.value === 3 && setC.value.has(el) ? 4 : 0)
const regions = computed(() => {
  const list = []
  for (let m = 0; m <= MASK.value; m++) {
    const els = U.value.filter(e => maskOf(e) === m)
    const parts = [(m & 1) ? 'A' : '~A', (m & 2) ? 'B' : '~B', ...(nSet.value === 3 ? [(m & 4) ? 'C' : '~C'] : [])]
    list.push({ m, els, expr: parts.join('∩') })
  }
  return list
})

// 五种运算统一写成「区域掩码是否命中」的谓词：判一个区域 = 判该区域全部元素
const OPS = {
  union: { l2: '并 A∪B', l3: '并 A∪B∪C', f: m => (m & MASK.value) !== 0 },
  inter: { l2: '交 A∩B', l3: '交 A∩B∩C', f: (m, n) => (n === 2 ? (m & 3) === 3 : m === 7) },
  comp: { l2: '补 ~A', l3: '补 ~A', f: m => !(m & 1) },
  diff: { l2: '差 A−B', l3: '差 A−B', f: m => !!(m & 1) && !(m & 2) },
  sym: { l2: '对称差 A⊕B', l3: '对称差 A⊕B', f: m => !!(m & 1) !== !!(m & 2) }
}
const OP_LIST = [{ k: 'union', label: '并 A∪B' }, { k: 'inter', label: '交 A∩B' }, { k: 'comp', label: '补 ~A' }, { k: 'diff', label: '差 A−B' }, { k: 'sym', label: '对称差 A⊕B' }]

const steps = computed(() => {
  const out = [], n = nSet.value, regs = regions.value, colored = []
  let result = []
  // 每步快照：已染色的区域 + 当前扫描的区域 + 已收集的结果元素
  function snap(desc, extra = {}) { out.push({ colored: colored.map(c => ({ ...c })), curM: -1, result: [...result], desc, ...extra }) }
  // 逐区域扫描：命中则染成 color，并把该区域的元素并入结果集
  function paint(hit, color, tag, yesTxt, noTxt) {
    for (const r of regs) {
      const yes = hit(r.m)
      if (yes) { colored.push({ m: r.m, color }); result = result.concat(r.els) }
      snap(`【${tag}】区域 ${r.expr} = {${r.els.join(',') || '∅'}} → ${yes ? yesTxt : noTxt}`, { curM: r.m, label: tag })
    }
  }
  snap(`全集 U = {${U.value.join(',')}}；A = {${[...setA.value].join(',') || '∅'}}，B = {${[...setB.value].join(',') || '∅'}}${n === 3 ? `，C = {${[...setC.value].join(',') || '∅'}}` : ''}`, { label: '初始化' })
  if (mode.value === 'op') {
    const o = OPS[op.value] || OPS.union
    const label = n === 2 ? o.l2 : o.l3
    paint(m => o.f(m, n), '#3b6ef6', label, '命中，染蓝', '不命中')
    snap(`${label} = {${result.join(',') || '∅'}}，共 ${result.length} 个元素`, { label })
  } else if (mode.value === 'demorgan') {
    const eL = n === 2 ? '~(A∪B)' : '~(A∪B∪C)'
    const eR = n === 2 ? '~A∩~B' : '~A∩~B∩~C'
    const outside = m => (m & MASK.value) === 0
    paint(outside, '#e05252', eL, '在所有圆之外，染红', '属于并集，跳过')
    const left = result.join(',')
    snap(`左式 ${eL} = {${left || '∅'}}，共 ${result.length} 个元素`, { label: eL })
    colored.length = 0
    result = []
    paint(outside, '#8b5cf6', eR, `同时不属于 A、B${n === 3 ? '、C' : ''}，染紫`, '跳过')
    const right = result.join(',')
    snap(`两边比对：{${left || '∅'}} ${left === right ? '=' : '≠'} {${right || '∅'}} → ${eL} = ${eR} ${left === right ? '成立 ✓' : '不成立 ✗'}`, { label: '两边比对' })
  } else {
    // 容斥原理：奇重交相加、偶重交相减
    const names = n === 2 ? [['A', 1], ['B', 2]] : [['A', 1], ['B', 2], ['C', 4]]
    const terms = names.map(([nm, b]) => ({ sign: 1, bits: b, expr: nm }))
    for (let i = 0; i < names.length; i++) for (let j = i + 1; j < names.length; j++) terms.push({ sign: -1, bits: names[i][1] | names[j][1], expr: `${names[i][0]}∩${names[j][0]}` })
    if (n === 3) terms.push({ sign: 1, bits: 7, expr: 'A∩B∩C' })
    let sum = 0
    const fml = []
    for (const t of terms) {
      const c = U.value.filter(e => (maskOf(e) & t.bits) === t.bits).length
      sum += t.sign * c
      fml.push(`${t.sign > 0 ? '+' : '−'}|${t.expr}|`)
      colored.length = 0
      regs.forEach(r => { if ((r.m & t.bits) === t.bits) colored.push({ m: r.m, color: t.sign > 0 ? '#22a06b' : '#e05252' }) })
      snap(`容斥项 ${t.sign > 0 ? '+' : '−'} |${t.expr}| = ${c}，累计 = ${sum}`, { label: fml.join(' ') })
    }
    result = U.value.filter(e => (maskOf(e) & MASK.value) !== 0)
    colored.length = 0
    regs.forEach(r => { if ((r.m & MASK.value) !== 0) colored.push({ m: r.m, color: '#3b6ef6' }) })
    snap(`容斥得 |A∪B${n === 3 ? '∪C' : ''}| = ${sum}，直接计数 = ${result.length} → ${sum === result.length ? '一致 ✓' : '不一致 ✗'}`, { label: `${fml.join(' ')} = ${sum}` })
  }
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const curExpr = computed(() => { const r = regions.value.find(x => x.m === cur.value.curM); return r ? `${r.expr} = {${r.els.join(',') || '∅'}}` : '' })
const tip = computed(() => ({
  op: '考点：2 集把全集切成 4 个互斥区域、3 集切成 8 个；任一集合运算的结果都是若干区域的并 →「切区域、染色、读元素」就是通用算法。',
  demorgan: '考点：德摩根律 ~(A∪B) = ~A∩~B（3 集：~(A∪B∪C) = ~A∩~B∩~C），否定穿过括号时 ∪ 与 ∩ 互换；两边都恰好是「所有圆之外」的同一批区域。',
  inclusion: '考点：容斥原理 |A∪B∪C| = Σ|Ai| − Σ|Ai∩Aj| + |A∩B∩C|，口诀「奇数重交加、偶数重交减」，用于覆盖类计数问题。'
}[mode.value]))

const pt = m => { const t = (nSet.value === 2 ? PT2 : PT3)[m]; return { x: t[0], y: t[1] } }
// 全集矩形挖掉圆 c：矩形与圆合成一条 path，evenodd 填充规则下即补集
const donut = c => `M0,0H${W}V${H}H0Z M${c.x - c.r},${c.y}a${c.r},${c.r} 0 1,0 ${2 * c.r},0a${c.r},${c.r} 0 1,0 ${-2 * c.r},0Z`
// 第 i 个集合用「圆内」还是「圆外」裁剪；集合数不足时退化为全集
const cond = (m, i) => (i >= circles.value.length ? 'all' : (m & (1 << i)) ? 'in-' + circles.value[i].k : 'out-' + circles.value[i].k)
const regFill = m => (cur.value.colored || []).some(c => c.m === m) ? '#1f2733' : '#8b95a3'
function resetAll() {
  inA.value = DEFAULTS.A; inB.value = DEFAULTS.B; inC.value = DEFAULTS.C; mode.value = 'op'; op.value = 'union'; nSet.value = 3
  player.reset()
}
</script>

<style scoped>
.vn-wrap { display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap; } .vn-svg { flex-shrink: 0; background: #fcfdff; border: 1px solid var(--border); border-radius: 10px; }
.vn-panel { flex: 1; min-width: 280px; }
.info-row { display: flex; justify-content: space-between; gap: 12px; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.vn-inputs { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.vn-inputs .lbl { width: 14px; font-weight: 700; color: var(--text-2); } .vn-inputs .el-input { width: 92px; }
.tip { margin-top: 10px; line-height: 1.7; } .dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
