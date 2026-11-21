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
        <el-icon><Cpu /></el-icon>
        <span class="nav-crumb-text">{{ crumbText }}</span>
      </div>
    </div>

    <div class="head card">
      <div class="head-text">
        <h2 class="page-title">程序设计算法题</h2>
        <p class="small muted">真实编译运行 · 逐用例判分 · 按题目权值累计排名。先自己写，写不出来再看提示和参考答案。</p>
      </div>
      <el-button type="warning" plain class="head-btn" @click="$router.push('/algorithm/ranking')">
        <el-icon><Trophy /></el-icon> 排行榜
      </el-button>
    </div>

    <!-- 筛选 -->
    <div class="filter-bar card">
      <div class="filter-grid">
        <div class="filter-item">
          <label class="filter-label"><el-icon><Star /></el-icon> 难度</label>
          <el-select v-model="difficulty" size="small" clearable placeholder="全部" @change="reload">
            <el-option :value="1" label="入门" />
            <el-option :value="2" label="容易" />
            <el-option :value="3" label="中等" />
            <el-option :value="4" label="较难" />
            <el-option :value="5" label="困难" />
          </el-select>
        </div>

        <div class="filter-item">
          <label class="filter-label"><el-icon><Collection /></el-icon> 标签</label>
          <el-select v-model="tag" size="small" clearable placeholder="全部" @change="reload">
            <el-option v-for="t in tagOptions" :key="t" :value="t" :label="t" />
          </el-select>
        </div>

        <div class="filter-item">
          <label class="filter-label"><el-icon><Files /></el-icon> 来源</label>
          <el-select v-model="source" size="small" clearable placeholder="全部" @change="reload">
            <el-option v-for="s in sourceOptions" :key="s" :value="s" :label="s" />
          </el-select>
        </div>

        <div class="filter-item grow">
          <label class="filter-label"><el-icon><Search /></el-icon> 关键词</label>
          <el-input
            v-model="keyword" size="small" clearable
            placeholder="搜索题目标题 / 标签" @keyup.enter="reload" @clear="reload"
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
      <div v-if="list.length" class="algo-grid">
        <div v-for="a in list" :key="a.id" class="algo-card card" @click="goDetail(a)">
          <div class="ac-head">
            <span class="ac-title">{{ a.title }}</span>
            <el-tag v-if="a.solved" size="small" type="success" effect="dark">
              <el-icon><Select /></el-icon> 已通过
            </el-tag>
          </div>

          <div class="ac-meta">
            <el-tag size="small" :type="diffType(a.difficulty)" effect="light">
              {{ a.difficultyText || '中等' }} {{ '★'.repeat(a.difficulty || 3) }}
            </el-tag>
            <span class="weight-badge" :title="'权值 ' + a.weight + '：通过后可累计到排行榜总分'">
              <el-icon><Trophy /></el-icon> 权值 {{ a.weight }}
            </span>
            <el-tag v-if="a.source" size="small" effect="plain" type="info">{{ a.source }}</el-tag>
          </div>

          <div v-if="tagList(a.tags).length" class="ac-tags">
            <el-tag v-for="t in tagList(a.tags)" :key="t" size="small" effect="plain">{{ t }}</el-tag>
          </div>

          <div class="ac-foot">
            <span class="small muted">通过率 {{ acceptRate(a) }}</span>
            <span class="small muted">{{ a.submitCount || 0 }} 次提交 / {{ a.acceptedCount || 0 }} 人通过</span>
            <el-button size="small" type="primary" plain @click.stop="goDetail(a)">
              {{ a.solved ? '再练一次' : '去挑战' }}
            </el-button>
          </div>
          <el-progress
            v-if="a.solved && a.bestScore" :percentage="scorePercent(a)"
            :stroke-width="6" :show-text="false" color="var(--success)" style="margin-top:8px"
          />
        </div>
      </div>

      <el-empty v-else-if="!loading" :description="hasFilter ? '没有找到匹配的题目，换个条件试试' : '暂无算法题目'">
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
import { algorithmApi } from '@/api'
import { ElMessage } from 'element-plus'
import PaginationBar from '@/components/PaginationBar.vue'
import {
  Trophy, Select, Search, Star, Collection, Files, Cpu,
  ArrowLeft, ArrowRight, Refresh
} from '@element-plus/icons-vue'
import {
  readFilterState, writeFilterState, saveFilterSnapshot, restoreFilterSnapshot
} from '@/utils/filterState'

