<template>
  <VisFrame title="死锁 · 资源分配图与银行家算法" desc="四个必要条件同时满足即可能死锁；银行家算法通过安全性检查避免进入不安全状态" :player="player" :status-text="statusText" back-to="/knowledge/17">
    <template #extra>
      <el-button size="small" plain @click="player.reset()">重播</el-button>
    </template>

    <el-row :gutter="16">
      <el-col :span="12">
        <div class="panel-title">资源分配图</div>
        <svg width="330" height="280" class="dl-svg">
          <!-- 边：分配边（资源→进程） -->
          <g v-for="(e, i) in assignEdges" :key="'a' + i">
            <line :x1="e.x1" :y1="e.y1" :x2="e.x2" :y2="e.y2" stroke="#22a06b" stroke-width="2" marker-end="url(#dl-green)" />
          </g>
          <!-- 边：请求边（进程→资源） -->
          <g v-for="(e, i) in requestEdges" :key="'r' + i">
            <line :x1="e.x1" :y1="e.y1" :x2="e.x2" :y2="e.y2" stroke="#e05252" stroke-width="2" marker-end="url(#dl-red)" />
          </g>
          <!-- 进程 -->
          <g v-for="p in processes" :key="p.name">
            <circle :cx="p.x" :cy="p.y" r="24" :fill="p.deadlocked ? '#fdeaea' : '#fff'" :stroke="p.deadlocked ? '#e05252' : '#3b6ef6'" stroke-width="2" />
            <text :x="p.x" :y="p.y + 5" text-anchor="middle" font-size="13" font-weight="600" :fill="p.deadlocked ? '#a32c2c' : '#1f2733'">{{ p.name }}</text>
          </g>
          <!-- 资源 -->
          <g v-for="r in resources" :key="r.name">
            <rect :x="r.x - 30" :y="r.y - 24" width="60" height="48" rx="4" fill="#fff" stroke="#8b95a3" stroke-width="2" />
            <text :x="r.x" :y="r.y - 30" text-anchor="middle" font-size="12" font-weight="600">{{ r.name }}</text>
            <circle v-for="(d, i) in r.units" :key="i" :cx="r.x - 12 + i * 24" :cy="r.y" r="6" fill="#c8d3e6" />
          </g>
          <defs>
            <marker id="dl-green" markerWidth="9" markerHeight="9" refX="8" refY="3" orient="auto">
              <path d="M0,0 L8,3 L0,6 z" fill="#22a06b" />
            </marker>
            <marker id="dl-red" markerWidth="9" markerHeight="9" refX="8" refY="3" orient="auto">
              <path d="M0,0 L8,3 L0,6 z" fill="#e05252" />
            </marker>
          </defs>
        </svg>
        <div class="graph-legend small">
          <span><i class="line" style="background:#22a06b"></i> 分配边（资源 → 进程，已占有）</span>
          <span><i class="line" style="background:#e05252"></i> 请求边（进程 → 资源，正在等待）</span>
        </div>
      </el-col>

      <el-col :span="12">
        <div class="panel-title">死锁产生的四个必要条件</div>
        <div class="cond-list">
          <div v-for="(c, i) in conditions" :key="i" class="cond-item" :class="{ active: c.active }">
            <el-icon><component :is="c.active ? 'CircleCheckFilled' : 'CircleCheck'" /></el-icon>
            <div>
              <b>{{ c.name }}</b>
              <div class="small muted">{{ c.desc }}</div>
            </div>
          </div>
        </div>
        <el-alert v-if="deadlocked" type="error" :closable="false" style="margin-top:10px" show-icon>
          <b>检测到死锁</b>：资源分配图中存在环路 P1 → R2 → P2 → R1 → P1，且每类资源只有一个实例 → 环路不可化简，死锁成立。
        </el-alert>
      </el-col>
    </el-row>

    <!-- 银行家算法 -->
    <div class="banker-area">
      <el-divider />
      <div class="panel-title">银行家算法 · 安全性检查（{{ bankerStepText }}）</div>
      <el-row :gutter="12">
        <el-col :span="8">
          <table class="btable">
            <thead><tr><th>进程</th><th>Max (A,B,C)</th><th>Allocation</th><th>Need</th></tr></thead>
            <tbody>
              <tr v-for="(p, i) in banker.procs" :key="p.name" :class="{ hl: i === highlightRow }">
                <td><b>{{ p.name }}</b></td>
                <td>{{ p.max.join(', ') }}</td>
                <td>{{ p.alloc.join(', ') }}</td>
                <td>{{ p.need.join(', ') }}</td>
              </tr>
            </tbody>
          </table>
        </el-col>
        <el-col :span="8">
          <div class="avail-box">
            <div class="small muted">可用资源向量 Available</div>
            <div class="avail-row">
              <span v-for="(a, i) in available" :key="i" class="avail-chip">{{ a }}</span>
            </div>
            <div class="small muted" style="margin-top:10px">安全序列</div>
            <div class="seq-row">
              <span v-for="(s, i) in safeSeq" :key="i" class="safe-chip">{{ s }}</span>
              <span v-if="!safeSeq.length" class="small muted">（尚未开始检查）</span>
            </div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="banker-note">
            <ul class="rules">
              <li>若存在一个<b>安全序列</b>使所有进程都能顺利完成，则系统处于安全状态</li>
              <li>银行家算法在<b>分配前试探</b>，若分配后仍安全才真正分配（死锁<b>避免</b>）</li>
              <li>与死锁预防不同：预防是破坏四个必要条件之一</li>
            </ul>
          </div>
        </el-col>
      </el-row>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#e05252"></i> 死锁进程</span>
      <span><i class="dot" style="background:#3b6ef6"></i> 正常进程</span>
      <span><i class="dot" style="background:#22a06b"></i> 满足的必要条件</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const processes = [
  { name: 'P1', x: 80, y: 80 },
  { name: 'P2', x: 80, y: 210 },
  { name: 'P3', x: 250, y: 145 }
]
const resources = [
  { name: 'R1', x: 250, y: 55, units: 1 },
  { name: 'R2', x: 250, y: 235, units: 1 }
]

