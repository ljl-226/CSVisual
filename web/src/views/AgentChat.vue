<template>
  <div class="page agent-page">
    <el-row :gutter="16">
      <!-- 历史对话：窄屏整体堆到对话区上方，不再挤成一条窄栏 -->
      <el-col :xs="24" :sm="24" :md="7" :lg="6">
        <div class="card side">
          <div class="side-head">
            <b>多轮会话</b>
            <el-button text type="primary" size="small" @click="newChat">新建对话</el-button>
          </div>
          <div class="hist-list">
            <div
              v-for="s in sessions" :key="s.id"
              class="hist-item" :class="{ active: s.id === sessionId }"
              @click="loadSession(s)"
            >
              <div class="hist-q">
                <el-icon v-if="s.id === 'legacy'" class="hist-ico"><Clock /></el-icon>
                {{ s.title || '新对话' }}
              </div>
              <div class="hist-t small muted">
                <span>
                  {{ formatTime(s.updated_at || s.created_at) }}
                  <span v-if="s.msg_count"> · {{ s.msg_count }} 条</span>
                </span>
                <el-icon class="del-icon" @click.stop="removeSession(s)"><Delete /></el-icon>
              </div>
            </div>
            <el-empty v-if="!sessions.length" description="暂无会话" :image-size="50" />
          </div>
          <el-divider style="margin:12px 0" />
          <div class="tools-box">
            <el-button size="small" type="warning" plain style="width:100%;margin-bottom:10px" :loading="reportLoading" @click="openReport">
              <el-icon><DataLine /></el-icon> 生成我的学习报告
            </el-button>
            <div class="panel-title">
              助手能力
              <el-button
                v-if="tools.length > 4" text size="small" class="tools-toggle"
                @click="toolsOpen = !toolsOpen"
              >
                {{ toolsOpen ? '收起' : '展开全部 ' + tools.length + ' 项' }}
              </el-button>
            </div>
            <!-- 能力清单默认只露 4 项：8 项全展开在 800px 高的屏上会把侧栏撑出视口，
                 底部条目被裁成半行，看起来就像文字压在盒子上 -->
            <div v-if="tools.length" class="tools-list" :class="{ collapsed: !toolsOpen }">
              <div v-for="t in tools" :key="t.name" class="tool-item">
                <b>{{ t.name }}</b>
                <div class="small muted">{{ t.desc }}</div>
              </div>
            </div>
            <!-- 工具箱 / 记忆：侧栏两个窄按钮并排，比塞进能力清单更好找 -->
            <div class="panel-actions">
              <el-button size="small" plain @click="openToolbox">工具箱</el-button>
              <el-button size="small" plain @click="openMemory">记忆与设置</el-button>
            </div>
          </div>

          <!-- 其他模块敬请期待：贴在侧栏底部。无论右侧会话列表多长，
               这个卡片始终占据左列剩余空间，把左下角空档填满。 -->
          <div class="soon-card">
            <div class="soon-head">
              <el-icon><Grid /></el-icon>
              <b>其他模块敬请期待</b>
            </div>
            <ul class="soon-list">
              <li v-for="s in SOON_MODULES" :key="s">
                <span class="soon-dot"></span>{{ s }}
              </li>
            </ul>
          </div>
        </div>
      </el-col>

      <!-- 对话区 -->
      <el-col :xs="24" :sm="24" :md="17" :lg="18">
        <div class="card chat-card">
          <div class="chat-head">
            <el-icon class="ai-icon"><MagicStick /></el-icon>
            <div>
              <b>智能学习助手</b>
              <div class="small muted">可以讲解知识点、跳转可视化动画、解析代码、诊断薄弱环节</div>
            </div>
            <el-tag v-if="lastMode === 'fallback'" type="info" size="small" effect="light">本地知识库模式</el-tag>
            <el-tag v-else-if="lastMode && lastMode !== 'guard' && lastMode !== 'local'" type="success" size="small" effect="light">大模型模式</el-tag>
            <el-tag v-if="sessionId" size="small" effect="plain">多轮会话 #{{ sessionId }}</el-tag>
          </div>

          <div class="msg-list" ref="msgBox">
            <div v-if="!messages.length" class="welcome">
              <h3>你好，{{ userName }} 👋</h3>
              <p class="muted">我可以帮你搞懂四大专业课的抽象原理，试试下面的问题：</p>
              <div class="quick-grid">
                <div v-for="q in quickQuestions" :key="q" class="quick-item" @click="input = q; send()">
                  {{ q }}
                </div>
              </div>
              <p class="small muted" style="margin-top:14px">
                也可以直接粘贴一段算法代码，我会解析它并打开对应的可视化动画。
              </p>
            </div>

            <div v-for="(m, i) in messages" :key="i" class="msg" :class="m.role">
              <el-avatar :size="30" class="avatar" :style="{ background: m.role === 'user' ? '#8b95a3' : 'var(--brand)' }">
                {{ m.role === 'user' ? '我' : 'AI' }}
              </el-avatar>
              <div class="bubble">
                <el-tag
                  v-if="m.intentTag" size="small" effect="light"
                  :type="m.intentTag.type" style="margin-bottom:6px"
                >{{ m.intentTag.text }}</el-tag>
                <!-- 思考过程：先让用户看到"依据是什么"，再给结论 -->
                <div v-if="m.role === 'ai' && m.reasoning && m.reasoning.length" class="think-box">
                  <div class="think-head" @click="toggleThink(i)">
                    <span class="think-icon">🤔</span>
                    <span>思考过程（{{ m.reasoning.length }} 步）</span>
                    <span class="small muted">{{ m.thinkOpen ? '收起' : '展开' }}</span>
                  </div>
                  <ol v-show="m.thinkOpen" class="think-list">
                    <li v-for="(r, ri) in m.reasoning" :key="ri">
                      <b>{{ r.title }}</b>
                      <span class="small muted"> — {{ r.detail }}</span>
                    </li>
                  </ol>
                </div>
                <!-- 任务拆解：先告诉学生"我打算怎么答"，再给结论 -->
                <div v-if="m.role === 'ai' && m.plan && m.plan.length" class="agent-panel">
                  <div class="panel-head" @click="togglePanel(i, 'planOpen')">
                    <span>🧭 任务拆解（{{ m.plan.length }} 步）</span>
                    <span class="small muted">{{ m.planOpen ? '收起' : '展开' }}</span>
                  </div>
                  <ol v-show="m.planOpen" class="plan-list">
                    <li v-for="p in m.plan" :key="p.id">
                      <span class="plan-dot" :class="p.status"></span>
                      <b>{{ p.title }}</b>
                      <span class="small muted"> — {{ p.detail }}</span>
                      <span v-if="p.tool" class="plan-tool">
                        {{ toolLabel(p.tool) }}<span v-if="p.ms"> · {{ p.ms }}ms</span>
                      </span>
                    </li>
                  </ol>
                </div>
                <!-- 工具时间线：这次真的调了哪些工具，一目了然 -->
                <div v-if="m.role === 'ai' && m.toolCalls && m.toolCalls.length" class="tool-timeline">
                  <span
                    v-for="(c, ci) in m.toolCalls" :key="ci"
                    class="tool-chip" :class="{ fail: !c.ok }"
                    :title="c.summary || ''"
                  >
                    <span class="chip-dot">{{ c.ok ? '✓' : '✕' }}</span>
                    {{ c.label || c.name }} · {{ c.ms }}ms
                  </span>
                </div>

                <div v-if="m.role === 'user'" class="msg-text">{{ m.content }}</div>
                <div v-else class="markdown-body msg-text" v-html="render(m.content)"></div>
                <!-- 打字光标：正在接收流式内容时给出"还在写"的信号 -->
                <span v-if="m.typing" class="type-caret"></span>

                <!-- 来源标注：答案依据哪几个知识点，可点回去核对 -->
                <div v-if="m.role === 'ai' && m.sources && m.sources.length" class="src-box">
                  <b class="small">参考来源：</b>
                  <el-tag
                    v-for="s in m.sources" :key="s.knowledgeId || s.name"
                    size="small" effect="plain" class="src-tag" @click="gotoSource(s)"
                  >{{ s.course ? s.course + ' / ' : '' }}{{ s.name }}</el-tag>
                </div>

                <!-- Agent 动作指令 -->
                <div v-if="m.actions && m.actions.length" class="action-row">
                  <el-button
                    v-for="(a, ai) in m.actions" :key="ai"
                    size="small" :type="a.type === 'navigate' ? 'primary' : 'success'"
                    :plain="a.type !== 'navigate'"
                    @click="doAction(a)"
                  >
                    <el-icon><component :is="a.type === 'navigate' ? 'VideoPlay' : 'EditPen'" /></el-icon>
                    {{ a.label }}
                  </el-button>
                </div>
                <div v-if="m.weakPoints && m.weakPoints.length" class="weak-box">
                  <b class="small">薄弱知识点：</b>
                  <el-tag v-for="w in m.weakPoints" :key="w.knowledge_id || w.id" size="small" type="danger" effect="light" style="margin-right:6px">
                    {{ w.name }}（错 {{ w.wrong_count }} 次）
                  </el-tag>
                </div>
                <!-- 语义记忆召回：让"我记得你以前栽过这里"这件事看得见 -->
                <div v-if="(m.relatedMemory || []).length" class="rel-box">
                  <b class="small">你以前在这里栽过：</b>
                  <div v-for="r in m.relatedMemory" :key="r.id" class="rel-item">
                    <el-tag size="small" effect="plain" :type="r.kind === 'wrong' ? 'danger' : 'info'">
                      {{ r.kind === 'wrong' ? '错过' : '问过' }}
                    </el-tag>
                    <span class="small">{{ r.excerpt }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="waitingFirstChar" class="msg ai">
              <el-avatar :size="30" class="avatar" style="background:var(--brand)">AI</el-avatar>
              <div class="bubble">
                <div class="typing"><span></span><span></span><span></span></div>
                <div class="small muted">正在检索知识库并思考…</div>
              </div>
            </div>
          </div>

          <div class="input-area">
            <el-input
              v-model="input" type="textarea" :rows="3" resize="none"
              placeholder="输入你的问题，或粘贴一段算法代码（Ctrl + Enter 发送）"
              @keydown.ctrl.enter="send"
            />
            <div class="input-foot">
              <div class="chips">
                <el-tag
                  v-for="q in quickQuestions.slice(0, 3)" :key="q"
                  size="small" effect="plain" class="chip" @click="input = q"
                >{{ q }}</el-tag>
                <el-tag size="small" type="warning" effect="plain" class="chip" @click="fillCode">粘贴示例代码</el-tag>
              </div>
              <el-button v-if="loading" type="danger" plain @click="stopStream">
                停止 <el-icon><CircleClose /></el-icon>
              </el-button>
              <el-button type="primary" :loading="loading" :disabled="!input.trim()" @click="send">
                发送 <el-icon><Promotion /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Agent 工具箱：能看到助手有哪些工具，也可以单独跑一次 -->
    <el-drawer v-model="toolboxVisible" title="Agent 工具箱" size="430px">
      <div class="drawer-box">
        <div v-for="t in capabilityTools" :key="t.name" class="tool-card">
          <div class="tool-card-head">
            <b>{{ t.label }}</b>
            <code class="small muted">{{ t.name }}</code>
          </div>
          <div class="small muted">{{ t.desc }}</div>
          <div class="tool-card-foot">
            <el-button
              size="small" type="primary" plain
              :loading="toolRunning === t.name" @click="runTool(t)"
            >运行一次</el-button>
            <span v-if="toolResults[t.name]" class="small muted">{{ toolResults[t.name].summary }}</span>
          </div>
          <pre v-if="toolResults[t.name] && toolResults[t.name].text" class="tool-result">{{ toolResults[t.name].text }}</pre>
        </div>
        <el-empty v-if="!capabilityTools.length" description="后端未返回工具清单" :image-size="60" />
      </div>
    </el-drawer>

    <!-- 记忆与设置：回答风格 / 记忆开关 / 记住了什么 -->
    <el-drawer v-model="memoryVisible" title="记忆与设置" size="430px">
      <div class="drawer-box" v-loading="memoryLoading">
        <div class="panel-title">回答设置</div>
        <div class="set-row">
          <span>回答风格</span>
          <el-radio-group v-model="style" size="small">
            <el-radio-button value="concise">简洁</el-radio-button>
            <el-radio-button value="standard">标准</el-radio-button>
            <el-radio-button value="detailed">详细</el-radio-button>
          </el-radio-group>
        </div>
        <div class="set-row">
          <span>使用对话记忆</span>
          <el-switch v-model="useMemory" />
        </div>
        <div class="small muted">关掉后每次提问都当成全新问题，不会被上一轮的话题牵着走。</div>

        <el-divider />
        <div class="panel-title">用户画像</div>
        <div class="portrait-grid">
          <div class="stat-card">
            <div class="stat-num">{{ memory.portrait?.studyDays ?? 0 }}</div>
            <div class="small muted">学习天数</div>
          </div>
          <div class="stat-card">
            <div class="stat-num">{{ memory.portrait?.accuracy ?? 0 }}%</div>
            <div class="small muted">答题正确率</div>
          </div>
          <div class="stat-card">
            <div class="stat-num">{{ memory.portrait?.answerTotal ?? 0 }}</div>
            <div class="small muted">累计答题</div>
          </div>
          <div class="stat-card">
            <div class="stat-num">{{ memory.portrait?.chatCount ?? 0 }}</div>
            <div class="small muted">提问次数</div>
          </div>
        </div>
        <div v-if="(memory.portrait?.favoriteCourses || []).length" class="small muted" style="margin-top:8px">
          常问课程：{{ memory.portrait.favoriteCourses.map(c => c.courseName).join('、') }}
        </div>

        <el-divider />
        <div class="panel-title">短期记忆（最近 {{ (memory.shortTerm || []).length }} 轮）</div>
        <div v-for="s in (memory.shortTerm || [])" :key="s.id" class="mem-item">
          <div class="mem-q">{{ s.question }}</div>
          <div class="small muted">{{ s.answer }}</div>
        </div>
        <el-empty v-if="!(memory.shortTerm || []).length" description="还没有对话记忆" :image-size="50" />

        <el-divider />
        <div class="panel-title">长期记忆</div>
        <div v-if="(memory.longTerm?.weakPoints || []).length" style="margin-bottom:8px">
          <div class="small">薄弱知识点</div>
          <el-tag v-for="w in memory.longTerm.weakPoints" :key="w.id" size="small" type="danger" effect="light" style="margin:4px 6px 0 0">
            {{ w.name }}（错 {{ w.wrongCount }} 次）
          </el-tag>
        </div>
        <div v-if="(memory.longTerm?.strongPoints || []).length">
          <div class="small">掌握较好</div>
          <el-tag v-for="w in memory.longTerm.strongPoints" :key="w.id" size="small" type="success" effect="light" style="margin:4px 6px 0 0">
            {{ w.name }}（对 {{ w.correctCount }} 次）
          </el-tag>
        </div>
        <el-empty v-if="!memory.longTerm" description="暂无长期记忆" :image-size="50" />

        <!-- 语义记忆：按"意思相近"召回的旧笔记，是聚合统计给不出来的那一半 -->
        <el-divider />
        <div class="panel-title">
          语义记忆
          <span class="small muted" style="margin-left:6px">
            {{ (memory.semantic?.noteCount) || 0 }} 条 · {{ semanticModeLabel }}
          </span>
        </div>
        <div class="small muted" style="margin-bottom:6px">
          记住的是「你错过的具体内容」，不只是「错了几次」。
        </div>
        <div v-for="r in (memory.longTerm?.related || [])" :key="r.id" class="mem-item">
          <div class="mem-q">
            <el-tag size="small" effect="plain" :type="r.kind === 'wrong' ? 'danger' : 'info'">
              {{ r.kind === 'wrong' ? '错过' : '问过' }}
            </el-tag>
            {{ r.title || r.excerpt.slice(0, 24) }}
          </div>
          <div class="small muted">{{ r.excerpt }}</div>
        </div>
        <el-empty v-if="!(memory.longTerm?.related || []).length" description="还没有相关的记忆" :image-size="50" />

        <el-divider />
        <el-button type="danger" plain style="width:100%" @click="clearMemory">清空对话记忆</el-button>
        <div class="small muted" style="margin-top:6px">
          只清对话记录；答题与错题属于真实学习档案，不会一起删掉。
        </div>
      </div>
    </el-drawer>

    <!-- 个性化学习报告 -->
    <el-dialog v-model="reportVisible" title="我的个性化学习报告" width="720px" top="6vh">
      <div v-if="reportData" class="report-box">
        <el-row :gutter="12" class="stat-row">
          <el-col :xs="12" :sm="12" :md="6" :lg="6" v-for="s in reportStatCards" :key="s.label">
            <div class="stat-card">
              <div class="stat-num">{{ s.value }}</div>
              <div class="small muted">{{ s.label }}</div>
            </div>
          </el-col>
        </el-row>
        <el-divider />
        <div v-if="reportData.weakPoints && reportData.weakPoints.length">
          <b>薄弱知识点 TOP{{ reportData.weakPoints.length }}</b>
          <div class="weak-list">
            <div v-for="w in reportData.weakPoints" :key="w.id" class="weak-row">
              <span>{{ w.name }}</span>
              <el-tag size="small" type="danger" effect="light">错 {{ w.wrongCount }} 次</el-tag>
              <el-button size="small" text type="primary" @click="gotoKnowledge(w)">去复习</el-button>
            </div>
          </div>
        </div>
        <el-empty v-else description="还没有错题记录，继续保持！" :image-size="60" />
        <el-divider />
        <div ref="reportBox" class="markdown-body" v-html="render(reportMarkdown)"></div>
      </div>
      <el-empty v-else description="暂无学习数据" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { agentApi, learnApi } from '@/api'
import { useUserStore } from '@/stores/user'
import { renderMd, hydrateRich } from '../utils/markdown'
import { streamPost, useTypewriter } from '../utils/sse'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, DataLine, Clock, CircleClose, Grid } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const store = useUserStore()
const userName = computed(() => store.userInfo?.realName || '同学')

