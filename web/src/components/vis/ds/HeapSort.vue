<template>
  <VisFrame title="堆与堆排序 · 大顶堆" desc="先自下而上筛选建大顶堆，再反复「交换堆顶与末尾 + 筛选」，大顶堆得到升序序列" :player="player" :status-text="statusText" back-to="/knowledge/37">
    <template #extra>
      <el-input v-model="inputData" size="small" style="width:210px" placeholder="数组，逗号分隔" />
      <el-button size="small" @click="applyData">应用</el-button>
      <el-button size="small" plain @click="rebuild">重置</el-button>
    </template>

    <div class="hs-wrap">
      <svg :width="svgW" :height="svgH" class="hs-svg">
        <!-- 数组视图 -->
        <g v-for="(v, i) in arr" :key="'a' + i" :transform="`translate(${i * 46}, 12)`">
          <rect width="42" height="36" rx="5" :fill="arrFill(i)" :stroke="arrStroke(i)" stroke-width="2" />
          <text x="21" y="24" text-anchor="middle" font-size="14" font-weight="600" :fill="arrText(i)">{{ v }}</text>
          <text x="21" y="50" text-anchor="middle" font-size="11" fill="#8b95a3">{{ i + 1 }}</text>
        </g>
        <text y="76" font-size="11" fill="#8b95a3">数组视图（下标从 1 起）：蓝色=当前筛选位置，橙色=本步交换的两元素，绿色=已归位</text>
        <!-- 完全二叉树视图 -->
        <line v-for="(e, i) in edges" :key="'e' + i" :x1="e.x1" :y1="e.y1" :x2="e.x2" :y2="e.y2" stroke="#c8d3e6" stroke-width="1.5" />
        <g v-for="(v, i) in arr" :key="'t' + i" :transform="`translate(${tx(i)}, ${ty(i)})`">
          <circle r="18" :fill="treeFill(i)" :stroke="treeStroke(i)" stroke-width="2" :opacity="inHeap(i) ? 1 : 0.45" />
          <text y="5" text-anchor="middle" font-size="13" font-weight="600" :fill="treeText(i)" :opacity="inHeap(i) ? 1 : 0.45">{{ v }}</text>
          <text y="-24" text-anchor="middle" font-size="10" fill="#8b95a3">{{ i + 1 }}</text>
        </g>
        <text :x="tx(0)" :y="ty(0) - 34" text-anchor="middle" font-size="11" fill="#e8a13a" font-weight="700">堆顶 a[1]</text>
      </svg>

      <div class="hs-panel">
        <div class="info-row"><span>当前阶段</span><b>{{ phase }}</b></div>
        <div class="info-row"><span>堆大小 heap</span><b>{{ heapSize }}</b></div>
        <div class="info-row"><span>筛选位置 i</span><b style="color:var(--brand)">{{ hl >= 0 ? hl + 1 : '-' }}</b></div>
        <div class="info-row"><span>比较 / 移动</span><b>{{ compares }} / {{ moves }}</b></div>
        <div class="info-row"><span>已归位</span><b style="color:var(--success)">{{ sortedCount }}</b></div>
        <el-divider />
        <div class="tip small muted">
          完全二叉树性质：编号 i 的左孩子 2i、右孩子 2i+1、双亲 ⌊i/2⌋；最后一个非终端结点为 ⌊n/2⌋。<br />
          <b>考点：</b>建堆 O(n)，每趟筛选 O(log n)，总体 <b>O(n log n)</b>；空间 O(1)；<b>不稳定</b>；
          最坏/最好/平均均为 O(n log n)，适合取 Top-K。
        </div>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> 当前筛选结点</span><span><i class="dot" style="background:#e8a13a"></i> 交换的两个元素</span>
      <span><i class="dot" style="background:#22a06b"></i> 已归位（移出堆）</span><span><i class="dot" style="background:#c8d3e6"></i> 堆内普通结点</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const UNIT = 56, LV = 58, TY = 148
const defaultData = [49, 38, 65, 97, 76, 13, 27, 49]
const inputData = ref(defaultData.join(','))
const data = ref([...defaultData])

