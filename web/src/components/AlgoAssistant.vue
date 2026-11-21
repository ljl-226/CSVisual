<template>
  <div class="aa">
    <div class="aa-head">
      <el-icon class="aa-icon"><MagicStick /></el-icon>
      <div class="aa-title">
        <b>算法小助手</b>
        <div class="small muted">先讲思路再给结论；卡住了可以贴代码让我帮你看</div>
      </div>
      <el-tag v-if="lastMode === 'llm'" size="small" type="success" effect="light">大模型模式</el-tag>
      <el-tag v-else-if="lastMode" size="small" type="info" effect="light">本地知识库模式</el-tag>
    </div>

    <div class="aa-quick">
      <el-button size="small" plain :loading="loading" @click="ask('explain')">
        <el-icon><MagicStick /></el-icon> 讲解思路
      </el-button>
      <el-button size="small" plain :loading="loading" @click="ask('complexity')">
        <el-icon><DataLine /></el-icon> 分析复杂度
      </el-button>
      <el-button size="small" plain :loading="loading" @click="ask('debug')">
        <el-icon><View /></el-icon> 帮我看代码
      </el-button>
    </div>

    <div class="aa-list" ref="listBox">
      <div v-if="!records.length" class="aa-empty small muted">
        试试上面的快捷按钮，或直接在下方描述你的问题 / 粘贴代码。
      </div>

      <div v-for="(r, i) in records" :key="i" class="msg" :class="r.role">
        <el-avatar :size="28" class="avatar" :style="{ background: r.role === 'user' ? '#8b95a3' : 'var(--brand)' }">
          {{ r.role === 'user' ? '我' : 'AI' }}
        </el-avatar>
        <div class="bubble">
          <!-- 用户提问 -->
          <div v-if="r.role === 'user'" class="msg-text user-text">
            {{ r.content }}
            <div v-if="r.withCode" class="small" style="opacity:.85;margin-top:4px">（已附带编辑器里的代码）</div>
          </div>

          <!-- 助手回答：思考过程 + 结论 -->
          <template v-else>
            <div v-if="r.reasoning && r.reasoning.length" class="think">
              <div class="think-head" @click="r.open = !r.open">
                <el-icon class="caret" :class="{ on: r.open }"><ArrowRight /></el-icon>
                <el-icon class="think-ico"><Loading /></el-icon>
                <span>思考过程（{{ r.reasoning.length }} 步）</span>
                <span class="small muted">{{ r.open ? '收起' : '展开' }}</span>
              </div>
              <div v-show="r.open" class="think-body">
                <div v-for="(s, si) in r.reasoning" :key="si" class="think-item">
                  <div class="think-no">{{ si + 1 }}</div>
                  <div class="think-main">
                    <div class="think-title">{{ s.title || s.phase }}</div>
                    <div class="think-detail">{{ s.detail }}</div>
                  </div>
                </div>
              </div>
            </div>

            <div class="msg-text markdown-body" v-html="render(r.answer)"></div>
            <span v-if="r.typing" class="type-caret"></span>
          </template>
        </div>
      </div>

      <div v-if="loading && lastIsUser" class="msg ai">
        <el-avatar :size="28" class="avatar" style="background:var(--brand)">AI</el-avatar>
        <div class="bubble">
          <div class="typing"><span></span><span></span><span></span></div>
          <div class="small muted">正在结合题面思考…</div>
        </div>
      </div>
    </div>

    <div class="aa-input">
      <el-input
        v-model="input" type="textarea" :rows="3" resize="none"
        placeholder="描述你的问题，或把报错 / 代码粘贴到这里（Ctrl + Enter 发送）"
        @keydown.ctrl.enter="ask(currentMode)"
      />
      <div class="aa-foot">
        <span class="small muted">
          <el-icon><InfoFilled /></el-icon>
          「帮我看代码」会带上编辑器里当前的代码
        </span>
        <el-button type="primary" size="small" :loading="loading" :disabled="!canSend" @click="ask(currentMode)">
          发送 <el-icon><Promotion /></el-icon>
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { algorithmApi } from '@/api'
import { renderMd } from '../utils/markdown'
import { streamPost, useTypewriter } from '../utils/sse'
import { ElMessage } from 'element-plus'
import { MagicStick, DataLine, View, ArrowRight, Loading, InfoFilled, Promotion } from '@element-plus/icons-vue'

