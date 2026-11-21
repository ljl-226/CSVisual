import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  { path: '/login', name: 'Login', component: () => import('@/views/Login.vue'), meta: { public: true } },
  { path: '/register', name: 'Register', component: () => import('@/views/Register.vue'), meta: { public: true } },
  { path: '/forgot', name: 'ForgotPassword', component: () => import('@/views/ForgotPassword.vue'), meta: { public: true } },
  // 姓名也想不起来时的兜底：提交账号 + 电话，由管理员核实后发放临时密码
  { path: '/temp-password', name: 'TempPassword', component: () => import('@/views/TempPassword.vue'), meta: { public: true } },
  {
    path: '/',
    component: () => import('@/layout/MainLayout.vue'),
    children: [
      { path: '', name: 'Home', component: () => import('@/views/Home.vue'), meta: { title: '首页' } },
      { path: 'courses', name: 'Courses', component: () => import('@/views/Courses.vue'), meta: { title: '课程中心' } },
      { path: 'course/:id', name: 'CourseDetail', component: () => import('@/views/CourseDetail.vue'), meta: { title: '课程详情' } },
      { path: 'knowledge/:id', name: 'Knowledge', component: () => import('@/views/KnowledgeDetail.vue'), meta: { title: '知识点' } },
      { path: 'vis/:name', name: 'Vis', component: () => import('@/views/VisPlayer.vue'), meta: { title: '可视化演示', fullscreen: true } },
      { path: 'code/:slug', name: 'CodeLab', component: () => import('@/views/CodeLab.vue'), meta: { title: '代码实验室' } },
      { path: 'practice/:kid', name: 'Practice', component: () => import('@/views/Practice.vue'), meta: { title: '练习' } },
      /* 错题重做：跨知识点的一份错题题集，复用练习页（kid 传 0，页面按 wrong 模式取题） */
      { path: 'wrong-practice', name: 'WrongPractice', component: () => import('@/views/Practice.vue'), meta: { title: '错题重做' } },
      // 程序设计算法题（ranking 必须放在 :id 之前）
      { path: 'algorithm', name: 'Algorithm', component: () => import('@/views/Algorithm.vue'), meta: { title: '程序设计算法题' } },
      { path: 'algorithm/ranking', name: 'AlgorithmRanking', component: () => import('@/views/AlgorithmRanking.vue'), meta: { title: '算法排行榜' } },
      { path: 'algorithm/:id', name: 'AlgorithmDetail', component: () => import('@/views/AlgorithmDetail.vue'), meta: { title: '算法题详情' } },
      // 题库：全站知识点练习题集中检索
      { path: 'question', name: 'QuestionBank', component: () => import('@/views/QuestionBank.vue'), meta: { title: '题库' } },
      { path: 'question/ranking', name: 'QuestionRanking', component: () => import('@/views/QuestionRanking.vue'), meta: { title: '题库排行榜' } },
      { path: 'agent', name: 'Agent', component: () => import('@/views/AgentChat.vue'), meta: { title: '智能学习助手' } },
      { path: 'profile', name: 'Profile', component: () => import('@/views/Profile.vue'), meta: { title: '个人中心' } },
      // 管理员后台
      { path: 'admin', name: 'AdminDashboard', component: () => import('@/views/admin/Dashboard.vue'), meta: { title: '数据统计', admin: true } },
      { path: 'admin/knowledge', name: 'AdminKnowledge', component: () => import('@/views/admin/KnowledgeManage.vue'), meta: { title: '知识点管理', admin: true } },
      { path: 'admin/visualization', name: 'AdminVisualization', component: () => import('@/views/admin/VisualizationManage.vue'), meta: { title: '可视化案例管理', admin: true } },
      { path: 'admin/question', name: 'AdminQuestion', component: () => import('@/views/admin/QuestionManage.vue'), meta: { title: '题库管理', admin: true } },
      { path: 'admin/algorithm', name: 'AdminAlgorithm', component: () => import('@/views/admin/AlgorithmManage.vue'), meta: { title: '算法题管理', admin: true } },
      { path: 'admin/users', name: 'AdminUsers', component: () => import('@/views/admin/UserManage.vue'), meta: { title: '用户管理', admin: true } },
      { path: 'admin/security', name: 'AdminSecurity', component: () => import('@/views/admin/SecurityLog.vue'), meta: { title: '安全日志', admin: true } },
      { path: 'admin/feedback', name: 'AdminFeedback', component: () => import('@/views/admin/FeedbackManage.vue'), meta: { title: '反馈建议', admin: true } },
      { path: 'admin/password-requests', name: 'AdminPasswordRequests', component: () => import('@/views/admin/PasswordRequestManage.vue'), meta: { title: '临时密码申请', admin: true } }
    ]
  },
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

/** 恢复登录态最多等多久：后端挂了也不能让页面一直白着 */
const RESTORE_TIMEOUT = 3000

router.beforeEach(async (to, from, next) => {
  const store = useUserStore()

  /**
   * 令牌存在 HttpOnly Cookie 里，刷新后 store 是空的 —— 需要先问一次 /auth/me
   * 才能判断登录态。只对**需要登录**的路由等：
   *  · 公开页（首页、登录页）不必等，点了就能看，首屏不受网络影响
   *  · 受保护页必须等，否则刷新会被误判成未登录弹回登录页
   * 后端不可达时由超时兜底，按未登录处理。
   */
  if (!to.meta.public && !store.restored) {
    await Promise.race([
      store.restore(),
      new Promise(r => setTimeout(() => { store.restored = true; r() }, RESTORE_TIMEOUT))
    ])
  }

  if (!to.meta.public && !store.isLogin) {
    return next({ path: '/login', query: { redirect: to.fullPath } })
  }
  if (to.meta.admin && !store.isAdmin) {
    return next({ path: '/' })
  }
  if (to.meta.public && store.isLogin && to.path === '/login') {
    return next({ path: '/' })
  }
  next()
})

router.afterEach(to => {
  document.title = (to.meta.title ? to.meta.title + ' · ' : '') + 'CSVisual 可视化学习平台'
})

export default router
