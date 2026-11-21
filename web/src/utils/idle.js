/**
 * 会话空闲超时：长时间无操作自动登出。
 *
 * 令牌有效期是 7 天，如果只靠它过期，一台公用电脑上的账号能被人用一周。
 * 这里在前端按「无操作时长」兜一层 —— 后端令牌无法被主动作废（JWT 无状态），
 * 所以前端必须自己清掉 Cookie 与状态，否则超时提示只是个装饰。
 *
 * 注意：这只是便利性与公共终端场景的防护，不是安全边界。
 * 真正的边界是后端令牌过期 + 敏感操作二次校验。
 */

const EVENTS = ['mousemove', 'mousedown', 'keydown', 'touchstart', 'wheel', 'click']

/**
 * @param {number} minutes 无操作多少分钟后触发
 * @param {() => void} onIdle 触发回调（通常是登出）
 * @returns {() => void} 取消监听的函数
 */
export function watchIdle(minutes, onIdle) {
  const ms = Math.max(1, Number(minutes) || 30) * 60 * 1000
  let timer = null
  let done = false

  function fire() {
    if (done) return
    done = true
    cleanup()
    onIdle()
  }

  function reset() {
    if (done) return
    clearTimeout(timer)
    timer = setTimeout(fire, ms)
  }

  function cleanup() {
    clearTimeout(timer)
    EVENTS.forEach(e => window.removeEventListener(e, reset, { passive: true }))
    document.removeEventListener('visibilitychange', onVisible)
  }

  // 页面被切到后台再回来时，按回到前台重新计时：
  // 挂后台期间定时器可能被浏览器节流，回来就超时会显得很突然
  function onVisible() {
    if (document.visibilityState === 'visible') reset()
  }

  EVENTS.forEach(e => window.addEventListener(e, reset, { passive: true }))
  document.addEventListener('visibilitychange', onVisible)
  reset()

  return cleanup
}
