<template>
  <div class="page" v-if="data">
    <el-breadcrumb separator="/" style="margin-bottom:12px">
      <el-breadcrumb-item :to="{ path: '/courses' }">课程中心</el-breadcrumb-item>
      <el-breadcrumb-item :to="{ path: '/course/' + data.knowledge.course_id }">{{ data.knowledge.course_name }}</el-breadcrumb-item>
      <el-breadcrumb-item>{{ data.knowledge.name }}</el-breadcrumb-item>
    </el-breadcrumb>

    <el-row :gutter="16">
      <el-col :xs="24" :sm="24" :md="24" :lg="16">
        <div class="card k-main fade-up">
          <div class="k-head">
            <div class="k-head-left">
              <span class="k-chip">{{ data.knowledge.course_name }}</span>
              <h2>{{ data.knowledge.name }}</h2>
            </div>
            <div class="k-head-actions">
              <el-button :type="favorited ? 'warning' : 'default'" round @click="toggleFav">
                <el-icon><Star :filled="favorited" /></el-icon> {{ favorited ? '已收藏' : '收藏' }}
              </el-button>
              <el-button type="primary" round class="btn-cta" @click="$router.push(data.knowledge.route)">
                <el-icon><VideoPlay /></el-icon> 打开可视化动画
              </el-button>
            </div>
          </div>
          <p class="summary">{{ data.knowledge.summary }}</p>
          <el-divider />
          <div class="markdown-body" v-html="renderedContent"></div>
        </div>

        <!-- 可视化案例 -->
        <div class="card fade-up" style="padding:18px;margin-top:16px">
          <div class="section-title"><el-icon><VideoPlay /></el-icon> 配套可视化动画</div>
          <div class="vis-list">
            <div v-for="v in data.visualizations" :key="v.id" class="vis-card hover-lift" @click="$router.push(data.knowledge.route)">
              <div class="vis-thumb"><el-icon><VideoPlay /></el-icon></div>
              <div class="vis-info">
                <div class="vis-title">{{ v.title }}</div>
                <div class="vis-desc">{{ v.description }}</div>
              </div>
              <el-icon class="vis-arrow"><Right /></el-icon>
            </div>
            <el-empty v-if="!data.visualizations.length" description="暂无可视化案例" :image-size="50" />
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :sm="24" :md="24" :lg="8" class="k-side-col">
        <div class="k-side-sticky">
        <div class="card side side-practice fade-up">
          <div class="section-title"><el-icon><EditPen /></el-icon> 随堂练习</div>
          <p class="muted small">
            本知识点共 <b class="q-count">{{ questionCount }}</b> 道配套习题，做完自动记录错题。
          </p>
          <el-button type="primary" style="width:100%" round @click="$router.push('/practice/' + data.knowledge.id)">
            开始练习
          </el-button>
        </div>
        <div class="card side side-agent fade-up">
          <div class="section-title"><el-icon><ChatDotRound /></el-icon> 不懂就问智能学习助手</div>
          <p class="muted small">让智能助手针对「{{ data.knowledge.name }}」深入讲解，还能自动带你回到动画页面。</p>
          <el-button plain style="width:100%" round @click="askAgent">向助手提问</el-button>
        </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { courseApi, questionApi, learnApi } from '@/api'
import { renderMd } from '../utils/markdown'
import { Right, Star, VideoPlay, EditPen, ChatDotRound } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const store = useUserStore()
const data = ref(null)
const favorited = ref(false)
const questionCount = ref(0)

const renderedContent = computed(() => renderMd(data.value?.knowledge?.content))

async function toggleFav() {
  const res = await learnApi.toggleFavorite(data.value.knowledge.id)
  favorited.value = res.data.favorited
  ElMessage.success(res.message)
}

function askAgent() {
  router.push({ path: '/agent', query: { q: '请讲解' + data.value.knowledge.name } })
}

