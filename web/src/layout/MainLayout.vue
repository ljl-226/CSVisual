<template>
  <div class="layout">
    <header class="header">
      <div class="header-inner">
        <div class="logo" @click="$router.push('/')">
          <BrandLogo />
          <span class="logo-text">
            CSVisual
            <span class="logo-sub">计算机可视化智能学习平台</span>
          </span>
        </div>
        <nav class="nav" v-show="!isNarrow">
          <router-link
            v-for="n in navItems" :key="n.to" :to="n.to"
            class="nav-item" :class="{ 'is-active': isActive(n.to), 'nav-agent': n.agent }"
          >
            <el-icon v-if="n.icon"><component :is="n.icon" /></el-icon>
            {{ n.label }}
          </router-link>
        </nav>
        <div class="user-area">
          <!-- 白天 / 夜晚：状态落在 <html> 上 + localStorage，刷新后保持 -->
          <el-tooltip :content="isDark ? '切换到白天模式' : '切换到夜晚模式'" placement="bottom" :show-after="300">
            <button class="theme-btn" :aria-label="isDark ? '切换到白天模式' : '切换到夜晚模式'" @click="onToggleTheme">
              <el-icon><Sunny v-if="!isDark" /><Moon v-else /></el-icon>
            </button>
          </el-tooltip>
          <el-dropdown @command="onCommand">
            <span class="user-btn">
              <!-- 设了自定义头像就显示图片，没设回退姓名首字 -->
              <el-avatar :size="30" class="avatar" :src="(userInfo && userInfo.avatar) || undefined">
                {{ (userInfo?.realName || 'U')[0] }}
              </el-avatar>
              <span class="uname">{{ userInfo?.realName || userInfo?.username }}</span>
              <el-tag v-if="isAdmin" size="small" type="warning" effect="light" round>管理员</el-tag>
              <el-icon class="caret"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="wrong">我的错题</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <!-- 窄屏：导航收进抽屉，避免顶栏折行成竖排 -->
          <button v-if="isNarrow" class="menu-btn" aria-label="打开导航菜单" @click="menuOpen = true">
            <el-icon><Menu /></el-icon>
          </button>
        </div>
      </div>
    </header>

    <!-- 窄屏导航抽屉：宽度按屏幕比例给，最窄 240 / 最宽 320 -->
    <el-drawer v-model="menuOpen" direction="rtl" :size="drawerSize" class="nav-drawer" :with-header="false">
      <div class="drawer-box">
        <div class="drawer-head">
          <BrandLogo size="sm" />
          <div class="drawer-user">
            <el-avatar :size="40" class="drawer-avatar" :src="(userInfo && userInfo.avatar) || undefined">
              {{ (userInfo?.realName || 'U')[0] }}
            </el-avatar>
            <div class="drawer-user-text">
              <b>{{ userInfo?.realName || userInfo?.username || '未登录' }}</b>
              <span class="muted small">{{ isAdmin ? '管理员' : '学习者' }}</span>
            </div>
          </div>
        </div>
        <router-link
          v-for="n in navItems" :key="n.to" :to="n.to"
          class="drawer-item" :class="{ 'is-active': isActive(n.to), 'nav-agent': n.agent }"
          @click="menuOpen = false"
        >
          <el-icon v-if="n.icon"><component :is="n.icon" /></el-icon>
          <span>{{ n.label }}</span>
          <el-icon class="arrow"><ArrowRight /></el-icon>
        </router-link>
        <div class="drawer-foot">
          <el-button class="drawer-btn" @click="runCmd('profile')">个人中心</el-button>
          <el-button class="drawer-btn" @click="runCmd('wrong')">我的错题</el-button>
          <el-button class="drawer-btn" type="danger" plain @click="runCmd('logout')">退出登录</el-button>
        </div>
      </div>
    </el-drawer>

    <main class="main">
      <div v-if="isAdminRoute" class="admin-shell">
        <aside class="admin-side">
          <div class="side-title">管理后台</div>
          <router-link v-for="m in adminMenus" :key="m.path" :to="m.path" class="side-item">
            <el-icon><component :is="m.icon" /></el-icon>
            <span>{{ m.label }}</span>
            <!-- 待处理数量：藏在菜单里的一级入口等于没有提醒，
                 管理员不可能整天盯着后台刷 —— 有人等着用账号，必须看得见 -->
            <em v-if="m.badge && pendingPasswordRequests" class="side-badge">{{ pendingPasswordRequests }}</em>
          </router-link>
        </aside>
        <section class="admin-content">
          <router-view />
        </section>
      </div>
      <router-view v-else />
    </main>

    <footer class="footer">
      <div class="footer-inner">
        <!-- 品牌区：一句话定位 + 两个主入口 -->
        <div class="footer-brand">
          <div class="footer-brand-top">
            <BrandLogo size="sm" />
            <div class="footer-brand-text">
              <b>CSVisual</b>
              <span class="small muted">计算机专业多学科可视化智能学习平台</span>
            </div>
          </div>
          <p class="footer-slogan small muted">
            把抽象原理画出来 —— {{ courseTotal }} 门课程、{{ knowledgeTotal }} 个知识点，
            每个知识点都配可交互动画与在线判题。
          </p>
          <div class="footer-actions">
            <el-button size="small" type="primary" plain @click="router.push('/courses')">开始学习</el-button>
            <el-button size="small" plain @click="router.push('/agent')">问问智能助手</el-button>
          </div>
        </div>

        <!-- 快速导航：按用户动线分四组，避免一长串链接糊成一行 -->
        <nav class="footer-cols">
          <div v-for="g in footerGroups" :key="g.title" class="footer-col">
            <div class="footer-col-title">{{ g.title }}</div>
            <router-link
              v-for="l in g.links" :key="l.to" :to="l.to" class="footer-link"
            >{{ l.label }}</router-link>
          </div>
        </nav>
      </div>

      <div class="footer-bottom">
        <span class="small muted">© {{ year }} CSVisual · 计算机专业多学科可视化智能学习平台</span>
        <div class="footer-subjects small muted">
          <span v-for="s in SUBJECTS" :key="s">{{ s }}</span>
        </div>
      </div>
    </footer>

    <!-- 全局意见反馈入口：任意页面随手可提，bug 才会有机会被修 -->
    <FeedbackFab />

    <!-- 全局 Agent 跳转指令提示 -->
    <el-dialog v-model="actionVisible" title="智能助手学习建议" width="420px">
      <p style="margin:0 0 8px">{{ pendingTip }}</p>
      <template #footer>
        <el-button @click="actionVisible = false">稍后再看</el-button>
        <el-button type="primary" @click="doAction">立即前往</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { courseApi, adminApi } from '@/api'
