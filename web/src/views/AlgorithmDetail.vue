<template>
  <div class="page algo-page" v-loading="loading">
    <!-- 页面内导航：详情页必须能一键回到列表（带上原筛选条件），否则用户筛选半天点进详情就丢了 -->
    <div class="detail-nav card">
      <el-button size="small" :disabled="!canBack" @click="goBack">
        <el-icon><ArrowLeft /></el-icon> 上一步
      </el-button>
      <el-button size="small" type="primary" plain @click="backToList">
        <el-icon><Back /></el-icon> 返回算法题列表
      </el-button>
    </div>

    <el-breadcrumb separator="/" style="margin-bottom:12px">
      <el-breadcrumb-item :to="listPath">程序设计算法题</el-breadcrumb-item>
      <el-breadcrumb-item>{{ algo.title || '题目详情' }}</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 三栏：题目 30% / 写代码 70%；开助手后 题目 30% / 代码 45% / 助手 25%。
         用内嵌列而不是抽屉浮层，是为了让「读题 / 写代码 / 问助手」三件事
         真正能并排进行，助手不会盖住代码。 -->
    <div class="algo-work" :class="{ 'with-assist': assistantOpen }">
      <!-- ================= 左：题目 ================= -->
      <section class="card panel problem-panel">
        <div class="p-head">
          <h2 class="p-title">{{ algo.title }}</h2>
          <div class="p-meta">
            <el-tag size="small" :type="diffType(algo.difficulty)" effect="light">
              {{ algo.difficultyText || '中等' }} {{ '★'.repeat(algo.difficulty || 3) }}
            </el-tag>
            <span class="weight-badge">
              <el-icon><Trophy /></el-icon> 权值 {{ algo.weight }}
            </span>
            <el-tag v-if="algo.source" size="small" effect="plain" type="info">{{ algo.source }}</el-tag>
            <el-tag v-for="t in algo.tags || []" :key="t" size="small" effect="plain">{{ t }}</el-tag>
          </div>
          <div class="small muted">
            提交 {{ algo.submitCount || 0 }} 次 · 通过 {{ algo.acceptedCount || 0 }} 次
            <template v-if="algo.myBest">
              · 我的最好成绩
              <b :style="{ color: algo.myBest.status === 'accepted' ? 'var(--success)' : 'var(--danger)' }">
                {{ algo.myBest.status === 'accepted' ? '已通过' : '未通过' }} {{ algo.myBest.score }}/{{ algo.myBest.maxScore }}
              </b>
            </template>
          </div>
        </div>

        <el-tabs v-model="tab" class="p-tabs">
          <!-- ---------- 题面 ---------- -->
          <el-tab-pane label="题目描述" name="desc">
            <div class="tab-body">
              <div class="sec">
                <div class="sec-title">题面</div>
                <div class="markdown-body desc" v-html="render(algo.description)"></div>
              </div>

              <div class="sec two-col">
                <div>
                  <div class="sec-title">输入格式</div>
                  <pre class="mono">{{ algo.inputDesc || '见题面说明' }}</pre>
                </div>
                <div>
                  <div class="sec-title">输出格式</div>
                  <pre class="mono">{{ algo.outputDesc || '见题面说明' }}</pre>
                </div>
              </div>

              <div class="sec">
                <div class="sec-title">样例</div>
                <div v-if="samples.length" class="sample-list">
                  <div v-for="(s, i) in samples" :key="i" class="sample">
                    <div class="sample-head">
                      <span>样例 {{ i + 1 }}</span>
                      <el-button size="small" text type="primary" @click="loadSampleToEditor(s)">填入编辑器</el-button>
                    </div>
                    <div class="sample-body">
                      <div class="sample-col">
                        <div class="sample-label">输入</div>
                        <pre class="mono">{{ s.stdin }}</pre>
                      </div>
                      <div class="sample-col">
                        <div class="sample-label">输出</div>
                        <pre class="mono">{{ s.expected }}</pre>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else class="sample">
                  <div class="sample-body">
                    <div class="sample-col">
                      <div class="sample-label">输入</div>
                      <pre class="mono">{{ algo.sampleInput || '（无）' }}</pre>
                    </div>
                    <div class="sample-col">
                      <div class="sample-label">输出</div>
                      <pre class="mono">{{ algo.sampleOutput || '（无）' }}</pre>
                    </div>
                  </div>
                </div>
              </div>

              <div class="sec">
                <el-button size="small" type="warning" plain @click="hintOpen = !hintOpen">
                  <el-icon><View /></el-icon> {{ hintOpen ? '收起提示' : '看提示' }}
                </el-button>
                <div v-show="hintOpen" class="hint-box">
                  <div class="small muted" style="margin-bottom:6px">提示会剧透思路，建议先自己想 10 分钟再看。</div>
                  <pre class="mono hint-text">{{ algo.hints || '这道题暂时没有提示，可以点右下角的算法小助手。' }}</pre>
                </div>
              </div>

              <!-- 参考答案：点击才请求，可一键复制 -->
              <div class="sec">
                <div class="sol-actions">
                  <el-button size="small" type="danger" plain :loading="solLoading" @click="loadSolution">
                    <el-icon><Unlock /></el-icon> {{ solution ? '已显示参考答案' : '查看参考答案' }}
                  </el-button>
                  <el-button v-if="solution && solution.code" size="small" plain @click="copyText(solution.code, '参考答案')">
                    <el-icon><CopyDocument /></el-icon> 复制代码
                  </el-button>
                  <el-button v-if="solution && solution.code" size="small" plain @click="useSolution">
                    <el-icon><EditPen /></el-icon> 载入到编辑器
                  </el-button>
                </div>
                <div v-if="solution" class="sol-box">
                  <div class="sol-head">
                    <!-- 多语言参考答案：一题可能只有部分语言有答案（库里原本 200 道全是 Python），
                         没配的语言在下面列出来但标「暂无」，不拿别的语言冒充。 -->
                    <el-select
                      v-if="solLangs.length"
                      :model-value="solution.language"
                      size="small"
                      class="sol-lang"
                      title="切换参考答案的语言"
                      @change="onSolLangChange"
                    >
                      <el-option
                        v-for="l in solLangs" :key="l.value"
                        :value="l.value" :label="l.label"
                        :disabled="!l.has"
                      >
                        <span class="sol-opt">
                          <span>{{ l.label }}</span>
                          <span v-if="!l.has" class="sol-opt-none">暂无</span>
                        </span>
                      </el-option>
                    </el-select>
                    <el-tag v-else size="small" effect="light">{{ langLabel(solution.language) }}</el-tag>
                    <span class="small muted">{{ solution.tip }}</span>
                  </div>
                  <pre class="mono code-block">{{ solution.code || '（该题尚未配置参考答案）' }}</pre>
                </div>
              </div>

              <div v-if="algo.knowledge" class="sec">
                <el-button size="small" plain @click="$router.push(algo.knowledge.route)">
                  <el-icon><Reading /></el-icon> 相关知识点：{{ algo.knowledge.name }}
                </el-button>
              </div>
            </div>
          </el-tab-pane>

          <!-- ---------- 题解区 ---------- -->
          <el-tab-pane :label="`题解（${solutions.length}）`" name="solution">
            <div class="tab-body">
              <div class="sol-toolbar">
                <span class="small muted">写下你的思路，帮后来的同学少走弯路（支持 Markdown 与代码块）</span>
                <el-button type="primary" size="small" @click="openSolutionEditor">
                  <el-icon><EditPen /></el-icon> 写题解
                </el-button>
              </div>

              <el-empty v-if="!solutions.length" description="还没有人发题解，来写第一篇" :image-size="70" />
              <div v-for="s in solutions" :key="s.id" class="sol-item">
                <div class="sol-item-head">
                  <b class="sol-title">{{ s.title }}</b>
                  <el-tag size="small" effect="plain">{{ langLabel(s.language) }}</el-tag>
                  <span class="small muted">{{ s.author }} · {{ formatTime(s.createdAt) }}</span>
                  <span class="sol-item-ops">
                    <el-button size="small" text :type="s.liked ? 'primary' : 'default'" @click="toggleLike(s)">
                      👍 {{ s.likes }}
                    </el-button>
                    <el-button v-if="s.isMine || isAdmin" size="small" text type="danger" @click="removeSolution(s)">删除</el-button>
                  </span>
                </div>
                <div class="markdown-body sol-content" v-html="render(s.content)"></div>
              </div>
            </div>
          </el-tab-pane>

          <!-- ---------- 提交记录 ---------- -->
          <el-tab-pane :label="`提交记录（${mySubmits.length}）`" name="submit">
            <div class="tab-body">
              <div class="small muted" style="margin-bottom:8px">
                点「载入代码」可以把任意一次历史提交回填到右侧编辑器，从上次写到一半的地方继续。
              </div>
              <el-table v-if="mySubmits.length" :data="mySubmits" size="small" stripe>
                <el-table-column prop="id" label="#" width="70" />
                <el-table-column label="语言" width="80">
                  <template #default="{ row }">{{ langLabel(row.language) }}</template>
                </el-table-column>
                <el-table-column label="状态" width="100">
                  <template #default="{ row }">
                    <el-tag size="small" :type="statusType(row.status)" effect="light">{{ statusText(row.status) }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="用例" width="76">
                  <template #default="{ row }">{{ row.passed }}/{{ row.total }}</template>
                </el-table-column>
                <el-table-column label="得分" width="80">
                  <template #default="{ row }">{{ row.score }}/{{ row.max_score }}</template>
                </el-table-column>
                <el-table-column label="耗时" width="80">
                  <template #default="{ row }">{{ row.runtime }} ms</template>
                </el-table-column>
                <el-table-column label="时间" width="140">
                  <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
                </el-table-column>
                <el-table-column label="操作" width="150">
                  <template #default="{ row }">
                    <el-button size="small" text type="primary" :disabled="!row.code" @click="useSubmitCode(row)">
                      载入代码
                    </el-button>
                    <el-button size="small" text @click="copyText(row.code, '提交代码')" :disabled="!row.code">复制</el-button>
                  </template>
                </el-table-column>
              </el-table>
              <el-empty v-else description="还没有提交记录，写一段代码试试" :image-size="60" />
            </div>
          </el-tab-pane>
        </el-tabs>
      </section>

      <!-- ================= 右：写代码 ================= -->
      <section class="card panel code-panel">
        <div class="edit-head">
          <span class="sec-title" style="margin:0">写代码</span>
          <div class="edit-head-right">
            <span v-if="savedTip" class="small muted save-tip">
              <el-icon><Select /></el-icon> {{ savedTip }}
            </span>
            <!-- 换语言时同步换模板由 watch(language) 负责：
                 el-select 的 change 只抛新值，拿不到旧语言，别在这里做草稿切换 -->
            <el-select v-model="language" size="small" class="lang-select" title="切换编程语言，代码模板会同步替换">
              <el-option v-for="l in LANGS" :key="l.value" :value="l.value" :label="l.label" />
            </el-select>
          </div>
        </div>

        <CodeEditor v-model="code" :language="language" :height="430" :running="running" @run="runCode" />

        <div class="edit-foot">
          <el-button plain :loading="running" :disabled="!code.trim()" @click="runCode">
            <el-icon><CaretRight /></el-icon> 运行（样例 · 不计提交）
          </el-button>
          <el-button type="primary" :loading="running" :disabled="!code.trim()" @click="submit">
            <el-icon><Upload /></el-icon> 提交判题
          </el-button>
          <el-button plain :disabled="!code.trim()" @click="saveNow">保存草稿</el-button>
          <span class="small muted">Ctrl + Enter 运行 · 控制台里敲了数据就跑那组输入，没敲就跑样例；「提交判题」才会计入提交次数</span>
        </div>

        <!-- 运行结果：与代码实验室同款 —— 常驻面板 + 清空/放大/收起三档 -->
        <div class="card out-card">
          <div v-if="dock === 'collapsed'" class="dock-mini" @click="dock = 'normal'">
            <el-icon><ArrowUp /></el-icon>
            <b>运行结果</b>
            <span class="muted small">已收起 · 点击展开</span>
          </div>

          <div v-show="dock !== 'collapsed'" class="dock-body" :class="{ expanded: dock === 'expanded' }">
            <div class="out-head">
              <b>运行结果</b>
              <template v-if="result">
                <el-tag :type="statusType(result.status)" effect="dark" size="small">{{ statusText(result.status) }}</el-tag>
                <!-- 自定义输入那条通道没有标准答案，判题口径的「通过用例/得分」全都不成立 -->
                <span v-if="result.custom" class="small muted">自定义输入 · 只看输出，不比对答案</span>
                <template v-else>
                  <span v-if="result.sample" class="small muted">样例运行 · 不计入提交记录</span>
                  <span class="small">通过用例 <b>{{ result.passed }}/{{ result.total }}</b></span>
                  <span v-if="!result.sample" class="small">得分 <b>{{ result.score }}/{{ result.maxScore }}</b></span>
                </template>
                <span class="small muted" v-if="result.runtime">耗时 {{ result.runtime }} ms</span>
              </template>
              <span class="head-actions">
                <el-button size="small" plain :disabled="!result" @click="clearResult">清空</el-button>
                <el-button size="small" plain @click="cycleDock">{{ dockBtnLabel }}</el-button>
                <el-button size="small" plain @click="dock = 'collapsed'">
                  <el-icon><ArrowDown /></el-icon> 收起
                </el-button>
              </span>
            </div>

            <!-- 控制台：输入与输出同一个黑框（与代码实验室、随堂练习同一套组件） -->
            <RunConsole
              ref="consoleEl"
              v-model="stdinText" :code="code"
              :output="consoleOutput" :stderr="consoleError"
              :error="!!result && result.status !== 'accepted' && result.status !== 'custom'"
              :time="result ? result.runtime : 0"
              :running="running" :result-key="runSeq"
              @run="runCode"
            />

            <div v-if="failedCases.length" class="case-box">
              <div class="small muted" style="margin-bottom:6px">失败用例（最多展示 3 个）</div>
              <div v-for="(c, i) in failedCases" :key="i" class="case">
                <div class="case-row">
                  <div class="case-col">
                    <div class="case-label">输入</div>
                    <pre class="mono">{{ c.stdin }}</pre>
                  </div>
                  <div class="case-col">
                    <div class="case-label">期望输出</div>
                    <pre class="mono ok-text">{{ c.expected }}</pre>
                  </div>
                  <div class="case-col">
                    <div class="case-label">实际输出</div>
                    <pre class="mono bad-text">{{ c.actual || '（无输出）' }}</pre>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ================= 右：算法小助手（按需展开，占 25%）================= -->
      <aside v-show="assistantOpen" class="card panel assist-panel">
        <div class="assist-head">
          <b><el-icon><MagicStick /></el-icon> 算法小助手</b>
          <el-button size="small" text @click="assistantOpen = false">
            <el-icon><DArrowRight /></el-icon> 收起
          </el-button>
        </div>
        <AlgoAssistant :algorithm-id="algoId" :code="code" :language="language" />
      </aside>
    </div>

    <!-- 悬浮入口：助手收起时显示 -->
    <button v-show="!assistantOpen" class="assistant-fab" @click="assistantOpen = true" title="打开算法小助手">
      <el-icon><MagicStick /></el-icon>
      <span>算法小助手</span>
    </button>

    <!-- 写题解对话框 -->
    <el-dialog v-model="solEditorVisible" title="写题解" width="680px" top="6vh">
      <el-form label-position="top">
        <el-form-item label="标题">
          <el-input v-model="solForm.title" maxlength="80" show-word-limit placeholder="例如：单调栈一遍扫描 O(n)" />
        </el-form-item>
        <el-form-item label="正文（支持 Markdown，代码请用 ``` 包裹）">
          <el-input v-model="solForm.content" type="textarea" :rows="12" placeholder="先说思路，再贴代码，最后写复杂度与易错点。" />
        </el-form-item>
        <el-form-item label="题解使用的语言">
          <el-select v-model="solForm.language" style="width:160px">
            <el-option v-for="l in LANGS" :key="l.value" :value="l.value" :label="l.label" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="solEditorVisible = false">取消</el-button>
        <el-button type="primary" :loading="solSaving" @click="submitSolution">发布题解</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { algorithmApi } from '@/api'
import { renderMd } from '../utils/markdown'
import { ElMessage, ElMessageBox } from 'element-plus'
import CodeEditor from '@/components/CodeEditor.vue'
import RunConsole from '@/components/RunConsole.vue'
import AlgoAssistant from '@/components/AlgoAssistant.vue'
import { useUserStore } from '@/stores/user'
import { restoreFilterSnapshot } from '@/utils/filterState'
import { SCOPE, loadDraft as loadDraftStore, saveDraft as saveDraftStore, loadStdin, saveStdin } from '@/utils/draftStore'
import { LANG_ORDER, langLabel } from '@/utils/codeTemplates'
import {
  Trophy, View, Unlock, Reading, CaretRight, MagicStick, CopyDocument,
  EditPen, Select, DArrowRight, Upload, ArrowLeft, Back, ArrowUp, ArrowDown
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const store = useUserStore()
const algoId = computed(() => route.params.id)
const isAdmin = computed(() => (store.userInfo && store.userInfo.role) === 'admin')

/* ---------- 返回列表：带上原来的筛选条件 ----------
   从列表点进来时列表已经把条件写进了 URL，也存了 sessionStorage 快照。
   这里两者取其一重建 query，用户点「返回算法题列表」看到的还是刚才那批题。 */
const snap = restoreFilterSnapshot('algo')
const listQuery = computed(() => {
  const q = {}
  if (snap) {
    if (snap.state.difficulty) q.difficulty = snap.state.difficulty
    if (snap.state.tag) q.tag = snap.state.tag
    if (snap.state.source) q.source = snap.state.source
    if (snap.state.keyword) q.keyword = snap.state.keyword
    if (snap.page && snap.page > 1) q.page = snap.page
  }
  return q
})
const listPath = computed(() => ({ path: '/algorithm', query: listQuery.value }))
const canBack = ref(true)
function goBack() { canBack.value = false; router.back() }
function backToList() { router.push(listPath.value) }

const loading = ref(false)
const algo = ref({})
const samples = ref([])
const tab = ref('desc')

const language = ref('python')
const code = ref('')
const running = ref(false)
const result = ref(null)

/** 控制台里敲的运行输入（自定义 stdin）—— 与代码实验室、随堂练习同一套交互 */
const stdinText = ref('')
const consoleEl = ref(null)
/** 每跑完一次自增，驱动控制台往会话流水里追加一段结果 */
const runSeq = ref(0)

/** 控制台要显示的正文 / 错误：algorithm 的 run 只回一个 consoleLog，
 *  出错时额外把 message（失败原因、编译错误）贴在下面，别让用户对着空面板猜。 */
const consoleOutput = computed(() => {
  const r = result.value
  if (!r) return ''
  const body = String(r.consoleLog || '')
  const extra = r.status === 'custom' ? '' : String(r.message || '')
  if (!extra) return body
  // consoleLog 已经把 stdout 原样带回来了，message 是同一件事的第二视角（比对结论）
  return (body ? body.replace(/\n+$/, '') + '\n\n' : '') + '— 判题结论 —\n' + extra
})
const consoleError = computed(() => {
  const r = result.value
  if (!r) return ''
  return r.status === 'custom' ? '' : String(r.message || '')
})

/** 运行结果面板三档：常规 / 放大 / 收起 —— 与代码实验室同款交互 */
const dock = ref('normal')
const dockBtnLabel = computed(() =>
  dock.value === 'collapsed' ? '展开' : dock.value === 'expanded' ? '还原' : '放大'
)
function cycleDock() {
  dock.value = dock.value === 'collapsed' ? 'normal' : dock.value === 'expanded' ? 'normal' : 'expanded'
}
/** 收起/窄化状态下点运行，自动把面板放出来 —— 不然点了像没反应 */
function ensureDockVisible() {
  if (dock.value !== 'normal') dock.value = 'normal'
}
const mySubmits = ref([])
const savedTip = ref('')

const hintOpen = ref(false)
const solLoading = ref(false)
const solution = ref(null)

const solutions = ref([])
const solEditorVisible = ref(false)
const solSaving = ref(false)
const solForm = ref({ title: '', content: '', language: 'python' })

const assistantOpen = ref(false)

/* 下拉里的语言项。顺序从 utils/codeTemplates 的 LANG_ORDER 取，
   全站统一为 C → C++ → Java → Python → JavaScript。
   原来是 python 打头（因为库里最初只有 Python 参考答案），
   同一个下拉在代码实验室和这里顺序不同，看着像两套东西。 */
const LANGS = LANG_ORDER
  .filter(l => ['c', 'cpp', 'java', 'python', 'javascript'].includes(l))
  .map(l => ({ value: l, label: langLabel(l) }))

/* 每种语言的算法竞赛模板。
 * 关键点：每份都自带「怎么读标准输入」，否则新手切完语言第一件事就是卡在读数上。
 * 输入格式以题目下方的样例为准，按需改用 BufferedReader / getline 等更合适的方式。
 *
 * 和 utils/codeTemplates.js 的 BASE_TEMPLATES 分工：
 *   - BASE_TEMPLATES 是「编辑器空白骨架」，给代码实验室/随堂练习用（只含 main 框架）
 *   - 这里的 TEMPLATES 是「算法竞赛模板」，多了整块读 stdin + 切分的样板
 * 两处用途不同，故意不合并，避免在实验室里塞进一堆竞赛读数代码。 */
const TEMPLATES = {
  python:
`import sys

def main():
    # 一次性读完再按空白切分，跨行输入也不会漏
    data = sys.stdin.read().split()
    if not data:
        return
    # TODO: 在这里实现你的解法（样例：a, b = int(data[0]), int(data[1])）
    print()

if __name__ == "__main__":
    main()
`,
  c:
`#include <stdio.h>
#include <stdlib.h>

int main(void) {
    // TODO: 在这里实现你的解法
    // 需要读输入时用：int a, b; if (scanf("%d %d", &a, &b) == 2) { ... }
    // 需要输出时用：printf("%d\\n", ans);
    return 0;
}
`,
  cpp:
`#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
using namespace std;

int main() {
    ios::sync_with_stdio(false);   // 关同步，cin 快很多
    cin.tie(nullptr);              // 解除 cout 与 cin 的绑定
    // TODO: 在这里实现你的解法（样例：int a, b; if (cin >> a >> b) { ... }）
    return 0;
}
`,
  java:
`import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        // 一次性读完再切分，跨行输入也不会漏
        Scanner sc = new Scanner(System.in);
        StringBuilder sb = new StringBuilder();
        while (sc.hasNext()) sb.append(sc.next()).append(' ');
        String[] data = sb.toString().trim().split("\\\\s+");
        if (data.length == 0) return;
        // TODO: 在这里实现你的解法（样例：int a = Integer.parseInt(data[0])）
        System.out.println();
    }
}
`,
  javascript:
`// Node 读标准输入：先整块读进来，再按空白切分
const data = require('fs').readFileSync(0, 'utf8').trim().split(/\\s+/);
if (data.length === 1 && data[0] === '') {
  // 没有输入，直接结束
  process.exit(0);
}
// TODO: 在这里实现你的解法（样例：const a = Number(data[0]), b = Number(data[1])）
console.log('');
`
}


const STATUS = {
  accepted: { text: '通过', type: 'success' },
  custom: { text: '自定义输入', type: 'info' },
  wrong_answer: { text: '答案错误', type: 'danger' },
  compile_error: { text: '编译失败', type: 'warning' },
  runtime_error: { text: '运行错误', type: 'danger' },
  timeout: { text: '运行超时', type: 'warning' }
}

const failedCases = computed(() => (result.value && result.value.cases ? result.value.cases.slice(0, 3) : []))

/* ================= 草稿本地持久化 =================
 * 需求：写一半的代码要能留下来。按「题目 + 语言」分别存，
 * 换语言不会互相覆盖；同时保留每个语言最后一次的草稿。
 * 实现走统一的 draftStore（见 utils/draftStore.js），代码实验室与随堂练习共用一套。 */
function loadDraft(lang) {
  return loadDraftStore(SCOPE.ALGO, algoId.value, lang)
}
function saveDraft(lang, text) {
  saveDraftStore(SCOPE.ALGO, algoId.value, lang, text)
}

/* 运行输入的草稿：与代码同键位（题目 + 语言）、分开存放 ——
   换语言时上一份测试数据不该顶掉这一份，反过来也一样。 */
function loadStdinDraft(lang) {
  return loadStdin(SCOPE.ALGO, algoId.value, lang) || ''
}
let stdinTimer = null
watch(stdinText, v => {
  if (!algoId.value) return
  clearTimeout(stdinTimer)
  stdinTimer = setTimeout(() => saveStdin(SCOPE.ALGO, algoId.value, language.value, v), 500)
})

function saveNow() {
  saveDraft(language.value, code.value)
  savedTip.value = '草稿已保存'
  setTimeout(() => { if (savedTip.value === '草稿已保存') savedTip.value = '' }, 1800)
}

let saveTimer = null
watch(code, v => {
  if (!algoId.value) return
  clearTimeout(saveTimer)
  saveTimer = setTimeout(() => {
    saveDraft(language.value, v)
    savedTip.value = '已自动保存 ' + new Date().toLocaleTimeString().slice(0, 5)
    setTimeout(() => { if (String(savedTip.value).startsWith('已自动保存')) savedTip.value = '' }, 1800)
  }, 600)
})

/* ================= 切换语言：同步换成该语言的代码模板 =================
 * 需求：做算法题时切换编程语言，敲代码的地方要立刻换成对应语言的模板。
 *
 * 坑：el-select 的 change 事件**只抛新值**（Element Plus 源码
 * `emit(CHANGE_EVENT, val)`，只有一个参数），所以 onLangChange(nv, ov) 里
 * ov 恒为 undefined。之前靠它取「旧语言」就变成了
 * `saveDraft(language.value, code.value)` —— 而 v-model 已经先一步把
 * language 改成了新语言，于是**旧语言的代码被存进了新语言的草稿键**。
 * 表现：切到 C++ 后草稿里躺着的还是刚才那段 Python，看起来像「模板没换」。
 *
 * 修法：不在 change 里猜旧值，改用 watch —— Vue 的 watch 回调
 * 拿到的是 (newVal, oldVal)，两个值都可靠。
 */
/* 载入历史提交 / 参考答案时用：这些函数会自己设置 code，
 * 若同时改了 language，watch 会用草稿/模板把刚载入的代码冲掉。
 * 置 true 让这一次 language 变化不触发模板替换。 */
let suppressLangSync = false

watch(language, (nv, ov) => {
  if (suppressLangSync) { suppressLangSync = false; return }
  if (!nv || nv === ov) return
  // 旧语言草稿先落盘，再恢复新语言草稿；没有草稿就用该语言模板
  saveDraft(ov, code.value)
  const draft = loadDraft(nv)
  code.value = draft || TEMPLATES[nv] || ''
  // 运行输入跟着语言一起换：C 的测试数据不该混进 Java 那份里
  saveStdin(SCOPE.ALGO, algoId.value, ov, stdinText.value)
  stdinText.value = loadStdinDraft(nv)
  const label = langLabel(nv)
  if (draft) {
    ElMessage.success(`已切换到 ${label}，恢复你之前写的草稿`)
  } else {
    ElMessage.success(`已切换到 ${label}，代码模板同步替换`)
  }
})

/* langLabel 来自 utils/codeTemplates（全站唯一数据源），不在这里再定义一份。
   原来这里只认 LANGS 里那 5 门语言，html / css 之类的会显示成 '-'。 */
function statusText(s) { return (STATUS[s] || { text: s || '未知' }).text }
function statusType(s) { return (STATUS[s] || { type: 'info' }).type }
function diffType(d) {
  const n = Number(d) || 3
  return n <= 2 ? 'success' : (n === 3 ? 'warning' : 'danger')
}
function render(text) {
  return renderMd(text)
}
function formatTime(t) {
  if (!t) return '-'
  const d = new Date(t)
  const p = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}

/** 复制到剪贴板：优先用 Clipboard API，非安全上下文（http 局域网）回退到 execCommand */
async function copyText(text, label) {
  const s = String(text == null ? '' : text)
  if (!s) { ElMessage.warning('没有可复制的内容'); return }
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(s)
    } else {
      const ta = document.createElement('textarea')
      ta.value = s
      ta.style.position = 'fixed'
      ta.style.opacity = '0'
      document.body.appendChild(ta)
      ta.select()
      document.execCommand('copy')
      document.body.removeChild(ta)
    }
    ElMessage.success((label || '内容') + '已复制')
  } catch (e) {
    ElMessage.error('复制失败，请手动选中复制')
  }
}

