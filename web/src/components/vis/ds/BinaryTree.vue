<template>
  <VisFrame :title="`二叉树遍历 · ${orderName}`" :desc="'递归遍历：每个结点访问一次，输出访问序列'" :player="player" :status-text="statusText" back-to="/knowledge/4">
    <template #extra>
      <el-select v-model="order" size="small" style="width:120px">
        <el-option value="pre" label="先序 根-左-右" />
        <el-option value="in" label="中序 左-根-右" />
        <el-option value="post" label="后序 左-右-根" />
        <el-option value="level" label="层序（队列）" />
      </el-select>
      <el-input v-model="preset" size="small" style="width:180px" placeholder="结点值，逗号分隔" @change="buildTree" />
      <el-button size="small" plain @click="buildTree">重建</el-button>
    </template>

    <div class="tree-wrap">
      <svg :width="svgW" :height="svgH" class="tree-svg">
        <!-- 边 -->
        <line
          v-for="(e, i) in edges" :key="'e' + i"
          :x1="e.x1" :y1="e.y1" :x2="e.x2" :y2="e.y2"
          :stroke="e.active ? '#3b6ef6' : '#d6dde8'" :stroke-width="e.active ? 2.4 : 1.6"
        />
        <!-- 结点 -->
        <g v-for="n in layout" :key="n.id" :transform="`translate(${n.x}, ${n.y})`">
          <circle
            r="20" :fill="fillOf(n.id)" :stroke="strokeOf(n.id)"
            :stroke-width="n.id === currentId ? 3 : 1.6"
          />
          <text y="5" text-anchor="middle" font-size="13" font-weight="600" :fill="textOf(n.id)">{{ n.v }}</text>
          <text v-if="n.left" :x="-14" y="-24" font-size="10" fill="#8b95a3">L</text>
          <text v-if="n.right" :x="10" y="-24" font-size="10" fill="#8b95a3">R</text>
        </g>
      </svg>

      <div class="tree-panel">
        <div class="panel-title">访问序列</div>
        <div class="seq">
          <span v-for="(v, i) in visited" :key="i" class="seq-item seq-done">{{ v }}</span>
          <span v-if="currentVal !== null" class="seq-item seq-cur">{{ currentVal }}</span>
        </div>

        <div class="panel-title" style="margin-top:14px">
          {{ order === 'level' ? '辅助队列' : '递归调用栈' }}
        </div>
        <div class="stack-view">
          <div v-for="(s, i) in aux" :key="i" class="stack-item">
            {{ typeof s === 'object' ? s.v : s }}
          </div>
          <span v-if="!aux.length" class="small muted">（空）</span>
        </div>

        <el-divider />
        <div class="panel-title">遍历规则</div>
        <div class="rule-box">
          <code>{{ ruleText }}</code>
        </div>
        <div class="tip small muted">
          提示：对二叉排序树做<b>中序遍历</b>可得到递增有序序列；<b>先序+中序</b>或<b>后序+中序</b>可唯一确定一棵二叉树。
        </div>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> 当前访问结点</span>
      <span><i class="dot" style="background:#22a06b"></i> 已访问</span>
      <span><i class="dot" style="background:#e8a13a"></i> 在栈/队列中待处理</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const order = ref('pre')
const preset = ref('30,15,45,8,20,38,52')
const tree = ref([])

const orderName = computed(
  () => ({ pre: '先序', in: '中序', post: '后序', level: '层序' }[order.value])
)
const ruleText = computed(() => ({
  pre: 'void pre(T){ visit(T); pre(T->lchild); pre(T->rchild); }',
  in: 'void in(T){ in(T->lchild); visit(T); in(T->rchild); }',
  post: 'void post(T){ post(T->lchild); post(T->rchild); visit(T); }',
  level: 'queue.push(root); while(!empty){ n=pop(); visit(n); push(n->lchild); push(n->rchild); }'
}[order.value]))

function buildTree() {
  const vals = preset.value
    .split(/[,，\s]+/)
    .map(v => Number(v.trim()))
    .filter(v => !isNaN(v))
  const nodes = []
  vals.forEach((v, i) => {
    nodes.push({ id: i, v, left: null, right: null })
  })
  // 按 BST 规则插入
  const root = { id: -1 }
  let newNodes = []
  let counter = 0
  const rootNode = vals.length ? { id: counter++, v: vals[0], left: null, right: null } : null
  if (rootNode) {
    newNodes.push(rootNode)
    for (let i = 1; i < vals.length; i++) {
      let cur = rootNode
      const node = { id: counter++, v: vals[i], left: null, right: null }
      newNodes.push(node)
      while (true) {
        if (vals[i] < cur.v) {
          if (cur.left === null) { cur.left = node.id; break }
          cur = newNodes.find(n => n.id === cur.left)
        } else {
          if (cur.right === null) { cur.right = node.id; break }
          cur = newNodes.find(n => n.id === cur.right)
        }
      }
    }
  }
  tree.value = newNodes
  player.reset()
}

