<template>
  <div class="page code-lab" v-if="lab">
    <el-breadcrumb separator="/" style="margin-bottom:12px">
      <el-breadcrumb-item :to="{ path: '/courses' }">课程中心</el-breadcrumb-item>
      <el-breadcrumb-item v-if="knowledge" :to="{ path: '/knowledge/' + knowledge.id }">
        {{ knowledge.name }}
      </el-breadcrumb-item>
      <el-breadcrumb-item>代码实验室</el-breadcrumb-item>
    </el-breadcrumb>

    <div class="lab-head card">
      <div class="lab-head-text">
        <h2>{{ lab.title }}</h2>
        <p class="muted">{{ lab.desc || (knowledge && knowledge.summary) }}</p>
      </div>
      <div class="head-actions">
        <el-tag type="primary" effect="plain">{{ langName }}</el-tag>
        <!-- 如实标注运行环境来源：内置 = 项目自带的 runtime/，与本机装没装编译器无关 -->
        <el-tag v-if="isWeb" type="success" effect="plain"
                title="HTML / CSS / JavaScript 直接在浏览器里执行，不需要任何编译器，发给别人也能直接跑">
          浏览器内运行
        </el-tag>
        <el-tag v-else-if="envSource === 'bundled'" type="success" effect="plain"
                title="运行环境由项目自带的 runtime/ 提供，换台电脑也不用重装编译器">
          内置编译器
        </el-tag>
        <el-tag v-else-if="envSource === 'system'" type="info" effect="plain"
                title="使用本机已安装的编译器">
          本机环境
        </el-tag>
        <el-button v-if="lab.kid" @click="$router.push('/knowledge/' + lab.kid)">知识点讲解</el-button>
        <el-button v-if="lab.kid" plain @click="$router.push('/practice/' + lab.kid)">做配套练习</el-button>
        <el-button type="primary" plain @click="assistantOpen = !assistantOpen">
          <el-icon><MagicStick /></el-icon>
          {{ assistantOpen ? '收起算法助手' : '打开算法助手' }}
        </el-button>
      </div>
    </div>

    <!-- 语言切换：把同一个概念换一种语言再写一遍，方便横向对比语法差异。
         切过去的同时会把代码换成该语言的等价模板（任务五）。
         任务三：横排按钮组在语言多的时候会把卡片撑爆两行，改成下拉框。 -->
    <div v-if="switchLangs.length" class="lang-switch card">
      <div class="ls-head">
        <el-icon><Switch /></el-icon>
        <div class="ls-title">
          <b>换语言对比</b>
          <span class="small muted">
            同主题「{{ variantLabel }}」的等价写法，切换时自动换上该语言的代码模板
          </span>
        </div>
      </div>
      <div class="ls-picker">
        <el-select
          :model-value="curLang"
          size="default"
          class="ls-select"
          placeholder="选择语言"
          @change="switchLang"
        >
          <el-option
            v-for="l in switchLangs" :key="l"
            :value="l"
            :label="(LANGS[l] && LANGS[l].name) || l"
          >
            <span class="ls-opt">
              <span class="ls-opt-name">{{ (LANGS[l] && LANGS[l].name) || l }}</span>
              <el-tag v-if="l === nativeLang" size="small" type="info" effect="plain" round>本语言</el-tag>
              <span v-else-if="variantLabelOf(l)" class="ls-opt-theme">{{ variantLabelOf(l) }}</span>
            </span>
          </el-option>
        </el-select>
      </div>
      <div v-if="dirtyLangs.length" class="ls-warn small muted">
        <el-icon><WarningFilled /></el-icon>
        当前有 {{ dirtyLangs.length }} 种语言写过代码，切换会覆盖本语言的内容
        <el-button size="small" text type="primary" @click="askOverwrite">知道了，继续切换</el-button>
      </div>
    </div>

    <!-- 布局比例：默认 题目 30% / 编辑器 70%；
         打开算法助手后 编辑器 45% / 助手 25%（题目仍是 30%），
         让「读题 / 写代码 / 问助手」三栏能同时看得见。 -->
    <div class="lab-body" :class="{ 'with-assist': assistantOpen }">
      <!-- 左侧讲解：占 30% -->
      <div class="lab-left card">
        <h3 class="sec-title">要点速记</h3>
        <ul class="point-list">
          <li v-for="(p, i) in lab.points || []" :key="i">{{ p }}</li>
        </ul>

        <template v-if="renderedContent">
          <el-divider />
          <h3 class="sec-title">知识点详解</h3>
          <div class="markdown-body" v-html="renderedContent"></div>
        </template>
      </div>

      <!-- 中间编辑器：默认 70%，开助手后 45%
           编辑器吸顶、运行结果吸底，两块永远同屏（见脚本里的 dock 说明）。 -->
      <div class="lab-mid" :class="{ 'dock-fit': dockFit, 'dock-on': dockOn }" ref="midEl">
        <div class="card ed-card" ref="edEl">
          <CodeEditor
            v-model="code"
            :language="curLang"
            :height="editorHeight"
            :running="running"
            @run="runCode"
          />
        </div>

        <div class="card out-card" ref="outEl" :style="{ '--dock-h': dockH + 'px' }">
          <!-- 收起态：整块结果区压成一条，点一下还原 -->
          <div v-if="dock === 'collapsed'" class="dock-mini" @click="dock = 'normal'">
            <el-icon><ArrowUp /></el-icon>
            <b>运行结果</b>
            <span class="muted small">已收起 · 点击展开</span>
          </div>

          <div class="dock-body" v-show="dock !== 'collapsed'">
            <!-- HTML / CSS / JavaScript 走浏览器沙箱，显示渲染结果 + 捕获到的 console 输出 -->
            <WebPreview
              v-if="isWeb"
              :language="curLang"
              :code="code"
              :demo="demo"
              :run-token="runToken"
            >
              <template #actions>
                <el-button size="small" plain @click="cycleDock">{{ dockBtnLabel }}</el-button>
                <el-button size="small" plain @click="dock = 'collapsed'">
                  <el-icon><ArrowDown /></el-icon> 收起
                </el-button>
              </template>
            </WebPreview>

            <template v-else>
              <div class="out-head">
                <b>运行结果</b>
                <span class="muted small" v-if="result.time">耗时 {{ result.time }} ms</span>
                <span class="head-actions">
                  <el-button size="small" plain @click="clearResult">清空</el-button>
                  <el-button size="small" plain @click="cycleDock">{{ dockBtnLabel }}</el-button>
                  <el-button size="small" plain @click="dock = 'collapsed'">
                    <el-icon><ArrowDown /></el-icon> 收起
                  </el-button>
                </span>
              </div>

              <div v-if="envWarn" class="env-warn">
                <el-icon><WarningFilled /></el-icon>
                <span>{{ envWarn }}</span>
              </div>

              <!-- 控制台：输入与输出同一个黑框（详见 RunConsole 组件注释） -->
              <RunConsole
                ref="consoleEl"
                v-if="!isWeb"
                v-model="stdinText" :code="code"
                :output="result.output || ''" :stderr="result.stderr || ''"
                :error="!!result.error" :time="result.time"
                :running="running" :result-key="runSeq"
                @run="runCode"
              />
            </template>
          </div>
        </div>
      </div>

      <!-- 右侧算法助手：仅在打开时占 25%，不叠加成浮层遮挡代码 -->
      <div v-show="assistantOpen" class="lab-assist card">
        <div class="assist-head">
          <b><el-icon><MagicStick /></el-icon> 算法小助手</b>
          <el-button size="small" text @click="assistantOpen = false">
            <el-icon><DArrowRight /></el-icon> 收起
          </el-button>
        </div>
        <AlgoAssistant :code="code" :language="curLang" />
      </div>
    </div>
  </div>

  <div class="page" v-else>
    <div class="card empty-card">
      <el-empty description="未找到该代码实验室">
        <el-button type="primary" @click="$router.push('/courses')">返回课程中心</el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { renderMd } from '../utils/markdown'
