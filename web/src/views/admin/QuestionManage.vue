<template>
  <div class="page">
    <div class="page-head">
      <h2>题库管理</h2>
      <div class="head-tools">
        <el-select v-model="filterCourse" placeholder="全部课程" clearable style="width:150px" @change="load">
          <el-option v-for="c in courses" :key="c.id" :value="c.id" :label="c.name" />
        </el-select>
        <el-select v-model="filterType" placeholder="全部题型" clearable style="width:140px" @change="onTypeChange">
          <el-option v-for="t in TYPE_OPTIONS" :key="t.value" :value="t.value" :label="t.label" />
        </el-select>
        <el-input v-model="keyword" placeholder="搜索题干" clearable style="width:170px" @change="load" />
        <el-button type="primary" @click="openAdd">新增题目</el-button>
      </div>
    </div>

    <div class="card">
      <el-table :data="list" size="small" border max-height="620" v-loading="loading">
        <el-table-column prop="id" label="ID" width="56" />
        <el-table-column prop="course_name" label="课程" width="110" />
        <el-table-column prop="knowledge_name" label="知识点" width="120" />
        <el-table-column prop="title" label="题干" min-width="240" show-overflow-tooltip />
        <el-table-column label="题型" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="TYPE_MAP[row.type]?.tag" effect="light">
              {{ TYPE_MAP[row.type]?.label || row.type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="答案" width="90">
          <template #default="{ row }">
            <span v-if="isSubjective(row.type)" class="muted small">主观题</span>
            <span v-else>{{ row.answer }}</span>
          </template>
        </el-table-column>
        <el-table-column label="难度" width="70" align="center">
          <template #default="{ row }">
            <span class="small">{{ DIFFICULTY_TEXT[row.difficulty] || '中等' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="score" label="分值" width="60" align="center" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="openEdit(row)">编辑</el-button>
            <el-button text type="danger" size="small" @click="del(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <!-- 题库是前端分页（后端不支持题型筛选，拉全量后本地切页），change 直接重切 applyPage -->
      <PaginationBar :total="total" v-model:page="page" v-model:pageSize="pageSize" @change="applyPage" />
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑题目' : '新增题目'" width="680px" :close-on-click-modal="false">
      <el-form :model="form" label-width="90px">
        <el-form-item label="知识点">
          <el-select v-model="form.knowledgeId" filterable style="width:100%">
            <el-option v-for="k in knowledgeList" :key="k.id" :value="k.id" :label="k.name" />
          </el-select>
        </el-form-item>
        <el-form-item label="题型">
          <el-select v-model="form.type" style="width:200px" @change="onTypeChange">
            <el-option v-for="t in TYPE_OPTIONS" :key="t.value" :value="t.value" :label="t.label" />
          </el-select>
          <span class="type-hint">
            {{ isSubjective(form.type) ? '主观题：由智能助手参照答案与要点逐条判分' : '客观题：系统按标准答案自动判分' }}
          </span>
        </el-form-item>
        <el-form-item label="题干">
          <el-input v-model="form.title" type="textarea" :rows="3" />
        </el-form-item>

        <!-- 客观题 -->
        <template v-if="!isSubjective(form.type)">
          <el-form-item label="选项">
            <div v-for="(o, i) in form.options" :key="i" class="opt-row">
              <span class="opt-key">{{ o.key }}</span>
              <el-input v-model="o.text" style="flex:1" />
              <el-button v-if="form.options.length > 2" text type="danger" @click="form.options.splice(i, 1)">删除</el-button>
            </div>
            <el-button size="small" @click="addOption">添加选项</el-button>
          </el-form-item>
          <el-form-item label="正确答案">
            <el-select v-model="form.answer" style="width:140px">
              <el-option v-for="o in form.options" :key="o.key" :value="o.key" :label="o.key" />
            </el-select>
          </el-form-item>
        </template>

        <!-- 主观题：案例分析 / 编程 -->
        <template v-else>
          <el-form-item label="参考答案">
            <el-input
              v-model="form.referenceAnswer"
              type="textarea"
              :rows="5"
              placeholder="填写完整参考答案供智能助手比对，支持 Markdown"
            />
          </el-form-item>
          <el-form-item label="评分要点">
            <div class="points-box">
              <div class="points-tip">
                判分时会逐条核对这些要点，要点写得越具体，判分越准
              </div>
              <div v-for="(p, i) in form.points" :key="i" class="point-row">
                <span class="point-no">{{ i + 1 }}</span>
                <el-input v-model="p.point" placeholder="要点描述，例如：说明时间复杂度的推导过程" style="flex:1" />
                <el-input-number v-model="p.score" :min="0" :max="50" :step="1" controls-position="right" style="width:110px" />
                <el-button text type="danger" @click="form.points.splice(i, 1)">删除</el-button>
              </div>
              <div class="points-foot">
                <el-button size="small" @click="addPoint">添加要点</el-button>
                <span class="points-sum">当前要点总分 <b>{{ pointsTotal }}</b> 分</span>
                <el-button size="small" type="warning" plain @click="syncScore">同步到分值</el-button>
              </div>
            </div>
          </el-form-item>
        </template>

        <el-form-item label="解析">
          <el-input v-model="form.analysis" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="来源">
          <el-select v-model="form.source" style="width:160px">
            <el-option v-for="s in SOURCE_OPTIONS" :key="s" :value="s" :label="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="难度">
          <el-select v-model="form.difficulty" style="width:160px">
            <el-option v-for="d in 5" :key="d" :value="d" :label="`${d} · ${DIFFICULTY_TEXT[d]}`" />
          </el-select>
        </el-form-item>
        <el-form-item label="分值">
          <el-input-number v-model="form.score" :min="1" :max="100" />
          <span class="type-hint">主观题默认 10 分，客观题默认 5 分</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { adminApi, courseApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import PaginationBar from '@/components/PaginationBar.vue'

const TYPE_OPTIONS = [
  { value: 'single', label: '单选题' },
  { value: 'judge', label: '判断题' },
  { value: 'multi', label: '多选题' },
  { value: 'case', label: '案例分析题' },
  { value: 'programming', label: '编程题' }
]
// 主观题（Agent 判分）：case 案例分析 / programming 编程
const SUBJECTIVE = ['case', 'programming']
const TYPE_MAP = {
  single: { label: '单选', tag: 'primary' },
  judge: { label: '判断', tag: 'info' },
  multi: { label: '多选', tag: 'success' },
  case: { label: '案例分析', tag: 'danger' },
  programming: { label: '编程', tag: 'warning' }
}
const SOURCE_OPTIONS = ['基础', '考研408', '软考', 'NCRE', '期末', '编程语言']
const DIFFICULTY_TEXT = { 1: '简单', 2: '较易', 3: '中等', 4: '较难', 5: '困难' }

const list = ref([])
const allRows = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(50)
const courses = ref([])
const knowledgeList = ref([])
const filterCourse = ref(null)
const filterType = ref(null)
const keyword = ref('')
const dialog = ref(false)
const loading = ref(false)
const saving = ref(false)
const form = ref(emptyForm())

function emptyForm() {
  return {
    id: null, knowledgeId: null, type: 'single', title: '',
    options: [
      { key: 'A', text: '' }, { key: 'B', text: '' },
      { key: 'C', text: '' }, { key: 'D', text: '' }
    ],
    answer: 'A', analysis: '', score: 5,
    source: '基础', difficulty: 3,
    referenceAnswer: '', points: []
  }
}

const isSubjective = t => SUBJECTIVE.includes(t)
const pointsTotal = computed(() =>
  (form.value.points || []).reduce((s, p) => s + (Number(p.score) || 0), 0)
)

async function load() {
  loading.value = true
  try {
    // 后端接口不支持题型筛选，这里在前端过滤
    const res = await adminApi.question({
      courseId: filterCourse.value,
      keyword: keyword.value
    })
    const rows = res.data || []
    // 后端不再截断为 500 条，改由前端分页渲染，避免一次性塞上千行拖慢表格
    total.value = Number(res.total || rows.length)
    allRows.value = rows
    applyPage()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '加载失败')
  } finally {
    loading.value = false
  }
}
function applyPage() {
  const rows = filterType.value
    ? allRows.value.filter(r => r.type === filterType.value)
    : allRows.value
  total.value = rows.length
  const start = (page.value - 1) * pageSize.value
  list.value = rows.slice(start, start + pageSize.value)
}
function onTypeChange(t) {
  if (t === 'judge') {
    form.value.options = [{ key: 'A', text: '正确' }, { key: 'B', text: '错误' }]
  } else if (t === 'single' || t === 'multi') {
    form.value.options = [
      { key: 'A', text: '' }, { key: 'B', text: '' },
      { key: 'C', text: '' }, { key: 'D', text: '' }
    ]
  }
  form.value.answer = 'A'
  // 主观题默认分值更高，切过去时给一个合理初值
  if (isSubjective(t) && (form.value.score === 5 || !form.value.score)) form.value.score = 10
  if (!isSubjective(t) && form.value.score === 10) form.value.score = 5
}
function addOption() {
  const keys = ['A', 'B', 'C', 'D', 'E', 'F']
  const next = keys[form.value.options.length]
  if (next) form.value.options.push({ key: next, text: '' })
  else ElMessage.warning('选项最多 6 个')
}
function addPoint() {
  form.value.points.push({ point: '', score: 2 })
}
function syncScore() {
  const total = pointsTotal.value
  if (!total) {
    ElMessage.warning('请为要点设置分值')
    return
  }
  form.value.score = total
  ElMessage.success(`分值已同步为 ${total} 分`)
}
function openAdd() {
  form.value = emptyForm()
  form.value.knowledgeId = knowledgeList.value[0]?.id
  dialog.value = true
}
function openEdit(row) {
  let opts = []
  try { opts = JSON.parse(row.options || '[]') } catch (e) { opts = [] }
  let pts = []
  try { pts = JSON.parse(row.grading_points || '[]') } catch (e) { pts = [] }
  const base = emptyForm()
  form.value = {
    id: row.id, knowledgeId: row.knowledge_id, type: row.type, title: row.title,
    options: opts.length ? opts : (SUBJECTIVE.includes(row.type) ? [] : base.options),
    answer: row.answer, analysis: row.analysis, score: row.score,
    source: row.source || '基础', difficulty: row.difficulty || 3,
    referenceAnswer: row.reference_answer || '',
    points: (pts || []).map(p => ({ point: p.point || '', score: Number(p.score) || 0 }))
  }
  dialog.value = true
}
async function save() {
  if (!form.value.title || !form.value.knowledgeId) {
    ElMessage.warning('知识点和题干必填')
    return
  }
  const subjective = isSubjective(form.value.type)
  // 评分要点：只保留填写了描述的要点，且分值必须大于 0
  const validPoints = (form.value.points || []).filter(p => String(p.point || '').trim())
  for (const p of validPoints) {
    if (!(Number(p.score) > 0)) {
      ElMessage.warning('每个评分要点的分值必须大于 0')
      return
    }
  }
  if (subjective && !String(form.value.referenceAnswer || '').trim() && !validPoints.length) {
    ElMessage.warning('案例分析题/编程题需要填写参考答案或评分要点，否则无法智能判分')
    return
  }
  if (!subjective && !form.value.answer) {
    ElMessage.warning('客观题必须填写正确答案')
    return
  }

  const payload = {
    knowledgeId: form.value.knowledgeId,
    type: form.value.type,
    title: form.value.title,
    analysis: form.value.analysis || '',
    score: Number(form.value.score) || (subjective ? 10 : 5),
    source: form.value.source || '基础',
    difficulty: Number(form.value.difficulty) || 3
  }
  if (subjective) {
    payload.referenceAnswer = form.value.referenceAnswer || ''
    payload.gradingPoints = validPoints.length
      ? JSON.stringify(validPoints.map(p => ({ point: String(p.point).trim(), score: Number(p.score) })))
      : ''
  } else {
    payload.options = form.value.options.filter(o => String(o.text || '').trim())
    payload.answer = form.value.answer
  }

  saving.value = true
  try {
    const res = form.value.id
      ? await adminApi.updateQuestion(form.value.id, payload)
      : await adminApi.addQuestion(payload)
    ElMessage.success(res.message || '保存成功')
    dialog.value = false
    load()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '保存失败')
  } finally {
    saving.value = false
  }
}
async function del(row) {
  await ElMessageBox.confirm(`确定删除题目「${row.title}」？`, '提示', { type: 'warning' })
  try {
    await adminApi.deleteQuestion(row.id)
    ElMessage.success('删除成功')
    load()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '删除失败')
  }
}

onMounted(async () => {
  loading.value = true
  try {
    const [c, k] = await Promise.all([courseApi.list(), adminApi.knowledge()])
    courses.value = c.data || []
    knowledgeList.value = k.data || []
  } catch (e) {
    ElMessage.error('初始化数据加载失败')
  } finally {
    loading.value = false
  }
  load()
})
</script>

<style scoped>
.page-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 10px; }
.page-head h2 { margin: 0; font-size: 20px; }
.head-tools { display: flex; gap: 8px; flex-wrap: wrap; }
.opt-row { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; width: 100%; }
.opt-key { width: 20px; font-weight: 700; }
.type-hint { margin-left: 10px; font-size: 12px; color: var(--text-3); }

.points-box { width: 100%; border: 1px dashed var(--border); border-radius: 8px; padding: 10px; background: var(--soft-bg); }
.points-tip { font-size: 12px; color: var(--warning); margin-bottom: 8px; }
.point-row { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.point-no { width: 18px; font-weight: 700; color: var(--text-3); font-size: 13px; }
.points-foot { display: flex; align-items: center; gap: 10px; margin-top: 6px; }
.points-sum { font-size: 13px; color: var(--text-2); }
.points-sum b { color: var(--danger); font-size: 15px; }

/* 题库已上千道，后端返回全量、前端分页渲染，这里的分页条是必需的 */

</style>
