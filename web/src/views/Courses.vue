<template>
  <div class="page">
    <!-- 页面内导航条：不依赖浏览器按钮，手机也能一键后退 / 前进 / 刷新 -->
    <div class="nav-bar card">
      <div class="nav-btns">
        <el-button size="small" :disabled="!canBack" title="回到上一个页面" @click="goBack">
          <el-icon><ArrowLeft /></el-icon> 上一步
        </el-button>
        <el-button size="small" :disabled="!canForward" title="前进到刚刚离开的页面" @click="goForward">
          <el-icon><ArrowRight /></el-icon> 下一步
        </el-button>
        <el-button size="small" title="重新加载课程列表" :loading="loading" @click="reloadPage">
          <el-icon><Refresh /></el-icon> 刷新
        </el-button>
      </div>
      <div class="nav-crumb">
        <el-icon><Reading /></el-icon>
        <span class="nav-crumb-text">{{ crumbText }}</span>
      </div>
    </div>

    <div class="page-head fade-up">
      <div>
        <h2 class="grad-text">课程中心</h2>
        <p class="muted small head-sub">按课程浏览知识点，每个知识点都配有可交互的可视化动画</p>
      </div>
      <el-input
        v-model="keyword" placeholder="搜索知识点，如：三次握手 / 快速排序 / 特征值"
        clearable class="search-box" :prefix-icon="Search"
      />
    </div>

    <div class="tabs-scroll">
      <el-radio-group v-model="group" size="small" class="group-tabs">
      <el-radio-button value="all">全部 {{ courses.length }} 门</el-radio-button>
      <el-radio-button value="core">计算机核心课</el-radio-button>
      <el-radio-button value="math">数学物理基础课</el-radio-button>
      <el-radio-button value="lang">编程语言实战</el-radio-button>
      <el-radio-button value="web">Web 前端开发</el-radio-button>
      </el-radio-group>
    </div>

    <div v-for="c in filtered" :key="c.id" class="card course-block fade-up">
      <div class="course-head" @click="$router.push('/course/' + c.id)">
        <div class="course-icon" :style="{ background: colorOf(c.category), boxShadow: '0 6px 16px ' + colorOf(c.category) + '38' }">
          <el-icon><component :is="iconOf(c.category)" /></el-icon>
        </div>
        <div class="course-title-wrap">
          <div class="course-title">{{ c.name }}</div>
          <div class="muted small course-intro">{{ c.intro }}</div>
        </div>
        <div class="course-meta">
          <span class="course-count">{{ filteredKnowledge(c).length }} 个知识点</span>
          <el-button text type="primary" class="course-enter">进入课程 <el-icon><Right /></el-icon></el-button>
        </div>
      </div>
      <div class="k-grid">
        <div
          v-for="k in filteredKnowledge(c)" :key="k.id"
          class="k-card hover-lift" @click="$router.push('/knowledge/' + k.id)"
        >
          <div class="k-top">
            <span class="k-badge" :class="'badge-' + tagTypeOf(k.route)">
              <el-icon v-if="isCodeLab(k.route)"><Cpu /></el-icon>
              <el-icon v-else-if="k.route"><VideoPlay /></el-icon>
              <el-icon v-else><Document /></el-icon>
              {{ tagTextOf(k.route) }}
            </span>
          </div>
          <div class="k-name">{{ k.name }}</div>
          <div class="k-summary">{{ k.summary }}</div>
          <div class="k-foot">
            <span class="k-go">立即学习</span>
            <el-icon class="k-arrow"><Right /></el-icon>
          </div>
        </div>
      </div>
      <el-empty v-if="!filteredKnowledge(c).length" description="无匹配知识点" :image-size="50" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { courseApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Search, Right, Cpu, VideoPlay, Document, ArrowLeft, ArrowRight, Refresh } from '@element-plus/icons-vue'

const router = useRouter()
const keyword = ref('')
const group = ref('all')
const courses = ref([])
const allKnowledge = ref([])
const loading = ref(false)

/** 分组归一化：历史数据里出现过 prog / lang 两种写法，统一按 lang 处理 */
function groupOf(c) {
  const g = c.group_name || 'core'
  return g === 'prog' ? 'lang' : g
}

const filtered = computed(() =>
  courses.value.filter(c => {
    if (group.value !== 'all' && groupOf(c) !== group.value) return false
    if (!keyword.value) return true
    return filteredKnowledge(c).length > 0
  })
)

function filteredKnowledge(c) {
  const list = allKnowledge.value.filter(k => k.course_id === c.id)
  if (!keyword.value) return list
  const kw = keyword.value.toLowerCase()
  return list.filter(
    k =>
      k.name.toLowerCase().includes(kw) ||
      (k.summary || '').toLowerCase().includes(kw)
  )
}

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

