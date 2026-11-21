<template>
  <div class="page">
    <div class="page-head">
      <h2>用户管理</h2>
      <div class="head-right">
        <!-- 用户 500+ 后翻页找人已不现实：按账号或姓名模糊搜，走后端（分页结果才准确） -->
        <el-input
          v-model="q" class="search-input" clearable
          placeholder="按账号或姓名搜索" :prefix-icon="Search"
          maxlength="50" @keyup.enter="doSearch" @clear="doSearch"
        />
        <el-button type="primary" plain @click="doSearch">搜索</el-button>
        <el-button @click="load">刷新</el-button>
      </div>
    </div>
    <div class="card">
      <el-table :data="list" size="small" border>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="账号" width="140" />
        <el-table-column prop="real_name" label="姓名" width="120" />
        <el-table-column label="角色" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="row.role === 'admin' ? 'warning' : 'info'" effect="light">
              {{ row.role === 'admin' ? '管理员' : '学生' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="answer_count" label="答题数" width="100" />
        <el-table-column prop="wrong_count" label="错题数" width="100" />
        <el-table-column prop="created_at" label="注册时间" min-width="180" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <!-- 学生忘了姓名、自助找回走不通时的兜底：管理员重置成随机临时密码 -->
            <el-button text type="warning" size="small" @click="onResetPwd(row)">重置密码</el-button>
          </template>
        </el-table-column>
      </el-table>
      <!-- 用户数随注册增长（当前 500+），全量塞表已经明显变慢，走后端真分页 -->
      <PaginationBar :total="total" v-model:page="page" v-model:pageSize="pageSize" @change="load" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import PaginationBar from '@/components/PaginationBar.vue'

const list = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const q = ref('')

async function load() {
  const res = await adminApi.users({ page: page.value, pageSize: pageSize.value, q: q.value.trim() || undefined })
  list.value = res.data || []
  total.value = Number(res.total || (res.data || []).length)
  const maxPage = Math.max(1, Math.ceil(total.value / pageSize.value))
  if (page.value > maxPage) {
    page.value = maxPage
    return load()
  }
}

function doSearch() {
  page.value = 1
  load()
}

async function onResetPwd(row) {
  try {
    await ElMessageBox.confirm(
      `将把用户「${row.real_name || row.username}」（${row.username}）的密码重置为随机临时密码，原密码立即失效。确定继续吗？`,
      '重置密码',
      { type: 'warning', confirmButtonText: '重置', cancelButtonText: '取消' }
    )
  } catch (e) {
    return
  }
  try {
    const res = await adminApi.resetUserPassword(row.id)
    if (res.code !== 200) {
      ElMessage.error(res.message || '重置失败，请稍后重试')
      return
    }
    // 新密码只此一次展示：明文不落库不存日志，关闭后只能再次重置
    await ElMessageBox.alert(
      `新密码：${res.data.password}`,
      '已重置，请告知学生',
      { confirmButtonText: '我已记下', type: 'success' }
    )
  } catch (e) {
    ElMessage.error('重置失败，请稍后重试')
  }
}

onMounted(load)
</script>

<style scoped>
.page-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; gap: 12px; flex-wrap: wrap; }
.page-head h2 { margin: 0; font-size: 20px; }
.head-right { display: flex; align-items: center; gap: 10px; }
.search-input { width: 240px; }
</style>
