// 编辑器自动配对逻辑回归测试
// 目的：锁住「在字符串里打括号会被强行补成 ()」这个用户实际反馈的 bug
// 直接复用 CodeEditor.vue 里的同一套规则（此文件与源码逻辑保持同步）

const PAIRS = { '(': ')', '[': ']', '{': '}', '"': '"', "'": "'" }
const CLOSERS = new Set([')', ']', '}'])
const QUOTES = new Set(['"', "'"])

function insideString(text, pos) {
  let inS = false, inD = false
  for (let i = 0; i < pos; i++) {
    const c = text[i]
    if (c === '\\') { i++; continue }
    if (c === '\n') { inS = false }
    if (c === '"' && !inS) inD = !inD
    else if (c === "'" && !inD) inS = !inS
  }
  return inD || inS
}

function press(text, start, end, key) {
  const after = text.slice(end)
  const prevChar = text.slice(start - 1, start)
  if (CLOSERS.has(key)) {
    if (key === after.slice(0, 1)) return { text, cursor: start + 1, act: 'skip' }
    return { text, cursor: start, act: 'nothing' }
  }
  if (PAIRS[key]) {
    if (QUOTES.has(key) && /[A-Za-z0-9_]/.test(prevChar)) return { text, cursor: start, act: 'no-pair' }
    const sel = text.slice(start, end)
    const closer = PAIRS[key]
    if (sel) return { text: text.slice(0, start) + key + sel + closer + text.slice(end), cursor: start + 1 + sel.length, act: 'wrap' }
    if (!QUOTES.has(key) && insideString(text, start))
      return { text: text.slice(0, start) + key + text.slice(start), cursor: start + 1, act: 'inside-string:open-only' }
    if (after.startsWith(closer))
      return { text: text.slice(0, start) + key + text.slice(start), cursor: start + 1, act: 'reuse-closer' }
    return { text: text.slice(0, start) + key + closer + text.slice(end), cursor: start + 1, act: 'pair' }
  }
  return { text, cursor: start, act: '--' }
}

const cases = [
  // [说明, 初始文本, 光标, 选中终点(-1表示不选), 按键, 期望文本, 期望act]
  ['用户报的bug: printf(" 里打 ( ', 'printf("");', 8, -1, '(', 'printf("(");', 'inside-string:open-only'],
  ['光标在 ) 上按 ) 应跳过', 'printf("hi");', 11, -1, ')', 'printf("hi");', 'skip'],
  ['写 () 时先 ( 再 )', 'f', 1, -1, '(', 'f()', 'pair'],
  ['abc 后打 ( 正常补对', 'abc', 3, -1, '(', 'abc()', 'pair'],
  ['右侧已有 ) 时只补左半边', 'f)', 1, -1, '(', 'f()', 'reuse-closer'],
  ["it 后打 ' 不补成对", 'it', 2, -1, "'", 'it', 'no-pair'],
  ['选中内容被括号包住', 'abc', 0, 3, '(', '(abc)', 'wrap'],
  ['普通打 { 补对', '', 0, -1, '{', '{}', 'pair'],
  ['字符串里的 [ 不配对', 'a = "x"]', 6, -1, '[', 'a = "x["]', 'inside-string:open-only'],
]

let pass = 0, fail = 0
for (const [desc, t, pos, selEnd, key, want, wantAct] of cases) {
  const end = selEnd === -1 ? pos : selEnd
  const r = press(t, pos, end, key)
  const ok = r.text === want && r.act === wantAct
  if (ok) pass++
  else fail++
  console.log((ok ? 'PASS  ' : 'FAIL  ') + desc)
  if (!ok) console.log('      期望: ' + JSON.stringify(want) + ' [' + wantAct + ']\n      实得: ' + JSON.stringify(r.text) + ' [' + r.act + ']')
}
console.log('\n' + pass + ' passed, ' + fail + ' failed')
process.exit(fail ? 1 : 0)
