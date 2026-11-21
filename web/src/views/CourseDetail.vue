<template>
  <div class="page" v-if="course">
    <el-breadcrumb separator="/" style="margin-bottom:12px">
      <el-breadcrumb-item :to="{ path: '/courses' }">课程中心</el-breadcrumb-item>
      <el-breadcrumb-item>{{ course.name }}</el-breadcrumb-item>
    </el-breadcrumb>

    <div class="card course-header">
      <div class="course-icon" :style="{ background: colorOf(course.category) }">
        <el-icon><component :is="iconOf(course.category)" /></el-icon>
      </div>
      <div>
        <h2>{{ course.name }}</h2>
        <p class="muted">{{ course.intro }}</p>
      </div>
      <el-button type="primary" @click="goFirst">开始学习</el-button>
    </div>

    <div class="card" style="padding:16px;margin-top:16px">
      <div class="section-title"><el-icon><Menu /></el-icon> 知识点目录（{{ knowledge.length }}）</div>
      <div class="k-list">
        <div v-for="(k, i) in knowledge" :key="k.id" class="k-row" @click="$router.push('/knowledge/' + k.id)">
          <div class="k-index">{{ i + 1 }}</div>
          <div style="flex:1;min-width:0">
            <div class="k-title">{{ k.name }}</div>
            <div class="k-sum">{{ k.summary }}</div>
          </div>
          <div class="k-actions">
            <!-- 三态由共享注册表 labOf() 判定，不在这里靠 route 前缀猜：
                 既没有可视化动画、也没有代码实验室的知识点（数据库/编译原理等
                 教材类知识点）落到「学概念」，跳知识点正文页，
                 而不是挂着一个「看动画」按钮然后 push null -->
            <el-button size="small" @click.stop="$router.push(labOf(k.route, k.id).path)">
              <el-icon><component :is="labOf(k.route, k.id).icon" /></el-icon>
              {{ labOf(k.route, k.id).label }}
            </el-button>
            <el-button size="small" type="primary" plain @click.stop="$router.push('/practice/' + k.id)">做题</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { courseApi } from '@/api'
import { labOf } from '@/data/visMap'

const route = useRoute()
const router = useRouter()
const course = ref(null)
const knowledge = ref([])

const COLORS = {
  ds: '#3b6ef6', net: '#22a06b', os: '#e8a13a', co: '#8b5cf6',
  math: '#e05252', linalg: '#0ea5e9', prob: '#14b8a6', phys: '#f59e0b', dm: '#6366f1',
  c: '#0f766e', cpp: '#1d4ed8', java: '#ea580c', python: '#16a34a',
  html: '#e34c26', css: '#264de4', js: '#d6a327', db: '#0e7490', cp: '#7c3aed'
}
const ICONS = {
  ds: 'DataAnalysis', net: 'Connection', os: 'Cpu', co: 'Monitor',
  math: 'TrendCharts', linalg: 'Grid', prob: 'Histogram', phys: 'Compass', dm: 'Share',
  c: 'Document', cpp: 'SetUp', java: 'Coffee', python: 'MagicStick',
  html: 'Files', css: 'Brush', js: 'Lightning', db: 'Coin', cp: 'Files'
}
function colorOf(c) { return COLORS[c] || '#3b6ef6' }
function iconOf(c) { return ICONS[c] || 'Reading' }
/** 代码实验室类知识点（route 形如 /code/xxx） */
function goFirst() {
  if (knowledge.value[0]) router.push('/knowledge/' + knowledge.value[0].id)
}

onMounted(async () => {
  const res = await courseApi.detail(route.params.id)
  if (res.data) {
    course.value = res.data.course
    knowledge.value = res.data.knowledge
  }
})
</script>

<style scoped>
.course-header { padding: 20px; display: flex; align-items: center; gap: 16px; }
.course-icon {
  width: 52px; height: 52px; border-radius: 13px; color: #fff;
  display: flex; align-items: center; justify-content: center; font-size: 26px;
}
.course-header h2 { margin: 0 0 4px; font-size: 20px; }
.course-header p { margin: 0; font-size: 13px; }
.course-header .el-button { margin-left: auto; }
.k-row {
  display: flex; align-items: center; gap: 14px; padding: 12px;
  border-radius: 10px; cursor: pointer; transition: background 0.2s;
  border-bottom: 1px solid #f0f2f6;
}
.k-row:hover { background: var(--bg); }
.k-index {
  width: 26px; height: 26px; border-radius: 50%; background: var(--brand-light);
  color: var(--brand); font-size: 12px; font-weight: 600;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.k-title { font-weight: 600; font-size: 14px; }
.k-sum { font-size: 12px; color: var(--text-2); margin-top: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.k-actions { display: flex; gap: 8px; }

/* ---------- 响应式 ---------- */
@media (max-width: 600px) {
  .course-header { padding: 14px; gap: 12px; flex-wrap: wrap; }
  .course-icon { width: 44px; height: 44px; border-radius: 11px; font-size: 22px; }
  .course-header h2 { font-size: 18px; }
  .course-header .el-button { margin-left: 0; }
  .k-row { gap: 9px; }
  .k-actions { flex-wrap: wrap; }
}
</style>
