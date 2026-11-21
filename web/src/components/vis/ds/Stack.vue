<template>
  <VisFrame :title="mode === 'basic' ? '栈 · 入栈与出栈（LIFO）' : '栈的应用 · 括号匹配'" :desc="mode === 'basic' ? '始终只在栈顶操作，遵循后进先出原则' : '遇左括号入栈，遇右括号出栈比对'" :player="player" :status-text="statusText" back-to="/knowledge/2">
    <template #extra>
      <el-radio-group v-model="mode" size="small" @change="rebuild">
        <el-radio-button value="basic">基础操作</el-radio-button>
        <el-radio-button value="brackets">括号匹配</el-radio-button>
      </el-radio-group>
      <template v-if="mode === 'basic'">
        <el-button size="small" @click="addPush">push {{ pushLabel }}</el-button>
        <el-button size="small" type="danger" plain @click="addPop">pop</el-button>
        <el-button size="small" plain @click="rebuild">重置</el-button>
      </template>
      <el-input v-else v-model="expr" size="small" style="width:150px" placeholder="括号串" @change="rebuild" />
    </template>

    <!-- 自定义初始栈：栈底→栈顶的序列不再写死，学生想研究哪条栈就生成哪条 -->
    <div v-if="mode === 'basic'" class="init-bar">
      <span class="init-label">初始栈（栈底→栈顶）</span>
      <el-input v-model="initInput" size="small" class="init-input"
        placeholder="如 A,B,C（逗号或空格分隔，最多 6 个）"
        @keyup.enter="applyInit" />
      <el-button size="small" type="primary" plain @click="applyInit">生成栈</el-button>
    </div>

    <div class="stack-wrap">
      <!-- 栈容器：索引 0 在视觉底部，元素自下而上堆叠 -->
      <div class="stack-col">
        <div class="stack-tag stack-tag-top">
          <span class="tag-text">栈顶 top</span>
          <span class="tag-arrow">↓</span>
        </div>

        <div class="slots" :class="{ 'slots-err': cur.op === 'full' || cur.op === 'empty' || cur.op === 'bad' }">
          <div
            v-for="i in capacity"
            :key="i"
            class="slot-row"
          >
            <span class="slot-idx">[{{ capacity - i }}]</span>
            <div class="slot" :class="slotClass(capacity - i)">
              <span v-if="itemAt(capacity - i) !== ''" class="slot-val">{{ itemAt(capacity - i) }}</span>
            </div>
            <span class="slot-top-mark">
              <span v-if="capacity - i === top && top >= 0" class="top-flag">← top</span>
            </span>
          </div>
        </div>

        <div class="stack-tag stack-tag-bottom">
          <span class="tag-text">栈底 bottom</span>
          <span class="tag-arrow">↑</span>
        </div>
      </div>

      <!-- 说明面板 -->
      <div class="side-panel">
        <div class="info-row">
          <span>栈顶指针 top</span>
          <b class="hl">{{ top }}</b>
        </div>
        <div class="info-row">
          <span>栈中元素个数</span>
          <b>{{ stack.length }}</b>
        </div>
        <div class="info-row">
          <span>容量 MaxSize</span>
          <b>{{ capacity }}</b>
        </div>
        <div class="info-row">
          <span>栈空 / 栈满判定</span>
          <b>{{ stack.length === 0 ? '空栈' : (stack.length >= capacity ? '已满' : '正常') }}</b>
        </div>

        <el-divider />
        <div v-if="mode === 'brackets'" class="expr-row">
          <span class="small muted">扫描进度：</span>
          <span class="expr-char" v-for="(ch, i) in expr" :key="i" :class="charClass(i)">{{ ch }}</span>
        </div>
        <div v-if="mode === 'brackets' && matchResult" class="match-result" :class="matchResult.ok ? 'ok' : 'bad'">
          {{ matchResult.text }}
        </div>

        <div class="stack-list">
          <div class="small muted" style="margin-bottom:6px">栈内容（栈底 → 栈顶）</div>
          <div class="chip-row">
            <el-tag v-for="(s, i) in stack" :key="i" size="small" :type="i === stack.length - 1 ? 'primary' : 'info'">{{ s }}</el-tag>
            <span v-if="!stack.length" class="small muted">空栈</span>
          </div>
        </div>

        <div class="tip small muted">
          顺序栈：<code>top = -1</code> 表示空栈；<code>push</code> 先 <code>++top</code> 再存元素，
          <code>pop</code> 先取 <code>S[top]</code> 再 <code>top--</code>。
        </div>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> 栈顶元素</span>
      <span><i class="dot" style="background:#22a06b"></i> 刚入栈</span>
      <span><i class="dot" style="background:#e05252"></i> 刚出栈 / 不匹配</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const capacity = 6
