import { defineStore } from 'pinia'

/**
 * 这里刻意用动态 import 而不是顶部 `import { authApi } from '@/api'`：
 * api/index.js 的请求拦截器反过来要读本 store 的 token，顶部互引会形成循环依赖，
 * 打包顺序一变就可能拿到未初始化的绑定。运行时才用到的东西，运行时再取。
 */
async function api() {
  return (await import('@/api')).authApi
}

/**
 * 恢复登录态的 Promise，模块级保存以实现「并发调用只发一次请求」。
 * 不放在 state 里：Promise 不该进响应式系统。
 */
let restorePromise = null

/**
 * 安全读取 localStorage 里的用户信息缓存。
 * 这里不能用裸 JSON.parse：一旦 cv_user 存的是脏数据（手工写入、同源其它应用污染、
 * 旧版本残留），异常会在 store 初始化的同步代码里抛出，导致整个应用挂载前就崩 ——
 * 而且刷新也没用，因为每次启动都会再 parse 一次。宁可当成未登录。
 *
 * 注意这里缓存的只是「我叫什么、什么角色」这类展示信息，
 * **不含任何凭据** —— 令牌在 HttpOnly Cookie 里，JS 读不到。
 */
function readCachedUser() {
  try {
    const raw = localStorage.getItem('cv_user')
    if (!raw) return null
    const v = JSON.parse(raw)
    return v && typeof v === 'object' && !Array.isArray(v) ? v : null
  } catch {
    localStorage.removeItem('cv_user')
    return null
  }
}

export const useUserStore = defineStore('user', {
  state: () => ({
    /**
     * 令牌只活在内存里。
     *
     * 之前它存在 localStorage（cv_token）：页面上任何一处 XSS ——
     * 哪怕只是某段富文本漏了一个 onerror —— 都能把它读走，
     * 然后拿着完整身份调管理员接口。现在令牌由后端下发的 HttpOnly Cookie 携带，
     * 浏览器自动带上、脚本读不到；这里保留的只是登录成功后顺手缓存的一份，
     * 刷新即失效，真实凭据靠 Cookie 恢复（见 restore()）。
     */
    token: '',
    userInfo: readCachedUser(),
    /** 是否已用 Cookie 恢复过登录态：路由守卫要等它为真才做跳转判断 */
    restored: false,
    // 助手待执行的跳转指令（由对话结果写入，由全局监听消费）
    pendingAction: null
  }),
  getters: {
    isLogin: state => !!state.token || !!state.userInfo,
    isAdmin: state => !!state.userInfo && state.userInfo.role === 'admin',
    username: state => (state.userInfo ? state.userInfo.username : '')
  },
  actions: {
    setAuth(token, user) {
      this.token = token || ''
      this.userInfo = user
      // 只缓存展示信息，令牌绝不落盘
      try {
        localStorage.setItem('cv_user', JSON.stringify(user))
      } catch {
        /* 隐私模式下 localStorage 可能不可写，忽略即可 */
      }
    },
    // 只更新用户资料（如改姓名），token 不动
    setUser(user) {
      this.userInfo = user
      try {
        localStorage.setItem('cv_user', JSON.stringify(user))
      } catch {
        /* 同上 */
      }
    },
    /**
     * 刷新后用 HttpOnly Cookie 恢复登录态。
     *
     * 由于令牌不再落盘，刷新后内存里的 token 是空的；这里拿 Cookie（浏览器自动带）
     * 问一次 /auth/me，成功就把用户信息填回来，失败就当作已登出清干净。
     *
     * 调用方可以并发调用（路由守卫与 main.js 都会调），这里是幂等的：
     * 只有第一次真正发请求，后续复用同一个 Promise。避免刷新时打两遍 /auth/me。
     */
    restore() {
      if (!restorePromise) {
        restorePromise = this._doRestore()
      }
      return restorePromise
    },
    async _doRestore() {
      try {
        const res = await (await api()).me()
        if (res && res.code === 200 && res.data) {
          this.userInfo = {
            id: res.data.id,
            username: res.data.username,
            realName: res.data.realName || res.data.real_name || '',
            role: res.data.role,
            avatar: res.data.avatar || ''
          }
          try {
            localStorage.setItem('cv_user', JSON.stringify(this.userInfo))
          } catch {
            /* 忽略 */
          }
        } else {
          this.logout()
        }
      } catch {
        // 401 / 网络失败都按「未登录」处理：刷新后本来就该是这个结果
        this.logout()
      } finally {
        this.restored = true
      }
      return this.restored
    },
    logout() {
      this.token = ''
      this.userInfo = null
      try {
        localStorage.removeItem('cv_user')
        // 兼容旧版本残留（升级前存过的令牌），顺手清掉
        localStorage.removeItem('cv_token')
      } catch {
        /* 忽略 */
      }
    },
    /** 主动退出：通知后端清 Cookie，再清本地状态 */
    async logoutRequest() {
      try {
        await (await api()).logout()
      } catch {
        /* 后端清不掉也不影响前端已登出 */
      }
      this.logout()
    },
    setPendingAction(action) {
      this.pendingAction = action
    },
    consumePendingAction() {
      const a = this.pendingAction
      this.pendingAction = null
      return a
    }
  }
})