function loadSampleToEditor(s) {
  // 只把样例输入填进编辑器不方便，这里放到剪贴板更实用
  copyText(s.stdin, '样例输入')
}

function useSolution() {
  if (!solution.value || !solution.value.code) return
  /* 答案的语言可能和编辑器当前语言不一致（答案区可以切 C++，
     编辑器还在 Python）。直接塞进去就是「C++ 代码跑在 Python 解释器里」，
     必错。所以先把编辑器切到答案的语言。
     suppressLangSync 必须置位 —— 否则新 watch 会用草稿/模板把刚载入的答案冲掉。 */
  const lang = solution.value.language
  if (lang && lang !== language.value) {
    suppressLangSync = true
    language.value = lang
  }
  code.value = solution.value.code
  saveDraft(language.value, code.value)
  ElMessage.success(`参考答案已载入编辑器（${langLabel(language.value)}，已覆盖当前草稿）`)
}

function useSubmitCode(row) {
  if (!row || !row.code) return
  // 先关掉 watch 的模板替换，再改语言 —— 否则刚载入的历史代码会被草稿冲掉
  if (row.language && row.language !== language.value) {
    suppressLangSync = true
    language.value = row.language
  }
  code.value = row.code
  saveDraft(language.value, code.value)
  ElMessage.success(`已载入提交 #${row.id} 的代码${row.truncated ? '（超长部分被截断）' : ''}`)
}

