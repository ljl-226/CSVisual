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
        <el-button size="small" title="重新加载本页数据" :loading="loading" @click="reloadPage">
          <el-icon><Refresh /></el-icon> 刷新
        </el-button>
      </div>
      <div class="nav-crumb">
        <el-icon><Collection /></el-icon>
        <span class="nav-crumb-text">{{ crumbText }}</span>
      </div>
    </div>

    <div class="head card">
      <div class="head-text">
        <h2 class="page-title">题库 · 全部练习题</h2>
        <p class="small muted">各学科知识点的配套练习题集中在这里，按课程分类检索；点击题目即可前往对应知识点边学边练。</p>
      </div>
      <div class="head-btns">
        <el-button plain class="head-btn" @click="$router.push('/question/ranking')">
          <el-icon><Trophy /></el-icon> 刷题排名
        </el-button>
        <el-button type="primary" plain class="head-btn" @click="$router.push('/courses')">
          <el-icon><Reading /></el-icon> 去学知识点
        </el-button>
      </div>
    </div>

    <!-- 筛选：每组「标签 + 控件」包成一块，窄屏时整块换行而不是挤成一团 -->
    <div class="filter-bar card">
      <div class="filter-grid">
        <div class="filter-item">
          <label class="filter-label"><el-icon><Collection /></el-icon> 课程</label>
          <el-select v-model="courseId" size="small" clearable placeholder="全部课程" @change="reload">
            <el-option v-for="c in courseOptions" :key="c.id" :value="c.id" :label="c.name + '（' + c.count + '）'" />
          </el-select>
        </div>

        <div class="filter-item">
          <label class="filter-label"><el-icon><Document /></el-icon> 题型</label>
          <el-select v-model="type" size="small" clearable placeholder="全部" @change="reload">
            <el-option v-for="(t, k) in TYPE_TEXT" :key="k" :value="k" :label="t" />
          </el-select>
        </div>

        <div class="filter-item">
          <label class="filter-label"><el-icon><Star /></el-icon> 难度</label>
          <el-select v-model="difficulty" size="small" clearable placeholder="全部" @change="reload">
            <el-option v-for="d in 5" :key="d" :value="d" :label="DIFF_TEXT[d]" />
          </el-select>
        </div>

        <div class="filter-item grow">
          <label class="filter-label"><el-icon><Search /></el-icon> 关键词</label>
          <el-input
            v-model="keyword" size="small" clearable
            placeholder="搜索题干关键词" @keyup.enter="reload" @clear="reload"
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </div>

        <div class="filter-ops">
          <el-button size="small" type="primary" :loading="loading" @click="reload">
            <el-icon><Search /></el-icon> 搜索
          </el-button>
          <el-button size="small" plain :disabled="!hasFilter" @click="resetFilter">重置</el-button>
        </div>
      </div>

      <div class="filter-foot">
        <span class="small muted">共 <b class="f-num">{{ total }}</b> 题</span>
        <span v-if="hasFilter" class="f-chip">
          已筛选
          <button class="f-clear" title="清空全部筛选" @click="resetFilter">✕</button>
        </span>
      </div>
    </div>

    <!-- 题目列表 -->
    <div v-loading="loading">
      <div v-if="list.length" class="qbank-grid">
        <div v-for="q in list" :key="q.id" class="qbank-card card" @click="goPractice(q)">
          <div class="qc-head">
            <el-tag size="small" :type="typeTagType(q.type)" effect="light">{{ typeText(q.type) }}</el-tag>
            <el-tag size="small" :type="diffType(q.difficulty)" effect="plain">
              {{ diffText(q.difficulty) }}
            </el-tag>
            <el-tag v-if="q.source" size="small" effect="plain" type="info">{{ q.source }}</el-tag>
          </div>

          <div class="qc-title">{{ q.title }}</div>

          <div class="qc-foot">
            <span class="qc-src" :title="q.course_name + ' · ' + q.knowledge_name">
              <el-icon><Collection /></el-icon>
              {{ q.course_name }} · {{ q.knowledge_name }}
            </span>
            <span class="small muted">{{ q.score }} 分</span>
            <el-button size="small" type="primary" plain @click.stop="goPractice(q)">
              去做题
            </el-button>
          </div>
        </div>
      </div>

      <el-empty v-else-if="!loading" :description="hasFilter ? '没有找到匹配的题目，换个条件试试' : '题库暂无题目'">
        <el-button v-if="hasFilter" type="primary" plain @click="resetFilter">重置筛选</el-button>
      </el-empty>

      <PaginationBar v-if="total > size" :total="total" v-model:page="page" v-model:pageSize="size"
                     :sizes="[12, 24, 48]" @change="onPaged" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { questionApi } from '@/api'
import { ElMessage } from 'element-plus'
import PaginationBar from '@/components/PaginationBar.vue'
import {
  Search, Collection, Reading, Document, Star,
  ArrowLeft, ArrowRight, Refresh, Trophy
} from '@element-plus/icons-vue'
import {
  readFilterState, writeFilterState, saveFilterSnapshot, restoreFilterSnapshot
} from '@/utils/filterState'

