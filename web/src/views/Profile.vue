<template>
  <div class="page">
    <div class="card profile-head">
      <!-- 头像：点击换图，hover 出蒙层提示可点。
           没设过头像时回退显示姓名首字，和顶栏逻辑保持一致 -->
      <!-- 头像 + 「恢复默认」。整块 .avatar-box 是「更换头像」的点击热区，
           所以「恢复默认」必须放在热区外面，否则点它会顺带弹出选图框 -->
      <div class="avatar-col">
        <div class="avatar-box" :class="{ 'is-uploading': uploading }" @click="pickAvatar">
          <el-avatar :size="72" class="big-avatar" :src="avatarUrl || undefined">
            {{ (userInfo?.realName || 'U')[0] }}
          </el-avatar>
          <div class="avatar-mask">
            <el-icon><Camera /></el-icon>
            <span>{{ uploading ? '上传中…' : '更换头像' }}</span>
          </div>
        </div>
        <!-- 两个操作始终显示：默认头像时「查看」展示大号文字头像，
             「恢复」提示已是默认 —— 藏起来反而让人以为按钮坏了 -->
        <div class="avatar-actions">
          <button class="avatar-reset" :disabled="uploading || resetting" @click="viewAvatar">
            查看头像
          </button>
          <button class="avatar-reset" :disabled="uploading || resetting" @click="resetAvatar">
            {{ resetting ? '处理中…' : '恢复默认' }}
          </button>
        </div>
      </div>
      <!-- 全屏看大图：el-image-viewer 自带缩放 / 关闭，不重复造轮子（自定义头像用） -->
      <el-image-viewer
        v-if="viewerVisible && avatarUrl"
        :url-list="[avatarUrl]"
        teleported
        @close="viewerVisible = false"
      />
      <!-- 默认头像没有图片 URL，用弹窗展示大号文字头像 -->
      <el-dialog v-model="defaultVisible" title="默认头像" width="300px" align-center>
        <div class="default-preview">
          <el-avatar :size="120" class="big-avatar">
            {{ (userInfo?.realName || 'U')[0] }}
          </el-avatar>
          <p class="small muted">当前使用默认头像（姓名首字）</p>
        </div>
      </el-dialog>
      <!-- 隐藏的文件选择框：用原生 input 而不是 el-upload，
           因为我们只要「选一张图 → 压缩 → 传一个字段」，套 el-upload 反而多出一堆要关的交互 -->
      <input
        ref="fileRef" type="file" accept="image/jpeg,image/png,image/webp"
        style="display: none" @change="onAvatarChange"
      />
      <div class="p-info">
        <!-- 姓名是「我是谁」，角色是「我能干什么」，账号是「系统里怎么叫我」。
             三件事挤一行，改个名都想不起来角色在哪；拆开后扫一眼各归各位 -->
        <div class="p-name-row">
          <h2>{{ userInfo?.realName || userInfo?.username }}</h2>
          <el-tag :type="isAdmin ? 'warning' : 'success'" effect="light" round class="p-role">
            {{ isAdmin ? '管理员' : '学生' }}
          </el-tag>
        </div>
        <p class="muted small p-account">账号：{{ userInfo?.username }}</p>
      </div>
      <div class="p-stats">
        <div class="ps-item"><b>{{ overview.knowledgeStudied || 0 }}</b><span>已学知识点</span></div>
        <div class="ps-item"><b>{{ rate }}%</b><span>答题正确率</span></div>
        <div class="ps-item"><b>{{ overview.wrongCount || 0 }}</b><span>错题</span></div>
        <div class="ps-item"><b>{{ overview.favoriteCount || 0 }}</b><span>收藏</span></div>
      </div>
    </div>

    <el-tabs v-model="tab" class="card tabs-card">
      <!-- 学习进度 -->
      <el-tab-pane label="学习进度" name="progress">
        <div v-for="p in overview.courseProgress || []" :key="p.id" class="prog-row">
          <span class="pname">{{ p.name }}</span>
          <el-progress :percentage="p.total ? Math.round(p.done / p.total * 100) : 0" :stroke-width="12" style="flex:1" />
          <span class="pval">{{ p.done }}/{{ p.total }}</span>
          <el-button text type="primary" size="small" @click="$router.push('/course/' + p.id)">继续学习</el-button>
        </div>
        <el-empty v-if="!overview.courseProgress?.length" description="还没有学习记录，快去课程中心看看吧" />
        <PaginationBar :total="progressTotal" v-model:page="progressPage.page"
                       v-model:pageSize="progressPage.pageSize" :sizes="profileSizes"
                       @change="loadOverview" />
      </el-tab-pane>

      <!-- 收藏 -->
      <el-tab-pane :label="'收藏 (' + favTotal + ')'" name="fav">
        <div class="fav-grid">
          <div v-for="f in favorites" :key="f.id" class="fav-card" @click="$router.push('/knowledge/' + f.knowledge_id)">
            <div class="fav-name">{{ f.name }}</div>
            <div class="fav-sum small muted">{{ f.summary }}</div>
            <div class="fav-foot">
              <el-tag size="small" effect="light">{{ f.course_name }}</el-tag>
              <el-button text type="primary" size="small" @click.stop="$router.push(labOf(f.route, f.knowledge_id).path)">
                {{ labOf(f.route, f.knowledge_id).label }}
              </el-button>
            </div>
          </div>
        </div>
        <el-empty v-if="!favorites.length" description="还没有收藏的知识点" />
        <PaginationBar :total="favTotal" v-model:page="favPage.page"
                       v-model:pageSize="favPage.pageSize" :sizes="profileSizes"
                       @change="loadFav" />
      </el-tab-pane>

      <!-- 错题本 -->
      <el-tab-pane :label="'错题本 (' + wrongTotal + ')'" name="wrong">
        <!-- 重做入口：错题本此前只能看答案，没有一条「再做一遍」的路。
             三档粒度对应三种场景：整本清空式复习、只消化本页、单题补刀。 -->
        <div class="wrong-tools">
          <span class="small muted">
            错题 {{ wrongTotal }} 道 —— 重做一遍才叫真的掌握，只看答案不算
          </span>
          <div class="wrong-tools-btns">
            <el-button size="small" type="danger" plain :disabled="!wrongTotal" @click="redoWrongs()">
              <el-icon><RefreshRight /></el-icon> 重做全部错题
            </el-button>
            <el-button size="small" type="danger" plain :disabled="!wrongs.length" @click="redoWrongs(wrongs.map(w => w.question_id))">
              重做本页 {{ wrongs.length }} 道
            </el-button>
          </div>
        </div>
        <div v-for="w in wrongs" :key="w.id" class="wrong-item">
          <div class="wrong-head">
            <el-tag size="small" type="danger" effect="light">错 {{ w.wrong_count }} 次</el-tag>
            <el-tag size="small" effect="light">{{ w.course_name }} · {{ w.knowledge_name }}</el-tag>
            <span class="small muted">{{ formatTime(w.last_wrong_time) }}</span>
            <div style="margin-left:auto;display:flex;gap:8px">
              <el-button text type="primary" size="small" @click="redoWrongs([w.question_id])">重做此题</el-button>
              <el-button text type="primary" size="small" @click="$router.push(labOf(w.knowledge_route, w.knowledge_id).path)">
                {{ labOf(w.knowledge_route, w.knowledge_id).label }}
              </el-button>
              <el-button text type="success" size="small" @click="removeWrong(w.question_id)">已掌握</el-button>
            </div>
          </div>
          <div class="wrong-title">{{ w.title }}</div>
          <el-collapse>
            <el-collapse-item title="查看答案与解析">
              <div class="small"><b>正确答案：</b>{{ w.answer }}</div>
              <div class="small" style="margin-top:4px"><b>解析：</b>{{ w.analysis }}</div>
            </el-collapse-item>
          </el-collapse>
        </div>
        <el-empty v-if="!wrongs.length" description="错题本是空的，保持得很好！" />
        <PaginationBar :total="wrongTotal" v-model:page="wrongPage.page"
                       v-model:pageSize="wrongPage.pageSize" :sizes="profileSizes"
                       @change="loadWrongs" />
      </el-tab-pane>

      <!-- 对话记录 -->
      <el-tab-pane :label="'对话记录 (' + chatTotal + ')'" name="chat">
        <div v-for="c in chats" :key="c.id" class="chat-item">
          <div class="chat-q"><b>问：</b>{{ c.question }}</div>
          <div class="chat-a small">{{ (c.answer || '').slice(0, 200) }}…</div>
          <div class="small muted">{{ formatTime(c.created_at) }}
            <el-button text type="primary" size="small" style="margin-left:8px" @click="$router.push('/agent')">继续提问</el-button>
          </div>
        </div>
        <el-empty v-if="!chats.length" description="还没有与智能助手对话" />
        <PaginationBar :total="chatTotal" v-model:page="chatPage.page"
                       v-model:pageSize="chatPage.pageSize" :sizes="profileSizes"
                       @change="loadChats" />
      </el-tab-pane>

      <!-- 我的反馈：看自己提过什么、管理员回复了什么 -->
      <el-tab-pane :label="'我的反馈 (' + fbTotal + ')'" name="feedback">
        <div class="fb-head">
          <span class="small muted">遇到问题或有建议，点右下角「意见反馈」随时提交，处理结果会显示在这里。</span>
          <el-button size="small" @click="loadFeedback">刷新</el-button>
        </div>
        <div v-for="f in feedbacks" :key="f.id" class="fb-item">
          <div class="fb-item-head">
            <el-tag size="small" :type="fbTypeTag(f.type)" effect="light">{{ fbTypeLabel(f.type) }}</el-tag>
            <el-tag size="small" :type="fbStatusTag(f.status)" effect="light">{{ fbStatusLabel(f.status) }}</el-tag>
            <span class="small muted">{{ formatTime(f.created_at) }}</span>
            <!-- 只有「待处理」能撤回：管理员已经在跟进的东西被悄悄删掉，
                 双方都会以为对方没动静，这种"消失的反馈"比留着更难办 -->
            <el-button v-if="f.status === 'pending'" text type="danger" size="small"
                       style="margin-left:auto" @click="removeFeedback(f)">撤回</el-button>
          </div>
          <div class="fb-content">{{ f.content }}</div>
          <div v-if="f.page" class="small muted">页面：{{ f.page }}</div>
          <div v-if="f.admin_reply" class="fb-reply">
            <b>管理员回复：</b>{{ f.admin_reply }}
            <span class="small muted">（{{ formatTime(f.replied_at) }}）</span>
          </div>
          <div v-else class="small muted fb-wait">还没有回复，我们会尽快处理</div>
        </div>
        <el-empty v-if="!feedbacks.length" description="还没有提交过反馈" />
        <PaginationBar :total="fbTotal" v-model:page="fbPage.page"
                       v-model:pageSize="fbPage.pageSize" :sizes="profileSizes"
                       @change="loadFeedback" />
      </el-tab-pane>

      <!-- 账号设置 -->
      <el-tab-pane label="账号设置" name="setting">
        <el-form :model="pwdForm" :rules="pwdRules" ref="pwdRef" label-width="100px" style="max-width:420px">
          <el-form-item label="原密码" prop="oldPassword">
            <el-input v-model="pwdForm.oldPassword" type="password" show-password maxlength="64" />
          </el-form-item>
          <el-form-item label="新密码" prop="newPassword">
            <el-input v-model="pwdForm.newPassword" type="password" show-password maxlength="64" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="changePwd">修改密码</el-button>
          </el-form-item>
        </el-form>

        <!-- 姓名是找回密码的唯一凭证：忘记密码时靠「账号 + 姓名」自证身份 -->
        <el-divider content-position="left">找回密码凭证</el-divider>
        <el-alert type="info" show-icon :closable="false" class="rec-tip">
          忘记密码时在登录页点「忘记密码？」，凭<b>账号 + 这里填写的姓名</b>即可自己重置，不用找管理员。
        </el-alert>
        <el-form :model="nameForm" label-width="100px" style="max-width:420px;margin-top:14px">
          <el-form-item label="姓名" prop="realName">
            <el-input v-model="nameForm.realName" placeholder="请填写真实姓名" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="nameSaving" @click="saveName">保存姓名</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { learnApi, authApi, feedbackApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { RefreshRight } from '@element-plus/icons-vue'
import { labOf } from '@/data/visMap'
import { compressAvatar, isAvatarImage } from '@/utils/avatar'
import PaginationBar from '@/components/PaginationBar.vue'

const route = useRoute()
const router = useRouter()
const store = useUserStore()
const userInfo = computed(() => store.userInfo)
const isAdmin = computed(() => store.isAdmin)

/* ---- 头像：本地选图 → 压缩 → 上传 → 同步 store ----
 * URL 是后端 /uploads 的静态路径（dev 走 vite 代理，生产同源），
 * 带时间戳之外的防缓存靠文件名里的随机段，这里不用再拼参数。 */
const avatarUrl = computed(() => (userInfo.value && userInfo.value.avatar) || '')
const fileRef = ref(null)
const uploading = ref(false)
const resetting = ref(false)
const viewerVisible = ref(false)
const defaultVisible = ref(false)

/* 查看头像：自定义头像走全屏 viewer（可缩放）；
   默认头像没有图片 URL，弹窗里放大展示文字头像 */
function viewAvatar() {
  if (avatarUrl.value) viewerVisible.value = true
  else defaultVisible.value = true
}

function pickAvatar() {
  if (uploading.value) return
  // 触发前先清 value：换过头像再选同一张文件，change 事件也能照常触发
  if (fileRef.value) fileRef.value.value = ''
  fileRef.value && fileRef.value.click()
}

async function onAvatarChange(e) {
  const file = e.target.files && e.target.files[0]
  if (!file) return
  if (!isAvatarImage(file)) {
    ElMessage.warning('仅支持 jpg / png / webp 格式的图片')
    return
  }
  uploading.value = true
  try {
    const blob = await compressAvatar(file)
    const fd = new FormData()
    // 文件名带扩展名，后端 multer 才能拿到合法的原始名（真正的类型校验在后端做魔数）
    fd.append('file', blob, 'avatar.jpg')
    const res = await authApi.uploadAvatar(fd)
    if (res.code !== 200) {
      ElMessage.error(res.message || '上传失败，请稍后重试')
      return
    }
    // 顶栏头像读的也是 store，不同步的话上传完页面上的头像纹丝不动
    store.setUser({ ...(store.userInfo || {}), avatar: res.data.avatar })
    ElMessage.success('头像已更新')
  } catch (err) {
    ElMessage.error((err && err.message) || '上传失败，请稍后重试')
  } finally {
    uploading.value = false
  }
}

/* 恢复默认头像：后端把 avatar 置空并删掉旧图，前端同步置空 ——
   顶栏头像读的也是 store，不同步的话这边恢复了、那边还是旧图。
   要不要二次确认？删掉的是用户自己上传的图，恢复后原图不在 CDN 上留底，
   手滑点一下就找不回来（只能重新上传原文件），所以值得拦一道。 */
async function resetAvatar() {
  if (resetting.value || uploading.value) return
  // 已经是默认头像就别再打接口了：后端置空是幂等的，但提示一句更清楚
  if (!avatarUrl.value) {
    ElMessage.info('当前已经是默认头像')
    return
  }
  try {
    await ElMessageBox.confirm(
      '将移除当前头像，改用默认的文字头像。原图会从服务器删除，如需恢复需要重新上传。',
      '恢复默认头像',
      { type: 'warning', confirmButtonText: '恢复默认', cancelButtonText: '取消' }
    )
  } catch (e) {
    return // 用户取消
  }
  resetting.value = true
  try {
    const res = await authApi.resetAvatar()
    if (res.code !== 200) {
      ElMessage.error(res.message || '操作失败，请稍后重试')
      return
    }
    store.setUser({ ...(store.userInfo || {}), avatar: '' })
    ElMessage.success('已恢复默认头像')
  } catch (err) {
    ElMessage.error((err && err.message) || '操作失败，请稍后重试')
  } finally {
    resetting.value = false
  }
}

const tab = ref(route.query.tab || 'progress')
const overview = ref({})
const favorites = ref([])
const wrongs = ref([])
const chats = ref([])
const pwdRef = ref()
const pwdForm = ref({ oldPassword: '', newPassword: '' })

/* ---- 四个列表各自的分页状态（全站统一用 PaginationBar，底部居中） ----
 * 个人中心是弹窗卡片式列表，每页 10 条起步比管理表格的 20 更合适，
 * 通过 sizes 覆盖组件默认档位。 */
const profileSizes = [10, 20, 50]
const progressPage = ref({ page: 1, pageSize: 10 })
const favPage = ref({ page: 1, pageSize: 10 })
const wrongPage = ref({ page: 1, pageSize: 10 })
const chatPage = ref({ page: 1, pageSize: 10 })
const fbPage = ref({ page: 1, pageSize: 10 })
const progressTotal = ref(0)
const favTotal = ref(0)
const wrongTotal = ref(0)
const chatTotal = ref(0)
const fbTotal = ref(0)

// 通用：页码超出总页数（删数据 / 改 pageSize 后）回退最后一页再拉一次
function clampPage(pageState, total) {
  const maxPage = Math.max(1, Math.ceil(total / pageState.pageSize))
  if (pageState.page > maxPage) {
    pageState.page = maxPage
    return true
  }
  return false
}

async function loadOverview() {
  try {
    const res = await learnApi.overview({
      page: progressPage.value.page, pageSize: progressPage.value.pageSize
    })
    const d = res.data || {}
    overview.value = d
    progressTotal.value = Number(d.courseProgressTotal || (d.courseProgress || []).length)
    if (clampPage(progressPage.value, progressTotal.value)) return loadOverview()
  } catch (e) {
    overview.value = {}
  }
}

async function loadFav() {
  try {
    const res = await learnApi.favorites({
      page: favPage.value.page, pageSize: favPage.value.pageSize
    })
    favorites.value = res.data || []
    favTotal.value = Number(res.total || favorites.value.length)
    if (clampPage(favPage.value, favTotal.value)) return loadFav()
  } catch (e) {
    favorites.value = []
  }
}

async function loadWrongs() {
  try {
    const res = await learnApi.wrongList({
      page: wrongPage.value.page, pageSize: wrongPage.value.pageSize
    })
    wrongs.value = res.data || []
    wrongTotal.value = Number(res.total || wrongs.value.length)
    if (clampPage(wrongPage.value, wrongTotal.value)) return loadWrongs()
  } catch (e) {
    wrongs.value = []
  }
}

async function loadChats() {
  try {
    const res = await learnApi.chats({
      page: chatPage.value.page, pageSize: chatPage.value.pageSize
    })
    chats.value = res.data || []
    chatTotal.value = Number(res.total || chats.value.length)
    if (clampPage(chatPage.value, chatTotal.value)) return loadChats()
  } catch (e) {
    chats.value = []
  }
}

/* ---- 我的反馈 ---- */
const feedbacks = ref([])
const FB_TYPE_LABELS = { bug: '功能异常', feature: '功能建议', experience: '体验问题', other: '其他' }
const FB_STATUS_LABELS = { pending: '待处理', processing: '处理中', resolved: '已解决', closed: '已关闭' }
const fbTypeLabel = t => FB_TYPE_LABELS[t] || '其他'
const fbStatusLabel = s => FB_STATUS_LABELS[s] || s
const fbTypeTag = t => (t === 'bug' ? 'danger' : t === 'feature' ? 'success' : t === 'experience' ? 'warning' : 'info')
const fbStatusTag = s => (s === 'pending' ? 'warning' : s === 'processing' ? 'primary'
  : s === 'resolved' ? 'success' : 'info')

async function loadFeedback() {
  try {
    const res = await feedbackApi.mine({
      page: fbPage.value.page, pageSize: fbPage.value.pageSize
    })
    feedbacks.value = res.data || []
    fbTotal.value = Number(res.total || feedbacks.value.length)
    if (clampPage(fbPage.value, fbTotal.value)) return loadFeedback()
  } catch (e) {
    feedbacks.value = []
  }
}

async function removeFeedback(f) {
  try {
    await feedbackApi.remove(f.id)
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '撤回失败，请稍后重试')
    return
  }
  ElMessage.success('已撤回')
  loadFeedback()
}

