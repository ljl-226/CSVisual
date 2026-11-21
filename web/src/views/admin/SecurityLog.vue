<template>
  <div class="page">
    <div class="page-head">
      <h2>安全日志</h2>
      <el-button @click="load">刷新</el-button>
    </div>

    <div class="card">
      <!-- 筛选：日期 / 事件类型（下拉项来自接口回传的 dates / events，不写死） -->
      <div class="filters">
        <el-select v-model="filterDate" clearable placeholder="全部日期" style="width:150px" @change="onFilter">
          <el-option v-for="d in dates" :key="d" :value="d" :label="d" />
        </el-select>
        <el-select v-model="filterEvent" clearable placeholder="全部事件" style="width:180px" @change="onFilter">
          <el-option v-for="e in events" :key="e" :value="e" :label="eventLabel(e)" />
        </el-select>
        <el-button @click="resetFilter">重置</el-button>
        <span class="small muted">记录登录成功/失败、锁定、改密、注册等安全事件，按天落盘</span>
      </div>

      <el-table :data="list" size="small" border v-loading="loading">
        <el-table-column label="时间" width="165">
          <template #default="{ row }">{{ fmtTime(row.time) }}</template>
        </el-table-column>
        <el-table-column label="事件" width="150">
          <template #default="{ row }">
            <el-tag size="small" :type="tagType(row.event)" effect="light">{{ eventLabel(row.event) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="账号" width="140">
          <template #default="{ row }">{{ row.username || '-' }}</template>
        </el-table-column>
        <el-table-column label="用户ID" width="80" align="center">
          <template #default="{ row }">{{ row.id ?? '-' }}</template>
        </el-table-column>
        <el-table-column label="IP" width="130">
          <template #default="{ row }">{{ row.ip || '-' }}</template>
        </el-table-column>
        <el-table-column label="详情" min-width="200">
          <template #default="{ row }">
            <span class="small detail">{{ detailOf(row) || '-' }}</span>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && !list.length" description="暂无安全日志" :image-size="60" />

      <PaginationBar :total="total" v-model:page="page" v-model:pageSize="pageSize" @change="load" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api'
import { ElMessage } from 'element-plus'
import PaginationBar from '@/components/PaginationBar.vue'

const list = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dates = ref([])
const events = ref([])
const filterDate = ref('')
const filterEvent = ref('')
const loading = ref(false)

// 与双端 audit 事件名一一对应；出现未映射的新事件时兜底显示原始名
const EVENT_LABELS = {
  login_ok: '登录成功',
  login_fail: '登录失败',
  login_blocked: '失败过多被锁定',
  logout: '退出登录',
  register: '注册账号',
  change_password: '修改密码',
  forgot_reset: '找回密码重置',
  forgot_hint: '查询姓名提示',
  avatar_update: '更新头像',
  avatar_reset: '恢复默认头像',
  admin_reset_pwd: '管理员重置密码',
  temp_pwd_apply: '申请临时密码',
  temp_pwd_approve: '发放临时密码',
  temp_pwd_reject: '驳回临时密码申请'
}
const eventLabel = e => EVENT_LABELS[e] || e
const tagType = e => (e === 'login_fail' || e === 'login_blocked' ? 'danger'
  : e === 'login_ok' || e === 'register' ? 'success' : 'info')

function fmtTime(t) {
  return String(t || '').replace('T', ' ')
}

// 详情列：把 time/event/username/id/ip 之外的附加字段拼成 k=v（如 locked=15、exists=True）
const SKIP_KEYS = ['time', 'event', 'username', 'id', 'ip']
function detailOf(row) {
  return Object.entries(row || {})
    .filter(([k]) => !SKIP_KEYS.includes(k))
    .map(([k, v]) => `${k}=${v}`)
    .join('；')
}

async function load() {
  loading.value = true
  try {
    const res = await adminApi.securityLogs({
      date: filterDate.value || undefined,
      event: filterEvent.value || undefined,
      page: page.value,
      pageSize: pageSize.value
    })
    list.value = res.data || []
    total.value = Number(res.total || list.value.length)
    dates.value = res.dates || []
    events.value = res.events || []
    // 筛选后页码可能超出总页数：回退最后一页再拉一次
    const maxPage = Math.max(1, Math.ceil(total.value / pageSize.value))
    if (page.value > maxPage) {
      page.value = maxPage
      return load()
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '日志加载失败')
  } finally {
    loading.value = false
  }
}
function onFilter() {
  // 换筛选条件一律回第 1 页
  page.value = 1
  load()
}
function resetFilter() {
  filterDate.value = ''
  filterEvent.value = ''
  onFilter()
}
onMounted(load)
</script>

<style scoped>
.page-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-head h2 { margin: 0; font-size: 20px; }
.filters { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; flex-wrap: wrap; }
.detail { color: var(--text-2); word-break: break-all; }
</style>