const TYPE_TEXT = { single: '单选', judge: '判断', multi: '多选', case: '案例', programming: '编程' }
const DIFF_TEXT = { 1: '入门', 2: '容易', 3: '中等', 4: '较难', 5: '困难' }

const route = useRoute()
const router = useRouter()

const list = ref([])
const courseOptions = ref([])
const total = ref(0)
const page = ref(1)
const size = ref(12)
const loading = ref(false)

/* 筛选条件的默认值。readFilterState 会优先从 URL query 还原，
   URL 上没有时回退 sessionStorage 快照（从详情页直接返回的场景）。 */
const DEFAULTS = { course: '', type: '', difficulty: '', keyword: '' }
const init = readFilterState(route, DEFAULTS)
const snap = restoreFilterSnapshot('qbank')

const courseId = ref(init.course !== '' ? init.course : (snap ? snap.state.course : DEFAULTS.course))
const type = ref(init.type !== '' ? init.type : (snap ? snap.state.type : DEFAULTS.type))
const difficulty = ref(init.difficulty !== '' ? init.difficulty : (snap ? snap.state.difficulty : DEFAULTS.difficulty))
const keyword = ref(init.keyword !== '' ? init.keyword : (snap ? snap.state.keyword : DEFAULTS.keyword))
page.value = Number(route.query.page) || (snap ? snap.page : 1) || 1

const hasFilter = computed(() =>
  !!(courseId.value || type.value || difficulty.value || (keyword.value && keyword.value.trim()))
)

/** 当前筛选的可读描述：给导航条上的面包屑用，顺便让用户知道自己在筛什么 */
const crumbText = computed(() => {
  const parts = []
  const c = courseOptions.value.find(x => String(x.id) === String(courseId.value))
  if (c) parts.push(c.name)
  if (type.value) parts.push(TYPE_TEXT[type.value])
  if (difficulty.value) parts.push(DIFF_TEXT[difficulty.value])
  if (keyword.value && keyword.value.trim()) parts.push('“' + keyword.value.trim() + '”')
  return parts.length ? parts.join(' · ') : '全部题目'
})

/* ---------- 页面内导航：上一步 / 下一步 / 刷新 ---------- */
const canBack = ref(true)
const canForward = ref(false)

function syncHistoryState() {
  // history.state 为 null 说明这是本会话的第一页，上一步不该可点
  canBack.value = !!window.history.state
  canForward.value = false
}
/** 用 router.push 走 SPA 内部跳转时同步记录；back/forward 之后再校准 */
function markForward(on) {
  if (on) canForward.value = true
}

function goBack() {
  if (!canBack.value) return
  markForward(true)
  router.back()
}
function goForward() {
  if (!canForward.value) return
  canForward.value = false
  router.forward()
}
function reloadPage() {
  load()
  ElMessage.success('已刷新')
}

function typeText(t) { return TYPE_TEXT[t] || '练习' }
function typeTagType(t) {
  return { single: 'primary', judge: 'success', multi: 'warning', case: 'danger', programming: 'danger' }[t] || 'info'
}
function diffText(d) { return DIFF_TEXT[Number(d)] || '中等' }
function diffType(d) {
  const n = Number(d) || 3
  if (n <= 2) return 'success'
  if (n === 3) return 'warning'
  return 'danger'
}

/**
 * 进入练习页。带上 qid（题目 id）和筛选快照：
 * Practice 读到 qid 会直接定位到那一题；没有 qid 时用快照里的 kid 兜底。
 */
function goPractice(q) {
  const kid = q && q.knowledge_id
  if (!kid) {
    ElMessage.warning('这道题没有关联知识点，暂时无法进入练习')
    return
  }
  saveFilterSnapshot('qbank', {
    course: courseId.value, type: type.value,
    difficulty: difficulty.value, keyword: keyword.value
  }, page.value)
  router.push({ path: '/practice/' + kid, query: { qid: q.id, from: 'qbank' } })
}

function syncUrl() {
  writeFilterState(router, route, {
    course: courseId.value, type: type.value,
    difficulty: difficulty.value, keyword: keyword.value
  }, page.value)
}

async function load() {
  loading.value = true
  syncUrl()
  try {
    const params = { page: page.value, size: size.value }
    if (courseId.value) params.course = courseId.value
    if (type.value) params.type = type.value
    if (difficulty.value) params.difficulty = difficulty.value
    if (keyword.value && keyword.value.trim()) params.keyword = keyword.value.trim()
    const res = await questionApi.bank(params)
    if (res.code === 200 && res.data) {
      list.value = res.data.list || []
      total.value = Number(res.data.total) || 0
      courseOptions.value = res.data.courses || []
    } else {
      ElMessage.error(res.message || '题库加载失败')
      list.value = []
      total.value = 0
    }
  } catch (e) {
    ElMessage.error('题库加载失败')
  } finally {
    loading.value = false
  }
}

