<template>
  <div class="page" v-if="questions.length">
    <el-breadcrumb separator="/" style="margin-bottom:12px">
      <template v-if="wrongMode">
        <el-breadcrumb-item :to="{ path: '/profile?tab=wrong' }">个人中心</el-breadcrumb-item>
        <el-breadcrumb-item>错题重做</el-breadcrumb-item>
      </template>
      <template v-else>
        <el-breadcrumb-item :to="{ path: '/courses' }">课程中心</el-breadcrumb-item>
        <el-breadcrumb-item>{{ knowledgeName }}</el-breadcrumb-item>
        <el-breadcrumb-item>随堂练习</el-breadcrumb-item>
      </template>
    </el-breadcrumb>

    <!-- 页面内导航条 + 筛选 -->
    <div class="filter-bar card">
      <div class="nav-btns">
        <el-button size="small" :disabled="!canBack" @click="goBack">
          <el-icon><ArrowLeft /></el-icon> 上一步
        </el-button>
        <el-button size="small" @click="reload">
          <el-icon><Refresh /></el-icon> 刷新
        </el-button>
        <el-button size="small" type="primary" plain @click="goBackToList">
          <el-icon><Back /></el-icon> 返回题库
        </el-button>
      </div>

      <div class="filter-row">
        <div class="filter-item">
          <label class="filter-label">题目范围</label>
          <el-select v-model="source" size="small" @change="reload">
            <el-option value="all" label="全部来源" />
            <el-option value="考研408" label="考研 408" />
            <el-option value="软考" label="软考" />
            <el-option value="NCRE" label="等级考试(NCRE)" />
            <el-option value="期末" label="期末/期中" />
            <el-option value="编程语言" label="编程语言" />
            <el-option value="基础" label="基础练习" />
          </el-select>
        </div>

        <div class="filter-item">
          <label class="filter-label">难度</label>
          <el-select v-model="difficulty" size="small" @change="reload">
            <el-option :value="0" label="全部难度" />
            <el-option :value="1" label="入门" />
            <el-option :value="2" label="容易" />
            <el-option :value="3" label="中等" />
            <el-option :value="4" label="较难" />
            <el-option :value="5" label="困难" />
          </el-select>
        </div>

        <div class="filter-item">
          <label class="filter-label">题型</label>
          <el-select v-model="typeFilter" size="small" @change="reload">
            <el-option value="all" label="全部题型" />
            <el-option value="single" label="单选题" />
            <el-option value="judge" label="判断题" />
            <el-option value="multi" label="多选题" />
            <el-option value="case" label="案例分析题" />
            <el-option value="programming" label="编程题" />
          </el-select>
        </div>

        <!-- 掌握状态：错题模式本身就是错题集，再筛就没意义了 -->
        <div v-if="!wrongMode" class="filter-item">
          <label class="filter-label">掌握状态</label>
          <el-select v-model="mastery" size="small" @change="reload">
            <el-option v-for="m in MASTERY_OPTIONS" :key="m.value" :value="m.value" :label="m.label" />
          </el-select>
        </div>

        <div class="filter-stat">
          <span class="small muted">当前 <b class="f-num">{{ questions.length }}</b> 题</span>
          <el-tag v-if="current && current.source" size="small" effect="plain" type="info">{{ current.source }}</el-tag>
          <el-tag v-if="current && current.difficulty" size="small" effect="plain">
            难度 {{ '★'.repeat(current.difficulty) }}
          </el-tag>
        </div>
      </div>
    </div>

    <el-row :gutter="16">
      <el-col :xs="24" :sm="24" :md="24" :lg="17">
        <div class="card q-card">
          <div class="q-head">
            <div>
              <el-tag size="small" :type="typeTag.type" effect="light">{{ typeTag.text }}</el-tag>
              <span class="small muted" style="margin-left:8px">第 {{ index + 1 }} / {{ questions.length }} 题</span>
              <el-tag v-if="isSubjective" size="small" type="warning" effect="plain" style="margin-left:8px">
                {{ current.score || 10 }} 分 · 智能判分
              </el-tag>
              <!-- 切回做过但还没提交的题时给个提示，否则「怎么已经有答案了」会让人以为串题 -->
              <el-tag v-if="hasSavedPick && !result" size="small" type="info" effect="plain" style="margin-left:8px">
                已保留上次作答
              </el-tag>
              <!-- 错题重做：题目跨知识点，必须标出它属于哪门课哪个知识点，
                   否则做到第 5 题已经不知道在考什么了 -->
              <el-tag v-if="wrongMode && current.knowledge_name" size="small" effect="plain" style="margin-left:8px">
                {{ current.course_name }} · {{ current.knowledge_name }}
              </el-tag>
              <el-tag v-if="wrongMode && current.wrong_count" size="small" type="danger" effect="light" style="margin-left:8px">
                错 {{ current.wrong_count }} 次
              </el-tag>
              <el-tag v-if="wrongMode && isMastered" size="small" type="success" effect="light" style="margin-left:8px">
                本次已攻克
              </el-tag>
            </div>
            <el-progress :percentage="Math.round((index / questions.length) * 100)" :stroke-width="8" style="width:140px" :show-text="false" />
          </div>

          <h3 class="q-title">{{ current.title }}</h3>

          <!-- 客观题选项：多选题用 checkbox（可多选），其余用 radio -->
          <el-checkbox-group v-if="isMulti" v-model="answerArr" class="opt-group" :disabled="!!result">
            <div
              v-for="o in options" :key="o.key"
              class="opt-item" :class="optClass(o.key)"
              @click="!result && toggleMulti(o.key)"
            >
              <el-checkbox :value="o.key" style="width:100%">
                <span class="opt-key">{{ o.key }}</span>
                <span class="opt-text">{{ o.text }}</span>
              </el-checkbox>
            </div>
          </el-checkbox-group>

          <el-radio-group v-else-if="!isSubjective" v-model="answer" class="opt-group" :disabled="!!result">
            <div v-for="o in options" :key="o.key" class="opt-item" :class="optClass(o.key)" @click="!result && (answer = o.key)">
              <el-radio :value="o.key" style="width:100%">
                <span class="opt-key">{{ o.key }}</span>
                <span class="opt-text">{{ o.text }}</span>
              </el-radio>
            </div>
          </el-radio-group>

          <!-- 主观题：案例分析 = 文本编辑器 -->
          <div v-else-if="current.type === 'case'" class="subjective">
            <div class="sub-tip small muted">
              这是一道案例分析题。请写出你的分析过程与结论 —— 说得越具体，判分越准。
            </div>
            <el-input
              v-model="answer"
              type="textarea"
              :rows="12"
              :disabled="!!result"
              maxlength="8000"
              show-word-limit
              placeholder="例如：先说明现象产生的原因，再给出验证方法，最后给出解决方案……"
            />
            <div class="quick-bar">
              <span class="small muted">常用句式：</span>
              <el-button size="small" plain @click="insert('原因是：')">原因是</el-button>
              <el-button size="small" plain @click="insert('解决方法是：')">解决方法是</el-button>
              <el-button size="small" plain @click="insert('验证方式：')">验证方式</el-button>
            </div>
          </div>

          <!-- 主观题：编程题 = 代码编辑器 -->
          <div v-else-if="current.type === 'programming'" class="subjective">
            <div class="sub-tip small muted">
              这是一道编程题。请在编辑器里写出完整可运行的作答，交卷后会逐条核对评分要点并指出如何改正。
            </div>
            <div class="lang-bar">
              <span class="small muted">作答语言</span>
              <!-- 选项由 LANG_ORDER 循环生成，不再手写一份。
                   原来是 python 打头，和算法题页的顺序对不上。
                   进题时若题面写了「用 C99 / C++ / Java…」会自动切过去；
                   用户手动选过就以手动为准，不再自动覆盖。 -->
              <el-select v-model="lang" size="small" style="width:130px" :disabled="!!result" @change="langTouched = true">
                <el-option
                  v-for="l in PRACTICE_LANGS" :key="l.value"
                  :value="l.value" :label="l.label"
                />
              </el-select>
              <span v-if="langAutoTip" class="small" style="color:var(--brand)">
                <el-icon><InfoFilled /></el-icon> 已按题目要求切换为 {{ langAutoTip }}
              </span>
            </div>
            <CodeEditor v-model="answer" :language="lang" :height="330" :running="running || grading" @run="runCode" />

            <div class="code-foot small muted">
              <span>
                <el-icon><InfoFilled /></el-icon>
                代码与运行输入自动保存在本机，刷新页面或切走再回来都还在（按题目 + 语言分别保存）
              </span>
              <el-button size="small" text :disabled="grading" @click="clearCode">清空重写</el-button>
            </div>

            <!-- 控制台：输入和输出在同一个黑框里 —— 用代码实验室同一个组件，
                 下面一行 › 逐行敲数据，回显与程序输出按时间排在一起，像真终端。 -->
            <div v-if="isProgramming" class="run-box">
              <div class="run-head">
                <b>控制台</b>
                <span class="small muted" v-if="runResult && runResult.time">上次耗时 {{ runResult.time }} ms</span>
                <el-tag size="small" effect="plain" type="info">运行 · 不计分</el-tag>
                <span class="run-actions">
                  <el-button size="small" text @click="clearConsole">清空</el-button>
                </span>
              </div>
              <RunConsole
                ref="consoleEl"
                v-model="stdinText" :code="answer"
                :output="(runResult && runResult.output) || ''"
                :stderr="(runResult && runResult.stderr) || ''"
                :error="!!(runResult && runResult.error)"
                :time="(runResult && runResult.time) || 0"
                :running="running || grading"
                :result-key="runSeq"
                @run="runCode"
              />
            </div>

            <div class="small muted" style="margin-top:6px">提示：Ctrl + Enter 运行查看输出（不计分）· 判分请点「提交并智能判分」。</div>
          </div>

          <!-- 客观题结果 -->
          <div v-if="result && !isSubjective" class="result-box" :class="result.correct ? 'ok' : 'bad'">
            <div class="result-head">
              <el-icon><component :is="result.correct ? 'CircleCheckFilled' : 'CircleCloseFilled'" /></el-icon>
              <b>{{ result.correct ? '回答正确' : '回答错误' }}</b>
              <span class="small">正确答案：{{ answerText(result.answer) }}</span>
              <span v-if="isMulti" class="small muted">你的选择：{{ myAnswerText }}</span>
            </div>
            <div class="analysis"><b>解析：</b>{{ result.analysis }}</div>
          </div>

          <!-- 主观题判分结果 -->
          <div v-if="result && isSubjective" class="grade-box">
            <div class="grade-head" :class="result.correct ? 'ok' : 'bad'">
              <div class="grade-score">
                <b>{{ result.score }}</b><span> / {{ result.maxScore }} 分</span>
              </div>
              <div class="grade-meta">
                <el-tag size="small" :type="result.correct ? 'success' : 'danger'" effect="light">
                  {{ result.correct ? '掌握' : '尚未掌握' }}
                </el-tag>
                <span class="small muted">
                  命中 {{ result.hits.length }} 个要点
                  <template v-if="result.misses.length">，遗漏 {{ result.misses.length }} 个</template>
                </span>
                <span class="small muted" v-if="result.mode === 'heuristic'">（本地智能判分）</span>
              </div>
            </div>

            <!-- Agent 判分的思考过程 -->
            <div v-if="result.reasoning && result.reasoning.length" class="reasoning">
              <div class="reasoning-title" @click="showReasoning = !showReasoning">
                <span>判分的思考过程</span>
                <span class="small muted">{{ showReasoning ? '收起' : '展开' }}</span>
              </div>
              <ol v-show="showReasoning" class="reasoning-list">
                <li v-for="(r, i) in result.reasoning" :key="i">
                  <b>{{ r.title }}</b>
                  <span class="small muted"> — {{ r.detail }}</span>
                </li>
              </ol>
            </div>

            <!-- 作弊指令提示 -->
            <div v-if="result.cheat && result.cheat.detected" class="cheat-tip">
              <el-icon><WarningFilled /></el-icon>
              <span>{{ result.cheat.notice }}</span>
            </div>

            <div v-if="result.comment" class="analysis comment">
              <b>总评：</b>{{ result.comment }}
            </div>

            <div v-if="result.hits.length" class="point-block">
              <div class="small" style="color:var(--success);font-weight:600">✓ 你答到的要点</div>
              <ul>
                <li v-for="(h, i) in result.hits" :key="'h' + i" class="small">
                  <span v-if="typeof h === 'string'">{{ h }}</span>
                  <template v-else>{{ h.point }} <em>（+{{ h.score }}分）</em></template>
                </li>
              </ul>
            </div>

            <div v-if="result.misses.length" class="point-block">
              <div class="small" style="color:var(--danger);font-weight:600">✗ 遗漏的要点（这就是你要补的地方）</div>
              <ul>
                <li v-for="(m, i) in result.misses" :key="'m' + i" class="small">
                  <span v-if="typeof m === 'string'">{{ m }}</span>
                  <template v-else>{{ m.point }} <em>（{{ m.score }}分）</em></template>
                </li>
              </ul>
            </div>

            <div v-if="result.suggestions && result.suggestions.length" class="point-block">
              <div class="small" style="font-weight:600">怎么改正</div>
              <ul>
                <li v-for="(s, i) in result.suggestions" :key="'s' + i" class="small">{{ s }}</li>
              </ul>
            </div>

            <div v-if="result.referenceAnswer" class="ref-block">
              <div class="ref-head" @click="showRef = !showRef">
                <span class="small">参考答案</span>
                <span class="small muted">{{ showRef ? '收起' : '点击展开（建议先自己改一遍再看）' }}</span>
              </div>
              <pre v-show="showRef" class="ref-body">{{ result.referenceAnswer }}</pre>
            </div>
          </div>

          <div class="q-actions">
            <el-button :disabled="index === 0" @click="prev">上一题</el-button>
            <el-button :disabled="!canRedo" @click="redoCurrent">
              <el-icon><RefreshRight /></el-icon> 重新做此题
            </el-button>
            <el-button v-if="!result && isProgramming" :loading="running" :disabled="grading" @click="runCode">
              <el-icon><CaretRight /></el-icon> 运行（不计分）
            </el-button>
            <el-button v-if="!result" type="primary" :disabled="!canSubmit" :loading="grading" @click="submit">
              {{ isSubjective ? '提交并智能判分' : '提交答案' }}
            </el-button>
            <el-button v-else type="primary" @click="next">
              {{ index === questions.length - 1 ? '完成练习' : '下一题' }}
            </el-button>
            <el-button v-if="result && !result.correct" @click="openVis">看动画搞懂它</el-button>
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :sm="24" :md="24" :lg="7">
        <div class="card side-card">
          <div class="panel-title">{{ wrongMode ? '错题答题卡' : '答题卡' }}</div>
          <div class="card-grid">
            <div
              v-for="(q, i) in questions" :key="q.id"
              class="card-cell"
              :class="{ cur: i === index, right: answers[i] === true, wrong: answers[i] === false }"
              :title="typeText(q.type)"
              @click="go(i)"
            >{{ i + 1 }}</div>
          </div>
          <el-divider />
          <div class="stat-line"><span>已作答</span><b>{{ answeredCount }} / {{ questions.length }}</b></div>
          <div class="stat-line"><span>正确</span><b style="color:var(--success)">{{ correctCount }}</b></div>
          <div class="stat-line"><span>错误</span><b style="color:var(--danger)">{{ wrongCount }}</b></div>
          <div v-if="wrongMode" class="stat-line">
            <span>本次攻克</span><b style="color:var(--success)">{{ masteredCount }}</b>
          </div>
          <div class="side-btns">
            <el-button style="flex:1 1 140px" @click="openVis">
              {{ wrongMode ? '看这题的动画' : '打开可视化动画' }}
            </el-button>
            <el-button
              style="flex:1 1 140px" type="warning" plain
              :disabled="!hasAnyProgress" @click="redoAll"
            >
              <el-icon><RefreshRight /></el-icon> {{ wrongMode ? '重做这套错题' : '重新做此套题' }}
            </el-button>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 完成弹窗 -->
    <el-dialog v-model="doneVisible" :title="wrongMode ? '错题重做完成' : '练习完成'" width="420px">
      <div class="done-box">
        <template v-if="wrongMode">
          <div class="score">{{ masteredCount }} / {{ questions.length }}</div>
          <p>
            本次攻克 {{ masteredCount }} 道
            <template v-if="remainWrongCount">，还剩 {{ remainWrongCount }} 道留在错题本里，下次再来</template>
            <template v-else>，错题本清空了！</template>
          </p>
        </template>
        <template v-else>
          <div class="score">{{ score }} 分</div>
          <p>共 {{ questions.length }} 题，答对 {{ correctCount }} 题{{ wrongCount ? `，${wrongCount} 题已存入错题本` : '，太棒了！' }}</p>
        </template>
      </div>
      <template #footer>
        <el-button @click="doneVisible = false">继续{{ wrongMode ? '重做' : '练习' }}</el-button>
        <el-button v-if="wrongMode && remainWrongCount" type="warning" plain @click="redoWrongSet">
          再练一遍剩下的
        </el-button>
        <el-button v-else-if="!wrongMode && wrongCount" type="warning" plain @click="$router.push('/profile?tab=wrong')">
          查看错题本
        </el-button>
        <el-button type="primary" @click="openVis">看可视化动画</el-button>
      </template>
    </el-dialog>
  </div>
  <div class="page" v-else>
    <el-empty :description="emptyText">
      <el-button v-if="wrongMode" type="primary" @click="$router.push('/courses')">去做新题</el-button>
      <el-button v-else type="primary" @click="$router.push('/courses')">返回课程中心</el-button>
    </el-empty>
    <!-- 筛掉了全部题目：不是没题，是条件太严。给一条退路，否则整页空白像坏了 -->
    <div v-if="!wrongMode && hasFilters" class="filter-empty-tip">
      <span class="small muted">当前筛选没有匹配的题目，</span>
      <el-button text type="primary" size="small" @click="resetFilters">清空筛选条件</el-button>
    </div>
  </div>
