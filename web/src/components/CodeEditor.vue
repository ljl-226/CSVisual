<template>
  <div class="ce" :class="{ 'ce-focus': focused }" :style="ceStyle">
    <!-- 工具条 -->
    <div class="ce-bar">
      <el-tag size="small" type="primary" effect="plain">{{ langName }}</el-tag>
      <el-button size="small" type="primary" :loading="running" @click="emit('run')">
        <el-icon><CaretRight /></el-icon> 运行 (Ctrl+Enter)
      </el-button>
      <el-button size="small" plain @click="resetCode">还原示例</el-button>
      <el-button size="small" plain title="按当前语言的缩进规则整理（Python 4 空格 / C 系按大括号）" @click="tidy">缩进整理</el-button>
      <el-select v-model="fontSize" size="small" class="ce-font-size" title="编辑器字号">
        <el-option v-for="s in SIZES" :key="s" :value="s" :label="s + ' px'" />
      </el-select>
      <el-select v-model="fontKey" size="small" class="ce-font-family" title="编辑器字体">
        <el-option v-for="f in FONTS" :key="f.label" :value="f.label" :label="f.label" />
      </el-select>
      <span class="ce-hint small muted">
        <el-icon><InfoFilled /></el-icon>
        边输入边提示 · ↑↓ 选择 · Tab/Enter 接受 · 函数名自动补括号
      </span>
    </div>

    <div class="ce-body">
      <!-- 行号 -->
      <div class="ce-gutter" ref="gutter">
        <div v-for="n in lineCount" :key="n" class="ce-line-no" :class="{ active: n === curLine }">{{ n }}</div>
      </div>

      <div class="ce-main">
        <!-- 高亮层（与输入层像素对齐） -->
        <pre class="ce-highlight" ref="hl" aria-hidden="true"><code v-html="highlighted"></code></pre>

        <textarea
          ref="ta"
          v-model="inner"
          class="ce-input"
          spellcheck="false"
          autocomplete="off"
          autocorrect="off"
          autocapitalize="off"
          wrap="off"
          @scroll="syncScroll"
          @keydown="onKeydown"
          @click="refreshCandidates"
          @input="refreshCandidates"
          @focus="focused = true"
          @blur="onBlur"
        ></textarea>

        <!-- 自动补全弹层 -->
        <div v-if="showTip && candidates.length" class="ce-tip" :style="tipStyle">
          <div
            v-for="(c, i) in candidates" :key="c.label + i"
            class="ce-tip-item" :class="{ on: i === tipIndex }"
            @mousedown.prevent="accept(c)"
          >
            <span class="ce-kind" :style="{ background: kindColor(c.kind) }">{{ kindText(c.kind) }}</span>
            <span class="ce-label">{{ c.label }}</span>
            <span class="ce-detail">{{ c.detail }}</span>
          </div>
          <div class="ce-tip-foot">
            <span v-if="activeItem && activeItem.kind === 'func'">签名：{{ activeItem.detail }}</span>
            <span v-else-if="activeItem && activeItem.kind === 'snip'">代码片段：Tab 键插入</span>
            <span v-else>↑↓ 选择 · Tab/Enter 接受 · Esc 关闭</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { CaretRight, InfoFilled } from '@element-plus/icons-vue'
import { LANGS } from '@/data/codeLabs'
import { tidyCode, indentWidth } from '@/utils/indent'

const props = defineProps({
  modelValue: { type: String, default: '' },
  language: { type: String, default: 'python' },
  height: { type: Number, default: 420 },
  running: { type: Boolean, default: false }
})
const emit = defineEmits(['update:modelValue', 'run', 'lang-change'])

const ta = ref(null)
const hl = ref(null)
const gutter = ref(null)
const focused = ref(false)
const inner = ref(props.modelValue || '')
const initial = ref(props.modelValue || '')

watch(() => props.modelValue, v => { if (v !== inner.value) { inner.value = v || ''; initial.value = v || '' } })
watch(inner, v => emit('update:modelValue', v))

const langKey = computed(() => {
  const l = String(props.language || 'python').toLowerCase()
  return LANGS[l] ? l : 'python'
})
const langDef = computed(() => LANGS[langKey.value])
const langName = computed(() => langDef.value.name)