import { ElMessage } from 'element-plus'
import { getTheme, toggleTheme } from '@/utils/theme'
import BrandLogo from '@/components/BrandLogo.vue'
import FeedbackFab from '@/components/FeedbackFab.vue'

const router = useRouter()
const route = useRoute()
const store = useUserStore()
const userInfo = computed(() => store.userInfo)
const isAdmin = computed(() => store.isAdmin)

const isDark = ref(getTheme() === 'dark')
function onToggleTheme() {
  isDark.value = toggleTheme() === 'dark'
  ElMessage.success(isDark.value ? '已切换到夜晚模式' : '已切换到白天模式')
}

const isAdminRoute = computed(() => route.path.startsWith('/admin'))

// 自己按路径判断激活态：嵌套路由下 router-link-active 的语义不直观，
// 「首页」会被判成始终激活。这里用精确规则，行为可预期。
const navItems = computed(() => [
  { to: '/', label: '首页' },
  { to: '/courses', label: '课程中心' },
  { to: '/question', label: '题库' },
  { to: '/algorithm', label: '算法题' },
  { to: '/agent', label: '智能学习助手', icon: 'ChatDotRound', agent: true },
  { to: '/profile', label: '个人中心' },
  ...(isAdmin.value ? [{ to: '/admin', label: '管理后台' }] : [])
])
function isActive(to) {
  const p = route.path
  if (to === '/') return p === '/' || p === ''
  return p === to || p.startsWith(to + '/')
}
const adminMenus = [
  { path: '/admin', label: '数据统计', icon: 'DataAnalysis' },
  { path: '/admin/knowledge', label: '知识点管理', icon: 'Collection' },
  { path: '/admin/visualization', label: '可视化案例', icon: 'MagicStick' },
  { path: '/admin/question', label: '题库管理', icon: 'EditPen' },
  { path: '/admin/algorithm', label: '算法题', icon: 'Trophy' },
  { path: '/admin/users', label: '用户管理', icon: 'User' },
  { path: '/admin/security', label: '安全日志', icon: 'Lock' },
  { path: '/admin/feedback', label: '反馈建议', icon: 'ChatLineSquare' },
  // 学生在登录页提交的临时密码申请，最终落到这里处理
  { path: '/admin/password-requests', label: '临时密码申请', icon: 'Key', badge: true }
]