</template>

<script setup>
/* watch 必须在这里 import —— 漏了会在 setup 阶段直接抛
   `ReferenceError: watch is not defined`，组件挂不上，整页白屏（不是局部报错，很难一眼看出）。
   教训：新增 Vue 组合式 API 别只写调用，先确认这个名字在顶部 import 列表里。 */
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { questionApi, courseApi, learnApi, codeApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Refresh, RefreshRight, Back, InfoFilled, CaretRight } from '@element-plus/icons-vue'
import CodeEditor from '@/components/CodeEditor.vue'
import RunConsole from '@/components/RunConsole.vue'
import { baseTemplate, LANG_ORDER, langLabel } from '@/utils/codeTemplates'
import { SCOPE, loadDraft, saveDraft, clearDraft, loadStdin, saveStdin } from '@/utils/draftStore'
import { labOf } from '@/data/visMap'

const route = useRoute()
const router = useRouter()
/* 错题重做模式：同一套做题 UI，题目来自「我的错题本」而不是某个知识点。
   错题散落在不同知识点里，不可能塞进 practice/:kid，所以单开一条路由，
   页面内只切换取数来源 —— 判分、保留作答、重做这些能力全部复用。 */
const wrongMode = computed(() => route.name === 'WrongPractice')
/** 本次重做里答对的题：提交时后端会自动把它移出错题本，这里只为结算展示 */
const masteredIds = ref(new Set())
const questions = ref([])
const index = ref(0)
const answer = ref('')
const result = ref(null)
const answers = ref([]) // true/false/undefined
const knowledgeName = ref('')
const knowledgeRoute = ref('')
const doneVisible = ref(false)
const source = ref('all')
const difficulty = ref(0)
const typeFilter = ref('all')
/* 掌握状态：全部 / 只看未掌握 / 只看错题本。
   「这套题里还有哪些不会」要一次点出来，而不是靠学生自己回忆哪道错过。
   后端按 user_id 过滤；未登录（游客浏览）时后端会忽略该条件，返回全部。 */
