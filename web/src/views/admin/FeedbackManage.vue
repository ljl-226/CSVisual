<template>
  <div class="page">
    <div class="page-head">
      <h2>反馈建议</h2>
      <el-button @click="load">刷新</el-button>
    </div>

    <!-- 状态概览：一眼看到还有多少条没处理，不必逐个切筛选去数 -->
    <div class="stat-row">
      <div v-for="s in statusCards" :key="s.value" class="stat-card" :class="{ 'is-on': filterStatus === s.value }"
           @click="pickStatus(s.value)">
        <div class="stat-num">{{ statusCount[s.value] || 0 }}</div>
        <div class="stat-label">{{ s.label }}</div>
      </div>
    </div>

    <div class="card">
      <div class="filters">
        <el-select v-model="filterStatus" clearable placeholder="全部状态" style="width:130px" @change="onFilter">
          <el-option v-for="s in statusList" :key="s" :value="s" :label="statusLabel(s)" />
        </el-select>
        <el-select v-model="filterType" clearable placeholder="全部类型" style="width:130px" @change="onFilter">
          <el-option v-for="t in typeList" :key="t" :value="t" :label="typeLabel(t)" />
        </el-select>
        <el-input v-model="filterKeyword" clearable placeholder="搜内容 / 账号" style="width:200px"
                  @keyup.enter="onFilter" @clear="onFilter" />
        <el-button @click="onFilter">查询</el-button>
        <el-button @click="resetFilter">重置</el-button>
      </div>

      <el-table :data="list" size="small" border v-loading="loading">
        <el-table-column label="ID" width="60" align="center">
          <template #default="{ row }">{{ row.id }}</template>
        </el-table-column>
        <el-table-column label="提交人" width="120">
          <template #default="{ row }">
            <div class="who">
              <span>{{ row.username || '-' }}</span>
              <span class="small muted">#{{ row.user_id }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="96">
          <template #default="{ row }">
            <el-tag size="small" :type="typeTag(row.type)" effect="light">{{ typeLabel(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="内容" min-width="220">
          <template #default="{ row }">
            <div class="content-cell">{{ row.content }}</div>
            <div class="small muted">
              {{ row.page ? '页面：' + row.page : '未记录页面' }}
              <template v-if="row.contact"> · 联系方式：{{ row.contact }}</template>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="管理员回复" min-width="180">
          <template #default="{ row }">
            <div v-if="row.admin_reply" class="reply-cell">{{ row.admin_reply }}</div>
            <span v-else class="small muted">—</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="statusTag(row.status)" effect="light">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="时间" width="150">
          <template #default="{ row }">{{ fmtTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="openReply(row)">处理</el-button>
            <el-button size="small" type="danger" link @click="onDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && !list.length" description="暂无反馈" :image-size="60" />

      <PaginationBar :total="total" v-model:page="page" v-model:pageSize="pageSize"
                     :sizes="[10, 20, 50, 100]" @change="load" />
    </div>

    <!-- 处理弹窗：改状态 + 写回复，一次提交 -->
    <el-dialog v-model="replyVisible" title="处理反馈" width="560px">
      <div v-if="current" class="reply-head">
        <div class="reply-meta small muted">
          #{{ current.id }} · {{ current.username || '匿名' }} · {{ typeLabel(current.type) }}
          · {{ fmtTime(current.created_at) }}
        </div>
        <div class="reply-content">{{ current.content }}</div>
        <div v-if="current.page" class="small muted">页面：{{ current.page }}</div>
      </div>

      <el-form label-width="76px" class="reply-form">
        <el-form-item label="状态">
          <el-select v-model="replyForm.status" style="width:180px">
            <el-option v-for="s in statusList" :key="s" :value="s" :label="statusLabel(s)" />
          </el-select>
        </el-form-item>
        <el-form-item label="回复">
          <el-input v-model="replyForm.adminReply" type="textarea" :rows="4" maxlength="1000" show-word-limit
                    placeholder="写给用户看的回复（留空表示只改状态）" resize="none" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="replyVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveReply">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { adminApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import PaginationBar from '@/components/PaginationBar.vue'

// 与后端 utils/feedback.js（Node）与 routers/feedback.py（Python）里的白名单一一对应；
// 接口也会回传 statusList / typeList，这里只为「接口还没回来时」先渲染出筛选项。
const STATUS_LABELS = {
  pending: '待处理', processing: '处理中', resolved: '已解决', closed: '已关闭'
}
const TYPE_LABELS = {
  bug: '功能异常', feature: '功能建议', experience: '体验问题', other: '其他'
}
const statusLabel = s => STATUS_LABELS[s] || s
const typeLabel = t => TYPE_LABELS[t] || t
const statusTag = s => (s === 'pending' ? 'warning' : s === 'processing' ? 'primary'
  : s === 'resolved' ? 'success' : 'info')
const typeTag = t => (t === 'bug' ? 'danger' : t === 'feature' ? 'success'
  : t === 'experience' ? 'warning' : 'info')

const statusCards = computed(() =>
  (statusList.value.length ? statusList.value : Object.keys(STATUS_LABELS)).map(v => ({
    value: v, label: STATUS_LABELS[v] || v
  }))
)

const list = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const loading = ref(false)
const statusCount = ref({})
const statusList = ref([])
const typeList = ref([])
const filterStatus = ref('')
const filterType = ref('')
const filterKeyword = ref('')

function fmtTime(t) {
  return String(t || '').replace('T', ' ').slice(0, 19)
}

async function load() {
  loading.value = true
  try {
    const res = await adminApi.feedback({
      status: filterStatus.value || undefined,
      type: filterType.value || undefined,
      keyword: filterKeyword.value || undefined,
      page: page.value,
      pageSize: pageSize.value
    })
    list.value = res.data || []
    total.value = Number(res.total || list.value.length)
    // 筛选项与计数由接口回传，不在前端写死 —— 加一种状态只改后端
    if (res.statusCount) statusCount.value = res.statusCount
    if (res.statusList) statusList.value = res.statusList
    if (res.typeList) typeList.value = res.typeList
    const maxPage = Math.max(1, Math.ceil(total.value / pageSize.value))
    if (page.value > maxPage) {
      page.value = maxPage
      return load()
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '反馈加载失败')
  } finally {
    loading.value = false
  }
}

function onFilter() {
  page.value = 1
  load()
}
function resetFilter() {
  filterStatus.value = ''
  filterType.value = ''
  filterKeyword.value = ''
  onFilter()
}
// 点概览卡片直接切到该状态；再点一次取消筛选 —— 比下拉两步操作快
function pickStatus(v) {
  filterStatus.value = filterStatus.value === v ? '' : v
  onFilter()
}

/* ---------- 处理 ---------- */
const replyVisible = ref(false)
const saving = ref(false)
const current = ref(null)
const replyForm = ref({ status: 'pending', adminReply: '' })

function openReply(row) {
  current.value = row
  replyForm.value = { status: row.status || 'pending', adminReply: row.admin_reply || '' }
  replyVisible.value = true
}

async function saveReply() {
  if (!current.value) return
  saving.value = true
  try {
    await adminApi.updateFeedback(current.value.id, {
      status: replyForm.value.status,
      adminReply: replyForm.value.adminReply
    })
    ElMessage.success('已保存')
    replyVisible.value = false
    load()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除 #${row.id} 这条反馈？删除后不可恢复。`, '删除反馈', {
      type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消'
    })
  } catch (e) {
    return
  }
  try {
    await adminApi.deleteFeedback(row.id)
    ElMessage.success('已删除')
    load()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '删除失败')
  }
}

onMounted(load)
</script>

<style scoped>
.page-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-head h2 { margin: 0; font-size: 20px; }

.stat-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); gap: 12px; margin-bottom: 16px; }
.stat-card {
  background: var(--card); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 12px 14px; cursor: pointer; transition: all 0.2s;
}
.stat-card:hover { border-color: var(--brand-3); transform: translateY(-2px); }
.stat-card.is-on { border-color: var(--brand); background: var(--brand-light); }
.stat-num { font-size: 22px; font-weight: 700; color: var(--brand); line-height: 1.2; }
.stat-label { font-size: 12px; color: var(--text-3); margin-top: 2px; }

.filters { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; flex-wrap: wrap; }
.who { display: flex; flex-direction: column; line-height: 1.35; }
.content-cell { white-space: pre-wrap; word-break: break-word; line-height: 1.6; }
.reply-cell { white-space: pre-wrap; word-break: break-word; color: var(--text-2); line-height: 1.6; }

.reply-head {
  background: var(--soft-bg); border-radius: var(--radius);
  padding: 10px 12px; margin-bottom: 14px;
}
.reply-meta { margin-bottom: 6px; }
.reply-content { white-space: pre-wrap; word-break: break-word; line-height: 1.7; }
.reply-form :deep(.el-form-item:last-child) { margin-bottom: 0; }
</style>
