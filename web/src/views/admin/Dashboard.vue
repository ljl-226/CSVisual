<template>
  <div class="page">
    <div class="page-head">
      <h2>数据统计</h2>
      <el-button @click="load">刷新</el-button>
    </div>

    <!-- 统计卡：数字旁边配图标 + 浅色底，一眼看出「这是哪类数据」。
         原来只有一行数字 + 小字标签，六张卡长得一模一样，只能挨个读标签。
         正确率单独画进度环 —— 39% 光看数字没有感觉，环一出来就知道「四成不到」。 -->
    <el-row :gutter="12" class="stat-cards">
      <el-col :xs="12" :sm="8" :md="6" :lg="4" v-for="s in cards" :key="s.label">
        <div class="card stat-card">
          <div class="sc-top">
            <span class="sc-icon" :style="{ background: s.soft, color: s.color }">
              <el-icon><component :is="s.icon" /></el-icon>
            </span>
            <span v-if="s.ring" class="sc-ring">
              <el-progress type="circle" :percentage="s.ring" :width="52" :stroke-width="6"
                           :color="s.color" />
            </span>
          </div>
          <div class="sc-value" :style="{ color: s.color }">{{ s.value }}</div>
          <div class="sc-label">{{ s.label }}</div>
        </div>
      </el-col>
    </el-row>

    <!-- 主体两列：左课程表 / 右错题 + 活跃用户 + 快捷入口 -->
    <el-row :gutter="16" class="dash-main">
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <div class="card block">
          <div class="section-title">各课程知识点与题目数量</div>
          <!-- 每行加一条双色占比条：条长对齐全场最大值，哪门课内容多哪门少，
               一眼扫过去就知道了，不用在数字之间来回比。 -->
          <el-table :data="stats.byCourse || []" size="small">
            <el-table-column prop="name" label="课程" min-width="150" />
            <el-table-column label="内容量" min-width="180">
              <template #default="{ row }">
                <div class="bar-row">
                  <div class="bar-track">
                    <i class="bar bar-k" :style="{ width: pct(row.question_count, maxCourse) }"></i>
                    <i class="bar bar-q" :style="{ width: pct(row.knowledge_count, maxCourse) }"></i>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="knowledge_count" label="知识点" width="80" align="center" />
            <el-table-column prop="question_count" label="题目" width="80" align="center" />
          </el-table>
          <div class="legend">
            <span><i class="dot dot-q"></i>题目</span>
            <span><i class="dot dot-k"></i>知识点</span>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <!-- 高频错题放右列第一位：左列课程表很长，右栏顶部先给错题，滚动时不再留白。
             （此前加过 sticky 吸顶，按需求已取消定位，恢复普通文档流。） -->
        <div class="card block">
          <div class="section-title">高频错题知识点 TOP 8</div>
          <el-table :data="stats.topWrong || []" size="small">
            <el-table-column prop="name" label="知识点" min-width="170" />
            <el-table-column label="错误次数" min-width="160">
              <template #default="{ row }">
                <div class="bar-row">
                  <div class="bar-track single">
                    <i class="bar bar-w" :style="{ width: pct(row.c, maxWrong) }"></i>
                  </div>
                  <b class="bar-num">{{ row.c }}</b>
                </div>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!stats.topWrong?.length" description="暂无错题数据" :image-size="50" />
        </div>
        <div class="card block">
          <div class="section-title">学习活跃用户 TOP 10</div>
          <el-table :data="stats.activeUsers || []" size="small">
            <el-table-column label="#" width="52" align="center">
              <template #default="{ $index }">
                <span class="rank" :class="'rank-' + ($index + 1)" v-if="$index < 3">{{ $index + 1 }}</span>
                <span class="rank plain" v-else>{{ $index + 1 }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="username" label="账号" />
            <el-table-column prop="real_name" label="姓名" />
            <el-table-column prop="studied" label="已学知识点" width="100" align="center" />
            <el-table-column prop="answers" label="答题数" width="90" align="center" />
          </el-table>
        </div>
        <div class="card block">
          <div class="section-title">快捷入口</div>
          <div class="quick-row">
            <el-button @click="$router.push('/admin/knowledge')">知识点管理</el-button>
            <el-button @click="$router.push('/admin/visualization')">可视化案例</el-button>
            <el-button @click="$router.push('/admin/question')">题库管理</el-button>
            <el-button @click="$router.push('/admin/algorithm')">算法题</el-button>
            <el-button @click="$router.push('/admin/users')">用户管理</el-button>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { adminApi } from '@/api'

const stats = ref({})

/* 统计卡配置：icon / color / soft(浅底) 成对出现 —— 数字的颜色和图标底色一致，
   看到颜色就知道两类数据同源（如「助手对话」配对话气泡）。 */
const cards = computed(() => {
  const rate = stats.value.answerTotal
    ? Math.round((stats.value.answerCorrect / stats.value.answerTotal) * 100)
    : 0
  return [
    { label: '学生用户', value: stats.value.userCount || 0, color: '#3b6ef6', soft: '#e8eefc', icon: 'User' },
    { label: '知识点总数', value: stats.value.knowledgeCount || 0, color: '#22a06b', soft: '#e3f4ec', icon: 'Reading' },
    { label: '题库总数', value: stats.value.questionCount || 0, color: '#e8a13a', soft: '#fbf1df', icon: 'Files' },
    { label: '累计答题', value: stats.value.answerTotal || 0, color: '#8b5cf6', soft: '#efebfd', icon: 'EditPen' },
    { label: '正确率', value: rate + '%', color: '#e05252', soft: '#fbe7e7', icon: 'CircleCheck', ring: rate },
    { label: '助手对话', value: stats.value.chatCount || 0, color: '#2f9ad0', soft: '#e4f2f9', icon: 'ChatDotRound' }
  ]
})

/* 条形图基准：取各表最大值，条长相对化 —— 新增课程/错题变化时条会自动重算 */
const maxCourse = computed(() =>
  Math.max(1, ...(stats.value.byCourse || []).map(r => Number(r.question_count) || 0)))
const maxWrong = computed(() =>
  Math.max(1, ...(stats.value.topWrong || []).map(r => Number(r.c) || 0)))
const pct = (v, max) => Math.round(((Number(v) || 0) / max) * 100) + '%'

async function load() {
  const res = await adminApi.stats()
  stats.value = res.data || {}
}
onMounted(load)
</script>

<style scoped>
.page-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-head h2 { margin: 0; font-size: 20px; }
.stat-cards { margin-bottom: 16px; }

/* ---- 统计卡：图标在左上，数字放大居左，标签垫底 ---- */
.stat-card { padding: 14px 16px; }
.sc-top { display: flex; align-items: center; justify-content: space-between; min-height: 52px; }
.sc-icon {
  width: 38px; height: 38px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 19px; flex-shrink: 0;
}
.sc-ring { line-height: 0; }
.sc-value { font-size: 26px; font-weight: 700; margin-top: 8px; }
.sc-label { font-size: 12px; color: var(--text-2); margin-top: 2px; }

/* ---- 占比条 ---- */
.bar-row { display: flex; align-items: center; gap: 8px; }
.bar-track {
  position: relative; flex: 1; height: 10px; border-radius: 5px;
  background: var(--soft-bg); overflow: hidden;
}
/* 双色条：题目（深）打底、知识点（浅）叠上去 —— 两个量纲不同，
   分开两根条反而看不清谁是谁，叠在一起靠颜色区分更省空间 */
.bar { position: absolute; top: 0; left: 0; height: 100%; border-radius: 5px; }
.bar-q { background: #3b6ef6; opacity: 0.32; }
.bar-k { background: #22a06b; opacity: 0.5; }
.bar-track.single .bar-w { position: static; display: block; background: #e05252; opacity: 0.75; }
.bar-num { min-width: 40px; text-align: right; font-size: 12px; color: var(--text-2); }
.legend { display: flex; gap: 14px; margin-top: 8px; font-size: 12px; color: var(--text-2); }
.legend span { display: inline-flex; align-items: center; gap: 5px; }
.dot { width: 9px; height: 9px; border-radius: 3px; display: inline-block; }
.dot-q { background: #3b6ef6; opacity: 0.32; }
.dot-k { background: #22a06b; opacity: 0.5; }

/* ---- TOP 名次徽标：金 / 银 / 铜，后面的是灰色圆 ---- */
.rank {
  display: inline-flex; width: 22px; height: 22px;
  align-items: center; justify-content: center;
  border-radius: 50%; font-size: 12px; font-weight: 600;
  background: var(--soft-bg); color: var(--text-2);
}
.rank-1 { background: #fdf0d5; color: #b8860b; }
.rank-2 { background: #eef0f3; color: #6b7686; }
.rank-3 { background: #f9e9dd; color: #a05a2c; }

.block { padding: 16px; margin-bottom: 16px; }
.quick-row { display: flex; gap: 8px; flex-wrap: wrap; }
</style>