const route = useRoute()
const router = useRouter()

const list = ref([])
const total = ref(0)
const page = ref(1)
const size = ref(12)
const loading = ref(false)

/* 筛选状态：URL query 优先，缺失时回退 sessionStorage 快照 */
const DEFAULTS = { difficulty: '', tag: '', source: '', keyword: '' }
const init = readFilterState(route, DEFAULTS)
const snap = restoreFilterSnapshot('algo')

const difficulty = ref(init.difficulty !== '' ? init.difficulty : (snap ? snap.state.difficulty : DEFAULTS.difficulty))
const tag = ref(init.tag !== '' ? init.tag : (snap ? snap.state.tag : DEFAULTS.tag))
const source = ref(init.source !== '' ? init.source : (snap ? snap.state.source : DEFAULTS.source))
const keyword = ref(init.keyword !== '' ? init.keyword : (snap ? snap.state.keyword : DEFAULTS.keyword))
page.value = Number(route.query.page) || (snap ? snap.page : 1) || 1

const hasFilter = computed(() =>
  !!(difficulty.value || tag.value || source.value || (keyword.value && keyword.value.trim()))
)

const DIFF_TEXT = { 1: '入门', 2: '容易', 3: '中等', 4: '较难', 5: '困难' }
const crumbText = computed(() => {
  const parts = []
  if (difficulty.value) parts.push(DIFF_TEXT[Number(difficulty.value)] || '难度')
  if (tag.value) parts.push(tag.value)
  if (source.value) parts.push(source.value)
  if (keyword.value && keyword.value.trim()) parts.push('“' + keyword.value.trim() + '”')
  return parts.length ? parts.join(' · ') : '全部算法题'
})

// 标签 / 来源选项：从已加载的题目里汇总（题目表没有单独的枚举接口）
const tagSet = ref([])
const sourceSet = ref([])
const tagOptions = computed(() => tagSet.value)
const sourceOptions = computed(() => sourceSet.value)

/* ---------- 页面内导航 ---------- */
const canBack = ref(true)
const canForward = ref(false)
function syncHistoryState() {
  canBack.value = !!window.history.state
  canForward.value = false
}
function goBack() { canForward.value = true; router.back() }
function goForward() { canForward.value = false; router.forward() }
function reloadPage() { load(); ElMessage.success('已刷新') }

function norm(r) {
  return {
    ...r,
    submitCount: r.submitCount != null ? r.submitCount : (r.submit_count || 0),
    acceptedCount: r.acceptedCount != null ? r.acceptedCount : (r.accepted_count || 0),
    weight: r.weight != null ? r.weight : 10
  }
}

function tagList(tags) {
  if (Array.isArray(tags)) return tags.filter(Boolean)
  return String(tags || '').split(/[,，\s]+/).filter(Boolean)
}

function diffType(d) {
  const n = Number(d) || 3
  if (n <= 2) return 'success'
  if (n === 3) return 'warning'
  return 'danger'
}

function acceptRate(a) {
  const s = Number(a.submitCount) || 0
  const c = Number(a.acceptedCount) || 0
  if (!s) return '暂无'
  return Math.round((c / s) * 100) + '%'
}

function scorePercent(a) {
  const max = Number(a.weight) || 10
  return Math.min(100, Math.round((Number(a.bestScore || 0) / max) * 100))
}

function collectTagSource(rows) {
  const t = new Set(tagSet.value)
  const s = new Set(sourceSet.value)
  rows.forEach(r => {
    tagList(r.tags).forEach(x => t.add(x))
    if (r.source) s.add(String(r.source))
  })
  tagSet.value = [...t].slice(0, 60)
  sourceSet.value = [...s].slice(0, 30)
}

