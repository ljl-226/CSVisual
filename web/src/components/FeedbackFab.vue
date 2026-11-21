<template>
  <!-- 全局「意见反馈」入口。
       做成右下角悬浮钮而不是藏进个人中心：反馈的触发时机是「正在用某个页面时踩到坑」，
       这个时候让用户先跳转去个人中心再填表，一半人就放弃了，而 bug 也就跟着消失了。 -->
  <button class="fb-fab" :title="tip" @click="open">
    <el-icon><ChatLineSquare /></el-icon>
    <span class="fb-fab-text">意见反馈</span>
  </button>

  <el-dialog v-model="visible" title="意见反馈" width="520px" class="fb-dialog" @closed="onClosed">
    <p class="fb-tip">
      遇到功能异常、有改进建议，或者觉得哪里用着别扭，都可以告诉我们。
      描述得越具体，修复得越快。
    </p>

    <el-form :model="form" label-width="76px" class="fb-form">
      <el-form-item label="类型">
        <el-radio-group v-model="form.type">
          <el-radio-button v-for="t in TYPES" :key="t.value" :value="t.value">{{ t.label }}</el-radio-button>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="问题描述" required>
        <el-input
          v-model="form.content" type="textarea" :rows="5" maxlength="1000" show-word-limit
          :placeholder="placeholder" resize="none"
        />
      </el-form-item>
      <el-form-item label="联系方式">
        <el-input v-model="form.contact" maxlength="120" placeholder="选填，方便我们回复你（邮箱 / QQ / 微信）" />
      </el-form-item>
      <el-form-item label="当前页面">
        <!-- 自动带上当前路由：管理员看到「/vis/quick-sort」就知道去哪儿复现，
             比让用户自己描述「那个排序的动画页面」准确得多 -->
        <span class="fb-page small muted">{{ form.page || '-' }}</span>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submit">提交</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { reactive, ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { feedbackApi } from '@/api'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const route = useRoute()
const store = useUserStore()

const TYPES = [
  { value: 'bug', label: '功能异常' },
  { value: 'feature', label: '功能建议' },
  { value: 'experience', label: '体验问题' },
  { value: 'other', label: '其他' }
]

const PLACEHOLDER = {
  bug: '例如：快速排序动画第三步的分界线位置不对，点「下一步」后画面卡住不动',
  feature: '例如：希望题库能按难度筛选，方便从简单的开始刷',
  experience: '例如：手机上打开算法题页面，代码编辑器挡住了题目',
  other: '说说你的想法，我们会认真看每一条'
}

const visible = ref(false)
const saving = ref(false)
const form = reactive({ type: 'bug', content: '', contact: '', page: '' })
const placeholder = computed(() => PLACEHOLDER[form.type] || PLACEHOLDER.other)
const tip = computed(() => (store.isLogin ? '提交反馈或建议' : '登录后提交反馈'))

function open() {
  if (!store.isLogin) {
    ElMessage.warning('请先登录再提交反馈')
    return
  }
  form.page = route.fullPath || route.path
  visible.value = true
}

async function submit() {
  const content = String(form.content || '').trim()
  if (content.length < 5) {
    ElMessage.warning('请至少写 5 个字，方便我们定位问题')
    return
  }
  saving.value = true
  try {
    await feedbackApi.submit({
      type: form.type,
      content,
      contact: String(form.contact || '').trim(),
      page: form.page
    })
    ElMessage.success('提交成功，感谢你的反馈！')
    visible.value = false
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '提交失败，请稍后再试')
  } finally {
    saving.value = false
  }
}

function onClosed() {
  // 关掉就清空，下次打开是干净的；类型保留上次选择（连续提同类问题是常态）
  form.content = ''
  form.contact = ''
}
</script>

<style scoped>
.fb-fab {
  position: fixed;
  right: 22px;
  bottom: 26px;
  z-index: 900;
  display: flex;
  align-items: center;
  gap: 6px;
  height: 40px;
  padding: 0 16px;
  border-radius: 20px;
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--text-2);
  font-size: 13px;
  cursor: pointer;
  box-shadow: var(--shadow);
  transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
}
.fb-fab:hover {
  color: #fff;
  border-color: transparent;
  background: var(--grad-brand);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.16);
}
.fb-fab .el-icon { font-size: 16px; }

/* 窄屏只留图标：带文字的胶囊 + 内容区容易撞上右侧元素 */
@media (max-width: 600px) {
  .fb-fab { right: 12px; bottom: 16px; padding: 0; width: 40px; justify-content: center; }
  .fb-fab-text { display: none; }
}

.fb-tip {
  margin: 0 0 14px;
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-2);
}
.fb-form :deep(.el-radio-button__inner) { padding: 8px 12px; }
.fb-page { word-break: break-all; }
</style>
