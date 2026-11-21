import axios from 'axios'
import { useUserStore } from '@/stores/user'

const http = axios.create({
  baseURL: '/api',
  // 普通接口 30s 够了。跑代码 / 判题不行：本机没编译环境时要退到云端沙箱，
  // 排队 + 冷启动一次二十多秒是常态，照样掐在 30s 上会被前端误报成「连接失败」。
  // 这类请求在下面单独放宽到 RUN_TIMEOUT。
  timeout: 30000,
  /**
   * 带上 Cookie 是整条 HttpOnly 令牌链的关键：
   * 后端登录时把令牌写进 HttpOnly Cookie，浏览器在同源请求里自动带上；
   * 前端 JS 全程读不到它，XSS 也就偷不走。
   * 跨域场景（前端独立域名）需要后端把该域名加进 ALLOWED_ORIGINS，
   * 且 Cookie 走 HTTPS（SameSite=None 必须配 Secure）。
   */
  withCredentials: true
})

http.interceptors.request.use(config => {
  const store = useUserStore()
  if (store.token) config.headers.Authorization = 'Bearer ' + store.token
  // 防重放时间戳：后端对注册 / 改密码 / 找回密码强制校验（±5 分钟）
  config.headers['X-Timestamp'] = Date.now()
  return config
})

http.interceptors.response.use(
  res => res.data,
  err => {
    if (err.response && err.response.status === 401) {
      const store = useUserStore()
      store.logout()
    }
    return Promise.reject(err)
  }
)

// 公开统计（登录页 / 首页用，无需登录）
export const statsApi = {
  overview: () => http.get('/stats')
}

/** 执行类请求的超时：云端沙箱排队 + 冷启动最坏能到 1 分钟级，给 120s 留足余量 */
const RUN_TIMEOUT = 120000

export const authApi = {
  login: data => http.post('/auth/login', data),
  register: data => http.post('/auth/register', data),
  logout: () => http.post('/auth/logout'),
  me: () => http.get('/auth/me'),
  password: data => http.post('/auth/password', data),
  // 找回密码：用「账号 + 注册时填写的姓名」自证身份后重设密码
  forgotConfirm: data => http.post('/auth/forgot/confirm', data),
  // 忘记姓名时的脱敏提示（首字+掩码+末字），帮回忆但不泄露完整姓名
  forgotHint: username => http.get('/auth/forgot/hint', { params: { username } }),
  updateProfile: data => http.post('/auth/profile', data),
  // 头像：multipart 上传，字段名 file（前后端约定）
  uploadAvatar: formData => http.post('/auth/avatar', formData),
  // 恢复默认头像：清空 avatar 记录（默认头像 = 没有自定义头像，前端回退显示姓名首字）
  resetAvatar: () => http.delete('/auth/avatar'),
  // 临时密码：姓名也想不起来时，提交「账号 + 电话」由管理员核身后发放
  applyTempPassword: data => http.post('/auth/temp-password/apply', data),
  // 凭申请单号 + 账号查处理进度，通过后当场把临时密码取回来
  tempPasswordStatus: params => http.get('/auth/temp-password/status', { params })
}

export const courseApi = {  list: () => http.get('/course'),
  detail: id => http.get(`/course/${id}`),
  knowledge: kid => http.get(`/course/knowledge/${kid}`),
  viewKnowledge: kid => http.post(`/course/knowledge/${kid}/view`)
}

export const questionApi = {
  byKnowledge: (kid, params) => http.get(`/question/by-knowledge/${kid}`, { params: params || {} }),
  // 题库：全站练习题集中检索（题库页）
  bank: params => http.get('/question/bank', { params: params || {} }),
  // 题库刷题排行榜
  ranking: params => http.get('/question/ranking', { params: params || {} }),
  randomPaper: params => http.get('/question/paper/random', { params }),
  submit: data => http.post('/question/submit', data),
  submitPaper: data => http.post('/question/submit-paper', data),
  // 主观题（案例分析 / 编程）：交给 Agent 智能判分
  grade: data => http.post('/question/grade', data)
}

export const learnApi = {
  // overview / wrongList / favorites / chats 均支持可选分页（page/pageSize，不传返回全量；
  // 列表类接口 total 平铺响应顶层，overview 用 courseProgressTotal 表达进度总数）
  overview: params => http.get('/learn/overview', { params }),
  wrongList: params => http.get('/learn/wrong', { params }),
  /* 错题重做：取回错题对应的完整题目（可跨知识点）。
     传 ids 则只取这几道（错题本的「重做本页」），不传取全部（上限 200）。 */
  wrongQuestions: params => http.get('/learn/wrong/questions', { params: params || {} }),
  removeWrong: qid => http.delete(`/learn/wrong/${qid}`),
  favorites: params => http.get('/learn/favorite', { params }),
  toggleFavorite: kid => http.post(`/learn/favorite/${kid}`),
  favoriteStatus: kid => http.get(`/learn/favorite/${kid}/status`),
  chats: params => http.get('/learn/chats', { params }),
  weakPoints: () => http.get('/learn/weak-points')
}