// 与后端 /auth/password 的校验保持一致（新密码 6-64 位）
const pwdRules = {
  oldPassword: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  newPassword: [{ required: true, min: 6, max: 64, message: '新密码长度应为 6-64 位', trigger: 'blur' }]
}

// ---- 姓名：找回密码的唯一凭证，允许随时更正 ----
const nameForm = ref({ realName: '' })
const nameSaving = ref(false)

async function loadName() {
  try {
    const me = await authApi.me()
    nameForm.value.realName = (me.data && me.data.realName) || ''
    // 头像可能在别的设备上换过：以 /auth/me 为准回写 store，别只信本地缓存
    const av = (me.data && me.data.avatar) || ''
    if (av && av !== ((store.userInfo || {}).avatar || '')) {
      store.setUser({ ...(store.userInfo || {}), avatar: av })
    }
  } catch (e) { /* 拿不到就留空，用户自己填 */ }
}

async function saveName() {
  const name = String(nameForm.value.realName || '').trim()
  if (name.length < 2 || name.length > 20) {
    ElMessage.warning('姓名长度应为 2-20 个字符')
    return
  }
  nameSaving.value = true
  try {
    const res = await authApi.updateProfile({ realName: name })
    if (res.code !== 200) {
      ElMessage.error(res.message)
      return
    }
    // 顶部头像/欢迎语读的是 store 里的用户信息，不同步的话改完姓名页面还显示旧的
    store.setUser({ ...(store.userInfo || {}), realName: name })
    ElMessage.success('姓名已保存')
  } catch (e) {
    ElMessage.error('无法连接服务器，请确认后端已启动')
  } finally {
    nameSaving.value = false
  }
}

