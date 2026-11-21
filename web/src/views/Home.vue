<template>
  <div class="page">
    <!-- 欢迎横幅 -->
    <div class="banner fade-up">
      <div class="banner-glow banner-glow-a"></div>
      <div class="banner-glow banner-glow-b"></div>
      <div class="banner-inner">
        <div class="banner-text">
          <div class="banner-eyebrow">
            <el-icon><Lightning /></el-icon>
            <span>可视化 · 智能答疑 · 在线判题</span>
          </div>
          <h1>欢迎回来，{{ userInfo?.realName || '同学' }} 👋</h1>
          <p>今天想攻克哪个知识点？让可视化动画和智能助手帮你把抽象原理看明白。</p>
          <div class="banner-actions">
            <el-button type="primary" size="large" class="btn-hero" @click="$router.push('/agent')">
              <el-icon><ChatDotRound /></el-icon> 问问智能助手
            </el-button>
            <el-button size="large" class="btn-hero-ghost" @click="$router.push('/courses')">
              <el-icon><Reading /></el-icon> 浏览课程中心
            </el-button>
          </div>
        </div>
        <div class="banner-stat">
          <div class="stat-item">
            <div class="stat-num">{{ overview.knowledgeStudied || 0 }}</div>
            <div class="stat-label">已学知识点</div>
          </div>
          <div class="stat-item">
            <div class="stat-num">{{ rate }}%</div>
            <div class="stat-label">答题正确率</div>
          </div>
          <div class="stat-item">
            <div class="stat-num">{{ overview.wrongCount || 0 }}</div>
            <div class="stat-label">待攻克错题</div>
          </div>
        </div>
      </div>
    </div>

    <el-row :gutter="16" style="margin-top:16px">
      <!-- 四大课程 -->
      <el-col :xs="24" :lg="16" class="home-left">
        <div class="card block fade-up">
          <div class="section-title"><el-icon><Reading /></el-icon> 全部课程（{{ courses.length }} 门）</div>
          <div class="course-grid">
            <div
              v-for="c in courses" :key="c.id"
              class="course-card hover-lift"
              :style="{ '--accent': colorOf(c.category) }"
              @click="$router.push('/course/' + c.id)"
            >
              <div class="course-icon">
                <el-icon><component :is="iconOf(c.category)" /></el-icon>
              </div>
              <div class="course-info">
                <div class="course-name">{{ c.name }}</div>
                <div class="course-intro">{{ c.intro }}</div>
                <div class="course-meta">
                  <el-tag size="small" effect="light" round>{{ c.knowledge_count }} 个知识点</el-tag>
                  <el-tag size="small" :type="groupTagType(c)" effect="plain" round>{{ groupTagText(c) }}</el-tag>
                  <span class="progress-text">已学 {{ progressOf(c.id) }}/{{ c.knowledge_count }}</span>
                </div>
                <el-progress
                  :percentage="percentOf(c)" :stroke-width="6" :show-text="false"
                  :color="colorOf(c.category)"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- 其他模块敬请期待：紧跟在课程区下方（.block 自带 margin-bottom:16px）。
             加了 position:sticky，滚动到顶栏下方就停住，右侧长列表在读时
             视线不用来回找。原先用 margin-top:auto 把它压到左列底部对齐右栏，
             左列比右栏短时会造出一整块空白，两个盒子看起来是断开的。 -->
        <div class="card soon-card fade-up">
          <div class="soon-head">
            <el-icon><Grid /></el-icon>
            <b>其他模块敬请期待</b>
            <span class="soon-badge">持续开发中</span>
          </div>
          <div class="soon-grid">
            <div v-for="s in SOON_MODULES" :key="s.t" class="soon-item">
              <el-icon class="soon-ico"><component :is="s.i" /></el-icon>
              <div class="soon-text">
                <div class="soon-name">{{ s.t }}</div>
                <div class="soon-desc">{{ s.d }}</div>
                <!-- 逐条列出这个模块准备做成什么样。只有一句 slogan 撑不满
                     卡片高度（上一版下方留了一大片空白），列 3~4 条具体能力更像路线图。 -->
                <ul class="soon-points">
                  <li v-for="p in s.p" :key="p">{{ p }}</li>
                </ul>
                <!-- 底部一行标签，用 margin-top:auto 顶到卡片底部。
                     卡片会被 grid-auto-rows 拉高到 200px 以上，内容只有 100px 出头，
                     不做这一步的话每张卡片下方都留一条说不清的空白。 -->
                <div class="soon-meta">
                  <span v-for="m in s.m" :key="m" class="soon-tag">{{ m }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-col>

      <!-- 侧栏：学习进度摘要在最上（用户高频关注），其余入口在后 -->
      <el-col :xs="24" :lg="8">
        <!-- 学习进度：环形总览 + 进行中课程 + 可展开的全部列表 -->
        <div class="card block fade-up">
          <div class="section-title"><el-icon><TrendCharts /></el-icon> 我的学习进度</div>
          <template v-if="progressList.length">
            <div class="prog-hero">
              <el-progress
                type="dashboard" :percentage="overallPct" :width="104" :stroke-width="10"
                :color="overallPct >= 100 ? 'var(--success)' : 'var(--brand)'"
              >
                <template #default>
                  <div class="prog-hero-num">{{ overallPct }}%</div>
                  <div class="small muted">总进度</div>
                </template>
              </el-progress>
              <div class="prog-hero-side">
                <div class="prog-line">
                  <b>{{ totalDone }}</b><span class="small muted"> / {{ totalKn }} 个知识点</span>
                </div>
                <div class="prog-line">
                  <b class="p-success">{{ finishedCount }}</b><span class="small muted"> 门课程已完成</span>
                </div>
                <div class="prog-line">
                  <b class="p-brand">{{ inProgress.length }}</b><span class="small muted"> 门课程进行中</span>
                </div>
              </div>
            </div>

            <template v-if="inProgress.length">
              <div class="prog-sub">进行中</div>
              <div v-for="p in inProgress" :key="p.id" class="prog-mini" @click="$router.push('/course/' + p.id)">
                <div class="prog-mini-head">
                  <span class="prog-mini-name">{{ p.name }}</span>
                  <span class="prog-mini-pct">{{ Math.round(p.done / p.total * 100) }}%</span>
                </div>
                <el-progress
                  :percentage="Math.round(p.done / p.total * 100)" :stroke-width="5"
                  :show-text="false" :color="colorOfById(p.id)"
                />
              </div>
            </template>

            <el-button text type="primary" size="small" class="prog-toggle" @click="showAll = !showAll">
              {{ showAll ? '收起全部 ↑' : '查看全部 ' + progressList.length + ' 门课程 →' }}
            </el-button>
            <div v-if="showAll" class="prog-all">
              <div v-for="p in progressList" :key="p.id" class="progress-row">
                <span class="pname">{{ p.name }}</span>
                <el-progress
                  :percentage="p.total ? Math.round(p.done / p.total * 100) : 0"
                  :stroke-width="8" style="flex:1" :color="colorOfById(p.id)"
                />
                <span class="pval">{{ p.done }}/{{ p.total }}</span>
              </div>
            </div>
          </template>
          <el-empty v-else description="暂无学习记录" :image-size="60" />
        </div>

        <!-- 薄弱知识点诊断 -->
        <div class="card block fade-up">
          <div class="section-title"><el-icon><WarningFilled /></el-icon> 薄弱知识点诊断</div>
          <div v-if="weak.length">
            <div v-for="w in weak" :key="w.knowledge_id" class="weak-item" @click="$router.push(w.route)">
              <div class="weak-main">
                <div class="weak-name">{{ w.name }}</div>
                <div class="small muted">{{ w.course_name }}</div>
              </div>
              <el-tag type="danger" size="small" effect="light" round>错 {{ w.wrong_count }} 次</el-tag>
            </div>
            <el-button text type="primary" size="small" style="margin-top:8px" @click="$router.push('/profile?tab=wrong')">
              查看全部错题 →
            </el-button>
          </div>
          <el-empty v-else description="还没有错题，继续保持！" :image-size="60" />
        </div>

        <!-- 程序设计算法题入口 -->
        <div class="card block fade-up">
          <div class="section-title"><el-icon><Trophy /></el-icon> 程序设计算法题</div>
          <div class="algo-entry" @click="$router.push('/algorithm')">
            <div class="algo-icon"><el-icon><Cpu /></el-icon></div>
            <div class="algo-info">
              <div class="algo-name">在线判题 · 权值排名</div>
              <div class="small muted">真实编译运行，逐用例比对，按题目权值累计上榜。</div>
            </div>
          </div>
          <div class="algo-actions">
            <el-button type="primary" size="small" @click="$router.push('/algorithm')">去刷题</el-button>
            <el-button size="small" plain @click="$router.push('/algorithm/ranking')">看排行榜</el-button>
          </div>
        </div>

        <div class="card block fade-up">
          <div class="section-title"><el-icon><MagicStick /></el-icon> 智能助手能做什么</div>
          <div v-for="t in tools" :key="t.name" class="tool-item">
            <div class="tool-name">{{ t.name }}</div>
            <div class="small muted">{{ t.desc }}</div>
          </div>
          <el-button type="primary" plain style="width:100%;margin-top:10px" @click="$router.push('/agent')">
            开始对话
          </el-button>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { courseApi, learnApi, agentApi } from '@/api'
import { useUserStore } from '@/stores/user'

const store = useUserStore()
const userInfo = computed(() => store.userInfo)
const courses = ref([])
const overview = ref({})
const weak = ref([])
const tools = ref([])

const rate = computed(() => {
  const t = overview.value.answerTotal || 0
  return t ? Math.round((overview.value.answerCorrect / t) * 100) : 0
})

const COLORS = {
  ds: '#3b6ef6', net: '#22a06b', os: '#e8a13a', co: '#8b5cf6',
  math: '#e05252', linalg: '#0ea5e9', prob: '#14b8a6', phys: '#f59e0b', dm: '#6366f1',
  c: '#0f766e', cpp: '#1d4ed8', java: '#ea580c', python: '#16a34a',
  html: '#e34c26', css: '#264de4', js: '#d6a327',
  db: '#0e7490', cp: '#7c3aed'
}
const ICONS = {
  ds: 'DataAnalysis', net: 'Connection', os: 'Cpu', co: 'Monitor',
  math: 'TrendCharts', linalg: 'Grid', prob: 'Histogram', phys: 'Compass', dm: 'Share',
  c: 'Document', cpp: 'SetUp', java: 'Coffee', python: 'MagicStick',
  html: 'Files', css: 'Brush', js: 'Lightning',
  db: 'Coin', cp: 'Files'
}
function colorOf(c) { return COLORS[c] || '#3b6ef6' }
function iconOf(c) { return ICONS[c] || 'Reading' }

/* 左下角「其他模块敬请期待」：模块名 + 一句话说明 + 图标 */
/* 规划中的模块。p 是具体要做出来的东西（2~3 条）——
   只写一句 slogan 的话，卡片被 grid-auto-rows 拉高后下方会空一大片，
   看起来像没做完。列成条目才像一份真的路线图。 */
const SOON_MODULES = [
  {
    t: '课程笔记与思维导图',
    d: '边学边记，自动生成知识树',
    i: 'EditPen',
    p: ['知识点内随手记笔记，代码与截图一起存', '按章节自动生成思维导图，可导出图片', '笔记全文检索，按薄弱点推送复习'],
    m: ['与知识点绑定', '可导出']
  },
  {
    t: '历年真题与模拟考',
    d: '按章节组卷，限时模考',
    i: 'Tickets',
    p: ['按知识点和难度组卷，支持单选/多选/判断', '限时模考，交卷后给出分项统计', '考完自动生成报告，标出该背的和该练的'],
    m: ['按章节组卷', '限时模考']
  },
  {
    t: '学习小组与讨论区',
    d: '和同学一起讨论疑难',
    i: 'ChatDotRound',
    p: ['按课程分小组，发帖可附上自己的代码', '答疑标记「已解决」，方便别人直接搜', '小组内共享笔记与解题思路'],
    m: ['按课程分组', '代码可附帖']
  },
  {
    t: '错题智能归因分析',
    d: '定位薄弱环节，给改进建议',
    i: 'TrendCharts',
    p: ['按知识点统计错误率与重复出错次数', '判断是「概念没懂」还是「粗心/笔误」', '给出针对性练习顺序，而不是只列一堆错题'],
    m: ['按知识点归因', '可跟进']
  }
]

/** 课程分组标签（历史数据里 prog / lang 都表示编程语言，统一归一） */
function groupKey(c) {
  const g = c.group_name || 'core'
  return g === 'prog' ? 'lang' : g
}
function groupTagText(c) {
  const g = groupKey(c)
  return g === 'math' ? '数理基础'
    : g === 'lang' ? '编程语言'
    : g === 'web' ? 'Web 前端'
    : '核心课'
}
function groupTagType(c) {
  const g = groupKey(c)
  return g === 'math' ? 'warning'
    : g === 'lang' ? 'success'
    : g === 'web' ? 'danger'
    : 'primary'
}
function progressOf(id) {
  const p = (overview.value.courseProgress || []).find(x => x.id === id)
  return p ? p.done : 0
}
function percentOf(c) {
  const p = (overview.value.courseProgress || []).find(x => x.id === c.id)
  return c.knowledge_count ? Math.round(((p ? p.done : 0) / c.knowledge_count) * 100) : 0
}

/* ---------- 学习进度摘要（右侧栏） ---------- */
const progressList = computed(() => overview.value.courseProgress || [])
const totalKn = computed(() => progressList.value.reduce((s, p) => s + (Number(p.total) || 0), 0))
const totalDone = computed(() => progressList.value.reduce((s, p) => s + (Number(p.done) || 0), 0))
const overallPct = computed(() => (totalKn.value ? Math.round((totalDone.value / totalKn.value) * 100) : 0))
const finishedCount = computed(() => progressList.value.filter(p => p.total && p.done >= p.total).length)
// 进行中的课程：按完成比例降序，右侧栏只露 5 条，其余在「查看全部」里
const inProgress = computed(() =>
  progressList.value
    .filter(p => p.total && p.done > 0 && p.done < p.total)
    .sort((a, b) => b.done / b.total - a.done / a.total)
    .slice(0, 5)
)
const showAll = ref(false)
function colorOfById(id) {
  const c = courses.value.find(x => x.id === id)
  return c ? colorOf(c.category) : 'var(--brand)'
}

onMounted(async () => {
  // 用 allSettled 而非 all：任一接口失败只应让对应区块空着，
  // 不能让「薄弱诊断」这种非核心模块挂掉时连课程列表也一起消失（整页只剩横幅）
  const [c, o, w, t] = await Promise.allSettled([
    courseApi.list(),
    learnApi.overview(),
    learnApi.weakPoints(),
    agentApi.tools()
  ])
  courses.value = c.status === 'fulfilled' ? (c.value?.data || []) : []
  overview.value = o.status === 'fulfilled' ? (o.value?.data || {}) : {}
  weak.value = w.status === 'fulfilled' ? (w.value?.data || []) : []
  tools.value = t.status === 'fulfilled' ? (t.value?.data || []) : []
})
</script>

<style scoped>
/* ---------- 横幅 ---------- */
.banner {
  position: relative; overflow: hidden;
  background: linear-gradient(118deg, #2f5fe0 0%, #3b6ef6 42%, #6f9bff 100%);
  border-radius: var(--radius-lg);
  padding: 30px 34px; color: #fff;
  box-shadow: var(--shadow-brand);
}
.banner-glow {
  position: absolute; border-radius: 50%; pointer-events: none; filter: blur(6px);
}
.banner-glow-a {
  width: 320px; height: 320px; right: -70px; top: -140px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.22) 0%, rgba(255, 255, 255, 0) 68%);
}
.banner-glow-b {
  width: 260px; height: 260px; right: 24%; bottom: -150px;
  background: radial-gradient(circle, rgba(120, 255, 210, 0.20) 0%, rgba(120, 255, 210, 0) 70%);
}
.banner-inner {
  position: relative;
  display: flex; justify-content: space-between; align-items: center; gap: 24px; flex-wrap: wrap;
}
.banner-eyebrow {
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(255, 255, 255, 0.16); border: 1px solid rgba(255, 255, 255, 0.24);
  border-radius: 20px; padding: 4px 13px; font-size: 12px; margin-bottom: 12px;
  backdrop-filter: blur(4px);
}
.banner-text h1 { margin: 0 0 8px; font-size: 26px; letter-spacing: 0.3px; font-weight: 700; }
.banner-text p { margin: 0 0 20px; opacity: 0.92; font-size: 14px; line-height: 1.7; }
.banner-actions { display: flex; gap: 12px; flex-wrap: wrap; }
/* 两个主按钮是同一层级，必须严格等宽等高。
   Element Plus 把按钮内容包进一个 <span>，图标和文字是这个 span 里的两个
   flex 子项。之前只靠 .el-icon 的 margin-right 撑间距，在桌面端两项被压到
   同一基线，图标直接贴在文字上。
   现在改成：span 内用 gap 撑间距、white-space nowrap 禁止换行、图标禁止收缩。

   注意 :deep() 不能省：那个 <span> 是 el-button 自己模板里渲染的，
   不带本组件的 scope 属性，写 `.el-button > span` 压根匹配不上（实测 gap 恒为 0）。*/
