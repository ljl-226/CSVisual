<template>
  <div class="web-preview">
    <div class="wp-head">
      <b>运行结果</b>
      <el-radio-group v-model="tab" size="small">
        <el-radio-button value="preview">页面预览</el-radio-button>
        <el-radio-button value="console">
          控制台<span v-if="logs.length"> ({{ logs.length }})</span>
        </el-radio-button>
      </el-radio-group>
      <span v-if="hasError" class="wp-err-tip">
        <el-icon><WarningFilled /></el-icon> 有报错
      </span>
      <span class="head-actions">
        <!-- 宿主页面可以在这里塞自己的按钮（比如结果面板的收起 / 放大） -->
        <slot name="actions" />
        <el-button size="small" plain @click="clear">清空</el-button>
      </span>
    </div>

    <div v-show="tab === 'preview'" class="wp-stage">
      <iframe
        class="wp-frame"
        title="预览"
        sandbox="allow-scripts allow-modals allow-forms allow-popups"
        :srcdoc="doc"
      />
    </div>

    <pre
      v-show="tab === 'console'"
      class="wp-console"
      :class="{ error: hasError }"
    >{{ consoleText || '（暂无输出。console.log 的内容会显示在这里）' }}</pre>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { WarningFilled } from '@element-plus/icons-vue'
import { buildPreviewDoc } from '@/utils/webSandbox'

/**
 * 浏览器内沙箱预览：HTML / CSS / JavaScript 直接在本页的 iframe 里执行。
 *
 * 为什么不让这三种语言走后端编译：
 *  1) HTML/CSS 没有「编译输出」这回事，它们的运行结果就是渲染出来的页面；
 *  2) JS 里大量用到 document / window，交给 Node 跑会得到 "document is not defined"，
 *     对初学者是纯误导；
 *  3) 在本页执行意味着把项目发给别人时，这三种语言零配置就能跑，
 *     不依赖对方机器上有没有 Node。
 *
 * iframe 带 sandbox 且不给 allow-same-origin，源为 null，只能靠 postMessage 回传日志。
 */
const props = defineProps({
  language: { type: String, default: 'html' },
  code: { type: String, default: '' },
  /** CSS 实验室配套的示例标记，用来承载用户写的样式 */
  demo: { type: String, default: '' },
  /** 每次自增即触发一次重新执行 */
  runToken: { type: Number, default: 0 }
})

const tab = ref('preview')
const logs = ref([])
const hasError = ref(false)

const doc = computed(() => buildPreviewDoc(props.language, props.code, props.demo, props.runToken))

const consoleText = computed(() =>
  logs.value.map(l => (l.level === 'error' ? '✗ ' : l.level === 'warn' ? '! ' : '') + l.text).join('\n')
)

function clear() {
  logs.value = []
  hasError.value = false
}

function onMessage(e) {
  const d = e && e.data
  if (!d || d.__csvisual !== true) return
  const text = String(d.text || '')
  if (logs.value.length > 300) logs.value.shift()
  logs.value.push({ level: d.level || 'log', text })
  if (d.level === 'error') hasError.value = true
}

/** 每次重新执行都要清空上一次的输出，否则旧报错会一直挂着 */
watch(
  () => props.runToken,
  () => { logs.value = []; hasError.value = false }
)
watch(
  () => props.language,
  () => { logs.value = []; hasError.value = false; tab.value = 'preview' }
)

onMounted(() => window.addEventListener('message', onMessage))
onBeforeUnmount(() => window.removeEventListener('message', onMessage))
</script>

<style scoped>
/* 纵向 flex：头部固定，预览舞台吃掉剩余高度。
   iframe 用 absolute 填满舞台 —— 不写死 340px，
   卡片有空间就更高，空间紧张时退到 min-height 保底并靠外层滚动。 */
.web-preview { display: flex; flex-direction: column; align-items: stretch; }
.wp-head { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; flex-shrink: 0; }
.wp-head .head-actions { margin-left: auto; display: flex; align-items: center; gap: 6px; }
.wp-err-tip {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 12px; color: #c45656;
}
.wp-stage { position: relative; flex: 1 1 auto; min-height: 240px; }
.wp-frame {
  position: absolute; inset: 0; width: 100%; height: 100%;
  border: 1px solid var(--border);
  border-radius: 8px; background: #fff; display: block;
}
.wp-console {
  margin: 0; padding: 12px 14px; background: #1f2733; color: #d8e2ee;
  border-radius: 8px; font: 13px/1.7 Consolas, Monaco, monospace;
  white-space: pre-wrap; word-break: break-all;
  min-height: 120px; max-height: 320px; overflow: auto;
}
.wp-console.error { background: #3a2020; color: #ffb4b4; }
</style>