const input = ref('')
const messages = ref([])
const loading = ref(false)
const sessions = ref([])
const sessionId = ref(null)
const tools = ref([])
const lastMode = ref('')
const msgBox = ref()
// 当前正在进行的流式请求，用户点「停止」时可以掐断
let currentStream = null

// 学习报告
const reportVisible = ref(false)
const reportLoading = ref(false)
const reportData = ref(null)
const reportMarkdown = ref('')
const reportBox = ref()

const INTENT_TAGS = {
  privacy: { type: 'danger', text: '已拒绝：涉及隐私信息' },
  injection: { type: 'danger', text: '已拒绝：越权/指令请求' },
  greeting: { type: 'info', text: '闲聊' },
  chitchat: { type: 'info', text: '闲聊' },
  encourage: { type: 'warning', text: '鼓励' },
  quiz: { type: 'success', text: '出题练习' },
  draw: { type: 'success', text: '流程图' },
  plan: { type: 'success', text: '学习计划' },
  wrong_review: { type: 'warning', text: '错题整理' },
  formula: { type: 'success', text: '公式讲解' },
  diagnose: { type: 'warning', text: '薄弱点诊断' },
  report: { type: 'warning', text: '学习报告' },
  code: { type: 'success', text: '代码解析' }
}

// 工具箱 / 记忆 / 设置
const toolboxVisible = ref(false)
const memoryVisible = ref(false)
const capabilityTools = ref([])
const toolResults = ref({})
const toolRunning = ref('')
const memory = ref({})
const memoryLoading = ref(false)
// standard 不传给后端（后端默认就是标准篇幅），只有简洁/详细才需要额外指令
const style = ref('standard')
const useMemory = ref(true)