.banner-actions .el-button {
  height: 44px; padding: 0 22px;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 15px; font-weight: 600;
}
.banner-actions .el-button :deep(> span) {
  display: inline-flex; align-items: center; justify-content: center;
  gap: 7px; white-space: nowrap; line-height: 1.2;
}
.banner-actions .el-button :deep(.el-icon) {
  margin-right: 0 !important; flex-shrink: 0; font-size: 17px;
}

.btn-hero {
  border: none !important;
  box-shadow: 0 6px 18px rgba(20, 40, 110, 0.32);
  font-weight: 600;
}
.btn-hero:hover { transform: translateY(-2px); box-shadow: 0 10px 24px rgba(20, 40, 110, 0.4); }
.btn-hero-ghost {
  background: rgba(255, 255, 255, 0.16) !important;
  border: 1px solid rgba(255, 255, 255, 0.42) !important;
  color: #fff !important;
  backdrop-filter: blur(6px);
}
.btn-hero-ghost:hover { background: rgba(255, 255, 255, 0.26) !important; transform: translateY(-2px); }

/* 玻璃质感统计块 */
/* 三块 × 92px + 2 个 gap = 300px，折叠屏外屏放不下 —— 允许换行 */
.banner-stat { display: flex; gap: 12px; flex-wrap: wrap; }
.stat-item {
  text-align: center; min-width: 92px; padding: 14px 12px; flex: 1 1 84px;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 14px;
  backdrop-filter: blur(8px);
}
.stat-num { font-size: 27px; font-weight: 700; font-variant-numeric: tabular-nums; }
.stat-label { font-size: 12px; opacity: 0.88; margin-top: 3px; }

