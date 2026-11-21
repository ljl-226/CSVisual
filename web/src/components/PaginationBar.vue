<template>
  <!-- 全站统一的分页栏模板：所有分页查询（管理后台 / 题库 / 算法题 / 个人中心）
       都用这一个组件，改样式或行为只动这一处。
       默认底部居中；el-pagination 自带 margin 补偿需要归零才能真正居中。 -->
  <div v-if="total > 0" class="pager-bar">
    <el-pagination
      background
      :layout="layout"
      :total="total"
      :current-page="page"
      :page-size="pageSize"
      :page-sizes="sizes"
      :pager-count="pagerCount"
      @current-change="onPage"
      @size-change="onSize"
    />
  </div>
</template>

<script setup>
/* 受控组件：分页状态由父级持有（v-model:page / v-model:pageSize），
 * 组件只负责「把用户的操作翻译成一次 change 事件」。
 * 父级统一用法：
 *   <PaginationBar :total="total" v-model:page="page"
 *                  v-model:pageSize="pageSize" @change="load" />
 * 约定：
 * ① 换每页条数自动回第 1 页（change 事件里 page 恒为 1）；
 * ② page 超出总页数时由父级在 load 里回退最后一页再拉一次（各页已有此逻辑）。
 */
const props = defineProps({
  total: { type: Number, default: 0 },
  page: { type: Number, default: 1 },
  pageSize: { type: Number, default: 20 },
  // 每页条数可选项；列表体型小的页面（如个人中心）可传更小的一档
  sizes: { type: Array, default: () => [20, 50, 100, 200] },
  layout: { type: String, default: 'total, sizes, prev, pager, next' },
  // 页码按钮过多时折叠（el-pagination 原生能力），窄屏不易撑爆
  pagerCount: { type: Number, default: 7 }
})

const emit = defineEmits(['update:page', 'update:pageSize', 'change'])

function onPage(p) {
  if (p === props.page) return
  emit('update:page', p)
  emit('change', { page: p, pageSize: props.pageSize })
}

function onSize(s) {
  if (s === props.pageSize) return
  emit('update:pageSize', s)
  emit('update:page', 1)
  emit('change', { page: 1, pageSize: s })
}
</script>

<style scoped>
.pager-bar {
  margin-top: 14px;
  display: flex;
  justify-content: center;
}
/* el-pagination 默认自带 margin，居中时会向右偏半个 margin */
.pager-bar :deep(.el-pagination) { margin: 0; }
</style>
