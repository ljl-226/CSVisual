<template>
  <VisFrame title="二叉排序树 BST · 插入 / 查找 / 删除" desc="BST 性质：左子树结点值均小于根、右子树均大于根；查找长度取决于树高，平衡时 O(log n)，退化为单支链表时 O(n)" :player="player" :status-text="statusText" back-to="/knowledge/36">
    <template #extra>
      <el-input v-model="seqInput" size="small" style="width:168px" placeholder="关键字序列" />
      <el-button size="small" @click="applySeq">建树</el-button>
      <el-select v-model="opType" size="small" style="width:88px">
        <el-option value="insert" label="插入" /><el-option value="find" label="查找" /><el-option value="delete" label="删除" />
      </el-select>
      <el-input v-model="opKey" size="small" style="width:70px" placeholder="key" />
      <el-button size="small" @click="runOp">执行</el-button>
      <el-button size="small" plain @click="loadDegenerate">退化演示</el-button>
      <el-button size="small" plain @click="resetAll">重置</el-button>
    </template>

    <div class="bst-wrap">
      <svg :width="lay.w" :height="lay.h" class="bst-svg">
        <line v-for="(e, i) in lay.edges" :key="'e' + i" :x1="e.x1" :y1="e.y1" :x2="e.x2" :y2="e.y2"
          :stroke="onPath(e.b) && onPath(e.a) ? '#3b6ef6' : '#c8d3e6'" :stroke-width="onPath(e.b) && onPath(e.a) ? 2.4 : 1.5" />
        <g v-for="n in lay.nodes" :key="n.id" :transform="`translate(${n.x}, ${n.y})`">
          <circle r="19" :fill="fillOf(n.id)" :stroke="strokeOf(n.id)" stroke-width="2" :stroke-dasharray="dashOf(n.id)" />
          <text y="5" text-anchor="middle" font-size="13" font-weight="600" :fill="textOf(n.id)">{{ n.key }}</text>
          <text y="-26" text-anchor="middle" font-size="11" fill="#8b95a3">第 {{ depthOf(n) + 1 }} 层</text>
        </g>
        <text v-if="!lay.nodes.length" x="30" y="40" font-size="13" fill="#8b95a3">空树</text>
      </svg>

      <div class="bst-panel">
        <div class="info-row"><span>结点数 n</span><b>{{ stats.n }}</b></div>
        <div class="info-row"><span>树高 h</span><b :style="{ color: stats.h === stats.n && stats.n > 2 ? 'var(--danger)' : 'inherit' }">{{ stats.h }}</b></div>
        <div class="info-row"><span>本次查找长度</span><b style="color:var(--brand)">{{ cur.compares }}</b></div>
        <div class="info-row"><span>待操作关键字</span><b style="color:var(--warning)">{{ cur.pending ?? '—' }}</b></div>
        <div class="info-row"><span>查找路径</span><b>{{ pathKeys.join(' → ') || '—' }}</b></div>
        <div class="info-row"><span>成功 ASL</span><b>{{ stats.asl }}</b></div>
        <el-divider />
        <div class="tip small muted">
          <b>删除三情形：</b>①叶子直接摘除；②单子树——子树顶替（子承父位）；③左右子树俱全——用<b>中序前驱</b>（左子树最右下）顶替后再删前驱。<br />
          <b>考点：</b>三种操作均为 O(h)；平衡时成功 ASL ≈ log₂n，输入有序则退化为单支链表，h = n、ASL ≈ (n+1)/2。
        </div>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> 查找路径</span><span><i class="dot" style="background:#e8a13a"></i> 当前比较结点</span>
      <span><i class="dot" style="background:#22a06b"></i> 命中 / 新插入</span><span><i class="dot" style="background:#e05252"></i> 待删除结点</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const GAP = 58, LH = 68
const defaultSeq = [45, 24, 53, 12, 37, 93]
const seqInput = ref(defaultSeq.join(','))
const seq = ref([...defaultSeq])
const opType = ref('find')
const opKey = ref(37)
const defaultOps = [{ type: 'find', key: 37 }]
const opList = ref([...defaultOps])

