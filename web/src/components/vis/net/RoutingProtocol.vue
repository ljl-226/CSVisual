<template>
  <VisFrame
    :title="isRip ? '路由协议 · RIP 距离向量' : '路由协议 · OSPF 链路状态'"
    :desc="isRip ? '相邻路由器周期性交换整张路由表，只告诉邻居「我到某网络还有多少跳」' : '洪泛链路状态通告使全网 LSDB 一致，每台路由器再用 Dijkstra 独立算出最短路径树'"
    :player="player" :status-text="statusText" back-to="/knowledge/46"
  >
    <template #extra>
      <el-select v-model="proto" size="small" style="width:110px">
        <el-option value="rip" label="RIP" />
        <el-option value="ospf" label="OSPF" />
      </el-select>
      <el-select v-if="isRip" v-model="scene" size="small" style="width:150px">
        <el-option value="converge" label="正常收敛" />
        <el-option value="count" label="坏消息传得慢" />
        <el-option value="horizon" label="水平分割" />
      </el-select>
      <el-button size="small" plain @click="resetAll">重置</el-button>
    </template>

    <div class="rp-wrap">
      <svg width="620" height="330" class="rp-svg">
        <!-- 链路：RIP 每跳代价 1；OSPF 用接口代价 -->
        <g v-for="(l, i) in links" :key="'l' + i">
          <line :x1="POS[l.a].x" :y1="POS[l.a].y" :x2="POS[l.b].x" :y2="POS[l.b].y"
            :stroke="isHL(l) ? '#3b6ef6' : '#c8d3e6'" :stroke-width="isHL(l) ? 3.2 : 1.8" />
          <text :x="(POS[l.a].x + POS[l.b].x) / 2" :y="(POS[l.a].y + POS[l.b].y) / 2 - 6" text-anchor="middle"
            font-size="11" :fill="isHL(l) ? '#3b6ef6' : '#8b95a3'">{{ isRip ? '1 跳' : l.c }}</text>
        </g>
        <!-- 最短路径树边（OSPF 计算结果） -->
        <g v-for="(e, i) in treeEdges" :key="'e' + i">
          <line :x1="POS[e.a].x" :y1="POS[e.a].y" :x2="POS[e.b].x" :y2="POS[e.b].y" stroke="#22a06b" stroke-width="5" opacity="0.35" />
        </g>
        <g v-for="(p, i) in POS" :key="'n' + i">
          <circle :cx="p.x" :cy="p.y" r="26" :fill="cur.active === i ? '#eef3ff' : '#fff'"
            :stroke="cur.active === i ? '#3b6ef6' : '#c8d3e6'" stroke-width="2" />
          <text :x="p.x" :y="p.y + 5" text-anchor="middle" font-size="13" font-weight="700" fill="#1f2733">{{ NAMES[i] }}</text>
          <text v-if="!isRip" :x="p.x" :y="p.y + 42" text-anchor="middle" font-size="11" fill="#176b48">LSDB {{ cur.lsdb[i].length }}/4</text>
        </g>
        <text x="310" y="316" text-anchor="middle" font-size="11" fill="#8b95a3">
          {{ isRip ? 'RIP：跳数最大 15，16 即不可达；每 30 秒与相邻路由器交换一次整张路由表（UDP 520）' : 'OSPF：直接用 IP 数据报封装（协议号 89），只在链路状态变化时洪泛' }}
        </text>
      </svg>

      <div class="rp-panel">
        <div class="info-row"><span>当前协议</span><b style="color:var(--brand)">{{ isRip ? 'RIP 距离向量' : 'OSPF 链路状态' }}</b></div>
        <div v-if="isRip" class="info-row"><span>更新轮次</span><b>第 {{ cur.round }} 轮</b></div>
        <div v-if="isRip" class="info-row"><span>最近更新表项</span><b>{{ changeText }}</b></div>
        <div v-else class="info-row"><span>LSDB 条数 R1~R4</span><b>{{ cur.lsdb.map(v => v.length).join(' / ') }}</b></div>
        <div v-if="isRip" class="panel-title" style="margin-top:8px">距离向量表（行=源，列=目的网络，∞=16）</div>
        <table v-if="isRip" class="dv">
          <tr><th></th><th v-for="(n, i) in NAMES" :key="'h' + i">{{ n }}</th></tr>
          <tr v-for="(row, i) in cur.rip" :key="'r' + i">
            <th>{{ NAMES[i] }}</th>
            <td v-for="(v, j) in row" :key="'c' + j" :class="{ hl: hl && hl.r === i && hl.dst === j }">{{ fmt(v) }}</td>
          </tr>
        </table>
        <div v-else class="panel-title" style="margin-top:8px">Dijkstra 集合 S 与候选距离（源点 R1）</div>
        <table v-if="!isRip" class="dv">
          <tr><th>顶点</th><th>距离 D</th><th>前驱</th><th>状态</th></tr>
          <tr v-for="(d, i) in cur.dist" :key="'d' + i">
            <th>{{ NAMES[i] }}</th><td>{{ fmt(d) }}</td>
            <td>{{ cur.prev[i] >= 0 ? NAMES[cur.prev[i]] : '—' }}</td>
            <td :style="{ color: cur.done[i] ? '#22a06b' : 'inherit' }">{{ cur.done[i] ? '在 S 中' : '待选' }}</td>
          </tr>
        </table>
        <div class="panel-title" style="margin-top:8px">教材要点</div>
        <ul class="points">
          <li v-for="(p, i) in points" :key="i">{{ p }}</li>
        </ul>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> 本步正在交换 / 松弛的链路</span>
      <span><i class="dot" style="background:#22a06b"></i> 最短路径树上的边</span>
      <span><i class="dot" style="background:#e05252"></i> 表项被更新（高亮单元格 / LSDB 增长）</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const NAMES = ['R1', 'R2', 'R3', 'R4']
