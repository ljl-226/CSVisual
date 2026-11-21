import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import App from './App.vue'
import router from './router'
import './styles/main.css'
// KaTeX 样式：AI 回答里的公式用它排版。放在全局入口而不是 markdown.js，
// 是为了让 markdown.js 保持能在 Node（xss-check.mjs）里直接 import。
import 'katex/dist/katex.min.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import { getTheme, applyTheme } from './utils/theme'
import { useUserStore } from './stores/user'
import { watchIdle } from './utils/idle'

// 挂载前先定主题，避免深色用户看到一帧白底
applyTheme(getTheme())

const app = createApp(App)
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}
app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })

/** 空闲自动登出时长（分钟），默认 30 */
const IDLE_MINUTES = Number(import.meta.env.VITE_IDLE_MINUTES || 30)

/**
 * 登录态恢复。
 *
 * 令牌不再存 localStorage，刷新后内存里是空的，得拿 HttpOnly Cookie 问一次
 * /auth/me 才知道「我到底登没登录」。
 *
 * 这里**不**等它完成再挂载：曾经写成「恢复完再 mount + 3 秒超时兜底」，
 * 结果开发环境首次加载（Vite 现编译模块 + 动态 import）常常超过 3 秒，
 * 兜底先触发 → 按未登录渲染 → 刷新就被踢到登录页。
 * 现在改成：立刻挂载，由**路由守卫**在需要登录的路由上 await 恢复结果
 * （见 router/index.js），公开页面完全不受影响。
 */
const store = useUserStore()
store.restore()

app.mount('#app')

watchIdle(IDLE_MINUTES, async () => {
  // 已经登出就不用再清一次
  if (!store.isLogin) return
  await store.logoutRequest()
  ElMessage.warning(`已超过 ${IDLE_MINUTES} 分钟无操作，已自动退出登录`)
  router.push('/login')
})