const rate = computed(() => {
  const t = overview.value.answerTotal || 0
  return t ? Math.round((overview.value.answerCorrect / t) * 100) : 0
})

function formatTime(t) {
  if (!t) return ''
  const d = new Date(t)
  return `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

/* 错题重做入口：把错题本里的题直接送进做题页。
   不传 ids = 整本重做（后端按最近错的取，上限 200）；
   传 ids = 只做这几道（本页 / 单题）。题目跨知识点，所以走 /wrong-practice，
   不能塞进 practice/:kid —— 那是一条按知识点取题的路由。 */
function redoWrongs(ids) {
  const q = {}
  if (ids && ids.length) q.ids = ids.join(',')
  router.push({ path: '/wrong-practice', query: q })
}

async function removeWrong(qid) {
  // 先打请求再改本地列表：否则失败时会「提示已移除但刷新又回来了」，数据不一致
  try {
    await learnApi.removeWrong(qid)
  } catch (e) {
    ElMessage.error('移除失败，请稍后重试')
    return
  }
  ElMessage.success('已从错题本移除')
  // 重新拉当前页（页可能被删空，loadWrongs 内部会回退最后一页），顶部错题数同步刷新
  loadWrongs()
  loadOverview()
}

async function changePwd() {
  await pwdRef.value.validate(async valid => {
    if (!valid) return
    // 这里的 await 在 Element Plus 的异步校验回调里，异常会原样抛成 unhandled rejection，
    // 不兜住的话网络失败时用户点完毫无反应，连出错都不知道
    let res
    try {
      res = await authApi.password(pwdForm.value)
    } catch (e) {
      ElMessage.error('修改失败，请检查网络后重试')
      return
    }
    if (res.code === 200) {
      ElMessage.success('密码修改成功')
      pwdForm.value = { oldPassword: '', newPassword: '' }
    } else ElMessage.error(res.message)
  })
}

onMounted(async () => {
  await loadOverview()
  await loadName()
  // 收藏 / 错题 / 对话三个 Tab 互相独立，各自的分页加载失败只影响自己，
  // 不能用 Promise.all 让它们同生共死
  loadFav()
  loadWrongs()
  loadChats()
  loadFeedback()
})
</script>

<style scoped>
.profile-head { padding: 20px 24px; display: flex; align-items: center; gap: 18px; margin-bottom: 16px; flex-wrap: wrap; }
.big-avatar { background: var(--brand); font-size: 28px; }

/* 头像列：图片在上、操作在下。原来是单个 .avatar-box 直接参与头部 flex 行，
   加了「查看头像 / 恢复默认」后需要一个纵向容器；头像宽度固定，按钮比它宽就两端不齐，
   所以按钮行用自适应宽度 + 居中，不强行拉成 72px。 */
.avatar-col { display: flex; flex-direction: column; align-items: center; gap: 6px; flex-shrink: 0; }
.avatar-actions { display: flex; align-items: center; gap: 10px; }
.avatar-reset {
  padding: 0; border: none; background: none; cursor: pointer;
  font-size: 12px; line-height: 1.4; color: var(--text-3);
  transition: color .2s; white-space: nowrap;
}
.avatar-reset:hover:not(:disabled) { color: var(--brand); }
.avatar-reset:disabled { cursor: not-allowed; opacity: .6; }
.avatar-box {
  position: relative; width: 72px; height: 72px; border-radius: 50%;
  cursor: pointer; flex-shrink: 0; overflow: hidden;
}
/* 不能用 display:block：会废掉 el-avatar 自带的 inline-flex 居中，
   首字会顶到圆圈上沿。用 flex 保持块级布局的同时保留居中。 */
.avatar-box :deep(.el-avatar) {
  display: flex;
  align-items: center;
  justify-content: center;
  transition: filter .2s;
}
.avatar-box:hover :deep(.el-avatar) { filter: brightness(.82); }
.avatar-box.is-uploading { pointer-events: none; }
.avatar-mask {
  position: absolute; inset: auto 0 0 0; height: 26px;
  display: flex; align-items: center; justify-content: center; gap: 3px;
  background: rgba(17, 24, 39, .62); color: #fff;
  font-size: 11px; line-height: 1; opacity: 0; transition: opacity .2s;
}
.avatar-mask .el-icon { font-size: 12px; }
.avatar-box:hover .avatar-mask { opacity: 1; }
.avatar-box.is-uploading .avatar-mask { opacity: 1; }
/* 默认头像预览弹窗：头像居中 + 一句说明 */
.default-preview { display: flex; flex-direction: column; align-items: center; gap: 14px; padding: 6px 0 2px; }
.default-preview p { margin: 0; }

.p-info h2 { margin: 0; font-size: 20px; }
.p-name-row { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.p-role { flex-shrink: 0; }
.p-account { margin: 0; letter-spacing: .2px; }
.p-info p { margin: 0; }
.p-stats { margin-left: auto; display: flex; gap: 32px; }
.ps-item { text-align: center; }
.ps-item b { display: block; font-size: 22px; color: var(--brand); }
.ps-item span { font-size: 12px; color: var(--text-2); }
/* 窄屏：统计块不再靠右对齐（会把头像区挤成两行），改成整行铺开 */
@media (max-width: 768px) {
  .profile-head { padding: 16px 16px; gap: 12px; }
  .p-info h2 { font-size: 18px; }
  .p-stats { margin-left: 0; width: 100%; gap: 14px; flex-wrap: wrap; justify-content: space-between; }
  .ps-item { flex: 1 1 30%; }
  .ps-item b { font-size: 19px; }
  .tabs-card { padding: 8px 12px 14px; }
}
@media (max-width: 480px) {
  .pname { width: 92px; }
  .prog-row { gap: 8px; }
}

.tabs-card { padding: 8px 18px 18px; }
.prog-row { display: flex; align-items: center; gap: 14px; margin-bottom: 14px; }
.pname { width: 130px; font-size: 14px; }
.pval { width: 50px; text-align: right; font-size: 13px; color: var(--text-2); }

.fav-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 260px), 1fr)); gap: 12px; }
.fav-card { border: 1px solid var(--border); border-radius: 10px; padding: 14px; cursor: pointer; transition: all .2s; }
.fav-card:hover { border-color: var(--brand); box-shadow: 0 4px 12px rgba(59,110,246,.08); }
.fav-name { font-weight: 600; margin-bottom: 4px; }
.fav-sum { height: 34px; overflow: hidden; line-height: 1.6; }
.fav-foot { display: flex; justify-content: space-between; align-items: center; margin-top: 6px; }

/* 错题本顶部的重做工具条 */
.wrong-tools {
  display: flex; align-items: center; justify-content: space-between;
  gap: 10px; flex-wrap: wrap; margin-bottom: 12px;
}
.wrong-tools-btns { display: flex; gap: 8px; flex-wrap: wrap; }
.wrong-tools-btns .el-button { margin-left: 0; }
.wrong-item { border: 1px solid var(--border); border-radius: 10px; padding: 12px 14px; margin-bottom: 10px; }
.wrong-head { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.wrong-title { font-size: 14px; line-height: 1.7; margin: 8px 0; }

.chat-item { border-bottom: 1px dashed var(--border); padding: 10px 0; }
.chat-q { font-size: 14px; margin-bottom: 4px; }
.chat-a { color: var(--text-2); line-height: 1.7; }

/* 我的反馈 */
.fb-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 12px; }
.fb-item { border: 1px solid var(--border); border-radius: 10px; padding: 12px 14px; margin-bottom: 10px; }
.fb-item-head { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.fb-content { font-size: 14px; line-height: 1.7; margin: 8px 0; white-space: pre-wrap; word-break: break-word; }
.fb-reply {
  margin-top: 8px; padding: 8px 10px; border-radius: 8px;
  background: var(--brand-light); font-size: 13px; line-height: 1.7;
  white-space: pre-wrap; word-break: break-word;
}
.fb-wait { margin-top: 6px; }
</style>
