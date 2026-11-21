/**
 * 主题变量体检：确认「白天 / 夜晚」两套配色没有漏项。
 *
 * 检查两件事：
 * 1. :root 里定义的颜色型变量，html.dark 里是否都有覆盖 —— 漏了就是夜间模式下
 *    某个模块仍然是浅底浅字 / 深底深字；
 * 2. html.dark 里出现的变量，:root 里是否都有定义 —— 漏了说明组件里用了
 *    var(--x, fallback)，两套主题不一致（不一定错，但要人工确认）。
 *
 * 用法：node scripts/theme-check.mjs
 */
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const css = readFileSync(join(root, 'src/styles/main.css'), 'utf8')

/** 抽取某个选择器块的变量表（只取最外层那一对花括号） */
function varsOf(selector) {
  const at = css.indexOf(selector + ' {')
  if (at < 0) return null
  let i = css.indexOf('{', at)
  let depth = 0
  let end = i
  for (; end < css.length; end++) {
    if (css[end] === '{') depth++
    else if (css[end] === '}') {
      depth--
      if (depth === 0) break
    }
  }
  const body = css.slice(i + 1, end)
  const map = new Map()
  for (const m of body.matchAll(/(--[\w-]+)\s*:\s*([^;]+);/g)) {
    map.set(m[1], m[2].trim())
  }
  return map
}

const isColor = v => /^#|^rgb|^hsl|^linear-gradient|^radial-gradient/i.test(v)

const light = varsOf(':root')
const dark = varsOf('html.dark')
if (!light || !dark) {
  console.error('✗ 没找到 :root 或 html.dark 变量块')
  process.exit(1)
}

const missingInDark = [...light.entries()].filter(([k, v]) => isColor(v) && !dark.has(k))
const missingInLight = [...dark.keys()].filter(k => !light.has(k))

console.log('=== 主题变量体检 ===')
console.log(`白天变量 ${light.size} 个，夜晚覆盖 ${dark.size} 个`)
if (missingInDark.length) {
  console.log('\n--- :root 里的颜色变量在 html.dark 中没有覆盖 ---')
  for (const [k, v] of missingInDark) console.log(`  ! ${k}: ${v}`)
}
if (missingInLight.length) {
  console.log('\n--- html.dark 里新增、:root 未定义的变量（依赖组件里的 fallback）---')
  for (const k of missingInLight) console.log(`  · ${k}: ${dark.get(k)}`)
}
if (!missingInDark.length && !missingInLight.length) {
  console.log('两套主题变量完全对齐 ✅')
}
process.exit(missingInDark.length ? 1 : 0)