const steps = computed(() => {
  const out = []
  let root = null, idc = 0, cmp = 0
  const path = []
  function clone(n) { return n ? { id: n.id, key: n.key, left: clone(n.left), right: clone(n.right) } : null }
  // 快照：整棵树副本 + 当前查找路径 + 比较次数 + 高亮结点
  function snap(desc, extra = {}) {
    out.push({ tree: clone(root), path: [...path], compares: cmp, desc, hl: -1, danger: -1, ok: false, ...extra })
  }
  function detach(parent, target, child) {
    if (!parent) root = child
    else if (parent.left === target) parent.left = child
    else parent.right = child
  }
  function doInsert(key) {
    cmp = 0; path.length = 0
    if (!root) { root = { id: ++idc, key, left: null, right: null }; snap(`树为空：${key} 直接作为根结点`, { hl: root.id, ok: true }); return }
    let p = root, fa = null
    while (p) {
      cmp++; path.push(p.id)
      if (key === p.key) { snap(`第 ${cmp} 次比较：${key} == ${p.key}，关键字重复，插入失败`, { hl: p.id, ok: true }); return }
      fa = p
      const l = key < p.key
      snap(`第 ${cmp} 次比较：${key} ${l ? '<' : '>'} ${p.key}，进入${l ? '左' : '右'}子树`, { hl: p.id })
      p = l ? p.left : p.right
    }
    const node = { id: ++idc, key, left: null, right: null }
    if (key < fa.key) fa.left = node; else fa.right = node
    path.push(node.id)
    snap(`到达空子树：挂为 ${fa.key} 的${key < fa.key ? '左' : '右'}孩子，插入完成（查找长度 ${cmp}）`, { hl: node.id, ok: true })
  }
  function doFind(key) {
    cmp = 0; path.length = 0
    let p = root
    while (p) {
      cmp++; path.push(p.id)
      if (key === p.key) { snap(`第 ${cmp} 次比较命中：${key} == ${p.key}，查找成功，查找长度 = ${cmp}`, { hl: p.id, ok: true }); return }
      const l = key < p.key
      snap(`第 ${cmp} 次比较：${key} ${l ? '<' : '>'} ${p.key}，继续在${l ? '左' : '右'}子树中查找`, { hl: p.id })
      p = l ? p.left : p.right
    }
    snap(`走到空指针：查找失败，${key} 不在树中（共比较 ${cmp} 次）`, {})
  }
  function doDelete(key) {
    cmp = 0; path.length = 0
    let p = root, fa = null
    while (p && p.key !== key) {
      cmp++; path.push(p.id); fa = p
      const l = key < p.key
      snap(`第 ${cmp} 次比较：${key} ${l ? '<' : '>'} ${p.key}，向${l ? '左' : '右'}查找待删结点`, { hl: p.id })
      p = l ? p.left : p.right
    }
    if (!p) { snap(`查找失败：树中不存在 ${key}，删除结束`, {}); return }
    cmp++; path.push(p.id)
    snap(`找到待删结点 ${key}（查找长度 ${cmp}），判断其子树情况`, { hl: p.id, danger: p.id })
    if (!p.left && !p.right) {                       // ① 叶子
      snap(`${key} 是叶子结点：直接摘除，双亲对应指针域置空`, { danger: p.id })
      detach(fa, p, null); snap('删除完成，树高可能减小', {}); return
    }
    if (!p.left || !p.right) {                      // ② 单子树
      snap(`${key} 只有${p.left ? '左' : '右'}子树：用该子树顶替它的位置（子承父位）`, { danger: p.id })
      detach(fa, p, p.left || p.right); snap('删除完成', {}); return
    }
    let q = p.left, qf = p                          // ③ 双子树：找中序前驱
    while (q.right) { path.push(q.id); snap(`在左子树中向右寻找中序前驱（当前 ${q.key}）`, { hl: q.id, danger: p.id }); qf = q; q = q.right }
    path.push(q.id)
    snap(`中序前驱 = ${q.key}（左子树最右下结点，值小于 ${key} 且最接近）`, { hl: q.id, danger: p.id })
    p.key = q.key
    snap(`用前驱值 ${q.key} 顶替被删结点，问题转化为删除前驱结点（它至多只有左子树）`, { hl: q.id })
    detach(qf, q, q.left)
    snap(`删除完成：中序遍历序列仍是递增有序的`, {})
  }
  snap('初始状态：空树', {})
  // pending = 本轮待插入/待操作的关键字。带上它，「准备插入 45」这一步
  // 才有画面变化，否则与上一步快照完全相同，看着像卡住。
  for (const k of seq.value) { snap(`按序列插入关键字 ${k}`, { pending: k }); doInsert(k) }
  for (const op of opList.value) {
    snap(`执行操作：${op.type === 'insert' ? '插入' : op.type === 'find' ? '查找' : '删除'} ${op.key}`, {})
    if (op.type === 'insert') doInsert(op.key); else if (op.type === 'find') doFind(op.key); else doDelete(op.key)
  }
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const pathSet = computed(() => new Set(cur.value.path || []))

// 中序遍历定横坐标、深度定纵坐标
const lay = computed(() => {
  const root = cur.value.tree
  const nodes = [], edges = []
  let i = 0, maxD = 0
  ;(function walk(n, d) {
    if (!n) return
    walk(n.left, d + 1)
    n.x = 40 + (i++) * GAP; n.y = 36 + d * LH
    maxD = Math.max(maxD, d); nodes.push(n)
    walk(n.right, d + 1)
  })(root, 0)
  ;(function link(n) {
    if (!n) return
    for (const c of [n.left, n.right]) if (c) { edges.push({ x1: n.x, y1: n.y, x2: c.x, y2: c.y, a: n.id, b: c.id }); link(c) }
  })(root)
  return { nodes, edges, w: Math.max(520, i * GAP + 60), h: 40 + (maxD + 1) * LH }
})

const stats = computed(() => {
  let n = 0, sum = 0, h = 0
  ;(function dfs(t, d) { if (!t) return; n++; sum += d + 1; if (d + 1 > h) h = d + 1; dfs(t.left, d + 1); dfs(t.right, d + 1) })(cur.value.tree, 0)
  return { n, h, asl: n ? (sum / n).toFixed(2) : '-' }
})
const pathKeys = computed(() => lay.value.nodes.filter(n => pathSet.value.has(n.id)).map(n => n.key))
function depthOf(n) { return Math.round((n.y - 36) / LH) }
function onPath(id) { return pathSet.value.has(id) }
function fillOf(id) {
  if (id === cur.value.danger) return '#fbdada'
  if (id === cur.value.hl) return cur.value.ok ? '#bfe9d3' : '#fdf3e2'
  return onPath(id) ? '#e6eeff' : '#ffffff'
}
function strokeOf(id) {
  if (id === cur.value.danger) return '#e05252'
  if (id === cur.value.hl) return cur.value.ok ? '#22a06b' : '#e8a13a'
  return onPath(id) ? '#3b6ef6' : '#c8d3e6'
}
function dashOf(id) { return id === cur.value.danger ? '4 3' : '0' }
function textOf(id) { return id === cur.value.danger ? '#a32c2c' : (id === cur.value.hl ? '#176b48' : '#1f2733') }

function applySeq() {
  const list = seqInput.value.split(/[,，\s]+/).map(v => Number(v.trim())).filter(v => !isNaN(v))
  if (list.length) { seq.value = list; player.reset() }
}
function runOp() {
  const v = Number(opKey.value)
  if (isNaN(v)) return
  opList.value.push({ type: opType.value, key: v })
}
function loadDegenerate() {
  const s = [12, 24, 37, 45, 53, 93]
  seq.value = s; seqInput.value = s.join(','); opList.value = [{ type: 'find', key: 93 }]; player.reset()
}
function resetAll() {
  seq.value = [...defaultSeq]; seqInput.value = defaultSeq.join(','); opList.value = [...defaultOps]; player.reset()
}
</script>

<style scoped>
.bst-wrap { display: flex; gap: 24px; align-items: flex-start; flex-wrap: wrap; }
.bst-svg { flex-shrink: 0; background: #fbfcff; border-radius: 8px; }
.bst-panel { flex: 1; min-width: 250px; }
.info-row { display: flex; justify-content: space-between; gap: 10px; padding: 4px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.tip { line-height: 1.8; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
