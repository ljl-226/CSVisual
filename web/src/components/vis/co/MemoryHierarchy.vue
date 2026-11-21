<template>
  <VisFrame title="存储器层次结构与 Cache 命中" desc="依靠程序局部性原理，用少量高速 Cache 覆盖大部分访问；直接映射：块号 = 主存块号 mod Cache 块数" :player="player" :status-text="statusText" back-to="/knowledge/19">
    <template #extra>
      <el-input v-model="seqText" size="small" style="width:180px" placeholder="访问的主存块号" @change="player.reset()" />
      <span class="small muted">Cache 命中时间 10ns / 主存 100ns</span>
      <el-button size="small" plain @click="player.reset()">重播</el-button>
    </template>

    <el-row :gutter="16">
      <el-col :span="10">
        <div class="panel-title">存储层次金字塔</div>
        <div class="pyramid">
          <div v-for="(l, i) in levels" :key="i" class="pyr-row" :class="{ active: activeLevel === i }">
            <div class="pyr-name">{{ l.name }}</div>
            <div class="pyr-meta small">{{ l.speed }} · {{ l.cap }}</div>
            <div class="pyr-cost small muted">{{ l.cost }}</div>
          </div>
        </div>
        <div class="tip small muted" style="margin-top:8px">
          越靠近 CPU：速度越快、容量越小、每位成本越高。层次结构靠<b>时间局部性</b>与<b>空间局部性</b>工作。
        </div>
      </el-col>

      <el-col :span="14">
        <div class="panel-title">Cache 状态（共 {{ cacheLines }} 块，直接映射）</div>
        <table class="ctable">
          <thead><tr><th>块号</th><th>有效位 V</th><th>标记 Tag</th><th>数据块</th><th>状态</th></tr></thead>
          <tbody>
            <tr v-for="(line, i) in cache" :key="i" :class="{ hitrow: hitIndex === i, missrow: missIndex === i }">
              <td>{{ i }}</td>
              <td>{{ line.valid ? 1 : 0 }}</td>
              <td>{{ line.valid ? line.tag : '—' }}</td>
              <td>{{ line.valid ? '块 ' + line.block : '—' }}</td>
              <td>
                <el-tag v-if="hitIndex === i" size="small" type="success" effect="dark">命中</el-tag>
                <el-tag v-else-if="missIndex === i" size="small" type="danger" effect="dark">调入</el-tag>
              </td>
            </tr>
          </tbody>
        </table>

        <div class="access-row">
          <span class="small muted">访问序列：</span>
          <span v-for="(a, i) in sequence" :key="i" class="acc-cell" :class="{ cur: i === curIndex, passed: i < curIndex }">{{ a }}</span>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:14px">
      <el-col :span="12">
        <div class="stat-row">
          <div class="stat-box"><div class="sv small-sv">{{ hits }}</div><div class="sl">命中次数</div></div>
          <div class="stat-box"><div class="sv small-sv">{{ misses }}</div><div class="sl">未命中次数</div></div>
          <div class="stat-box"><div class="sv small-sv">{{ hitRate }}%</div><div class="sl">命中率 H</div></div>
          <div class="stat-box"><div class="sv small-sv">{{ avgTime }} ns</div><div class="sl">平均访问时间</div></div>
        </div>
        <div class="formula-box">
          <code>T = H × Tc + (1 − H) × Tm = {{ (hits) }}/{{ total }} × 10 + {{ misses }}/{{ total }} × 100 = {{ avgTime }} ns</code>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="panel-title">要点</div>
        <ul class="rules">
          <li><b>时间局部性</b>：刚被访问的单元很可能再次被访问 → Cache 保留近期访问的内容</li>
          <li><b>空间局部性</b>：邻近单元很可能被访问 → 以块（行）为单位调入</li>
          <li><b>命中</b>：CPU 直接在 Cache 取到，耗时 Tc；<b>未命中</b>：需访问主存并调入整块</li>
          <li>命中率与 Cache 容量、块大小、映射方式（直接/全相联/组相联）相关</li>
        </ul>
      </el-col>
    </el-row>

    <template #legend>
      <span><i class="dot" style="background:#22a06b"></i> Cache 命中</span>
      <span><i class="dot" style="background:#e05252"></i> 未命中（访问主存）</span>
      <span><i class="dot" style="background:#3b6ef6"></i> 当前访问</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const cacheLines = 4
const Tc = 10
const Tm = 100
const seqText = ref('1,5,1,9,2,5,1,13,2,5,1,9')
const sequence = computed(() =>
  seqText.value.split(/[,，\s]+/).map(v => Number(v.trim())).filter(v => !isNaN(v))
)

const levels = [
  { name: '寄存器', speed: '<1ns', cap: '几十~几百 B', cost: '成本最高' },
  { name: 'L1 Cache (SRAM)', speed: '~1ns', cap: '几十 KB', cost: '成本高' },
  { name: 'L2/L3 Cache', speed: '几 ns', cap: 'MB 级', cost: '成本中' },
  { name: '主存 (DRAM)', speed: '~100ns', cap: 'GB 级', cost: '成本较低' },
  { name: '辅存（磁盘/SSD）', speed: 'ms 级', cap: 'TB 级', cost: '成本最低' }
]

