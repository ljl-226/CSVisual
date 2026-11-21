<template>
  <VisFrame title="归并排序 · 分治与二路归并" desc="先递归划分到单个元素，再两两合并成有序序列；时间复杂度稳定 O(n log n)" :player="player" :status-text="statusText" back-to="/knowledge/7">
    <template #extra>
      <el-input v-model="inputData" size="small" style="width:200px" placeholder="数组，逗号分隔" />
      <el-button size="small" @click="applyData">应用</el-button>
      <el-button size="small" plain @click="rebuild">重置</el-button>
    </template>

    <div class="ms-wrap">
      <div class="ms-main">
        <svg :width="svgW" height="200" class="ms-svg">
          <g v-for="(v, i) in arr" :key="i" :transform="`translate(${i * 54}, 46)`">
            <rect
              width="46" :height="barH(v)" rx="4"
              :fill="barFill(i)" :stroke="barStroke(i)" stroke-width="2"
            />
            <text x="23" :y="barH(v) + 18" text-anchor="middle" font-size="13" font-weight="600" :fill="barText(i)">{{ v }}</text>
            <text x="23" y="-12" text-anchor="middle" font-size="11" fill="#8b95a3">{{ i }}</text>
          </g>
          <!-- 当前处理区间 -->
          <rect
            v-if="range"
            :x="range.l * 54 - 5" :y="38" :width="(range.r - range.l + 1) * 54 - 8" height="30" rx="6"
            fill="none" stroke="#3b6ef6" stroke-width="1.6" stroke-dasharray="4 3"
          />
          <text v-if="range" :x="(range.l + range.r + 1) / 2 * 54 - 4" y="30" text-anchor="middle" font-size="11" fill="#3b6ef6">
            归并区间 [{{ range.l }}, {{ range.r }}]
          </text>
        </svg>

        <div class="aux-box">
          <span class="small muted">辅助数组（合并结果）</span>
          <div class="aux-row">
            <span v-for="(t, i) in tmp" :key="i" class="aux-item">{{ t }}</span>
            <span v-if="!tmp.length" class="small muted">（空）</span>
          </div>
        </div>
      </div>

      <div class="ms-panel">
        <div class="info-row"><span>当前归并区间</span><b>{{ range ? `[${range.l}, ${range.r}]` : '-' }}</b></div>
        <div class="info-row"><span>左半指针 i</span><b style="color:var(--brand)">{{ iPos >= 0 ? iPos : '-' }}</b></div>
        <div class="info-row"><span>右半指针 j</span><b style="color:var(--danger)">{{ jPos >= 0 ? jPos : '-' }}</b></div>
        <div class="info-row"><span>比较次数</span><b>{{ compares }}</b></div>
        <div class="info-row"><span>归并趟数</span><b>{{ Math.ceil(Math.log2(arr.length || 1)) }}</b></div>
        <el-divider />
        <div class="panel-title">递归分解过程</div>
        <div class="tree-view">
          <div v-for="(t, i) in treeLog" :key="i" class="tree-item" :class="{ active: i === treeLog.length - 1 }">
            <span class="tl">[{{ t.l }}, {{ t.r }}]</span>
            <span class="tr">{{ t.text }}</span>
          </div>
          <span v-if="!treeLog.length" class="small muted">（空）</span>
        </div>
        <div class="tip small muted">
          二路归并：需要 O(n) 辅助空间，<b>稳定</b>排序，时间复杂度与初始序列无关。
        </div>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> 左半部分指针</span>
      <span><i class="dot" style="background:#e05252"></i> 右半部分指针</span>
      <span><i class="dot" style="background:#22a06b"></i> 已排好序的子序列</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const inputData = ref('49,38,65,97,76,13,27')
const data = ref([49, 38, 65, 97, 76, 13, 27])
const defaultData = [49, 38, 65, 97, 76, 13, 27]

