<template>
  <VisFrame title="快速排序 · 划分与递归" desc="挖坑法划分：取基准 pivot，双指针从两端扫描交换，递归处理左右子表" :player="player" :status-text="statusText" back-to="/knowledge/6">
    <template #extra>
      <el-input v-model="inputData" size="small" style="width:200px" placeholder="数组，逗号分隔" />
      <el-button size="small" @click="applyData">应用</el-button>
      <el-button size="small" plain @click="rebuild">重置</el-button>
    </template>

    <div class="qs-wrap">
      <svg :width="svgW" height="230" class="qs-svg">
        <!-- 递归区间底色 -->
        <rect
          v-for="(r, i) in ranges" :key="'r' + i"
          :x="r.x - 4" :y="r.y - 4" :width="r.w + 8" height="56" rx="6"
          :fill="r.color" opacity="0.35"
        />
        <text v-for="(r, i) in ranges" :key="'rt' + i" :x="r.x + r.w / 2" :y="r.y - 10" text-anchor="middle" font-size="10" :fill="r.text">
          {{ r.label }}
        </text>

        <g v-for="(v, i) in arr" :key="i" :transform="`translate(${i * (BAR_W + BAR_GAP)}, 40)`">
          <rect
            width="46" :height="barH(v)" y="0" rx="4"
            :fill="barFill(i)" :stroke="barStroke(i)" stroke-width="2"
          />
          <text x="23" :y="barH(v) + 18" text-anchor="middle" font-size="13" font-weight="600" :fill="barText(i)">{{ v }}</text>
          <text x="23" y="-14" text-anchor="middle" font-size="11" fill="#8b95a3">{{ i }}</text>
          <text v-if="i === pivotIdx" x="23" y="-28" text-anchor="middle" font-size="11" fill="#e8a13a" font-weight="700">pivot</text>
          <text v-else-if="i === iIdx" x="23" y="-28" text-anchor="middle" font-size="11" fill="#3b6ef6" font-weight="700">i</text>
          <text v-else-if="i === jIdx" x="23" y="-28" text-anchor="middle" font-size="11" fill="#e05252" font-weight="700">j</text>
        </g>
      </svg>

      <div class="qs-panel">
        <div class="info-row"><span>基准 pivot</span><b style="color:var(--warning)">{{ pivotVal ?? '-' }}</b></div>
        <div class="info-row"><span>左指针 i</span><b style="color:var(--brand)">{{ iIdx >= 0 ? iIdx : '-' }}</b></div>
        <div class="info-row"><span>右指针 j</span><b style="color:var(--danger)">{{ jIdx >= 0 ? jIdx : '-' }}</b></div>
        <div class="info-row"><span>递归深度</span><b>{{ depth }}</b></div>
        <div class="info-row"><span>比较次数</span><b>{{ compares }}</b></div>
        <div class="info-row"><span>移动次数</span><b>{{ moves }}</b></div>
        <el-divider />
        <div class="panel-title">递归调用栈</div>
        <div class="call-stack">
          <div v-for="(c, i) in callStack" :key="i" class="call-item">quickSort({{ c.l }}, {{ c.r }})</div>
          <span v-if="!callStack.length" class="small muted">（空）</span>
        </div>
        <div class="tip small muted">
          平均时间复杂度 O(n log n)，最坏（序列有序）退化为 O(n²)；<b>不稳定</b>排序。
        </div>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#e8a13a"></i> 基准 pivot</span>
      <span><i class="dot" style="background:#3b6ef6"></i> 左指针 i</span>
      <span><i class="dot" style="background:#e05252"></i> 右指针 j</span>
      <span><i class="dot" style="background:#22a06b"></i> 已归位元素</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const BAR_W = 46
const BAR_GAP = 8

const inputData = ref('49,38,65,97,76,13,27')
const data = ref([49, 38, 65, 97, 76, 13, 27])
const defaultData = [49, 38, 65, 97, 76, 13, 27]