async function loadDetail() {
  loading.value = true
  try {
    const res = await algorithmApi.detail(algoId.value)
    if (res.code === 200 && res.data) {
      const d = res.data
      algo.value = {
        ...d,
        submitCount: d.submitCount != null ? d.submitCount : (d.submit_count || 0),
        acceptedCount: d.acceptedCount != null ? d.acceptedCount : (d.accepted_count || 0)
      }
      samples.value = d.samples || []
      // 恢复草稿优先，其次模板
      if (!code.value.trim()) {
        code.value = loadDraft(language.value) || TEMPLATES[language.value] || ''
      }
      // 测试输入同批恢复：刷新回来接着调的时候，敲过的数据还在控制台里
      if (!stdinText.value) stdinText.value = loadStdinDraft(language.value)
    } else {
      ElMessage.error(res.message || '题目加载失败')
    }
  } catch (e) {
    ElMessage.error('题目加载失败')
  } finally {
    loading.value = false
  }
}

async function loadMy() {
  try {
    const res = await algorithmApi.mySubmits(algoId.value)
    mySubmits.value = res.data || []
  } catch (e) { /* 提交记录失败不影响做题 */ }
}

async function loadSolutions() {
  try {
    const res = await algorithmApi.solutions(algoId.value)
    solutions.value = res.data || []
  } catch (e) {
    solutions.value = []
  }
}