import { WarningFilled, MagicStick, DArrowRight, Switch, ArrowDown, ArrowUp } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import CodeEditor from '@/components/CodeEditor.vue'
import RunConsole from '@/components/RunConsole.vue'
import AlgoAssistant from '@/components/AlgoAssistant.vue'
import WebPreview from '@/components/WebPreview.vue'
import { LABS, LANGS, getLabByRoute, getLabDemo } from '@/data/codeLabs'
import { getVariant, availableLangsFor, themeOf } from '@/data/labVariants'
import { isWebLang } from '@/utils/webSandbox'
import { baseTemplate, pickCode, sortLangs } from '@/utils/codeTemplates'
import { SCOPE, loadDraft, saveDraft, loadStdin, saveStdin } from '@/utils/draftStore'
import { codeApi, courseApi } from '@/api'

const route = useRoute()
const slug = computed(() => route.params.slug)
const lab = computed(() => LABS[slug.value] || getLabByRoute('/code/' + slug.value) || null)

const code = ref('')
const running = ref(false)
const result = ref({})
const knowledge = ref(null)
const env = ref({})
const assistantOpen = ref(false)
const runToken = ref(0)

/* ---------- 跨语言对比（任务四 / 任务五） ----------
   curLang 是「当前正在用的语言」，与 lab.lang（实验原生语言）区分开：
   切换不改路由、不换知识点，只换语言与对应模板。 */
