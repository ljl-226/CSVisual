<template>
  <VisFrame title="贝叶斯公式 · 先验 → 似然 → 后验" desc="由先验概率与似然算出联合概率，再由全概率归一化得到后验：P(D|+) = P(D)P(+|D) / [P(D)P(+|D) + P(¬D)P(+|¬D)]" :player="player" :status-text="statusText" back-to="/knowledge/60">
    <template #extra>
      <el-select v-model="caseKey" size="small" style="width:150px" @change="applyCase">
        <el-option v-for="c in CASES" :key="c.key" :value="c.key" :label="c.label" />
      </el-select>
      <span class="small muted">患病率 {{ pPct }}%</span>
      <el-slider v-model="pPct" :min="0.1" :max="50" :step="0.1" style="width:90px" :show-tooltip="false" @change="player.reset()" />
      <span class="small muted">灵敏度 {{ sePct }}%</span>
      <el-slider v-model="sePct" :min="50" :max="100" :step="1" style="width:80px" :show-tooltip="false" @change="player.reset()" />
      <span class="small muted">特异度 {{ spPct }}%</span>
      <el-slider v-model="spPct" :min="50" :max="100" :step="1" style="width:80px" :show-tooltip="false" @change="player.reset()" />
    </template>

    <div class="by-wrap">
      <svg :width="W" :height="H" class="by-svg">
        <!-- 概率树：先验分支 → 似然分支 → 四种联合结果。先验概率写进节点框里，避免连线从文字中间穿过 -->
        <circle cx="44" cy="110" r="7" fill="#1f2733" />
        <text x="44" y="92" text-anchor="middle" font-size="11" fill="#1f2733">总体</text>

        <line x1="44" y1="110" x2="150" y2="66" :stroke="cur.stage >= 1 ? '#e05252' : '#c8d3e6'" :stroke-width="2 + 10 * Math.max(0.05, cur.p)" />
        <line x1="44" y1="110" x2="150" y2="162" :stroke="cur.stage >= 2 ? '#8b5cf6' : '#c8d3e6'" :stroke-width="2 + 10 * Math.max(0.05, 1 - cur.p)" />
        <rect x="150" y="46" width="104" height="40" rx="7" :fill="cur.stage >= 1 ? '#fdeaea' : '#f4f6fa'" :stroke="cur.stage >= 1 ? '#e05252' : '#c8d3e6'" />
        <text x="202" y="62" text-anchor="middle" font-size="11.5" fill="#1f2733">患病 D</text>
        <text x="202" y="78" text-anchor="middle" font-size="10.5" fill="#e05252">P(D) = {{ fmt(cur.p, 4) }}</text>
        <rect x="150" y="142" width="104" height="40" rx="7" :fill="cur.stage >= 2 ? '#f3ecff' : '#f4f6fa'" :stroke="cur.stage >= 2 ? '#8b5cf6' : '#c8d3e6'" />
        <text x="202" y="158" text-anchor="middle" font-size="11.5" fill="#1f2733">健康 ¬D</text>
        <text x="202" y="174" text-anchor="middle" font-size="10.5" fill="#7c3aed">P(¬D) = {{ fmt(1 - cur.p, 4) }}</text>

        <g v-for="(lf, i) in leaves" :key="'lf' + i">
          <line :x1="lf.x1" :y1="lf.y1" :x2="lf.x2" :y2="lf.y2" :stroke="lf.stroke" :stroke-width="lf.w" />
          <rect :x="lf.bx" :y="lf.by" :width="lf.bw" height="36" rx="7" :fill="lf.fill" :stroke="lf.stroke" />
          <text :x="lf.bx + 9" :y="lf.by + 15" font-size="10.5" font-weight="600" :fill="lf.text">{{ lf.label }}</text>
          <text :x="lf.bx + lf.bw - 9" :y="lf.by + 15" text-anchor="end" font-size="10.5" :fill="lf.text">{{ lf.countText }}</text>
          <text :x="lf.bx + 9" :y="lf.by + 30" font-size="10.5" :fill="lf.text">{{ lf.probText }}</text>
        </g>

        <!-- 面积图：段宽表示人数；图例等距排布，避免极窄段的标签叠在一起 -->
        <text x="16" y="232" font-size="11.5" fill="#8b95a3">面积图：每 10000 人的四种结局</text>
        <rect v-for="(s, i) in bars" :key="'b' + i" :x="s.x" y="242" :width="s.w" height="42" :fill="s.fill" :stroke="s.stroke" />
        <g v-for="(s, i) in bars" :key="'lg' + i">
          <rect :x="s.lx" y="294" width="10" height="10" rx="2" :fill="s.fill" :stroke="s.stroke" />
          <text :x="s.lx + 15" y="303" font-size="10.5" :fill="s.stroke">{{ s.legend }}</text>
        </g>

        <!-- 后验 = 阳性人群中「真阳」占的比例，用一条按比例切分的条形表示 -->
        <text x="16" y="330" font-size="11.5" fill="#1f2733">阳性人群 P(+) = {{ Math.round(cur.pos) }} 人（真阳 {{ Math.round(cur.nDP) }} + 假阳 {{ Math.round(cur.nHP) }}）</text>
        <rect x="16" y="340" width="480" height="18" rx="4" fill="#8b5cf6" fill-opacity="0.85" />
        <rect x="16" y="340" :width="posStat.trueW" height="18" rx="4" fill="#e05252" />
        <text x="16" y="378" font-size="11" fill="#c02b2b">后验 P(D|+) = 真阳 {{ Math.round(cur.nDP) }} / {{ Math.round(cur.pos) }} = {{ fmt(cur.post, 4) }}（{{ (cur.post * 100).toFixed(2) }}%）</text>
      </svg>

      <div class="by-panel">
        <div class="def-box">
          <div class="small muted">教材公式（浙大《概率论与数理统计》）</div>
          <code>全概率 P(+) = P(D)P(+|D) + P(¬D)P(+|¬D)
