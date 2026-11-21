<template>
  <div class="page">
    <div class="page-head">
      <h2>知识点管理</h2>
      <div class="head-tools">
        <el-select v-model="filterCourse" placeholder="全部课程" clearable style="width:160px" @change="onFilterChange">
          <el-option v-for="c in courses" :key="c.id" :value="c.id" :label="c.name" />
        </el-select>
        <el-input v-model="keyword" placeholder="搜索知识点" clearable style="width:180px" @change="onFilterChange" />
        <el-button type="primary" @click="openAdd">新增知识点</el-button>
      </div>
    </div>

    <div class="card">
      <el-table :data="list" size="small" border>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="course_name" label="课程" width="130" />
        <el-table-column prop="name" label="知识点名称" width="160" />
        <el-table-column prop="summary" label="摘要" min-width="240" show-overflow-tooltip />
        <el-table-column prop="route" label="可视化路由" width="180" />
        <el-table-column prop="sort_no" label="排序" width="70" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="openEdit(row)">编辑</el-button>
            <el-button text type="danger" size="small" @click="del(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <!-- 后端真分页：page/pageSize 传给 /admin/knowledge，total 按当前筛选条件计数 -->
      <PaginationBar :total="total" v-model:page="page" v-model:pageSize="pageSize" @change="load" />
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑知识点' : '新增知识点'" width="640px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="所属课程">
          <el-select v-model="form.courseId" style="width:100%">
            <el-option v-for="c in courses" :key="c.id" :value="c.id" :label="c.name" />
          </el-select>
        </el-form-item>
        <el-form-item label="名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="摘要">
          <el-input v-model="form.summary" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="正文(MD)">
          <el-input v-model="form.content" type="textarea" :rows="8" />
        </el-form-item>
        <el-form-item label="可视化路由">
          <el-input v-model="form.route" placeholder="/vis/quick-sort" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sortNo" />
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
import { adminApi, courseApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import PaginationBar from '@/components/PaginationBar.vue'

const list = ref([])
const courses = ref([])
const filterCourse = ref(null)
const keyword = ref('')
const dialog = ref(false)
const form = ref({ id: null, courseId: null, name: '', summary: '', content: '', route: '', sortNo: 0 })
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

async function load() {
  const res = await adminApi.knowledge({
    courseId: filterCourse.value, keyword: keyword.value,
    page: page.value, pageSize: pageSize.value
  })
  list.value = res.data || []
  total.value = Number(res.total || (res.data || []).length)
  // 筛选/删除后当前页可能超出范围（比如删到只剩前几条），回退到最后一页
  const maxPage = Math.max(1, Math.ceil(total.value / pageSize.value))
  if (page.value > maxPage) {
    page.value = maxPage
    return load()
  }
}
/* 换筛选条件时回第 1 页：不回的话可能停在一个空页上，看着像「搜不到」 */
function onFilterChange() {
  page.value = 1
  load()
}
function openAdd() {
  form.value = { id: null, courseId: courses.value[0]?.id, name: '', summary: '', content: '', route: '', sortNo: 0 }
  dialog.value = true
}
function openEdit(row) {
  form.value = {
    id: row.id, courseId: row.course_id, name: row.name, summary: row.summary,
    content: row.content, route: row.route, sortNo: row.sort_no
  }
  dialog.value = true
}
async function save() {
  if (!form.value.name || !form.value.courseId) {
    ElMessage.warning('课程和名称必填')
    return
  }
  const res = form.value.id
    ? await adminApi.updateKnowledge(form.value.id, form.value)
    : await adminApi.addKnowledge(form.value)
  ElMessage.success(res.message || '保存成功')
  dialog.value = false
  load()
}
async function del(row) {
  await ElMessageBox.confirm(`确定删除知识点「${row.name}」？`, '提示', { type: 'warning' })
  await adminApi.deleteKnowledge(row.id)
  ElMessage.success('删除成功')
  load()
}

onMounted(async () => {
  const c = await courseApi.list()
  courses.value = c.data || []
  load()
})
</script>

<style scoped>
.page-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 10px; }
.page-head h2 { margin: 0; font-size: 20px; }
.head-tools { display: flex; gap: 8px; flex-wrap: wrap; }
</style>