// 运行（样例用例）：只验证结果，不写提交记录 —— 「运行」与「提交」分离
async function runCode() {
  if (running.value) return
  if (!code.value.trim()) {
    ElMessage.warning('请先写代码')
    return
  }
  running.value = true
  result.value = null
  ensureDockVisible()
  saveDraft(language.value, code.value)
  // 输入不必等 debounce —— 点运行的当下就把测试数据存好，切回来还在
  saveStdin(SCOPE.ALGO, algoId.value, language.value, stdinText.value)
  try {
    // 控制台里敲了数据就跑那组自定义输入，不敲就照老规矩跑样例
    const res = await algorithmApi.run(algoId.value, {
      language: language.value, code: code.value, stdin: stdinText.value
    })
    if (res.code === 200 && res.data) {
      result.value = res.data
      runSeq.value += 1
      if (res.data.custom) {
        // 自定义输入：没有标准答案可比对，报「通过/未通过」是骗人，只说跑完了
        ElMessage.success('已用你敲的输入跑完（不计提交、不计分）')
      } else if (res.data.status === 'accepted') {
        ElMessage.success('样例全部通过！点「提交判题」正式计分')
      } else {
        ElMessage.warning(statusText(res.data.status) + '（仅样例运行，不计提交）')
      }
    } else {
      ElMessage.error(res.message || '运行失败')
      result.value = {
        custom: false, status: 'runtime_error', passed: 0, total: 0,
        consoleLog: '', message: res.message || '运行失败', runtime: 0
      }
      runSeq.value += 1
    }
  } catch (e) {
    ElMessage.error('判题服务连接失败')
    result.value = {
      custom: false, status: 'runtime_error', passed: 0, total: 0,
      consoleLog: '', message: '判题服务连接失败，请确认后端已通过 start.bat 启动', runtime: 0
    }
    runSeq.value += 1
  } finally {
    running.value = false
  }
}