贝叶斯 P(D|+) = P(D)P(+|D) / P(+)</code>
        </div>
        <el-divider />
        <div class="info-row"><span>先验 P(D)</span><b>{{ fmt(cur.p, 4) }}</b></div>
        <div class="info-row"><span>似然 P(+|D)（灵敏度）</span><b style="color:var(--brand)">{{ fmt(cur.se, 3) }}</b></div>
        <div class="info-row"><span>似然 P(+|¬D)（假阳率）</span><b style="color:#7c3aed">{{ fmt(1 - cur.sp, 3) }}</b></div>
        <div class="info-row"><span>联合 P(D∩+)</span><b style="color:var(--danger)">{{ fmt(cur.p * cur.se, 5) }}</b></div>
        <div class="info-row"><span>联合 P(¬D∩+)</span><b style="color:#7c3aed">{{ fmt((1 - cur.p) * (1 - cur.sp), 5) }}</b></div>
        <div class="info-row"><span>全概率 P(+)</span><b>{{ fmt((cur.p * cur.se) + (1 - cur.p) * (1 - cur.sp), 5) }}</b></div>
        <div class="info-row"><span>后验 P(D|+)</span><el-tag size="small" :type="cur.post > 0.5 ? 'success' : 'warning'">{{ fmt(cur.post, 4) }}</el-tag></div>
        <el-divider />
        <div class="info-row"><span>每 10000 人：真阳 / 假阳</span><b>{{ Math.round(cur.nDP) }} / {{ Math.round(cur.nHP) }}</b></div>
        <p class="small muted tip">考点：先验概率（基础发病率）越低，即使检测很准，假阳性的绝对人数也会淹没真患者，后验概率远低于直觉 —— 这就是「基础概率谬误」。</p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#e05252"></i> 患病且阳性（真阳）</span>
      <span><i class="dot" style="background:#f7c9c9;border:1px solid #e05252"></i> 患病但阴性（漏检）</span>
      <span><i class="dot" style="background:#8b5cf6"></i> 健康但阳性（假阳）</span>
      <span><i class="dot" style="background:#dfe3ea"></i> 健康且阴性（真阴）</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const CASES = [
  { key: 'rare', label: '罕见病筛查', p: 0.001, se: 0.99, sp: 0.99 },
  { key: 'normal', label: '常见病筛查', p: 0.1, se: 0.95, sp: 0.95 },
  { key: 'hi', label: '高灵敏度试剂盒', p: 0.02, se: 0.99, sp: 0.9 }
]
const caseKey = ref('rare')
const pPct = ref(0.1)
const sePct = ref(99)
const spPct = ref(99)
function applyCase() {
  const c = CASES.find(x => x.key === caseKey.value) || CASES[0]
  pPct.value = c.p * 100; sePct.value = c.se * 100; spPct.value = c.sp * 100
  player.reset()
}

const W = 560, H = 390
const LEAF_X = 300, LEAF_MIN = 120, LEAF_MAX = 190
const POP = 10000 // 面积图的人口基数

// 一次试验的四种结局：nD, nH 为人数比例的分子
function measure(p, se, sp) {
  const nD = p * POP, nH = (1 - p) * POP
  const nDP = nD * se, nDN = nD * (1 - se), nHP = nH * (1 - sp), nHN = nH * sp
  const pos = nDP + nHP
  return { p, se, sp, nD, nH, nDP, nDN, nHP, nHN, pos, post: pos > 0 ? nDP / pos : 0 }
}