/* ---------- 管理侧：待处理的临时密码申请 ---------- */
const pendingPasswordRequests = ref(0)
async function loadPendingRequests() {
  if (!isAdmin.value) return
  try {
    // 只取计数：pageSize=1 让列表不真的捞出数据，接口额外平铺 pendingCount
    const res = await adminApi.passwordRequests({ page: 1, pageSize: 1, status: 'pending' })
    pendingPasswordRequests.value = Number(res.pendingCount || 0)
  } catch (e) {
    pendingPasswordRequests.value = 0  // 拿不到就不显示角标，不阻塞侧栏
  }
}
watch(() => route.path, p => {
  // 处理完回到后台列表时刷新角标，否则数字会停在进入前的旧值
  if (isAdmin.value && String(p).startsWith('/admin')) loadPendingRequests()
})
onMounted(() => {
  loadPendingRequests()
  // 管理页处理完工单会广播这个事件：不用等下一次路由跳转，角标立刻归零
  window.addEventListener('cv:pwd-req-refresh', loadPendingRequests)
})
onBeforeUnmount(() => window.removeEventListener('cv:pwd-req-refresh', loadPendingRequests))

/* ---------- 页脚 ---------- */
const year = new Date().getFullYear()
const SUBJECTS = [
  '数据结构与算法', '计算机网络', '操作系统', '计算机组成原理',
  '高等数学', '线性代数', '概率统计', '大学物理', '离散数学'
]
/** 页脚按用户动线分四组，比一长串「·」连接的链接更容易扫读。
    这里只放真实存在的静态路由：/course/:id 与 /knowledge/:id 是动态段，
    写裸路径会被兜底路由重定向回首页，点了等于没点。 */
const footerGroups = [
  {
    title: '学习',
    links: [
      { to: '/courses', label: '课程中心' },
      { to: '/', label: '学习总览' }
    ]
  },
  {
    title: '练习',
    links: [
      { to: '/question', label: '题库练习' },
      { to: '/question/ranking', label: '题库排名' },
      { to: '/algorithm', label: '算法题' },
      { to: '/algorithm/ranking', label: '算法排名' }
    ]
  },
  {
    title: '助手',
    links: [
      { to: '/agent', label: '智能学习助手' },
      { to: '/profile', label: '个人中心' },
      { to: '/profile?tab=wrong', label: '我的错题' }
    ]
  },
  {
    title: '关于',
    links: [
      { to: '/register', label: '注册账号' },
      { to: '/forgot', label: '找回密码' }
    ]
  }
]

/* 课程 / 知识点总数：页脚想给出平台规模，不能写死 —— 写死过一次就过期了 */
const courseTotal = ref(0)
const knowledgeTotal = ref(0)
onMounted(async () => {
  try {
    const list = (await courseApi.list()).data || []
    courseTotal.value = list.length
    knowledgeTotal.value = list.reduce(
      (s, c) => s + (Number(c.knowledge_count) || 0), 0
    )
  } catch (e) {
    // 页脚是装饰性信息，拉不到就留空，不能因此在控制台报错或阻塞首屏
  }
})

const actionVisible = ref(false)
const pendingTip = ref('')
let pendingRoute = ''

watch(
  () => store.pendingAction,
  action => {
    if (action && action.route) {
      pendingRoute = action.route
      pendingTip.value = action.label || '智能助手为你推荐了相关内容'
      actionVisible.value = true
    }
  }
)

function doAction() {
  actionVisible.value = false
  store.consumePendingAction()
  if (pendingRoute) router.push(pendingRoute)
}

