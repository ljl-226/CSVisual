<template>
  <!-- 统一控制台（输入 + 输出同一个黑框）
       以前「程序输入」是编辑区旁边一个折叠框、输出是下面另一个黑框，
       一个的事情劈成两处，眼睛来回跳。这里改成真终端的样子：
         · 上面是会话流水：敲进去的输入行（灰蓝，带 ›）与程序输出按时间排在一起
         · 底下常驻一行提示符 ›，敲一行回车就把这一行收进输入队列
         · ↑ ↓ 调回敲过的行，退格（空行时）删掉上一行，Ctrl+Enter 直接运行
       执行模型还是「一次请求跑完」（在线运行没法真的中途挂起等你打字），
       所以顺序是：先敲完要喂的数据 → 运行 → 输出接着流水往下长。 -->
  <div class="run-console" :class="{ 'is-busy': running }">
    <div class="rc-log" ref="logEl">
      <div v-if="!lines.length && !running" class="rc-row sys">
        控制台就绪 —— 点「运行 ▶」看结果；程序要读键盘时，在下面 › 后敲一行数据回车。
      </div>

      <div v-for="(l, i) in lines" :key="i" class="rc-row" :class="l.kind">
        <span v-if="l.kind === 'in'" class="rc-pre">›</span><span v-if="l.kind === 'in'" class="echo-in">{{ l.text }}</span><template v-else>{{ l.text }}</template>
      </div>

      <div v-if="running" class="rc-row sys">
        <span class="rc-spin">···</span> 正在执行（{{ busyHint }}）
      </div>
    </div>

    <div v-if="needsInput && !inRows.length && !hasOutput" class="rc-tip">
      <el-icon><WarningFilled /></el-icon>
      <span>这段代码要从键盘读入 —— 在下面 › 后面敲一行数据回车，再点运行。</span>
    </div>

    <div class="rc-input">
      <span class="rc-pre rc-pre-live">›</span>
      <input
        ref="inputEl"
        class="stdin-input"
        v-model="draft"
        :disabled="running || disabled"
        spellcheck="false"
        autocapitalize="off"
        autocomplete="off"
        :placeholder="phText"
        @keydown="onKey"
      />
      <span class="rc-count muted small" v-if="inRows.length">已输入 {{ inRows.length }} 行</span>
      <el-button size="small" text :disabled="running || disabled" @click="clearInput">清空输入</el-button>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { WarningFilled } from '@element-plus/icons-vue'

