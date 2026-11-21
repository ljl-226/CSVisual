<template>
  <VisFrame title="页面置换算法 · FIFO / LRU / OPT" desc="内存无空闲块时选择换出页面：FIFO 换最早进入的，LRU 换最近最久未用的，OPT 换未来最久不用的" :player="player" :status-text="statusText" back-to="/knowledge/16">
    <template #extra>
      <span class="small muted">物理块</span>
      <el-input-number v-model="frames" size="small" :min="2" :max="5" style="width:90px" @change="player.reset()" />
      <el-input v-model="seqText" size="small" style="width:220px" placeholder="访问序列" @change="player.reset()" />
      <el-button size="small" plain @click="player.reset()">重播</el-button>
    </template>

    <!-- 访问序列 -->
    <div class="seq-area">
      <span class="small muted">页面访问序列：</span>
      <span
        v-for="(p, i) in sequence" :key="i"
        class="seq-cell"
        :class="{ cur: i === curIndex, done: i < curIndex }"
      >{{ p }}</span>
    </div>

    <el-row :gutter="12">
      <el-col :span="8" v-for="algo in algos" :key="algo.key">
        <div class="algo-card" :class="{ best: algo.key === 'opt' }">
          <div class="algo-head">
            <b>{{ algo.name }}</b>
            <el-tag size="small" :type="algo.key === 'opt' ? 'warning' : 'info'" effect="light">
              {{ algo.key === 'opt' ? '理论最优（不可实现）' : '可实现' }}
            </el-tag>
          </div>
          <div class="frame-row">
            <div
              v-for="(f, i) in (state[algo.key] || []).frames" :key="i"
              class="frame-cell"
              :class="{
                empty: f === null,
                hit: (state[algo.key] || {}).hitIndex === i,
                miss: (state[algo.key] || {}).fault && (state[algo.key] || {}).replaceIndex === i
              }"
            >{{ f === null ? '空' : f }}</div>
          </div>
          <div class="algo-stat">
            <span>缺页 {{ (state[algo.key] || {}).faults || 0 }} 次</span>
            <span>缺页率 {{ faultRate((state[algo.key] || {}).faults || 0) }}%</span>
          </div>
          <div class="algo-desc small muted">{{ (state[algo.key] || {}).desc || algo.desc }}</div>
        </div>
      </el-col>
    </el-row>

    <div class="pr-tip">
      <el-divider />
      <div class="panel-title">算法对比</div>
      <ul class="rules">
        <li><b>FIFO</b>：实现简单，但可能出现 <b>Belady 异常</b>（物理块增加，缺页次数反而上升）</li>
        <li><b>LRU</b>：性能好，接近 OPT；需硬件支持（寄存器/栈）记录访问时间</li>
        <li><b>OPT</b>：缺页率最低，但需预知未来访问序列，<b>无法实现</b>，仅作评价基准</li>
        <li><b>缺页中断处理</b>：保护现场 → 调入页面（无空闲块则置换，修改过的页需写回外存）→ 更新页表 → 恢复执行</li>
      </ul>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#dcf3e7"></i> 命中（页面已在内存）</span>
      <span><i class="dot" style="background:#fdeaea"></i> 缺页并置换</span>
      <span><i class="dot" style="background:#f7f9fc"></i> 空闲物理块</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const frames = ref(3)
const seqText = ref('7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1')
const sequence = computed(() =>
  seqText.value.split(/[,，\s]+/).map(v => Number(v.trim())).filter(v => !isNaN(v))
)

const algos = [
  { key: 'fifo', name: 'FIFO 先进先出', desc: '换出最早进入内存的页面' },
  { key: 'lru', name: 'LRU 最近最久未用', desc: '换出最近最久没有被访问的页面' },
  { key: 'opt', name: 'OPT 最佳置换', desc: '换出未来最长时间不会被访问的页面' }
]