const TOOL_LABELS = {
  kb_search: '知识库检索',
  code_run: '代码执行',
  render_formula: '公式渲染',
  draw_diagram: '流程图',
  quiz_generate: '习题生成',
  wrong_record: '错题记录',
  study_plan: '学习计划'
}
function toolLabel(name) {
  return TOOL_LABELS[name] || name
}

const reportStatCards = computed(() => {
  const d = reportData.value
  if (!d) return []
  // 注意：后端 accuracy 已经是 0~100 的百分数（不是 0~1 的比例）。
  // 早先这里又乘了一次 100，导致 68% 显示成 6800%，这次一并纠正。
  return [
    { label: '答题总数', value: d.answerTotal ?? 0 },
    { label: '正确率', value: (d.accuracy != null ? d.accuracy : 0) + '%' },
    { label: '错题知识点', value: d.wrongKnowledgeCount ?? d.wrongCount ?? 0 },
    { label: '学习天数', value: d.studyDays ?? 0 }
  ]
})

const quickQuestions = [
  '讲讲 TCP 三次握手的完整过程',
  '快速排序的时间复杂度是多少？',
  '我哪些知识点比较薄弱？',
  '帮我对比 LRU 和 FIFO 页面置换算法',
  '中心极限定理到底在说什么？',
  '特征值的几何意义是什么？'
]