/* ---------- 左列：课程卡片 + 底部期待卡片 ----------
   el-row 默认 align-items: stretch，左列会被拉到和右栏一样高。
   这里让左列走 flex column：
     - 课程区 flex: 0 0 auto —— 按内容高度，不额外留白
     - 期待卡片 flex: 0 0 auto —— 同样按内容高度，紧跟在课程区下面

   曾试过让期待卡片 flex: 1 1 auto 吃掉剩余高度、grid-auto-rows: 1fr 把格子拉满，
   右栏短时确实没空白，但右栏「查看全部」展开后左列被一起拉高，
   每张卡撑到 400px+ 而内容全顶在上方 —— 换了个地方留空白，更难看。

   又试过 margin-top: auto 把卡片压到左列底部，让它和右栏底部对齐。
   问题是左列比右栏短时（截图里就是这样：右栏「查看全部」展开后很长），
   auto 会造出一整块说不清的空白，视觉上像是两个盒子断开了。
   用户要的是「两个盒子上下相邻」，所以这里用固定间距，不做对齐。 */
.home-left { display: flex; flex-direction: column; }
.home-left > .block { flex: 0 0 auto; }

/* 期待卡片：紧贴课程区下方，间距 16px 与 .block 的 margin-bottom 一致。 */
.soon-card {
  flex: 0 0 auto;
  min-height: 0;
  display: flex; flex-direction: column;
  margin-bottom: 16px;
  padding: 15px 16px;
  border-radius: var(--radius-lg);
  border: 1px dashed var(--brand-3);
  background: linear-gradient(150deg, var(--brand-light) 0%, var(--card) 68%);
  /* 吸顶：右栏（学习进度 / 薄弱诊断 / 算法入口 / 助手能力）通常比左列长，
     滚到下面时左列已经滚出视野，右侧却还在读，右边就空一大片。
     sticky 让期待卡片滚到顶栏下方就停住，视线不必来回找。
     74px = 顶栏 62px + 12px 间距。

     【不要加 align-self: flex-start —— 上一批踩过的坑】
     .home-left 是 flex-direction: column，交叉轴是「水平方向」，
     flex-start 作用的是宽度：卡片会从「撑满左列」收缩成内容宽（约 255px），
     右边留出一大块空白（用户截图里的问题）。
     当时注释里写「防止被 stretch 拉到与右栏等高」是理解错了：
     column 布局的交叉轴是水平的，子项高度由内容决定（flex: 0 0 auto 不会被拉伸），
     根本不存在「被拉到与右栏等高」这回事。
     sticky 能动的原因是容器（.home-left）被 el-row 拉到与右栏等高，
     而卡片高度小于容器 —— 余量天然存在，不需要 align-self 参与。 */
  position: sticky;
  top: 74px;
}
/* 标题行不参与拉伸，剩余高度全给下面的格子 */
.soon-head { display: flex; align-items: center; gap: 7px; margin-bottom: 12px; color: var(--brand); flex-shrink: 0; }
.soon-head b { font-size: 14px; }
.soon-head .el-icon { font-size: 16px; }
.soon-badge {
  margin-left: auto;
  font-size: 11px; font-weight: 600;
  color: var(--brand);
  background: var(--brand-light);
  border: 1px solid var(--brand-3);
  border-radius: 20px;
  padding: 2px 9px;
}
/* 列宽下限 300px —— 原来是 210px。
   .page 最大 1280px，左列 :lg=16 扣掉 gutter 后内宽约 818px：
   210px 下能排 3 列（每列 262px），5 张卡里的能力条目被挤成两三次换行，
   读起来像坏了。现在 300px 下 818px 只排 2 列（2×300+10=610），
   正好 2×2 四张卡，条目一行放得下。
   同时 grid-auto-rows 改成 auto —— 原来的 1fr 遇到右栏「查看全部」展开后
   变高，会把左列一起拉高，每张卡被撑到 400px+ 而内容全顶在上方。 */
