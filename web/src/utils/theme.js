/**
 * 白天 / 夜晚模式。
 *
 * 实现方式：在 <html> 上挂 .dark 类 + data-theme 属性，全部配色走 CSS 变量
 * （见 styles/main.css 的 :root 与 html.dark），Element Plus 由官方 dark/css-vars.css 接管。
 *
 * 两个细节：
 * 1. 主题必须在 Vue 挂载前就落到 <html> 上（main.js 里 applyTheme），否则深色用户会先闪一帧白屏。
 * 2. 同步 color-scheme，让原生滚动条、表单控件、日期选择等跟随系统语义。
 */
const KEY = 'cv_theme'

function read() {
  try {
    const v = localStorage.getItem(KEY)
    if (v === 'dark' || v === 'light') return v
  } catch (e) {
    // 隐私模式下 localStorage 可能不可用，退化成系统偏好即可
  }
  // 没选过就跟随系统：深色系统的用户第一次进来就是夜晚模式
  try {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) return 'dark'
  } catch (e) { /* 老浏览器不支持就按白天处理 */ }
  return 'light'
}

export function getTheme() {
  return read()
}

export function applyTheme(theme) {
  if (typeof document === 'undefined') return
  const dark = theme === 'dark'
  const el = document.documentElement
  el.classList.toggle('dark', dark)
  el.setAttribute('data-theme', dark ? 'dark' : 'light')
  el.style.colorScheme = dark ? 'dark' : 'light'
}

export function setTheme(theme) {
  const t = theme === 'dark' ? 'dark' : 'light'
  try {
    localStorage.setItem(KEY, t)
  } catch (e) {
    /* 存不下也要让本次切换生效 */
  }
  applyTheme(t)
  return t
}

export function toggleTheme() {
  return setTheme(read() === 'dark' ? 'light' : 'dark')
}
