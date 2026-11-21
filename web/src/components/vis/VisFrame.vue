<template>
  <div class="vis-frame card" :class="{ 'is-full': isFull }">
    <div class="vis-head">
      <div class="head-left">
        <h3>{{ title }}</h3>
        <p class="muted small">{{ desc }}</p>
      </div>
      <div class="head-right">
        <slot name="extra" />
        <el-button text type="primary" @click="toggleFull">
          <el-icon><FullScreen v-if="!isFull" /><Aim v-else /></el-icon>
          {{ isFull ? '退出全屏' : '全屏观看' }}
        </el-button>
        <el-button v-if="backTo && !isFull" text type="primary" @click="$router.push(backTo)">返回知识点</el-button>
      </div>
    </div>

    <div class="vis-canvas">
      <slot :step="player.current.value" :index="player.idx.value" />
    </div>

    <!-- 状态说明 -->
    <div class="vis-status" v-if="statusText" :class="{ 'is-live': player.playing.value }">
      <span class="status-badge"><el-icon><InfoFilled /></el-icon></span>
      <span class="status-text">{{ statusText }}</span>
    </div>

    <!-- 控制条 -->
    <div class="vis-controls">
      <el-button-group class="ctrl-group">
        <el-button :disabled="player.idx.value <= 0" @click="player.prev()" :icon="ArrowLeft" title="上一步" />
        <el-button type="primary" class="btn-play" @click="player.toggle()">
          <el-icon><VideoPause v-if="player.playing.value" /><VideoPlay v-else /></el-icon>
          {{ player.playing.value ? '暂停' : '播放' }}
        </el-button>
        <el-button :disabled="player.finished.value" @click="player.next()" title="下一步">
          <el-icon><ArrowRight /></el-icon>
        </el-button>
        <el-button @click="player.reset()" :icon="RefreshLeft" title="重置" />
      </el-button-group>

      <div class="slider-wrap">
        <span class="step-badge">{{ player.idx.value + 1 }} / {{ player.total.value }}</span>
        <el-slider
          v-model="player.idx.value"
          :min="0"
          :max="Math.max(0, player.total.value - 1)"
          :show-tooltip="false"
          style="flex:1"
          @input="player.pause()"
        />
      </div>

      <div class="speed-wrap">
        <span class="small muted">速度</span>
        <el-select v-model="player.speed.value" size="small" style="width:82px">
          <el-option :value="0.5" label="0.5x" />
          <el-option :value="1" label="1x" />
          <el-option :value="1.5" label="1.5x" />
          <el-option :value="2" label="2x" />
          <el-option :value="4" label="4x" />
        </el-select>
      </div>
    </div>

    <!-- 图例 -->
    <div class="vis-legend" v-if="$slots.legend">
      <slot name="legend" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { InfoFilled, ArrowLeft, ArrowRight, RefreshLeft, FullScreen, Aim } from '@element-plus/icons-vue'

defineProps({
  title: { type: String, default: '可视化演示' },
  desc: { type: String, default: '' },
  statusText: { type: String, default: '' },
  backTo: { type: String, default: '' },
  player: { type: Object, required: true }
})

/**
 * 全屏观看：CSS fixed 伪全屏 + 尽量请求整页原生全屏。
 *
 * 为什么不再对 .vis-frame 调 Fullscreen API：Fullscreen API 生效时浏览器
 * 只渲染全屏元素这一棵子树，而 el-select / el-tooltip 的浮层是 teleport 到
 * <body> 的 —— 不在全屏子树里，浮层完全不可见、点不到（71 个动画的通用 bug）。
 * 改为 fixed 覆盖层后 <body> 仍在渲染，浮层（z-index 2000+）天然盖在覆盖层
 * （z-index 1900）上，全屏里所有下拉框都能正常展开。
 * 原生全屏改为请求 documentElement（整页都在全屏子树内，浮层同样可见），
 * 失败（无手势 / iframe 受限 / 老浏览器）不影响伪全屏本身。
 */
const isFull = ref(false)

async function toggleFull() {
  isFull.value = !isFull.value
  document.body.style.overflow = isFull.value ? 'hidden' : ''
  try {
    if (isFull.value && !document.fullscreenElement) {
      const el = document.documentElement
      if (el.requestFullscreen) await el.requestFullscreen().catch(() => {})
      else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen()
    } else if (!isFull.value && document.fullscreenElement) {
      await document.exitFullscreen().catch(() => {})
    }
  } catch (e) {
    // 原生全屏被拒绝时保持伪全屏即可，不必打断观看
  }
}

function closeFull() {
  if (!isFull.value) return
  isFull.value = false
  document.body.style.overflow = ''
  if (document.fullscreenElement) document.exitFullscreen().catch(() => {})
}

function onEscKey(e) {
  if (e.key === 'Escape') closeFull()
}

// 用户用 Esc 退出原生全屏时，覆盖层一起收起，避免出现「半全屏」的困惑态
function syncFull() {
  if (!document.fullscreenElement && isFull.value) closeFull()
}