const mastery = ref('all')
const MASTERY_OPTIONS = [
  { value: 'all', label: '全部题目' },
  { value: 'unmastered', label: '只看未掌握' },
  { value: 'wrong', label: '只看错题本' }
]
const lang = ref('python')
/* 作答语言选项：只取「能编译运行」的五门语言（不含 html / css），
   顺序取全站 LANG_ORDER：c → cpp → java → python → javascript */
const PRACTICE_LANGS = LANG_ORDER
  .filter(l => ['c', 'cpp', 'java', 'python', 'javascript'].includes(l))
  .map(l => ({ value: l, label: langLabel(l) }))

/** 题面语言要求 → 自动切换作答语言。
 *  题面写「用 C99 写出完整程序」而编辑器还是 Python 模板，是本批修掉的体验断裂：
 *  学生往往照着 Python 骨架写半天才发现语言不对。匹配顺序刻意先 C++ 再 C ——
 *  「C++」里也含 C，先匹配宽的会被 C 的正则抢走。 */
function detectRequiredLang(text) {
  const t = String(text || '')
  if (/JavaScript/i.test(t)) return 'javascript'
  if (/C\+\+|CXX\b/i.test(t)) return 'cpp'
  if (/C\s*(?:99|11|17|语言)\b/i.test(t)) return 'c'
  if (/\bJava\b/i.test(t)) return 'java'
  if (/Python/i.test(t)) return 'python'
  return ''
}
/** 用户手动选过语言就以手动为准 —— 否则来回切题会不停覆盖用户的选择 */
const langTouched = ref(false)
/** 自动切换进行中的标志：watch(lang) 要跳过「存旧取新 + 清判分结果」，
 *  applyCurrent 已经按新语言取好了草稿，watch 再跑一遍会把新代码写进旧语言键下 */
