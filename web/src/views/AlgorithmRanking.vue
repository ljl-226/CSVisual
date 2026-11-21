<template>
  <div class="page">
    <div class="head card">
      <div>
        <h2 class="page-title">算法排行榜</h2>
        <p class="small muted">总分 = 已通过题目的权值之和，难度越高的题权值越大（入门 5 / 困难 30 上下）。</p>
      </div>
      <el-button plain @click="$router.push('/algorithm')">
        <el-icon><Back /></el-icon> 返回题目列表
      </el-button>
    </div>

    <div class="card block" v-loading="loading">
      <div v-if="me" class="me-card">
        <div class="me-rank">
          <div class="me-num">{{ me.rank }}</div>
          <div class="small muted">我的排名</div>
        </div>
        <div class="me-item">
          <div class="me-val">{{ me.totalScore }}</div>
          <div class="small muted">我的总分</div>
        </div>
        <div class="me-item">
          <div class="me-val">{{ me.solvedCount }}</div>
          <div class="small muted">通过题数</div>
        </div>
        <div class="me-item">
          <div class="me-val">{{ me.totalWeight || me.totalScore }}</div>
          <div class="small muted">累计权值</div>
        </div>
        <el-button type="primary" plain style="margin-left:auto" @click="$router.push('/algorithm')">继续刷题</el-button>
      </div>

      <el-table v-if="list.length" :data="list" size="small" stripe :row-class-name="rowClass">
        <el-table-column label="排名" width="90" align="center">
          <template #default="{ row }">
            <span v-if="row.rank <= 3" class="medal" :class="'m' + row.rank">{{ row.rank }}</span>
            <span v-else class="rank-num">{{ row.rank }}</span>
          </template>
        </el-table-column>
        <el-table-column label="用户" min-width="160">
          <template #default="{ row }">
            <span>{{ row.realName || row.username }}</span>
            <el-tag v-if="isMe(row)" size="small" type="primary" effect="light" style="margin-left:6px">我</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="总分（权值累计）" width="150" align="center">
          <template #default="{ row }"><b class="score">{{ row.totalScore }}</b></template>
        </el-table-column>
        <el-table-column prop="solvedCount" label="通过题数" width="100" align="center" />
        <el-table-column prop="totalWeight" label="总权值" width="100" align="center" />
      </el-table>

      <el-empty v-else-if="!loading" description="还没有人提交通过，快去拿下首杀">
        <el-button type="primary" @click="$router.push('/algorithm')">去刷题</el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { algorithmApi } from '@/api'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { Back } from '@element-plus/icons-vue'

const store = useUserStore()
const list = ref([])
const me = ref(null)
const loading = ref(false)

function isMe(row) {
  const u = store.userInfo || {}
  const uid = u.id || u.userId
  if (uid && row.userId === uid) return true
  return !!u.username && row.username === u.username
}

function rowClass({ row }) {
  return isMe(row) ? 'me-row' : ''
}

async function load() {
  loading.value = true
  try {
    const res = await algorithmApi.ranking({ size: 50 })
    if (res.code === 200 && res.data) {
      list.value = res.data.list || []
      me.value = res.data.me || null
    } else {
      ElMessage.error(res.message || '排行榜加载失败')
    }
  } catch (e) {
    ElMessage.error('排行榜加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.head { display: flex; justify-content: space-between; align-items: center; gap: 16px; padding: 18px 20px; margin-bottom: 14px; }
.page-title { margin: 0 0 4px; font-size: 20px; }
.head p { margin: 0; }
.block { padding: 18px; }

/* flex-wrap：四项（排名/总分/通过/权值 + 按钮）在折叠屏外屏排不开，
   不换行会把「继续刷题」顶出视口 */
.me-card {
  display: flex; align-items: center; gap: 28px; margin-bottom: 16px; flex-wrap: wrap;
  background: var(--brand-light); border: 1px solid #cddcff; border-radius: 12px; padding: 14px 18px;
}
.me-num { font-size: 26px; font-weight: 700; color: var(--brand); line-height: 1.1; }
.me-val { font-size: 20px; font-weight: 700; color: var(--text); line-height: 1.2; }
.me-item { text-align: center; }

:deep(.me-row) { background: var(--brand-light); }
:deep(.me-row:hover) > td { background: var(--brand-light) !important; }

.medal {
  display: inline-block; width: 24px; height: 24px; line-height: 24px; border-radius: 50%;
  color: #fff; font-size: 12px; font-weight: 700;
}
.m1 { background: linear-gradient(135deg, #f5c451, #e8a13a); }
.m2 { background: linear-gradient(135deg, #c9d2dd, #9aa7b8); }
.m3 { background: linear-gradient(135deg, #d9a273, #bd7b46); }
.rank-num { color: var(--text-2); font-size: 13px; }
.score { color: var(--brand); font-size: 14px; }

@media (max-width: 768px) {
  .head { padding: 14px 14px; gap: 10px; flex-wrap: wrap; }
  .page-title { font-size: 18px; }
  .block { padding: 14px; }
  .me-card { gap: 16px; padding: 12px 14px; }
}
@media (max-width: 480px) {
  .me-card { gap: 12px; justify-content: space-between; }
  .me-num { font-size: 22px; }
  .me-val { font-size: 17px; }
  .me-card .el-button { margin-left: 0 !important; width: 100%; }
}
</style>