const steps = computed(() => {
  const a = [...data.value]
  const out = []
  let compares = 0
  let moves = 0
  const stack = []

  function snap(desc, extra = {}) {
    out.push({
      arr: [...a], compares, moves, stack: stack.map(s => ({ ...s })),
      done: [...doneSet], desc, ...extra
    })
  }
  const doneSet = new Set()

  function quickSort(l, r) {
    if (l >= r) {
      if (l === r) doneSet.add(l)
      return
    }
    stack.push({ l, r })
    snap(`进入 quickSort(${l}, ${r})，取 a[${l}]=${a[l]} 作为基准 pivot`, {
      pivot: l, i: l, j: r, depth: stack.length
    })
    const pivot = a[l]
    let i = l
    let j = r
    while (i < j) {
      while (i < j && a[j] >= pivot) { compares++; j--; snap(`右指针 j 左移寻找 < ${pivot} 的元素 → j=${j}`, { pivot: l, i, j, depth: stack.length }) }
      if (i < j) { a[i] = a[j]; moves++; snap(`a[j]=${a[j]} 小于基准，填到左坑 a[${i}]`, { pivot: -1, i, j, pval: pivot, depth: stack.length }) }
      while (i < j && a[i] <= pivot) { compares++; i++; snap(`左指针 i 右移寻找 > ${pivot} 的元素 → i=${i}`, { pivot: -1, i, j, pval: pivot, depth: stack.length }) }
      if (i < j) { a[j] = a[i]; moves++; snap(`a[i]=${a[i]} 大于基准，填到右坑 a[${j}]`, { pivot: -1, i, j, pval: pivot, depth: stack.length }) }
    }
    a[i] = pivot
    doneSet.add(i)
    snap(`i == j == ${i}，基准 ${pivot} 归位：左侧均 ≤ 它，右侧均 ≥ 它`, { pivot: -1, i: -1, j: -1, placed: i, depth: stack.length })
    stack.pop()
    quickSort(l, i - 1)
    quickSort(i + 1, r)
    if (stack.length) snap(`子表处理完毕，返回上层递归`, { pivot: -1, i: -1, j: -1, depth: stack.length })
  }

  snap('初始序列，开始快速排序', { pivot: -1, i: -1, j: -1, depth: 0 })
  quickSort(0, a.length - 1)
  for (let k = 0; k < a.length; k++) doneSet.add(k)
  snap(`排序完成：[${a.join(', ')}]`, { pivot: -1, i: -1, j: -1, depth: 0 })
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const arr = computed(() => cur.value.arr || [])
const statusText = computed(() => cur.value.desc)
const pivotIdx = computed(() => cur.value.pivot ?? -1)
const iIdx = computed(() => cur.value.i ?? -1)
const jIdx = computed(() => cur.value.j ?? -1)
const pivotVal = computed(() => (pivotIdx.value >= 0 ? arr.value[pivotIdx.value] : (cur.value.pval ?? null)))
const depth = computed(() => cur.value.depth || 0)
const compares = computed(() => cur.value.compares || 0)
const moves = computed(() => cur.value.moves || 0)
const callStack = computed(() => cur.value.stack || [])
const doneSet = computed(() => new Set(cur.value.done || []))

const svgW = computed(() => arr.value.length * (BAR_W + BAR_GAP) + 20)

// 柱高按当前数组最大值归一化：以前写死 v*2.2，值一上 100 柱子和文字直接冲出画布
const BAR_MAX_H = 150
const maxV = computed(() => Math.max(1, ...arr.value.map(v => Math.abs(Number(v) || 0))))
function barH(v) { return Math.max(10, Math.round((Math.abs(Number(v) || 0) / maxV.value) * BAR_MAX_H)) }

const ranges = computed(() => {
  const s = callStack.value
  if (!s.length) return []
  const top = s[s.length - 1]
  return s.map((r, idx) => ({
    x: r.l * (BAR_W + BAR_GAP),
    w: (r.r - r.l + 1) * (BAR_W + BAR_GAP) - BAR_GAP,
    y: 36,
    color: idx === s.length - 1 ? '#3b6ef6' : '#c8d3e6',
    text: idx === s.length - 1 ? '#3b6ef6' : '#8b95a3',
    label: `[${r.l}, ${r.r}]`
  }))
})

function barFill(i) {
  if (i === pivotIdx.value) return '#fdf3e2'
  if (i === iIdx.value) return '#e6eeff'
  if (i === jIdx.value) return '#fdeaea'
  if (doneSet.value.has(i)) return '#dcf3e7'
  return '#fff'
}
function barStroke(i) {
  if (i === pivotIdx.value) return '#e8a13a'
  if (i === iIdx.value) return '#3b6ef6'
  if (i === jIdx.value) return '#e05252'
  if (doneSet.value.has(i)) return '#22a06b'
  return '#c8d3e6'
}
function barText(i) {
  if (i === pivotIdx.value) return '#a5701a'
  if (i === jIdx.value) return '#a32c2c'
  if (doneSet.value.has(i)) return '#176b48'
  return '#1f2733'
}

function applyData() {
  const list = inputData.value.split(/[,，\s]+/).map(v => Number(v.trim())).filter(v => !isNaN(v))
  if (list.length) { data.value = list; player.reset() }
}
function rebuild() {
  data.value = [...defaultData]
  inputData.value = defaultData.join(',')
  player.reset()
}
</script>

<style scoped>
.qs-wrap { display: flex; gap: 24px; align-items: flex-start; flex-wrap: wrap; }
.qs-svg { flex-shrink: 0; background: #fbfcff; border-radius: 8px; }
.qs-panel { flex: 1; min-width: 240px; }
.info-row { display: flex; justify-content: space-between; padding: 4px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.panel-title { font-size: 13px; font-weight: 600; margin-bottom: 6px; color: var(--text-2); }
.call-stack { border: 1px dashed var(--border); border-radius: 8px; padding: 8px; min-height: 50px; display: flex; flex-direction: column-reverse; gap: 4px; background: #fbfcff; }
.call-item { background: #eef3ff; border: 1px solid #cfe0ff; border-radius: 4px; padding: 3px 10px; font-size: 12px; text-align: center; }
.tip { margin-top: 10px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