const steps = computed(() => {
  const cache = Array.from({ length: cacheLines }, () => ({ valid: false, tag: null, block: null }))
  let hits = 0
  let misses = 0
  const out = []
  out.push({
    cache: cache.map(c => ({ ...c })), hits, misses, index: -1, hitIndex: -1, missIndex: -1, level: 1,
    desc: 'Cache 初始为空，所有有效位 V = 0'
  })
  sequence.value.forEach((block, i) => {
    const idx = block % cacheLines
    const tag = Math.floor(block / cacheLines)
    // 查 Cache
    out.push({
      cache: cache.map(c => ({ ...c })), hits, misses, index: i, hitIndex: -1, missIndex: -1, level: 1,
      desc: `CPU 访问主存块 ${block}：块号 = ${block} mod ${cacheLines} = ${idx}，标记 tag = ${tag}，查 Cache`
    })
    const line = cache[idx]
    if (line.valid && line.tag === tag) {
      hits++
      out.push({
        cache: cache.map(c => ({ ...c })), hits, misses, index: i, hitIndex: idx, missIndex: -1, level: 1,
        desc: `Cache 命中！第 ${idx} 块有效位为 1 且 tag 匹配 → 直接读取，耗时 ${Tc}ns`
      })
    } else {
      misses++
      line.valid = true
      line.tag = tag
      line.block = block
      out.push({
        cache: cache.map(c => ({ ...c })), hits, misses, index: i, hitIndex: -1, missIndex: idx, level: 3,
        desc: `Cache 未命中 → 访问主存（耗时 ${Tm}ns），将块 ${block} 调入 Cache 第 ${idx} 行`
      })
      out.push({
        cache: cache.map(c => ({ ...c })), hits, misses, index: i, hitIndex: -1, missIndex: idx, level: 1,
        desc: `调入完成，数据同时送 CPU；当前命中率 H = ${hits}/${hits + misses}`
      })
    }
  })
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const cache = computed(() => cur.value.cache || [])
const hitIndex = computed(() => cur.value.hitIndex ?? -1)
const missIndex = computed(() => cur.value.missIndex ?? -1)
const curIndex = computed(() => cur.value.index ?? -1)
const activeLevel = computed(() => cur.value.level ?? -1)
const hits = computed(() => cur.value.hits || 0)
const misses = computed(() => cur.value.misses || 0)
const total = computed(() => hits.value + misses.value)
const hitRate = computed(() => (total.value ? Math.round((hits.value / total.value) * 100) : 0))
const avgTime = computed(() =>
  total.value ? ((hits.value / total.value) * Tc + (misses.value / total.value) * Tm).toFixed(1) : '0.0'
)
</script>

<style scoped>
.panel-title { font-size: 13px; font-weight: 600; margin-bottom: 8px; color: var(--text-2); }
.pyramid { display: flex; flex-direction: column; gap: 5px; }
.pyr-row {
  border: 1.5px solid var(--border); border-radius: 8px; padding: 8px 12px; background: #fff;
  text-align: center; transition: all .25s;
}
.pyr-row.active { border-color: var(--brand); background: var(--brand-light); }
.pyr-name { font-weight: 600; font-size: 13px; }
.pyr-meta { color: var(--text-2); }
.pyr-cost { font-size: 11px; }
.ctable { width: 100%; border-collapse: collapse; font-size: 12px; }
.ctable th, .ctable td { border: 1px solid var(--border); padding: 5px 8px; text-align: center; }
.ctable th { background: #f7f9fc; }
.ctable tr.hitrow { background: #dcf3e7; }
.ctable tr.missrow { background: #fdeaea; }
.access-row { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; margin-top: 12px; }
.acc-cell {
  width: 26px; height: 26px; line-height: 26px; text-align: center; border-radius: 4px;
  border: 1px solid var(--border); font-size: 12px; color: var(--text-3);
}
.acc-cell.passed { background: #f0f2f6; }
.acc-cell.cur { background: var(--brand); color: #fff; border-color: var(--brand); font-weight: 700; }
.stat-row { display: flex; gap: 10px; flex-wrap: wrap; }
.stat-box { flex: 1; min-width: 90px; background: #fbfcff; border: 1px solid var(--border); border-radius: 8px; padding: 8px; text-align: center; }
.sv { font-size: 18px; font-weight: 700; color: var(--brand); }
.sl { font-size: 11px; color: var(--text-2); margin-top: 2px; }
.formula-box { margin-top: 10px; }
.formula-box code { display: block; background: #f2f4f8; padding: 6px 10px; border-radius: 6px; font-size: 12px; }
.rules { padding-left: 18px; margin: 0; }
.rules li { font-size: 12px; line-height: 1.9; color: var(--text-2); }
.tip { line-height: 1.8; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
