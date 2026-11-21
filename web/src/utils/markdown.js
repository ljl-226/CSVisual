import { marked } from 'marked'
import createDOMPurify from 'dompurify'

/**
 * Markdown → 安全 HTML 的唯一入口。
 *
 * 为什么不直接用 marked.parse + v-html：marked 默认保留原始 HTML 标签，
 * 而本项目有 6 处 v-html 渲染的是「非本人可控」的内容 —— AI 回答会把用户输入回显、
 * 知识点正文和算法题面由管理端录入。只要其中一处放过 <img onerror=...>，
 * token（存在 localStorage 的 cv_token）就能被直接外传。
 * AI 回答还会存进 chat_record，历史会话重载时再次执行，构成存储型 XSS。
 *
 * 所有 v-html 都必须走这里；新增渲染点也请沿用，不要图省事直接调 marked。
 */
marked.setOptions({ breaks: true, gfm: true })

const SANITIZE_OPTS = {
  ADD_ATTR: ['target', 'rel'],
  FORBID_TAGS: ['style', 'form', 'input', 'button'],
  FORBID_ATTR: ['srcset', 'formaction', 'onerror', 'onload'],
}

/**
 * DOMPurify 必须挂在一个真实的 window 上才能工作。
 * 浏览器里直接用现成的 window；Node（xss-check.mjs）里由测试脚本通过
 * globalThis.__CSP_WINDOW__ 注入一个 jsdom 实例。
 * 注意：拿不到清洗器时绝不能返回未清洗的 HTML 敷衍了事。
 */
let purifier
function ensurePurifier() {
  if (purifier) return purifier
  const w = typeof window !== 'undefined'
    ? window
    : (typeof globalThis.__CSP_WINDOW__ !== 'undefined' ? globalThis.__CSP_WINDOW__ : null)
  if (!w) return null
  purifier = createDOMPurify(w)
  return purifier
}

/**
 * 公式与流程图：renderMd 只把源码**转义后**放进占位标签，真正的排版交给 hydrateRich。
 *
 * 为什么不在 renderMd 里直接调 katex.renderToString：
 *  1) renderMd 必须保持同步且能在 Node 里跑（scripts/xss-check.mjs 就靠它做注入回归），
 *     而 katex / mermaid 的按需加载是异步的；
 *  2) 公式与图的内容来自大模型输出，属于不可信内容 ——
 *     先变占位符过一遍 DOMPurify，再在浏览器里用 katex / mermaid 渲染，
 *     渲染器的安全开关（katex 的 trust=false、mermaid 的 securityLevel='strict'）才生效。
 */
const MERMAID_FENCE = /```mermaid\s*\n([\s\S]*?)```/g
const MATH_BLOCK = /\$\$([\s\S]+?)\$\$/g
const MATH_INLINE = /(?<!\$)\$(?!\$)([^$\n]+?)\$/g

function escapeHtml(s) {
  return String(s == null ? '' : s).replace(/[&<>"]/g, c => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]
  ))
}

export function renderMd(text) {
  const src = String(text == null ? '' : text)
  if (!src.trim()) return ''
  const clean = ensurePurifier()
  if (!clean) {
    console.warn('[markdown] 未拿到 DOM 清洗器，已按纯文本输出以避免注入')
    return escapeHtml(src)
  }
  try {
    // 顺序不能反：mermaid 源码里可能带 $，先切图块，公式才不会被图里的符号污染
    const withDiagram = src.replace(
      MERMAID_FENCE,
      (_, code) => '<pre class="mermaid-slot">' + escapeHtml(code) + '</pre>'
    )
    const withMath = withDiagram
      .replace(MATH_BLOCK, (_, tex) => '<span class="math-slot" data-display="1">' + escapeHtml(tex.trim()) + '</span>')
      .replace(MATH_INLINE, (_, tex) => '<span class="math-slot" data-display="0">' + escapeHtml(tex.trim()) + '</span>')
    return clean.sanitize(marked.parse(withMath), SANITIZE_OPTS)
  } catch {
    // 解析失败时退回纯文本，宁可不渲染格式也不要把未清洗的内容塞进 v-html
    return escapeHtml(src)
  }
}

/**
 * 渲染完 v-html 之后调用：把占位符换成真正的公式与流程图。
 * 只在浏览器执行（组件里 nextTick 后调用），Node 侧不会走到这里。
 */
export async function hydrateRich(root) {
  if (!root || typeof window === 'undefined') return
  const mathSlots = root.querySelectorAll('.math-slot')
  const diagramSlots = root.querySelectorAll('.mermaid-slot')
  if (!mathSlots.length && !diagramSlots.length) return

  if (mathSlots.length) {
    try {
      const katex = (await import('katex')).default
      mathSlots.forEach(el => {
        const tex = el.textContent || ''
        if (!tex.trim()) return
        try {
          el.innerHTML = katex.renderToString(tex, {
            displayMode: el.getAttribute('data-display') === '1',
            throwOnError: false,
            strict: false,
          })
          el.classList.remove('math-slot')
        } catch {
          el.textContent = tex // 渲染不了就原样展示源码，别让学生看到空白
        }
      })
    } catch (e) {
      console.warn('[markdown] KaTeX 加载失败，公式按源码显示', e)
    }
  }

  if (diagramSlots.length) {
    try {
      const mermaid = (await import('mermaid')).default
      mermaid.initialize({
        startOnLoad: false,
        // securityLevel=strict：图的内容来自模型输出，禁止其中的 HTML 标签与点击行为
        securityLevel: 'strict',
        theme: 'default',
      })
      const nodes = []
      diagramSlots.forEach(el => {
        const box = document.createElement('div')
        box.className = 'mermaid'
        box.textContent = el.textContent || ''
        el.replaceWith(box)
        nodes.push(box)
      })
      await mermaid.run({ nodes })
    } catch (e) {
      console.warn('[markdown] Mermaid 渲染失败，按源码显示', e)
      // 失败时保留 <pre>：学生至少能看到图的源码，而不是一片空白
    }
  }
}

export default renderMd
