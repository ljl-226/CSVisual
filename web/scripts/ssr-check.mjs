/**
 * SSR 真实渲染校验：把全部可视化组件 + 代码编辑器在 Node 里渲染一遍，
 * 捕获运行时错误（编译通过 ≠ 运行不崩）。
 */
import { createServer } from 'vite'
import { createSSRApp, h } from 'vue'
import { renderToString } from '@vue/server-renderer'
import ElementPlus from 'element-plus'
import * as ElIcons from '@element-plus/icons-vue'
import fs from 'node:fs'
import path from 'node:path'

const root = path.resolve(process.cwd())
const visDir = path.join(root, 'src/components/vis')

/** 收集所有可视化组件 */
function collect(dir, base = 'vis') {
  const out = []
  if (!fs.existsSync(dir)) return out
  for (const name of fs.readdirSync(dir)) {
    const full = path.join(dir, name)
    if (fs.statSync(full).isDirectory()) out.push(...collect(full, base + '/' + name))
    else if (name.endsWith('.vue')) out.push(base + '/' + name)
  }
  return out
}

const targets = [
  ...collect(visDir),
  'CodeEditor.vue',
  'AlgoAssistant.vue',   // 算法小助手面板
]

const vite = await createServer({
  root,
  logLevel: 'error',
  server: { middlewareMode: true },
  appType: 'custom',
})

let pass = 0
const fails = []

for (const rel of targets) {
  const modPath = rel.startsWith('vis/') ? `@/components/${rel}` : `@/components/${rel}`
  try {
    const mod = await vite.ssrLoadModule(modPath)
    const Comp = mod.default
    if (!Comp) throw new Error('组件没有 default 导出')
    // VisFrame 是外壳组件，必需 player prop，用 mock 播放器验证
    const isFrame = rel.endsWith('VisFrame.vue')
    const props = isFrame
      ? {
          title: '测试', desc: '测试', statusText: '就绪',
          player: {
            steps: { value: [] }, total: { value: 1 }, idx: { value: 0 },
            playing: { value: false }, speed: { value: 1 },
            current: { value: null }, finished: { value: false },
            play: () => {}, pause: () => {}, toggle: () => {},
            next: () => {}, prev: () => {}, reset: () => {}, seek: () => {},
          },
        }
      : {}
    const app = createSSRApp({ render: () => h(Comp, props) })
    app.use(ElementPlus)
    // 消除 SSR 下 Element Plus 的 id 注入警告（仅提示，不影响渲染）
    app.provide('__EP_ID_INJECTION__', { prefix: 1, current: 0 })
    for (const [k, v] of Object.entries(ElIcons)) app.component(k, v)
    app.config.warnHandler = () => {}
    const html = await renderToString(app)
    if (!html || html.length < 20) throw new Error('渲染结果为空（可能未产出 DOM）')
    pass++
  } catch (e) {
    fails.push({ rel, err: String(e.message || e).split('\n')[0].slice(0, 160) })
  }
}

await vite.close()

console.log(`\n=== SSR 渲染校验 ===`)
console.log(`通过: ${pass} / ${targets.length}`)
if (fails.length) {
  console.log('\n失败明细:')
  fails.forEach(f => console.log('  ✗', f.rel, '=>', f.err))
} else {
  console.log('全部组件在真实渲染下无运行时错误 ✅')
}
process.exit(fails.length ? 1 : 0)