const curLang = ref('c')
/** 每种语言各自的代码缓存：切来切去不会丢用户写的东西 */
const codeByLang = ref({})
/** 当前语言下代码是否被用户改过（有改过就不能无提示覆盖） */
const dirtyLangs = computed(() =>
  Object.keys(codeByLang.value).filter(k => (codeByLang.value[k] || '').trim() &&
    codeByLang.value[k] !== originalOf(k))
)

/** 该实验支持切换的语言（含原生语言），没有跨语言主题时为空数组
 *
 *  统一走 sortLangs：可用语言来自 labVariants.VARIANTS 的键序，
 *  而那些对象的键是按主题分组写的，顺序不保证等于全站语言顺序。
 *  不排的话，同一个下拉在算法题页是 C 打头、这里可能是 Python 打头。 */
const switchLangs = computed(() => {
  if (!lab.value) return []
  const list = availableLangsFor(slug.value)
  if (!list.includes(lab.value.lang)) list.unshift(lab.value.lang)
  return sortLangs(list)
})
/** 该实验的原生语言：下拉里标「本语言」，用户一眼知道自己在读哪份原文 */
const nativeLang = computed(() => (lab.value ? lab.value.lang : ''))
/** 某个候选语言对应的主题名，用于在下拉选项右侧做副标题 */
function variantLabelOf(lang) {
  const v = getVariant(slug.value, lang)
  return v ? v.label : ''
}
const variantLabel = computed(() => {
  const t = themeOf(slug.value)
  if (!t) return ''
  const v = getVariant(slug.value, curLang.value)
  return (v && v.label) || ''
})

/** 某语言的「原始模板」：切回该语言时用它恢复 */
function originalOf(lang) {
  if (!lab.value) return ''
  if (lab.value.lang === lang) return lab.value.code || ''
  const v = getVariant(slug.value, lang)
  return v ? v.code : ''
}

/* 运行输入（stdin）：在线运行没法像真终端那样中途等人敲键盘，
   所以运行前把要喂的数据写好；按「实验 + 语言」落盘，切回来还在。 */
const stdinText = ref('')
let stdinTimer = null
watch(stdinText, v => {
  if (!lab.value || !slug.value) return
  clearTimeout(stdinTimer)
  stdinTimer = setTimeout(() => saveStdin(SCOPE.LAB, slug.value, curLang.value, v), 600)
})

/** 每跑完一次自增 —— 控制台靠它把这一段结果追加到会话流水里 */
const runSeq = ref(0)
const consoleEl = ref(null)

/** 「清空」按钮：结果对象清空的同时把控制台会话也收干净，两者永远一致 */
function clearResult() {
  result.value = {}
  if (consoleEl.value && consoleEl.value.clear) consoleEl.value.clear()
}

/** 编辑器绑到 code 上，用 watch 把它写回按语言的缓存 + 落盘 */
let saveTimer = null
watch(code, v => {
  if (!lab.value) return
  codeByLang.value[curLang.value] = v
  // 落盘做防抖：编辑器每次按键都会触发，逐次写 localStorage 会拖慢输入。
  // 600ms 与算法题页一致 —— 足够短，刷新页面时基本不会丢。
  clearTimeout(saveTimer)
  saveTimer = setTimeout(() => {
    saveDraft(SCOPE.LAB, slug.value, curLang.value, v)
  }, 600)
})

async function askOverwrite() {
  try {
    await ElMessageBox.confirm(
      '切换语言会把这个语言下的代码替换成标准模板，你写的内容将丢失。是否继续？',
      '确认切换语言',
      { type: 'warning', confirmButtonText: '继续切换', cancelButtonText: '再想想' }
    )
    return true
  } catch (e) {
    return false
  }
}

