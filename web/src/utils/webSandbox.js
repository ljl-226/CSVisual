/**
 * 浏览器内沙箱：把 HTML / CSS / JavaScript 代码拼成一份可直接塞进 iframe srcdoc 的文档。
 *
 * 为什么单独拆成 .js 而不是写在 .vue 里：Vue 的 SFC 解析器会把源码中的
 * `<script>` / `</script>` / `<style>` 字面量当成真实的块标签，
 * 一旦出现在 script 块内部就会提前截断，导致「Element is missing end tag」这类编译错误。
 * 放在普通 JS 模块里就没有这层解析，字符串怎么写都不会被误认。
 */

const SCRIPT_OPEN = '<' + 'script>'
const SCRIPT_CLOSE = '<' + '/script>'
const END_SCRIPT_RE = new RegExp('<' + '/script', 'gi')

/** 控制台捕获脚本：重写 console 与全局错误钩子，把输出 postMessage 回父页面 */
const SHIM = [
  '(function () {',
  '  var send = function (level, text) {',
  "    try { parent.postMessage({ __csvisual: true, level: level, text: text }, '*'); } catch (e) {}",
  '  };',
  '  var fmt = function (args) {',
  '    return Array.prototype.map.call(args, function (v) {',
  '      if (v instanceof Error) return v.stack || (v.name + \': \' + v.message);',
  "      if (typeof v === 'function') return v.toString();",
  "      if (typeof v === 'object' && v !== null) {",
  "        try { return JSON.stringify(v); } catch (e) { return Object.prototype.toString.call(v); }",
  '      }',
  '      return String(v);',
  '    }).join(\' \');',
  '  };',
  "  ['log', 'info', 'warn', 'error', 'debug'].forEach(function (k) {",
  '    var orig = console[k];',
  '    console[k] = function () {',
  "      send(k === 'debug' ? 'log' : k, fmt(arguments));",
  '      if (orig) { try { orig.apply(console, arguments); } catch (e) {} }',
  '    };',
  '  });',
  '  window.onerror = function (msg, src, line, col, err) {',
  "    send('error', (err && err.stack) ? err.stack : (msg + '  (第 ' + line + ' 行)'));",
  '    return false;',
  '  };',
  "  window.addEventListener('unhandledrejection', function (e) {",
  "    send('error', '未捕获的 Promise 拒绝: ' + fmt([e && e.reason]));",
  '  });',
  '})();'
].join('\n')

/** 预览区的基础样式：只负责让示例看得清，不干扰用户写的样式 */
const BASE_STYLE = [
  'body{font-family:system-ui,"Microsoft YaHei",sans-serif;margin:0;padding:16px;color:#1f2733;background:#fff}',
  '*{box-sizing:border-box}',
  '.box{padding:14px;border:1px solid #c7d2e4;border-radius:8px;background:#f3f7ff}',
  '.m-merge-a,.m-merge-b{background:#eef3ff;padding:8px 10px}',
  'input,button,a{font:inherit}'
].join('\n')

/** 用户代码里若出现结束脚本标签会提前闭合脚本块，必须转义 */
function safeJs(code) {
  return String(code || '').replace(END_SCRIPT_RE, '<\\' + '/script')
}

function pageOf(bodyInner, headExtra, stamp) {
  return (
    '<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">' +
    '<meta name="viewport" content="width=device-width, initial-scale=1.0">' +
    SCRIPT_OPEN + SHIM + SCRIPT_CLOSE +
    '<style>' + BASE_STYLE + '</style>' +
    (headExtra || '') +
    '</head><body>' + bodyInner + '</body></html>' + stamp
  )
}

/**
 * 生成预览文档
 * @param {string} language html | css | javascript
 * @param {string} code 用户代码
 * @param {string} demo CSS 实验室配套的示例标记
 * @param {number} runToken 每次自增即让 srcdoc 变化从而重新加载 iframe
 */
export function buildPreviewDoc(language, code, demo, runToken) {
  const lang = String(language || 'html').toLowerCase()
  const src = String(code || '')
  // runToken 只作为注释参与，保证每次点击运行都触发一次重新加载
  const stamp = '\n<!-- run ' + (runToken || 0) + ' -->'

  if (lang === 'css') {
    return pageOf(
      demo || '<p>该实验暂无示例标记</p>',
      '<style>' + src + '</style>',
      stamp
    )
  }

  if (lang === 'javascript') {
    // 包在 async 立即执行函数里：既支持顶层 await，又能把异常统一接到控制台
    return pageOf(
      SCRIPT_OPEN + '(async function(){' + safeJs(src) +
        '})().catch(function(e){console.error(e && e.stack ? e.stack : e)});' + SCRIPT_CLOSE,
      '',
      stamp
    )
  }

  // HTML：可能是一份完整文档，也可能只是一段片段，两种情况都要能预览
  if (/<html[\s>]/i.test(src)) {
    let html = src
    if (/<head[\s>]/i.test(html)) {
      html = html.replace(/<head([^>]*)>/i, '<head$1>' + SCRIPT_OPEN + SHIM + SCRIPT_CLOSE)
    } else {
      html = html.replace(
        /<html([^>]*)>/i,
        '<html$1><head><meta charset="utf-8">' + SCRIPT_OPEN + SHIM + SCRIPT_CLOSE + '</head>'
      )
    }
    return html + stamp
  }

  return pageOf(src, '', stamp)
}

/** 语言是否走浏览器沙箱（不需要后端编译器） */
export const WEB_LANGS = ['html', 'css', 'javascript']

export function isWebLang(lang) {
  return WEB_LANGS.indexOf(String(lang || '').toLowerCase()) >= 0
}