onMounted(async () => {
  const res = await courseApi.knowledge(route.params.id)
  data.value = res.data
  if (res.data) {
    courseApi.viewKnowledge(res.data.knowledge.id)
    const st = await learnApi.favoriteStatus(res.data.knowledge.id)
    favorited.value = st.data.favorited
    const qs = await questionApi.byKnowledge(res.data.knowledge.id)
    questionCount.value = (qs.data || []).length
  }
})
</script>

<style scoped>
.k-main { padding: 24px; border-radius: var(--radius-lg); }
.k-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; flex-wrap: wrap; }
.k-head-left { position: relative; padding-left: 13px; min-width: 0; }
.k-head-left::before {
  content: ''; position: absolute; left: 0; top: 6px; bottom: 6px;
  width: 4px; border-radius: 3px; background: var(--grad-brand);
}
.k-chip {
  display: inline-block; font-size: 12px; font-weight: 600;
  color: var(--brand-deep); background: var(--brand-light);
  border-radius: 20px; padding: 3px 11px; margin-bottom: 8px;
}
.k-head h2 { margin: 0; font-size: 23px; letter-spacing: 0.3px; }
.k-head-actions { display: flex; gap: 9px; flex-shrink: 0; }
.btn-cta { box-shadow: 0 4px 14px rgba(59, 110, 246, 0.28); }
.btn-cta:hover { box-shadow: 0 7px 20px rgba(59, 110, 246, 0.36); }
.summary {
  color: var(--text-2); font-size: 13.5px; line-height: 1.85;
  margin: 14px 0 0; padding: 12px 15px;
  background: var(--soft-bg); border-radius: 10px; border-left: 3px solid var(--brand-3);
}
.markdown-body { font-size: 14px; }

.vis-list { display: flex; flex-direction: column; gap: 11px; }
.vis-card {
  display: flex; align-items: center; gap: 14px; padding: 13px;
  border: 1px solid var(--border); border-radius: var(--radius); cursor: pointer;
}
.vis-thumb {
  width: 46px; height: 46px; border-radius: 12px; flex-shrink: 0;
  background: var(--grad-brand); color: #fff;
  display: flex; align-items: center; justify-content: center; font-size: 21px;
  box-shadow: 0 4px 12px rgba(59, 110, 246, 0.28);
}
.vis-info { min-width: 0; }
.vis-title { font-weight: 600; font-size: 14px; }
.vis-desc { font-size: 12px; color: var(--text-2); margin-top: 3px; line-height: 1.6; }
.vis-arrow { margin-left: auto; color: var(--text-3); transition: transform 0.22s, color 0.22s; }
.vis-card:hover .vis-arrow { transform: translateX(4px); color: var(--brand); }

.side { padding: 18px; margin-bottom: 16px; border-radius: var(--radius-lg); }
.side p { line-height: 1.75; margin: 0 0 13px; }
.q-count { color: var(--brand); font-size: 15px; }
.side-practice { background: linear-gradient(160deg, var(--soft-bg) 0%, var(--card) 100%); }
.side-agent { background: linear-gradient(160deg, var(--success-light) 0%, var(--card) 100%); }

/* 右栏吸顶：左侧知识点正文往往很长（图文 + 公式），右侧只有两张卡。
   不吸顶的话滚到正文一半，右边就空一大片。
   74px = 顶栏 62px + 12px；align-self: flex-start 不可省 ——
   el-col 默认 stretch（元素被拉到与左列等高），没有可移动的余量，sticky 就完全不动。 */
.k-side-sticky {
  position: sticky; top: 74px;
  /* align-self: flex-start 必须写 —— el-row 是 align-items: stretch（默认），
     会把这个唯一子元素拉到与左列等高，元素高等于容器高就没有可移动余量，
     sticky 会完全不动（看起来像没生效）。 */
  align-self: flex-start;
  display: flex; flex-direction: column;
}
/* 单列布局下（lg 断点以下）右栏在正文下方，sticky 反而会挡住正文 */
@media (max-width: 992px) {
  .k-side-sticky { position: static; }
}
</style>