/** 知识点卡片标签：代码实验室 / 可视化动画 / 图文讲解 */
function isCodeLab(route) { return String(route || '').indexOf('/code/') >= 0 }
function tagTextOf(route) {
  if (isCodeLab(route)) return '代码实验室'
  return route ? '可视化动画' : '图文讲解'
}
function tagTypeOf(route) {
  if (isCodeLab(route)) return 'warning'
  return route ? 'primary' : 'info'
}

async function load(silent = false) {
  if (loading.value) return
  loading.value = true
  if (!silent) courses.value = []
  try {
    courses.value = (await courseApi.list()).data || []
    // 逐门课拉详情是 N+1 请求，只要一门课报错就会让整个「知识点」的数据全丢，
    // 搜索框形同虚设。用 allSettled 让失败的那一门安静降级。
    const details = await Promise.allSettled(courses.value.map(c => courseApi.detail(c.id)))
    allKnowledge.value = details.flatMap(d =>
      d.status === 'fulfilled' && d.value && d.value.data ? (d.value.data.knowledge || []) : []
    )
  } catch (e) {
    if (!silent) ElMessage.error('课程加载失败，请检查网络后重试')
    courses.value = []
  } finally {
    loading.value = false
  }
}

/* ---------- 页面内导航：上一步 / 下一步 / 刷新 ---------- */
const canBack = ref(true)
const canForward = ref(false)

/** 当前分组 / 搜索词的可读描述，让导航条顺便告诉用户「现在在看哪一片」 */
const crumbText = computed(() => {
  const parts = []
  if (group.value !== 'all') {
    parts.push({ core: '计算机核心课', math: '数学物理基础课', lang: '编程语言实战', web: 'Web 前端开发' }[group.value] || group.value)
  }
  if (keyword.value && keyword.value.trim()) parts.push(`“${keyword.value.trim()}”`)
  if (!parts.length) return `全部 ${courses.value.length} 门课程`
  return parts.join(' · ')
})

function syncHistoryState() {
  canBack.value = !!window.history.state
  canForward.value = false
}
function goBack() {
  if (!canBack.value) return
  canForward.value = true
  router.back()
}
function goForward() {
  if (!canForward.value) return
  canForward.value = false
  router.forward()
}
function reloadPage() {
  load(true)
  ElMessage.success('已刷新')
}

onMounted(() => {
  syncHistoryState()
  load()
})
</script>

<style scoped>
/* ---------- 页面内导航条：上一步 / 下一步 / 刷新 + 当前位置 ---------- */
.nav-bar {
  display: flex; align-items: center; gap: 12px;
  padding: 9px 12px; margin-bottom: 14px;
}
.nav-btns { display: flex; gap: 8px; flex-shrink: 0; }
.nav-btns .el-button + .el-button { margin-left: 0; }
.nav-crumb {
  display: flex; align-items: center; gap: 6px; min-width: 0;
  font-size: 12.5px; color: var(--text-3);
}
.nav-crumb-text { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.page-head {
  display: flex; justify-content: space-between; align-items: flex-end;
  gap: 20px; margin-bottom: 16px; flex-wrap: wrap;
}
.page-head h2 { margin: 0; font-size: 24px; font-weight: 700; }
.head-sub { margin: 6px 0 0; }
/* 写死 340px 在 360 宽的折叠屏外屏会顶出视口，用 max-width 收口 */
.search-box { width: 340px; max-width: 100%; flex: 0 1 340px; }

.group-tabs { margin-bottom: 16px; }
.group-tabs :deep(.el-radio-button__inner) { border-radius: 20px !important; }
.group-tabs :deep(.el-radio-button:first-child .el-radio-button__inner) { border-radius: 20px !important; }
.group-tabs :deep(.el-radio-button:last-child .el-radio-button__inner) { border-radius: 20px !important; }
.group-tabs :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: var(--grad-brand); border-color: var(--brand);
  box-shadow: 0 3px 10px rgba(59, 110, 246, 0.3);
}

.course-block {
  padding: 20px; margin-bottom: 16px; border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
}
/* flex-wrap：图标 + 标题 + 知识点数 + 「进入课程」四项在窄屏排不开，
   不换行会把按钮顶到视口外（实测 280px 溢出 30px） */
.course-head {
  display: flex; align-items: center; gap: 14px; cursor: pointer; flex-wrap: wrap;
  padding-bottom: 15px; border-bottom: 1px solid var(--border-2); margin-bottom: 15px;
}
.course-icon {
  width: 46px; height: 46px; border-radius: 13px; color: #fff;
  display: flex; align-items: center; justify-content: center; font-size: 23px;
  flex-shrink: 0;
}
.course-title-wrap { flex: 1; min-width: 0; }
.course-title { font-size: 17px; font-weight: 600; margin-bottom: 3px; }
.course-intro { line-height: 1.6; }
/* 计数 + 进入按钮：桌面并排在右侧，窄屏由媒体查询拉成独占第二行 */
.course-meta {
  display: flex; align-items: center; gap: 12px; flex-shrink: 0;
}
.course-count {
  font-size: 12px; color: var(--text-3); background: var(--soft-bg);
  border-radius: 20px; padding: 4px 11px; white-space: nowrap;
}
.course-enter { margin-left: 0 !important; }