const POS = [{ x: 90, y: 150 }, { x: 300, y: 62 }, { x: 300, y: 250 }, { x: 510, y: 150 }]
const INF = 16        // RIP：跳数上限 15，16 表示不可达
const BIG = 99        // OSPF：Dijkstra 中的无穷大

// RIP 使用线型拓扑 R1—R2—R3—R4（每跳代价 1），便于演示坏消息传得慢；OSPF 使用带权拓扑
const RIP_LINKS = [{ a: 0, b: 1, c: 1 }, { a: 1, b: 2, c: 1 }, { a: 2, b: 3, c: 1 }]
const OSPF_LINKS = [{ a: 0, b: 1, c: 1 }, { a: 0, b: 2, c: 4 }, { a: 1, b: 2, c: 2 }, { a: 1, b: 3, c: 5 }, { a: 2, b: 3, c: 1 }]

const proto = ref('rip')
const scene = ref('count')
const isRip = computed(() => proto.value === 'rip')

function fmt(v) { return v >= INF ? '∞' : String(v) }

/* ---------- RIP：距离向量 + 坏消息传得慢 + 水平分割 ---------- */
function ripSteps(sc) {
  const split = sc === 'horizon'
  const out = []
  let links = RIP_LINKS.map(l => ({ ...l }))
  let d = NAMES.map(() => Array(4).fill(INF))
  let nh = NAMES.map(() => Array(4).fill(-1))  // 下一跳，-1 表示直连或尚无
  let round = 0
  let broken = false
  let hl = null
  for (let i = 0; i < 4; i++) d[i][i] = 0
  links.forEach(l => { d[l.a][l.b] = 1; d[l.b][l.a] = 1 })

  function snap(desc, extra = {}) {
    out.push({ kind: 'rip', active: -1, linksHL: [], round, broken, hl: hl ? { ...hl } : null, rip: d.map(r => [...r]), lsdb: [[], [], [], []], dist: [0, 0, 0, 0], prev: [-1, -1, -1, -1], done: [false, false, false, false], desc, ...extra })
  }
  // 一次通告：recv 收到 sender 的完整路由表后立即更新（触发式更新，异步生效）
  function advert(recv, sender) {
    const logs = []
    for (let dst = 0; dst < 4; dst++) {
      if (dst === sender) continue
      if (split && nh[sender][dst] === recv) continue     // 水平分割：不把从该邻居学来的路由再通告回去
      const cand = Math.min(INF, 1 + d[sender][dst])      // RIP 只算跳数，每经过一个路由器 +1
      const old = d[recv][dst]
      if (nh[recv][dst] === sender && cand !== old) {     // 沿当前下一跳更新，即使变差 —— 计数到无穷的根源
        d[recv][dst] = cand
        logs.push({ dst, old, v: cand })
      } else if (cand < old) {                            // 其它情况只接受更优的距离
        d[recv][dst] = cand
        nh[recv][dst] = sender
        logs.push({ dst, old, v: cand })
      }
    }
    return logs
  }
  // 跑一整轮：每条链路的两个方向各通告一次；silent=true 时不生成步骤（用于静默收敛）
  function runRound(silent) {
    let changed = false
    for (const l of links) {
      for (const [recv, sender] of [[l.b, l.a], [l.a, l.b]]) {
        const logs = advert(recv, sender)
        if (!logs.length) continue
        changed = true
        if (silent) continue
        const txt = logs.map(g => `${NAMES[recv]} 到 ${NAMES[g.dst]}：${fmt(g.old)} → ${fmt(g.v)}`).join('；')
        hl = { r: recv, dst: logs[0].dst, from: sender, old: logs[0].old, v: logs[0].v }
        const note = split ? '。水平分割禁止把从该邻居学来的路由再通告回去，虚假的好消息无法注入'
          : sc === 'count' ? '。双方互相把对方当成路径，距离被一轮轮放大（计数到无穷）' : ''
        snap(`${NAMES[sender]} 向 ${NAMES[recv]} 发出触发更新 —— ${txt}${note}`, { active: recv, linksHL: [[recv, sender]] })
      }
    }
    return changed
  }

  if (sc === 'converge') {
    snap('初始：每台路由器只知道与自己直接相连的网络（距离 1），其余全部记为不可达 ∞（16 跳）')
    while (round < 8) {
      round++
      hl = null
      snap(`第 ${round} 轮开始：相邻路由器按 30 秒定时器交换各自的完整路由表（RIP 报文封装在 UDP 520 端口）`)
      if (!runRound(false)) { snap('不再有任何表项变化 → 网络已收敛，RIP 距离向量算法结束'); break }
    }
    return out
  }

  // 故障场景：先静默收敛到稳态，再断开 R2—R3 之间的链路
  for (let k = 0; k < 8 && runRound(true); k++) { /* 静默收敛 */ }
  snap('稳态：R1—R2—R3—R4 线型拓扑上每台路由器都已知最短跳数与下一跳（此时 R2—R3 之间的链路突然断开）')
  links = links.filter(l => !(l.a === 1 && l.b === 2))
  d[1][2] = INF; d[2][1] = INF; nh[1][2] = -1; nh[2][1] = -1
  broken = true
  snap('故障瞬间：R2、R3 立即把相关表项改为 ∞，但这个「坏消息」要等下一次通告才能传给邻居', { linksHL: [[0, 1]] })

  let used = 0
  // R2—R3 断开后网络分成 {R1,R2} 与 {R3,R4} 两半，跨断点的 8 个表项必须全部到 ∞ 才算传完坏消息。
  // 只查一半（如仅 d[0][2]）会在另一侧还留着虚假路由时就收尾，终态表里出现
  // 「到 R3 不可达却到 R4 可达」这种自相矛盾的内容
  const allCrossInf = () => [[0, 2], [0, 3], [1, 2], [1, 3], [2, 0], [2, 1], [3, 0], [3, 1]]
    .every(([i, j]) => d[i][j] >= INF)
  let reached = false
  while (round < 20) {
    round++
    if (runRound(false)) used = round
    else if (round > 2) break
    if (allCrossInf()) { reached = true; break }
  }
  // 180 秒路由超时定时器：下一跳已不再是邻居的陈旧表项被删除（记为 ∞）
  const gone = []
  for (let i = 0; i < 4; i++) {
    const nbs = links.filter(l => l.a === i || l.b === i).map(l => (l.a === i ? l.b : l.a))
    for (let dst = 0; dst < 4; dst++) {
      if (d[i][dst] < INF && nh[i][dst] >= 0 && !nbs.includes(nh[i][dst])) {
        gone.push(`${NAMES[i]} 到 ${NAMES[dst]}`)
        d[i][dst] = INF
        nh[i][dst] = -1
      }
    }
  }
  if (gone.length) {
    snap(`180 秒路由超时定时器到期：${gone.join('、')} 的下一跳已不是邻居，表项被删除为 ∞（RIP 用定时器清理陈旧路由）`, { linksHL: [[0, 1]] })
    // 删掉陈旧路由后要一直通告到全网稳定为止；只补跑一轮会把未传完的坏消息留在终态表里
    while (round < 40 && runRound(false)) { if (allCrossInf()) break }
  }
  reached = reached || allCrossInf()
  hl = null
  snap(reached
    ? `距离终于增大到 16（∞）：全网确认对端不可达，坏消息传得慢的过程到此结束，共 ${used} 轮`
    : `不再有新的更新：${split ? '水平分割堵住了环路，虚假的间接路由无法回送' : '全网表项稳定'}，第 ${used} 轮即收敛`, { linksHL: [[0, 1]] })
  return out
}