const mode = ref('basic')
const expr = ref('{([])}')
const nextVal = ref(4) // A,B,C 已被初始栈占用，push 按钮从 D 继续
const pushLabel = computed(() => String.fromCharCode(64 + nextVal.value)) // 按钮显示实际要压的字母

// 初始栈由学生自己定 —— 以前的演示序列（push ABC、pop、push DE…）是写死的，
// 想换条栈研究只能干瞪眼。现在：输入栈底→栈顶序列 -> 生成 -> push/pop 都基于它。
const initInput = ref('A,B,C')
const initVals = ref(['A', 'B', 'C'])

/** 把「初始栈」翻译成操作序列：从空栈逐个 push（栈底 → 栈顶） */
function buildOps(vals) {
  return vals.map(v => ({ op: 'push', v }))
}

const basicOps = ref(buildOps(initVals.value))

const steps = computed(() => {
  const out = []
  if (mode.value === 'basic') {
    let stack = []
    out.push({ stack: [], op: 'init', pos: -1, desc: '初始空栈：top = -1，栈中无元素' })
    for (const o of basicOps.value) {
      if (o.op === 'push') {
        if (stack.length >= capacity) {
          out.push({ stack: [...stack], op: 'full', pos: -1, desc: '栈已满，push 失败（上溢 overflow）' })
          continue
        }
        stack = [...stack, o.v]
        out.push({
          stack: [...stack],
          op: 'push',
          pos: stack.length - 1,
          desc: `push(${o.v})：先判栈满，top 先加 1 变为 ${stack.length - 1}，再把元素存入 S[${stack.length - 1}]`
        })
      } else {
        if (!stack.length) {
          out.push({ stack: [], op: 'empty', pos: -1, desc: '栈已空，pop 失败（下溢 underflow）' })
          continue
        }
        const v = stack[stack.length - 1]
        out.push({ stack: [...stack], op: 'pop', pos: stack.length - 1, desc: `pop()：取出栈顶元素 S[${stack.length - 1}] = ${v}，随后 top 变为 ${stack.length - 2}` })
        stack = stack.slice(0, -1)
        out.push({ stack: [...stack], op: 'popped', pos: -1, desc: `元素 ${v} 已出栈，栈深度减 1` })
      }
    }
  } else {
    let stack = []
    let scan = 0
    out.push({ stack: [], op: 'init', pos: -1, scan: 0, match: null, desc: '开始扫描括号串，栈初始为空' })
    for (let i = 0; i < expr.value.length; i++) {
      const ch = expr.value[i]
      scan = i + 1
      if ('({['.includes(ch)) {
        stack = [...stack, ch]
        out.push({ stack: [...stack], op: 'push', pos: stack.length - 1, scan, match: null, desc: `读到左括号 ${ch} → 入栈` })
      } else {
        const pairs = { ')': '(', '}': '{', ']': '[' }
        const top = stack[stack.length - 1]
        if (top === pairs[ch]) {
          out.push({ stack: [...stack], op: 'match', pos: stack.length - 1, scan, match: true, desc: `读到右括号 ${ch}，栈顶 ${top} 匹配 → 出栈` })
          stack = stack.slice(0, -1)
          out.push({ stack: [...stack], op: 'match', pos: -1, scan, match: true, desc: `匹配成功，继续扫描` })
        } else {
          out.push({ stack: [...stack], op: 'bad', pos: stack.length - 1, scan, match: false, desc: `读到右括号 ${ch}，栈顶 ${top || '空'} 不匹配 → 匹配失败` })
          break
        }
      }
    }
    if (stack.length === 0 && out[out.length - 1].op !== 'bad') {
      out.push({ stack: [], op: 'done', pos: -1, scan, match: true, desc: '扫描结束且栈为空 → 括号完全匹配 ✓' })
    } else if (out[out.length - 1].op !== 'bad') {
      out.push({ stack: [...stack], op: 'done', pos: -1, scan, match: false, desc: '扫描结束但栈非空 → 有左括号未匹配 ✗' })
    }
  }
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || { stack: [], op: '', pos: -1, desc: '', scan: 0, match: null })
const stack = computed(() => cur.value.stack || [])
const top = computed(() => stack.value.length - 1)
const statusText = computed(() => cur.value.desc)
const matchResult = computed(() => {
  if (cur.value.match === null) return null
  return { ok: cur.value.match, text: cur.value.match ? '匹配成功 ✓' : '匹配失败 ✗' }
})

function itemAt(i) {
  return stack.value[i] !== undefined ? stack.value[i] : ''
}
function slotClass(i) {
  if (i >= stack.value.length) return 'slot-empty'
  if (i === cur.value.pos) {
    if (cur.value.op === 'push') return 'slot-push'
    if (cur.value.op === 'bad') return 'slot-bad'
    return 'slot-pop'
  }
  if (i === stack.value.length - 1) return 'slot-top'
  return 'slot-normal'
}
function charClass(i) {
  if (i === (cur.value.scan || 0) - 1) return 'cur-char'
  if (i < (cur.value.scan || 0)) return 'done-char'
  return ''
}

function addPush() {
  const prevTotal = player.total.value
  basicOps.value.push({ op: 'push', v: String.fromCharCode(64 + nextVal.value) })
  nextVal.value = nextVal.value + 1
  if (nextVal.value > 26) nextVal.value = 1
  player.playAppended(prevTotal)
}
function addPop() {
  const prevTotal = player.total.value
  basicOps.value.push({ op: 'pop' })
  player.playAppended(prevTotal)
}
function rebuild() {
  // 回到「当前初始栈」的生成过程，而不是某条写死的演示序列
  nextVal.value = (initVals.value.length % 26) + 1
  basicOps.value = buildOps(initVals.value)
  player.reset()
}

function applyInit() {
  const raw = String(initInput.value || '')
  const vals = raw
    .split(/[,，、\s]+/)
    .map(s => s.trim())
    .filter(Boolean)
  if (!vals.length) {
    ElMessage.warning('初始栈要是元素，用逗号或空格分隔，例如 A,B,C')
    return
  }
  if (vals.length > capacity) {
    ElMessage.warning(`容量 MaxSize=${capacity}，初始栈最多 ${capacity} 个元素`)
    return
  }
  initVals.value = vals
  // push 按钮的字母接在初始栈后面（A,B,C 用掉后从 D 继续）
  nextVal.value = (vals.length % 26) + 1
  basicOps.value = buildOps(vals)
  player.reset()
  // 自动播一遍入栈过程：元素一个一个压进去，比直接看到成品更能建立直觉
  player.play()
}
</script>

<style scoped>
.stack-wrap { display: flex; gap: 28px; align-items: flex-start; flex-wrap: wrap; }

/* 自定义初始栈工具行：跟画布放在一起，语义上属于「配置这条栈」 */
.init-bar {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 12px; flex-wrap: wrap;
}
.init-label { font-size: 12px; color: var(--text-2); white-space: nowrap; }
.init-input { width: 240px; }

/* ---------- 栈容器 ---------- */
.stack-col { width: 190px; text-align: center; flex-shrink: 0; }
.stack-tag {
  display: flex; align-items: center; justify-content: center; gap: 6px;
  font-size: 12px; font-weight: 600; padding: 3px 0;
}
.stack-tag-top { color: var(--brand); }
.stack-tag-bottom { color: var(--text-3); margin-top: 6px; }
.tag-arrow { font-size: 13px; opacity: 0.75; }

.slots {
  /* 正常纵向排列：DOM 首项在视觉顶部 → 索引大的空槽在上，索引 0（栈底）在下，
     元素自下而上堆叠，与课本「栈从栈底向上生长」一致 */
  display: flex; flex-direction: column; gap: 4px;
  border: 2px solid var(--border); border-radius: 10px;
  padding: 8px; background: linear-gradient(180deg, #ffffff, #f7f9fe);
  transition: border-color 0.25s;
}
.slots-err { border-color: var(--danger); }

.slot-row { display: flex; align-items: center; gap: 6px; }
.slot-idx {
  width: 30px; text-align: right; font-size: 10px; color: var(--text-3);
  font-family: 'Consolas', 'Menlo', monospace; flex-shrink: 0;
}
.slot {
  flex: 1; height: 38px; line-height: 35px;
  border: 1.5px solid var(--border); border-radius: 7px;
  font-weight: 700; font-size: 15px; background: #fff;
  transition: background 0.25s, border-color 0.25s, color 0.25s, transform 0.25s;
}
.slot-val { display: inline-block; animation: pop-in 0.28s ease-out; }
@keyframes pop-in {
  0% { transform: scale(0.55); opacity: 0; }
  70% { transform: scale(1.12); }
  100% { transform: scale(1); opacity: 1; }
}
.slot-top-mark { width: 44px; text-align: left; flex-shrink: 0; }
.top-flag {
  font-size: 11px; font-weight: 700; color: var(--brand);
  background: var(--brand-light); border-radius: 4px; padding: 1px 4px;
}

.slot-empty { background: transparent; border-style: dashed; border-color: #e8edf5; }
.slot-normal { background: #fff; }
.slot-top {
  background: linear-gradient(135deg, #eaf0ff, #dfe9ff);
  border-color: var(--brand-2); color: var(--brand);
  box-shadow: 0 2px 8px rgba(59, 110, 246, 0.14);
}
.slot-push {
  background: linear-gradient(135deg, #dcf3e7, #c8ecd9);
  border-color: var(--success); color: #176b48;
  box-shadow: 0 2px 10px rgba(34, 160, 107, 0.18);
}
.slot-pop {
  background: linear-gradient(135deg, #fdeaea, #fbd6d6);
  border-color: var(--danger); color: #a32c2c;
  box-shadow: 0 2px 10px rgba(224, 82, 82, 0.18);
}
.slot-bad {
  background: #fbdada; border-color: var(--danger); color: #a32c2c;
  animation: shake .3s;
}
@keyframes shake { 0%,100%{transform:translateX(0)} 50%{transform:translateX(4px)} }

/* ---------- 侧栏 ---------- */
.side-panel { flex: 1; min-width: 260px; }
.info-row { display: flex; justify-content: space-between; padding: 5px 0; font-size: 13px; }
.hl { color: var(--brand); font-size: 15px; }
.expr-row { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; }
.expr-char {
  width: 26px; height: 26px; line-height: 26px; text-align: center; border-radius: 6px;
  border: 1px solid var(--border); font-size: 14px; font-weight: 600; transition: all 0.2s;
}
.cur-char {
  background: var(--brand); color: #fff; border-color: var(--brand);
  box-shadow: 0 2px 8px rgba(59, 110, 246, 0.3); transform: translateY(-2px);
}
.done-char { background: #f0f2f6; color: var(--text-3); }
.match-result { margin-top: 10px; font-weight: 600; font-size: 14px; }
.match-result.ok { color: var(--success); }
.match-result.bad { color: var(--danger); }
.chip-row { display: flex; gap: 6px; flex-wrap: wrap; }
.tip { margin-top: 12px; line-height: 1.8; }
.tip code {
  background: #f2f4f8; padding: 1px 5px; border-radius: 4px;
  font-size: 12px; font-family: 'Consolas', 'Menlo', monospace;
}
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
