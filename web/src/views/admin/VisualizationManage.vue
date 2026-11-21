<template>
  <div class="page">
    <div class="page-head">
      <h2>可视化案例管理</h2>
      <el-button type="primary" @click="openAdd">新增案例</el-button>
    </div>

    <div class="card">
      <el-table :data="list" size="small" border>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="案例标题" width="220" />
        <el-table-column prop="knowledge_name" label="关联知识点" width="160" />
        <el-table-column prop="description" label="描述" min-width="260" show-overflow-tooltip />
        <el-table-column prop="config" label="动画参数" min-width="180" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="openEdit(row)">编辑</el-button>
            <el-button text type="danger" size="small" @click="del(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <!-- 后端真分页：page/pageSize 传给 /admin/visualization，total 按全表计数 -->
        <PaginationBar :total="total" v-model:page="page" v-model:pageSize="pageSize" @change="load" />
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑案例' : '新增案例'" width="560px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="关联知识点">
          <el-select v-model="form.knowledgeId" filterable style="width:100%">
            <el-option v-for="k in knowledgeList" :key="k.id" :value="k.id" :label="k.name" />
          </el-select>
        </el-form-item>
        <el-form-item label="案例标题">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="动画参数">
          <el-input v-model="configText" type="textarea" :rows="4" placeholder='JSON，例如 {"order":3}' />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import PaginationBar from '@/components/PaginationBar.vue'

const list = ref([])
const knowledgeList = ref([])
const dialog = ref(false)
const configText = ref('{}')
const form = ref({ id: null, knowledgeId: null, title: '', description: '', config: {} })
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

async function load() {
  // 知识点下拉要保持全量（不传 page → 后端返回全部），列表本身走分页
  const [v, k] = await Promise.all([
    adminApi.visualization({ page: page.value, pageSize: pageSize.value }),
    adminApi.knowledge()
  ])
  list.value = v.data || []
  total.value = Number(v.total || (v.data || []).length)
  knowledgeList.value = k.data || []
  const maxPage = Math.max(1, Math.ceil(total.value / pageSize.value))
  if (page.value > maxPage) {
    page.value = maxPage
    return load()
  }
}
function openAdd() {
  form.value = { id: null, knowledgeId: knowledgeList.value[0]?.id, title: '', description: '', config: {} }
  configText.value = '{}'
  dialog.value = true
}
function openEdit(row) {
  form.value = { id: row.id, knowledgeId: row.knowledge_id, title: row.title, description: row.description, config: {} }
  configText.value = row.config || '{}'
  dialog.value = true
}
async function save() {
  let cfg = {}
  try { cfg = JSON.parse(configText.value || '{}') } catch (e) { ElMessage.warning('参数 JSON 格式错误'); return }
  const payload = { ...form.value, config: cfg }
  const res = form.value.id
    ? await adminApi.updateVisualization(form.value.id, payload)
    : await adminApi.addVisualization(payload)
  ElMessage.success(res.message || '保存成功')
  dialog.value = false
  load()
}
async function del(row) {
  await ElMessageBox.confirm(`确定删除案例「${row.title}」？`, '提示', { type: 'warning' })
  await adminApi.deleteVisualization(row.id)
  ElMessage.success('删除成功')
  load()
}
onMounted(load)
</script>

<style scoped>
.page-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-head h2 { margin: 0; font-size: 20px; }
</style>