const steps = computed(() => {
  const seq = sequence.value
  const m = frames.value
  const mem = { fifo: [], lru: [], opt: [] }
  const lastUsed = { lru: {} }
  const faults = { fifo: 0, lru: 0, opt: 0 }
  const out = []

  function runAlgo(key, page, idx) {
    const cur = mem[key]
    if (cur.includes(page)) {
      if (key === 'lru') lastUsed.lru[page] = idx
      return { frames: [...cur], fault: false, hitIndex: cur.indexOf(page), replaceIndex: -1, desc: `页面 ${page} 已在内存中 → 命中，不缺页` }
    }
    faults[key]++
    if (cur.length < m) {
      cur.push(page)
      if (key === 'lru') lastUsed.lru[page] = idx
      return {
        frames: [...cur], fault: true, hitIndex: -1, replaceIndex: cur.length - 1,
        desc: `缺页！还有空闲块，直接将页面 ${page} 装入`
      }
    }
    let victimIdx = 0
    let victimPage = null
    if (key === 'fifo') {
      victimIdx = 0
      victimPage = cur[0]
      cur.shift()
      cur.push(page)
    } else if (key === 'lru') {
      let minIdx = Infinity
      cur.forEach((p, i) => {
        const t = lastUsed.lru[p] !== undefined ? lastUsed.lru[p] : -1
        if (t < minIdx) { minIdx = t; victimIdx = i; victimPage = p }
      })
      cur[victimIdx] = page
      lastUsed.lru[page] = idx
    } else {
      // OPT：换出未来最久不用的
      let far = -1
      cur.forEach((p, i) => {
        const next = seq.indexOf(p, idx + 1)
        const dist = next === -1 ? Infinity : next
        if (dist > far) { far = dist; victimIdx = i; victimPage = p }
      })
      cur[victimIdx] = page
    }
    return {
      frames: [...cur], fault: true, hitIndex: -1, replaceIndex: victimIdx,
      desc: `缺页且无空闲块 → 换出页面 ${victimPage}，装入 ${page}`
    }
  }

  for (let i = 0; i < seq.length; i++) {
    const page = seq[i]
    const res = {}
    algos.forEach(a => {
      res[a.key] = { ...runAlgo(a.key, page, i), faults: faults[a.key] }
    })
    out.push({
      index: i, page, state: res,
      desc: `访问页面 ${page}：FIFO ${res.fifo.fault ? '缺页' : '命中'}，LRU ${res.lru.fault ? '缺页' : '命中'}，OPT ${res.opt.fault ? '缺页' : '命中'}`
    })
  }
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || { index: 0, page: null, state: {}, desc: '点击播放开始模拟' })
const statusText = computed(() => cur.value.desc)
const curIndex = computed(() => cur.value.index || 0)
const state = computed(() => cur.value.state || {})

function faultRate(f) {
  const total = (curIndex.value || 0) + 1
  return total ? Math.round((f / total) * 100) : 0
}
</script>

<style scoped>
.seq-area { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; margin-bottom: 12px; }
.seq-cell {
  width: 26px; height: 26px; line-height: 26px; text-align: center; border-radius: 4px;
  border: 1px solid var(--border); font-size: 12px; background: #fff; color: var(--text-3);
}
.seq-cell.done { background: #f0f2f6; }
.seq-cell.cur { background: var(--brand); color: #fff; border-color: var(--brand); font-weight: 700; }
.algo-card { border: 1px solid var(--border); border-radius: 10px; padding: 12px; background: #fff; height: 100%; }
.algo-card.best { border-color: #f0d9ae; background: #fffdf7; }
.algo-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; font-size: 13px; }
.frame-row { display: flex; gap: 6px; margin-bottom: 8px; }
.frame-cell {
  width: 40px; height: 44px; line-height: 44px; text-align: center; border-radius: 6px;
  border: 1.5px solid var(--border); font-weight: 600; font-size: 15px; background: #f7f9fc; color: var(--text-3);
}
.frame-cell.empty { border-style: dashed; }
.frame-cell.hit { background: #dcf3e7; border-color: var(--success); color: #176b48; }
.frame-cell.miss { background: #fdeaea; border-color: var(--danger); color: #a32c2c; }
.algo-stat { display: flex; justify-content: space-between; font-size: 12px; color: var(--text-2); margin-bottom: 6px; }
.algo-desc { min-height: 34px; line-height: 1.6; }
.pr-tip { margin-top: 16px; }
.panel-title { font-size: 13px; font-weight: 600; margin-bottom: 6px; color: var(--text-2); }
.rules { padding-left: 18px; margin: 0; }
.rules li { font-size: 12px; line-height: 1.9; color: var(--text-2); }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
