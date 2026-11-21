<template>
  <AuthShell title="账号登录" sub="登录后即可使用全部可视化动画与智能助手">
    <el-form :model="form" :rules="rules" ref="formRef" size="large">
      <el-form-item prop="username">
        <el-input v-model="form.username" placeholder="请输入账号" :prefix-icon="User" maxlength="20" />
      </el-form-item>
      <el-form-item prop="password">
        <el-input v-model="form.password" type="password" placeholder="请输入密码" :prefix-icon="Lock" show-password maxlength="64" @keyup.enter="onLogin" />
      </el-form-item>
      <el-button type="primary" class="submit" :loading="loading" @click="onLogin">登 录</el-button>
    </el-form>
    <div class="bottom split">
      <router-link to="/forgot">忘记密码？</router-link>
      <span>
        <span>还没有账号？</span>
        <router-link to="/register">立即注册</router-link>
      </span>
    </div>
    <!-- 右下角单独一行：自助找回的凭证是姓名，姓名也忘了就只能一路走到这里。
         放在主链接区里会和「忘记密码」抢注意力，而它是最冷的兜底入口。 -->
    <div class="side-entry">
      <span class="small muted">连姓名也不记得？</span>
      <router-link to="/temp-password">申请临时密码</router-link>
    </div>
    <el-divider><span class="small muted">演示账号</span></el-divider>
    <div class="demo">
      <el-button size="small" @click="fill('student','123456')">学生：student / 123456</el-button>
      <el-button size="small" @click="fill('admin','admin123')">管理员：admin / admin123</el-button>
    </div>
  </AuthShell>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import AuthShell from '@/components/AuthShell.vue'
import { authApi } from '@/api'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const store = useUserStore()
const formRef = ref()
const loading = ref(false)
const form = ref({ username: '', password: '' })
/**
 * 校验规则与后端 /api/auth/login 完全一致（长度、字符范围）。
 * 前端校验只是为了少发一次无效请求、让用户当场看到问题；
 * 真正的把关在后端 —— 绕过前端直接调接口时，这些规则同样生效。
 * maxlength 则纯粹是防手滑：粘贴一大段文本进来没有意义，
 * 也不该让后端为它跑一次 bcrypt。
 */
const rules = {
  username: [
    { required: true, message: '请输入账号', trigger: 'blur' },
    { pattern: /^[A-Za-z0-9_]{3,20}$/, message: '账号需为 3-20 位字母、数字或下划线', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 64, message: '密码长度应为 6-64 位', trigger: 'blur' }
  ]
}

function fill(u, p) {
  form.value.username = u
  form.value.password = p
}

onMounted(() => {
  const q = route.query || {}
  // 从「找回密码」页回来时带上账号，少填一次
  if (q.username) form.value.username = String(q.username)
  else {
    const saved = sessionStorage.getItem('cv_username')
    if (saved) form.value.username = saved
  }
  // 临时密码是八位随机字符，让用户手抄一遍是最容易输错的一步 ——
  // 申请页已经把它暂存到这里，登录页直接填好
  try {
    const hint = JSON.parse(sessionStorage.getItem('cv_login_hint') || 'null')
    if (hint && hint.username) {
      form.value.username = hint.username
      if (hint.password) form.value.password = hint.password
      sessionStorage.removeItem('cv_login_hint')
      ElMessage.info('临时密码已填入，登录后请立即修改为自己的密码')
    }
  } catch (e) {
    sessionStorage.removeItem('cv_login_hint')
  }
})

async function onLogin() {
  await formRef.value.validate(async valid => {
    if (!valid) return
    loading.value = true
    try {
      const res = await authApi.login(form.value)
      if (res.code === 200) {
        store.setAuth(res.data.token, res.data.user)
        ElMessage.success('欢迎回来，' + res.data.user.realName)
        router.push(route.query.redirect || '/')
      } else {
        ElMessage.error(res.message)
      }
    } catch (e) {
      ElMessage.error('无法连接服务器，请确认后端已启动')
    } finally {
      loading.value = false
    }
  })
}

</script>

<style scoped>
.demo { display: flex; flex-direction: column; gap: 6px; }
.demo :deep(.el-button) { justify-content: flex-start; }
/* side-entry 的样式统一放在 AuthShell 壳里（与找回密码页共用） */
</style>