/** 进详情前存筛选快照，从详情返回时才能恢复同样的列表 */
function goDetail(a) {
  if (!a || !a.id) {
    ElMessage.warning('题目信息不完整，无法打开')
    return
  }
  saveFilterSnapshot('algo', {
    difficulty: difficulty.value, tag: tag.value,
    source: source.value, keyword: keyword.value
  }, page.value)
  router.push({ path: '/algorithm/' + a.id, query: { from: 'algo' } })
}

function syncUrl() {
  writeFilterState(router, route, {
    difficulty: difficulty.value, tag: tag.value,
    source: source.value, keyword: keyword.value
  }, page.value)
}

async function load() {
  loading.value = true
  syncUrl()
  try {
    const params = { page: page.value, size: size.value }
    if (difficulty.value) params.difficulty = difficulty.value
    if (tag.value) params.tag = tag.value
    if (source.value) params.source = source.value
    if (keyword.value && keyword.value.trim()) params.keyword = keyword.value.trim()
    const res = await algorithmApi.list(params)
    if (res.code === 200 && res.data) {
      const rows = (res.data.list || []).map(norm)
      list.value = rows
      total.value = Number(res.data.total) || 0
      collectTagSource(rows)
    } else {
      ElMessage.error(res.message || '题目列表加载失败')
      list.value = []
      total.value = 0
    }
  } catch (e) {
    ElMessage.error('题目列表加载失败')
  } finally {
    loading.value = false
  }
}

function reload() { page.value = 1; load() }
function onPaged() { load(); syncHistoryState() }

function resetFilter() {
  difficulty.value = ''
  tag.value = ''
  source.value = ''
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
.nav-crumb-text { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* ---------- 头部 ---------- */
.head {
  display: flex; justify-content: space-between; align-items: center; gap: 16px;
  padding: 18px 20px; margin-bottom: 14px;
}
.head-text { min-width: 0; }
.page-title { margin: 0 0 4px; font-size: 20px; }
.head p { margin: 0; }
.head-btn { flex-shrink: 0; }

/* ---------- 筛选条 ---------- */
.filter-bar { padding: 12px 14px; margin-bottom: 14px; }
.filter-grid {
  display: grid; gap: 10px 14px;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 210px), 1fr));
  align-items: end;
}
.filter-item { display: flex; flex-direction: column; gap: 5px; min-width: 0; }
.filter-item :deep(.el-select) { width: 100%; }
.filter-label { display: flex; align-items: center; gap: 4px; font-size: 12px; color: var(--text-3); font-weight: 500; }
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
.algo-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 320px), 1fr)); gap: 12px; }
.algo-card { padding: 14px 16px; cursor: pointer; transition: all .2s; }
.algo-card:hover { border-color: var(--brand-2); box-shadow: 0 6px 18px rgba(59, 110, 246, .1); transform: translateY(-2px); }
.ac-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; }
.ac-title { font-size: 15px; font-weight: 600; line-height: 1.5; }
.ac-meta { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-top: 10px; }

.weight-badge {
  display: inline-flex; align-items: center; gap: 4px;
  background: linear-gradient(135deg, #e8a13a, #f0b95f); color: #fff;
  font-size: 12px; font-weight: 700; padding: 2px 8px; border-radius: 10px;
  box-shadow: 0 2px 6px rgba(232, 161, 58, .35);
}
.ac-tags { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 10px; }
.ac-foot {
  display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-top: 12px;
  padding-top: 10px; border-top: 1px dashed var(--border);
}
.ac-foot .el-button { margin-left: auto; }


/* ---------- 响应式 ---------- */
@media (max-width: 768px) {
  /* 三个按钮 + 面包屑在平板宽度排不开，面包屑换到第二行独占 */
  .nav-bar { flex-wrap: wrap; }
  .nav-crumb { width: 100%; }
  .head { flex-direction: column; align-items: flex-start; gap: 10px; }
  .head-btn { width: 100%; }
}
@media (max-width: 480px) {
  /* 手机上三按钮平分整行，避免「上一步 下一步」挤成两行 */
  .nav-btns { width: 100%; }
  .nav-btns .el-button { flex: 1; margin-left: 0 !important; padding: 0 6px; }
  .filter-grid { grid-template-columns: 1fr; }
  .filter-foot { flex-wrap: wrap; }
}
</style>