/** 清空运行结果：清屏幕但保留输入队列 —— 同一批数据还想再跑一次时直接点运行 */
function clearResult() {
  result.value = null
  consoleEl.value && consoleEl.value.clear()
}

async function submit() {
  if (running.value) return
  if (!code.value.trim()) {
    ElMessage.warning('请先写代码')
    return
  }
  running.value = true
  result.value = null
  ensureDockVisible()
  saveDraft(language.value, code.value)
  try {
    const res = await algorithmApi.submit(algoId.value, { language: language.value, code: code.value })
    if (res.code === 200 && res.data) {
      result.value = res.data
      // 判题结论也进同一个控制台：流水里接着上一次运行往下排，不用再盯提示条
      runSeq.value += 1
      if (res.data.status === 'accepted') {
        ElMessage.success('恭喜，全部用例通过！')
        algo.value.solved = true
        tab.value = 'submit'
      } else {
        ElMessage.warning(statusText(res.data.status) + '，看看下面的失败用例')
      }
      loadMy()
    } else {
      ElMessage.error(res.message || '判题失败')
    }
  } catch (e) {
    ElMessage.error('判题服务连接失败')
  } finally {
    running.value = false
  }
}

async function loadSolution() {
  if (solution.value) return
  solLoading.value = true
  try {
    const res = await algorithmApi.solution(algoId.value)
    if (res.code === 200 && res.data) {
      solution.value = res.data
      syncSolLangs(res.data)
    } else {
      ElMessage.error(res.message || '参考答案获取失败')
    }
  } catch (e) {
    ElMessage.error('参考答案获取失败')
  } finally {
    solLoading.value = false
  }
}

