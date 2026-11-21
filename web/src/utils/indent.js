/**
 * 缩进整理：按语言规则重新排布代码缩进。
 *
 * 为什么单独抽成模块而不是写在 CodeEditor.vue 里：
 * 这套逻辑是纯函数（输入字符串、输出字符串，不碰 DOM 也不碰 Vue），
 * 抽出来才能被脚本直接跑单元测试 —— 「缩进整理」这类规则一旦写错，
 * 现象是「整理完更乱了」，靠肉眼点几下很难覆盖全部分支。
 *
 * 三种规则：
 *   python     —— 冒号 / 相对层级（保留原结构，绝不发明新层级）
 *   html       —— 标签嵌套（HTML 没有大括号，按 {} 整理等于什么都没做）
 *   其它       —— 大括号（c / cpp / java / javascript / css）
 */

/** 缩进宽度按语言区分：示例代码与社区惯例都是 Python/C 系 4 空格、Web 系 2 空格。
 *  这里必须和编辑器的 Tab 键、回车续行用同一份宽度 —— 之前 Tab 插 2 空格、
 *  「缩进整理」输出 4 空格，用户按 Tab 缩完一整理宽度就变了。 */
export function indentWidth(lang) {
  const l = String(lang || '').toLowerCase()
  if (l === 'python' || l === 'c' || l === 'cpp' || l === 'java') return 4
  return 2 // html / css / javascript 等 Web 语言
}

/** HTML 空元素（void element）：只有开始标签，不产生层级。
 *  漏掉这张表最直接的表现就是「每写一张图片，后面的代码就多缩进一层」 */
const VOID_TAGS = new Set([
  'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
  'link', 'meta', 'param', 'source', 'track', 'wbr'
])

/** 内容原样保留的标签：里面的缩进由各自语言决定，不能当 HTML 标签算
 *  （script 里写 `if (a < b)` 会被误认成开标签） */
const RAW_TAGS = ['script', 'style', 'pre', 'textarea']

/** 一行内标签的净增减：<div> +1、</div> -1、<br> 与 <img/> 0。
 *  `<!DOCTYPE html>` 与 `<!-- -->` 以 `<!` 开头，不匹配下面的正则，天然被跳过。 */
export function htmlDelta(line) {
  let d = 0
  const re = /<\/?([A-Za-z][\w-]*)\b[^>]*?(\/?)>/g
  let m
  while ((m = re.exec(line)) !== null) {
    const tag = m[1].toLowerCase()
    const closing = m[0].charAt(1) === '/'
    const selfClose = m[2] === '/' || /\/\s*>$/.test(m[0])
    if (closing) d--
    else if (!selfClose && !VOID_TAGS.has(tag)) d++
  }
  return d
}

/**
 * 逐标签模拟一行，返回 { level, depth }。
 *   level —— 本行应该落在哪一层（第一个标签之前所处的层级）
 *   depth —— 处理完本行后所处的层级
 *
 * 为什么必须逐个标签走，不能用「行首闭标签数 + 行内净增量」：
 * 后者会把闭标签减两次（退层一次、净增量又减一次），
 * 于是 `</head>` 之后层级直接掉到 0，后面的 `<body>` 及其内容全部少缩一级。
 */
function htmlLineLevel(line, depth) {
  const re = /<\/?([A-Za-z][\w-]*)\b[^>]*?(\/?)>/g
  let m
  let level = null
  let d = depth
  while ((m = re.exec(line)) !== null) {
    const tag = m[1].toLowerCase()
    const closing = m[0].charAt(1) === '/'
    const self = m[2] === '/' || /\/\s*>$/.test(m[0])
    if (level === null) {
      // 行首就是闭标签 → 先退一层再落笔（`</div>` 与它的 `<div>` 对齐）
      level = closing ? Math.max(0, d - 1) : d
    }
    if (closing) d = Math.max(0, d - 1)
    else if (!self && !VOID_TAGS.has(tag)) d++
  }
  return { level: level === null ? depth : level, depth: d }
}

/**
 * HTML：按标签嵌套定层级。
 * 与 tidyBraced 的最大区别就是这里 —— HTML 一行里根本没有 {}，
 * 用括号规则算出来的净增量恒为 0，整理完所有行都顶格，等于没做。
 */