const langAuto = ref(false)
/** 自动切换成功后的气泡提示（如「C99」），几秒后消失 */
const langAutoTip = ref('')
let langAutoTimer = null
function autoSwitchLang(q) {
  const want = detectRequiredLang(q && q.title)
  if (!want || want === lang.value) return
  langAuto.value = true
  lang.value = want
  langAutoTip.value = PRACTICE_LANGS.find(l => l.value === want)?.label || want
  clearTimeout(langAutoTimer)
  langAutoTimer = setTimeout(() => { langAutoTip.value = '' }, 4000)
}
const grading = ref(false)
const showReasoning = ref(true)
const showRef = ref(false)
/** 从题库带 qid 进来时要定位的那道题；手动改筛选后失效 */
const focusQuestionId = ref(null)

/* ================= 作答记忆：做过的题保留上次答案 =================
 * 需求：切走再切回来（甚至刷新页面）要能看到自己上次选了什么。
 *
 * 为什么分两张表：
 *   - pickMap  —— 作答内容（单/判的 key、多选的 key 数组、案例分析的整段文本），落 localStorage，
 *                 按知识点分组（换知识点互不干扰），这样刷新后还在。
 *   - resultMap —— 判分结果，只活在会话里。判分结果依赖当前题库与判分策略，
 *                  持久化一份过期的「正确/错误」反而会误导人，刷新就该重新做。
 *
 * 键名按 kid 分组而不是按整套题的 id 列表：筛选条件一变题目集合就变，
 * 按集合存会让「换了个难度」就找不到上次作答。 */
// 错题模式是自成一体的题集，单独一个键，不跟任何知识点的作答记录混在一起
const pickKey = computed(() => 'cv_prac_pick_' + (wrongMode.value ? 'wrong' : String(route.params.kid || 0)))
const pickMap = ref({})
const resultMap = ref({})

const current = computed(() => questions.value[index.value] || {})
/** 多选题：answerArr 存选中的 key 数组，提交时拼成 'ABC' 传给后端 */
const isMulti = computed(() => current.value.type === 'multi')
const answerArr = ref([])
const myAnswerText = computed(() => (answerArr.value.length ? answerArr.value.slice().sort().join('') : '未作答'))
/** 主观题：案例分析题与编程题，需要文本/代码编辑器 + Agent 判分 */
const isSubjective = computed(() => {
  const t = current.value.type
  return t === 'case' || t === 'programming'
})
// 判断题兜底：库里出现过 answer 写成 T/F、options 却留空的记录，
// 那时这里拿到空数组 → 整道题一个选项都渲染不出来，学生没法作答。
// 迁移脚本已修数据，但 UI 不能假设数据一定干净，这里补上默认的两个选项。
const JUDGE_OPTIONS = [{ key: 'A', text: '正确' }, { key: 'B', text: '错误' }]
const options = computed(() => {
  try {
    const raw = current.value.options
    if (Array.isArray(raw) && raw.length) return raw
  } catch (e) { /* 落到下面的兜底 */ }
  return current.value.type === 'judge' ? JUDGE_OPTIONS : []
})
const canSubmit = computed(() => {
  if (isSubjective.value) return String(answer.value || '').trim().length >= 2
  if (isMulti.value) return answerArr.value.length > 0
  return !!answer.value
})

/** 多选勾选：el-checkbox 自带 toggle，这里手动同步成数组，
 *  保证点击整行（不点小方块）也能选中 —— 与单选的交互保持一致 */
function toggleMulti(key) {
  if (result.value) return
  const i = answerArr.value.indexOf(key)
  if (i >= 0) answerArr.value.splice(i, 1)
  else answerArr.value.push(key)
}

const typeTag = computed(() => {
  const map = {
    judge: { text: '判断题', type: 'warning' },
    case: { text: '案例分析题', type: 'danger' },
    programming: { text: '编程题', type: 'success' },
    multi: { text: '多选题', type: 'primary' }
  }
  return map[current.value.type] || { text: '单选题', type: 'primary' }
})

// 判断题的标准答案历史上写成过 T/F，直接显示会冒出意义不明的字母
function answerText(a) {
  // 多选答案统一排序后展示，避免 'CAB' 这种顺序差异让用户以为自己错了
  if (current.value.type === 'multi') return String(a || '').split('').sort().join('')
  if (current.value.type !== 'judge') return a
  return { A: 'A（正确）', B: 'B（错误）', T: 'A（正确）', F: 'B（错误）' }[String(a).toUpperCase().trim()] || a
}

function typeText(t) {
  return { single: '单选题', judge: '判断题', multi: '多选题', case: '案例分析题', programming: '编程题' }[t] || '习题'
}

const answeredCount = computed(() => answers.value.filter(a => a !== undefined && a !== null).length)
const correctCount = computed(() => answers.value.filter(a => a === true).length)
const wrongCount = computed(() => answers.value.filter(a => a === false).length)
const score = computed(() => Math.round((correctCount.value / (questions.value.length || 1)) * 100))

function optClass(key) {
  const picked = isMulti.value ? answerArr.value.includes(key) : answer.value === key
  if (!result.value) return picked ? 'selected' : ''
  // 多选答案按字符集合比对，兼容 'ABC' / 'CAB' / 'A,C,B' 等写法。
  // 直接用 === 比字符串，顺序不同就会把正确项标成错。
  const k = String(key).toUpperCase()
  const rightSet = String(result.value.answer || '')
    .split(/[,，\s]+/).flatMap(s => s.split(''))
    .map(s => s.trim().toUpperCase()).filter(Boolean)
  if (rightSet.includes(k)) return 'right'
  if (picked && !result.value.correct) return 'wrong'
  return ''
}

function insert(text) {
  answer.value = (answer.value || '') + (answer.value ? '\n' : '') + text
}

/* ================= 运行（不计分） =================
 * 「运行」与「提交判分」分离：运行只把代码跑起来看输出 —— 不判分、
 * 不写答题卡、不影响错题本；判分只发生在「提交并智能判分」。
 * 和代码实验室 / 算法题页同一个 /api/code/run 通道。 */
const running = ref(false)
const runResult = ref(null)
/** 程序输入（stdin）：在线运行没法中途等人敲键盘，改成运行前把数据写好一起提交 */
const stdinText = ref('')

/** 每跑完一次自增 —— 控制台靠它把这一段输出追加到会话流水里 */
const runSeq = ref(0)
const consoleEl = ref(null)

/** 「清空」按钮：结果对象与控制台屏幕一起收干净（输入队列不清，还能接着用） */
function clearConsole() {
  runResult.value = null
  if (consoleEl.value && consoleEl.value.clear) consoleEl.value.clear()
}

async function runCode() {
  if (!isProgramming.value || running.value || grading.value) return
  const code = String(answer.value || '')
  const tpl = String(baseTemplate(lang.value) || '').trim()
  if (!code.trim() || code.trim() === tpl) {
    ElMessage.warning('先写点代码再运行，现在是初始模板')
    return
  }
  // 输入不必等失焦再落盘 —— 点运行的当下就把草稿存好，切回来还在
  const ident0 = draftIdent()
  if (ident0) saveStdin(SCOPE.PRACTICE, ident0, lang.value, stdinText.value)
  running.value = true
  runResult.value = null
  try {
    const res = await codeApi.run({ language: lang.value, code, stdin: stdinText.value })
    if (res && res.code === 200 && res.data) {
      runResult.value = { ...res.data }
    } else {
      runResult.value = { output: '', stderr: (res && res.message) || '运行失败', error: true, time: 0 }
    }
  } catch (e) {
    runResult.value = { output: '', stderr: '运行服务连接失败，请确认后端已通过 start.bat 启动', error: true, time: 0 }
  } finally {
    running.value = false
    runSeq.value += 1        // 通知控制台：这一趟跑完了，把输出追加到会话里
  }
}