/** 「其他模块敬请期待」清单：占住侧栏左下角空白，给后续迭代留位置 */
const SOON_MODULES = [
  '课程笔记与思维导图',
  '历年真题与模拟考',
  '学习小组与讨论区',
  '错题智能归因分析'
]

/** 能力清单默认折叠：8 项全展开在 800px 高的屏上会把侧栏顶出视口，
 *  只露前 4 项 + 「展开全部」，左下角的期待卡片才始终有位置 */
const toolsOpen = ref(false)

function render(text) {
  return renderMd(text)
}

/**
 * 公式 / 流程图要在 v-html 落地之后才能渲染（KaTeX 与 Mermaid 都要操作真实 DOM）。
 * 流式输出时正文每 18ms 变一次，逐帧 hydrate 会疯狂重建节点，
 * 所以攒一个 150ms 的防抖，在一句话落地后再统一排版。
 */
let hydrateTimer = null
let hydrating = false
function scheduleHydrate(root) {
  // 打字机每 18ms 写一次，这里每次写都重排定时器 ——
  // 于是真正执行总是在「最后一次写入之后 150ms」，也就是整段话落地之后。
  // 只挂在 onDone 上是不够的：done 事件到达时打字机可能还有半屏字没吐完，
  // 那时 hydrate 会漏掉后半段里的公式与流程图。
  clearTimeout(hydrateTimer)
  hydrateTimer = setTimeout(async () => {
    await nextTick()
    if (hydrating) return
    hydrating = true
    try {
      await hydrateRich(root || msgBox.value)
    } finally {
      hydrating = false
    }
  }, 150)
}

/** 展开/收起某条回复里的面板（任务拆解等） */
function togglePanel(i, key) {
  const m = messages.value[i]
  if (m) m[key] = !m[key]
}