export function tidyHtml(lines, W) {
  const out = []
  let depth = 0
  let inComment = false
  let i = 0

  while (i < lines.length) {
    const line = lines[i]
    const t = line.trim()

    // 多行注释：整段按当前层级挂，注释里出现的标签不参与层级计算
    if (inComment || /^<!--/.test(t)) {
      const ends = t.indexOf('-->') >= 0
      if (inComment && ends) inComment = false
      else if (!inComment && !ends) inComment = true
      out.push(' '.repeat(W * depth) + t)
      i++
      continue
    }
    if (!t) { out.push(''); i++; continue }

    const { level: d, depth: nextDepth } = htmlLineLevel(t, depth)
    out.push(' '.repeat(W * d) + t)
    i++

    // 原始内容块：整块收集后按「块内相对缩进」平移，保留作者原本的排版
    const open = t.match(/<(script|style|pre|textarea)\b[^>]*>/i)
    const closed = open && new RegExp('</' + open[1] + '\\s*>', 'i').test(t)
    if (open && !/\/\s*>$/.test(open[0]) && !closed) {
      const tag = open[1].toLowerCase()
      const closeRe = new RegExp('</' + tag + '\\s*>', 'i')
      const start = i
      let j = i
      while (j < lines.length && !closeRe.test(lines[j])) j++

      const body = lines.slice(start, j)
      // script / style 里装的是 JS / CSS，就该按大括号规则整理，
      // 而且 `if (a < b)` 这种小于号在 HTML 标签规则里会被误认成开标签 —— 必须隔离处理
      const base = ' '.repeat(W * (d + 1))
      if (tag === 'script' || tag === 'style') {
        // tidyBraced 已经算好了块内的相对层级，这里只能整体平移，
        // 再 trim 一次就把 JS / CSS 自己的缩进抹平了
        for (const l of tidyBraced(body, W)) out.push(l.trim() ? base + l : '')
      } else {
        // pre / textarea 的内容不是代码：只按块内相对缩进平移，保留作者排版
        const nonBlank = body.filter(l => l.trim())
        const min = nonBlank.reduce(
          (m, l) => Math.min(m, (l.match(/^ */) || [''])[0].length), Infinity
        )
        for (const l of body) {
          const lt = l.trim()
          if (!lt) { out.push(''); continue }
          const oi = (l.match(/^ */) || [''])[0].length
          out.push(base + ' '.repeat(Math.max(0, oi - (min === Infinity ? 0 : min))) + lt)
        }
      }
      // 闭标签回到入口层级
      if (j < lines.length) { out.push(' '.repeat(W * d) + lines[j].trim()); j++ }
      i = j
      depth = d
      continue
    }

    depth = nextDepth
  }
  return out
}

/** 统计一行里括号的净增减（跳过字符串字面量与注释，避免 "://" 这类干扰） */
export function bracketDelta(line) {
  let inS = null, inLineComment = false, inBlock = false
  let delta = 0
  for (let i = 0; i < line.length; i++) {
    const c = line[i], n = line[i + 1]
    if (inLineComment) break
    if (inBlock) { if (c === '*' && n === '/') { inBlock = false; i++ } continue }
    if (inS) { if (c === '\\') i++; else if (c === inS) inS = null; continue }
    if (c === '#') break                    // Python 行注释
    if (c === '/' && n === '/') break       // C 系行注释
    if (c === '/' && n === '*') { inBlock = true; i++; continue }
    if (c === '"' || c === "'") { inS = c; continue }
    if (c === '(' || c === '[' || c === '{') delta++
    else if (c === ')' || c === ']' || c === '}') delta--
  }
  return delta
}

/**
 * C / C++ / Java / JavaScript / CSS：大括号决定层级。
 * 行首的连续闭符先把层级退掉再落笔（`} else {` 这种行才不会越缩越深），
 * 行内的开括号计入下一行。跨行的 /* *\/ 注释整段挂着不动。
 */