async function submit() {
  if (!canSubmit.value) return
  // 编程题防呆：代码还是初始模板 = 没动笔，别浪费一次判分
  if (isProgramming.value) {
    const tpl = String(baseTemplate(lang.value) || '').trim()
    if (String(answer.value || '').trim() === tpl) {
      ElMessage.warning('还没有写代码，编辑器里是初始模板 —— 先写代码，或用「运行」试试输出')
      return
    }
  }
  // 主观题交给 Agent 智能判分；客观题走普通比对
  if (isSubjective.value) {
    grading.value = true
    try {
      const res = await questionApi.grade({ questionId: current.value.id, answer: answer.value })
      if (!res || res.code !== 200 || !res.data) {
        ElMessage.error((res && res.message) || '判分失败，请稍后重试')
        return
      }
      result.value = res.data
      answers.value[index.value] = !!res.data.correct
      // 按题号存一份判分结果：切走再切回来还能看到自己错在哪、解析是什么
      if (current.value.id) resultMap.value[String(current.value.id)] = res.data
      markMastered(current.value.id, res.data.correct)
      if (res.data.cheat && res.data.cheat.detected) {
        ElMessage.warning('作答中检测到影响评分的指令，已按评分要点客观判分')
      }
    } catch (e) {
      ElMessage.error('判分失败，请稍后重试')
    } finally {
      grading.value = false
    }
    return
  }
  // 客观题提交必须兜住两种失败：后端返回 {code:404}（题目已被删除，HTTP 仍是 200）、
  // 以及网络异常 reject。二者都要给用户明确反馈，否则点了「提交」毫无反应，
  // 连自己答对没都不知道。
  let res
  try {
    // 多选把选中的 key 排序后拼成 'ABC' 传给后端，避免选择顺序影响判分
    const payload = isMulti.value
      ? answerArr.value.slice().sort().join('')
      : answer.value
    res = await questionApi.submit({ questionId: current.value.id, answer: payload })
  } catch (e) {
    ElMessage.error('提交失败，请检查网络后重试')
    return
  }
  if (!res || res.code !== 200 || !res.data) {
    ElMessage.error((res && res.message) || '提交失败：题目可能已被删除')
    return
  }
  result.value = res.data
  answers.value[index.value] = !!res.data.correct
  if (current.value.id) resultMap.value[String(current.value.id)] = res.data
  markMastered(current.value.id, res.data.correct)
}

/* 错题重做的闭环：答对一题，后端已经把它从 wrong_question 里删掉了，
   这里记一笔用于结算展示，并明确告诉学生「这题出师了」。
   答错不用处理 —— 后端会把 wrong_count +1，题目自然还留在错题本里。 */
function markMastered(qid, correct) {
  if (!wrongMode.value || !qid) return
  if (correct) {
    masteredIds.value.add(Number(qid))
    ElMessage.success('答对了，本题已从错题本移除')
  } else {
    masteredIds.value.delete(Number(qid))
  }
}

/* ---------- 作答记忆读写 ---------- */
/** 读一次 localStorage；数据是用户可编辑的，坏数据一律降级成空表，不能让整页挂掉 */
function loadPicks() {
  try {
    const raw = localStorage.getItem(pickKey.value)
    const obj = raw ? JSON.parse(raw) : null
    pickMap.value = (obj && typeof obj === 'object' && !Array.isArray(obj)) ? obj : {}
  } catch (e) {
    pickMap.value = {}
  }
}

function persistPicks() {
  try {
    if (Object.keys(pickMap.value).length) localStorage.setItem(pickKey.value, JSON.stringify(pickMap.value))
    else localStorage.removeItem(pickKey.value)
  } catch (e) { /* 配额不足 / 隐私模式：不落盘也不影响做题 */ }
}

/** 写一条作答；a 与 m 都空视为「没做过」，直接删键，避免留一堆空记录 */
function savePick(qid, patch) {
  const k = String(qid || '')
  if (!k) return
  const next = { ...(pickMap.value[k] || {}), ...patch }
  const empty = !String(next.a || '').trim() && !(next.m && next.m.length)
  if (empty) delete pickMap.value[k]
  else pickMap.value[k] = next
  persistPicks()
}

function dropPick(qid) {
  const k = String(qid || '')
  if (!k) return
  delete pickMap.value[k]
  delete resultMap.value[k]
  persistPicks()
}

/** 当前题是否还留着上次作答（用于「已保留上次作答」提示与按钮禁用判断） */
const hasSavedPick = computed(() => {
  const q = current.value
  if (!q || !q.id || isProgramming.value) return false
  const r = pickMap.value[String(q.id)]
  if (!r) return false
  return !!String(r.a || '').trim() || !!(r.m && r.m.length)
})

/** 错题模式：本题在本次重做里答对了（后端已自动把它移出错题本） */
const isMastered = computed(() => masteredIds.value.has(Number(current.value.id)))

/* 切题/切回来统一走这里：**先按题目取回上次作答，再取回上次判分结果**。
   以前一律清空（answer=''），学生回头检查第 2 题时看到的是一道空白题，
   根本想不起来自己当时选了什么 —— 这正是要修的点。 */
function applyCurrent() {
  const q = current.value
  const qid = q && q.id ? String(q.id) : ''
  const rec = qid ? pickMap.value[qid] : null
  if (isProgramming.value) {
    /* 编程题走 restoreCode()，**不要**先把 answer 清成空串 ——
       清空会触发下面的 watch，等它 600ms 后就把空串写进草稿，
       刚恢复出来的代码被自己抹掉。代码按题号 + 语言存着，回来自动取回。 */
    // 每道题重置「手动选过语言」标志，并按题面要求自动切换语言
    // （必须放在 restoreCode 之前：lang 变了取的就是新语言的草稿/模板）
    langTouched.value = false
    autoSwitchLang(q)
    restoreCode()
    answerArr.value = []
    // 运行结果是上一题跑出来的，跟题走 —— 换题就清（连同控制台屏幕）
    clearConsole()
  } else if (q.type === 'multi') {
    answerArr.value = rec && Array.isArray(rec.m) ? rec.m.slice() : []
    answer.value = ''
  } else {
    answer.value = (rec && rec.a) || ''
    answerArr.value = []
  }
  result.value = qid ? (resultMap.value[qid] || null) : null
  // 取回了判分结果就把答题卡状态对齐，避免出现「题卡没颜色但有解析」的错位
  if (result.value) answers.value[index.value] = !!result.value.correct
  showReasoning.value = true
  showRef.value = false
}

/* ================= 编程题代码记忆 =================
 * 需求：编辑器要有记忆功能，刷新/切走再回来，代码还在。
 *
 * 分键维度与代码实验室一致：题目 id + 语言。
 * 只按题目 id 存的话，切语言会把上一个语言的代码当成新语言的作答。
 * 客观题（单选/多选/判断）不落盘 —— 那些答案提交后就已在服务端，
 * 本地再存一份只会让「上一题选了 B」在切回来时误导人。 */
const isProgramming = computed(() => current.value.type === 'programming')

/** 当前题目 + 语言的草稿键标识；非编程题返回空串（loadDraft 会直接返回 ''） */
function draftIdent() {
  return isProgramming.value && current.value.id ? String(current.value.id) : ''
}

function restoreCode() {
  if (!isProgramming.value) return
  const ident = draftIdent()
  if (!ident) return
  answer.value = loadDraft(SCOPE.PRACTICE, ident, lang.value) || baseTemplate(lang.value)
  // 运行输入跟着一起取：刷新回来接着调试时，测试数据不丢
  stdinText.value = loadStdin(SCOPE.PRACTICE, ident, lang.value) || ''
}