function gotoSource(s) {
  if (s && s.route) router.push(s.route)
  else if (s && s.knowledgeId) router.push('/knowledge/' + s.knowledgeId)
}
function formatTime(t) {
  if (!t) return ''
  const d = new Date(t)
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

/** 流式请求还在等待第一个字时，才显示"正在检索…"的占位气泡 */
const waitingFirstChar = computed(() => {
  if (!loading.value) return false
  const last = messages.value[messages.value.length - 1]
  return !(last && last.role === 'ai')
})

/** 流式失败时降级：走一次性接口，保证用户一定拿得到答案。
 *  注意：即使是一次性拿到的整段文本，也要过打字机逐字吐出来 ——
 *  否则同一个助手里「流式时有打字效果、降级时整段糊上来」，
 *  用户会觉得功能坏了。观感一致比"省一点渲染"重要。 */
async function sendSync(payload) {
  try {
    const res = await agentApi.chat(payload)
    if (res.code !== 200) {
      ElMessage.error(res.message || '助手暂时无法回答')
      return
    }
    const d = res.data
    if (d.sessionId) sessionId.value = d.sessionId
    messages.value.push({
      role: 'ai',
      content: '',
      actions: d.actions || [],
      weakPoints: d.weakPoints || [],
      reasoning: d.reasoning || [],
      plan: d.plan || [],
      toolCalls: d.toolCalls || [],
      sources: d.sources || [],
      planOpen: true,
      thinkOpen: true,
      intentTag: INTENT_TAGS[d.intent] || null,
      typing: true
    })
    const box = messages.value[messages.value.length - 1]
    const tw = useTypewriter(() => box.content, v => { box.content = v; scrollBottom(); scheduleHydrate() })
    tw.push(d.answer || '')
    tw.finish()
    lastMode.value = d.mode
    scheduleHydrate()
    if (d.knowledge && d.actions && d.actions.length) autoJump(d)
    loadSessions()
  } catch (e) {
    ElMessage.error('无法连接服务')
  }
}

async function send() {
  const q = input.value.trim()
  if (!q || loading.value) return

  messages.value.push({ role: 'user', content: q })
  input.value = ''
  loading.value = true
  scrollBottom()

  const payload = {
    question: q,
    sessionId: sessionId.value,
    history: messages.value.slice(-9, -1).map(m => ({ role: m.role === 'user' ? 'user' : 'assistant', content: m.content })),
    // 设置项随提问一起下发：后端据此调整 system 指令与是否读取历史
    style: style.value === 'standard' ? undefined : style.value,
    useMemory: useMemory.value
  }

  // 先落一条空的 AI 气泡，正文到了往里灌 —— 不要让用户盯着"思考中"干等
  messages.value.push({
    role: 'ai', content: '', actions: [], weakPoints: [], reasoning: [],
    plan: [], toolCalls: [], sources: [],
    thinkOpen: true, planOpen: true, intentTag: null, typing: false
  })
  scrollBottom()
  // 必须操作 reactive 代理本身，改原始对象不会触发视图更新
  const box = messages.value[messages.value.length - 1]

  const tw = useTypewriter(() => box.content, v => { box.content = v; scrollBottom(); scheduleHydrate() })

  let settled = false
  const settle = mode => {
    if (settled) return
    settled = true
    box.typing = false
    if (mode) lastMode.value = mode
    loading.value = false
    currentStream = null
    scrollBottom()
  }

  currentStream = streamPost('/api/agent/chat/stream', payload, {
    onMeta: m => {
      if (m.sessionId) sessionId.value = m.sessionId
      box.actions = m.actions || []
      box.weakPoints = m.weakPoints || []
      box.relatedMemory = m.relatedMemory || []
      box.reasoning = m.reasoning || []
      // 计划与工具调用先于正文到达：时间线先画出来，正文再逐字冒
      box.plan = m.plan || []
      box.toolCalls = m.toolCalls || []
      box.sources = m.sources || []
      box.intentTag = INTENT_TAGS[m.intent] || null
      if (m.report) {
        reportData.value = m.report
        // 报告随 meta 一次性到达，但也让它逐字展开 ——
        // 否则「正文在打字、报告整段闪出来」，同一屏两种节奏很割裂
        reportMarkdown.value = ''
        const rtw = useTypewriter(() => reportMarkdown.value, v => { reportMarkdown.value = v; scheduleHydrate(reportBox.value) })
        rtw.push(m.report.markdown || '')
        rtw.finish()
        scheduleHydrate(reportBox.value)
      }
      if (m.knowledge && m.actions && m.actions.length) autoJump({ knowledge: m.knowledge, actions: m.actions })
      scrollBottom()
    },
    onDelta: t => { box.typing = true; tw.push(t) },
    // 输出校验拦截：正文已经吐出去一部分，用安全话术整段覆盖
    onReplace: r => {
      tw.stop()
      box.content = r.content || '这条回答包含不安全内容，已被系统拦截。'
      box.typing = false
      if (r.issues && r.issues.length) ElMessage.warning('已拦截：' + r.issues[0])
      scrollBottom()
    },
    onDone: d => {
      tw.finish()
      scheduleHydrate()
      // 兜底：一次都没吐出正文就结束了，不能留一个空气泡让人以为「回答了但没显示」。
      // 历史上这个坑是真的 —— Python 后端 delta 帧送的是 text、前端读 content，
      // 于是思考过程正常渲染、回答却是空白，用户看到的就是「问了没反应」。
      if (!String(box.content || '').trim()) {
        box.content = '这次没有拿到有效回答。可以换个说法再问一次，或确认后端是否已启动。'
      }
      settle(d && d.mode)
      loadSessions()
    },
    onAbort: () => {
      tw.stop()
      if (!String(box.content || '').trim()) messages.value.pop()
      settle()
    },
    onError: async err => {
      tw.stop()
      console.warn('[agent] 流式失败，降级为一次性接口：', err && err.message)
      messages.value.pop() // 丢掉空气泡，避免留下一条"空气泡"
      await sendSync(payload)
      settle()
    }
  })
}

/** 停止本次生成 */
function stopStream() {
  if (currentStream) currentStream.abort()
  currentStream = null
  loading.value = false
  const last = messages.value[messages.value.length - 1]
  if (last && last.role === 'ai') last.typing = false
}

/** Agent 联动：写入待执行动作，弹窗确认或直接跳转 */
function autoJump(d) {
  const nav = d.actions.find(a => a.type === 'navigate')
  if (nav) store.setPendingAction(nav)
}

function doAction(a) {
  if (!a.route) return
  router.push(a.route)
}

/** 工具箱：单独跑一次工具，验证它到底输出了什么 */
async function openToolbox() {
  toolboxVisible.value = true
  if (capabilityTools.value.length) return
  try {
    const res = await agentApi.capabilities()
    capabilityTools.value = (res.data || {}).tools || []
  } catch (e) { /* 抽屉里已有空状态提示 */ }
}

async function runTool(t) {
  const q = input.value.trim()
  const args = {}
  if (t.name === 'kb_search') args.query = q || '快速排序'
  else if (t.name === 'quiz_generate') args.count = 3
  else if (t.name === 'wrong_record') { args.action = 'list'; args.limit = 5 }
  else if (t.name === 'study_plan') args.days = 7
  else if (t.name === 'draw_diagram') args.topic = q || 'TCP 三次握手'
  else if (t.name === 'render_formula') args.latex = q || '\\frac{a}{b}'
  else if (t.name === 'code_run') {
    if (!q) { ElMessage.warning('先在输入框里粘贴一段代码再运行'); return }
    args.code = q
  }

  toolRunning.value = t.name
  try {
    const res = await agentApi.invokeTool({ name: t.name, args })
    if (res.code !== 200) { ElMessage.error(res.message || '调用失败'); return }
    const d = res.data || {}
    const call = d.call || {}
    toolResults.value = {
      ...toolResults.value,
      [t.name]: { summary: call.summary || '', text: briefOf(t.name, d.data) }
    }
  } catch (e) {
    ElMessage.error('工具调用失败')
  } finally {
    toolRunning.value = ''
  }
}

/** 工具结果在抽屉里只露摘要：完整数据（题目、计划、图）会贴在对话里 */
function briefOf(name, data) {
  if (!data) return ''
  if (name === 'kb_search') return (data.docs || []).map(d => `· ${d.course_name || ''}/${d.name}`).join('\n')
  if (name === 'quiz_generate') return (data.questions || []).map(q => `· ${q.title}`).join('\n')
  if (name === 'wrong_record') return (data.items || []).map(w => `· ${w.name}：错 ${w.wrong_count} 次`).join('\n')
  if (name === 'study_plan') return (data.plan || []).map(p => `第${p.day}天 ${p.focus}`).join('\n')
  if (name === 'draw_diagram') return data.code || ''
  if (name === 'render_formula') return data.latex || ''
  if (name === 'code_run') {
    return `语言 ${data.language} · ${data.lines} 行\n`
      + (data.executed ? (data.output || '(无输出)') : (data.reason || '未执行'))
  }
  return JSON.stringify(data).slice(0, 300)
}

const semanticModeLabel = computed(() =>
  (memory.value?.semantic?.mode === 'remote-embedding') ? '语义向量' : '本地语义'
)

async function openMemory() {
  memoryVisible.value = true
  memoryLoading.value = true
  try {
    // 带上输入框里的内容：后端会按它做一次语义召回，列出"和这个问题像"的旧笔记。
    // 没输入时就只展示统计，不浪费一次检索。
    const q = (input.value || '').trim()
    const res = await agentApi.memory(q ? { q } : undefined)
    memory.value = res.data || {}
  } catch (e) {
    ElMessage.error('读取记忆失败')
  } finally {
    memoryLoading.value = false
  }
}

async function clearMemory() {
  try {
    await ElMessageBox.confirm('清空后助手将不再记得你之前问过什么，确定继续吗？', '清空对话记忆', { type: 'warning' })
  } catch (e) {
    return
  }
  await agentApi.clearMemory('chat')
  memory.value = { ...memory.value, shortTerm: [] }
  ElMessage.success('已清空对话记忆')
  loadSessions()
}

/** 展开/收起某条回复的思考过程 */
function toggleThink(i) {
  const m = messages.value[i]
  if (m) m.thinkOpen = !m.thinkOpen
}

function newChat() {
  messages.value = []
  sessionId.value = null
  lastMode.value = ''
}

/** 载入某个历史会话的完整多轮消息 */
async function loadSession(s) {
  sessionId.value = s.id
  messages.value = []
  try {
    const res = await agentApi.sessionMessages(s.id)
    const list = res.data || []
    // 后端返回的是「一轮一条」的记录（question / answer / mode / intent），
    // 而消息区需要 role+content 的扁平结构。早先前端直接读 m.role / m.content，
    // 两个字段都不存在 → 历史会话点开永远是空白，这里按轮次展开。
    const out = []
    for (const m of list) {
      if (m.question) out.push({ role: 'user', content: m.question, actions: [] })
      if (m.answer) {
        out.push({
          role: 'ai',
          content: m.answer,
          actions: [],
          weakPoints: [],
          reasoning: [],
          // 历史消息没有存计划/工具调用（那是当次运行时的过程数据），
          // 但答案里可能带公式与流程图，仍要走一遍 hydrate
          plan: [],
          toolCalls: [],
          sources: [],
          thinkOpen: false,
          planOpen: false,
          intentTag: INTENT_TAGS[m.intent] || null
        })
      }
    }
    messages.value = out
    const lastAi = [...list].reverse().find(m => m.answer)
    lastMode.value = lastAi ? (lastAi.mode || '') : ''
    scheduleHydrate()
    scrollBottom()
  } catch (e) {
    ElMessage.error('载入会话失败')
  }
}

async function removeSession(s) {
  try {
    await ElMessageBox.confirm('确定删除这个会话及其全部消息吗？', '删除会话', { type: 'warning' })
  } catch (e) {
    return
  }
  await agentApi.deleteSession(s.id)
  if (sessionId.value === s.id) newChat()
  loadSessions()
  ElMessage.success('已删除')
}

async function loadSessions() {
  try {
    const res = await agentApi.sessions()
    sessions.value = (res.data || []).slice(0, 30)
  } catch (e) { /* 忽略 */ }
}

/** 生成个性化学习报告 */
async function openReport() {
  reportVisible.value = true
  reportLoading.value = true
  reportData.value = null
  reportMarkdown.value = ''
  try {
    const res = await agentApi.report()
    if (res.code === 200 && res.data) {
      reportData.value = res.data
      reportMarkdown.value = res.data.markdown || ''
      scheduleHydrate(reportBox.value)
    } else {
      ElMessage.error(res.message || '暂无学习数据')
    }
  } catch (e) {
    ElMessage.error('生成报告失败')
  } finally {
    reportLoading.value = false
  }
}

function gotoKnowledge(w) {
  reportVisible.value = false
  if (w && w.id) router.push('/knowledge/' + w.id)
}

function fillCode() {
  input.value = `#include <stdio.h>\nvoid quickSort(int a[], int l, int r) {\n    if (l >= r) return;\n    int i = l, j = r, pivot = a[l];\n    while (i < j) {\n        while (i < j && a[j] >= pivot) j--;\n        a[i] = a[j];\n        while (i < j && a[i] <= pivot) i++;\n        a[j] = a[i];\n    }\n    a[i] = pivot;\n    quickSort(a, l, i - 1);\n    quickSort(a, i + 1, r);\n}`
}

function scrollBottom() {
  nextTick(() => {
    if (msgBox.value) msgBox.value.scrollTop = msgBox.value.scrollHeight
  })
}

onMounted(async () => {
  await loadSessions()
  const t = await agentApi.tools()
  tools.value = t.data || []
  // 预热工具清单：点开工具箱时不用再等一次请求
  agentApi.capabilities().then(r => { capabilityTools.value = (r.data || {}).tools || [] }).catch(() => {})
  if (route.query.q) {
    input.value = String(route.query.q)
    send()
  }
})
</script>

<style scoped>
.agent-page { max-width: 1280px; }
.side {
  padding: 14px; height: calc(100vh - 120px);
  display: flex; flex-direction: column;
  /* 内容超出时侧栏自身滚动，而不是被裁掉半行 ——
     早期这里没写 overflow，导致「Agent 能力」条目被容器切一半，看着像文字压到盒子上 */
  overflow-y: auto;
}
.side-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
/* min-height:0：flex 子项默认 min-height:auto，不加这句它不肯缩到内容以下，
   侧栏就会整体溢出而不是让 .hist-list 自己滚动 */
.hist-list { flex: 1; min-height: 0; overflow-y: auto; }
.hist-item {
  padding: 8px 10px; border-radius: 8px; cursor: pointer; margin-bottom: 4px; transition: background .2s;
}
.hist-item:hover { background: var(--bg); }
.hist-item.active { background: var(--brand-light); }
.hist-q { font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: flex; align-items: center; gap: 4px; }
.hist-ico { color: var(--text-3); flex-shrink: 0; }
.tools-box { flex-shrink: 0; }
.panel-title { font-size: 13px; font-weight: 600; margin-bottom: 6px; color: var(--text-2); display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.tools-toggle { padding: 0; font-size: 12px; flex-shrink: 0; }
.tool-item { margin-bottom: 8px; }
.tool-item b { font-size: 12px; }

/* 能力清单折叠：只留前 4 项。
   用 nth-child 隐藏而不是 max-height 写死像素 —— 条目高度会随 desc 换行变化，
   写死 max-height 会出现「最后一项被切成半行」，正是任务九那种文字被裁的观感。 */
.tools-list.collapsed .tool-item:nth-child(n+5) { display: none; }

/* 「其他模块敬请期待」：贴在侧栏最底部。
   .hist-list 已是 flex:1，会吃掉所有剩余高度把这个卡片顶到底部，
   所以无论会话列表多长，卡片都稳稳待在左下角，不留空白。 */
.soon-card {
  flex-shrink: 0; margin-top: 12px; padding: 12px 13px;
  border: 1px dashed var(--brand-3); border-radius: 10px;
  background: linear-gradient(150deg, var(--brand-light) 0%, var(--card) 72%);
  display: flex; flex-direction: column; gap: 8px;
}
.soon-head { display: flex; align-items: center; gap: 6px; font-size: 13px; color: var(--brand); }
.soon-head .el-icon { font-size: 15px; }
.soon-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 6px; }
.soon-list li {
  display: flex; align-items: center; gap: 7px;
  font-size: 12px; color: var(--text-2); line-height: 1.5;
}
.soon-dot {
  width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0;
  background: var(--brand-2); opacity: .8;
}

/* 矮屏（笔记本半屏 / 横屏手机）：侧栏高度是 100vh - 120px，
   能力清单再露 4 项就会把期待卡片顶出视口，这里再收一档 */
@media (max-height: 700px) and (min-width: 992px) {
  .tools-list.collapsed .tool-item:nth-child(n+3) { display: none; }
}

.chat-card { padding: 0; height: calc(100vh - 120px); display: flex; flex-direction: column; }
.chat-head {
  display: flex; align-items: center; gap: 12px; padding: 14px 18px;
  border-bottom: 1px solid var(--border);
}
.ai-icon { font-size: 22px; color: var(--brand); }
.chat-head b { font-size: 15px; }
.msg-list { flex: 1; overflow-y: auto; padding: 18px; background: var(--bg); }
.welcome { text-align: center; padding: 20px 0; }
.welcome h3 { margin: 0 0 6px; }
/* min(100%, 190px)：极窄屏（折叠屏外屏）自动退成单列，不会溢出 */
.quick-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 190px), 1fr)); gap: 10px; margin-top: 16px; }
.quick-item {
  border: 1px solid var(--border); border-radius: 8px; padding: 10px 14px; cursor: pointer;
  font-size: 13px; background: var(--card); transition: all .2s; text-align: left;
}
.quick-item:hover { border-color: var(--brand); background: var(--brand-light); }

