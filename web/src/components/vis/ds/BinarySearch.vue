<template>
  <VisFrame title="折半查找 · 判定树" desc="有序顺序表上每次与 mid = ⌊(low+high)/2⌋ 比较，成功/失败过程等价于在判定树上走一条从根到某结点的路径" :player="player" :status-text="statusText" back-to="/knowledge/40">
    <template #extra>
      <el-radio-group v-model="mode" size="small">
        <el-radio-button value="binary">折半查找</el-radio-button><el-radio-button value="seq">顺序查找</el-radio-button>
      </el-radio-group>
      <el-input v-model="inputData" size="small" style="width:210px" placeholder="有序表，逗号分隔" />
      <el-input v-model="keyInput" size="small" style="width:80px" placeholder="key" />
      <el-button size="small" @click="applyData">应用</el-button>
      <el-button size="small" plain @click="resetAll">重置</el-button>
    </template>

    <div class="bs-wrap">
      <svg :width="tree.w" :height="tree.h" class="bs-svg">
        <!-- 有序表 -->
        <g v-for="(v, i) in arr" :key="'c' + i" :transform="`translate(${i * 46}, 12)`">
          <rect width="42" height="34" rx="5" :fill="cellFill(i)" :stroke="cellStroke(i)" stroke-width="2" />
          <text x="21" y="23" text-anchor="middle" font-size="13" font-weight="600" :fill="cellText(i)">{{ v }}</text>
          <text x="21" y="50" text-anchor="middle" font-size="11" fill="#8b95a3">{{ i + 1 }}</text>
        </g>
        <text v-if="low >= 0 && low < arr.length" :x="low * 46 + 21" y="80" text-anchor="middle" font-size="12" fill="#3b6ef6" font-weight="700">low</text>
        <text v-if="high >= 0 && high < arr.length" :x="high * 46 + 21" y="80" text-anchor="middle" font-size="12" fill="#e05252" font-weight="700">high</text>
        <text v-if="mid >= 0 && mid < arr.length" :x="mid * 46 + 21" y="-2" text-anchor="middle" font-size="12" fill="#e8a13a" font-weight="700">mid</text>
        <text v-if="seq >= 0 && seq < arr.length" :x="seq * 46 + 21" y="80" text-anchor="middle" font-size="12" fill="#e8a13a" font-weight="700">↑i</text>
        <!-- 判定树 -->
        <text x="2" y="104" font-size="12" fill="#5a6472">判定树（圆=成功结点，方=失败结点）：</text>
        <line v-for="(e, i) in tree.edges" :key="'e' + i" :x1="e.x1" :y1="e.y1" :x2="e.x2" :y2="e.y2" stroke="#c8d3e6" stroke-width="1.5" />
        <g v-for="n in tree.nodes" :key="n.id" :transform="`translate(${n.x}, ${n.y})`">
          <rect v-if="n.fail" x="-11" y="-11" width="22" height="22" rx="3" :fill="nodeFill(n)" :stroke="nodeStroke(n)" stroke-width="1.6" />
          <circle v-else r="17" :fill="nodeFill(n)" :stroke="nodeStroke(n)" stroke-width="2" />
          <text v-if="!n.fail" y="5" text-anchor="middle" font-size="12" font-weight="600" :fill="nodeText(n)">{{ n.val }}</text>
          <text v-if="!n.fail" y="-24" text-anchor="middle" font-size="10" fill="#8b95a3">第 {{ n.depth + 1 }} 层</text>
        </g>
      </svg>

      <div class="bs-panel">
        <div class="info-row"><span>查找方式</span><b>{{ mode === 'binary' ? '折半查找' : '顺序查找' }}</b></div>
        <div class="info-row"><span>low / mid / high</span><b>{{ low >= 0 ? low + 1 : '-' }} / {{ mid >= 0 ? mid + 1 : '-' }} / {{ high >= 0 ? high + 1 : '-' }}</b></div>
        <div class="info-row"><span>比较次数</span><b style="color:var(--brand)">{{ cmp }}</b></div>
        <div class="info-row"><span>查找结果</span><b :style="{ color: found ? 'var(--success)' : 'var(--danger)' }">{{ resultText }}</b></div>
        <div class="info-row"><span>成功 ASL</span><b>{{ asl }}</b></div>
        <el-divider />
        <div class="tip small muted">
          判定树：mid 为根，左半区为左子树、右半区为右子树；树高 ⌊log₂n⌋+1，<b>成功 ASL ≈ log₂(n+1) - 1</b>，
          时间复杂度 <b>O(log n)</b>；失败结点个数为 n+1（即外结点）。<br />
          折半只适用于<b>顺序存储的有序表</b>（链表无法随机访问）；顺序查找 ASL = (n+1)/2，O(n)，但对存储与有序性无要求。
        </div>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#e8a13a"></i> mid / 当前比较</span><span><i class="dot" style="background:#3b6ef6"></i> low 指针</span>
      <span><i class="dot" style="background:#e05252"></i> high 指针</span><span><i class="dot" style="background:#22a06b"></i> 查找成功</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const GAP = 44, LH = 54, TY = 132