/* 运行输入的草稿：和代码同一套「题目 + 语言」分键，但独立存储 ——
   换语言时 scanf 的测试数据和前一语言的输入不该互相覆盖。 */
let stdinTimer = null
watch(stdinText, v => {
  const ident = draftIdent()
  if (!ident) return
  clearTimeout(stdinTimer)
  stdinTimer = setTimeout(() => saveStdin(SCOPE.PRACTICE, ident, lang.value, v), 500)
})

/* watch 回调里闭包捕获的 qid 一定是「作答发生时的那道题」——
   切题后 debounce 再触发也不会把旧答案写到新题名下（之前担心的串题问题不存在）。 */
let pracTimer = null
let pickTimer = null
watch(answer, v => {
  const q = current.value
  if (!q || !q.id) return
  if (q.type === 'programming') {
    clearTimeout(pracTimer)
    pracTimer = setTimeout(() => {
      const id = String(q.id)
      // 代码退回成基础模板就等于没写过，把草稿删掉 ——
      // 否则「清空重写」之后草稿还在，「重新做此题」会一直亮着
      const tpl = String(baseTemplate(lang.value) || '').trim()
      if (String(v || '').trim() === tpl) clearDraft(SCOPE.PRACTICE, id, lang.value)
      else saveDraft(SCOPE.PRACTICE, id, lang.value, v)
    }, 600)
    return
  }
  // 案例分析题整段文本最大 8000 字，逐键写 localStorage 太重，防抖 500ms
  if (q.type === 'case') {
    clearTimeout(pickTimer)
    pickTimer = setTimeout(() => savePick(q.id, { a: v }), 500)
    return
  }
  // 单选 / 判断：量小，直接写，切题前一定已经落盘
  savePick(q.id, { a: v })
})

/* 多选是数组内部增删（push/splice），不加 deep 监听不到；
   同样用闭包里的 qid，保证写到正确的题目上。 */
watch(answerArr, arr => {
  const q = current.value
  if (!q || q.type !== 'multi' || !q.id) return
  savePick(q.id, { m: arr.slice() })
}, { deep: true })

/* 切语言：旧语言的代码先落盘，新语言取回自己的草稿，没有就换基础模板。
   顺序不能反 —— 先存再改 lang，否则会存到新语言的键下。
   applyCurrent 里的自动切换要跳过这套逻辑（langAuto 标志）：
   那边的 restoreCode 已按新语言取好草稿，这里再跑会把新代码写进旧语言键下，
   还会误清新题刚取回的判分结果。 */
watch(lang, (nv, ov) => {
  if (langAuto.value) { langAuto.value = false; return }
  if (ov) {
    const ident = draftIdent()
    if (ident) {
      saveDraft(SCOPE.PRACTICE, ident, ov, answer.value)
      saveStdin(SCOPE.PRACTICE, ident, ov, stdinText.value)
    }
  }
  if (!isProgramming.value) return
  const ident = draftIdent()
  answer.value = (ident && loadDraft(SCOPE.PRACTICE, ident, nv)) || baseTemplate(nv)
  stdinText.value = (ident && loadStdin(SCOPE.PRACTICE, ident, nv)) || ''
  // 换了语言，上一语言的判分结果不再适用，本题的缓存也一起清掉
  if (ident) delete resultMap.value[ident]
  result.value = null
})

/** 「清空重写」：把当前这道题当前语言的草稿删掉，回到基础模板 */
function clearCode() {
  const ident = draftIdent()
  if (ident) clearDraft(SCOPE.PRACTICE, ident, lang.value)
  answer.value = baseTemplate(lang.value)
  result.value = null
  clearConsole()
  ElMessage.success('已清空，重新从模板开始')
}

function next() {
  if (index.value === questions.value.length - 1) {
    doneVisible.value = true
    return
  }
  index.value++
  applyCurrent()
}
function prev() {
  if (index.value > 0) {
    index.value--
    applyCurrent()
  }
}
function go(i) {
  index.value = i
  applyCurrent()
}

/* ================= 重新做此题 / 重新做此套题 =================
 * 保留上次答案之后必须给一个「从零再来」的出口，否则做过的题永远改不了答案：
 * 切回来直接是上次的选择 + 上次判分结果，选项是禁用的。 */
/** 本题是否值得重做（没动过就禁用，避免按钮一直亮着误导） */
const canRedo = computed(() => {
  if (result.value) return true
  const q = current.value
  if (!q) return false
  if (isProgramming.value) {
    const tpl = String(baseTemplate(lang.value) || '').trim()
    const draft = String(loadDraft(SCOPE.PRACTICE, String(q.id || ''), lang.value) || '').trim()
    // 代码和基础模板一模一样 = 还没动笔，不给重做
    return (!!draft && draft !== tpl) || String(answer.value || '').trim() !== tpl
  }
  return hasSavedPick.value || !!String(answer.value || '').trim() || !!answerArr.value.length
})

/** 重新做此题：只清这一道 —— 作答记录、判分结果、答题卡颜色、编程题草稿 */
function redoCurrent() {
  const q = current.value
  if (!q || !q.id) return
  dropPick(String(q.id))
  if (isProgramming.value) {
    clearDraft(SCOPE.PRACTICE, String(q.id), lang.value)
    answer.value = baseTemplate(lang.value)
    stdinText.value = ''          // 运行输入也属于作答，一并回到空白
    runResult.value = null
  } else {
    answer.value = ''
  }
  answers.value[index.value] = undefined
  answerArr.value = []
  result.value = null
  runResult.value = null
  showReasoning.value = true
  showRef.value = false
  ElMessage.success('已清空本题作答，可以重新做一遍')
}

/* 错题模式的结算口径：攻克的题数直接看 masteredIds（后端已同步移出错题本），
   剩下的 = 这套题里还没答对的。不看 correctCount —— 那是本轮作答的统计，
   切回旧题看结果时会重复计数。 */
const masteredCount = computed(() => masteredIds.value.size)
const remainWrongCount = computed(() =>
  questions.value.filter(q => !masteredIds.value.has(Number(q.id))).length
)

/** 整套题是否有进度（一套全新的题没必要弹「重新做此套题」） */
const hasAnyProgress = computed(() =>
  answeredCount.value > 0 || Object.keys(pickMap.value).length > 0 || Object.keys(resultMap.value).length > 0
)

/** 重新做此套题：清掉本套所有题的作答 + 判分 + 编程题草稿（各语言都清），回到第 1 题 */
async function redoAll() {
  try {
    await ElMessageBox.confirm(
      wrongMode.value
        // 错题模式要说清一件事：重做只清本地作答，答对的题不会「放回」错题本
        ? '将清空这套错题的全部作答记录与判分结果，从第 1 题重新做。已经答对的题已经掌握，不会回到错题本。'
        : '将清空这套题的全部作答记录、判分结果和编程题代码，回到第 1 题重新开始。确定吗？',
      wrongMode.value ? '重做这套错题' : '重新做此套题',
      { type: 'warning', confirmButtonText: '确定重做', cancelButtonText: '取消' }
    )
  } catch (e) {
    return // 用户取消
  }
  questions.value.forEach(q => {
    const id = String(q.id || '')
    if (!id) return
    delete pickMap.value[id]
    delete resultMap.value[id]
    // 整套重做就把所有语言的草稿都清掉，避免换个语言还能翻出旧作答
    if (q.type === 'programming') {
      PRACTICE_LANGS.forEach(l => {
        clearDraft(SCOPE.PRACTICE, id, l.value)
        saveStdin(SCOPE.PRACTICE, id, l.value, '')
      })
    }
  })
  persistPicks()
  answers.value = new Array(questions.value.length).fill(undefined)
  index.value = 0
  doneVisible.value = false
  applyCurrent()
  ElMessage.success(wrongMode.value ? '已重置这套错题，从第 1 题重新做' : '已重置整套题，从第 1 题重新开始')
}