const props = defineProps({
  algorithmId: { type: [Number, String], default: null },
  // 编辑器里的当前代码，「帮我看代码」时自动带上
  code: { type: String, default: '' },
  language: { type: String, default: '' }
})

const input = ref('')
const loading = ref(false)
const records = ref([])
const listBox = ref()
const currentMode = ref('explain')
const lastMode = ref('')

const canSend = computed(() => !!input.value.trim() || !!props.code.trim() || !!props.algorithmId)
/** 流式已经吐第一个字之后，就不再显示"正在思考"的占位气泡 */
const lastIsUser = computed(() => {
  const last = records.value[records.value.length - 1]
  return !last || last.role === 'user'
})

const DEFAULT_QUESTION = {
  explain: '请讲解这道题的解题思路，并给出关键步骤。',
  complexity: '请分析这道题的时间复杂度与空间复杂度，并说明能否优化。',
  debug: '帮我看看这段代码错在哪里、应该怎么改。'
}

function render(text) {
  return renderMd(text)
}

function scrollBottom() {
  nextTick(() => {
    if (listBox.value) listBox.value.scrollTop = listBox.value.scrollHeight
  })
}

/** 一次性接口兜底：流式不可用时（未开启 SSE / 反代缓冲）仍能拿到答案。
 *  同样要走打字机：降级不能让「逐字输出」这个承诺失效。 */
async function askSync(payload) {
  try {
    const res = await algorithmApi.assistant(payload)
    if (res.code === 200 && res.data) {
      lastMode.value = res.data.mode || ''
      records.value.push({
        role: 'ai',
        reasoning: res.data.reasoning || [],
        answer: '',
        open: true,
        typing: true
      })
      const box = records.value[records.value.length - 1]
      const tw = useTypewriter(() => box.answer, v => { box.answer = v; scrollBottom() })
      tw.push(res.data.answer || '（这次没有拿到回答，换个问法试试）')
      tw.finish()
    } else {
      ElMessage.error(res.message || '小助手暂时无法回答')
    }
  } catch (e) {
    ElMessage.error('无法连接服务')
  }
}

/** mode: explain / complexity / debug */
async function ask(mode) {
  if (loading.value) return
  const m = mode || 'explain'
  currentMode.value = m

  const isDebug = m === 'debug'
  const code = isDebug ? (props.code || '') : ''
  let question = input.value.trim()
  if (!question) {
    question = DEFAULT_QUESTION[m]
    if (isDebug && !code.trim()) {
      ElMessage.warning('请先在编辑器里写代码，或把代码粘贴到输入框')
      return
    }
  }
  if (!question && !code.trim() && !props.algorithmId) {
    ElMessage.warning('请描述你的问题')
    return
  }

  loading.value = true
  records.value.push({ role: 'user', content: question, withCode: !!code.trim() })
  input.value = ''
  scrollBottom()

  const payload = { algorithmId: props.algorithmId, question, code, mode: m }

  records.value.push({ role: 'ai', reasoning: [], answer: '', open: true, typing: false })
  scrollBottom()
  // 改代理对象，改原始对象不会触发视图更新
  const box = records.value[records.value.length - 1]
  const tw = useTypewriter(() => box.answer, v => { box.answer = v; scrollBottom() })

  let settled = false
  const settle = mode2 => {
    if (settled) return
    settled = true
    box.typing = false
    if (mode2) lastMode.value = mode2
    loading.value = false
    scrollBottom()
  }

  streamPost('/api/algorithm/assistant/stream', payload, {
    onMeta: meta => {
      box.reasoning = meta.reasoning || []
      scrollBottom()
    },
    onDelta: t => { box.typing = true; tw.push(t) },
    onDone: d => {
      tw.finish()
      settle(d && d.mode)
      if (!box.answer) box.answer = '（这次没有拿到回答，换个问法试试）'
    },
    onAbort: () => { tw.stop(); settle() },
    onError: async err => {
      tw.stop()
      console.warn('[algo-assistant] 流式失败，降级为一次性接口：', err && err.message)
      records.value.pop()
      await askSync(payload)
      settle()
    }
  })
}

