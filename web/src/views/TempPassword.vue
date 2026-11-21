<template>
  <AuthShell title="申请临时密码" sub="姓名也想不起来时，交给管理员核实身份后发放临时密码">
    <el-tabs v-model="tab" class="tp-tabs">
      <!-- ===== 第一步：提交申请 ===== -->
      <el-tab-pane label="提交申请" name="apply">
        <el-form :model="form" :rules="rules" ref="formRef" size="large">
          <el-form-item prop="username">
            <el-input v-model="form.username" placeholder="请输入你的登录账号" :prefix-icon="User" maxlength="20" />
          </el-form-item>
          <el-form-item prop="phone">
            <el-input v-model="form.phone" placeholder="11 位手机号，管理员会打这个电话跟你核对身份"
                      :prefix-icon="Phone" maxlength="20"
                      @input="form.phone = filterPhoneInput($event)" @blur="tidyPhone" />
          </el-form-item>
          <el-form-item prop="reason">
            <el-input v-model="form.reason" type="textarea" :rows="2" resize="none" maxlength="200"
                      show-word-limit placeholder="选填：例如注册时填的姓名记不清了" />
          </el-form-item>
          <el-button type="primary" class="submit" :loading="loading" @click="onApply">提交申请</el-button>
        </el-form>

        <!-- 提交成功后把单号摆在最显眼的位置：它是取临时密码的唯一凭证 -->
        <div v-if="applyResult" class="ticket-card">
          <div class="tc-label">申请已受理，请记下你的申请单号</div>
          <div class="tc-ticket">{{ applyResult.ticket }}</div>
          <p class="tc-tip">
            管理员会按你留的电话联系核实，通过后在这页切换到「查询进度」，
            用 <b>单号 + 账号</b> 就能把临时密码取回来。
          </p>
        </div>
      </el-tab-pane>

      <!-- ===== 第二步：凭单号取件 ===== -->
      <el-tab-pane label="查询进度" name="status">
        <el-form :model="query" ref="queryRef" size="large">
          <el-form-item prop="ticket">
            <el-input v-model="query.ticket" placeholder="形如 TP-XXXXXX" maxlength="20" :prefix-icon="Ticket" />
          </el-form-item>
          <el-form-item prop="username">
            <el-input v-model="query.username" placeholder="提交申请时填的账号" maxlength="20" :prefix-icon="User" />
          </el-form-item>
          <el-button type="primary" class="submit" :loading="queryLoading" @click="onQuery">查询</el-button>
        </el-form>

        <div v-if="queryResult" class="result-card" :class="queryResult.status">
          <div class="rc-head">
            <span class="rc-status">{{ queryResult.statusText }}</span>
            <span class="rc-time muted small">{{ fmtTime(queryResult.createdAt) }} 提交</span>
          </div>

          <!-- 通过了：把临时密码摆出来，复制按钮比让用户手抄八位字符可靠 -->
          <template v-if="queryResult.status === 'approved' && queryResult.password">
            <div class="rc-pwd-row">
              <code class="rc-pwd">{{ queryResult.password }}</code>
              <el-button size="small" type="primary" plain @click="copy(queryResult.password)">复制</el-button>
            </div>
            <p class="rc-tip">这是你的临时密码，登录后请在「个人中心」立即改成自己记得住的密码。</p>
            <el-button class="rc-login" type="success" plain size="small" @click="gotoLogin">拿着它去登录</el-button>
          </template>

          <!-- used：学生已经用它登录过，明文随之销毁 —— 再想要一份得重新申请 -->
          <p v-else-if="queryResult.status === 'used'" class="rc-tip">
            这份临时密码你已经用过了，出于安全它已从服务器删除。又忘了密码？去「提交申请」重新提一次。
          </p>
          <p v-else-if="queryResult.status === 'approved'" class="rc-tip">
            已通过，但密码已不可用 —— 请在「提交申请」里重新提一次。
          </p>
          <p v-else-if="queryResult.status === 'rejected'" class="rc-tip">
            管理员没能核实你的身份：{{ queryResult.rejectReason || '未说明理由' }}。
            确认信息后可以在「提交申请」里再提一次。
          </p>
          <p v-else class="rc-tip">{{ queryResult.statusText }} —— 管理员核实后会按你留的电话联系你。</p>
        </div>
      </el-tab-pane>
    </el-tabs>

    <div class="bottom">
      <router-link to="/login">返回登录</router-link>
      <span>
        <span>想起来了？</span>
        <router-link to="/forgot">用姓名自助找回</router-link>
      </span>
    </div>
  </AuthShell>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import AuthShell from '@/components/AuthShell.vue'
import { authApi } from '@/api'
import { ElMessage } from 'element-plus'
import { User, Phone, Ticket } from '@element-plus/icons-vue'
import { isValidPhone, normalizePhone, filterPhoneInput } from '@/utils/phone'

const router = useRouter()
const tab = ref('apply')
const formRef = ref()
const queryRef = ref()
const loading = ref(false)
const queryLoading = ref(false)
const applyResult = ref(null)
const queryResult = ref(null)

const form = reactive({ username: '', phone: '', reason: '' })
const query = reactive({ ticket: '', username: '' })