/** 错题模式专属：完成弹窗里「再练一遍剩下的」——
    把已经攻克的题移出题集，只留还没答对的，作答与判分清零后从头再来。 */
function redoWrongSet() {
  const left = questions.value.filter(q => !masteredIds.value.has(Number(q.id)))
  if (!left.length) {
    doneVisible.value = false
    ElMessage.success('这套错题已经全部攻克啦')
    return
  }
  questions.value = left
  answers.value = new Array(left.length).fill(undefined)
  left.forEach(q => {
    const id = String(q.id)
    delete pickMap.value[id]
    delete resultMap.value[id]
    if (q.type === 'programming') {
      PRACTICE_LANGS.forEach(l => {
        clearDraft(SCOPE.PRACTICE, id, l.value)
        saveStdin(SCOPE.PRACTICE, id, l.value, '')
      })
    }
  })
  persistPicks()
  index.value = 0
  doneVisible.value = false
  applyCurrent()
  ElMessage.success(`还剩 ${left.length} 道错题，继续攻克`)
}
/** 载入题目（可按来源、难度、题型、掌握状态过滤） */
async function loadQuestions() {
  const kid = route.params.kid
  const params = {}
  if (source.value && source.value !== 'all') params.source = source.value
  if (difficulty.value) params.difficulty = difficulty.value
  if (typeFilter.value && typeFilter.value !== 'all') params.type = typeFilter.value
  let qs
  if (wrongMode.value) {
    /* 错题集来自错题本，只有 ids 白名单一个参数（「重做本页」用它精确锁定本页那几道）。
       来源 / 难度 / 题型在前端过滤：错题集通常就十几道，为它再开一组后端参数不值得。 */
    const p = {}
    if (route.query.ids) p.ids = String(route.query.ids)
    qs = await learnApi.wrongQuestions(p)
  } else {
    if (mastery.value && mastery.value !== 'all') params.mastery = mastery.value
    qs = await questionApi.byKnowledge(kid, params)
  }
  questions.value = (qs.data || []).filter(q => {
    if (source.value && source.value !== 'all' && q.source !== source.value) return false
    if (difficulty.value && Number(q.difficulty) !== Number(difficulty.value)) return false
    if (typeFilter.value && typeFilter.value !== 'all' && q.type !== typeFilter.value) return false
    return true
  })
  // 换筛选会换掉题目集合，但作答记录按题目 id 存，不受影响，不用清
  answers.value = new Array(questions.value.length).fill(undefined)
  loadPicks()
  // 从题库点「去做题」进来时带着 qid：直接定位到那一条，
  // 否则用户明明点了第 5 张卡，进来的却是这个知识点的第 1 题。
  focusQuestionId.value = route.query.qid ? Number(route.query.qid) : null
  index.value = 0
  if (focusQuestionId.value) {
    const i = questions.value.findIndex(q => Number(q.id) === focusQuestionId.value)
    if (i >= 0) index.value = i
  }
  applyCurrent()
}

function reload() {
  // 手动刷新要能兜住接口异常，否则点一下整页退回「暂无习题」
  focusQuestionId.value = null
  loadQuestions().catch(() => ElMessage.error('题目加载失败，请稍后重试'))
}

/** 是否加了筛选（决定空状态文案与「清空筛选」入口） */
const hasFilters = computed(() =>
  mastery.value !== 'all' || source.value !== 'all' || !!difficulty.value || typeFilter.value !== 'all'
)

/* 空状态文案要说清「为什么没有题」：
   筛没了的、都答对了的、本来就没题的，是三种完全不同的处境，
   一律显示「暂无配套习题」会让人以为题库坏了。 */
const emptyText = computed(() => {
  if (wrongMode.value) return '错题本是空的，保持得很好！'
  if (mastery.value === 'wrong') return '错题本里还没有这个知识点的题'
  if (mastery.value === 'unmastered') return '这个知识点的题你都答对过了，换「全部题目」再练练'
  if (hasFilters.value) return '当前筛选没有匹配的题目'
  return '该知识点暂无配套习题'
})

/** 清空筛选：筛成空集时的一键退路 */
function resetFilters() {
  source.value = 'all'
  difficulty.value = 0
  typeFilter.value = 'all'
  mastery.value = 'all'
  reload()
}

/* ---------- 页面内导航 ---------- */
const canBack = ref(true)

function goBack() {
  canBack.value = false
  router.back()
}

/** 返回来源列表：从题库进来的回题库（带筛选），错题重做回错题本，否则回知识点 */
function goBackToList() {
  if (route.query.from === 'qbank') router.push('/question')
  else if (wrongMode.value) router.push('/profile?tab=wrong')
  else if (knowledgeRoute.value) router.push(knowledgeRoute.value)
  else router.push('/courses')
}

/** 「看动画搞懂它」：错题模式每题自带知识点，直接按当前题跳，不能套用整页的 knowledgeRoute */
function openVis() {
  if (wrongMode.value) {
    const r = labOf(current.value.knowledge_route, current.value.knowledge_id).path
    router.push(r || '/courses')
    return
  }
  if (knowledgeRoute.value) router.push(knowledgeRoute.value)
  else router.push('/courses')
}

onMounted(async () => {
  canBack.value = !!window.history.state
  const kid = route.params.kid
  await reload()
  if (wrongMode.value) {
    // 错题集没有统一知识点，面包屑与「返回」都指向错题本
    knowledgeName.value = '错题重做'
    return
  }
  try {
    const kd = await courseApi.knowledge(kid)
    if (kd.data) {
      knowledgeName.value = kd.data.knowledge.name
      knowledgeRoute.value = kd.data.knowledge.route
    }
  } catch (e) {
    // 知识点信息取不到只影响面包屑和「看动画」，不影响做题
  }
})
</script>

<style scoped>
/* ---------- 筛选条 + 页面内导航 ---------- */
.filter-bar { padding: 12px 14px; margin-bottom: 14px; }
/* 编辑器下方的「已自动保存 / 清空重写」一行 */
.code-foot {
  display: flex; align-items: center; justify-content: space-between;
  gap: 10px; flex-wrap: wrap; margin-top: 7px;
}
.code-foot > span { display: flex; align-items: center; gap: 4px; min-width: 0; }

/* ---------- 控制台（输入 + 输出同一个框）：与代码实验室共用 RunConsole ---------- */
.run-box { margin-top: 10px; }
.run-head { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; flex-wrap: wrap; }
.run-head > b { font-size: 14px; }
.run-head .run-actions { margin-left: auto; }
/* 组件内部靠 flex 吃满父容器，本身不写死高度 —— 这里给它一块明确的地盘 */
.run-box :deep(.run-console) { min-height: 200px; max-height: 340px; }
.nav-btns { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 10px; }
.nav-btns .el-button { margin-left: 0; }
.filter-row {
  display: grid; gap: 10px 14px;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 190px), 1fr));
  align-items: end;
  padding-top: 10px; border-top: 1px dashed var(--border);
}
.filter-item { display: flex; flex-direction: column; gap: 5px; min-width: 0; }
/* 筛成空集时的退路提示 */
.filter-empty-tip { display: flex; align-items: center; justify-content: center; gap: 2px; margin-top: 4px; }
.filter-item :deep(.el-select) { width: 100%; }
.filter-label { font-size: 12px; color: var(--text-3); font-weight: 500; }
.filter-stat {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  font-size: 12.5px; padding-bottom: 1px;
}
.f-num { color: var(--brand); font-variant-numeric: tabular-nums; }

