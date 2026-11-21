<template>
  <VisFrame title="银行家算法 · 资源分配与安全性检查" desc="分配前先试探：Request ≤ Need 且 ≤ Available 才试分配，再用 Work/Finish 找安全序列；找不到则回滚拒绝，使系统永不进入不安全状态" :player="player" :status-text="statusText" back-to="/knowledge/48">
    <template #extra>
      <el-select v-model="reqProc" size="small" style="width:90px" @change="player.reset()">
        <el-option v-for="(p, i) in PROCS" :key="p.name" :value="i" :label="p.name" />
      </el-select>
      <el-input v-model="reqText" size="small" style="width:120px" placeholder="请求向量 A,B,C" />
      <el-button size="small" @click="applyReq">应用</el-button>
      <el-button size="small" plain @click="resetAll">重置</el-button>
    </template>
    <div class="bk-wrap">
      <svg :width="W" :height="H" class="bk-svg">
        <!-- ① 资源总量 / 已分配 / 可用 堆叠条 -->
        <text x="12" y="16" font-size="12" font-weight="700" fill="#1f2733">三类资源 R(A,B,C) 的分配情况</text>
        <g v-for="(nm, i) in RNAME" :key="nm">
          <text x="12" :y="47 + i * 32" font-size="12" font-weight="600" fill="#1f2733">{{ nm }}</text>
          <rect x="36" :y="32 + i * 32" width="240" height="22" rx="3" fill="#f2f4f8" stroke="#dfe4ec" />
          <rect x="36" :y="32 + i * 32" :width="240 * used[i] / TOTAL[i]" height="22" rx="3" fill="#3b6ef6" />
          <rect v-if="cur.probe" :x="36 + 240 * (used[i] - req[i]) / TOTAL[i]" :y="32 + i * 32" :width="240 * Math.min(req[i], TOTAL[i] - (used[i] - req[i])) / TOTAL[i]" height="22" fill="#e8a13a" opacity="0.85" />
          <text x="288" :y="47 + i * 32" font-size="10.5" fill="#8b95a3">已分配 {{ used[i] }} / 总量 {{ TOTAL[i] }}，剩余 {{ cur.avail[i] }}</text>
        </g>

        <!-- ② 安全序列（独占一行，不再与资源条的文字抢横向空间） -->
        <text x="12" y="140" font-size="12" font-weight="700" fill="#1f2733">安全序列（Work / Finish 检查）</text>
        <g v-for="(p, i) in PROCS" :key="p.name">
          <circle :cx="32 + i * 68" cy="178" r="19" :fill="seqHas(i) ? '#dcf3e7' : (cur.checkIdx === i ? '#eef3ff' : '#fff')" :stroke="seqHas(i) ? '#22a06b' : (cur.checkIdx === i ? '#3b6ef6' : '#c8d3e6')" stroke-width="2" />
          <text :x="32 + i * 68" y="183" text-anchor="middle" font-size="12" font-weight="700" fill="#1f2733">{{ p.name }}</text>
          <text :x="32 + i * 68" y="214" text-anchor="middle" font-size="10" :fill="seqHas(i) ? '#176b48' : '#b6bfcc'">{{ cur.finish && cur.finish[i] ? 'Finish=T' : 'Finish=F' }}</text>
          <line v-if="i < 4" :x1="51 + i * 68" y1="178" :x2="81 + i * 68" y2="178" stroke="#c8d3e6" stroke-width="1.5" marker-end="url(#bk-arrow)" />
        </g>

        <!-- ③ Work 向量 + 结论 -->
        <text x="12" y="240" font-size="11" fill="#8b95a3">当前 Work 向量（试探分配后的可用资源）</text>
        <g v-for="(v, i) in cur.work" :key="'w' + i">
          <rect :x="12 + i * 46" y="246" width="38" height="26" rx="4" fill="#eef3ff" stroke="#cfe0ff" />
          <text :x="31 + i * 46" y="264" text-anchor="middle" font-size="13" font-weight="700" fill="#3b6ef6">{{ v }}</text>
        </g>
        <text x="176" y="264" font-size="12" :fill="verdictColor" font-weight="700">{{ verdictText }}</text>
        <defs><marker id="bk-arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 z" fill="#c8d3e6" /></marker></defs>
      </svg>
      <div class="bk-panel">
        <table class="bk-table">
          <thead><tr><th>进程</th><th>Max</th><th>Allocation</th><th>Need</th><th>Finish</th></tr></thead>
          <tbody>
            <tr v-for="(p, i) in PROCS" :key="p.name" :class="{ hl: cur.checkIdx === i, done: seqHas(i) }">
              <td><b>{{ p.name }}</b></td>
              <td>{{ max[i].join(' , ') }}</td>
              <td>{{ cur.alloc[i].join(' , ') }}</td>
              <td>{{ cur.need[i].join(' , ') }}</td>
              <td>{{ cur.finish && cur.finish[i] ? 'T' : 'F' }}</td>
            </tr>
          </tbody>
          <tfoot><tr><td><b>Available</b></td><td colspan="3">{{ cur.avail.join(' , ') }}　（试探分配前为 {{ baseAvail.join(' , ')}}）</td><td>—</td></tr></tfoot>
        </table>
        <div class="seq-row">
          <span class="small muted">安全序列：</span>
          <span v-for="(s, i) in cur.seq" :key="i" class="seq-chip">{{ PROCS[s].name }}</span>
          <span v-if="!cur.seq.length" class="small muted">（未找到）</span>
        </div>
        <p class="tip small muted">
          考点：Need = Max − Allocation；Available = 资源总量 − 已分配总量。银行家算法是<b>死锁避免</b>：
          每次分配前试探，只有"分配后仍存在安全序列"才真正分配，否则让进程等待。
        </p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> 已分配资源</span>
      <span><i class="dot" style="background:#e8a13a"></i> 本次试探分配量 Request</span>
      <span><i class="dot" style="background:#22a06b"></i> 已加入安全序列（Finish = T）</span>
      <span><i class="dot" style="background:#e05252"></i> 不安全 / 拒绝分配</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const W = 660