.soon-grid {
  flex: 1 1 auto;
  display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 300px), 1fr));
  grid-auto-rows: auto; align-content: start; gap: 10px;
}
.soon-item {
  display: flex; align-items: stretch; gap: 9px;
  padding: 11px 12px;
  background: var(--soft-bg);
  border: 1px solid var(--border);
  border-radius: 10px;
  transition: border-color .2s, transform .2s;
  min-height: 0;
}
.soon-item:hover { border-color: var(--brand-3); transform: translateY(-2px); }
.soon-ico { font-size: 17px; color: var(--brand-2); flex-shrink: 0; margin-top: 2px; }
.soon-text { min-width: 0; flex: 1; display: flex; flex-direction: column; }
.soon-name { font-size: 13px; font-weight: 600; line-height: 1.4; }
.soon-desc { font-size: 12px; color: var(--text-3); line-height: 1.5; margin-top: 1px; }
.soon-points { list-style: none; margin: 7px 0 0; padding: 0; }
.soon-points li {
  position: relative;
  font-size: 11.5px; line-height: 1.62; color: var(--text-2);
  padding-left: 11px; margin-top: 2px;
}
/* 自绘小圆点，不用 list-style: disc —— 各浏览器缩进不一致，会让文字不对齐 */
.soon-points li::before {
  content: ''; position: absolute;
  left: 1px; top: 7px;
  width: 4px; height: 4px; border-radius: 50%;
  background: var(--brand-3);
}
/* margin-top:auto 把这一行压到卡片底部，吸收掉多余高度 */
.soon-meta { display: flex; flex-wrap: wrap; gap: 5px; margin-top: auto; padding-top: 9px; }
.soon-tag {
  font-size: 10.5px; line-height: 1.7; color: var(--brand-2);
  background: var(--brand-light);
  border: 1px solid var(--brand-3);
  border-radius: 5px; padding: 0 6px;
}