const steps = computed(() => {
  const a = [...data.value]
  const n = a.length
  const out = []
  const sorted = new Set()
  let compares = 0, moves = 0
  // 快照：数组副本 + 已归位集合 + 当前筛选位置(hl) + 本步交换对(sw) + 堆大小(heap)
  function snap(desc, extra = {}) {
    out.push({ arr: [...a], sorted: [...sorted], compares, moves, desc, hl: -1, sw: null, heap: n, phase: '建堆', mark: 'none', ...extra })
  }
  function sift(i, size) {                       // 筛选：小元素逐层下沉
    while (true) {
      const l = 2 * i + 1, r = 2 * i + 2
      let big = i
      if (l < size) { compares++; if (a[l] > a[big]) big = l }
      if (r < size) { compares++; if (a[r] > a[big]) big = r }
      // mark 区分「刚移到这一层，准备比较」和「比较后确认已满足堆性质」：
      // 两者数组与高亮位置都一样，没有 mark 的话画面会连续两步纹丝不动。
      if (big === i) { snap(`结点 ${i + 1}(${a[i]}) 已 ≥ 左右孩子，筛选结束`, { hl: i, heap: size, mark: 'settle' }); return }
      snap(`孩子 ${big + 1}(${a[big]}) > 双亲 ${i + 1}(${a[i]})，交换使大者上浮`, { hl: i, sw: [i, big], heap: size, mark: 'swap' })
      const t = a[i]; a[i] = a[big]; a[big] = t; moves++
      snap(`交换后继续向下筛选 → 结点 ${big + 1}`, { hl: big, heap: size, mark: 'move' })
      i = big
    }
  }
  snap('初始序列，按层序编号视为一棵完全二叉树', { phase: '初始' })
  for (let i = Math.floor(n / 2) - 1; i >= 0; i--) {
    snap(`建堆：对最后一个非终端结点 ${i + 1} 向下筛选（自下而上、从右到左）`, { hl: i, heap: n, mark: 'move' })
    sift(i, n)
  }
  snap(`大顶堆建成：堆顶 a[1] = ${a[0]} 为最大值（建堆共比较 ${compares} 次）`, { hl: 0, heap: n })
  for (let m = n - 1; m >= 1; m--) {
    const t = a[0]; a[0] = a[m]; a[m] = t; moves++
    sorted.add(m)
    snap(`第 ${n - m} 趟：堆顶 ${a[m]} 与末尾交换后归位，堆大小缩为 ${m}`, { sw: [0, m], hl: m, heap: m, phase: '排序' })
    sift(0, m)
  }
  sorted.add(0)
  snap(`排序完成：[${a.join(', ')}]（比较 ${compares} 次、移动 ${moves} 次）`, { heap: 0, phase: '完成' })
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const arr = computed(() => cur.value.arr || [])
const sortedSet = computed(() => new Set(cur.value.sorted || []))
const hl = computed(() => cur.value.hl ?? -1)
const sw = computed(() => cur.value.sw || null)
const heapSize = computed(() => cur.value.heap ?? 0)
const mark = computed(() => cur.value.mark || 'none')
const compares = computed(() => cur.value.compares || 0)
const moves = computed(() => cur.value.moves || 0)
const phase = computed(() => cur.value.phase || '建堆')
const sortedCount = computed(() => sortedSet.value.size)

const maxL = computed(() => (arr.value.length ? Math.floor(Math.log2(arr.value.length)) : 0))
const treeW = computed(() => Math.pow(2, maxL.value) * UNIT)
const svgW = computed(() => Math.max(arr.value.length * 46 + 20, treeW.value + 60))
const svgH = computed(() => TY + (maxL.value + 1) * LV)

// 完全二叉树：第 i 个结点在第 L 层的第 pos 个位置
function tx(i) {
  const L = Math.floor(Math.log2(i + 1)), pos = i + 1 - Math.pow(2, L)
  return (treeW.value / Math.pow(2, L)) * (pos + 0.5)
}
function ty(i) { return TY + Math.floor(Math.log2(i + 1)) * LV }
const edges = computed(() => arr.value.map((_, i) => i).slice(1).map(i => ({ x1: tx(Math.floor((i - 1) / 2)), y1: ty(Math.floor((i - 1) / 2)), x2: tx(i), y2: ty(i) })))
function inHeap(i) { return i < heapSize.value || heapSize.value === 0 }

// settle = 该结点已满足堆性质（筛选结束），与「刚移到这里准备比较」的 move 用不同配色，
// 否则连续两步画面完全一致，看不出动画在推进。
const COLORS = {
  swap: { fill: '#fdf3e2', stroke: '#e8a13a', text: '#a5701a' },
  move: { fill: '#e6eeff', stroke: '#3b6ef6', text: '#1a47b8' },
  settle: { fill: '#eafaf1', stroke: '#22a06b', text: '#176b48' },
}
function arrFill(i) {
  if (sw.value && (i === sw.value[0] || i === sw.value[1])) return COLORS.swap.fill
  if (sortedSet.value.has(i)) return '#dcf3e7'
  if (i === hl.value) return (COLORS[mark.value] || COLORS.move).fill
  return '#ffffff'
}
function arrStroke(i) {
  if (sw.value && (i === sw.value[0] || i === sw.value[1])) return COLORS.swap.stroke
  if (sortedSet.value.has(i)) return '#22a06b'
  if (i === hl.value) return (COLORS[mark.value] || COLORS.move).stroke
  return '#c8d3e6'
}
function arrText(i) {
  if (sw.value && (i === sw.value[0] || i === sw.value[1])) return COLORS.swap.text
  if (sortedSet.value.has(i)) return '#176b48'
  if (i === hl.value) return (COLORS[mark.value] || COLORS.move).text
  return '#1f2733'
}
const treeFill = arrFill
const treeStroke = arrStroke
const treeText = arrText

function applyData() {
  const list = inputData.value.split(/[,，\s]+/).map(v => Number(v.trim())).filter(v => !isNaN(v))
  if (list.length) { data.value = list; player.reset() }
}
function rebuild() { data.value = [...defaultData]; inputData.value = defaultData.join(','); player.reset() }
</script>

<style scoped>
.hs-wrap { display: flex; gap: 24px; align-items: flex-start; flex-wrap: wrap; }
.hs-svg { flex-shrink: 0; background: #fbfcff; border-radius: 8px; }
.hs-panel { flex: 1; min-width: 250px; }
.info-row { display: flex; justify-content: space-between; gap: 10px; padding: 4px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.tip { line-height: 1.8; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
