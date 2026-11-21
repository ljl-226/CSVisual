<template>
  <div class="page">
    <div class="page-head">
      <h2>
        临时密码申请
        <el-tag v-if="pendingCount" type="danger" size="small" effect="light" round class="head-badge">
          {{ pendingCount }} 条待处理
        </el-tag>
      </h2>
      <div class="head-right">
        <!-- 管理员手上的线索通常是单一的：只知道单号，或者只记住一个电话 -->
        <el-input
          v-model="q" class="search-input" clearable
          placeholder="按单号 / 账号 / 姓名 / 电话搜索" :prefix-icon="Search"
          maxlength="50" @keyup.enter="doSearch" @clear="doSearch"
        />
        <el-select v-model="status" class="status-select" placeholder="全部状态" @change="doSearch">
          <el-option label="全部状态" value="" />
          <el-option label="待处理" value="pending" />
          <el-option label="已通过" value="approved" />
          <el-option label="已驳回" value="rejected" />
          <el-option label="已使用" value="used" />
        </el-select>
        <el-button @click="load">刷新</el-button>
      </div>
    </div>

    <!-- 顶部一段说明：第一次进来看见一堆工单，需要知道「为什么有这张表、我要做什么」 -->
    <div class="card tip-card">
      学生忘了姓名、自助找回走不通时会在这里提交申请。请你<b>按电话联系本人核身</b>后再点「通过」——
      通过后密码立即重置为随机临时密码，弹窗里展示一次供你转告，同时留在工单里等学生凭单号自取。
    </div>

    <div class="card">
      <el-table :data="list" size="small" border>
        <el-table-column prop="ticket" label="单号" width="120" />
        <el-table-column prop="username" label="账号" width="130" />
        <el-table-column prop="real_name" label="姓名" width="110" />
        <el-table-column label="联系电话" width="130">
          <template #default="{ row }">
            <a v-if="row.phone" :href="'tel:' + row.phone" class="phone">{{ row.phone }}</a>
            <span v-else class="muted">—</span>
          </template>
        </el-table-column>
        <el-table-column label="临时密码" width="140">
          <template #default="{ row }">
            <!-- 明文只在「已通过且未被使用」期间存在：学生用它登录成功即被销毁 -->
            <code v-if="row.temp_password" class="pwd">{{ row.temp_password }}</code>
            <span v-else-if="row.status === 'used'" class="muted small">学生已使用过</span>
            <span v-else class="muted">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="申请说明" min-width="160" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" effect="light" :type="statusType(row.status)">{{ STATUS_TEXT[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="提交时间" min-width="150" />
        <el-table-column label="处理情况" min-width="160">
          <template #default="{ row }">
            <div v-if="row.handled_at" class="handled">
              <span class="small">{{ String(row.handled_at).replace('T', ' ').slice(0, 16) }} · {{ row.admin_name || '管理员' }}</span>
              <span v-if="row.reject_reason" class="small danger">驳回理由：{{ row.reject_reason }}</span>
            </div>
            <span v-else class="muted small">未处理</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button text type="success" size="small" @click="onApprove(row)">通过</el-button>
              <el-button text type="danger" size="small" @click="onReject(row)">驳回</el-button>
            </template>
            <span v-else class="muted small">已处理</span>
          </template>
        </el-table-column>
      </el-table>
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

const STATUS_TEXT = { pending: '待处理', approved: '已通过', rejected: '已驳回', used: '已使用' }
const statusType = s => ({ pending: 'warning', approved: 'success', rejected: 'danger' }[s] || 'info')

const list = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const pendingCount = ref(0)
const q = ref('')
const status = ref('')