onMounted(() => {
  document.addEventListener('fullscreenchange', syncFull)
  document.addEventListener('webkitfullscreenchange', syncFull)
  window.addEventListener('keydown', onEscKey)
})
onBeforeUnmount(() => {
  document.removeEventListener('fullscreenchange', syncFull)
  document.removeEventListener('webkitfullscreenchange', syncFull)
  window.removeEventListener('keydown', onEscKey)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.vis-frame {
  padding: 20px;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
}

/* ---------- 全屏模式：fixed 覆盖层，画布占满剩余高度，控制条固定在底部 ----------
 * z-index 取 1900：压过顶栏(100)，但让位于 EP 弹层（teleport 到 body 的
 * popper 从 2000 起递增），这样全屏里的下拉框才能浮在覆盖层上面。 */
.vis-frame.is-full {
  position: fixed;
  inset: 0;
  z-index: 1900;
  border-radius: 0;
  display: flex; flex-direction: column;
  padding: 18px 26px;
  overflow: auto;
  background: var(--card);
}
.vis-frame.is-full .vis-canvas {
  flex: 1; min-height: 0;
  display: flex; flex-direction: column;
  overflow: auto;
}
/*
 * 居中的正确写法：auto margin，而不是 justify-content: center。
 * flex 容器 overflow:auto + justify-content:center 有个老毛病——
 * 内容一旦比容器高，顶部会被推到「滚动条够不着」的负区域，
 * 表现就是全屏后动画的上边缘（内容矮时还有下边缘）永远看不到。
 * margin:auto 在内容矮时同样居中，内容超高时 margin 归零、从顶部开始排，
 * 全程可滚，不会丢边。
 */
.vis-frame.is-full .vis-canvas > * {
  margin: auto 0;
  flex-shrink: 0;
}
.vis-frame.is-full .vis-controls,
.vis-frame.is-full .vis-status,
.vis-frame.is-full .vis-legend { flex-shrink: 0; }

/* ---------- 头部 ---------- */
.vis-head {
  display: flex; justify-content: space-between; align-items: flex-start;
  gap: 16px; margin-bottom: 14px;
}
.head-left { position: relative; padding-left: 12px; min-width: 0; }
.head-left::before {
  content: ''; position: absolute; left: 0; top: 4px; bottom: 4px;
  width: 4px; border-radius: 3px; background: var(--grad-brand);
}
.vis-head h3 { margin: 0 0 4px; font-size: 18px; letter-spacing: 0.2px; }
.vis-head p { margin: 0; line-height: 1.6; }
.head-right { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }

/* ---------- 状态条 ---------- */
.vis-status {
  display: flex; align-items: center; gap: 9px; margin-top: 12px;
  background: linear-gradient(90deg, var(--brand-light) 0%, var(--status-bg) 100%);
  border-left: 3px solid var(--brand);
  color: var(--brand-deep);
  padding: 9px 13px; border-radius: 0 10px 10px 0;
  font-size: 13px; min-height: 38px; line-height: 1.6;
}
.status-badge {
  flex-shrink: 0; width: 19px; height: 19px; border-radius: 50%;
  background: var(--brand); color: #fff;
  display: flex; align-items: center; justify-content: center; font-size: 11px;
}
.vis-status.is-live .status-badge { animation: pulse 1.5s ease-in-out infinite; }
@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(59, 110, 246, 0.45); }
  50% { box-shadow: 0 0 0 7px rgba(59, 110, 246, 0); }
}
.status-text { flex: 1; }

/* ---------- 控制条 ---------- */
.vis-controls {
  display: flex; align-items: center; gap: 16px; margin-top: 16px;
  padding-top: 15px; border-top: 1px solid var(--border-2); flex-wrap: wrap;
}
.ctrl-group :deep(.el-button) { font-weight: 500; }
.ctrl-group :deep(.el-button--primary) {
  background: var(--grad-brand); border: none;
  box-shadow: 0 3px 10px rgba(59, 110, 246, 0.28);
}
.ctrl-group :deep(.el-button--primary:hover) {
  box-shadow: 0 5px 16px rgba(59, 110, 246, 0.38);
  filter: brightness(1.05);
}
.slider-wrap { display: flex; align-items: center; gap: 11px; flex: 1; min-width: 200px; }
.step-badge {
  width: 56px; text-align: center; font-size: 12px; color: var(--text-2);
  background: var(--soft-bg); border-radius: 20px; padding: 3px 0; font-variant-numeric: tabular-nums;
}
.speed-wrap { display: flex; align-items: center; gap: 6px; }

/* ---------- 图例：做成小药丸 ---------- */
.vis-legend {
  margin-top: 14px; display: flex; gap: 9px; flex-wrap: wrap;
  font-size: 12px; color: var(--text-2);
}
.vis-legend :deep(span) {
  display: inline-flex; align-items: center; gap: 5px;
  background: var(--soft-bg); border: 1px solid var(--border-2);
  border-radius: 20px; padding: 3px 11px;
}

/* ---------- 响应式 ----------
   画布本身靠 .vis-canvas 的 overflow-x:auto 横滚（动画 SVG 多有固定宽度，
   等比缩放会把字缩到看不清，横滚反而更可读）；这里只收外框与控制条。 */
@media (max-width: 768px) {
  .vis-frame { padding: 14px; border-radius: 12px; }
  .vis-head { flex-direction: column; gap: 8px; margin-bottom: 10px; }
  .vis-head h3 { font-size: 16px; }
  .head-right { justify-content: flex-start; }
  .vis-controls { gap: 10px; margin-top: 12px; padding-top: 12px; }
  .slider-wrap { min-width: 100%; }
  .vis-status { min-height: 0; font-size: 12px; padding: 8px 10px; }
  .vis-frame.is-full { padding: 12px 14px; }
}
@media (max-width: 480px) {
  .vis-frame { padding: 11px 10px; }
  .vis-head h3 { font-size: 15px; }
  .ctrl-group { display: flex; width: 100%; }
  .ctrl-group :deep(.el-button) { flex: 1; padding-left: 6px; padding-right: 6px; }
  .btn-play { flex: 1.6 1 auto; }
  .speed-wrap { width: 100%; justify-content: flex-end; }
}
</style>