/* 布局：中序序号决定 x，深度决定 y */
const layout = computed(() => {
  const nodes = tree.value
  if (!nodes.length) return []
  const pos = {}
  let idx = 0
  const GAP_X = 62
  const GAP_Y = 76
  function inorder(id, depth) {
    const n = nodes.find(x => x.id === id)
    if (!n) return
    inorder(n.left, depth + 1)
    pos[id] = { x: 40 + idx * GAP_X, y: 40 + depth * GAP_Y }
    n._depth = depth
    idx++
    inorder(n.right, depth + 1)
  }
  inorder(0, 0)
  return nodes.map(n => ({ ...n, x: pos[n.id].x, y: pos[n.id].y }))
})

const edges = computed(() => {
  const out = []
  const activeNode = currentId.value
  layout.value.forEach(n => {
    ;['left', 'right'].forEach(side => {
      const cid = n[side]
      if (cid === null || cid === undefined) return
      const c = layout.value.find(x => x.id === cid)
      if (!c) return
      out.push({
        x1: n.x, y1: n.y, x2: c.x, y2: c.y,
        active: activeNode !== null && (activeNode === n.id || activeNode === cid)
      })
    })
  })
  return out
})

const svgW = computed(() => Math.max(420, layout.value.length * 62 + 60))
const svgH = computed(() => {
  const maxD = Math.max(0, ...layout.value.map(n => n._depth || 0))
  return 90 + maxD * 76
})

