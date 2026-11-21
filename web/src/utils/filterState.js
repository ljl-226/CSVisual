/**
 * 筛选 / 分页状态保持。
 *
 * 背景：题库、算法题这类「筛选 → 进详情 → 返回」的页面，筛选条件如果只存在
 * 组件 ref 里，返回时组件重新挂载就全丢了，用户每次都得重选一遍。
 *
 * 这里用 URL query 作为唯一真相源：条件写进 query，返回时浏览器前进/后退
 * 自然带着条件回来，同时也让筛选状态可以被收藏、分享。
 * sessionStorage 只做「从详情页直接返回（query 里没带条件）」时的兜底。
 */

const MEM_PREFIX = 'cv_filter_'

/** 从 route.query 读出初始筛选值 */
export function readFilterState(route, defaults = {}) {
  const q = (route && route.query) || {}
  const out = {}
  Object.keys(defaults).forEach(k => {
    const v = q[k]
    if (v === undefined || v === null || v === '') {
      out[k] = defaults[k]
      return
    }
    // 数字型默认值做类型还原，避免 select 拿到字符串 '3' 匹配不上 option
    if (typeof defaults[k] === 'number') {
      const n = Number(v)
      out[k] = Number.isNaN(n) ? defaults[k] : n
    } else {
      out[k] = v
    }
  })
  return out
}

/** 把筛选 + 页码同步进 URL（replace，不往历史里塞垃圾记录） */
export function writeFilterState(router, route, state, page = 1) {
  if (!router || !route) return
  const query = { ...route.query }
  Object.keys(state).forEach(k => {
    const v = state[k]
    if (v === '' || v === null || v === undefined) delete query[k]
    else query[k] = v
  })
  if (page && page > 1) query.page = page
  else delete query.page
  const qs = new URLSearchParams(query).toString()
  const path = route.path + (qs ? '?' + qs : '')
  if (path !== route.fullPath) router.replace(path)
}

/**
 * 进入详情页前，把当前筛选存进 sessionStorage。
 * 返回时若 URL 上没有条件（用户是直接点链接进来的），
 * 可用 restoreFilter 回退到这份快照。
 */
export function saveFilterSnapshot(key, state, page = 1) {
  try {
    sessionStorage.setItem(MEM_PREFIX + key, JSON.stringify({ state, page, at: Date.now() }))
  } catch (e) { /* 隐私模式下 sessionStorage 可能不可写，忽略 */ }
}

export function restoreFilterSnapshot(key, maxAgeMs = 30 * 60 * 1000) {
  try {
    const raw = sessionStorage.getItem(MEM_PREFIX + key)
    if (!raw) return null
    const o = JSON.parse(raw)
    if (!o || !o.state) return null
    // 超过 30 分钟就当作过期，避免下次来看到上周的筛选
    if (maxAgeMs > 0 && Date.now() - (o.at || 0) > maxAgeMs) {
      sessionStorage.removeItem(MEM_PREFIX + key)
      return null
    }
    return o
  } catch (e) {
    return null
  }
}