.q-card { padding: 22px; }
.q-head { display: flex; justify-content: space-between; align-items: center; }
.q-title { font-size: 16px; line-height: 1.8; margin: 14px 0 18px; font-weight: 600; white-space: pre-wrap; }
.opt-group { width: 100%; }
.opt-item {
  border: 1px solid var(--border); border-radius: 8px; padding: 10px 14px; margin-bottom: 10px;
  cursor: pointer; transition: all .2s; background: var(--card);
  /* 选项里常是一整行代码（s->next=p->next; p->next=s; 中间没空格），
     不断字的话最小宽度会超过折叠屏外屏的可用宽度 */
  overflow-wrap: anywhere; word-break: break-word;
}
/* Element Plus 的 el-radio 自带 white-space: nowrap —— 代码类选项会被它锁成一行，
   在 280px 宽下把卡片顶出视口 30px。这里放开换行，并让圆点与多行文本顶部对齐 */
.opt-item :deep(.el-radio) {
  white-space: normal; width: 100%; height: auto;
  align-items: flex-start; margin-right: 0;
}
/* el-checkbox 与 el-radio 的 DOM 不同，但都要放开换行、顶部对齐 */
.opt-item :deep(.el-checkbox) {
  white-space: normal; width: 100%; height: auto;
  align-items: flex-start; margin-right: 0;
}
.opt-item :deep(.el-radio__input), .opt-item :deep(.el-checkbox__input) { flex-shrink: 0; margin-top: 2px; }
.opt-item :deep(.el-radio__label), .opt-item :deep(.el-checkbox__label) { white-space: normal; overflow-wrap: anywhere; word-break: break-word; }
.opt-item:hover { border-color: var(--brand-2); }
.opt-item.selected { border-color: var(--brand); background: var(--brand-light); }
.opt-item.right { border-color: var(--success); background: var(--success-light); }
.opt-item.wrong { border-color: var(--danger); background: var(--danger-light); }
.opt-key { font-weight: 700; margin-right: 8px; }
.opt-text { line-height: 1.6; }
.result-box { border-radius: 8px; padding: 12px 14px; margin-bottom: 14px; }
.result-box.ok { background: var(--success-light); border: 1px solid var(--success-border); }
.result-box.bad { background: var(--danger-light); border: 1px solid var(--danger-border); }
.result-head { display: flex; align-items: center; gap: 8px; font-size: 14px; margin-bottom: 6px; }
.result-box.ok .result-head { color: var(--success); }
.result-box.bad .result-head { color: var(--danger); }
.analysis { font-size: 13px; line-height: 1.8; color: var(--text-2); white-space: pre-wrap; }

/* 主观题作答区 */
.subjective { margin-bottom: 14px; }
.sub-tip {
  background: var(--brand-light); border-radius: 6px; padding: 8px 12px; margin-bottom: 10px; line-height: 1.6;
}
.quick-bar { display: flex; align-items: center; gap: 8px; margin-top: 8px; flex-wrap: wrap; }
.lang-bar { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }

/* 主观题判分结果 */
.grade-box { border: 1px solid var(--border); border-radius: 8px; padding: 14px; margin-bottom: 14px; background: var(--card); }
.grade-head { display: flex; align-items: center; gap: 14px; padding-bottom: 10px; border-bottom: 1px dashed var(--border); flex-wrap: wrap; }
.grade-score b { font-size: 28px; color: var(--brand); }
.grade-score span { font-size: 13px; color: var(--text-2); }
.grade-head.ok .grade-score b { color: var(--success); }
.grade-head.bad .grade-score b { color: var(--danger); }
.grade-meta { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.comment { margin-top: 10px; }
.reasoning {
  background: var(--brand-light); border: 1px solid var(--border); border-radius: 6px; padding: 8px 12px; margin-top: 10px;
}
.reasoning-title {
  display: flex; justify-content: space-between; align-items: center; cursor: pointer;
  font-size: 13px; font-weight: 600; color: var(--brand);
}
.reasoning-list { margin: 8px 0 0; padding-left: 18px; }
.reasoning-list li { font-size: 12.5px; line-height: 1.9; color: var(--text-2); }
.cheat-tip {
  display: flex; align-items: flex-start; gap: 8px; margin-top: 10px; padding: 8px 12px;
  background: var(--warning-light); border: 1px solid var(--warn-border); border-radius: 6px; font-size: 13px; line-height: 1.7; color: var(--warn-strong);
}
.point-block { margin-top: 10px; }
.point-block ul { margin: 6px 0 0; padding-left: 18px; }
.point-block li { line-height: 1.9; color: var(--text-2); }
.point-block em { font-style: normal; color: var(--text-3, #999); }
.ref-block { margin-top: 12px; border-top: 1px dashed var(--border); padding-top: 10px; }
.ref-head { display: flex; justify-content: space-between; align-items: center; cursor: pointer; }
.ref-body {
  background: var(--code-bg); border-radius: 6px; padding: 12px; margin: 8px 0 0;
  font-size: 12.5px; line-height: 1.8; white-space: pre-wrap; word-break: break-all; max-height: 320px; overflow: auto;
}
.q-actions { display: flex; gap: 10px; flex-wrap: wrap; }
/* 侧栏两个按钮：桌面并排，窄屏各占一行，不挤成一团 */
.side-btns { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 10px; }
.side-btns .el-button { margin-left: 0; }
.side-card { padding: 16px; }
.panel-title { font-size: 13px; font-weight: 600; margin-bottom: 8px; color: var(--text-2); }
/* 答题卡：桌面保持 5 列一排的整齐感；窄屏自动按 38px 最小格宽铺排，不溢出 */
.card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(38px, 1fr)); gap: 6px; }
.card-cell {
  height: 30px; line-height: 30px; text-align: center; border-radius: 6px; cursor: pointer;
  border: 1px solid var(--border); font-size: 12px; background: var(--card);
}
.card-cell.cur { border-color: var(--brand); background: var(--brand-light); color: var(--brand); font-weight: 700; }
.card-cell.right { background: var(--success-light); border-color: var(--success); color: var(--success-strong); }
.card-cell.wrong { background: var(--danger-light); border-color: var(--danger); color: var(--danger-strong); }
.stat-line { display: flex; justify-content: space-between; padding: 4px 0; font-size: 13px; }
.done-box { text-align: center; }
.score { font-size: 40px; font-weight: 700; color: var(--brand); }

/* ---------- 响应式 ---------- */
@media (max-width: 768px) {
  .q-card { padding: 16px 14px; }
  .q-head { flex-wrap: wrap; gap: 8px; }
  .q-head :deep(.el-progress) { width: 100% !important; }
  .q-title { font-size: 15px; margin: 12px 0 14px; }
}
@media (max-width: 480px) {
  .nav-btns .el-button { flex: 1 1 100%; margin-left: 0 !important; }
  .filter-row { grid-template-columns: 1fr; }
  .opt-item { padding: 9px 11px; }
}
</style>