/* ---------- OSPF：链路状态洪泛 + Dijkstra 最短路径 ---------- */
function ospfSteps() {
  const out = []
  const lsdb = NAMES.map((_, i) => [i])
  const links = OSPF_LINKS
  const dist = [0, BIG, BIG, BIG]
  const prev = [-1, -1, -1, -1]
  const done = [false, false, false, false]
  const empty = NAMES.map(() => Array(4).fill(0))
  let round = 0
  function snap(desc, extra = {}) {
    out.push({ kind: 'ospf', active: -1, linksHL: [], round, broken: false, hl: null, rip: empty, lsdb: lsdb.map(r => [...r]), dist: [...dist], prev: [...prev], done: [...done], desc, ...extra })
  }

  snap('初始：路由器通过 HELLO 报文发现邻居并测量代价（cost = 参考带宽 ÷ 接口带宽），据此生成自己的链路状态通告 LSA')
  let changed = true
  while (changed) {   // 洪泛：收到未知 LSA 就存入 LSDB 并向其余方向转发，直到全网数据库一致
    changed = false
    links.forEach(l => {
      [[l.a, l.b], [l.b, l.a]].forEach(([s, r]) => {
        lsdb[s].forEach(lsa => {
          if (!lsdb[r].includes(lsa)) {
            lsdb[r].push(lsa)
            changed = true
            snap(`${NAMES[r]} 收到 ${NAMES[s]} 洪泛的 LSA（源 ${NAMES[lsa]}）：加入链路状态数据库，并从其余接口继续转发出去`, { active: r, linksHL: [[s, r]] })
          }
        })
      })
    })
  }
  snap('洪泛结束：同一区域内所有路由器的链路状态数据库完全一致，于是形成了同一张带权拓扑图')
  round = 1
  for (let k = 0; k < 4; k++) {   // Dijkstra：以 R1 为根，每次选距离最小的顶点加入集合 S 并松弛其邻边
    let u = -1
    for (let i = 0; i < 4; i++) if (!done[i] && (u < 0 || dist[i] < dist[u])) u = i
    if (dist[u] >= BIG) break
    done[u] = true
    snap(`选出当前距离最小的顶点 ${NAMES[u]}（D = ${dist[u]}）加入集合 S：该顶点的最短路径已经最终确定`, { active: u })
    links.forEach(l => {
      const v = l.a === u ? l.b : (l.b === u ? l.a : -1)
      if (v < 0 || done[v]) return
      const nd = dist[u] + l.c
      if (nd < dist[v]) {
        const old = dist[v]
        dist[v] = nd
        prev[v] = u
        snap(`沿边 ${NAMES[u]}—${NAMES[v]}（代价 ${l.c}）松弛：D(${NAMES[v]}) 由 ${fmt(old)} 更新为 ${nd}，前驱记为 ${NAMES[u]}`, { active: u, linksHL: [[u, v]] })
      }
    })
  }
  const paths = []
  for (let i = 1; i < 4; i++) {
    const path = [NAMES[i]]
    for (let p = prev[i]; p >= 0; p = prev[p]) path.unshift(NAMES[p])
    paths.push(`${NAMES[0]}→${NAMES[i]}：${path.join('→')}，代价 ${dist[i]}`)
  }
  snap(`得到以 ${NAMES[0]} 为根的最短路径树：${paths.join('；')}。每台路由器都独立运行 Dijkstra 得到自己的路由表`, { active: 0 })
  return out
}