/**
 * 规则与后端 /auth/temp-password/apply 对齐：账号字符集、电话 6-15 位数字。
 * 电话放宽到允许 +86、区号与连字符 —— 卡住填不进去，管理员就联系不上人。
 */
const rules = {
  username: [
    { required: true, message: '请输入登录账号', trigger: 'blur' },
    { pattern: /^[A-Za-z0-9_]{3,20}$/, message: '账号需为 3-20 位字母、数字或下划线', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    {
      validator: (r, v, cb) => {
        // 与后端 auth 路由同一套规则：11 位手机号，允许 +86/分隔符，其余一律拦下
        if (!isValidPhone(v)) cb(new Error('请填写正确的 11 位手机号，例如 13812345678'))
        else cb()
      },
      trigger: 'blur'
    }
  ]
}

// 失焦时把「+86 138-0013-8000」整理成「13800138000」：
// 用户看得清白自己留的是哪个号，管理员也不用手抄带符号的版本
function tidyPhone() {
  if (isValidPhone(form.phone)) form.phone = normalizePhone(form.phone)
}

async function onApply() {
  await formRef.value.validate(async valid => {
    if (!valid) return
    loading.value = true
    try {
      const res = await authApi.applyTempPassword({
        username: form.username.trim(),
        phone: form.phone.trim(),
        reason: form.reason.trim()
      })
      if (res.code !== 200) {
        ElMessage.error(res.message || '提交失败，请稍后重试')
        return
      }
      applyResult.value = res.data
      ElMessage.success(res.message || '申请已提交')
      // 提交完顺手把账号带到查询表单里：查进度时少填一项
      query.username = form.username.trim()
    } catch (e) {
      ElMessage.error('无法连接服务器，请确认后端已启动')
    } finally {
      loading.value = false
    }
  })
}

async function onQuery() {
  const tk = query.ticket.trim().toUpperCase()
  const uname = query.username.trim()
  if (!tk || !uname) {
    ElMessage.warning('请填写申请单号和账号')
    return
  }
  queryLoading.value = true
  try {
    // ticket 大写、大小写都能查：单号要手抄，强求大写等于给查询加一道无谓的门槛
    const res = await authApi.tempPasswordStatus({ ticket: tk, username: uname })
    if (res.code !== 200) {
      queryResult.value = null
      ElMessage.error(res.message || '查询失败，请稍后重试')
      return
    }
    queryResult.value = res.data
  } catch (e) {
    ElMessage.error('无法连接服务器，请确认后端已启动')
  } finally {
    queryLoading.value = false
  }
}

async function copy(text) {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('临时密码已复制到剪贴板')
  } catch (e) {
    ElMessage.warning('浏览器拒绝了复制，请手动选中上面的密码复制')
  }
}

function gotoLogin() {
  // 带上账号与密码：登录页会填好，用户不用再手抄一遍八位随机字符
  sessionStorage.setItem('cv_login_hint', JSON.stringify({
    username: query.username.trim(),
    password: (queryResult.value || {}).password || ''
  }))
  router.push('/login')
}

function fmtTime(t) {
  return String(t || '').replace('T', ' ').slice(0, 16)
}
</script>

<style scoped>
/* 标签页头部的默认留白偏松，收一号让整体更紧凑 */
.tp-tabs :deep(.el-tabs__header) { margin-bottom: 12px; }
.tp-tabs :deep(.el-tabs__item) { font-size: 14px; height: 38px; }
/* 单号是全页最重要的一行：加框 + 等宽 + 放大，扫一眼就能记住 */
.ticket-card {
  margin-top: 14px; padding: 14px 16px; border-radius: 10px;
  border: 1px solid var(--brand-3); background: var(--brand-light);
}
.tc-label { font-size: 12.5px; color: var(--text-2); }
.tc-ticket {
  margin: 6px 0 8px; font-size: 24px; font-weight: 700; letter-spacing: 2px;
  font-family: ui-monospace, Menlo, Consolas, monospace; color: var(--brand); word-break: break-all;
}
.tc-tip { margin: 0; font-size: 12.5px; line-height: 1.8; color: var(--text-2); }

.result-card {
  margin-top: 14px; padding: 14px 16px; border-radius: 10px;
  border: 1px solid var(--border); background: var(--bg);
}
.result-card.approved { border-color: var(--el-color-success-light-3); }
.result-card.rejected { border-color: var(--el-color-danger-light-3); }
.rc-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.rc-status { font-size: 14px; font-weight: 600; }
.rc-time { font-size: 12px; }
.rc-pwd-row { display: flex; align-items: center; gap: 10px; margin: 10px 0 6px; }
.rc-pwd {
  flex: 1; min-width: 0; padding: 8px 10px; border-radius: 8px; word-break: break-all;
  font-size: 18px; font-weight: 700; letter-spacing: 1px; color: var(--el-color-success);
  font-family: ui-monospace, Menlo, Consolas, monospace; background: var(--card); border: 1px dashed var(--border);
}
.rc-tip { margin: 6px 0 0; font-size: 12.5px; line-height: 1.8; color: var(--text-2); }
.rc-login { margin-top: 10px; }
.bottom > span { margin-left: 10px; white-space: nowrap; }
</style>