const steps = computed(() => {
  const a = [...data.value]
  const out = []
  let compares = 0
  const treeLog = []
  const sorted = new Set()

  function snap(desc, extra = {}) {
    out.push({
      arr: [...a], compares, sorted: [...sorted], treeLog: [...treeLog],
      tmp: extra.tmp ? [...extra.tmp] : [], desc,
      range: extra.range || null, i: extra.i ?? -1, j: extra.j ?? -1
    })
  }

  function merge(l, mid, r) {
    const tmp = []
    let i = l
    let j = mid + 1
    snap(`归并 [${l},${mid}] 与 [${mid + 1},${r}]：双指针取小者放入辅助数组`, { range: { l, r }, i, j, tmp })
    while (i <= mid && j <= r) {
      compares++
      if (a[i] <= a[j]) {
        tmp.push(a[i])
        snap(`a[${i}]=${a[i]} ≤ a[${j}]=${a[j]}，取左半元素 ${a[i]}`, { range: { l, r }, i, j, tmp })
        i++
      } else {
        tmp.push(a[j])
        snap(`a[${i}]=${a[i]} > a[${j}]=${a[j]}，取右半元素 ${a[j]}`, { range: { l, r }, i, j, tmp })
        j++
      }
    }
    while (i <= mid) { tmp.push(a[i]); snap(`左半剩余元素 ${a[i]} 直接追加`, { range: { l, r }, i, j, tmp }); i++ }
    while (j <= r) { tmp.push(a[j]); snap(`右半剩余元素 ${a[j]} 直接追加`, { range: { l, r }, i, j, tmp }); j++ }
    for (let k = 0; k < tmp.length; k++) a[l + k] = tmp[k]
    for (let k = l; k <= r; k++) sorted.add(k)
    treeLog.push({ l, r, text: `合并完成 → [${tmp.join(', ')}]` })
    snap(`辅助数组写回 a[${l}..${r}]：${tmp.join(', ')}`, { range: { l, r }, i: -1, j: -1, tmp })
  }

  function mergeSort(l, r) {
    if (l >= r) {
      if (l === r) sorted.add(l)
      return
    }
    const mid = Math.floor((l + r) / 2)
    treeLog.push({ l, r, text: `划分为 [${l},${mid}] 和 [${mid + 1},${r}]` })
    snap(`划分 [${l}, ${r}] → 左 [${l}, ${mid}]、右 [${mid + 1}, ${r}]`, { range: { l, r } })
    mergeSort(l, mid)
    mergeSort(mid + 1, r)
    merge(l, mid, r)
  }

  snap('初始序列，开始归并排序')
  mergeSort(0, a.length - 1)
  for (let k = 0; k < a.length; k++) sorted.add(k)
  snap(`排序完成：[${a.join(', ')}]`)
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const arr = computed(() => cur.value.arr || [])
const tmp = computed(() => cur.value.tmp || [])
const statusText = computed(() => cur.value.desc)
const range = computed(() => cur.value.range)
const iPos = computed(() => cur.value.i ?? -1)
const jPos = computed(() => cur.value.j ?? -1)
const compares = computed(() => cur.value.compares || 0)
const treeLog = computed(() => (cur.value.treeLog || []).slice(-6))
const sortedSet = computed(() => new Set(cur.value.sorted || []))
const svgW = computed(() => arr.value.length * 54 + 20)

// 柱高按当前数组最大值归一化：以前写死 v*2.2，值一上 80 柱子和文字就冲出画布
const BAR_MAX_H = 126
const maxV = computed(() => Math.max(1, ...arr.value.map(v => Math.abs(Number(v) || 0))))
function barH(v) { return Math.max(10, Math.round((Math.abs(Number(v) || 0) / maxV.value) * BAR_MAX_H)) }

function barFill(i) {
  if (i === iPos.value) return '#e6eeff'
  if (i === jPos.value) return '#fdeaea'
  if (sortedSet.value.has(i)) return '#dcf3e7'
  return '#fff'
}
function barStroke(i) {
  if (i === iPos.value) return '#3b6ef6'
  if (i === jPos.value) return '#e05252'
  if (sortedSet.value.has(i)) return '#22a06b'
  return '#c8d3e6'
}
function barText(i) {
  if (sortedSet.value.has(i)) return '#176b48'
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
.ms-wrap { display: flex; gap: 24px; align-items: flex-start; flex-wrap: wrap; }
.ms-main { flex-shrink: 0; }
.ms-svg { background: #fbfcff; border-radius: 8px; display: block; }
.aux-box { margin-top: 8px; padding: 8px 12px; border: 1px dashed var(--border); border-radius: 8px; background: #fbfcff; }
.aux-row { display: flex; gap: 6px; margin-top: 6px; flex-wrap: wrap; min-height: 26px; }
.aux-item {
  min-width: 30px; height: 26px; line-height: 26px; text-align: center; border-radius: 4px;
  background: #eef3ff; border: 1px solid #cfe0ff; font-size: 12px; font-weight: 600; color: var(--brand);
}
.ms-panel { flex: 1; min-width: 240px; }
.info-row { display: flex; justify-content: space-between; padding: 4px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.panel-title { font-size: 13px; font-weight: 600; margin-bottom: 6px; color: var(--text-2); }
.tree-view { border: 1px solid var(--border); border-radius: 8px; padding: 8px; max-height: 150px; overflow: auto; background: #fbfcff; }
.tree-item { display: flex; gap: 8px; font-size: 12px; padding: 3px 0; color: var(--text-2); }
.tree-item.active { color: var(--brand); font-weight: 600; }
.tl { width: 62px; flex-shrink: 0; }
.tip { margin-top: 10px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
