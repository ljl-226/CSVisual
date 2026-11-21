import { ref, computed, onUnmounted, watch } from 'vue'

/**
 * 可视化播放器（通用）
 * 设计：所有动画预先计算成「步骤快照数组」，播放器只负责按索引回放，
 * 从而天然支持 播放 / 暂停 / 单步 / 回退 / 重置 / 倍速 / 拖拽进度。
 *
 * @param {Function|import('vue').Ref} stepSource  返回步骤数组的函数或 ref
 */
export function usePlayer(stepSource) {
  const steps = computed(() => {
    const s = typeof stepSource === 'function' ? stepSource() : stepSource.value
    return Array.isArray(s) ? s : []
  })
  const total = computed(() => steps.value.length)
  const idx = ref(0)
  const playing = ref(false)
  const speed = ref(1)

  let timer = null

  function clear() {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  function tick() {
    if (idx.value >= total.value - 1) {
      pause()
      return
    }
    idx.value++
  }

  function play() {
    if (total.value <= 1) return
    if (idx.value >= total.value - 1) idx.value = 0
    playing.value = true
    clear()
    timer = setInterval(tick, Math.max(120, 900 / speed.value))
  }

  function pause() {
    playing.value = false
    clear()
  }

  function toggle() {
    playing.value ? pause() : play()
  }

  function next() {
    if (idx.value < total.value - 1) idx.value++
    else pause()
  }

  function prev() {
    if (idx.value > 0) idx.value--
  }

  function reset() {
    pause()
    idx.value = 0
  }

  function seek(i) {
    idx.value = Math.min(Math.max(0, i), total.value - 1)
  }

  // 倍速变化时重启定时器以生效
  watch(speed, () => {
    if (playing.value) {
      clear()
      timer = setInterval(tick, Math.max(120, 900 / speed.value))
    }
  })

  // 步数变化只兜底「当前位置已经不存在」的情况。
  // 以前是无条件 idx = 0，结果把两类显式控制全覆盖了：
  //   1. 调参组件本来就有 @change="player.reset()"，watch 再踩一脚纯属重复；
  //   2. 追加操作（链表/栈/队列的「头插/入队」按钮）步数 8→9，idx 被按回第 1 帧，
  //      用户看到的是画面纹丝不动 —— 看起来就像按钮坏了。
  // 现在：回起点交给 reset()，追加交给 playAppended()，watch 只管别越界。
  watch(total, n => {
    if (idx.value > n - 1) idx.value = Math.max(0, n - 1)
  })

  /**
   * 追加了一步操作后调用：从旧末尾自动播放新增的过程帧。
   * 播而不是直接 seek 到最终态 —— 学生要看的是「这一步是怎么发生的」，
   * 啪一下跳到结果等于没演。
   * @param {number} prevTotal 追加前的步数（ops.push 之前读 player.total.value）
   */
  function playAppended(prevTotal) {
    if (total.value <= 1) return
    idx.value = Math.min(Math.max(0, prevTotal - 1), total.value - 1)
    play()
  }

  onUnmounted(clear)

  const current = computed(() => steps.value[idx.value] || null)
  const finished = computed(() => total.value > 0 && idx.value >= total.value - 1)

  return {
    steps, total, idx, playing, speed, current, finished,
    play, pause, toggle, next, prev, reset, seek, playAppended
  }
}
