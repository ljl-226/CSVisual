<template>
  <div class="page vis-page">
    <el-breadcrumb separator="/" style="margin-bottom:12px">
      <el-breadcrumb-item :to="{ path: '/courses' }">课程中心</el-breadcrumb-item>
      <el-breadcrumb-item v-if="knowledge" :to="{ path: '/knowledge/' + knowledge.id }">{{ knowledge.name }}</el-breadcrumb-item>
      <el-breadcrumb-item>可视化演示</el-breadcrumb-item>
    </el-breadcrumb>

    <component v-if="comp" :is="comp" v-bind="entry.props || {}" :key="routeKey" />

    <div v-else class="card empty-card">
      <el-empty description="未找到该可视化页面">
        <el-button type="primary" @click="$router.push('/courses')">返回课程中心</el-button>
      </el-empty>
    </div>

    <!-- 底部：知识点链接 -->
    <div v-if="knowledge" class="card vis-foot fade-up">
      <div class="foot-main">
        <span class="foot-chip">下一步</span>
        <b>{{ knowledge.name }}</b>
        <p class="muted small">{{ knowledge.summary }}</p>
      </div>
      <div class="foot-actions">
        <el-button round @click="$router.push('/knowledge/' + knowledge.id)">查看知识点讲解</el-button>
        <el-button type="primary" plain round @click="$router.push('/practice/' + knowledge.id)">做配套练习</el-button>
        <el-button type="primary" round @click="$router.push('/agent?q=' + encodeURIComponent('讲解' + knowledge.name))">问智能助手</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, shallowRef, defineAsyncComponent } from 'vue'
import { useRoute } from 'vue-router'
import { courseApi } from '@/api'
import { VIS_MAP } from '@/data/visMap'


const route = useRoute()
const comp = shallowRef(null)
const entry = ref(null)
const knowledge = ref(null)
const routeKey = ref('')

async function load() {
  const name = route.params.name
  const e = VIS_MAP[name]
  routeKey.value = name
  if (!e) {
    comp.value = null
    entry.value = null
    knowledge.value = null
    return
  }
  entry.value = e
  comp.value = defineAsyncComponent(e.comp)
  try {
    const res = await courseApi.knowledge(e.kid)
    knowledge.value = res.data ? res.data.knowledge : null
  } catch (err) {
    knowledge.value = null
  }
}

watch(() => route.params.name, load, { immediate: true })
</script>

<style scoped>
.vis-page { max-width: 1180px; }
.empty-card { padding: 40px; border-radius: var(--radius-lg); }
.vis-foot {
  margin-top: 16px; padding: 18px 22px;
  border-radius: var(--radius-lg);
  background: linear-gradient(120deg, #f9fbff 0%, #ffffff 60%, #f8fffb 100%);
  display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap;
}
.foot-main { min-width: 0; }
.foot-chip {
  display: inline-block; font-size: 11px; font-weight: 700; letter-spacing: 0.5px;
  color: var(--success); background: var(--success-light);
  border-radius: 20px; padding: 2px 10px; margin-bottom: 6px;
}
.vis-foot b { font-size: 16px; }
.vis-foot p { margin: 5px 0 0; line-height: 1.7; }
.foot-actions { display: flex; gap: 9px; flex-wrap: wrap; }
</style>