const steps = computed(() => {
  const out = []
  const p0 = Math.max(0.0001, Math.min(0.999, pPct.value / 100))
  const se = Math.max(0, Math.min(1, sePct.value / 100))
  const sp = Math.max(0, Math.min(1, spPct.value / 100))
  const m0 = measure(p0, se, sp)
  // 逐步揭示：先验 → 似然 → 全概率 → 后验
  out.push({ stage: 0, ...m0, desc: `先验：人群患病率 P(D) = ${(p0 * 100).toFixed(2)}%，每 ${POP} 人中约有 ${Math.round(m0.nD)} 名患者` })
  out.push({ stage: 1, ...m0, desc: `似然（患病者）：P(+|D) = ${se}，得到真阳性 P(D∩+) = ${p0}×${se} = ${(p0 * se).toFixed(5)}` })
  out.push({ stage: 2, ...m0, desc: `似然（健康者）：假阳率 P(+|¬D) = ${(1 - sp).toFixed(3)}，得到假阳性 P(¬D∩+) = ${((1 - p0) * (1 - sp)).toFixed(5)}` })
  out.push({ stage: 3, ...m0, desc: `全概率：P(+) = ${(p0 * se).toFixed(5)} + ${((1 - p0) * (1 - sp)).toFixed(5)} = ${(m0.pos / POP).toFixed(5)}，即每 ${POP} 人中有 ${Math.round(m0.pos)} 人检测阳性` })
  out.push({ stage: 4, ...m0, desc: `贝叶斯：P(D|+) = ${(p0 * se).toFixed(5)} / ${(m0.pos / POP).toFixed(5)} = ${(m0.post * 100).toFixed(2)}% —— 阳性者真患病概率` })
  // 改变基础发病率，观察后验随先验变化（基础概率谬误）
  const SWEEP = [0.0005, 0.002, 0.01, 0.03, 0.1, 0.2, 0.4]
  for (const p of SWEEP) {
    const mv = measure(p, se, sp)
    out.push({
      stage: 5, ...mv,
      desc: `把患病率调到 ${(p * 100).toFixed(2)}%：P(D|+) = ${(mv.post * 100).toFixed(2)}%（${Math.round(mv.nDP)} 真阳 / ${Math.round(mv.nHP)} 假阳）—— 似然不变，后验随先验提高`
    })
  }
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)

// 概率树的四片叶子：每行 36px 高，名称/人数/概率都写在框内，宽度只表示相对规模，绝不越出画布
const leaves = computed(() => {
  const c = cur.value
  const rows = [
    { name: 'D ∩ +', n: c.nDP, y: 22, color: '#e05252', fill: '#fdeaea', text: '#c02b2b' },
    { name: 'D ∩ -', n: c.nDN, y: 62, color: '#e8a13a', fill: '#fdf3e2', text: '#a5701a' },
    { name: '¬D ∩ +', n: c.nHP, y: 126, color: '#8b5cf6', fill: '#f3ecff', text: '#7c3aed' },
    { name: '¬D ∩ -', n: c.nHN, y: 166, color: '#8b95a3', fill: '#eef1f6', text: '#5b6472' }
  ]
  return rows.map((r, i) => {
    const parentY = i < 2 ? 66 : 162
    const w = Math.max(1.5, (r.n / POP) * 22)
    return {
      x1: 254, y1: parentY, x2: LEAF_X, y2: r.y + 18, stroke: r.color, w,
      bx: LEAF_X, by: r.y, bw: Math.max(LEAF_MIN, Math.min(LEAF_MAX, 90 + (r.n / POP) * 190)),
      fill: r.fill, text: r.text,
      label: r.name, countText: `${Math.round(r.n)} 人`, probText: `P = ${(r.n / POP).toFixed(4)}`
    }
  })
})

// 面积图：四种结局在总人口中的占比，横轴总宽表示全部人口
const bars = computed(() => {
  const c = cur.value
  const segs = [
    { n: c.nDP, fill: '#e05252', stroke: '#c02b2b', name: '真阳' },
    { n: c.nDN, fill: '#f7c9c9', stroke: '#e05252', name: '漏检' },
    { n: c.nHP, fill: '#8b5cf6', stroke: '#7c3aed', name: '假阳' },
    { n: c.nHN, fill: '#dfe3ea', stroke: '#8b95a3', name: '真阴' }
  ]
  let x = 16
  const total = 500
  // 图例固定等距排布：极窄的段也没法在原地放下标签，统一放到图例行避免文字互压
  const LX = [16, 150, 284, 418]
  return segs.map((s, i) => {
    const w = Math.max(2, (s.n / POP) * total)
    const b = { x, w, fill: s.fill, stroke: s.stroke, lx: LX[i], legend: `${s.name} ${Math.round(s.n)} 人` }
    x += w
    return b
  })
})

// 阳性人群内部构成：真阳占整条的比例 = 后验
const posStat = computed(() => {
  const pos = cur.value.pos || 0
  const t = pos > 0 ? Math.min(1, Math.max(0, cur.value.nDP / pos)) : 0
  return { trueW: Math.max(1, Math.min(480, 480 * t)) }
})

function fmt(v, d) {
  if (v === null || v === undefined || !isFinite(v)) return '-'
  return Number(v.toFixed(d || 3)).toString()
}
</script>

<style scoped>
.by-wrap { display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap; }
.by-svg { background: #fcfdff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.by-panel { flex: 1; min-width: 290px; }
.def-box code { background: #f2f4f8; padding: 8px 10px; border-radius: 6px; display: block; font-size: 12px; line-height: 1.7; white-space: pre-wrap; }
.info-row { display: flex; justify-content: space-between; align-items: center; gap: 10px; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.tip { margin-top: 10px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