function onCommand(cmd) {
  if (cmd === 'profile') router.push('/profile')
  else if (cmd === 'wrong') router.push('/profile?tab=wrong')
  else if (cmd === 'logout') {
    store.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  }
}
function runCmd(cmd) {
  menuOpen.value = false
  onCommand(cmd)
}

/* ---------- 窄屏导航 ----------
 * 900px 以下顶栏放不下 6~7 个导航项（会折行成竖排、把副标题挤出去），
 * 这里改成右侧抽屉。断点与 main.css 里的响应式基础层保持同一个数值。 */
const NARROW_BP = 900
const isNarrow = ref(false)
const menuOpen = ref(false)
const drawerSize = computed(() => {
  const w = typeof window === 'undefined' ? 1280 : window.innerWidth
  if (w <= 360) return '82%'
  if (w <= 480) return '78%'
  return '300px'
})
let mql = null
function onMq(e) {
  isNarrow.value = e.matches
  if (!e.matches) menuOpen.value = false
}
onMounted(() => {
  if (typeof window === 'undefined' || !window.matchMedia) return
  mql = window.matchMedia(`(max-width: ${NARROW_BP}px)`)
  isNarrow.value = mql.matches
  if (mql.addEventListener) mql.addEventListener('change', onMq)
  else if (mql.addListener) mql.addListener(onMq)
})
onBeforeUnmount(() => {
  if (!mql) return
  if (mql.removeEventListener) mql.removeEventListener('change', onMq)
  else if (mql.removeListener) mql.removeListener(onMq)
})
// 路由变化（含浏览器前进/后退、抽屉外跳转）一律收起抽屉
watch(() => route.path, () => { menuOpen.value = false })
</script>

<style scoped>
.layout { min-height: 100vh; display: flex; flex-direction: column; }

/* ---------- 顶栏 ---------- */
.header {
  background: var(--header-bg);
  backdrop-filter: saturate(180%) blur(12px);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
}
.header-inner {
  max-width: 1360px;
  margin: 0 auto;
  height: 62px;
  display: flex;
  align-items: center;
  gap: 22px;
  padding: 0 20px;
}
.logo { display: flex; align-items: center; gap: 9px; cursor: pointer; flex-shrink: 0; }
.logo-text {
  font-size: 16px; font-weight: 700;
  display: flex; flex-direction: column; line-height: 1.25; letter-spacing: 0.2px;
}
.logo-sub { font-size: 11px; font-weight: 400; color: var(--text-3); }

.nav { display: flex; gap: 2px; flex: 1; }
.nav-item {
  position: relative;
  padding: 8px 14px; border-radius: 10px; color: var(--text-2);
  font-size: 14px; display: flex; align-items: center; gap: 5px;
  transition: color 0.2s, background 0.2s;
}
.nav-item:hover { background: var(--hover-bg); color: var(--brand); }
/* 激活态：底部渐变指示条，比整块底色更克制也更有辨识度 */
.nav-item.is-active { color: var(--brand); font-weight: 600; background: var(--brand-light); }
.nav-item.is-active::after {
  content: ''; position: absolute; left: 12px; right: 12px; bottom: 2px; height: 3px;
  border-radius: 3px; background: var(--grad-brand);
}
.nav-agent { color: var(--brand); font-weight: 600; }

.user-area { margin-left: auto; display: flex; align-items: center; gap: 10px; }
/* 主题开关：和头像同一高度的圆形图标钮，不抢主操作 */
.theme-btn {
  width: 34px; height: 34px; border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  background: var(--soft-bg);
  border: 1px solid var(--border);
  color: var(--text-2);
  cursor: pointer; font-size: 16px;
  transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
}
.theme-btn:hover {
  color: var(--brand); border-color: var(--brand-3);
  background: var(--brand-light); transform: rotate(-18deg);
}
.user-btn {
  display: flex; align-items: center; gap: 8px; cursor: pointer;
  padding: 4px 10px 4px 4px; border-radius: 22px; outline: none;
  border: 1px solid transparent; transition: all 0.22s;
}
.user-btn:hover { background: var(--card); border-color: var(--border); box-shadow: var(--shadow); }
.uname { font-size: 13px; color: var(--text-2); font-weight: 500; }
.avatar { background: var(--grad-brand); font-weight: 600; }
.caret { color: var(--text-3); font-size: 12px; }
/* 汉堡按钮：只在窄屏出现，和主题钮同一视觉重量 */
.menu-btn {
  width: 34px; height: 34px; border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  background: var(--soft-bg); border: 1px solid var(--border); color: var(--text-2);
  cursor: pointer; font-size: 17px; transition: all 0.22s;
}
.menu-btn:hover { color: var(--brand); border-color: var(--brand-3); background: var(--brand-light); }