async function switchLang(lang) {
  if (!lab.value || lang === curLang.value) return
  // 当前语言被改过就先确认，避免默默覆盖学生的代码
  if (dirtyLangs.value.includes(curLang.value)) {
    const ok = await askOverwrite()
    if (!ok) return
  }
  /* 切换分三步，顺序不能乱：
   *   1. 先把**当前语言**的代码落盘（内存缓存 + localStorage）——
   *      必须发生在 curLang 改之前，否则存到新语言的键下，旧语言的代码就丢了。
   *      这就是任务三说的「保存切换之前的代码」。
   *   2. 再取目标语言的代码：草稿 > 等价实现 > 基础骨架（pickCode 三级回退）。
   *   3. 最后才改 curLang。 */
  clearTimeout(saveTimer)
  const from = curLang.value
  codeByLang.value[from] = code.value
  saveDraft(SCOPE.LAB, slug.value, from, code.value)
  clearTimeout(stdinTimer)
  saveStdin(SCOPE.LAB, slug.value, from, stdinText.value)
  stdinText.value = loadStdin(SCOPE.LAB, slug.value, lang) || ''

  const variantCode = lab.value.lang === lang ? lab.value.code : (getVariant(slug.value, lang) || {}).code
  const cached = codeByLang.value[lang] || loadDraft(SCOPE.LAB, slug.value, lang)
  const next = pickCode(lang, cached, variantCode)

  curLang.value = lang
  code.value = next
  if (next) codeByLang.value[lang] = next
  clearResult()                 // 换语言 = 换一段代码，上一语言的输出不该留在新语言的控制台里
  runToken.value += 1
  // 三种结果分别给不同提示：恢复草稿 / 换成等价实现 / 只给了基础骨架
  if (cached && cached.trim()) {
    ElMessage.success(`已切换到 ${langLabel(lang)}，恢复你之前写的代码`)
  } else if (variantCode && variantCode.trim()) {
    ElMessage.success(`已切换到 ${langLabel(lang)}，代码模板同步替换`)
  } else {
    ElMessage.success(`已切换到 ${langLabel(lang)}，已载入基础模板`)
  }
}

function langLabel(lang) {
  return (LANGS[lang] && LANGS[lang].name) || (lang || '').toUpperCase()
}

/* ---------- 编辑器吸顶 + 结果面板吸底 ----------
   左列「要点速记 / 知识点详解」经常很长，页面一滚编辑器就跑没影了，
   运行结果更是要滚到页面下半截才看得到 —— 写一行代码来回滚两趟。
   所以这里把中列做成上下两端固定：
     · 编辑器 sticky top   → 永远贴在顶栏下方；
     · 结果面板 sticky bottom → 永远贴在视口底部。
   两者合起来刚好吃掉一屏，中间不留空白：编辑器高度按「视口 − 面板」算出来。

   为什么不是整栏 sticky（上一版做法）也不是 fixed：
     · 整栏 sticky 要塞进 100vh，塞不下就得压缩结果区，看输出还要在小框里滚一次；
     · fixed 会脱离文档流压住左列和页脚，正是之前「挡住底部栏」的根因。
   sticky 元素仍在文档流里、且被限制在父容器（.lab-mid）内，
   滚到页面底部时 .lab-mid 到底了，面板就停回自然位置，页脚照常露出来。 */
const midEl = ref(null)
const edEl = ref(null)
const outEl = ref(null)

/** 视口尺寸做成响应式 ref：高度分配全靠它，resize 要能触发重算 */
const vw = ref(typeof window === 'undefined' ? 1440 : window.innerWidth)
const vh = ref(typeof window === 'undefined' ? 900 : window.innerHeight)

/** 结果面板三档：常规 / 放大 / 收起 */
const dock = ref('normal')
const dockBtnLabel = computed(() =>
  dock.value === 'collapsed' ? '展开' : dock.value === 'expanded' ? '还原' : '放大'
)
function cycleDock() {
  dock.value = dock.value === 'collapsed' ? 'normal' : dock.value === 'expanded' ? 'normal' : 'expanded'
}

/** 卡片外壳高度：编辑器卡 = 代码区 + 工具条/内边距；结果卡 = 面板体 + 头部/内边距。
 *  两者都只量一次（它们不随分配的高度变化），之后按实测值算，避免估算误差累积。 */
const chromeEd = ref(74)
const chromePanel = ref(96)
/** 结果卡实测总高（含头部与内边距），编辑器高度按它反推 */
const panelH = ref(0)
/** 中列在文档里的绝对顶部：滚过它 − 74 时编辑器刚好开始吸顶 */
const midTop = ref(0)
const scrollY = ref(0)

/** 编辑器至少要有这么高，再矮就没法写代码了 */
const MIN_EDITOR = 240
/** 结果面板至少这么高，否则看输出又得在框里滚 */
const MIN_PANEL = 160
/** 吸顶吸底都生效后的可用高度：顶栏 62px + 12px 间距，底部留 12px */
const avail = computed(() => Math.max(360, vh.value - 86))
/** 高度分配后还剩给「面板体」的余量 */
const room = computed(() => avail.value - MIN_EDITOR - 16 - chromeEd.value - chromePanel.value)