/* 剧本：逐步构造资源分配图并检测死锁 */
const script = [
  {
    assign: [{ r: 0, p: 0 }], request: [], deadlocked: false, conds: 0,
    desc: '初始状态：系统中有进程 P1、P2 和资源 R1、R2，尚无分配关系'
  },
  {
    assign: [{ r: 0, p: 0 }], request: [], deadlocked: false, conds: 1,
    desc: 'P1 申请并获得 R1：产生一条分配边 R1 → P1（资源已分配给进程）'
  },
  {
    assign: [{ r: 0, p: 0 }, { r: 1, p: 1 }], request: [], deadlocked: false, conds: 2,
    desc: 'P2 申请并获得 R2：产生分配边 R2 → P2。此时资源互斥占有（条件1、2 满足）'
  },
  {
    assign: [{ r: 0, p: 0 }, { r: 1, p: 1 }], request: [{ p: 0, r: 1 }], deadlocked: false, conds: 3,
    desc: 'P1 已占有 R1，又请求 R2（请求和保持条件成立）→ 产生请求边 P1 → R2，P1 阻塞等待'
  },
  {
    assign: [{ r: 0, p: 0 }, { r: 1, p: 1 }], request: [{ p: 0, r: 1 }, { p: 1, r: 0 }], deadlocked: true, conds: 4,
    desc: 'P2 已占有 R2，又请求 R1 → 产生请求边 P2 → R1。图中形成环路 P1→R2→P2→R1→P1，四个条件全部满足 → 死锁！'
  },
  {
    // 「解除方案」沿用上一帧的 assign/request 会让这两步数据完全相同（画面不动）。
    // 标成 resolved：表示这一帧讲的是「如何打破死锁」，而不是死锁本身
    assign: [{ r: 0, p: 0 }, { r: 1, p: 1 }], request: [{ p: 0, r: 1 }, { p: 1, r: 0 }],
    deadlocked: true, conds: 4, resolved: true,
    desc: '死锁解除方案：① 撤销进程（回滚 P1 或 P2 释放资源）；② 剥夺资源；③ 预先用银行家算法避免进入该状态'
  }
]

const banker = {
  procs: [
    { name: 'P0', max: [7, 5, 3], alloc: [0, 1, 0] },
    { name: 'P1', max: [3, 2, 2], alloc: [2, 0, 0] },
    { name: 'P2', max: [9, 0, 2], alloc: [3, 0, 2] },
    { name: 'P3', max: [2, 2, 2], alloc: [2, 1, 1] },
    { name: 'P4', max: [4, 3, 3], alloc: [0, 0, 2] }
  ],
  total: [10, 5, 7]
}
// Need = Max − Allocation
banker.procs.forEach(p => { p.need = p.max.map((m, i) => m - p.alloc[i]) })