/* ---------- 顶栏响应式 ----------
   逐级收缩：先收副标题 → 再压缩导航间距 → 最后整体换成抽屉。
   任何一级都不允许 .nav 折行，折行会把顶栏撑成两行、压掉正文首屏。 */
@media (max-width: 1180px) {
  .logo-sub { display: none; }
  .nav-item { padding: 8px 11px; font-size: 13.5px; }
}
@media (max-width: 1024px) {
  .header-inner { height: 58px; gap: 14px; padding: 0 14px; }
  .nav-item { padding: 7px 9px; font-size: 13px; }
  .nav { gap: 0; }
}
@media (max-width: 900px) {
  .header-inner { height: 56px; gap: 10px; padding: 0 12px; }
  .logo-text { font-size: 15px; }
}
@media (max-width: 600px) {
  .uname { display: none; }
  .user-btn { padding: 3px 6px 3px 3px; }
}
@media (max-width: 400px) {
  .header-inner { padding: 0 8px; gap: 8px; }
  .logo-text { font-size: 14px; }
  .user-btn .el-tag { display: none; }
}

/* ---------- 窄屏导航抽屉 ---------- */
.nav-drawer :deep(.el-drawer__body) { padding: 14px 14px 20px; }
.drawer-box { display: flex; flex-direction: column; height: 100%; }
.drawer-head {
  display: flex; align-items: center; gap: 10px;
  padding: 4px 4px 14px; border-bottom: 1px solid var(--border); margin-bottom: 10px;
}
.drawer-user { display: flex; align-items: center; gap: 10px; line-height: 1.35; }
.drawer-user-text { display: flex; flex-direction: column; line-height: 1.35; }
.drawer-user-text b { font-size: 15px; }
.drawer-item {
  display: flex; align-items: center; gap: 9px;
  padding: 12px 12px; border-radius: 11px;
  color: var(--text-2); font-size: 15px; margin-bottom: 4px;
  transition: background 0.2s, color 0.2s;
}
.drawer-item:hover { background: var(--hover-bg); color: var(--brand); }
.drawer-item.is-active { background: var(--brand-light); color: var(--brand); font-weight: 600; }
.drawer-item.nav-agent { color: var(--brand); font-weight: 600; }
.drawer-item .arrow { margin-left: auto; color: var(--text-3); font-size: 12px; }
.drawer-foot { margin-top: auto; display: flex; flex-direction: column; gap: 8px; padding-top: 14px; }
/* Element Plus 的 el-button 没有 block 属性（那是 Vue2 版的），整宽靠样式 */
.drawer-btn { width: 100%; margin-left: 0 !important; }

.main { flex: 1; }

/* ---------- 管理端：左侧菜单 + 右侧内容 ---------- */
.admin-shell {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  max-width: 1360px;
  margin: 0 auto;
  padding: 18px 20px;
}
.admin-side {
  width: 196px;
  flex: 0 0 196px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 12px 10px;
  position: sticky;
  top: 78px;
}
.side-title {
  font-size: 12px; font-weight: 700; color: var(--text-3);
  padding: 4px 10px 10px; letter-spacing: 0.5px;
}
.side-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 10px 12px;
  border-radius: 9px;
  color: var(--text-2);
  font-size: 14px;
  margin-bottom: 3px;
  transition: all 0.2s;
}
.side-item:hover { background: var(--hover-bg); color: var(--text); transform: translateX(2px); }
.side-badge {
  margin-left: auto; min-width: 18px; height: 18px; padding: 0 5px; border-radius: 9px;
  background: var(--el-color-danger); color: #fff; font-size: 11px; font-style: normal;
  line-height: 18px; text-align: center; font-weight: 600;
}
.side-item.router-link-exact-active {
  background: var(--brand-light);
  color: var(--brand);
  font-weight: 600;
}
.side-item.router-link-exact-active::before {
  content: ''; position: absolute; left: 0; top: 9px; bottom: 9px;
  width: 3px; border-radius: 3px; background: var(--brand);
}
.admin-content { flex: 1; min-width: 0; }
.admin-content :deep(.page) { padding: 0; max-width: none; }
/* 平板 / 手机：左侧菜单改成顶部横向条，内容铺满整宽 */
@media (max-width: 900px) {
  /* align-items 必须改回 stretch：基础样式里的 flex-start 在纵向布局下
     会让内容区按「内容宽度」而不是「容器宽度」排 —— 表格直接撑出视口 245px */
  .admin-shell { flex-direction: column; align-items: stretch; gap: 12px; padding: 12px; }
  .admin-content { width: 100%; min-width: 0; overflow-x: auto; }
  .admin-side {
    width: 100%; flex: none; position: static;
    display: flex; gap: 6px; padding: 8px;
    overflow-x: auto; -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
  }
  .admin-side::-webkit-scrollbar { display: none; }
  .side-title { display: none; }
  .side-item { margin-bottom: 0; white-space: nowrap; padding: 8px 12px; font-size: 13px; }
  .side-item:hover { transform: none; }
  .side-item.router-link-exact-active::before { display: none; }
}

