<template>
  <AuthShell title="注册新账号" sub="注册时填写的姓名将作为找回密码的唯一凭证，请填写真实姓名">
    <el-form :model="form" :rules="rules" ref="formRef" size="large" @submit.prevent>
      <el-form-item prop="username">
        <el-input v-model="form.username" placeholder="请输入账号（3-20 位字母/数字/下划线）" :prefix-icon="User" maxlength="20" />
      </el-form-item>
      <el-form-item prop="realName">
        <el-input v-model="form.realName" placeholder="请输入姓名（忘记密码时用它验证身份）" :prefix-icon="UserFilled" maxlength="20" />
      </el-form-item>
      <el-form-item prop="password">
        <el-input v-model="form.password" type="password" placeholder="请设置密码（6-64 位）" :prefix-icon="Lock" show-password maxlength="64" />
      </el-form-item>
      <el-form-item prop="confirm">
        <el-input v-model="form.confirm" type="password" placeholder="请再次输入密码" :prefix-icon="Lock" show-password maxlength="64" @keyup.enter="onRegister" />
      </el-form-item>
      <el-button type="primary" class="submit" :loading="loading" @click="onRegister">注 册</el-button>
    </el-form>
    <div class="bottom">
      <span>已有账号？</span>
      <router-link to="/login">返回登录</router-link>
    </div>
  </AuthShell>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AuthShell from '@/components/AuthShell.vue'
import { authApi } from '@/api'
import { ElMessage } from 'element-plus'
import { User, UserFilled, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const form = ref({ username: '', realName: '', password: '', confirm: '' })
const rules = {
  username: [
    { required: true, message: '请输入账号', trigger: 'blur' },
    { min: 3, max: 20, message: '账号需为 3-20 位字母、数字或下划线', trigger: 'blur' },
    { pattern: /^[A-Za-z0-9_]{3,20}$/, message: '账号只能包含字母、数字或下划线', trigger: 'blur' }
  ],
  // 姓名必填：找回密码只认「账号 + 姓名」，注册时不填等于永远找不回密码
  realName: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度应为 2-20 个字符', trigger: 'blur' }
  ],
  password: [{ required: true, min: 6, max: 64, message: '密码长度应为 6-64 位', trigger: 'blur' }],
  confirm: [
    {
      validator: (r, v, cb) => (v === form.value.password ? cb() : cb(new Error('两次密码不一致'))),
      trigger: 'blur'
    }
  ]
}

async function onRegister() {
  await formRef.value.validate(async valid => {
    if (!valid) return
    loading.value = true
    try {
      const res = await authApi.register(form.value)
      if (res.code === 200) {
        ElMessage.success('注册成功，请登录')
        router.push('/login')
      } else {
        ElMessage.error(res.message)
      }
    } catch (e) {
      ElMessage.error('注册失败')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.bottom > span { margin-right: 4px; }
</style>
