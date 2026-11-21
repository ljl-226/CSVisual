<template>
  <VisFrame title="Cache 地址映射 · 直接 / 全相联 / 组相联" desc="主存块按规则装入 Cache 行：命中直接访问，缺失则装入或按策略替换，三种映射方式决定「能放哪」" :player="player" :status-text="statusText" back-to="/knowledge/34">
    <template #extra>
      <el-select v-model="mode" size="small" style="width:130px" @change="player.reset()">
        <el-option value="direct" label="直接映射" />
        <el-option value="full" label="全相联" />
        <el-option value="set" label="2 路组相联" />
      </el-select>
      <el-select v-model="policy" size="small" style="width:110px" @change="player.reset()">
        <el-option value="lru" label="LRU 替换" />
        <el-option value="fifo" label="FIFO 替换" />
      </el-select>
    </template>

    <div class="cm-wrap">
      <svg :width="W" :height="H" class="cm-svg">
        <text :x="12" :y="16" font-size="12" fill="#8b95a3">
          访问序列：{{ SEQ.join(' → ') }}　（第 {{ cur.stepNo }} 次访问：块 {{ cur.block }}）
        </text>

        <!-- Cache 行 -->
        <g>
          <text :x="12" :y="44" font-size="12" font-weight="600" fill="#1f2733">Cache（{{ lines.length }} 行{{ mode === 'set' ? ' / ' + setCount + ' 组 × ' + waysPerSet + ' 路' : '' }}）</text>
          <g v-for="(ln, i) in lines" :key="'l'+i">
            <rect :x="12" :y="54 + i * 26" :width="W - 24" height="23" rx="4"
                  :fill="cur.hitIndex === i ? '#dcf3e7' : (cur.loadIndex === i ? '#fff3e0' : '#fff')"
                  :stroke="cur.hitIndex === i ? '#22a06b' : (cur.loadIndex === i ? '#f2994a' : '#dfe4ec')" stroke-width="1.5" />
            <text :x="20" :y="69 + i * 26" font-size="11" fill="#8b95a3">行 {{ i }}</text>
            <text v-if="mode === 'set'" :x="62" :y="69 + i * 26" font-size="11" fill="#8b95a3">组 {{ Math.floor(i / 2) }}</text>
            <text :x="110" :y="69 + i * 26" font-size="11" :fill="ln.valid ? '#1f2733' : '#c0c8d4'">
              有效位 {{ ln.valid ? 1 : 0 }}
            </text>
            <text :x="196" :y="69 + i * 26" font-size="11" :fill="ln.valid ? '#1f2733' : '#c0c8d4'">
              标记 {{ ln.valid ? ln.tag : '—' }}
            </text>
            <text :x="286" :y="69 + i * 26" font-size="11" :fill="ln.valid ? '#1f2733' : '#c0c8d4'">
              {{ ln.valid ? '块 ' + ln.block : '（空）' }}
            </text>
            <text :x="380" :y="69 + i * 26" font-size="11" fill="#8b95a3">
              {{ ln.valid ? (policy === 'lru' ? 'LRU 计数 ' + ln.stamp : '装入序 ' + ln.stamp) : '' }}
            </text>
            <text v-if="cur.hitIndex === i" :x="W - 76" :y="69 + i * 26" font-size="12" fill="#22a06b" font-weight="700">命中 ✓</text>
            <text v-else-if="cur.loadIndex === i" :x="W - 76" :y="69 + i * 26" font-size="12" :fill="cur.evict ? '#e05252' : '#f2994a'" font-weight="700">
              {{ cur.evict ? '替换' : '装入' }}
            </text>
          </g>
        </g>

        <!-- 主存块示意 -->
        <g>
          <text :x="12" :y="54 + lines.length * 26 + 30" font-size="12" font-weight="600" fill="#1f2733">主存块（当前访问）</text>
          <rect
            :x="120" :y="54 + lines.length * 26 + 12" width="60" height="26" rx="4"
            fill="#eef3ff" stroke="#3b6ef6" stroke-width="2"
          />
          <text :x="150" :y="54 + lines.length * 26 + 29" text-anchor="middle" font-size="12" fill="#3b6ef6" font-weight="700">
            块 {{ cur.block }}
          </text>
        </g>
      </svg>

      <div class="cm-panel">
        <div class="formula"><code>{{ formulaText }}</code></div>
        <el-divider />
        <div class="info-row"><span>当前访问的主存块</span><b style="color:var(--brand)">{{ cur.block }}</b></div>
        <div class="info-row"><span>{{ mode === 'direct' ? 'Cache 行号 = 块号 mod 行数' : (mode === 'set' ? '组号 = 块号 mod 组数' : '可放入任意行') }}</span>
          <b>{{ cur.targetText }}</b>
        </div>
        <div class="info-row"><span>本次结果</span>
          <el-tag size="small" :type="cur.hitIndex >= 0 ? 'success' : 'warning'">{{ cur.hitIndex >= 0 ? '命中 HIT' : '缺失 MISS' }}</el-tag>
        </div>
        <div class="info-row"><span>累计命中 / 访问</span><b style="color:var(--success)">{{ cur.hits }} / {{ cur.stepNo }}</b></div>
        <div class="info-row"><span>当前命中率</span><b>{{ cur.stepNo ? ((cur.hits / cur.stepNo) * 100).toFixed(1) : '0.0' }}%</b></div>
        <el-divider />
        <div class="tbl">
          <div class="tbl-head"><span>#</span><span>块号</span><span>结果</span><span>命中率</span></div>
          <div v-for="(s, i) in player.steps.value" :key="i" class="tbl-row" :class="{ active: i === player.idx.value }" @click="player.seek(i)">
            <span>{{ s.stepNo }}</span><span>{{ s.block }}</span>
            <span :style="{ color: s.hitIndex >= 0 ? '#22a06b' : '#e05252' }">{{ s.hitIndex >= 0 ? 'HIT' : 'MISS' }}</span>
            <span>{{ s.stepNo ? ((s.hits / s.stepNo) * 100).toFixed(0) : 0 }}%</span>
          </div>
        </div>
        <p class="small muted tip">{{ modeNote }}</p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#22a06b"></i> 命中</span>
      <span><i class="dot" style="background:#f2994a"></i> 缺失后装入</span>
      <span><i class="dot" style="background:#e05252"></i> 替换掉旧块</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const SEQ = [1, 4, 1, 9, 4, 1, 8, 9, 2, 1, 4, 9]