/* ================= 参考答案的多语言切换 =================
 * 需求：答案区加下拉，能切 C / C++ / Java / JS 的写法。
 *
 * 数据来自后端 available 列表（只含有答案的语言）。
 * 前端把 5 种语言全列出来，有答案的可选、没有的置灰标「暂无」——
 * 藏着不提会让人以为「切过去还是一样」，明说没有更清楚。 */
const solLangs = ref([])

function syncSolLangs(data) {
  const has = Array.isArray(data.available) && data.available.length
    ? data.available
    : [data.language]
  solLangs.value = LANGS.map(x => ({ value: x.value, label: x.label, has: has.includes(x.value) }))
}

async function onSolLangChange(lang) {
  if (!lang || (solution.value && solution.value.language === lang)) return
  solLoading.value = true
  try {
    const res = await algorithmApi.solution(algoId.value, lang)
    if (res.code === 200 && res.data) {
      solution.value = res.data
      syncSolLangs(res.data)
    } else {
      ElMessage.error(res.message || '参考答案获取失败')
    }
  } catch (e) {
    ElMessage.error('参考答案获取失败')
  } finally {
    solLoading.value = false
  }
}

/* ================= 题解 ================= */
function openSolutionEditor() {
  solForm.value = { title: '', content: '', language: language.value }
  solEditorVisible.value = true
}