function reload() { page.value = 1; load() }
function onPaged() { load(); syncHistoryState(); markForward(true) }
function resetFilter() {
  courseId.value = ''
  type.value = ''
  difficulty.value = ''
  keyword.value = ''
  reload()
}

onMounted(() => {
  syncHistoryState()
  load()
})
</script>

<style scoped>
/* ---------- 页面内导航条：上一步 / 下一步 / 刷新 + 筛选面包屑 ---------- */
.nav-bar {
  display: flex; align-items: center; gap: 12px;
  padding: 9px 12px; margin-bottom: 12px;
}
.nav-btns { display: flex; gap: 8px; flex-shrink: 0; }
.nav-btns .el-button + .el-button { margin-left: 0; }
.nav-crumb {
  display: flex; align-items: center; gap: 6px; min-width: 0;
  font-size: 12.5px; color: var(--text-3);
}
.nav-crumb-text {
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

/* ---------- 头部 ---------- */
.head {
  display: flex; justify-content: space-between; align-items: center; gap: 16px;
  padding: 18px 20px; margin-bottom: 14px;
}
.head-text { min-width: 0; }
.page-title { margin: 0 0 4px; font-size: 20px; }
.head p { margin: 0; }
/* 两个入口按钮并排；窄屏由媒体查询拉成上下两行各自整宽 */
.head-btns { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
.head-btn { flex-shrink: 0; }

/* ---------- 筛选条 ----------
   原来是一行 flex + 内联 style="width:170px"，窄屏下标签和控件会挤成一团。
   改成 grid：每个「标签 + 控件」是一格，窄屏整格换行，控件自己撑满格子。 */
.filter-bar { padding: 12px 14px; margin-bottom: 14px; }
.filter-grid {
  display: grid; gap: 10px 14px;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 210px), 1fr));
  align-items: end;
}
.filter-item { display: flex; flex-direction: column; gap: 5px; min-width: 0; }
.filter-item.grow { grid-column: span 1; }
/* 控件统一撑满所在格，不再靠内联 width 各写各的 */
.filter-item :deep(.el-select) { width: 100%; }

.filter-label {
  display: flex; align-items: center; gap: 4px;
  font-size: 12px; color: var(--text-3); font-weight: 500;
}
.filter-label .el-icon { font-size: 13px; }

.filter-ops { display: flex; gap: 8px; align-items: center; }
.filter-ops .el-button { flex: 1; }

.filter-foot {
  display: flex; align-items: center; gap: 10px;
  margin-top: 10px; padding-top: 9px; border-top: 1px dashed var(--border);
  font-size: 12.5px;
}
.f-num { color: var(--brand); font-variant-numeric: tabular-nums; }
.f-chip {
  display: inline-flex; align-items: center; gap: 4px;
  background: var(--brand-light); color: var(--brand);
  border-radius: 10px; padding: 1px 4px 1px 9px; font-size: 12px;
}
.f-clear {
  border: none; background: transparent; color: inherit; cursor: pointer;
  font-size: 12px; padding: 0 3px; line-height: 1.5; border-radius: 6px;
}
.f-clear:hover { background: var(--brand-3); }

/* ---------- 题目卡片 ---------- */
.qbank-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 300px), 1fr)); gap: 12px; }
.qbank-card { padding: 14px 16px; cursor: pointer; transition: all .2s; display: flex; flex-direction: column; }
.qbank-card:hover { border-color: var(--brand-2); box-shadow: 0 6px 18px rgba(59, 110, 246, .1); transform: translateY(-2px); }
.qc-head { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.qc-title {
  margin-top: 10px; font-size: 14px; line-height: 1.7; color: var(--text);
  display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
  min-height: 0; flex: 1;
}
.qc-foot {
  display: flex; align-items: center; gap: 10px; margin-top: 12px;
  padding-top: 10px; border-top: 1px dashed var(--border);
}
.qc-src {
  flex: 1; min-width: 0; display: flex; align-items: center; gap: 4px;
  font-size: 12px; color: var(--text-3);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.qc-foot .el-button { margin-left: auto; flex-shrink: 0; }


/* ---------- 响应式 ---------- */
@media (max-width: 768px) {
  /* 三个按钮 + 面包屑在平板宽度排不开，面包屑换到第二行独占 */
  .nav-bar { flex-wrap: wrap; }
  .nav-crumb { width: 100%; }
  .head { flex-direction: column; align-items: flex-start; gap: 10px; }
  .head-btns { width: 100%; }
  .head-btn { flex: 1; margin-left: 0 !important; }
}
@media (max-width: 480px) {
  /* 手机上三按钮平分整行，避免「上一步 下一步」挤成两行 */
  .nav-btns { width: 100%; }
  .nav-btns .el-button { flex: 1; margin-left: 0 !important; padding: 0 6px; }
  .filter-grid { grid-template-columns: 1fr; }
  .filter-ops { flex-direction: row; }
  .filter-foot { flex-wrap: wrap; }
}
</style>