/* ================= 字号 / 字体（任务九） ================= */
// 缩进宽度按语言：Python / C 系 4 空格，Web 系 2 空格。
// Tab 键、回车续行、缩进整理三处共用同一份宽度，
// 否则「按 Tab 缩两格、一整理变四格」这种自相矛盾的手感就会出现。
const indentUnit = computed(() => indentWidth(langKey.value))
const SIZES = [12, 13, 14, 16, 18]
const FONTS = [
  { label: 'Consolas', value: 'Consolas, Monaco, "Courier New", monospace' },
  { label: 'Cascadia Code', value: '"Cascadia Code", Consolas, monospace' },
  { label: 'JetBrains Mono', value: '"JetBrains Mono", Consolas, monospace' },
  { label: 'Source Code Pro', value: '"Source Code Pro", Consolas, monospace' },
  { label: 'Courier New', value: '"Courier New", monospace' },
  { label: '系统等宽', value: 'monospace' }
]

const FONT_STORE_KEY = 'cv_editor_font'
function loadFontPref() {
  try {
    const p = JSON.parse(localStorage.getItem(FONT_STORE_KEY) || '{}')
    if (SIZES.includes(p.size)) fontSize.value = p.size
    if (FONTS.some(f => f.label === p.font)) fontKey.value = p.font
  } catch (e) { /* 忽略坏数据 */ }
}
const fontSize = ref(13)
const fontKey = ref('Consolas')
loadFontPref()
const fontFamily = computed(() => (FONTS.find(f => f.label === fontKey.value) || FONTS[0]).value)
// 行高随字号等比缩放（13px -> 22px，与旧版完全一致）
const lineHeight = computed(() => Math.round(fontSize.value * 22 / 13))
const ceStyle = computed(() => ({
  '--ce-h': props.height + 'px',
  '--ce-fs': fontSize.value + 'px',
  '--ce-lh': lineHeight.value + 'px',
  '--ce-ff': fontFamily.value,
  '--ce-tab': indentUnit.value
}))
watch([fontSize, fontKey], () => {
  localStorage.setItem(FONT_STORE_KEY, JSON.stringify({ size: fontSize.value, font: fontKey.value }))
  nextTick(measureChar)
}, { immediate: false })

// 等宽字符宽度随字体/字号变化，提示弹层定位必须实测而不是写死 7.9px
const charW = ref(7.9)
function measureChar() {
  const el = ta.value
  if (!el) return
  const cs = getComputedStyle(el)
  const span = document.createElement('span')
  span.style.cssText = 'position:absolute;visibility:hidden;white-space:pre;'
  span.style.font = cs.font
  span.textContent = '0000000000'
  document.body.appendChild(span)
  const w = span.getBoundingClientRect().width / 10
  span.remove()
  if (w > 2) charW.value = w
}
onMounted(measureChar)

const lineCount = computed(() => inner.value.split('\n').length)
const curLine = computed(() => {
  const el = ta.value
  if (!el) return 1
  return inner.value.slice(0, el.selectionStart).split('\n').length
})

/* ================= 补全状态 ================= */
const showTip = ref(false)
const tipIndex = ref(0)
const candidates = ref([])
const tipPos = ref({ left: 0, top: 0 })
const activeItem = computed(() => candidates.value[tipIndex.value] || null)
const tipStyle = computed(() => ({ left: tipPos.value.left + 'px', top: tipPos.value.top + 'px' }))