const steps = computed(() => {
  const out = script.map(s => ({ ...s, bankerStep: 0, safeSeq: [], highlightRow: -1 }))
  // 银行家算法安全检查步骤
  const allocSum = [0, 1, 0].map((_, i) => banker.procs.reduce((s, p) => s + p.alloc[i], 0))
  const available = banker.total.map((t, i) => t - allocSum[i])
  const need = banker.procs.map(p => p.max.map((m, i) => m - p.alloc[i]))
  const work = [...available]
  const finish = banker.procs.map(() => false)
  const seq = []
  const checkSteps = []
  checkSteps.push({ bankerStep: 1, safeSeq: [], highlightRow: -1, desc: `银行家算法：Available = Total − 已分配 = [${available.join(', ')}]，开始寻找安全序列` })
  let guard = 0
  while (seq.length < banker.procs.length && guard++ < 20) {
    let found = -1
    for (let i = 0; i < banker.procs.length; i++) {
      if (finish[i]) continue
      if (need[i].every((n, k) => n <= work[k])) { found = i; break }
    }
    if (found === -1) break
    finish[found] = true
    for (let k = 0; k < 3; k++) work[k] += banker.procs[found].alloc[k]
    seq.push(banker.procs[found].name)
    checkSteps.push({
      bankerStep: 2, safeSeq: [...seq], highlightRow: found,
      desc: `${banker.procs[found].name} 的 Need [${need[found].join(', ')}] ≤ Work [${work.map((w, k) => w - banker.procs[found].alloc[k]).join(', ')}] → 可完成，Work 变为 [${work.join(', ')}]`
    })
  }
  checkSteps.push({
    bankerStep: 3, safeSeq: [...seq], highlightRow: -1,
    desc: seq.length === banker.procs.length
      ? `存在安全序列 ⟨${seq.join(' → ')}⟩ → 系统处于安全状态，不会发生死锁`
      : `找不到完整安全序列 → 系统处于不安全状态，可能引发死锁`
  })
  return [...out, ...checkSteps]
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const deadlocked = computed(() => !!cur.value.deadlocked)

const assignEdges = computed(() =>
  (cur.value.assign || []).map(e => {
    const p = processes[e.p]
    const r = resources[e.r]
    return { x1: r.x, y1: r.y + 24, x2: p.x, y2: p.y }
  })
)
const requestEdges = computed(() =>
  (cur.value.request || []).map(e => {
    const p = processes[e.p]
    const r = resources[e.r]
    return { x1: p.x, y1: p.y, x2: r.x, y2: r.y - 24 }
  })
)

const conditions = computed(() => {
  const n = cur.value.conds || 0
  return [
    { name: '互斥条件', desc: '资源一次只能被一个进程占有', active: n >= 1 },
    { name: '不可剥夺条件', desc: '资源只能由占有者主动释放', active: n >= 2 },
    { name: '请求和保持条件', desc: '占有资源的同时又申请新资源', active: n >= 3 },
    { name: '循环等待条件', desc: '存在进程—资源的环形等待链', active: n >= 4 }
  ]
})

const available = computed(() => {
  const allocSum = [0, 0, 0].map((_, i) => banker.procs.reduce((s, p) => s + p.alloc[i], 0))
  return banker.total.map((t, i) => t - allocSum[i])
})
const safeSeq = computed(() => cur.value.safeSeq || [])
const highlightRow = computed(() => cur.value.highlightRow ?? -1)
const bankerStepText = computed(() => ({
  0: '待执行',
  1: '计算 Available 向量',
  2: '逐进程试探寻找安全序列',
  3: '检查结论'
}[cur.value.bankerStep || 0]))
</script>

<style scoped>
.panel-title { font-size: 13px; font-weight: 600; margin-bottom: 8px; color: var(--text-2); }
.dl-svg { background: #fbfcff; border-radius: 8px; display: block; }
.graph-legend { display: flex; flex-direction: column; gap: 4px; color: var(--text-2); margin-top: 6px; }
.line { display: inline-block; width: 16px; height: 3px; margin-right: 6px; vertical-align: middle; }
.cond-list { display: flex; flex-direction: column; gap: 8px; }
.cond-item {
  display: flex; gap: 8px; padding: 8px 10px; border-radius: 8px;
  border: 1px solid var(--border); background: #fff; color: var(--text-3);
}
.cond-item.active { border-color: var(--success); background: #f2fbf6; color: #176b48; }
.banker-area { margin-top: 10px; }
.btable { width: 100%; border-collapse: collapse; font-size: 12px; }
.btable th, .btable td { border: 1px solid var(--border); padding: 5px 6px; text-align: center; }
.btable th { background: #f7f9fc; }
.btable tr.hl { background: #dcf3e7; }
.avail-box { border: 1px solid var(--border); border-radius: 8px; padding: 10px; background: #fbfcff; }
.avail-row, .seq-row { display: flex; gap: 6px; margin-top: 6px; flex-wrap: wrap; }
.avail-chip, .safe-chip {
  min-width: 34px; height: 28px; line-height: 28px; text-align: center; border-radius: 4px;
  font-size: 12px; font-weight: 600; background: #eef3ff; border: 1px solid #cfe0ff; color: var(--brand);
}
.safe-chip { background: #dcf3e7; border-color: var(--success); color: #176b48; }
.banker-note { padding-left: 0; }
.rules { padding-left: 18px; margin: 0; }
.rules li { font-size: 12px; line-height: 1.9; color: var(--text-2); }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