const mode = ref('direct')
const policy = ref('lru')

const W = 560
const lineCount = 8
const waysPerSet = 2            // 每组 2 路
const setCount = lineCount / waysPerSet  // 8 行 / 2 路 = 4 组（组数 ≠ 路数）
const lines = computed(() => Array.from({ length: lineCount }, (_, i) => ({ i })))
const H = computed(() => 54 + lineCount * 26 + 60)

const formulaText = computed(() => {
  if (mode.value === 'direct') return '直接映射：行号 = 块号 mod Cache 行数；标记 = 块号 div 行数'
  if (mode.value === 'full') return '全相联：主存块可装入任意 Cache 行；标记 = 完整块号'
  return '组相联：组号 = 块号 mod 组数；组内任意行可放；标记 = 块号 div 组数'
})
const modeNote = computed(() => {
  if (mode.value === 'direct') return '直接映射硬件最简单（只需比较一个标记），但同一行的不同块会反复冲突（抖动），命中率最低。'
  if (mode.value === 'full') return '全相联冲突最少、命中率最高，但每次要和所有行的标记并行比较，比较器成本最高。'
  return '组相联是两者的折中：组内全相联、组间直接映射，是现代 CPU 的主流方案（如 8 路 / 16 路组相联）。'
})

const steps = computed(() => {
  // candidate 行集合：给定块号能放入哪些行
  const candidatesOf = block => {
    if (mode.value === 'direct') return [block % lineCount]
    if (mode.value === 'full') return lines.value.map(l => l.i)
    const set = block % setCount
    return lines.value.filter(l => Math.floor(l.i / waysPerSet) === set).map(l => l.i)
  }
  const tagOf = block => {
    if (mode.value === 'direct') return Math.floor(block / lineCount)
    if (mode.value === 'full') return block
    return Math.floor(block / setCount)
  }

  const cache = Array.from({ length: lineCount }, () => ({ valid: false, tag: -1, block: -1, stamp: 0 }))
  const out = []
  let clock = 0
  let hitsTotal = 0

  SEQ.forEach((block, idx) => {
    const cands = candidatesOf(block)
    const tag = tagOf(block)
    let hitIndex = -1
    for (const i of cands) {
      if (cache[i].valid && cache[i].tag === tag) { hitIndex = i; break }
    }
    let loadIndex = -1
    let evict = false
    let evictBlock = null
    if (hitIndex >= 0) {
      hitsTotal++
      clock++
      cache[hitIndex].stamp = clock
    } else {
      const empty = cands.find(i => !cache[i].valid)
      if (empty !== undefined) {
        loadIndex = empty
      } else {
        // 选牺牲行：LRU → stamp 最小；FIFO → 装入序最小
        let victim = cands[0]
        for (const i of cands) if (cache[i].stamp < cache[victim].stamp) victim = i
        loadIndex = victim
        evict = true
      }
      const oldBlock = cache[loadIndex].valid ? cache[loadIndex].block : null
      clock++
      cache[loadIndex] = { valid: true, tag, block, stamp: clock }
      evictBlock = oldBlock
    }
    const targetText = mode.value === 'direct'
      ? `行 ${block % lineCount}`
      : (mode.value === 'set' ? `组 ${block % setCount}（行 ${candidatesOf(block).join(' 或 ')}）` : '任意行')
    out.push({
      stepNo: idx + 1,
      block, hitIndex, loadIndex, evict, evictBlock, targetText,
      hits: hitsTotal,
      lines: cache.map(c => ({ ...c })),
      desc: hitIndex >= 0
        ? `第 ${idx + 1} 次访问块 ${block}：在行 ${hitIndex} 找到标记 ${tag} → 命中（累计命中率 ${((hitsTotal / (idx + 1)) * 100).toFixed(0)}%）`
        : `第 ${idx + 1} 次访问块 ${block}：${targetText} 内无匹配 → 缺失；` +
          (evict
            ? `按 ${policy.value.toUpperCase()} 选中行 ${loadIndex}，替换掉其中的块 ${evictBlock}`
            : `装入空闲行 ${loadIndex}`)
    })
  })
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || { block: SEQ[0], hitIndex: -1, loadIndex: -1, hits: 0, stepNo: 1, targetText: '', evict: false })
const statusText = computed(() => cur.value.desc)
</script>

<style scoped>
.cm-wrap { display: flex; gap: 18px; align-items: flex-start; flex-wrap: wrap; }
.cm-svg { background: #fcfdff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.cm-panel { flex: 1; min-width: 300px; }
.formula code { background: #f2f4f8; padding: 8px 10px; border-radius: 6px; display: block; font-size: 12px; line-height: 1.7; }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; gap: 8px; }
.tbl { font-size: 12px; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
.tbl-head { display: grid; grid-template-columns: 0.6fr 0.8fr 0.9fr 0.9fr; background: #f6f8fb; padding: 7px 10px; font-weight: 600; }
.tbl-row { display: grid; grid-template-columns: 0.6fr 0.8fr 0.9fr 0.9fr; padding: 6px 10px; border-top: 1px solid #f0f2f6; cursor: pointer; }
.tbl-row:hover { background: #f6f8fb; }
.tbl-row.active { background: var(--brand-light); color: var(--brand); font-weight: 600; }
.tip { margin-top: 10px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