/* ================= 语法高亮 ================= */
function esc(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}
const RULES = {
  c: /(\/\/[^\n]*|\/\*[\s\S]*?\*\/)|("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|(\b\d+\.?\d*\b)|(\b[A-Za-z_]\w*\b)|([{}()[\];,.]|[+\-*/%=<>!&|^~?:])/g,
  cpp: /(\/\/[^\n]*|\/\*[\s\S]*?\*\/)|("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|(\b\d+\.?\d*\b)|(\b[A-Za-z_]\w*\b)|([{}()[\];,.]|[+\-*/%=<>!&|^~?:])/g,
  java: /(\/\/[^\n]*|\/\*[\s\S]*?\*\/)|("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|(\b\d+\.?\d*\b)|(\b[A-Za-z_]\w*\b)|([{}()[\];,.]|[+\-*/%=<>!&|^~?:])/g,
  python: /(#[^\n]*)|("""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|(\b\d+\.?\d*\b)|(\b[A-Za-z_]\w*\b)|([{}()[\];,.]|[+\-*/%=<>!&|^~?:])/g
}

const highlighted = computed(() => {
  const kw = new Set(langDef.value.keywords || [])
  const src = inner.value
  const re = RULES[langKey.value] || RULES.python
  let out = ''
  let last = 0
  let m
  re.lastIndex = 0
  while ((m = re.exec(src)) !== null) {
    out += esc(src.slice(last, m.index))
    const [full, comment, str, num, ident, op] = m
    if (comment) out += `<span class="tk-com">${esc(comment)}</span>`
    else if (str) out += `<span class="tk-str">${esc(str)}</span>`
    else if (num) out += `<span class="tk-num">${esc(num)}</span>`
    else if (ident) {
      if (kw.has(ident)) out += `<span class="tk-kw">${esc(ident)}</span>`
      else if (src[m.index + full.length] === '(') out += `<span class="tk-fn">${esc(ident)}</span>`
      else out += esc(ident)
    } else if (op) out += `<span class="tk-op">${esc(op)}</span>`
    last = m.index + full.length
  }
  out += esc(src.slice(last))
  return out + '\n'
})

/* ================= 智能提示 ================= */
function currentWord() {
  const el = ta.value
  if (!el) return ''
  const left = inner.value.slice(0, el.selectionStart)
  const m = left.match(/[A-Za-z_:][A-Za-z0-9_.:]*$/)
  return m ? m[0] : ''
}

function refreshCandidates() {
  const word = currentWord()
  if (!word) { showTip.value = false; return }
  const w = word.toLowerCase()
  const list = langDef.value.completions || []
  const prefix = list.filter(c => c.label.toLowerCase().startsWith(w))
  const contain = list.filter(c => !c.label.toLowerCase().startsWith(w) && c.label.toLowerCase().includes(w))
  // 源码里出现过的标识符也参与补全（像 IDEA 一样提示自己定义的变量/函数）
  const idents = [...new Set((inner.value.match(/\b[A-Za-z_]\w*\b/g) || []))]
    .filter(n => n.toLowerCase().startsWith(w) && n.toLowerCase() !== w && !prefix.some(c => c.label === n))
    .slice(0, 5)
    .map(n => ({ label: n, kind: 'var', detail: '源码中的标识符', insert: n }))
  candidates.value = prefix.concat(contain).slice(0, 10).concat(idents)
  tipIndex.value = 0
  showTip.value = candidates.value.length > 0
  if (showTip.value) computeTipPos(word.length)
}

function computeTipPos(wordLen) {
  const el = ta.value
  if (!el) return
  const before = inner.value.slice(0, el.selectionStart)
  const lineStart = before.lastIndexOf('\n') + 1
  const col = before.length - lineStart - wordLen
  const row = before.split('\n').length
  // 字符宽 / 行高随字号字体实时实测，换字号后弹层不飘
  tipPos.value = { left: Math.min(col * charW.value + 10, 480), top: Math.min(row * lineHeight.value + 4, 400) }
}

function accept(c) {
  const el = ta.value
  if (!el) return
  const word = currentWord()
  const start = el.selectionStart - word.length
  const before = inner.value.slice(0, start)
  const after = inner.value.slice(el.selectionStart)
  const insert = c.insert || c.label
  const paren = insert.indexOf('()')
  const cursor = start + (paren >= 0 ? paren + 1 : insert.length)
  inner.value = before + insert + after
  showTip.value = false
  nextTick(() => { el.focus(); el.setSelectionRange(cursor, cursor); syncScroll() })
}

function onKeydown(e) {
  if (showTip.value && candidates.value.length) {
    if (e.key === 'ArrowDown') { e.preventDefault(); tipIndex.value = (tipIndex.value + 1) % candidates.value.length; return }
    if (e.key === 'ArrowUp') { e.preventDefault(); tipIndex.value = (tipIndex.value - 1 + candidates.value.length) % candidates.value.length; return }
    if (e.key === 'Tab' || e.key === 'Enter') { e.preventDefault(); accept(candidates.value[tipIndex.value]); return }
    if (e.key === 'Escape') { e.preventDefault(); showTip.value = false; return }
  }

  if (e.ctrlKey && e.key === 'Enter') { e.preventDefault(); emit('run'); return }

  const el = e.target
  const start = el.selectionStart
  const end = el.selectionEnd

  if (e.key === 'Tab') {
    e.preventDefault()
    const unit = ' '.repeat(indentUnit.value)
    inner.value = inner.value.slice(0, start) + unit + inner.value.slice(end)
    nextTick(() => el.setSelectionRange(start + unit.length, start + unit.length))
    return
  }

  if (e.key === 'Enter') {
    const before = inner.value.slice(0, start)
    const lineStart = before.lastIndexOf('\n') + 1
    const lineText = before.slice(lineStart)
    const indent = (lineText.match(/^[ \t]*/) || [''])[0]
    // HTML 也要自动多缩一层：写完 <div> 回车，光标应该落在里面而不是跟它平级
    const opensTag = langKey.value === 'html' && /<[A-Za-z][\w-]*\b[^>]*[^/]\s*>\s*$/.test(lineText)
    const extra = /[{([]\s*$/.test(lineText) || opensTag
      || (langKey.value === 'python' && /:\s*(#.*)?$/.test(lineText))
    const ins = '\n' + indent + (extra ? ' '.repeat(indentUnit.value) : '')
    e.preventDefault()
    inner.value = before + ins + inner.value.slice(end)
    const pos = start + ins.length
    nextTick(() => { el.setSelectionRange(pos, pos); syncScroll() })
    return
  }

  // ---- 括号 / 引号自动配对 ----
  // 说明：这里分两类符号处理。
  //   开符 ( [ { " '  —— 决定「要不要自动补出对应的闭合符」
  //   闭符 ) ] }      —— 只决定「要不要跳过已存在的那个」
  // 之前把闭符也塞进同一个映射里查，而映射的键只有开符，于是
  // 「按 ) 跳过已有的 )」这条分支永远进不去，反而会再插一个 )》。
  const PAIRS = { '(': ')', '[': ']', '{': '}', '"': '"', "'": "'" }
  const CLOSERS = new Set([')', ']', '}'])
  const QUOTES = new Set(['"', "'"])
  const after = inner.value.slice(end)
  const prevChar = inner.value.slice(start - 1, start)

  // 1) 闭符：右侧就是同一个闭符 -> 光标跳过，不要重复插入
  if (CLOSERS.has(e.key)) {
    if (e.key === after.slice(0, 1)) {
      e.preventDefault()
      nextTick(() => el.setSelectionRange(start + 1, start + 1))
    }
    return
  }

  if (PAIRS[e.key]) {
    // 2) 引号：紧跟在标识符 / 数字后是缩写用法（it's、Don't），不补成对
    if (QUOTES.has(e.key) && /[A-Za-z0-9_]/.test(prevChar)) return

    const sel = inner.value.slice(start, end)
    const closer = PAIRS[e.key]
    e.preventDefault()

    if (sel) {
      // 有选中内容 -> 用括号/引号把选区包起来
      inner.value = inner.value.slice(0, start) + e.key + sel + closer + inner.value.slice(end)
      nextTick(() => el.setSelectionRange(start + 1, start + 1 + sel.length))
    } else if (!QUOTES.has(e.key) && insideString(inner.value, start)) {
      // 3) 已经处在字符串字面量内部时只插入左半边。
      //    printf(" 里再打 ( 是要写 printf("(") 或嵌套调用，补成 () 反而添乱
      //    —— 这正是用户反馈的现象。
      inner.value = inner.value.slice(0, start) + e.key + inner.value.slice(start)
      nextTick(() => el.setSelectionRange(start + 1, start + 1))
    } else if (after.startsWith(closer)) {
      // 4) 右侧已有对应闭符 -> 只补左半边，复用已有的右半边
      inner.value = inner.value.slice(0, start) + e.key + inner.value.slice(start)
      nextTick(() => el.setSelectionRange(start + 1, start + 1))
    } else {
      // 5) 常规：补一对，光标落中间
      inner.value = inner.value.slice(0, start) + e.key + closer + inner.value.slice(end)
      nextTick(() => el.setSelectionRange(start + 1, start + 1))
    }
    return
  }

  // ---- 退格：成对符号且中间为空时一起删 ----
  if (e.key === 'Backspace' && start === end && start > 0) {
    const prev = inner.value.slice(start - 1, start)
    const next = inner.value.slice(start, start + 1)
    if (PAIRS[prev] && PAIRS[prev] === next) {
      e.preventDefault()
      inner.value = inner.value.slice(0, start - 1) + inner.value.slice(start + 1)
      nextTick(() => el.setSelectionRange(start - 1, start - 1))
    }
  }
}

/**
 * 判断 pos 处是否落在字符串字面量内部。
 * 逐字符扫描并跳过转义，比正则可靠：正则处理不了 \" 这类转义与单双引号交织。
 */
function insideString(text, pos) {
  let inS = false, inD = false
  for (let i = 0; i < pos; i++) {
    const c = text[i]
    if (c === '\\') { i++; continue }
    if (c === '\n') { inS = false }          // 单引号字符串不跨行
    if (c === '"' && !inS) inD = !inD
    else if (c === "'" && !inD) inS = !inS
  }
  return inD || inS
}

function onBlur() {
  focused.value = false
  setTimeout(() => { showTip.value = false }, 160)
}

function syncScroll() {
  const el = ta.value
  if (!el) return
  if (hl.value) { hl.value.scrollTop = el.scrollTop; hl.value.scrollLeft = el.scrollLeft }
  if (gutter.value) gutter.value.scrollTop = el.scrollTop
}

function resetCode() {
  inner.value = initial.value || ''
  ElMessage.info('已还原为示例代码')
}

function tidy() {
  const lang = langKey.value
  inner.value = tidyCode(inner.value, lang)
  ElMessage.success(`已按 ${langDef.value.name} 规则整理缩进（${indentUnit.value} 空格）`)
}

function kindText(k) { return { kw: 'kw', func: 'fn', type: 'T', snip: '块', var: 'var' }[k] || '·' }
function kindColor(k) {
  return { kw: '#8b5cf6', func: '#3b6ef6', type: '#e8a13a', snip: '#22a06b', var: '#8b95a3' }[k] || '#8b95a3'
}
</script>

<style scoped>
.ce { border: 1px solid var(--border); border-radius: 10px; overflow: hidden; background: var(--editor-bg, #fff); }
.ce-focus { border-color: var(--brand); box-shadow: 0 0 0 3px rgba(59, 110, 246, .08); }
.ce-bar { display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: var(--editor-bar, #f8fafc); border-bottom: 1px solid var(--border); flex-wrap: wrap; }
.ce-font-size { width: 84px; }
.ce-font-family { width: 138px; }
.ce-hint { display: flex; align-items: center; gap: 4px; margin-left: auto; }
.ce-body { display: flex; height: var(--ce-h, 420px); background: var(--editor-bg, #fff); }
.ce-gutter { width: 46px; flex-shrink: 0; background: var(--editor-bar, #f8fafc); border-right: 1px solid var(--border); overflow: hidden; padding: 12px 0; text-align: right; }
.ce-line-no { font: var(--ce-fs, 13px)/var(--ce-lh, 22px) var(--ce-ff, Consolas, monospace); padding-right: 10px; color: var(--editor-ln, #a4b0c0); }
.ce-line-no.active { color: var(--brand); font-weight: 700; background: var(--brand-light); }
.ce-main { position: relative; flex: 1; overflow: hidden; }
.ce-highlight, .ce-input {
  position: absolute; inset: 0; margin: 0; padding: 12px 14px;
  font: var(--ce-fs, 13px)/var(--ce-lh, 22px) var(--ce-ff, Consolas, monospace);
  white-space: pre; tab-size: var(--ce-tab, 2); border: 0; overflow: auto;
}
.ce-highlight { pointer-events: none; color: var(--editor-fg, #1f2733); background: transparent; z-index: 1; }
/* 关键：浏览器 UA 样式给 <code> 写死了 font-family: monospace，会把 .ce-highlight
   上的字体设置吃掉 —— 表现就是「行号变了、代码字体不变」。显式继承回来。 */
.ce-highlight code { font: inherit; }
.ce-input { z-index: 2; color: transparent; background: transparent; caret-color: var(--brand); resize: none; outline: none; }
.ce-input::selection { background: rgba(59, 110, 246, .18); }
/* 语法高亮配色：白天/夜晚两套（深色底上原色普遍偏暗，需要整体提亮） */
.tk-com { color: var(--tk-com, #9aa5b1); font-style: italic; }
.tk-str { color: var(--tk-str, #22a06b); }
.tk-num { color: var(--tk-num, #e8a13a); }
.tk-kw { color: var(--tk-kw, #8b5cf6); font-weight: 600; }
.tk-fn { color: var(--tk-fn, #3b6ef6); }
.tk-op { color: var(--tk-op, #6b7787); }

.ce-tip {
  position: absolute; z-index: 5; min-width: 280px; max-width: 430px;
  background: var(--card); border: 1px solid var(--border); border-radius: 8px;
  box-shadow: 0 8px 24px rgba(31, 39, 51, .14); overflow: hidden;
}
.ce-tip-item { display: flex; align-items: center; gap: 8px; padding: 5px 10px; cursor: pointer; font-size: 13px; }
.ce-tip-item.on { background: var(--brand-light); }
.ce-kind { font-size: 10px; color: #fff; border-radius: 3px; padding: 1px 5px; flex-shrink: 0; }
.ce-label { font-weight: 600; color: var(--text); }
.ce-detail { color: var(--text-3); font-size: 12px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ce-tip-foot { border-top: 1px solid var(--border); padding: 4px 10px; font-size: 11px; color: var(--text-3); background: var(--soft-bg); }
</style>