export function tidyBraced(lines, W) {
  let depth = 0
  let inBlock = false
  return lines.map(raw => {
    const t = raw.trim()
    if (!t) return ''
    if (inBlock) {
      if (t.includes('*/')) inBlock = false
      return ' '.repeat(W * depth) + t
    }
    if (/^\/\*/.test(t) && !t.includes('*/')) {
      inBlock = true
      return ' '.repeat(W * depth) + t
    }
    let lead = 0
    while (lead < t.length && '})]'.includes(t[lead])) lead++
    const d = Math.max(0, depth - lead)
    const s = ' '.repeat(W * d) + t
    depth = Math.max(0, depth + bracketDelta(t))
    return s
  })
}

/** Python 相对层级归一化：保留原结构，把各种乱宽度统一成 4 空格 */
function tidyPythonRelative(lines, W) {
  let inTriple = null
  const stack = [0]   // 原始缩进宽度栈
  return lines.map(raw => {
    if (inTriple) {
      if (raw.includes(inTriple)) inTriple = null
      return raw
    }
    const tq = raw.match(/"""|'''/)
    if (tq && !raw.slice(raw.indexOf(tq[0]) + 3).includes(tq[0])) { inTriple = tq[0]; return raw }
    const t = raw.trim()
    if (!t) return ''
    const oi = (raw.match(/^ */) || [''])[0].length
    while (stack.length > 1 && oi < stack[stack.length - 1]) stack.pop()
    if (oi > stack[stack.length - 1]) stack.push(oi)
    return ' '.repeat(W * (stack.length - 1)) + t
  })
}

/** Python 冒号推断：只用于完全拍平的代码 —— else 系退层、括号内对齐续行 */
function tidyPythonColon(lines, W) {
  const DEDENT = /^(else|elif|except|finally|case)\b/
  let depth = 0
  let bracket = 0          // 未闭合括号数
  let bracketBase = 0      // 进入括号那一行所在的层级
  let inTriple = null      // 三引号字符串：内容属于字符串字面量，绝不能动
  return lines.map(raw => {
    if (inTriple) {
      if (raw.includes(inTriple)) inTriple = null
      return raw
    }
    const tq = raw.match(/"""|'''/)
    if (tq && !raw.slice(raw.indexOf(tq[0]) + 3).includes(tq[0])) {
      inTriple = tq[0]
      return ' '.repeat(W * depth) + raw.trim()
    }
    const t = raw.trim()
    if (!t) return ''
    if (bracket > 0) {
      bracket += bracketDelta(t)
      const closed = bracket <= 0
      const s = ' '.repeat(W * (bracketBase + 1)) + t
      if (closed) {
        bracket = 0
        depth = t.endsWith(':') ? bracketBase + 1 : bracketBase
      }
      return s
    }
    const dedent = DEDENT.test(t)
    const d = dedent ? Math.max(0, depth - 1) : depth
    const delta = bracketDelta(t)
    if (delta > 0) { bracket = delta; bracketBase = d; if (dedent) depth = d }
    else if (t.endsWith(':') && !t.startsWith('#')) depth = d + 1
    else if (dedent) depth = d
    return ' '.repeat(W * d) + t
  })
}

/** Python 总入口：
 *  - 原代码已经有缩进结构 → 按相对层级归一化（绝不发明新层级，不会毁掉正确代码）
 *  - 原代码完全拍平（全是 0 缩进）→ 只能靠冒号推断层级（flat 场景下的最优猜测） */
export function tidyPython(lines, W) {
  const nonBlank = lines.filter(l => l.trim())
  const flat = nonBlank.length > 0 && nonBlank.every(l => (l.match(/^ */) || [''])[0].length === 0)
  return flat ? tidyPythonColon(lines, W) : tidyPythonRelative(lines, W)
}

/** 对外唯一入口：code + lang → 整理后的代码 */
export function tidyCode(code, lang) {
  const l = String(lang || 'python').toLowerCase()
  const W = indentWidth(l)
  // Tab 先统一换算成空格，否则「Tab 与空格混排」的代码整理完仍是混排
  const lines = String(code || '').replace(/\t/g, ' '.repeat(W)).split('\n')
  const out = l === 'python' ? tidyPython(lines, W)
    : l === 'html' ? tidyHtml(lines, W)
      : tidyBraced(lines, W)
  return out.join('\n')
}