.msg { display: flex; gap: 10px; margin-bottom: 16px; }
.avatar { flex-shrink: 0; }
.bubble { max-width: 78%; }
.msg-text {
  background: var(--soft-bg); border: 1px solid var(--border); border-radius: 10px; padding: 12px 14px;
  font-size: 14px; line-height: 1.8; word-break: break-word;
}
.msg.user { flex-direction: row-reverse; }
.msg.user .bubble { display: flex; flex-direction: column; align-items: flex-end; }
.msg.user .msg-text { background: var(--brand); color: #fff; border-color: var(--brand); }
.action-row { display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap; }
.weak-box { margin-top: 8px; }
/* 语义记忆召回：与"薄弱知识点"区分开 —— 这里展示的是具体内容，不是次数 */
.rel-box {
  margin-top: 8px; padding: 8px 10px; border-radius: 8px;
  background: var(--warning-light); border: 1px solid var(--warn-border);
}
.rel-item {
  display: flex; align-items: flex-start; gap: 6px; margin-top: 4px;
  line-height: 1.6; color: var(--text-2);
}

/* 思考过程：弱化处理，突出"这是推导，不是结论" */
.think-box {
  background: var(--brand-light); border: 1px solid var(--border); border-radius: 8px;
  padding: 8px 12px; margin-bottom: 10px;
}
.think-head {
  display: flex; align-items: center; gap: 8px; cursor: pointer;
  font-size: 12.5px; font-weight: 600; color: var(--brand); user-select: none;
}
.think-icon { font-size: 13px; }
.think-list { margin: 8px 0 2px; padding-left: 18px; }
.think-list li { font-size: 12.5px; line-height: 1.9; color: var(--text-2); }

.typing { display: flex; gap: 4px; margin-bottom: 4px; }
.typing span {
  width: 6px; height: 6px; border-radius: 50%; background: var(--brand-2);
  animation: blink 1.2s infinite;
}
.typing span:nth-child(2) { animation-delay: .2s; }
.typing span:nth-child(3) { animation-delay: .4s; }
@keyframes blink { 0%, 60%, 100% { opacity: .3 } 30% { opacity: 1 } }

/* 流式输出时的打字光标 */
.type-caret {
  display: inline-block; width: 7px; height: 15px; margin-left: 2px;
  vertical-align: text-bottom; background: var(--brand); border-radius: 1px;
  animation: caret 1s steps(2, start) infinite;
}
@keyframes caret { 0%, 100% { opacity: 1 } 50% { opacity: 0 } }

.hist-t { display: flex; align-items: center; justify-content: space-between; }
.del-icon { cursor: pointer; opacity: .55; }
.del-icon:hover { opacity: 1; color: #e05252; }
.report-box { max-height: 62vh; overflow-y: auto; padding-right: 4px; }
.stat-card {
  background: var(--bg); border-radius: 10px; padding: 12px; text-align: center;
  border: 1px solid var(--border);
}
.stat-num { font-size: 20px; font-weight: 700; color: var(--brand); margin-bottom: 2px; }
.weak-row {
  display: flex; align-items: center; gap: 10px; padding: 8px 0;
  border-bottom: 1px dashed #f0f2f6; font-size: 13px;
}
.weak-row span { flex: 1; }

.input-area { border-top: 1px solid var(--border); padding: 12px 18px; }
.input-foot { display: flex; justify-content: space-between; align-items: center; margin-top: 8px; gap: 12px; }
.chips { display: flex; gap: 6px; flex-wrap: wrap; }
.chip { cursor: pointer; }

/* ---- 工具箱 / 记忆 入口 ---- */
.panel-actions { display: flex; gap: 8px; margin-top: 10px; }
.panel-actions .el-button { flex: 1; }

/* ---- 任务拆解 ---- */
.agent-panel {
  background: var(--bg); border: 1px solid var(--border); border-radius: 8px;
  padding: 8px 12px; margin-bottom: 8px;
}
.panel-head {
  display: flex; align-items: center; justify-content: space-between; gap: 8px;
  font-size: 12.5px; font-weight: 600; color: var(--brand); cursor: pointer; user-select: none;
}
.plan-list { margin: 8px 0 2px; padding-left: 16px; }
.plan-list li { font-size: 12.5px; line-height: 1.9; color: var(--text-2); }
.plan-dot {
  display: inline-block; width: 6px; height: 6px; border-radius: 50%;
  margin-right: 6px; vertical-align: middle; background: var(--text-3);
}
.plan-dot.done { background: #3aa675; }
.plan-dot.failed { background: #e05252; }
.plan-tool {
  display: inline-block; margin-left: 6px; padding: 0 6px; border-radius: 4px;
  background: var(--brand-light); color: var(--brand); font-size: 11.5px;
}

/* ---- 工具时间线 ---- */
.tool-timeline { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }
.tool-chip {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 2px 8px; border-radius: 10px; font-size: 11.5px;
  background: var(--brand-light); color: var(--brand); border: 1px solid var(--brand-3);
}
.tool-chip.fail { background: #fdecec; color: #c14646; border-color: #f6c9c9; }
.chip-dot { font-size: 11px; }

/* ---- 来源标注 ---- */
.src-box { margin-top: 8px; }
.src-tag { cursor: pointer; margin: 3px 6px 0 0; }

/* ---- 抽屉内容 ---- */
.drawer-box { padding: 0 4px 20px; }
.tool-card {
  border: 1px solid var(--border); border-radius: 10px; padding: 12px; margin-bottom: 10px;
}
.tool-card-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px; }
.tool-card-foot { display: flex; align-items: center; gap: 10px; margin-top: 8px; flex-wrap: wrap; }
.tool-result {
  margin: 8px 0 0; padding: 8px 10px; background: var(--bg); border-radius: 6px;
  font-size: 12px; line-height: 1.7; white-space: pre-wrap; word-break: break-word;
  max-height: 180px; overflow-y: auto;
}
.set-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; font-size: 13px; }
.portrait-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }
.mem-item { padding: 6px 0; border-bottom: 1px dashed #f0f2f6; }
.mem-q { font-size: 12.5px; font-weight: 600; margin-bottom: 2px; }

/* ---------- 响应式 ----------
   栅格在 md 以下（<992）堆成一列：侧栏此时只给一个可滚动的矮块，
   否则 calc(100vh - 120px) 的满高侧栏会把对话区整块顶到屏幕外。 */
@media (max-width: 991px) {
  .side { height: auto; max-height: 230px; margin-bottom: 12px; }
  .chat-card { height: auto; min-height: 62vh; }
  .msg-list { padding: 14px 12px; }
  .bubble { max-width: 88%; }
  /* 单列时侧栏不再有「贴底」空间，卡片跟着内容流走即可，
     但仍要保证历史列表不会把能力清单和期待卡片挤没 */
  .hist-list { max-height: 96px; flex: none; }
  /* 窄屏侧栏矮，折叠收到 2 项，给期待卡片留位置 */
  .tools-list.collapsed .tool-item:nth-child(n+3) { display: none; }
  .soon-card { margin-top: 10px; }
}
@media (max-width: 600px) {
  .chat-head { padding: 12px 14px; gap: 8px; }
  .chat-head b { font-size: 14px; }
  .input-area { padding: 10px 12px; }
  .input-foot { flex-direction: column; align-items: flex-start; gap: 8px; }
  .side { max-height: 320px; }
  .hist-list { max-height: 76px; }
  .soon-list { flex-direction: row; flex-wrap: wrap; gap: 6px 12px; }
}
</style>