async function load() {
  const res = await adminApi.passwordRequests({
    page: page.value,
    pageSize: pageSize.value,
    q: q.value.trim() || undefined,
    status: status.value || undefined
  })
  list.value = res.data || []
  total.value = Number(res.total || (res.data || []).length)
  // 角标要的是「全部待处理」而不是「当前筛选下的待处理」：
  // 接口返回的 pendingCount 不参与条件过滤
  pendingCount.value = Number(res.pendingCount || 0)
  // 让侧栏角标同步：处理完一张单回到列表时，角标不该还挂着旧数字
  window.dispatchEvent(new Event('cv:pwd-req-refresh'))
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

async function copyPwd(text) {
  try {
    await navigator.clipboard.writeText(text)
  } catch (e) {
    /* 复制失败不影响展示，管理员还能手抄 */
  }
}

async function onApprove(row) {
  try {
    await ElMessageBox.confirm(
      `确认已核实「${row.real_name || row.username}」（${row.username}）是本人？\n` +
        '通过后 TA 的原密码立即失效，你会拿到一个随机临时密码。',
      '通过申请',
      { type: 'warning', confirmButtonText: '确认通过', cancelButtonText: '取消' }
    )
  } catch (e) {
    return
  }
  try {
    const res = await adminApi.approvePasswordRequest(row.id)
    if (res.code !== 200) {
      ElMessage.error(res.message || '操作失败，请稍后重试')
      return
    }
    const pwd = (res.data || {}).password
    await copyPwd(pwd)  // 八位随机字符手抄容易错，先替管理员放进剪贴板
    // 明文不留犊不展示第二次：关掉这个框就只能让学生凭单号自取
    await ElMessageBox.alert(
      `新密码：${pwd}\n单号：${row.ticket}\n\n` +
        '密码已尝试复制到剪贴板。它同时留在工单里，学生凭单号也能自己取走；' +
        '学生用它登录成功后，这份明文会立即销毁。',
      '已通过，请告知学生',
      { confirmButtonText: '我已记下', type: 'success' }
    )
    ElMessage.success('已通过并重置密码')
    load()
  } catch (e) {
    ElMessage.error('操作失败，请稍后重试')
  }
}

async function onReject(row) {
  let reason = ''
  try {
    const res = await ElMessageBox.prompt(
      `请说明为什么驳回「${row.real_name || row.username}」的申请，学生会看到这段话。`,
      '驳回申请',
      {
        inputType: 'textarea',
        inputPlaceholder: '例如：电话未能接通，无法确认本人',
        inputValidator: v => {
          const s = String(v || '').trim()
          if (!s) return '请填写驳回理由'
          if (s.length > 200) return '驳回理由请控制在 200 字以内'
          return true
        },
        type: 'warning',
        confirmButtonText: '驳回',
        cancelButtonText: '取消'
      }
    )
    reason = String((res.value || '')).trim()
  } catch (e) {
    return
  }
  try {
    const res = await adminApi.rejectPasswordRequest(row.id, { reason })
    if (res.code !== 200) {
      ElMessage.error(res.message || '操作失败，请稍后重试')
      return
    }
    ElMessage.success('已驳回')
    load()
  } catch (e) {
    ElMessage.error('操作失败，请稍后重试')
  }
}

onMounted(load)
</script>

<style scoped>
.page-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; gap: 12px; flex-wrap: wrap; }
.page-head h2 { margin: 0; font-size: 20px; display: flex; align-items: center; gap: 8px; }
.head-right { display: flex; align-items: center; gap: 10px; }
.search-input { width: 250px; }
.status-select { width: 130px; }
/* 说明卡：一块很轻的底色 + 一行字，比把它塞进表格空状态更容易被读完 */
.tip-card { padding: 12px 14px; font-size: 13px; line-height: 1.9; color: var(--text-2); margin-bottom: 14px; }
.tip-card b { color: var(--text); }
.phone { color: var(--brand); text-decoration: none; }
.phone:hover { text-decoration: underline; }
.pwd {
  font-family: ui-monospace, Menlo, Consolas, monospace;
  font-size: 13px; font-weight: 600; letter-spacing: 0.5px;
  color: var(--el-color-success);
}
.handled { display: flex; flex-direction: column; gap: 2px; }
.danger { color: var(--el-color-danger); }
</style>