.k-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 240px), 1fr)); gap: 13px; }
.k-card {
  position: relative;
  border: 1px solid var(--border); border-radius: var(--radius);
  padding: 15px; cursor: pointer; background: var(--card); overflow: hidden;
}
.k-card:hover { border-color: var(--brand-3); }
.k-card:hover .k-arrow { transform: translateX(4px); color: var(--brand); }
.k-top { margin-bottom: 8px; }
.k-badge {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 11px; font-weight: 600; border-radius: 20px; padding: 3px 10px;
}
.badge-primary { background: var(--brand-light); color: var(--brand-deep); }
.badge-warning { background: var(--warning-light); color: var(--warn-strong); }
.badge-info { background: var(--soft-bg); color: var(--text-2); }
.k-name { font-weight: 600; font-size: 15px; margin-bottom: 6px; }
.k-summary {
  font-size: 12px; color: var(--text-2); line-height: 1.65;
  height: 40px; overflow: hidden;
}
.k-foot {
  display: flex; align-items: center; justify-content: space-between;
  margin-top: 11px; padding-top: 10px; border-top: 1px dashed var(--border-2);
}
.k-go { font-size: 12px; font-weight: 600; color: var(--brand); }
.k-arrow { color: var(--text-3); transition: all 0.22s; }

/* ---------- 响应式 ----------
   移动端原先是「图标 + 标题 + 计数 + 按钮」四列硬挤：
   标题被压成 4 行、简介被压成一条细缝，观感很差。
   这里改为：头部整体两行（图标+标题 / 计数+按钮），
   知识点标签行改横向滚动，避免换行造成的锯齿状排列。 */
@media (max-width: 768px) {
  /* 三个按钮 + 当前位置在平板宽度排不开，位置说明换到第二行独占 */
  .nav-bar { flex-wrap: wrap; }
  .nav-crumb { width: 100%; }
  .page-head { gap: 12px; margin-bottom: 12px; }
  .page-head h2 { font-size: 21px; }
  .search-box { flex: 1 1 100%; width: 100%; }

  /* 分组标签：单行横向滚动，不换行 */
  .tabs-scroll {
    position: relative;
    margin-bottom: 14px;
    -webkit-mask-image: linear-gradient(90deg, #000 0, #000 calc(100% - 34px), transparent 100%);
    mask-image: linear-gradient(90deg, #000 0, #000 calc(100% - 34px), transparent 100%);
  }
  .group-tabs {
    display: flex; flex-wrap: nowrap; overflow-x: auto;
    padding-bottom: 4px;
    scrollbar-width: none; -webkit-overflow-scrolling: touch;
  }
  .group-tabs::-webkit-scrollbar { display: none; }
  .group-tabs :deep(.el-radio-button) { flex-shrink: 0; }
  .group-tabs :deep(.el-radio-button__inner) { padding: 7px 14px; font-size: 13px; }

  .course-block { padding: 14px; border-radius: 12px; }
  /* 头部换行：图标+标题占第一行，计数+按钮占第二行 */
  .course-head {
    gap: 11px; padding-bottom: 12px; margin-bottom: 12px;
    align-items: flex-start;
  }
  .course-icon { width: 40px; height: 40px; border-radius: 11px; font-size: 20px; }
  .course-title { font-size: 16px; margin-bottom: 4px; }
  /* 简介不再限高挤压：窄屏允许两行，读起来比一条细缝舒服 */
  .course-intro { font-size: 12.5px; line-height: 1.65; }
  /* 第二行：计数在左、按钮在右，整行占满 */
  .course-meta {
    flex: 1 0 100%; display: flex; align-items: center; justify-content: space-between;
    gap: 10px; margin-top: 2px;
  }
  .course-enter { margin-left: 0 !important; font-weight: 600; }
  .course-enter .el-icon { margin-left: 2px; }

  .k-grid { gap: 10px; }
  .k-card { padding: 13px; }
  .k-name { font-size: 14.5px; }
  .k-summary { height: 38px; font-size: 12px; }
}
@media (max-width: 480px) {
  /* 手机上三按钮平分整行，避免「上一步 下一步」挤成两行 */
  .nav-btns { width: 100%; }
  .nav-btns .el-button { flex: 1; margin-left: 0 !important; padding: 0 6px; }
  .k-grid { grid-template-columns: 1fr; }
  .k-summary { height: auto; }
}
@media (max-width: 360px) {
  .course-icon { width: 36px; height: 36px; border-radius: 10px; font-size: 18px; }
  /* 「N 个知识点」是次要信息，极窄屏优先保证标题与按钮完整 */
  .course-count { display: none; }
  .course-enter { width: 100%; justify-content: center; }
}
</style>