const steps = computed(() => (isRip.value ? ripSteps(scene.value) : ospfSteps()))

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)

const links = computed(() => {
  const base = isRip.value ? RIP_LINKS : OSPF_LINKS
  return base.filter(l => !(cur.value.broken && l.a === 1 && l.b === 2))
})
const hl = computed(() => cur.value.hl || null)
function isHL(l) {
  const s = cur.value.linksHL || []
  return s.some(([a, b]) => (a === l.a && b === l.b) || (a === l.b && b === l.a))
}
// OSPF 最短路径树边：由前驱数组还原
const treeEdges = computed(() => {
  if (isRip.value) return []
  return (cur.value.prev || []).map((p, i) => (p >= 0 ? { a: p, b: i } : null)).filter(Boolean)
})

const changeText = computed(() => {
  const h = cur.value.hl
  return h ? `${NAMES[h.r]} → ${NAMES[h.dst]}：${fmt(h.old)} ⇒ ${fmt(h.v)}（经 ${NAMES[h.from]}）` : '—'
})
const points = computed(() => (isRip.value ? [
  '距离向量算法：每个路由器只维护「距离 + 下一跳」，靠邻居通告迭代更新',
  '坏消息传得慢：好消息传播快，坏消息要逐轮增大到 16 才被判定为不可达',
  '水平分割（split horizon）：不向某条路由的学习来源再通告它，可显著加快故障收敛',
  'RIP 最大跳数 15、每 30 秒广播一次，适用于小型自治系统'
] : [
  '链路状态：洪泛自己的邻接关系，全网 LSDB 一致后各自独立计算，收敛快',
  'OSPF 只在链路状态变化时触发更新（可靠洪泛 + 确认），支持区域划分与等价多路径',
  'Dijkstra 每次把距离最小的顶点加入集合 S，并对它的邻边做松弛',
  'OSPF 报文直接用 IP 数据报传输（协议号 89），支持 CIDR 与认证'
]))

function resetAll() {
  proto.value = 'rip'
  scene.value = 'count'
  player.reset()
}
</script>

<style scoped>
.rp-wrap { display: flex; gap: 24px; align-items: flex-start; flex-wrap: wrap; }
.rp-svg { background: #fbfcff; border-radius: 8px; flex-shrink: 0; }
.rp-panel { flex: 1; min-width: 280px; }
.panel-title { font-size: 13px; font-weight: 600; color: var(--text-2); }
.info-row { display: flex; justify-content: space-between; gap: 10px; padding: 4px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.dv { width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 6px; }
.dv th, .dv td { border: 1px solid var(--border); padding: 3px 6px; text-align: center; }
.dv th { background: #f7f8fb; color: var(--text-2); font-weight: 600; }
.dv td.hl { background: #fdeaea; color: #a32c2c; font-weight: 700; }
.points { padding-left: 18px; margin: 6px 0 0; }
.points li { font-size: 12px; line-height: 1.85; color: var(--text-2); }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