/** 面板体（.dock-body）的高度：先算「还剩多少空间」，再取想要的档位 */
const dockH = computed(() => {
  if (dock.value === 'collapsed') return 0
  // 空间不够 / 窄屏：不吸底，给一个看输出舒服的固定高度
  if (!dockFit.value) return 380
  const want = dock.value === 'expanded'
    ? Math.min(Math.round(vh.value * 0.52), 560)
    /* 常规档下限 280：扣掉预览头部约 34px 后舞台仍有 ~246px，看结果不憋屈 */
    : Math.round(Math.min(Math.max(vh.value * 0.30, 280), 380))
  return Math.max(MIN_PANEL, Math.min(want, room.value))
})

/** 高度按「吸顶吸底之后」的一屏来分，放得下才做两端固定 */
const dockFit = computed(() => vw.value > 1400 && room.value >= MIN_PANEL)

/* 吸底要等编辑器真的吸了顶才开：
   页面顶部时编辑器还在自然位置（上面压着面包屑 / 标题卡 / 语言切换，约 280px），
   此时面板若也吸底就会被顶上来压住编辑器。只有滚到编辑器贴住顶栏，
   两块才变成「上下分屏」，而且分配的高度刚好让临界点两侧位置连续、不跳变。 */
const dockOn = computed(() =>
  dockFit.value && scrollY.value >= Math.max(0, midTop.value - 74 - 4)
)

/** 编辑器高度 = 一屏 − 结果面板 − 间距 − 卡片外壳，刚好填满剩下的空间 */
const editorHeight = computed(() => {
  if (!dockFit.value) return assistantOpen.value ? 470 : 430
  const p = panelH.value || (dockH.value + chromePanel.value)
  const want = avail.value - p - 16 - chromeEd.value
  return Math.round(Math.min(900, Math.max(MIN_EDITOR, want)))
})

function measureChrome() {
  const card = edEl.value
  if (!card) return
  // 中列的文档坐标：用来判断「编辑器是否已经开始吸顶」
  if (midEl.value) midTop.value = midEl.value.getBoundingClientRect().top + (window.scrollY || 0)
  // 代码区高度就是传给 CodeEditor 的那个值，卡片总高减掉它 = 工具条 + 内边距
  const body = card.querySelector('.ce-body')
  if (body) chromeEd.value = Math.max(48, Math.min(140, card.offsetHeight - body.offsetHeight))
  const out = outEl.value
  if (out && dock.value !== 'collapsed' && dockH.value > 0) {
    chromePanel.value = Math.max(48, Math.min(160, out.offsetHeight - dockH.value))
  }
}

/* 面板高度会变的几个时机：窗口缩放、切语言（预览高度变）、开合助手、
   收起 / 放大。用 ResizeObserver 兜住布局变化，再量一次卡片外壳。 */
let ro = null
function watchSize() {
  ro = new ResizeObserver(() => {
    if (outEl.value) panelH.value = outEl.value.offsetHeight
    measureChrome()
  })
  if (outEl.value) ro.observe(outEl.value)
  measureChrome()
}
function onWinResize() {
  vw.value = window.innerWidth
  vh.value = window.innerHeight
  measureChrome()
}
function onScroll() {
  scrollY.value = window.scrollY || document.documentElement.scrollTop || 0
}

const isWeb = computed(() => isWebLang(curLang.value))

/** CSS 实验室配套的示例标记，预览时作为被样式作用的页面内容 */
const demo = computed(() => (lab.value ? getLabDemo(slug.value) : ''))

const langName = computed(() => {
  const l = curLang.value
  return (LANGS[l] && LANGS[l].name) || (l || '').toUpperCase()
})

/** 运行环境来源：内置工具链 / 本机已装。用来在界面上如实标注，不让人猜 */
const envSource = computed(() => {
  const l = curLang.value
  if (!l) return ''
  const item = env.value[l]
  return (item && item.source) || ''
})