async function submitSolution() {
  const f = solForm.value
  if (!f.content || f.content.trim().length < 10) {
    ElMessage.warning('题解内容太短了，至少写 10 个字说明思路')
    return
  }
  solSaving.value = true
  try {
    const res = await algorithmApi.addSolution(algoId.value, f)
    if (res.code === 200) {
      ElMessage.success('题解已发布')
      solEditorVisible.value = false
      loadSolutions()
    } else {
      ElMessage.error(res.message || '发布失败')
    }
  } catch (e) {
    ElMessage.error('发布失败')
  } finally {
    solSaving.value = false
  }
}

async function toggleLike(s) {
  try {
    const res = await algorithmApi.likeSolution(s.id)
    if (res.code === 200 && res.data) {
      s.likes = res.data.likes
      s.liked = res.data.liked
    }
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

async function removeSolution(s) {
  try {
    await ElMessageBox.confirm('确定删除这篇题解吗？', '删除题解', { type: 'warning' })
  } catch (e) {
    return
  }
  try {
    const res = await algorithmApi.deleteSolution(s.id)
    if (res.code === 200) {
      ElMessage.success('已删除')
      loadSolutions()
    } else {
      ElMessage.error(res.message || '删除失败')
    }
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

// 题目切换时重置状态（同组件复用时关键）
watch(() => route.params.id, async () => {
  solution.value = null
  result.value = null
  code.value = ''
  // 控制台跟着换题重开一段会话（清空 lines 由 RunConsole 的 modelValue watch 负责）
  stdinText.value = ''
  await loadDetail()
  loadMy()
  loadSolutions()
})

onMounted(async () => {
  canBack.value = !!window.history.state
  await loadDetail()
  loadMy()
  loadSolutions()
  nextTick(() => { if (route.query.tab) tab.value = String(route.query.tab) })
})
</script>

<style scoped>
.algo-page { max-width: 1560px; }
.detail-nav {
  display: flex; gap: 8px; flex-wrap: wrap;
  padding: 9px 12px; margin-bottom: 12px;
}
.detail-nav .el-button { margin-left: 0; }

/* ---------- 三栏工作区 ----------
   默认：题目 30% / 写代码 70%
   开助手：题目 30% / 写代码 45% / 助手 25% */
.algo-page { max-width: 1920px; }
.algo-work { display: flex; gap: 16px; align-items: flex-start; flex-wrap: nowrap; }
.panel { padding: 18px; }
.problem-panel { flex: 0 0 30%; max-width: 30%; min-width: 0; }
.code-panel { flex: 1 1 70%; min-width: 0; position: sticky; top: 12px; }
/* 助手展开后代码让出 25% */
.algo-work.with-assist .code-panel { flex: 0 0 45%; max-width: 45%; }
.assist-panel {
  flex: 0 0 25%; max-width: 25%; min-width: 0;
  position: sticky; top: 12px;
  max-height: calc(100vh - 40px); overflow: auto;
}
.assist-panel .assist-head {
  display: flex; align-items: center; justify-content: space-between;
  padding-bottom: 10px; margin-bottom: 8px; border-bottom: 1px solid var(--border);
}
.assist-panel .assist-head b { display: flex; align-items: center; gap: 6px; font-size: 14px; color: var(--brand); }

/* 窄屏退回纵向堆叠，避免把编辑器压成一条缝 */
@media (max-width: 1500px) {
  .algo-work { flex-wrap: wrap; }
  .problem-panel { flex: 0 0 100%; max-width: 100%; }
  .code-panel { flex: 1 1 100%; position: static; }
  .algo-work.with-assist .code-panel { flex: 0 0 58%; max-width: 58%; }
  .assist-panel { flex: 0 0 38%; max-width: 38%; position: static; max-height: none; }
}
@media (max-width: 1000px) {
  .algo-work.with-assist .code-panel,
  .assist-panel { flex: 0 0 100%; max-width: 100%; }
}
/* 栅格退成单列后，分隔线要跟着从左框改到上框，否则会留一条竖直短线 */
@media (max-width: 600px) {
  .sample-col + .sample-col { border-left: 0; border-top: 1px solid var(--border); }
  .case-col + .case-col { border-left: 0; border-top: 1px solid var(--border); }
  .sol-toolbar { flex-direction: column; align-items: flex-start; gap: 8px; }
  .sol-head { flex-wrap: wrap; }
  .edit-head { flex-wrap: wrap; gap: 8px; }
  .edit-head-right { flex-wrap: wrap; }
  .p-title { font-size: 18px; }
  .assistant-fab { right: 14px; bottom: 16px; }
  .code-block { max-height: 320px; }
}

.p-title { margin: 0 0 8px; font-size: 20px; }
.p-meta { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 6px; }
.weight-badge {
  display: inline-flex; align-items: center; gap: 4px;
  background: linear-gradient(135deg, #e8a13a, #f0b95f); color: #fff;
  font-size: 12px; font-weight: 700; padding: 2px 8px; border-radius: 10px;
}
.p-tabs { margin-top: 12px; }
.tab-body { padding-top: 4px; }
.sec { margin-top: 16px; }
.sec:first-child { margin-top: 4px; }
.sec-title { font-size: 14px; font-weight: 600; margin-bottom: 8px; color: var(--text-2); }
.desc { font-size: 14px; line-height: 1.9; }

.mono {
  background: var(--code-bg); border: 1px solid var(--border); border-radius: 8px;
  padding: 10px 12px; margin: 0; white-space: pre-wrap; word-break: break-word;
  font: 13px/1.7 Consolas, Monaco, "Courier New", monospace; color: var(--text);
}
.two-col { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 240px), 1fr)); gap: 12px; }

.sample-list { display: flex; flex-direction: column; gap: 10px; }
.sample { border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }
.sample-head {
  background: var(--soft-bg); padding: 4px 12px; font-size: 12px; color: var(--text-2);
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between;
}
.sample-body { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 240px), 1fr)); }
.sample-col { padding: 8px 12px; min-width: 0; }
.sample-col + .sample-col { border-left: 1px solid var(--border); }
.sample-label { font-size: 12px; color: var(--text-3); margin-bottom: 4px; }
.sample-col .mono { border: 0; background: transparent; padding: 0; }