const defaultData = [5, 13, 19, 21, 37, 56, 64, 75, 80, 88, 92]
const inputData = ref(defaultData.join(','))
const data = ref([...defaultData])
const keyInput = ref('21')
const mode = ref('binary')
const sorted = computed(() => [...data.value].sort((x, y) => x - y))

const steps = computed(() => {
  const a = sorted.value
  const n = a.length
  const k = Number(keyInput.value)
  const out = []
  let cmp = 0
  // 快照：有序表 + low/mid/high（0 基）+ 顺序查找游标 seq + 比较次数 + 是否命中
  function snap(desc, extra = {}) { out.push({ low: -1, mid: -1, high: -1, seq: -1, cmp, found: false, pos: -1, desc, ...extra }) }
  if (!n) { snap('有序表为空，无法查找', {}); return out }
  if (mode.value === 'seq') {
    snap(`顺序查找：从 a[1] 起逐个比较，查找 ${k}（设监视哨可免去每次判断越界）`, {})
    let i = 0
    while (i < n) {
      cmp++
      if (a[i] === k) { snap(`第 ${cmp} 次比较：a[${i + 1}] = ${k}，查找成功（位置 ${i + 1}）`, { seq: i, found: true, pos: i }); break }
      snap(`第 ${cmp} 次比较：a[${i + 1}] = ${a[i]} ≠ ${k}，指针后移`, { seq: i })
      i++
    }
    if (i >= n) snap(`扫完整表未找到 ${k}，查找失败：共比较 ${cmp} 次（顺序查找 ASL = (n+1)/2 = ${((n + 1) / 2).toFixed(1)}）`, {})
    return out
  }
  snap(`初始：low = 1，high = ${n}，查找关键字 ${k}`, { low: 0, high: n - 1 })
  let lo = 0, hi = n - 1, ok = false
  while (lo <= hi) {
    const m = (lo + hi) >> 1
    cmp++
    snap(`mid = ⌊(low+high)/2⌋ = ${m + 1}，第 ${cmp} 次比较：a[${m + 1}] = ${a[m]} 与 ${k}`, { low: lo, high: hi, mid: m })
    if (a[m] === k) { ok = true; snap(`相等：查找成功，${k} 在第 ${m + 1} 位，共比较 ${cmp} 次`, { low: lo, high: hi, mid: m, found: true, pos: m }); break }
    if (k < a[m]) { hi = m - 1; snap(`${k} < ${a[m]}：high = mid - 1 = ${hi + 1}，缩小到左半区`, { low: lo, high: hi, mid: m }) }
    else { lo = m + 1; snap(`${k} > ${a[m]}：low = mid + 1 = ${lo + 1}，缩小到右半区`, { low: lo, high: hi, mid: m }) }
  }
  if (!ok) snap(`low(${lo + 1}) > high(${hi + 1})：区间为空，查找失败，共比较 ${cmp} 次`, { low: lo, high: hi })
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const arr = computed(() => sorted.value)
const low = computed(() => cur.value.low ?? -1)
const mid = computed(() => cur.value.mid ?? -1)
const high = computed(() => cur.value.high ?? -1)
const seq = computed(() => cur.value.seq ?? -1)
const cmp = computed(() => cur.value.cmp || 0)
const found = computed(() => !!cur.value.found)
const resultText = computed(() => (found.value ? `成功，位于第 ${cur.value.pos + 1} 位` : cmp.value ? '尚未命中 / 查找失败' : '待查找'))

// 判定树：mid 为根，递归构造左右子树，空区间即失败结点
const tree = computed(() => {
  const a = arr.value
  const nodes = [], edges = []
  let id = 0
  function build(l, r, d) {
    const t = { id: id++, l, r, depth: d, fail: l > r, val: null, mid: -1, left: null, right: null }
    if (!t.fail) { t.mid = (l + r) >> 1; t.val = a[t.mid] }
    nodes.push(t)
    if (!t.fail) { t.left = build(l, t.mid - 1, d + 1); t.right = build(t.mid + 1, r, d + 1) }
    return t
  }
  const root = a.length ? build(0, a.length - 1, 0) : null
  let i = 0, maxD = 0
  ;(function walk(t) {
    if (!t) return
    walk(t.left); t.x = 30 + (i++) * GAP; t.y = TY + t.depth * LH; if (t.depth > maxD) maxD = t.depth; walk(t.right)
  })(root)
  ;(function link(t) {
    if (!t) return
    for (const c of [t.left, t.right]) if (c) { edges.push({ x1: t.x, y1: t.y, x2: c.x, y2: c.y }); link(c) }
  })(root)
  return { nodes, edges, w: Math.max(560, i * GAP + 40), h: TY + (maxD + 1) * LH + 24 }
})

const asl = computed(() => {
  const ns = tree.value.nodes.filter(n => !n.fail)
  if (!ns.length) return '-'
  return (ns.reduce((s, n) => s + n.depth + 1, 0) / ns.length).toFixed(2)
})

function cellFill(i) {
  if (found.value && i === cur.value.pos) return '#dcf3e7'
  if (i === mid.value || i === seq.value) return '#fdf3e2'
  if (i >= low.value && i <= high.value && low.value >= 0) return '#e6eeff'
  return '#ffffff'
}
function cellStroke(i) {
  if (found.value && i === cur.value.pos) return '#22a06b'
  if (i === mid.value || i === seq.value) return '#e8a13a'
  if (i === low.value) return '#3b6ef6'
  if (i === high.value) return '#e05252'
  if (i > low.value && i < high.value && low.value >= 0) return '#a9c6ff'
  return '#c8d3e6'
}
function cellText(i) { return cellStroke(i) === '#c8d3e6' ? '#1f2733' : '#176b48' }
function nodeFill(n) { return n.fail ? '#f4f6fa' : (n.val === Number(keyInput.value) && found.value ? '#dcf3e7' : '#ffffff') }
function nodeStroke(n) { return n.fail ? '#c8d3e6' : (n.val === Number(keyInput.value) && found.value ? '#22a06b' : '#3b6ef6') }
function nodeText(n) { return n.val === Number(keyInput.value) && found.value ? '#176b48' : '#1f2733' }

function applyData() {
  const list = inputData.value.split(/[,，\s]+/).map(v => Number(v.trim())).filter(v => !isNaN(v))
  if (list.length) { data.value = list; player.reset() }
}
function resetAll() { data.value = [...defaultData]; inputData.value = defaultData.join(','); keyInput.value = '21'; player.reset() }
</script>

<style scoped>
.bs-wrap { display: flex; gap: 24px; align-items: flex-start; flex-wrap: wrap; }
.bs-svg { flex-shrink: 0; background: #fbfcff; border-radius: 8px; }
.bs-panel { flex: 1; min-width: 250px; }
.info-row { display: flex; justify-content: space-between; gap: 10px; padding: 4px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.tip { line-height: 1.8; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