/* 生成遍历步骤 */
const steps = computed(() => {
  const nodes = tree.value
  if (!nodes.length) return []
  const out = []
  // 层序遍历：借助队列
  if (order.value === 'level') {
    const visited = []
    const queue = [nodes[0]]
    out.push({ visited: [], cur: null, aux: queue.map(n => n.v), desc: '根结点入队，开始层序遍历' })
    while (queue.length) {
      const n = queue.shift()
      visited.push(n.v)
      out.push({ visited: [...visited], cur: n.id, aux: queue.map(x => x.v), desc: `出队并访问 ${n.v}` })
      if (n.left !== null && n.left !== undefined) {
        const c = nodes.find(x => x.id === n.left)
        queue.push(c)
        out.push({ visited: [...visited], cur: null, aux: queue.map(x => x.v), desc: `左孩子 ${c.v} 入队` })
      }
      if (n.right !== null && n.right !== undefined) {
        const c = nodes.find(x => x.id === n.right)
        queue.push(c)
        out.push({ visited: [...visited], cur: null, aux: queue.map(x => x.v), desc: `右孩子 ${c.v} 入队` })
      }
    }
    return out
  }

  // 递归遍历（显式栈模拟）
  const visited = []
  function visit(id, auxArr = []) {
    const n = nodes.find(x => x.id === id)
    visited.push(n.v)
    out.push({
      visited: [...visited],
      cur: id,
      aux: [...auxArr],
      desc: `访问 ${n.v} → 输出序列 [${visited.join(', ')}]`
    })
  }
  const nameOf = id => {
    const n = nodes.find(x => x.id === id)
    return n ? n.v : ''
  }
  // 用非递归方式生成
  if (order.value === 'pre') {
    const st = [nodes[0].id]
    out.push({ visited: [], cur: null, aux: [nodes[0].v], desc: '根结点入栈' })
    while (st.length) {
      const id = st.pop()
      const n = nodes.find(x => x.id === id)
      visit(id, st.map(nameOf))
      let pushed = false
      if (n.right !== null && n.right !== undefined) st.push(n.right), (pushed = true)
      if (n.left !== null && n.left !== undefined) st.push(n.left), (pushed = true)
      if (pushed) {
        out.push({ visited: [...visited], cur: null, aux: st.map(nameOf), desc: '子结点入栈（先压右再压左，保证左子树先访问）' })
      }
    }
  } else if (order.value === 'in') {
    const st = []
    let cur = nodes[0].id
    out.push({ visited: [], cur: null, aux: [], desc: '从根结点开始，一路向左' })
    while (st.length || cur !== null) {
      while (cur !== null && cur !== undefined) {
        st.push(cur)
        out.push({
          visited: [...visited], cur: null,
          aux: st.map(x => nodes.find(y => y.id === x).v),
          desc: `结点 ${nodes.find(x => x.id === cur).v} 入栈，继续走向左子树`
        })
        const n = nodes.find(x => x.id === cur)
        cur = n.left
      }
      const id = st.pop()
      const n = nodes.find(x => x.id === id)
      visit(id, st.map(nameOf))
      cur = n.right
      if (cur !== null && cur !== undefined) {
        out.push({
          visited: [...visited], cur: null,
          aux: st.map(x => nodes.find(y => y.id === x).v),
          desc: `转向 ${n.v} 的右子树`
        })
      }
    }
  } else {
    // 后序：用栈 + 上次访问记录
    const st = []
    let cur = nodes[0].id
    let last = null
    out.push({ visited: [], cur: null, aux: [], desc: '从根结点开始后序遍历' })
    while (st.length || cur !== null) {
      while (cur !== null && cur !== undefined) {
        st.push(cur)
        const n = nodes.find(x => x.id === cur)
        out.push({
          visited: [...visited], cur: null,
          aux: st.map(x => nodes.find(y => y.id === x).v),
          desc: `${n.v} 入栈，走向左子树`
        })
        cur = n.left
      }
      const topNode = nodes.find(x => x.id === st[st.length - 1])
      if (topNode.right !== null && topNode.right !== undefined && last !== topNode.right) {
        cur = topNode.right
        out.push({
          visited: [...visited], cur: null,
          aux: st.map(x => nodes.find(y => y.id === x).v),
          desc: `${topNode.v} 的右子树尚未访问，转向右子树`
        })
      } else {
        st.pop()
        last = topNode.id
        visit(topNode.id, st.map(nameOf))
        out.push({
          visited: [...visited], cur: null,
          aux: st.map(x => nodes.find(y => y.id === x).v),
          desc: `${topNode.v} 的左右子树均处理完毕`
        })
      }
    }
  }
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || { visited: [], cur: null, aux: [], desc: '' })
const statusText = computed(() => cur.value.desc)
const currentId = computed(() => cur.value.cur ?? null)
const visited = computed(() => cur.value.visited || [])
const aux = computed(() => cur.value.aux || [])
const currentVal = computed(() => {
  if (currentId.value === null) return null
  const n = tree.value.find(x => x.id === currentId.value)
  return n ? n.v : null
})

watch(order, () => player.reset())

function fillOf(id) {
  if (id === currentId.value) return '#3b6ef6'
  if (visited.value.includes(valueOf(id))) return '#dcf3e7'
  if (aux.value.includes(valueOf(id))) return '#fdf3e2'
  return '#fff'
}
function strokeOf(id) {
  if (id === currentId.value) return '#3b6ef6'
  if (visited.value.includes(valueOf(id))) return '#22a06b'
  if (aux.value.includes(valueOf(id))) return '#e8a13a'
  return '#c8d3e6'
}
function textOf(id) {
  if (id === currentId.value) return '#fff'
  if (visited.value.includes(valueOf(id))) return '#176b48'
  return '#1f2733'
}
function valueOf(id) {
  const n = tree.value.find(x => x.id === id)
  return n ? n.v : null
}

buildTree()
</script>

<style scoped>
.tree-wrap { display: flex; gap: 24px; align-items: flex-start; flex-wrap: wrap; }
.tree-svg { flex-shrink: 0; background: #fbfcff; border-radius: 8px; }
.tree-panel { flex: 1; min-width: 260px; }
.panel-title { font-size: 13px; font-weight: 600; margin-bottom: 8px; color: var(--text-2); }
.seq { display: flex; gap: 6px; flex-wrap: wrap; min-height: 32px; }
.seq-item {
  min-width: 32px; height: 30px; line-height: 30px; text-align: center; border-radius: 6px;
  font-size: 13px; font-weight: 600; border: 1px solid var(--border);
}
.seq-done { background: #dcf3e7; border-color: var(--success); color: #176b48; }
.seq-cur { background: var(--brand); border-color: var(--brand); color: #fff; }
.stack-view {
  border: 1px dashed var(--border); border-radius: 8px; padding: 8px;
  min-height: 60px; display: flex; flex-direction: column-reverse; gap: 4px; background: #fbfcff;
}
.stack-item {
  background: #fdf3e2; border: 1px solid #f0d9ae; border-radius: 4px;
  padding: 3px 10px; font-size: 12px; text-align: center;
}
.rule-box code { background: #f2f4f8; padding: 8px 10px; border-radius: 6px; display: block; font-size: 12px; line-height: 1.7; word-break: break-all; }
.tip { margin-top: 10px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