defineExpose({ ask })
</script>

<style scoped>
.aa { display: flex; flex-direction: column; }
.aa-head { display: flex; align-items: center; gap: 8px; padding-bottom: 10px; border-bottom: 1px solid var(--border); }
.aa-icon { font-size: 20px; color: var(--brand); }
.aa-title { flex: 1; min-width: 0; }
.aa-title b { font-size: 14px; }
.aa-quick { display: flex; gap: 8px; flex-wrap: wrap; padding: 10px 0; }

.aa-list {
  flex: 1; min-height: 160px; max-height: 420px; overflow-y: auto;
  background: var(--soft-bg); border: 1px solid var(--border); border-radius: 10px; padding: 12px;
}
.aa-empty { padding: 16px 4px; }

.msg { display: flex; gap: 8px; margin-bottom: 14px; }
.msg:last-child { margin-bottom: 0; }
.avatar { flex-shrink: 0; }
.bubble { max-width: 84%; min-width: 0; }
.msg-text {
  background: var(--soft-bg); border: 1px solid var(--border); border-radius: 10px; padding: 10px 12px;
  font-size: 13px; line-height: 1.8; word-break: break-word;
}
.user-text { background: var(--brand); color: #fff; border-color: var(--brand); }
.msg.user { flex-direction: row-reverse; }

/* 思考过程（可折叠，默认展开） */
.think { border: 1px dashed var(--brand-2); border-radius: 10px; background: var(--brand-light); margin-bottom: 8px; overflow: hidden; }
.think-head {
  display: flex; align-items: center; gap: 6px; padding: 7px 10px; cursor: pointer;
  font-size: 12px; color: var(--brand); user-select: none;
}
.think-head .small { margin-left: auto; }
.caret { transition: transform .2s; }
.caret.on { transform: rotate(90deg); }
.think-ico { font-size: 13px; }
.think-body { border-top: 1px dashed var(--brand-2); padding: 8px 10px; }
.think-item { display: flex; gap: 8px; margin-bottom: 8px; }
.think-item:last-child { margin-bottom: 0; }
.think-no {
  width: 18px; height: 18px; flex-shrink: 0; border-radius: 50%; background: var(--brand); color: #fff;
  font-size: 11px; display: flex; align-items: center; justify-content: center; margin-top: 2px;
}
.think-title { font-size: 12px; font-weight: 600; color: var(--text); }
.think-detail { font-size: 12px; line-height: 1.7; color: var(--text-2); }

.typing { display: flex; gap: 4px; margin-bottom: 4px; }
.typing span { width: 6px; height: 6px; border-radius: 50%; background: var(--brand-2); animation: blink 1.2s infinite; }
.typing span:nth-child(2) { animation-delay: .2s; }
.typing span:nth-child(3) { animation-delay: .4s; }
@keyframes blink { 0%, 60%, 100% { opacity: .3 } 30% { opacity: 1 } }

/* 流式输出时的打字光标 */
.type-caret {
  display: inline-block; width: 7px; height: 14px; margin-left: 2px;
  vertical-align: text-bottom; background: var(--brand); border-radius: 1px;
  animation: caret 1s steps(2, start) infinite;
}
@keyframes caret { 0%, 100% { opacity: 1 } 50% { opacity: 0 } }

.aa-input { padding-top: 10px; border-top: 1px solid var(--border); }
.aa-foot { display: flex; justify-content: space-between; align-items: center; margin-top: 8px; gap: 10px; }
.aa-foot span { display: flex; align-items: center; gap: 4px; }
</style>