/** 语言对应的运行环境是否可用；不可用时给出「怎么办」而不是只说不可用 */
const envWarn = computed(() => {
  const l = curLang.value
  // Web 语言在本页执行，永远可用，不该提示「环境缺失」
  if (!l || isWeb.value) return ''
  if (!Object.keys(env.value).length) return ''
  const item = env.value[l]
  if (item && item.available) return ''
  // 后端已经算好「怎么办」（含内置工具链部署指引）时优先用它，
  // 免得前端文案和后端实际支持的解法各说各话。
  if (item && item.hint) return String(item.hint).replace(/\n/g, '　')
  const tips = {
    c: '未检测到 C 编译器。请在项目根目录双击 tools\\setup-runtime.bat 部署内置工具链，部署一次之后任何机器都能直接运行。',
    cpp: '未检测到 C++ 编译器。请在项目根目录双击 tools\\setup-runtime.bat 部署内置工具链。',
    java: '未检测到 JDK（javac）。请在项目根目录双击 tools\\setup-runtime.bat 部署内置工具链。',
    python: '未检测到 Python 解释器。后端本身就是 Python 服务，正常启动过服务就应当可用；否则请安装 Python 3 并加入 PATH。',
    javascript: '未检测到 Node.js 运行环境。前端本身依赖 Node，正常启动过项目就应当可用。'
  }
  return tips[l] || '当前语言暂不支持在线运行，可在编辑器中阅读与修改代码。'
})

const renderedContent = computed(() => {
  const c = knowledge.value && knowledge.value.content
  if (!c) return ''
  try { return renderMd(c) } catch (e) { return '' }
})

