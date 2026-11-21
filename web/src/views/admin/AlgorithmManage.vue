<template>
  <div class="page">
    <div class="page-head">
      <h2>算法题管理</h2>
      <div class="head-tools">
        <el-select v-model="filterDifficulty" placeholder="全部难度" clearable style="width:140px" @change="onFilterChange">
          <el-option v-for="d in 5" :key="d" :value="d" :label="`${d} · ${DIFFICULTY_TEXT[d]}`" />
        </el-select>
        <el-input v-model="keyword" placeholder="搜索标题/标签" clearable style="width:180px" @change="onFilterChange" />
        <el-button @click="load">刷新</el-button>
        <el-button type="primary" @click="openAdd">新增算法题</el-button>
      </div>
    </div>

    <div class="card">
      <el-table :data="list" size="small" border max-height="640" v-loading="loading">
        <el-table-column prop="id" label="ID" width="56" />
        <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip />
        <el-table-column label="难度" width="90" align="center">
          <template #default="{ row }">
            <el-tag size="small" effect="light" :type="DIFFICULTY_TAG[row.difficulty]">
              {{ row.difficulty }} · {{ DIFFICULTY_TEXT[row.difficulty] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="权值" width="86" align="center">
          <template #default="{ row }">
            <span class="weight-badge">{{ row.weight }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="tags" label="标签" width="130" show-overflow-tooltip />
        <el-table-column prop="source" label="来源" width="90" />
        <el-table-column label="通过率" width="90" align="center">
          <template #default="{ row }">
            <span v-if="row.submit_count">{{ Math.round((row.accepted_count / row.submit_count) * 100) }}%</span>
            <span v-else class="muted">-</span>
            <span class="rate-sub">{{ row.accepted_count }}/{{ row.submit_count }}</span>
          </template>
        </el-table-column>
        <el-table-column label="用例" width="130" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.case_count" size="small" type="success" effect="light">{{ row.case_count }} 条</el-tag>
            <el-tooltip v-else content="补齐测试用例后用户提交才能判题" placement="top">
              <el-tag size="small" type="danger" effect="light">未配用例，无法判题</el-tag>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-switch v-model="row.__on" size="small" @change="val => toggleStatus(row, val)" />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="150" />
        <el-table-column label="操作" width="190" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="openEdit(row)">编辑</el-button>
            <el-button text type="warning" size="small" @click="openCases(row)">用例</el-button>
            <el-button text type="danger" size="small" @click="del(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <!-- 后端真分页：page/pageSize 传给 /admin/algorithm。
           原来后端写死 LIMIT 300，题目涨过 300 后后面的永远翻不到。 -->
        <PaginationBar :total="total" v-model:page="page" v-model:pageSize="pageSize" @change="load" />
      <el-empty v-if="!loading && !list.length" description="暂无算法题" :image-size="60" />
    </div>

    <!-- 新增 / 编辑 -->
    <el-dialog
      v-model="dialog"
      :title="form.id ? '编辑算法题' : '新增算法题'"
      width="780px"
      top="5vh"
      :close-on-click-modal="false"
    >
      <el-tabs v-model="activeTab">
        <el-tab-pane label="基础信息" name="base">
          <el-form :model="form" label-width="100px">
            <el-form-item label="标题" required>
              <el-input v-model="form.title" placeholder="例如：两数之和" />
            </el-form-item>
            <el-form-item label="难度">
              <el-select v-model="form.difficulty" style="width:180px">
                <el-option v-for="d in 5" :key="d" :value="d" :label="`${d} · ${DIFFICULTY_TEXT[d]}`" />
              </el-select>
            </el-form-item>
            <el-form-item label="权值">
              <el-input-number v-model="form.weight" :min="1" :max="200" controls-position="right" />
              <span class="field-hint">留空则按难度自动推荐：1-2→10，3→20，4→30，5→50（用于排行榜计分）</span>
            </el-form-item>
            <el-form-item label="来源">
              <el-select v-model="form.source" style="width:180px">
                <el-option v-for="s in SOURCE_OPTIONS" :key="s" :value="s" :label="s" />
              </el-select>
            </el-form-item>
            <el-form-item label="标签">
              <el-input v-model="form.tags" placeholder="多个标签用逗号分隔，例如：数组,哈希表" />
            </el-form-item>
            <el-form-item label="关联知识点">
              <el-select v-model="form.knowledgeId" filterable clearable placeholder="可不关联" style="width:100%">
                <el-option v-for="k in knowledgeList" :key="k.id" :value="k.id" :label="k.name" />
              </el-select>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="题面描述" name="desc">
          <el-form :model="form" label-width="100px">
            <el-form-item label="题面(MD)" required>
              <el-input v-model="form.description" type="textarea" :rows="10" placeholder="支持 Markdown" />
            </el-form-item>
            <el-form-item label="输入说明">
              <el-input v-model="form.inputDesc" type="textarea" :rows="3" />
            </el-form-item>
            <el-form-item label="输出说明">
              <el-input v-model="form.outputDesc" type="textarea" :rows="3" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="输入输出样例" name="sample">
          <el-form :model="form" label-width="100px">
            <el-form-item label="样例输入">
              <el-input v-model="form.sampleInput" type="textarea" :rows="7" class="mono-text" />
            </el-form-item>
            <el-form-item label="样例输出">
              <el-input v-model="form.sampleOutput" type="textarea" :rows="7" class="mono-text" />
            </el-form-item>
            <div class="sample-tip">样例会展示给用户；判题用的是「用例」标签里配置的测试用例</div>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="提示与答案" name="answer">
          <el-form :model="form" label-width="100px">
            <el-form-item label="解题思路">
              <el-input v-model="form.hints" type="textarea" :rows="4" placeholder="给学生看的提示，可留空" />
            </el-form-item>
            <el-form-item label="语言">
              <el-select v-model="form.referenceLanguage" style="width:180px">
                <el-option v-for="l in LANGUAGE_OPTIONS" :key="l.value" :value="l.value" :label="l.label" />
              </el-select>
            </el-form-item>
            <el-form-item label="参考答案">
              <el-input v-model="form.referenceCode" type="textarea" :rows="12" class="mono-text" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>

    <!-- 测试用例抽屉 -->
    <el-drawer v-model="caseDrawer" :title="`测试用例 · ${caseAlgo?.title || ''}`" size="62%">
      <div class="case-bar">
        <span class="muted small">用户提交后逐条比对输出，样例用例会在题面展示</span>
        <div>
          <el-button size="small" @click="syncFromSample">从样例同步</el-button>
          <el-button size="small" type="primary" @click="openCaseAdd">新增用例</el-button>
        </div>
      </div>
      <el-table :data="caseList" size="small" border v-loading="caseLoading">
        <el-table-column prop="id" label="ID" width="56" />
        <el-table-column prop="stdin" label="输入(stdin)" min-width="150">
          <template #default="{ row }"><pre class="mono-cell">{{ row.stdin }}</pre></template>
        </el-table-column>
        <el-table-column prop="expected" label="期望输出" min-width="150">
          <template #default="{ row }"><pre class="mono-cell">{{ row.expected }}</pre></template>
        </el-table-column>
        <el-table-column label="样例" width="70" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="row.is_sample ? 'warning' : 'info'" effect="light">
              {{ row.is_sample ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sort_no" label="排序" width="64" align="center" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="openCaseEdit(row)">编辑</el-button>
            <el-button text type="danger" size="small" @click="delCase(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!caseLoading && !caseList.length" description="还没有测试用例，无法判题" :image-size="60" />
    </el-drawer>

    <!-- 用例新增 / 编辑 -->
    <el-dialog v-model="caseDialog" :title="caseForm.id ? '编辑用例' : '新增用例'" width="560px" append-to-body>
      <el-form :model="caseForm" label-width="90px">
        <el-form-item label="输入(stdin)">
          <el-input v-model="caseForm.stdin" type="textarea" :rows="5" class="mono-text" placeholder="每行一个输入值" />
        </el-form-item>
        <el-form-item label="期望输出" required>
          <el-input v-model="caseForm.expected" type="textarea" :rows="5" class="mono-text" placeholder="程序应输出的内容" />
        </el-form-item>
        <el-form-item label="样例用例">
          <el-switch v-model="caseForm.isSample" />
          <span class="field-hint">打开后该用例会作为样例展示给用户</span>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="caseForm.sortNo" :min="0" :max="999" controls-position="right" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="caseDialog = false">取消</el-button>
        <el-button type="primary" :loading="caseSaving" @click="saveCase">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import PaginationBar from '@/components/PaginationBar.vue'

const DIFFICULTY_TEXT = { 1: '简单', 2: '较易', 3: '中等', 4: '较难', 5: '困难' }
const DIFFICULTY_TAG = { 1: 'success', 2: 'success', 3: 'warning', 4: 'danger', 5: 'danger' }
const SOURCE_OPTIONS = ['基础', '考研408', '软考', 'NCRE', '期末', '编程语言']
const LANGUAGE_OPTIONS = [
  { value: 'python', label: 'Python' },
  { value: 'c', label: 'C' },
  { value: 'cpp', label: 'C++' },
  { value: 'java', label: 'Java' },
  { value: 'javascript', label: 'JavaScript' }
]

const list = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const knowledgeList = ref([])
const keyword = ref('')
const filterDifficulty = ref(null)
const loading = ref(false)
const dialog = ref(false)
const saving = ref(false)
const activeTab = ref('base')
const form = ref(emptyForm())

const caseDrawer = ref(false)
const caseDialog = ref(false)
const caseList = ref([])
const caseLoading = ref(false)
const caseSaving = ref(false)
const caseAlgo = ref(null)
const caseForm = ref({ id: null, stdin: '', expected: '', isSample: true, sortNo: 0 })

function emptyForm() {
  return {
    id: null, title: '', difficulty: 3, weight: null, source: '基础', tags: '', knowledgeId: null,
    description: '', inputDesc: '', outputDesc: '',
    sampleInput: '', sampleOutput: '',
    hints: '', referenceCode: '', referenceLanguage: 'python'
  }
}

function wrapList(rows) {
  return (rows || []).map(r => ({ ...r, __on: Number(r.status) !== 0 }))
}

async function load() {
  loading.value = true
  try {
    const res = await adminApi.algorithm({
      keyword: keyword.value,
      difficulty: filterDifficulty.value,
      page: page.value,
      pageSize: pageSize.value
    })
    list.value = wrapList(res.data)
    total.value = Number(res.total || (res.data || []).length)
    const maxPage = Math.max(1, Math.ceil(total.value / pageSize.value))
    if (page.value > maxPage) {
      page.value = maxPage
      return load()
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '加载失败')
  } finally {
    loading.value = false
  }
}
/* 换筛选条件回第 1 页，避免停在一个空页上 */
function onFilterChange() {
  // 筛选条件变化一律回第 1 页，否则可能停在超出范围的空页上
  page.value = 1
  load()
}

function openAdd() {
  form.value = emptyForm()
  activeTab.value = 'base'
  dialog.value = true
}
async function openEdit(row) {
  try {
    const res = await adminApi.algorithmDetail(row.id)
    const d = res.data || {}
    form.value = {
      id: d.id, title: d.title || '', difficulty: d.difficulty || 3, weight: d.weight || null,
      source: d.source || '基础', tags: d.tags || '', knowledgeId: d.knowledge_id || null,
      description: d.description || '', inputDesc: d.input_desc || '', outputDesc: d.output_desc || '',
      sampleInput: d.sample_input || '', sampleOutput: d.sample_output || '',
      hints: d.hints || '', referenceCode: d.reference_code || '',
      referenceLanguage: d.reference_language || 'python'
    }
    activeTab.value = 'base'
    dialog.value = true
  } catch (e) {
    ElMessage.error('题目详情加载失败')
  }
}
async function save() {
  if (!form.value.title.trim()) {
    ElMessage.warning('题目标题必填')
    activeTab.value = 'base'
    return
  }
  if (!form.value.description.trim()) {
    ElMessage.warning('题面描述必填')
    activeTab.value = 'desc'
    return
  }
  const payload = {
    title: form.value.title.trim(),
    difficulty: form.value.difficulty,
    source: form.value.source || '基础',
    tags: form.value.tags || '',
    knowledgeId: form.value.knowledgeId || null,
    description: form.value.description,
    inputDesc: form.value.inputDesc || '',
    outputDesc: form.value.outputDesc || '',
    sampleInput: form.value.sampleInput || '',
    sampleOutput: form.value.sampleOutput || '',
    hints: form.value.hints || '',
    referenceCode: form.value.referenceCode || '',
    referenceLanguage: form.value.referenceLanguage || 'python'
  }
  // 权值留空则由后端按难度自动推荐
  if (form.value.weight) payload.weight = Number(form.value.weight)

  saving.value = true
  try {
    const res = form.value.id
      ? await adminApi.updateAlgorithm(form.value.id, payload)
      : await adminApi.addAlgorithm(payload)
    ElMessage.success(res.message || '保存成功')
    dialog.value = false
    load()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '保存失败')
  } finally {
    saving.value = false
  }
}
async function toggleStatus(row, val) {
  try {
    await adminApi.updateAlgorithm(row.id, { status: val ? 1 : 0 })
    row.status = val ? 1 : 0
    ElMessage.success(val ? '已启用' : '已停用')
  } catch (e) {
    row.__on = !val
    ElMessage.error(e.response?.data?.message || '状态更新失败')
  }
}
async function del(row) {
  await ElMessageBox.confirm(
    `确定删除算法题「${row.title}」？该操作会同时删除它的所有测试用例与用户提交记录，且不可恢复。`,
    '删除确认',
    { type: 'warning', confirmButtonText: '确定删除', cancelButtonText: '取消' }
  )
  try {
    await adminApi.deleteAlgorithm(row.id)
    ElMessage.success('删除成功')
    load()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '删除失败')
  }
}

/* ---------- 测试用例 ---------- */
async function openCases(row) {
  caseAlgo.value = row
  caseDrawer.value = true
  await loadCases()
}
async function loadCases() {
  if (!caseAlgo.value) return
  caseLoading.value = true
  try {
    const res = await adminApi.algorithmCases({ algorithmId: caseAlgo.value.id })
    caseList.value = res.data || []
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '用例加载失败')
  } finally {
    caseLoading.value = false
  }
}
function openCaseAdd() {
  caseForm.value = { id: null, stdin: '', expected: '', isSample: true, sortNo: caseList.value.length }
  caseDialog.value = true
}
function openCaseEdit(row) {
  caseForm.value = {
    id: row.id, stdin: row.stdin || '', expected: row.expected || '',
    isSample: Number(row.is_sample) === 1, sortNo: row.sort_no || 0
  }
  caseDialog.value = true
}
async function syncFromSample() {
  if (!caseAlgo.value) return
  try {
    const res = await adminApi.algorithmDetail(caseAlgo.value.id)
    const d = res.data || {}
    if (!String(d.sample_input || '').trim() && !String(d.sample_output || '').trim()) {
      ElMessage.warning('该题尚未填写样例输入输出')
      return
    }
    await adminApi.addAlgorithmCase({
      algorithmId: caseAlgo.value.id,
      stdin: d.sample_input || '',
      expected: d.sample_output || '',
      isSample: 1,
      sortNo: 0
    })
    ElMessage.success('已从样例同步为第一条用例')
    await loadCases()
    load()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '同步失败')
  }
}
async function saveCase() {
  if (!String(caseForm.value.expected || '').trim()) {
    ElMessage.warning('期望输出必填')
    return
  }
  caseSaving.value = true
  try {
    if (caseForm.value.id) {
      await adminApi.updateAlgorithmCase(caseForm.value.id, {
        stdin: caseForm.value.stdin || '',
        expected: caseForm.value.expected,
        isSample: caseForm.value.isSample ? 1 : 0,
        sortNo: caseForm.value.sortNo || 0
      })
    } else {
      await adminApi.addAlgorithmCase({
        algorithmId: caseAlgo.value.id,
        stdin: caseForm.value.stdin || '',
        expected: caseForm.value.expected,
        isSample: caseForm.value.isSample ? 1 : 0,
        sortNo: caseForm.value.sortNo || 0
      })
    }
    ElMessage.success('保存成功')
    caseDialog.value = false
    await loadCases()
    load()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '保存失败')
  } finally {
    caseSaving.value = false
  }
}
async function delCase(row) {
  await ElMessageBox.confirm('确定删除该测试用例？', '提示', { type: 'warning' })
  try {
    await adminApi.deleteAlgorithmCase(row.id)
    ElMessage.success('删除成功')
    await loadCases()
    load()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '删除失败')
  }
}

onMounted(async () => {
  try {
    const res = await adminApi.knowledge()
    knowledgeList.value = res.data || []
  } catch (e) {
    ElMessage.error('知识点列表加载失败')
  }
  load()
})
</script>

<style scoped>
.page-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 10px; }
.page-head h2 { margin: 0; font-size: 20px; }
.head-tools { display: flex; gap: 8px; flex-wrap: wrap; }
.field-hint { margin-left: 10px; font-size: 12px; color: var(--text-3); }
.sample-tip { font-size: 12px; color: var(--text-3); padding-left: 100px; }

.weight-badge {
  display: inline-block;
  min-width: 42px;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 700;
  font-size: 13px;
  color: #7a4a00;
  background: linear-gradient(135deg, #ffe9b0, #ffd15c);
  border: 1px solid #f0bd45;
}
.rate-sub { display: block; font-size: 11px; color: var(--text-3); }

.case-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; gap: 10px; }
.mono-cell {
  margin: 0;
  font-family: Consolas, Menlo, 'Courier New', monospace;
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 88px;
  overflow: auto;
  color: var(--text);
}

/* 等宽字体：deep 穿透到 textarea 原生元素 */
.mono-text :deep(textarea) {
  font-family: Consolas, Menlo, 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
}
</style>