.hint-box { margin-top: 10px; background: var(--warning-light); border: 1px solid var(--warn-border); border-radius: 8px; padding: 10px 12px; }
.hint-text { background: transparent; border: 0; padding: 0; }

.sol-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.sol-box { margin-top: 10px; }
.sol-head { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; flex-wrap: wrap; }
.code-block { max-height: 460px; overflow: auto; background: var(--code-bg); }
/* 答案语言下拉：宽度按最长选项「JavaScript」给，126px 会把它挤成省略号 */
.sol-lang { width: 138px; flex-shrink: 0; }
/* 下拉面板里没有该语言答案的项：置灰并标「暂无」，明说没有比藏着强 */
.sol-opt { display: flex; align-items: center; justify-content: space-between; gap: 10px; width: 100%; }
.sol-opt-none { font-size: 12px; color: var(--text-3); }

/* ---------- 题解区 ---------- */
.sol-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px; padding-bottom: 10px; border-bottom: 1px dashed var(--border);
}
.sol-item { padding: 12px 0; border-bottom: 1px dashed #eef1f6; }
.sol-item-head { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 6px; }
.sol-title { font-size: 14px; }
.sol-item-ops { margin-left: auto; display: flex; align-items: center; gap: 2px; }
.sol-content { font-size: 13px; line-height: 1.85; }

/* ---------- 编辑器 ---------- */
.edit-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.edit-head-right { display: flex; align-items: center; gap: 8px; }
/* 语言下拉：宽度要放得下 "JavaScript"，126px 会把文字挤成省略号 */
.lang-select { width: 138px; flex-shrink: 0; }
.save-tip { display: inline-flex; align-items: center; gap: 3px; color: var(--success); }
.edit-foot { display: flex; align-items: center; gap: 10px; margin-top: 10px; flex-wrap: wrap; }

/* ---------- 运行结果面板：与代码实验室同款 ---------- */
.out-card { margin-top: 14px; padding: 12px 14px; }
.out-head { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; flex-wrap: wrap; }
.out-head > b { font-size: 14px; }
.out-head .head-actions { margin-left: auto; display: flex; align-items: center; gap: 6px; }
/* 面板体两档高度：常规 280px、放大后一屏能看完（吃掉视口 60vh） */
.dock-body { display: flex; flex-direction: column; height: 280px; }
.dock-body.expanded { height: max(60vh, 420px); }
.dock-mini {
  display: flex; align-items: center; gap: 8px; cursor: pointer;
  padding: 4px 2px; color: var(--text-2); user-select: none;
}
.dock-mini:hover { color: var(--brand); }
.dock-mini .muted { margin-left: auto; }
/* 控制台（RunConsole）：黑框样式、字号、滚动都在组件里，
   这里只负责让它吃满面板剩下的高度 —— 与代码实验室同一套写法 */
.dock-body :deep(.run-console) { flex: 1 1 auto; min-height: 0; }

.case-box { margin-top: 10px; flex-shrink: 0; }
.case { border: 1px solid var(--border); border-radius: 8px; overflow: hidden; background: var(--soft-bg); margin-bottom: 8px; }
.case-row { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 170px), 1fr)); }
.case-col { padding: 8px 10px; min-width: 0; }
.case-col + .case-col { border-left: 1px solid var(--border); }
.case-label { font-size: 11px; color: var(--text-3); margin-bottom: 4px; }
.case-col .mono { border: 0; background: transparent; padding: 0; font-size: 12px; max-height: 160px; overflow: auto; }
.ok-text { color: var(--success); }
.bad-text { color: var(--danger); }
@media (max-width: 480px) {
  .dock-body { height: auto; min-height: 240px; }
  .dock-body :deep(.run-console) { min-height: 200px; }
}

/* ---------- 悬浮小助手 ---------- */
.assistant-fab {
  position: fixed; right: 26px; bottom: 30px; z-index: 1800;
  display: flex; align-items: center; gap: 8px;
  padding: 11px 18px; border: none; border-radius: 26px; cursor: pointer;
  background: linear-gradient(135deg, #3b6ef6, #6f9bff); color: #fff;
  font-size: 14px; font-weight: 600; letter-spacing: .2px;
  box-shadow: 0 8px 24px rgba(59, 110, 246, .38);
  transition: transform .18s, box-shadow .18s;
}
.assistant-fab:hover { transform: translateY(-2px); box-shadow: 0 12px 30px rgba(59, 110, 246, .46); }
.assistant-fab .el-icon { font-size: 17px; }
</style>