/* ---------- 页脚 ---------- */
.footer {
  border-top: 1px solid var(--border);
  background: var(--footer-bg);
  padding: 26px 20px 16px;
  color: var(--text-2); font-size: 13px;
  margin-top: 20px;
}
.footer-inner {
  max-width: 1360px; margin: 0 auto;
  display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(0, 2fr);
  gap: 28px 40px; align-items: start;
}

/* 品牌区 */
.footer-brand { display: flex; flex-direction: column; gap: 12px; min-width: 0; }
.footer-brand-top { display: flex; align-items: center; gap: 11px; }
.footer-brand-text { display: flex; flex-direction: column; line-height: 1.4; min-width: 0; }
.footer-brand-text b { font-size: 16px; color: var(--text); letter-spacing: 0.2px; }
.footer-slogan { margin: 0; line-height: 1.75; max-width: 420px; }
.footer-actions { display: flex; gap: 10px; flex-wrap: wrap; }
.footer-actions .el-button + .el-button { margin-left: 0; }

/* 四组快速导航：桌面四列，容器不够时自动降列 */
.footer-cols {
  display: grid; gap: 20px 24px;
  grid-template-columns: repeat(auto-fit, minmax(118px, 1fr));
}
.footer-col { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.footer-col-title {
  font-size: 12px; font-weight: 700; color: var(--text-3);
  letter-spacing: 0.6px; margin-bottom: 8px;
}
.footer-link {
  color: var(--text-2); text-decoration: none; font-size: 13px;
  padding: 4px 0; border-radius: 6px;
  transition: color 0.18s, transform 0.18s;
}
.footer-link:hover { color: var(--brand); transform: translateX(2px); }

/* 底部版权条 */
.footer-bottom {
  max-width: 1360px; margin: 22px auto 0; padding-top: 14px;
  border-top: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between;
  gap: 10px 20px; flex-wrap: wrap;
}
.footer-subjects { display: flex; flex-wrap: wrap; gap: 4px 0; }
.footer-subjects span + span::before {
  content: '·'; margin: 0 7px; opacity: 0.55;
}

/* ---------- 页脚响应式 ----------
   平板以下品牌区与导航列改为上下堆叠：并排会把四组链接压成很窄的一列，
   「学习总览」这类四字标签会折行。 */
@media (max-width: 900px) {
  .footer-inner { grid-template-columns: 1fr; gap: 22px; }
  .footer-slogan { max-width: none; }
  .footer-bottom { flex-direction: column; align-items: flex-start; }
}
@media (max-width: 480px) {
  .footer { padding: 20px 14px 14px; }
  /* 极窄屏两组一行已经挤（118px × 2 + 24px 缝 ≈ 260px，280px 屏刚好放下），
     再窄就退成单列，避免「智能学习助手」被压到换行 */
  .footer-cols { grid-template-columns: repeat(auto-fit, minmax(min(100%, 118px), 1fr)); }
  .footer-actions .el-button { flex: 1 1 calc(50% - 5px); margin-left: 0 !important; }
}
</style>