const H = 286
const RNAME = ['A', 'B', 'C']
const TOTAL = [10, 5, 7]
// 教材经典实例（汤小丹《计算机操作系统》）：t0 时刻的资源分配表
const PROCS = [
  { name: 'P0', max: [7, 5, 3], alloc: [0, 1, 0] }, { name: 'P1', max: [3, 2, 2], alloc: [2, 0, 0] },
  { name: 'P2', max: [9, 0, 2], alloc: [3, 0, 2] }, { name: 'P3', max: [2, 2, 2], alloc: [2, 1, 1] }, { name: 'P4', max: [4, 3, 3], alloc: [0, 0, 2] }]
const max = PROCS.map(p => [...p.max])
const reqProc = ref(1)
const reqText = ref('1,0,2')
const req = ref([1, 0, 2])
// 已分配总量 与 初始可用向量 Available = Total − Σ Allocation
const used = TOTAL.map((t, i) => PROCS.reduce((s, p) => s + p.alloc[i], 0))
const baseAvail = computed(() => TOTAL.map((t, i) => t - PROCS.reduce((s, p) => s + p.alloc[i], 0)))

const steps = computed(() => {
  const out = []
  const alloc = PROCS.map(p => [...p.alloc])
  const need = PROCS.map((p, i) => p.max.map((v, k) => v - alloc[i][k]))
  let avail = baseAvail.value.slice()
  let work = [...avail]
  let finish = PROCS.map(() => false)
  let seq = []
  let probe = false
  const i = reqProc.value
  const R = req.value.map((v, k) => Math.max(0, Math.min(v, TOTAL[k])))
  function snap(desc, extra = {}) {
    out.push({ alloc: alloc.map(a => [...a]), need: need.map(n => [...n]), avail: [...avail], work: [...work], finish: [...finish], seq: [...seq], probe, checkIdx: -1, verdict: 'none', ...extra, desc })
  }
  snap(`t0 时刻：Need = Max − Allocation，Available = Total − 已分配 = [${avail.join(', ')}]。${PROCS[i].name} 提出请求 Request[${i}] = [${R.join(', ')}]`)
  // ① 请求量不得超过它声明的最大需求
  const overNeed = R.some((v, k) => v > need[i][k])
  snap(overNeed
    ? `检查① Request ≤ Need：Request [${R.join(', ')}] > Need [${need[i].join(', ')}] → 超过进程声明的最大需求，属非法请求，系统直接拒绝`
    : `检查① Request ≤ Need：Request [${R.join(', ')}] ≤ Need [${need[i].join(', ')}] → 合法，继续检查可用资源`,
    // check 标明当前在核对哪一项：两步检查的数据完全相同，
    // 没有它画面会连续两步没有变化。
    { checkIdx: i, check: 'need', verdict: overNeed ? 'reject-need' : 'none' })
  if (overNeed) return out
  // ② 请求量不得超过当前可用资源
  const overAvail = R.some((v, k) => v > avail[k])
  snap(overAvail
    ? `检查② Request ≤ Available：[${R.join(', ')}] > [${avail.join(', ')}] → 资源不足，${PROCS[i].name} 必须等待`
    : `检查② Request ≤ Available：[${R.join(', ')}] ≤ [${avail.join(', ')}] → 资源充足，可以试探分配`,
    { checkIdx: i, check: 'avail', verdict: overAvail ? 'wait' : 'none' })
  if (overAvail) return out
  // ③ 试探分配：并不真正写入，仅用于安全性判断
  probe = true
  for (let k = 0; k < 3; k++) { alloc[i][k] += R[k]; need[i][k] -= R[k]; avail[k] -= R[k] }
  work = [...avail]
  snap(`③ 试探分配：Allocation[${i}] += Request → [${alloc[i].join(', ')}]，Need[${i}] → [${need[i].join(', ')}]，Available → [${avail.join(', ')}]`, { checkIdx: i })
  // ④ 安全性算法：找 Need[i] ≤ Work 且未完成的进程，回收其资源
  let guard = 0
  while (seq.length < PROCS.length && guard++ < 30) {
    let found = -1
    for (let j = 0; j < PROCS.length; j++) if (!finish[j] && need[j].every((n, k) => n <= work[k])) { found = j; break }
    if (found === -1) break
    const before = [...work]
    finish[found] = true
    for (let k = 0; k < 3; k++) work[k] += alloc[found][k]
    seq.push(found)
    snap(`${PROCS[found].name}：Need [${need[found].join(', ')}] ≤ Work [${before.join(', ')}] → 可顺利完成并归还 [${alloc[found].join(', ')}]，Work 变为 [${work.join(', ')}]，加入安全序列`, { checkIdx: found })
  }
  // ⑤ 结论：安全则正式分配，不安全则回滚
  if (seq.length === PROCS.length) {
    snap(`⑤ 存在安全序列 ⟨${seq.map(s => PROCS[s].name).join(' → ')}⟩ → 系统仍处于安全状态，正式把资源分配给 ${PROCS[i].name}`, { verdict: 'safe' })
  } else {
    for (let k = 0; k < 3; k++) { alloc[i][k] -= R[k]; need[i][k] += R[k]; avail[k] += R[k] }
    probe = false
    snap(`⑤ 找不到完整安全序列（剩 ${PROCS.length - seq.length} 个进程无法满足）→ 分配后系统将进入不安全状态，回滚试探分配，${PROCS[i].name} 等待`, { verdict: 'unsafe', seq: [] })
  }
  return out
})
const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const seqHas = i => (cur.value.seq || []).includes(i)
const verdictText = computed(() => ({
  none: '尚未得出结论',
  safe: '安全 → 批准本次分配',
  unsafe: '不安全 → 拒绝分配并回滚',
  wait: '可用资源不足 → 进程等待',
  'reject-need': '请求超过最大需求 → 非法请求，拒绝'
}[cur.value.verdict] || ''))
const verdictColor = computed(() => (cur.value.verdict === 'safe' ? '#22a06b' : (cur.value.verdict === 'none' ? '#8b95a3' : '#e05252')))
// 解析请求向量，非法输入兜底为 0
function applyReq() {
  const parts = reqText.value.split(/[,，\s]+/).filter(Boolean).map(v => Number(v))
  req.value = [0, 1, 2].map(k => {
    const n = parts[k]
    return Number.isFinite(n) && n >= 0 ? Math.min(Math.floor(n), TOTAL[k]) : 0
  })
  reqText.value = req.value.join(',')
  player.reset()
}
function resetAll() { reqProc.value = 1; reqText.value = '1,0,2'; req.value = [1, 0, 2]; player.reset() }
</script>

<style scoped>
.bk-wrap { display: flex; gap: 18px; align-items: flex-start; flex-wrap: wrap; }
.bk-svg { background: #fbfcff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.bk-panel { flex: 1; min-width: 320px; }
.bk-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.bk-table th, .bk-table td { border: 1px solid var(--border); padding: 5px 6px; text-align: center; }
.bk-table th { background: #f7f9fc; }
.bk-table tr.hl { background: #eef3ff; }
.bk-table tr.done { background: #dcf3e7; }
.bk-table tfoot td { background: #f7f9fc; text-align: left; }
.seq-row { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; margin-top: 10px; }
.seq-chip { background: #dcf3e7; border: 1px solid var(--success); color: #176b48; border-radius: 4px; padding: 2px 9px; font-size: 12px; font-weight: 600; }
.tip { margin-top: 10px; line-height: 1.8; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
