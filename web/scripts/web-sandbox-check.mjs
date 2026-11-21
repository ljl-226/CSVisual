/**
 * 浏览器沙箱预览的回归测试
 * 运行：node scripts/web-sandbox-check.mjs
 *
 * 覆盖三类风险：
 *  1) HTML 片段与完整文档两种输入都要能拼出可预览文档；
 *  2) 用户代码里出现结束脚本标签必须被转义，否则会提前闭合脚本块（等同注入）；
 *  3) JS 要包进 async IIFE，否则顶层 await 语法错误、异常也捕获不到。
 */
import { buildPreviewDoc, isWebLang } from '../src/utils/webSandbox.js'

let pass = 0
let fail = 0

function check(name, cond) {
  if (cond) {
    pass++
    console.log('PASS ', name)
  } else {
    fail++
    console.log('FAIL ', name)
  }
}

// ---------- 1. HTML 片段 ----------
const frag = buildPreviewDoc('html', '<p>你好</p>', '', 0)
check('HTML 片段被补成完整文档', frag.startsWith('<!DOCTYPE html>'))
check('HTML 片段内容保留', frag.includes('<p>你好</p>'))
check('HTML 片段注入了控制台捕获', frag.includes('__csvisual'))

// ---------- 2. HTML 完整文档 ----------
const full = buildPreviewDoc(
  'html',
  '<!DOCTYPE html><html lang="zh-CN"><head><title>t</title></head><body>b</body></html>',
  '',
  0
)
check('完整文档不被二次包裹', (full.match(/<html/g) || []).length === 1)
check('完整文档的 head 里注入了捕获脚本', full.indexOf('__csvisual') < full.indexOf('</head>'))

// ---------- 3. CSS ----------
const css = buildPreviewDoc('css', 'body{color:red}', '<div class="box">x</div>', 0)
check('CSS 被放进 style 标签', css.includes('<style>body{color:red}</style>'))
check('CSS 预览带上示例标记', css.includes('<div class="box">x</div>'))
check('CSS 也会注入控制台捕获', css.includes('__csvisual'))

// ---------- 4. JavaScript ----------
const js = buildPreviewDoc('javascript', 'console.log(1)', '', 0)
check('JS 包进 async 立即执行函数', js.includes('(async function(){console.log(1)}'))
check('JS 异常被接到 console.error', js.includes('.catch(function(e){console.error'))
check('JS 预览注入了控制台捕获', js.includes('__csvisual'))

// 顶层 await 在 async IIFE 中合法，这里只验证代码原样进入函数体
const awa = buildPreviewDoc('javascript', 'const r = await Promise.resolve(1)', '', 0)
check('顶层 await 原样进入 async 函数体', awa.includes('const r = await Promise.resolve(1)'))

// ---------- 5. 结束脚本标签必须被转义 ----------
const evil = buildPreviewDoc('javascript', 'document.write("</script><img onerror=1>")', '', 0)
const bodyStart = evil.indexOf('(async function(){')
const bodyEnd = evil.indexOf('})().catch(')
const body = evil.slice(bodyStart, bodyEnd)
check('用户代码里的结束脚本标签被转义', !body.includes('</' + 'script'))
check('转义后仍保留可执行的等价内容', body.includes('<\\' + '/script'))

// ---------- 6. runToken 变化会改变文档（从而触发 iframe 重载） ----------
const t1 = buildPreviewDoc('javascript', 'console.log(1)', '', 1)
const t2 = buildPreviewDoc('javascript', 'console.log(1)', '', 2)
check('runToken 递增会生成不同文档', t1 !== t2)

// ---------- 7. 语言判定 ----------
check('html 属于浏览器语言', isWebLang('html') === true)
check('css 属于浏览器语言', isWebLang('css') === true)
check('javascript 属于浏览器语言', isWebLang('javascript') === true)
check('python 不属于浏览器语言', isWebLang('python') === false)
check('c 不属于浏览器语言', isWebLang('c') === false)

console.log(`\n${pass} passed, ${fail} failed`)
process.exit(fail === 0 ? 0 : 1)