/* ---------- 课程卡片 ---------- */
.block { padding: 20px; margin-bottom: 16px; border-radius: var(--radius-lg); }
/* min(100%, 250px)：容器比 250 还窄（折叠屏外屏）时自动退成单列，不会横向溢出 */
.course-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 250px), 1fr)); gap: 13px; }
.course-card {
  position: relative; overflow: hidden;
  border: 1px solid var(--border); border-radius: var(--radius);
  padding: 15px; display: flex; gap: 13px; cursor: pointer;
}
.course-card::before {
  content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 3px;
  background: var(--accent, var(--brand)); opacity: 0.85;
}
.course-card::after {
  content: ''; position: absolute; inset: 0; pointer-events: none;
  background: radial-gradient(420px 160px at 100% 0%, color-mix(in srgb, var(--accent, #3b6ef6) 12%, transparent) 0%, transparent 70%);
  opacity: 0; transition: opacity 0.24s;
}
.course-card:hover::after { opacity: 1; }
.course-icon {
  width: 44px; height: 44px; border-radius: 12px; color: #fff;
  background: var(--accent, var(--brand));
  display: flex; align-items: center; justify-content: center; font-size: 21px;
  flex-shrink: 0; box-shadow: 0 4px 12px color-mix(in srgb, var(--accent, #3b6ef6) 34%, transparent);
}
.course-info { flex: 1; min-width: 0; }
.course-name { font-weight: 600; font-size: 15px; margin-bottom: 4px; }
.course-intro {
  font-size: 12px; color: var(--text-2); line-height: 1.55;
  height: 37px; overflow: hidden; margin-bottom: 8px;
}
.course-meta { display: flex; align-items: center; gap: 7px; margin-bottom: 7px; flex-wrap: wrap; }
.progress-text { font-size: 12px; color: var(--text-3); }

.progress-row { display: flex; align-items: center; gap: 12px; margin-bottom: 13px; }
.pname { width: 130px; font-size: 13px; }
.pval { width: 46px; text-align: right; font-size: 12px; color: var(--text-2); font-variant-numeric: tabular-nums; }

/* ---------- 学习进度摘要 ---------- */
.prog-hero { display: flex; align-items: center; gap: 16px; margin-bottom: 4px; }
.prog-hero-num { font-size: 22px; font-weight: 700; line-height: 1.2; font-variant-numeric: tabular-nums; }
.prog-hero-side { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 7px; }
.prog-line b { font-size: 17px; margin-right: 4px; font-variant-numeric: tabular-nums; }
.p-success { color: var(--success); }
.p-brand { color: var(--brand); }
.prog-sub {
  font-size: 12px; font-weight: 600; color: var(--text-3); letter-spacing: 0.5px;
  margin: 12px 0 8px; padding-top: 10px; border-top: 1px dashed var(--border);
}
.prog-mini { padding: 7px 9px; border-radius: 9px; cursor: pointer; transition: background 0.2s; }
.prog-mini:hover { background: var(--soft-bg); }
.prog-mini-head { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; margin-bottom: 4px; }
.prog-mini-name { font-size: 13px; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.prog-mini-pct { font-size: 12px; color: var(--text-2); font-variant-numeric: tabular-nums; flex-shrink: 0; }
.prog-toggle { margin-top: 8px; padding-left: 0; }
.prog-all { margin-top: 6px; }

/* ---------- 侧栏 ---------- */
.weak-item {
  display: flex; align-items: center; justify-content: space-between; gap: 10px;
  padding: 10px; border-radius: 10px; cursor: pointer;
  border: 1px solid transparent; transition: all 0.2s;
}
.weak-item:hover { background: var(--brand-light); border-color: var(--brand-3); transform: translateX(2px); }
.weak-main { min-width: 0; }
.weak-name { font-size: 14px; font-weight: 500; }

.algo-entry {
  display: flex; align-items: center; gap: 12px; cursor: pointer;
  border: 1px solid var(--border); border-radius: var(--radius);
  padding: 13px; transition: all .24s;
  background: linear-gradient(135deg, var(--warning-light) 0%, var(--card) 100%);
}
.algo-entry:hover {
  border-color: var(--warning);
  box-shadow: 0 6px 18px rgba(232, 161, 58, 0.18);
  transform: translateY(-2px);
}
.algo-icon {
  width: 42px; height: 42px; border-radius: 12px; flex-shrink: 0; color: #fff;
  background: linear-gradient(135deg, #e8a13a, #f5c069);
  display: flex; align-items: center; justify-content: center; font-size: 21px;
  box-shadow: 0 4px 12px rgba(232, 161, 58, 0.34);
}
.algo-info { min-width: 0; }
.algo-name { font-weight: 600; font-size: 14px; margin-bottom: 3px; }
.algo-actions { display: flex; gap: 8px; margin-top: 11px; }

.tool-item {
  padding: 9px 10px; border-radius: 9px; margin-bottom: 4px;
  border-left: 3px solid var(--brand-3); background: var(--soft-bg);
}
.tool-name { font-size: 13px; font-weight: 600; margin-bottom: 2px; }

/* ---------- 响应式 ---------- */
/* lg 断点（992px）以下 el-col 从 :lg=16 掉成 :xs=24，两栏变单列。
   此时左右没有并排关系，期待卡片吸顶只会挡住下面一整节内容 —— 必须关掉。 */
@media (max-width: 992px) {
  .soon-card { position: static; }
}
@media (max-width: 768px) {
  /* 横幅：留白收一半，标题降一档，否则 360 宽下 h1 会被挤到换行成 4 行 */
  .banner { padding: 20px 18px; }
  .banner-text h1 { font-size: 21px; }
  .banner-text p { font-size: 13px; margin-bottom: 14px; }
  .banner-actions { gap: 8px; }
  .pname { width: 100px; }
  /* 单列布局下没有「右栏」可对齐，交给正常文档流：期待卡片回到内容高度 */
  .soon-card { flex: 0 0 auto; min-height: 0; }
  .soon-grid { grid-template-columns: 1fr; grid-auto-rows: auto; }
}@media (max-width: 480px) {
  .banner { padding: 16px 14px; border-radius: 12px; }
  .banner-text h1 { font-size: 18px; }
  .banner-text p { font-size: 13px; margin-bottom: 14px; }
  /* 两按钮并排等宽：flex:1 1 calc(50% - 4px) 保证两列等分 + 中间留 8px 缝。
     原来用 flex:1 1 100%，两个按钮各占整行但内容宽度不同 → 看着一宽一窄。 */
  .banner-actions { gap: 8px; flex-wrap: nowrap; }
  .banner-actions .el-button {
    flex: 1 1 calc(50% - 4px); min-width: 0; width: 0;
    height: 42px; padding: 0 8px; font-size: 13.5px;
  }
  /* 窄屏空间紧张，gap 从 7px 收到 4px，图标也降一档 */
  .banner-actions .el-button :deep(> span) { gap: 4px; }
  .banner-actions .el-button :deep(.el-icon) { font-size: 15px; }
  .pname { width: 88px; font-size: 12px; }
  .progress-row { gap: 8px; }
  .stat-item { min-width: 78px; padding: 10px 8px; }
  .stat-num { font-size: 22px; }
}
/* 极窄屏（折叠屏外屏 280px）：并排放不下了，回到上下两行但仍等宽 */
@media (max-width: 340px) {
  .banner-actions { flex-wrap: wrap; }
  .banner-actions .el-button { flex: 1 1 100%; width: auto; height: 40px; }
}
</style>