/** 代码里出现这些写法 = 这个程序会从标准输入读数据（与后端 stdin 提示判定同一套） */
const READS_STDIN = /scanf\s*\(|getchar\s*\(|gets\s*\(|getline\s*\(|cin\s*>>|std::cin|input\s*\(|raw_input\s*\(|sys\.stdin|Scanner|System\.in|readLine|readline|prompt\s*\(|readFileSync\s*\(\s*0|readSync\s*\(/i

const props = defineProps({
  /** 已排队的输入，多行用 \n 分隔 —— 与后端 stdin 字段一一对应 */
  modelValue: { type: String, default: '' },
  /** 当前代码：含读输入写法时给出「该敲数据了」的提示 */
  code: { type: String, default: '' },
  output: { type: String, default: '' },
  stderr: { type: String, default: '' },
  error: { type: Boolean, default: false },
  time: { type: [Number, String], default: 0 },
  running: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  /** 每「跑完一次」自增，用来驱动往会话里追加一段结果。
   *  不能只 watch output：父组件「清空」时 output 也会变空，会被误当成又一次运行。 */
  resultKey: { type: Number, default: 0 }
})
const emit = defineEmits(['update:modelValue', 'run'])

/** 会话流水：{ kind: 'in' | 'out' | 'err' | 'sys', text } */
const lines = ref([])
const draft = ref('')
const logEl = ref(null)
const inputEl = ref(null)
/** 敲过的行（↑ ↓ 用），去重保留最近若干条 */
const history = ref([])
let histIdx = -1

const needsInput = computed(() => READS_STDIN.test(props.code || ''))
const inRows = computed(() => lines.value.filter(l => l.kind === 'in'))
const hasOutput = computed(() => lines.value.some(l => l.kind === 'out' || l.kind === 'err'))
const busyHint = computed(() => (props.time ? '上次 ' + props.time + ' ms' : '本地工具链优先，缺失时自动走云端沙箱'))
const phText = computed(() =>
  needsInput.value ? '敲一行数据后回车，例如：12 30' : '要喂给程序的数据敲这里，回车收进队列；Ctrl + Enter 运行'
)

function scrollEnd() {
  nextTick(() => {
    const el = logEl.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

function toBottom() { scrollEnd() }

/** 把当前行收进输入队列 —— 终端里按下回车的那一下 */
function commit() {
  const text = String(draft.value || '').replace(/\r/g, '')
  if (!text.trim()) return                 // 空回车不产生空行：误敲一下不会污染输入
  if (!history.value.includes(text)) history.value.push(text)
  histIdx = -1
  draft.value = ''
  lines.value.push({ kind: 'in', text })
  const next = inRows.value.map(l => l.text).join('\n')
  internal = true
  emit('update:modelValue', next)
  toBottom()
}

/** 空行时的退格 = 删掉刚敲的最后一行（与终端退格习惯一致） */
function dropLast() {
  const idx = lines.value.map(l => l.kind).lastIndexOf('in')
  if (idx < 0) return
  lines.value.splice(idx, 1)
  internal = true
  emit('update:modelValue', inRows.value.map(l => l.text).join('\n'))
}

function onKey(e) {
  const ctrl = e.ctrlKey || e.metaKey
  if (e.key === 'Enter') {
    e.preventDefault()
    if (ctrl) emit('run')
    else commit()
    return
  }
  if (e.key === 'Backspace' && !draft.value) {
    e.preventDefault()
    dropLast()
    return
  }
  if (e.key === 'ArrowUp') {
    e.preventDefault()
    if (!history.value.length) return
    histIdx = histIdx < 0 ? history.value.length - 1 : Math.max(0, histIdx - 1)
    draft.value = history.value[histIdx]
    return
  }
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    if (histIdx < 0) return
    histIdx += 1
    if (histIdx >= history.value.length) { histIdx = -1; draft.value = '' }
    else draft.value = history.value[histIdx]
    return
  }
  if (ctrl && (e.key === 'l' || e.key === 'L')) {
    e.preventDefault()
    clearAll()
  }
}

/** 运行结束后把结果追加到会话里（父组件 resultKey 自增触发） */
function pushResult() {
  /* 清过屏但输入队列还在的情况（外层的「清空」只清屏幕、不清队列）：
     把要喂进去的行重新回显一次 —— 屏幕上看到的，和这次真正发出去的数据必须一致。 */
  if (!inRows.value.length) {
    String(props.modelValue || '').replace(/\n+$/, '').split('\n')
      .filter(s => s.length)
      .forEach(t => lines.value.push({ kind: 'in', text: t }))
  }
  const out = String(props.output || '').replace(/\n+$/, '')
  const err = String(props.stderr || '').replace(/\n+$/, '')
  if (props.error) {
    lines.value.push({ kind: 'err', text: err || out || '运行失败' })
  } else if (out) {
    lines.value.push({ kind: 'out', text: out })
  } else {
    lines.value.push({ kind: 'sys', text: '（这次运行没有任何输出）' })
  }
  if (props.time) lines.value.push({ kind: 'sys', text: '— 完成 · 耗时 ' + props.time + ' ms —' })
  toBottom()
}

/* ---------- 与外部 v-model 双向同步 ----------
   internal 标记：Enter / 退格是本组件自己产生的变更，回灌时要跳过重建，
   否则刚敲的行会被清掉重排，光标位置与「回车后换新行」的观感全乱。 */
let internal = false
function rebuild(v) {
  const rows = String(v || '').replace(/\n+$/, '').split('\n').filter(s => s.length)
  // 外部赋值只发生在「换题 / 换语言恢复草稿 / 清空」这些场景，
  // 上一轮会话的输出不该留在新场景下 —— 直接重开一段会话。
  lines.value = rows.map(t => ({ kind: 'in', text: t }))
}
watch(() => props.modelValue, v => {
  if (internal) { internal = false; return }
  rebuild(v)
})

let lastKey = -1
watch(() => props.resultKey, k => {
  if (!k || k === lastKey) return
  lastKey = k
  // 结果可能比标高先到一帧（父组件 nextTick 之后才置位），等一帧再取
  nextTick(pushResult)
})

onMounted(() => {
  rebuild(props.modelValue)
  histIdx = -1
})

/** 只清输入队列，会话里的输出留着（还盯着上次的打印排查的时候不想被连根拔） */
function clearInput() {
  lines.value = lines.value.filter(l => l.kind !== 'in')
  draft.value = ''
  internal = true
  emit('update:modelValue', '')
  scrollEnd()
  inputEl.value && inputEl.value.focus()
}
/** 清屏：连输出一起收干净（对应外层的「清空」按钮）。
 *  刻意不碰 modelValue —— 清屏不看输入：清完还想用同一批数据再跑一次，
 *  直接点运行就行（追加结果时会自动把队列回显出来）；不想要了点「清空输入」。 */
function clearAll() {
  lines.value = []
  draft.value = ''
}
defineExpose({ clear: clearAll, clearInput, focus: () => inputEl.value && inputEl.value.focus() })
</script>

<style scoped>
.run-console {
  display: flex; flex-direction: column; gap: 6px;
  min-height: 0; flex: 1 1 auto; overflow: hidden;
  padding: 10px 12px; border-radius: 8px;
  background: #1f2733; color: #d8e2ee;
  font: 13px/1.7 Consolas, Monaco, "Courier New", monospace;
}
.rc-log {
  flex: 1 1 auto; min-height: 0; overflow: auto;
  white-space: pre-wrap; word-break: break-all;
}
.rc-row { white-space: pre-wrap; }
.rc-pre { color: #7dd3a0; margin-right: 6px; user-select: none; }
/* 回显的输入行：压暗一档，和程序自己的输出区分开（沿用旧的 .echo-in 语义） */
.rc-row.in .echo-in { color: #8fa3b8; }
.rc-row.out { color: #e6eef8; }
.rc-row.err { color: #ffb4b4; }
.rc-row.sys { color: #7d8ea3; }
.rc-spin { animation: rc-blink 1.2s steps(3, end) infinite; }
@keyframes rc-blink { 0% { opacity: .35 } 50% { opacity: 1 } 100% { opacity: .35 } }

.rc-tip {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; color: #ffcf8b;
  background: rgba(224, 160, 60, .12); border: 1px solid rgba(224, 160, 60, .35);
  border-radius: 6px; padding: 5px 8px; flex-shrink: 0;
}
.rc-input {
  display: flex; align-items: center; gap: 6px; flex-shrink: 0;
  padding-top: 7px; border-top: 1px dashed #34414f;
}
.rc-input :deep(.el-button) { color: #9fb2c6; }
.rc-input :deep(.el-button:hover) { color: #d8e2ee; }
.stdin-input {
  flex: 1 1 auto; min-width: 0;
  background: transparent; border: none; outline: none;
  color: #eaf2fb; font: inherit; padding: 2px 0;
}
.stdin-input::placeholder { color: #6c7a8c; }
.stdin-input:disabled { opacity: .6; cursor: not-allowed; }
.rc-count { white-space: nowrap; }
.run-console.is-busy .rc-input { opacity: .75; }
</style>