/** 结果区不在视野里时，跑完顺手把它带进视野 —— 不然点「运行」像没反应 */
function revealResult() {
  const out = outEl.value
  if (!out || dockOn.value) return
  /* 宽屏：直接滚到「编辑器吸顶」的位置，一步进入「编辑器在上 / 结果在下」的分屏，
     比滚到结果区更直观 —— 滚过去之后两块谁都不用再找。 */
  if (dockFit.value) {
    window.scrollTo({ top: Math.max(0, midTop.value - 74), behavior: 'smooth' })
    return
  }
  const r = out.getBoundingClientRect()
  // 露出多少算够看：至少 320px，且不超过结果区自身高度
  const visible = Math.min(r.bottom, window.innerHeight) - Math.max(r.top, 74)
  const want = Math.min(320, r.height)
  if (visible < want) out.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

async function runCode() {
  if (!lab.value) return
  // 浏览器内语言：自增 runToken 让预览 iframe 重新加载即可，不必往返后端
  if (isWeb.value) { runToken.value += 1; nextTick(revealResult); return }
  running.value = true
  result.value = {}
  const feed = String(stdinText.value || '')       // 本次要喂给程序的键盘输入
  try {
    const res = await codeApi.run({ language: curLang.value, code: code.value, stdin: feed })
    const d = res.data || res
    result.value = {
      output: d.output || '', error: d.error, stderr: d.stderr || '', time: d.time
    }
  } catch (e) {
    const msg = (e && e.response && e.response.data && e.response.data.message) || '运行失败，请确认后端服务已启动'
    result.value = { output: '', error: true, stderr: msg }
  } finally {
    running.value = false
    runSeq.value += 1        // 通知控制台：这一趟跑完了，把输出追加到会话里
    // 收起状态下点运行，自动把面板放出来 —— 不然点了像没反应
    if (dock.value === 'collapsed') dock.value = 'normal'
    nextTick(() => { measureChrome(); revealResult() })
  }
}

async function loadKnowledge() {
  if (!lab.value || !lab.value.kid) { knowledge.value = null; return }
  try {
    const res = await courseApi.knowledge(lab.value.kid)
    knowledge.value = res.data ? res.data.knowledge : null
  } catch (e) {
    knowledge.value = null
  }
}

/* 语言 / 助手开合 / 面板档位改变的是编辑器高度与结果区内容，都要重新量一次 */
watch([curLang, assistantOpen, isWeb, dock], () => nextTick(measureChrome))

watch(lab, v => {
  if (!v) return
  /* 换实验（换知识点）时重置：语言回到该实验的原生语言，并按语言恢复草稿。
   * 旧实验的代码不该串到新实验里，所以这里不清 localStorage（草稿本来就带 slug 段），
   * 只重建内存缓存 —— 刷新页面后回到同一个实验，草稿仍在。 */
  curLang.value = v.lang
  // 每个候选语言都先查一次草稿：切语言时直接命中，不用再发请求
  const restored = {}
  const langs = Array.from(new Set([v.lang, ...availableLangsFor(slug.value)]))
  langs.forEach(l => {
    const d = loadDraft(SCOPE.LAB, slug.value, l)
    if (d) restored[l] = d
  })
  const first = restored[v.lang] || v.code || baseTemplate(v.lang) || ''
  code.value = first
  codeByLang.value = { ...restored, [v.lang]: first }
  // 输入跟着实验 + 语言一起恢复：换实验不该串味，换语言也要各存各的
  stdinText.value = loadStdin(SCOPE.LAB, slug.value, curLang.value) || ''
  clearResult()
  loadKnowledge()
}, { immediate: true })

onMounted(async () => {
  onWinResize()
  onScroll()
  watchSize()
  window.addEventListener('resize', onWinResize)
  window.addEventListener('scroll', onScroll, { passive: true })
  // 首帧字体/组件高度还没稳定，等一帧再量；tab 切换后也重算
  nextTick(measureChrome)
  setTimeout(measureChrome, 300)
  try {
    const res = await codeApi.env()
    env.value = (res && res.data) || {}
  } catch (e) {
    env.value = {}
  }
})

onBeforeUnmount(() => {
  if (ro) ro.disconnect()
  window.removeEventListener('resize', onWinResize)
  window.removeEventListener('scroll', onScroll)
})
</script>

<style scoped>
/* ---------- 布局比例 ----------
   默认：题目 30% / 编辑器 70%
   开算法助手：题目 30% / 编辑器 45% / 助手 25%
   用 flex-basis 百分比而不是写死 px，窄屏才不会崩。 */
.code-lab { max-width: 1680px; }
.lab-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; padding: 16px 20px; }
.lab-head h2 { margin: 0 0 4px; font-size: 19px; }
.lab-head p { margin: 0; font-size: 13px; }
.head-actions { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.lab-head-text { min-width: 0; }

/* ---------- 跨语言对比切换器 ---------- */
.lang-switch {
  margin-top: 12px; padding: 12px 16px;
  display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
}
.ls-head { display: flex; align-items: flex-start; gap: 8px; min-width: 0; flex: 1 1 260px; }
.ls-head > .el-icon { font-size: 18px; color: var(--brand); margin-top: 2px; }
.ls-title { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.ls-title b { font-size: 14px; }
.ls-title .small { line-height: 1.55; }
/* 下拉框：语言少的时候一个紧凑的 select 就够，不必横排一排按钮 */
.ls-picker { flex: 0 0 auto; display: flex; align-items: center; }
.ls-select { width: 208px; }
/* 下拉面板里的每一项：语言名 + 右侧副标题（本语言 / 主题名） */
.ls-opt { display: flex; align-items: center; gap: 8px; min-width: 0; }
.ls-opt-name { flex-shrink: 0; }
.ls-opt-theme {
  margin-left: auto; font-size: 12px; color: var(--text-3);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.ls-warn {
  display: flex; align-items: center; gap: 6px; flex-wrap: wrap;
  width: 100%; padding-top: 10px; border-top: 1px dashed var(--border);
  color: var(--warn-strong);
}

.lab-body { display: flex; gap: 16px; margin-top: 16px; align-items: flex-start; flex-wrap: nowrap; }
.lab-left { flex: 0 0 30%; max-width: 30%; padding: 16px 20px; min-width: 0; }
.lab-mid {
  flex: 1 1 70%; min-width: 0; display: flex; flex-direction: column; gap: 16px;
  align-self: flex-start;
}
/* ---------- 吸顶 + 吸底（dock） ----------
   两端固定的前提：中列容器要「够高」。sticky 的吸附范围 = 父容器，
   中列只有内容那么高的话，页面一滚它就整体离场了。
   所以这里让中列 stretch 到与左列等高（不够高时用 min-height 兜到一屏），
   容器够长，编辑器吸顶和面板吸底才能贯穿整段滚动。
   margin-top:auto 把结果卡推到容器底部，sticky bottom 再把它拉到视口底部。 */
/* dock-fit：高度已按一屏分配（中列拉到与左列等高，sticky 才有足够吸附范围）。
   这个类只跟视口尺寸有关，不随滚动开关，避免页面高度在滚动时抖动。 */
.lab-mid.dock-fit {
  align-self: stretch;
  min-height: calc(100vh - 90px);
}
/* 74px = 顶栏 62px + 12px 间距；矮屏顶栏略矮，多留的空白无伤大雅 */
.lab-mid.dock-on > .ed-card {
  position: sticky; top: 74px; flex-shrink: 0; z-index: 1;
}
.lab-mid.dock-on > .out-card {
  position: sticky; bottom: 12px; margin-top: auto; flex-shrink: 0; z-index: 2;
}
/* 结果卡纵向分配：标题条固定，面板体吃掉固定高度，内容超出在内部滚 */
.lab-mid .out-card { display: flex; flex-direction: column; }
.dock-body {
  height: var(--dock-h, 340px);
  display: flex; flex-direction: column; min-height: 0; overflow: hidden;
}
/* WebPreview 是孙组件：要让它填满面板体，得用后代选择器（写 `>` 会静默不匹配） */
.lab-mid :deep(.web-preview) { flex: 1 1 auto; min-height: 0; }
.lab-mid :deep(.wp-stage) { min-height: 0; }
/* 控制台不再写死 320px：面板给多少高度它就用多少，放大后能一屏看完 */
.lab-mid :deep(.wp-console) { max-height: none; flex: 1 1 auto; min-height: 120px; }
/* 收起态：整块压成一条，点一下还原 */
.dock-mini {
  display: flex; align-items: center; gap: 8px; cursor: pointer;
  padding: 4px 2px; color: var(--text-2); user-select: none;
}
.dock-mini:hover { color: var(--brand); }
.dock-mini .muted { margin-left: auto; }
/* 打开助手后让出 25%（编辑器 45%） */
.lab-body.with-assist .lab-mid { flex: 0 0 45%; max-width: 45%; }
.lab-assist {
  flex: 0 0 25%; max-width: 25%; min-width: 0;
  padding: 12px 14px; display: flex; flex-direction: column;
  position: sticky; top: 12px; max-height: calc(100vh - 40px); overflow: auto;
}
.assist-head {
  display: flex; align-items: center; justify-content: space-between;
  padding-bottom: 10px; margin-bottom: 8px; border-bottom: 1px solid var(--border);
}
.assist-head b { display: flex; align-items: center; gap: 6px; font-size: 14px; color: var(--brand); }

/* 窄屏：三栏挤不下就退回纵向堆叠，而不是把编辑器压成一条缝。
   此时必须关掉两端固定 —— 已经纵向排列了，再 sticky 会让编辑器盖住下面的正文。
   特异性要盖住 .lab-mid.dock-on，否则 JS 的判定会在窄屏照样生效。 */
@media (max-width: 1400px) {
  .lab-body { flex-wrap: wrap; }
  .lab-left { flex: 0 0 100%; max-width: 100%; }
  .lab-mid,
  .lab-mid.dock-fit {
    flex: 1 1 100%;
    align-self: flex-start; min-height: 0;
  }
  .lab-mid.dock-on > .ed-card,
  .lab-mid.dock-on > .out-card { position: static; margin-top: 0; }
  .lab-body.with-assist .lab-mid { flex: 0 0 58%; max-width: 58%; }
  .lab-assist { flex: 0 0 38%; max-width: 38%; position: static; max-height: none; }
}
/* 矮屏兜底：JS 也会判，这里再兜一道，避免首帧（JS 还没量）被压出溢出。 */
@media (max-height: 700px) {
  .lab-mid.dock-on > .ed-card,
  .lab-mid.dock-on > .out-card { position: static; margin-top: 0; }
  .lab-mid.dock-fit { align-self: flex-start; min-height: 0; }
}
@media (max-width: 980px) {
  .lab-body.with-assist .lab-mid,
  .lab-assist { flex: 0 0 100%; max-width: 100%; }
}

.sec-title { font-size: 15px; margin: 0 0 10px; color: var(--text-1); }
.point-list { margin: 0; padding-left: 18px; font-size: 13px; line-height: 1.9; color: var(--text-2); }

.out-card { padding: 12px 14px; }
.out-head { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; flex-shrink: 0; }
.out-head .head-actions { margin-left: auto; display: flex; align-items: center; gap: 6px; }
/* 控制台（RunConsole）：不再单独写黑框样式 ——
   背景/字号/滚动都在组件里，这里只负责让它吃满面板剩下的高度 */
.dock-body :deep(.run-console) { flex: 1 1 auto; min-height: 0; }
.env-warn {
  display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--warn-strong);
  background: var(--warning-light); border: 1px solid var(--warn-border); border-radius: 6px; padding: 6px 10px; margin-bottom: 8px;
}
.empty-card { padding: 40px; }

/* ---------- 响应式 ---------- */
@media (max-width: 900px) {
  .lab-head { flex-direction: column; align-items: flex-start; }
  .lab-head .head-actions { width: 100%; }
  .lang-switch { gap: 10px; }
  /* 平板：下拉框独占第二行整宽，不再和标题挤在一行 */
  .ls-picker { flex: 1 1 100%; }
  .ls-select { width: 100%; }
}
@media (max-width: 480px) {
  /* 小屏给结果区一个不撑爆手机的高度 */
  .dock-body { height: auto !important; min-height: 260px; }
  .dock-body :deep(.run-console) { min-height: 180px; }
}
</style>