export const agentApi = {
  chat: data => http.post('/agent/chat', data),
  clearChats: () => http.delete('/agent/chats'),
  tools: () => http.get('/agent/tools'),
  // 多轮会话
  sessions: () => http.get('/agent/sessions'),
  sessionMessages: id => http.get(`/agent/sessions/${id}/messages`),
  deleteSession: id => http.delete(`/agent/sessions/${id}`),
  // 个性化学习报告 / 向量库状态
  report: () => http.get('/agent/report'),
  vectorStats: () => http.get('/agent/vector-stats'),
  // 工具箱（注册表 + 手动调用）
  capabilities: () => http.get('/agent/capabilities'),
  invokeTool: data => http.post('/agent/tool', data),
  // 记忆模块
  // 传 q 时后端会额外做一次语义召回（列出与这个问题相近的旧笔记）
  memory: params => http.get('/agent/memory', { params: params || {} }),
  clearMemory: scope => http.delete('/agent/memory', { params: { scope } }),
  // 可观测 / 效果评估
  stats: days => http.get('/agent/stats', { params: { days } }),
  traces: limit => http.get('/agent/traces', { params: { limit } })
}

export const codeApi = {
  // 在线运行代码（C / C++ / Java / Python / JavaScript）
  run: data => http.post('/code/run', data, { timeout: RUN_TIMEOUT }),
  // 查询本机可用的运行环境
  env: () => http.get('/code/env')
}

export const algorithmApi = {
  // 题目列表：难度 / 标签 / 来源 / 关键词 / 分页
  list: params => http.get('/algorithm', { params }),
  // 权值排行榜
  ranking: params => http.get('/algorithm/ranking', { params }),
  detail: id => http.get(`/algorithm/${id}`),
  // 参考答案（用户显式点击才请求）
  solution: (id, lang) => http.get(`/algorithm/${id}/solution`, { params: { lang } }),
  // 运行（只跑样例，不计提交）；提交（全量用例 + 记录）
  run: (id, data) => http.post(`/algorithm/${id}/run`, data, { timeout: RUN_TIMEOUT }),
  submit: (id, data) => http.post(`/algorithm/${id}/submit`, data, { timeout: RUN_TIMEOUT }),
  mySubmits: id => http.get(`/algorithm/${id}/my`),
  // 算法小助手：explain / debug / complexity
  assistant: data => http.post('/algorithm/assistant', data),
  // 题解区（模仿洛谷）
  solutions: id => http.get(`/algorithm/${id}/solutions`),
  addSolution: (id, data) => http.post(`/algorithm/${id}/solutions`, data),
  deleteSolution: sid => http.delete(`/algorithm/solutions/${sid}`),
  likeSolution: sid => http.post(`/algorithm/solutions/${sid}/like`)
}

export const feedbackApi = {
  // 学生侧：提交 / 我的反馈 / 撤回（撤回仅限「待处理」）
  submit: data => http.post('/feedback', data),
  mine: params => http.get('/feedback/mine', { params }),
  remove: id => http.delete(`/feedback/${id}`)
}

export const adminApi = {
  knowledge: params => http.get('/admin/knowledge', { params }),
  addKnowledge: data => http.post('/admin/knowledge', data),
  updateKnowledge: (id, data) => http.put(`/admin/knowledge/${id}`, data),
  deleteKnowledge: id => http.delete(`/admin/knowledge/${id}`),
  // 可视化 / 用户列表已支持后端分页（page / pageSize 可选，不传返回全量）
  visualization: params => http.get('/admin/visualization', { params }),
  addVisualization: data => http.post('/admin/visualization', data),
  updateVisualization: (id, data) => http.put(`/admin/visualization/${id}`, data),
  deleteVisualization: id => http.delete(`/admin/visualization/${id}`),
  question: params => http.get('/admin/question', { params }),
  addQuestion: data => http.post('/admin/question', data),
  updateQuestion: (id, data) => http.put(`/admin/question/${id}`, data),
  deleteQuestion: id => http.delete(`/admin/question/${id}`),
  stats: () => http.get('/admin/stats'),
  users: params => http.get('/admin/users', { params }),
  // 管理员帮学生重置密码：返回一次性随机密码明文，由管理员线下告知学生
  resetUserPassword: id => http.post(`/admin/users/${id}/reset-password`),
  // 安全审计日志（date/event 可选筛选，data+total+dates+events 平铺）
  securityLogs: params => http.get('/admin/security-logs', { params }),
  // 用户反馈建议（status/type/keyword 可选筛选，额外平铺 statusCount/statusList/typeList）
  feedback: params => http.get('/admin/feedback', { params }),
  updateFeedback: (id, data) => http.put(`/admin/feedback/${id}`, data),
  deleteFeedback: id => http.delete(`/admin/feedback/${id}`),
  // ---- 临时密码申请（学生提交 → 管理员电话核身后通过 / 驳回）----
  passwordRequests: params => http.get('/admin/password-requests', { params }),
  approvePasswordRequest: id => http.post(`/admin/password-requests/${id}/approve`),
  rejectPasswordRequest: (id, data) => http.post(`/admin/password-requests/${id}/reject`, data),
  // ---- 程序设计算法题 ----
  algorithm: params => http.get('/admin/algorithm', { params }),
  algorithmDetail: id => http.get(`/admin/algorithm/${id}`),
  addAlgorithm: data => http.post('/admin/algorithm', data),
  updateAlgorithm: (id, data) => http.put(`/admin/algorithm/${id}`, data),
  deleteAlgorithm: id => http.delete(`/admin/algorithm/${id}`),
  // ---- 算法题测试用例 ----
  algorithmCases: params => http.get('/admin/algorithm-cases', { params }),
  addAlgorithmCase: data => http.post('/admin/algorithm-cases', data),
  updateAlgorithmCase: (id, data) => http.put(`/admin/algorithm-cases/${id}`, data),
  deleteAlgorithmCase: id => http.delete(`/admin/algorithm-cases/${id}`)
}

export default http
