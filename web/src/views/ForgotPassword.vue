<template>
  <AuthShell title="找回密码" sub="用注册时填写的姓名验证身份，验证通过即可直接设置新密码">
    <el-form :model="form" :rules="rules" ref="formRef" size="large" @submit.prevent>
      <el-form-item prop="username">
        <el-input v-model="form.username" placeholder="请输入登录账号" :prefix-icon="User" maxlength="20" />
      </el-form-item>
      <el-form-item prop="realName">
        <el-input v-model="form.realName" placeholder="请输入注册时填写的姓名" :prefix-icon="UserFilled" maxlength="20" />
        <!-- 姓名是自助找回的唯一凭证，忘了就死锁 —— 给个脱敏提示帮回忆 -->
        <div class="hint-row">
          <button type="button" class="hint-link" :disabled="hintLoading || !form.username" @click="onHint">
            {{ hintLoading ? '查询中…' : '不记得姓名？' }}
          </button>
          <span v-if="hintText" class="hint-text">{{ hintText }}</span>
        </div>
      </el-form-item>
      <el-form-item prop="newPassword">
        <el-input v-model="form.newPassword" type="password" placeholder="请输入新密码（6-64 位）" :prefix-icon="Lock" show-password maxlength="64" />
      </el-form-item>
      <el-form-item prop="confirm">
        <el-input v-model="form.confirm" type="password" placeholder="请再次输入新密码" :prefix-icon="Lock" show-password maxlength="64" @keyup.enter="onReset" />
      </el-form-item>
      <el-button type="primary" class="submit" :loading="loading" @click="onReset">确认重置</el-button>
    </el-form>
    <div class="bottom split">
      <router-link to="/login">返回登录</router-link>
      <span>
        <span>还没有账号？</span>
        <router-link to="/register">立即注册</router-link>
      </span>
    </div>
    <!-- 姓名是自助找回的唯一凭证，连它也想不起来时，这条路已经走到头了 -->
    <div class="side-entry">
      <span class="small muted">提示也想不起来？</span>
      <router-link to="/temp-password">申请临时密码</router-link>
    </div>
  </AuthShell>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AuthShell from '@/components/AuthShell.vue'
import { authApi } from '@/api'
import { ElMessage } from 'element-plus'
import { User, UserFilled, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const form = reactive({ username: '', realName: '', newPassword: '', confirm: '' })
const hintLoading = ref(false)
const hintText = ref('')
// 规则与后端 /auth/forgot/confirm 一致（账号字符集、姓名 2-20、密码 6-64）
const rules = {
  username: [
    { required: true, message: '请输入账号', trigger: 'blur' },
    { pattern: /^[A-Za-z0-9_]{3,20}$/, message: '账号需为 3-20 位字母、数字或下划线', trigger: 'blur' }
  ],
  realName: [
    { required: true, message: '请输入注册时填写的姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度应为 2-20 个字符', trigger: 'blur' }
  ],
  newPassword: [{ required: true, min: 6, max: 64, message: '新密码长度应为 6-64 位', trigger: 'blur' }],
  confirm: [
    {
      validator: (r, v, cb) => (v === form.newPassword ? cb() : cb(new Error('两次输入的新密码不一致'))),
      trigger: 'blur'
    }
  ]
}

async function onReset() {
  await formRef.value.validate(async valid => {
    if (!valid) return
    loading.value = true
    try {
      const res = await authApi.forgotConfirm({
        username: form.username.trim(),
        realName: form.realName.trim(),
        newPassword: form.newPassword
      })
      if (res.code !== 200) {
        ElMessage.error(res.message)
        return
      }
      ElMessage.success(res.message || '重置成功，请用新密码登录')
      router.push({ path: '/login', query: { tip: 'reset' } })
    } catch (e) {
      ElMessage.error('无法连接服务器，请确认后端已启动')
    } finally {
      loading.value = false
    }
  })
}

async function onHint() {
  const u = form.username.trim()
  if (!u) {
    ElMessage.warning('请先填写账号，再获取姓名提示')
    return
  }
  hintLoading.value = true
  hintText.value = ''
  try {
    const res = await authApi.forgotHint(u)
    if (res.code !== 200) {
      ElMessage.error(res.message || '获取提示失败，请稍后重试')
      return
    }
    const masked = (res.data || {}).masked
    // 账号不存在与没设置姓名返回同一响应 —— 前端也不区分，避免帮人试探注册名单
    hintText.value = masked
      ? `姓名提示：${masked}（共 ${res.data.length} 个字）`
      : '没有查到该账号的姓名提示，请确认账号是否正确；还是想不起来就去「申请临时密码」，由管理员核实身份后发放'
  } catch (e) {
    ElMessage.error('无法连接服务器，请确认后端已启动')
  } finally {
    hintLoading.value = false
  }
}

onMounted(() => {
  // 从「修改密码」页跳过来时带上账号，少填一次
  const u = sessionStorage.getItem('cv_username')
  if (u) form.username = u
})
</script>

<style scoped>
/* .bottom 与 .side-entry 的共用样式统一在 AuthShell 壳里 */
.hint-row { display: flex; align-items: center; gap: 10px; width: 100%; margin-top: 5px; font-size: 11.5px; }
.hint-link { padding: 0; border: none; background: none; cursor: pointer; color: var(--el-color-primary); font-size: 12px; }
.hint-link:disabled { cursor: not-allowed; opacity: .55; }
.hint-text { color: var(--text-3, #8b95a3); }
</style>
