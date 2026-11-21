/**
 * 可视化动画正确性监测
 *
 * 与 ssr-check.mjs 的分工：
 *   ssr-check  -> 只保证「渲染不崩」（编译通过 ≠ 运行不崩）
 *   本脚本     -> 保证「动画算得对」
 *
 * 原理：所有可视化组件共用 usePlayer 的「预计算步骤数组」架构，
 * 动画的每一步都是一份数据快照。因此正确性 = 步骤数组的正确性，
 * 可以脱离浏览器、脱离 DOM 直接在 Node 里校验。
 *
 * 用法：
 *   node scripts/vis-check.mjs              全部组件，输出体检报告
 *   node scripts/vis-check.mjs --json       输出机器可读结果
 *   node scripts/vis-check.mjs <组件名>     只看某一个
 */
import { createServer } from 'vite'
import { createSSRApp, h } from 'vue'
import { renderToString } from '@vue/server-renderer'
import ElementPlus from 'element-plus'
import * as ElIcons from '@element-plus/icons-vue'
import fs from 'node:fs'
import path from 'node:path'

const quiet = !process.argv.includes('--verbose')
if (quiet) { console.error = () => {}; console.warn = () => {} }

const root = path.resolve(process.cwd())
const visDir = path.join(root, 'src/components/vis')

function collect(dir, base = 'vis') {
  const out = []
  for (const name of fs.readdirSync(dir)) {
    const full = path.join(dir, name)
    if (fs.statSync(full).isDirectory()) out.push(...collect(full, base + '/' + name))
    else if (name.endsWith('.vue')) out.push(base + '/' + name)
  }
  return out.sort()
}

const only = process.argv.slice(2).find(a => !a.startsWith('--'))
const targets = collect(visDir)
  .filter(p => !p.endsWith('VisFrame.vue'))
  .filter(p => !only || p.toLowerCase().includes(only.toLowerCase()))

/* ------------------------------------------------------------------ */
/* 通用体检：不依赖任何算法语义，只检查「数据是否健全」                  */
/* ------------------------------------------------------------------ */

const NUMERIC_KEY_HINT = /^(x|y|r|t|val|value|idx|index|pos|len|n|count|score|dist|cost|sum|avg|prob|p|det|angle|speed|time|step|k|i|j|w|h|size|num|total|ratio|rate|temp|depth|level|freq|mean|var|sd)$/

/**
 * 递归扫描快照里的坏数值。
 * 区分两类：
 *   - 真错：NaN / Infinity / undefined —— 界面上会显示成 "NaN" 或空白
 *   - 提示：null —— 多数是语义上的「空」（空槽、无事件、无当前节点），不算错
 */
function scanBadNumbers(node, pathStr, out, depth = 0) {
  if (depth > 6) return
  if (node === undefined) { out.push({ path: pathStr, kind: 'undefined' }); return }
  if (node === null) { out.push({ path: pathStr, kind: 'null' }); return }
  if (typeof node === 'number') {
    if (Number.isNaN(node)) out.push({ path: pathStr, kind: 'NaN' })
    else if (!Number.isFinite(node)) out.push({ path: pathStr, kind: 'Infinity' })
    return
  }
  if (Array.isArray(node)) {
    if (node.length > 200) return  // 超长数组（采样点）不做逐项扫描
    node.forEach((v, i) => scanBadNumbers(v, `${pathStr}[${i}]`, out, depth + 1))
    return
  }
  if (typeof node === 'object') {
    for (const [k, v] of Object.entries(node)) scanBadNumbers(v, pathStr ? `${pathStr}.${k}` : k, out, depth + 1)
  }
}

// undefined / NaN 一定会在界面上露出空白或 "NaN"，是硬错误。
// Infinity 多半是合法语义（最短路「不可达」、除零极限），显示层通常已转成 ∞，
// 因此只作提示，不判失败 —— 否则会淹没真正的问题。
const FATAL_KINDS = new Set(['NaN', 'undefined'])
const WARN_KINDS = new Set(['Infinity'])

/** 检查每一步是否携带可读的说明文案 */
function findDescKey(step) {
  for (const k of ['desc', 'text', 'label', 'msg', 'message', 'tip', 'status', 'note', 'title']) {
    if (typeof step[k] === 'string' && step[k].trim()) return k
  }
  return null
}

function checkComponent(rel, steps) {
  const issues = []
  if (!Array.isArray(steps)) return [{ code: 'NO_STEPS', msg: '未取到步骤数组' }]
  if (steps.length === 0) issues.push({ code: 'EMPTY', msg: '步骤数组为空' })
  if (steps.length === 1) issues.push({ code: 'SINGLE', msg: '只有 1 步，动画无法演示过程' })

  const descKeys = new Set()
  let badCount = 0
  const badSamples = []
  let infCount = 0
  const infSamples = []
  steps.forEach((s, i) => {
    if (s === null || s === undefined) { issues.push({ code: 'NULL_STEP', msg: `第 ${i} 步是 ${s}` }); return }
    if (typeof s !== 'object') { issues.push({ code: 'NON_OBJ_STEP', msg: `第 ${i} 步不是对象：${typeof s}` }); return }
    const dk = findDescKey(s)
    if (!dk) issues.push({ code: 'NO_DESC', msg: `第 ${i} 步没有说明文案` })
    else descKeys.add(dk)
    const bad = []
    scanBadNumbers(s, '', bad)
    const fatal = bad.filter(b => FATAL_KINDS.has(b.kind))
    const warn = bad.filter(b => WARN_KINDS.has(b.kind))
    if (fatal.length) {
      badCount += fatal.length
      if (badSamples.length < 3) badSamples.push({ step: i, items: fatal.slice(0, 4) })
    }
    if (warn.length) {
      infCount += warn.length
      if (infSamples.length < 2) infSamples.push({ step: i, items: warn.slice(0, 3) })
    }
  })
  if (badCount) issues.push({ code: 'BAD_NUM', level: 'error', msg: `${badCount} 处会显示成 NaN/空白的坏数值`, samples: badSamples })
  if (infCount) issues.push({ code: 'INF_VALUE', level: 'warn', msg: `${infCount} 处 Infinity（多为合法语义，需确认显示层已转 ∞）`, samples: infSamples })

  // 相邻步骤完全一致：用户看到的是「点了下一步但画面没动」
  let dup = 0
  for (let i = 1; i < steps.length; i++) {
    if (JSON.stringify(stripDesc(steps[i])) === JSON.stringify(stripDesc(steps[i - 1]))) dup++
  }
  if (dup > 0) issues.push({ code: 'STATIC', level: 'warn', msg: `${dup} 个相邻步骤的数据完全相同（视觉上会卡住）` })

  for (const i of issues) if (!i.level) i.level = 'error'
  return issues
}

function stripDesc(s) {
  const o = { ...s }
  for (const k of ['desc', 'text', 'label', 'msg', 'message', 'tip', 'status', 'note']) delete o[k]
  return o
}

/* ------------------------------------------------------------------ */
/* 语义正确性断言：针对「结果算得对不对」，而不只是数据是否健全          */
/* 每条都对应一个真实踩过的坑，修好后用它锁死，防止回退                  */
/* ------------------------------------------------------------------ */

const isNumArr = v => Array.isArray(v) && v.length > 0 && v.every(x => typeof x === 'number' && isFinite(x))

const SEMANTIC = {
  // 排序类：终态必须有序，且元素多重集与初态一致（不能丢元素 / 凭空造元素）
  'vis/ds/QuickSort.vue': sortChecks,
  'vis/ds/MergeSort.vue': sortChecks,
  'vis/ds/HeapSort.vue': sortChecks,

  // ε-δ：求出的 δ 必须真的让边界偏差落在 ε 内。
  // 曾经因为采样漏掉端点 x = a±δ，导致 δ 偏大而界面仍宣称「恒有 |f(x)-L| < ε」。
  'vis/math/Limit.vue': steps => {
    const bad = steps.filter(s => typeof s.diff === 'number' && s.diff > s.eps + 1e-9)
    return bad.length
      ? [`${bad.length} 步的边界偏差 ${bad[0].diff.toFixed(6)} 超过 ε = ${bad[0].eps}（δ 求大了）`]
      : []
  },

  // 导数：差商描述里的自变量必须能分辨出增量。
  // 曾因 toFixed(3) 把 2.0001 截成 2，出现 [f(2) - f(2)] / 0.0001 = 4.0001 的荒谬表述。
  'vis/math/Derivative.vue': steps => {
    const bad = steps.filter(s => {
      const m = /\[f\(([-\d.]+)\) - f\(([-\d.]+)\)\]/.exec(s.desc || '')
      return m && s.h > 0 && m[1] === m[2]
    })
    return bad.length ? [`${bad.length} 步的差商描述里被减数与减数显示为同一个值（精度不足）`] : []
  },

  // 泰勒展开：局部误差应随阶数下降、有效逼近半径应随阶数扩大。
  // 曾在整个绘图域上比误差，得到「阶数越高误差越大」（1.0 → 57.2）的反直觉结论。
  'vis/math/Taylor.vue': steps => {
    const out = []
    const first = steps[0], last = steps[steps.length - 1]
    if (!(last.maxErr < first.maxErr)) out.push(`最大误差没有随阶数下降（${first.maxErr} → ${last.maxErr}）`)
    if (!(last.radius > first.radius)) out.push(`有效逼近半径没有随阶数扩大（${first.radius} → ${last.radius}）`)
    return out
  },

  // 循环队列：快照必须与当前指针自洽 —— 环形区间 [front, rear) 内的槽有值、区间外为空。
  // 曾经把出队后的数组引用直接存进快照又继续当队列用，后续入队会写进历史步骤，
  // 播放时能看到「还没入队的元素」。这条断言能直接抓住这种别名污染。
  'vis/ds/Queue.vue': steps => {
    const out = []
    const n = steps[0] && steps[0].q ? steps[0].q.length : 0
    if (!n) return []
    for (let i = 0; i < steps.length && out.length < 3; i++) {
      const s = steps[i]
      if (!Array.isArray(s.q)) continue
      const len = (s.rear - s.front + n) % n
      for (let k = 0; k < n; k++) {
        const inside = ((k - s.front + n) % n) < len
        const occupied = s.q[k] !== null && s.q[k] !== undefined
        if (inside !== occupied) {
          out.push(`第 ${i} 步槽位 [${k}] ${occupied ? '存着 ' + s.q[k] : '为空'}，但 front=${s.front} rear=${s.rear} 时它${inside ? '在' : '不在'}有效区间内（快照被后续操作污染）`)
          break
        }
      }
    }
    return out
  },

  // RIP 坏消息传得慢：R2—R3 断开后网络分成 {R1,R2} 与 {R3,R4}，
  // 跨断点的 8 个表项必须全部计到 16（∞）。曾经只检查了其中 4 个就收尾，
  // 终态表里留下「到 R3 不可达却到 R4 可达」的自相矛盾内容。
  'vis/net/RoutingProtocol.vue': steps => {
    const rip = steps.filter(s => s.kind === 'rip')
    if (!rip.length) return []
    const last = rip[rip.length - 1]
    const d = last.rip
    if (!d || !Array.isArray(d[0])) return []
    const INF = 16
    const cross = [[0, 2], [0, 3], [1, 2], [1, 3], [2, 0], [2, 1], [3, 0], [3, 1]]
    const fake = cross.filter(([i, j]) => d[i][j] < INF)
    if (fake.length) {
      return [`终态仍存在虚假路由：${fake.map(([i, j]) => `R${i + 1}→R${j + 1}=${d[i][j]}`).join('、')}（应全部到 ∞）`]
    }
    for (const [i, j] of [[0, 1], [1, 0], [2, 3], [3, 2]]) {
      if (d[i][j] !== 1) return [`终态应保留同侧直连 R${i + 1}→R${j + 1}=1，实际 ${d[i][j]}`]
    }
    return []
  },

  // TCP 拥塞控制：慢开始不允许越过 ssthresh，这是本组件最核心的考点。
  // 曾经先翻倍再判断门限，cwnd 从 8 直接翻到 16 越过 ssthresh=10，
  // 而且 phase 那时已切成拥塞避免，文案却说「线性 +1 = 16」，和实际行为对不上。
  'vis/net/CongestionControl.vue': steps => {
    const out = []
    for (let i = 1; i < steps.length; i++) {
      const prev = steps[i - 1], cur = steps[i]
      if (cur.event) continue                       // 丢包事件轮会重置 cwnd，不适用增长规则
      const delta = cur.cwnd - prev.cwnd
      const before = prev.cwnd
      const ssth = cur.ssthresh
      if (cur.grow === 'double') {
        // 慢开始：翻倍，且翻倍结果必须仍在门限之下
        if (Math.abs(delta - before) > 1e-9) {
          out.push(`第 ${cur.rtt} 轮声明慢开始翻倍，实际 ${before} → ${cur.cwnd}`)
        }
        if (cur.cwnd >= ssth) out.push(`第 ${cur.rtt} 轮慢开始翻倍后 cwnd=${cur.cwnd} 已越过门限 ${ssth}`)
      } else if (cur.grow === 'clamp') {
        // 封顶到门限
        if (Math.abs(cur.cwnd - ssth) > 1e-9) {
          out.push(`第 ${cur.rtt} 轮应封顶到 ssthresh=${ssth}，实际 cwnd=${cur.cwnd}`)
        }
        if (cur.cwnd < before) out.push(`第 ${cur.rtt} 轮封顶导致 cwnd 反而变小（${before} → ${cur.cwnd}）`)
      } else if (cur.grow === 'linear') {
        if (Math.abs(delta - 1) > 1e-9) {
          out.push(`第 ${cur.rtt} 轮声明线性 +1，实际 ${before} → ${cur.cwnd}`)
        }
      }
      // 拥塞避免期间绝不允许超过门限继续翻倍
      if (cur.phase === 'congestion-avoidance' && ssth > 0 && cur.cwnd > ssth && cur.grow === 'double') {
        out.push(`第 ${cur.rtt} 轮处于拥塞避免却用了翻倍增长`)
      }
      if (cur.cwnd <= 0) out.push(`第 ${cur.rtt} 轮 cwnd = ${cur.cwnd}（必须为正）`)
      if (out.length >= 4) break
    }
    // 窗口着色必须随轮次变化：曾经用累计发送量当起点，第 5 轮起 26 格全绿不动
    const sizes = new Set(steps.map(s => Math.min(s.cwnd, 20)))
    if (sizes.size < 3) out.push('窗口大小几乎没有变化，画面会一直卡着不动')
    return [...new Set(out)]
  },

  // 拓扑排序：描述「统计入度」的那一步，队列必须还是空的。
  // 曾在拍快照前就填好了队列，画面上队列里已有 A，与文案自相矛盾。
  'vis/ds/Topological.vue': steps => {
    const s = steps.find(x => (x.desc || '').includes('统计各顶点入度'))
    return s && s.queue && s.queue.length
      ? ['「统计入度」这一步队列不该已经有元素'] : []
  },

  // IEEE 754：①~④ 每步处理一个字段，阶段必须各不相同。
  // 曾经 ②（规格化）和 ③（求移码）共用 stage='exp'，且模板根本没读 stage，
  // 结果前六步画面完全一样，只有文字在动。
  'vis/co/FloatIeee754.vue': steps => {
    const out = []
    const stages = steps.map(s => s.stage)
    for (let i = 1; i < stages.length; i++) {
      if (stages[i] === stages[i - 1]) {
        out.push(`第 ${i - 1} 与第 ${i} 步阶段同为 '${stages[i]}'，画面不会变化`)
      }
    }
    for (const need of ['sign', 'exp', 'bias', 'mant']) {
      if (!stages.includes(need)) out.push(`缺少阶段 '${need}'（对应字段不会被高亮）`)
    }
    return out
  },

  // 高斯消元：把解代回最初的增广矩阵，残差必须为 0。
  // 这是最硬的校验 —— 消元过程画得再漂亮，解错了就是错的。
  'vis/linalg/Gauss.vue': steps => {
    const m0 = steps[0] && steps[0].m
    const x = steps[steps.length - 1] && steps[steps.length - 1].x
    if (!Array.isArray(m0) || !Array.isArray(x)) return ['取不到初始矩阵或解向量']
    const worst = Math.max(...m0.map(r =>
      Math.abs(r.slice(0, -1).reduce((s, v, i) => s + v * x[i], 0) - r[r.length - 1])
    ))
    return worst > 1e-6 ? [`解代回原方程的最大残差 ${worst.toFixed(6)}，消元解错了`] : []
  },

  // 页面置换：三个算法的缺页次数必须等于独立复算的结果。
  // 用经典教科书访问串与 3 个物理块：FIFO=15、LRU=12、OPT=9。
  'vis/os/PageReplacement.vue': steps => {
    const seq = steps.map(s => s.page)
    const last = steps[steps.length - 1].state || {}
    const expect = { fifo: fifoFaults(seq, FRAMES), lru: lruFaults(seq, FRAMES), opt: optFaults(seq, FRAMES) }
    const out = []
    for (const k of Object.keys(expect)) {
      const got = last[k] && last[k].faults
      if (typeof got !== 'number') { out.push(`取不到 ${k} 的缺页次数`); continue }
      if (got !== expect[k]) out.push(`${k.toUpperCase()} 缺页次数 ${got} ≠ 独立复算的 ${expect[k]}`)
    }
    return out
  },

  // 分页地址变换：初始步还没拆页号，P / d 必须是「未算出」。
  // 曾在第 0 步就把 P、d 算好了，于是第 1 步「① 拆分逻辑地址」画面毫无变化。
  'vis/os/PagingAddress.vue': steps => {
    const s0 = steps[0], s1 = steps[1]
    if (!s0 || !s1) return ['步骤不足']
    if (s0.P >= 0 || s0.d >= 0) return ['初始步就已经拆出了页号/页内偏移，下一步的「拆分」将没有视觉变化']
    if (!(s1.P >= 0 && s1.d >= 0)) return ['「① 拆分逻辑地址」这一步没有给出页号/页内偏移']
    return []
  },

  // 堆排序：筛选过程要有 move / settle 之类的状态标记，
  // 否则「移到某结点」与「该结点筛选结束」两步画面完全一致。
  'vis/ds/HeapSort.vue': steps => {
    const marks = new Set(steps.map(s => s.mark).filter(Boolean))
    return marks.has('settle') && marks.has('move') ? [] : ['缺少 move/settle 状态标记，筛选过程会出现静止帧']
  },
}

/* ------------------------------------------------------------------ */
/* 视觉方向断言：验证「画出来的上下/左右顺序」与课本一致                  */
/* 数据对了但画反了，是最难被发现的一类 bug —— 栈就是活例子：            */
/* 索引已经倒序渲染，CSS 又来一次 column-reverse，栈顶栈底整个颠倒。      */
/* 这里在 Node 里把播放器定位到指定步骤重新渲染，直接检查 DOM 顺序。      */
/* ------------------------------------------------------------------ */

/**
 * 求某个 CSS 类在渲染结果里的「视觉顺序」。
 * SSR 输出的 HTML 只有 DOM 顺序，CSS 不影响它 —— 所以必须自己把
 * flex-direction: *-reverse 考虑进去，否则这类检查会永远通过。
 */
function visualOrder(html, src, cls, cssSel) {
  const domOrder = [...html.matchAll(
    new RegExp('class="' + cls + '[^"]*"[^>]*>\\s*([^<]*)<', 'g')
  )].map(m => m[1].trim())
  // 注意：承载 flex-direction 的 CSS 选择器通常不是元素自身的 class，
  // 而是它的容器（栈的槽位叫 .slot-val，但排布规则写在 .slots 上）
  const block = new RegExp('\\.' + (cssSel || cls) + '\\s*\\{([^}]*)\\}').exec(src)
  const reversed = block && /flex-direction:\s*(column|row)-reverse/.test(block[1])
  return reversed ? domOrder.slice().reverse() : domOrder
}

const ORIENT = {
  // 拓扑排序：必须等算法真正结束才能宣布「存在环」。
  // 曾经额外补了一条「队列为空就当成有环」的判据，而中途队列为空是正常的
  // （刚出队、后继尚未入队），结果合法的 DAG 在整个排序过程中反复显示「存在环」，
  // 面板结论与实际数据自相矛盾。这条只能查渲染后的 HTML ——
  // hasCycle 是 computed，不落在步骤数组里，纯数据校验抓不到。
  'vis/ds/Topological.vue': {
    pick: steps => {
      const total = Math.max(...steps.map(s => (s.order || []).length))
      for (let i = 0; i < steps.length; i++) {
        const s = steps[i]
        if (s.cycle || s.done) continue
        if ((s.queue || []).length === 0 && (s.order || []).length > 0 && (s.order || []).length < total) return i
      }
      return -1
    },
    check: (steps, html) => (/存在环，无法拓扑排序/.test(html)
      ? ['排序尚未结束就显示「存在环」：中途队列为空是正常的，不能据此判定有环']
      : []),
  },

  // 流水线：公式框里的算式必须真的算得通。
  // 曾经分母写死 k + n − 1，于是屏幕上出现「6×5 / 10 = 2.73」——
  // 手算 30/10 明明是 3.00，而同一屏的「所需时钟周期」却写着 11（含 1 个气泡周期）。
  // 学生照着公式手算对不上，只会怀疑自己算错了。
  //
  // 这类错误**只能查渲染结果**：模板里的表达式在 computed 层面是自洽的，
  // 只有把页面渲染出来、把公式文本里的数字真的算一遍才会暴露。
  // 且只在勾选「数据冒险」时才出现，所以 set 里要开 hazard。
  'vis/co/Pipeline.vue': {
    set: { hazard: true },
    pick: () => 0,
    check: (steps, html) => {
      const out = []
      const strip = s => s.replace(/<[^>]+>/g, '')
      // 周期数：k + (n − 1) + 气泡 = a + b + c = d
      const cyc = /(\d+)\s*\+\s*\(?(\d+)\s*[−\-]\s*1\)?\s*\+\s*(\d+)\s*=\s*(\d+)/.exec(strip(html))
      if (cyc) {
        const [k, n, bub, total] = [Number(cyc[1]), Number(cyc[2]), Number(cyc[3]), Number(cyc[4])]
        if (k + n - 1 + bub !== total) {
          out.push(`周期数公式不成立：${k} + (${n} − 1) + ${bub} 应等于 ${k + n - 1 + bub}，页面写的是 ${total}`)
        }
      }
      // 加速比：n×k / 分母 = 结果
      const sp = /(\d+)×(\d+)\s*\/\s*(\d+)\s*=\s*([\d.]+)/.exec(strip(html))
      if (!sp) return out.concat(['公式框里找不到可验算的加速比算式'])
      const [n, k, den, res] = [Number(sp[1]), Number(sp[2]), Number(sp[3]), Number(sp[4])]
      if (den === 0) return out.concat(['加速比公式的分母为 0'])
      const expect = (n * k) / den
      if (Math.abs(expect - res) > 0.011) {
        out.push(`加速比公式不成立：页面写 ${n}×${k} / ${den} = ${res}，实际 ${n}×${k}/${den} = ${expect.toFixed(2)}`)
      }
      // 分母必须就是同一屏里显示的「所需时钟周期」
      if (cyc && Number(cyc[4]) !== den) {
        out.push(`公式框的分母 ${den} 与「所需时钟周期」${cyc[4]} 不一致，同屏两个数字对不上`)
      }
      return out
    },
  },

  'vis/ds/Stack.vue': {
    // 挑一个栈里有 ≥3 个元素的步骤，才看得出堆叠方向
    pick: steps => steps.findIndex(s => Array.isArray(s.stack) && s.stack.length >= 3),
    check: (steps, html, src) => {
      const i = steps.findIndex(s => Array.isArray(s.stack) && s.stack.length >= 3)
      const st = steps[i].stack
      const order = visualOrder(html, src, 'slot-val', 'slots')
      if (order.length !== st.length) {
        return [`渲染出的槽位数 ${order.length} 与栈深度 ${st.length} 不符`]
      }
      const out = []
      // 栈顶（最后入栈）必须画在最上面，栈底（最先入栈）画在最下面
      if (order[0] !== st[st.length - 1]) {
        out.push(`栈顶画错了：最上方的槽是 ${order[0]}，应为栈顶 ${st[st.length - 1]}`)
      }
      if (order[order.length - 1] !== st[0]) {
        out.push(`栈底画错了：最下方的槽是 ${order[order.length - 1]}，应为栈底 ${st[0]}`)
      }
      return out
    },
  },
}

/* 页面置换的独立实现：不复用被测组件的任何代码，用来交叉验证缺页次数 */
const FRAMES = 3 // 该组件用 3 个物理块演示
function fifoFaults(seq, f) {
  const q = [], mem = new Set()
  let n = 0
  for (const p of seq) {
    if (mem.has(p)) continue
    n++
    if (mem.size < f) { mem.add(p); q.push(p) }
    else { const o = q.shift(); mem.delete(o); mem.add(p); q.push(p) }
  }
  return n
}
function lruFaults(seq, f) {
  const mem = []
  let n = 0
  for (const p of seq) {
    const i = mem.indexOf(p)
    if (i >= 0) { mem.splice(i, 1); mem.push(p); continue }
    n++
    if (mem.length < f) mem.push(p)
    else { mem.shift(); mem.push(p) }
  }
  return n
}
function optFaults(seq, f) {
  const mem = []
  let n = 0
  for (let i = 0; i < seq.length; i++) {
    const p = seq[i]
    if (mem.includes(p)) continue
    n++
    if (mem.length < f) { mem.push(p); continue }
    let victim = mem[0], far = -1
    for (const m of mem) {
      const next = seq.indexOf(m, i + 1)
      const d = next < 0 ? Infinity : next
      if (d > far) { far = d; victim = m }
    }
    mem.splice(mem.indexOf(victim), 1)
    mem.push(p)
  }
  return n
}
/** 排序类通用检查：终态有序 + 元素不增不减 */
function sortChecks(steps) {
  const out = []
  const a0 = steps[0] && steps[0].arr
  const a1 = steps[steps.length - 1] && steps[steps.length - 1].arr
  if (!isNumArr(a0) || !isNumArr(a1)) return ['取不到初态/末态数组']
  if (a0.length !== a1.length) out.push(`排序后元素个数变了：${a0.length} → ${a1.length}`)
  const s0 = [...a0].sort((x, y) => x - y)
  const s1 = [...a1].sort((x, y) => x - y)
  if (s0.join(',') !== s1.join(',')) out.push('排序后元素集合与初态不一致（丢了或多了元素）')
  for (let i = 1; i < a1.length; i++) {
    if (a1[i - 1] > a1[i]) { out.push(`终态并未有序：位置 ${i - 1} 的 ${a1[i - 1]} > 位置 ${i} 的 ${a1[i]}`); break }
  }
  return out
}

/* ------------------------------------------------------------------ */
/* 加载并执行                                                          */
/* ------------------------------------------------------------------ */

const vite = await createServer({
  root,
  logLevel: 'error',
  server: { middlewareMode: true },
  appType: 'custom',
})

/** 把某个组件渲染到指定步骤（在 created 钩子里改播放器索引，赶在渲染前生效） */
async function renderAt(Comp, stepIdx, overrides = {}) {
  const app = createSSRApp({ render: () => h(Comp) })
  app.use(ElementPlus)
  app.provide('__EP_ID_INJECTION__', { prefix: 1, current: 0 })
  for (const [k, v] of Object.entries(ElIcons)) app.component(k, v)
  app.config.warnHandler = () => {}
  app.mixin({
    created() {
      const st = (this.$ || this).setupState
      if (st) {
        for (const [k, v] of Object.entries(overrides)) {
          if (!Object.prototype.hasOwnProperty.call(st, k)) continue
          st[k] = v
        }
      }
      const p = this.player
      if (p && p.idx && typeof p.idx === 'object' && 'value' in p.idx) p.idx.value = stepIdx
    },
  })
  return await renderToString(app)
}

/**
 * 部分分支在组件的默认状态下永远走不到（比如「无穷多解」「组相联映射」），
 * 光跑一遍默认场景等于没测。这里列出需要改写内部 ref 才能覆盖的场景。
 *   set   —— 在组件 created 时改写的 ref（必须是 ref，computed 不可写）
 *   check —— 对该变体步骤数组的语义断言
 */
const VARIANTS = {
  // 无穷多解：必须做完整回代，否则自由变量的系数算错，
  // 界面上会显示一组代回原方程残差不为 0 的「通解」
  'vis/linalg/Gauss.vue': [{
    // 注意：只改 presetKey 不会重新加载矩阵（rows 由 applyPreset 的 @change 填充），
    // 必须连 rows 一起改写，否则跑的还是默认的唯一解方程
    name: '无穷多解',
    set: { presetKey: 'inf', rows: [[1, 1, 1, 3], [2, 2, 2, 6], [1, -1, 2, 2]] },
    check: steps => {
      const first = steps[0], last = steps[steps.length - 1]
      if (!last || last.kind !== 'infinite') return ['最后一步的解类型不是无穷多解']
      const exprs = last.exprs, free = last.freeCols
      const n = first.m[0].length - 1
      if (!exprs || !exprs.length) return ['没有给出通解表达式']
      if (exprs.some(e => free.includes(e.pc))) return ['主元行里混入了自由未知量']
      const out = []
      // 取若干组自由变量取值，把通解代回最初的原方程，残差必须为 0
      for (const t of [0, 1, 2, -1, 0.5]) {
        const x = new Array(n).fill(0)
        for (const fc of free) x[fc] = t
        for (const e of exprs) {
          let v = e.c0
          for (const fc of free) v += (e.co[fc] || 0) * t
          if (!isFinite(v)) return [`通解出现非有限值（t=${t} 时 x${e.pc + 1}=${v}）`]
          x[e.pc] = v
        }
        const res = first.m.map(r => {
          let s = -r[n]
          for (let j = 0; j < n; j++) s += r[j] * x[j]
          return s
        })
        const worst = Math.max(...res.map(Math.abs))
        if (worst > 1e-6) {
          out.push(`t=${t} 时通解代回原方程残差最大 ${worst.toFixed(6)}（应为 0），解向量 = [${x.map(v => v.toFixed(3)).join(', ')}]`)
        }
      }
      return out
    },
  }, {
    name: '无解',
    set: { presetKey: 'none', rows: [[1, 1, 1, 3], [2, 2, 2, 7], [1, -1, 1, 1]] },
    check: steps => {
      const last = steps[steps.length - 1]
      if (last.kind !== 'none') return [`应为无解，实际解类型为 ${last.kind}`]
      const m = last.m
      const n = m[0].length - 1
      const hasConflict = m.some(r => r.slice(0, n).every(v => Math.abs(v) < 1e-9) && Math.abs(r[n]) > 1e-9)
      return hasConflict ? [] : ['声明无解，但终态矩阵里找不到「0 = 非零」的矛盾行']
    },
  }],

  // ARP：响应与数据帧的端点必须跟着选中的目标走。
  // 曾经硬编码 from:1/to:0（永远是主机 B），切换到主机 C/D 后，
  // 文案说「主机 C 识别出自己的 IP」，箭头却仍连在主机 B 上。
  'vis/net/Arp.vue': [{
    name: '目标=主机 D',
    set: { targetIp: '192.168.1.4' },
    check: steps => {
      const out = []
      const tgt = 3 // 主机 D 在 hosts 里的下标
      for (const s of steps) {
        for (const p of s.packets || []) {
          if (p.to === 'all' || typeof p.to !== 'number') continue
          // 目标是 D 时，响应应由 D 发往 A、数据帧由 A 发往 D
          const expectTo = p.label.includes('响应') ? 0 : tgt
          const expectFrom = p.label.includes('响应') ? tgt : 0
          if (p.from === expectFrom && p.to === expectTo) continue
          out.push(`「${p.label}」连成了 ${p.from} → ${p.to}，目标切换到主机 D 后应为 ${expectFrom} → ${expectTo}`)
        }
      }
      return [...new Set(out)]
    },
  }],

  // DNS：只有拿到 A 记录才该显示解析结果。
  // 曾经只要 m.cache 存在就显示最终 IP，而根/TLD 的 referral 也带 cache
  // （缓存的是下一级服务器地址），导致第 3 步还是「引用回答」时结果栏已提前显示 IP。
  'vis/net/Dns.vue': [{
    name: '迭代查询',
    set: { isRecursive: false },
    check: steps => {
      const out = []
      for (let i = 0; i < steps.length; i++) {
        const s = steps[i]
        const type = String(s.type || '')
        const hasIp = s.resultIp && s.resultIp !== '—'
        if (/引用回答|查询报文|递归委托|递归回送/.test(type) && hasIp) {
          out.push(`第 ${i} 步类型为「${type}」，却已显示解析结果 ${s.resultIp}`)
        }
      }
      // 末尾必须真的解析出结果
      const last = steps[steps.length - 1]
      if (!last || !last.resultIp || last.resultIp === '—') {
        out.push('最后一步没有给出解析出的 IP')
      }
      return out
    },
  }],

  // 组相联：8 行 × 2 路 = 4 组，组号 = 块号 mod 组数（4），不是 mod 路数（2）。
  // 曾经把路数当组数用，导致只用了一半 Cache 行、tag 也算错
  'vis/co/CacheMapping.vue': [{
    name: '组相联',
    set: { mode: 'set' },
    check: steps => {
      const out = []
      const WAYS = 2, SETS = 8 / WAYS
      const usedSets = new Set()
      for (const s of steps) {
        for (let i = 0; i < (s.lines || []).length; i++) {
          const l = s.lines[i]
          if (!l.valid) continue
          const expectTag = Math.floor(l.block / SETS)
          const expectSet = l.block % SETS
          if (Math.floor(i / WAYS) !== expectSet) {
            out.push(`块 ${l.block}（组 ${expectSet}）被放进了第 ${Math.floor(i / WAYS)} 组的行 ${i}`)
          }
          if (l.tag !== expectTag) out.push(`块 ${l.block} 的标记应为 ${expectTag}，实际 ${l.tag}`)
          usedSets.add(expectSet)
        }
      }
      // 用到的组数应等于「被访问过的块所属的组数」，而不是被 Cache 行数上限卡住。
      // 上面的逐行断言已经保证了每组放对位置；这里是防止整个组被闲置。
      const touched = new Set(steps.map(s => s.block % SETS))
      const missing = [...touched].filter(g => !usedSets.has(g))
      if (missing.length) out.push(`组 ${missing.join('、')} 的块从未真正装入对应组内`)
      return [...new Set(out)]
    },
  }],
}

/**
 * 有些错误藏在 computed 里，既不在步骤数组中、也读不到 HTML ——
 * 比如受力箭头的屏幕偏移（有多个箭头时，从 SVG 里判方向极易误判）。
 * 这里在组件实例上直接读取指定的 computed 值来做断言。
 *
 * 注意：只登记**纯数值/纯函数且一定会被求值**的字段；
 * 某些组件的 3D/2D 分支数据只在对应模式下才合法，强制求值会误报崩溃。
 */
const FIELD_CHECKS = {
  // 斜面受力：合力箭头必须与重力沿斜面分量同向（都指向下滑一侧），与摩擦力反向。
  // 曾经 netV 取的是 (+cos,+sin)，画面上合力画成沿斜面向上，
  // 而摩擦力明明已经正确地朝上、物块也正在下滑 —— 三个箭头自相矛盾，
  // 学生照着图会得出「合力阻止下滑」的错误结论。
  // 注意 netV/parV/fV 依赖「当前步骤」，静止状态下净力恰好为 0，
  // 只看初始步拿不到有意义的向量。必须先定位到滑动步骤。
  'vis/phys/Incline.vue': (state, steps) => {
    const idx = steps.findIndex(s => s.state === 'slide')
    if (idx < 0) return ['找不到处于滑动状态的步骤，无法验证受力方向']
    // 挪到这里再取值，computed 会按新的当前步骤重算
    if (state.player && state.player.idx) state.player.idx.value = idx

    const need = ['netV', 'parV', 'fV']
    for (const k of need) {
      const v = state[k]
      if (!v || typeof v.dx !== 'number' || typeof v.dy !== 'number') {
        return [`取不到 ${k} 的屏幕偏移（改名了？）`]
      }
    }
    const out = []
    const dot = (a, b) => a.dx * b.dx + a.dy * b.dy
    const dPar = dot(state.netV, state.parV)
    const dFric = dot(state.netV, state.fV)
    const eps = 1e-6
    // 三者都非零才有判断意义；只要方向不对就报错
    if (Math.abs(dPar) > eps && dPar < 0) {
      out.push('合力箭头与重力沿斜面分量反向（画成了沿斜面向上，但物块正在下滑）')
    }
    if (Math.abs(dFric) > eps && dFric > 0) {
      out.push('合力箭头与摩擦力同向（两者应相反）')
    }
    if (Math.abs(state.netV.dx) < eps && Math.abs(state.netV.dy) < eps) {
      out.push('滑动步骤的合力箭头长度为 0（只有静止态才该是零合力）')
    }
    return out
  },

  // 流水线：公式框里的分母必须与实际周期数一致。
  // 曾经分母写死 k + n − 1，屏幕上出现「6×5 / 10 = 2.73」——
  // 手算 30/10 是 3.00，而同一屏的「所需时钟周期」却写着 11（含 1 个气泡周期）。
  // 学生照着公式手算会对不上，反而怀疑是自己算错了。
  'vis/co/Pipeline.vue': state => {
    const out = []
    const totalCycles = state.totalCycles
    const instCount = state.instCount
    const stageCount = (state.stages && state.stages.length) || 0
    if (!totalCycles || !instCount || !stageCount) return ['拿不到周期数 / 指令数 / 流水级数']
    const sp = Number(state.speedup)
    if (!isFinite(sp)) return ['加速比不是有限数字']
    const expect = (instCount * stageCount) / totalCycles
    if (Math.abs(sp - expect) > 0.011) {
      out.push(`加速比 ${sp} 与 (n·k)/总周期 = ${expect.toFixed(2)} 不符（公式框的分母没用实际周期数）`)
    }
    const cp = Number(state.cpi)
    if (isFinite(cp) && Math.abs(cp - totalCycles / instCount) > 0.011) {
      out.push(`实际 CPI ${cp} 与 总周期/指令数 = ${(totalCycles / instCount).toFixed(2)} 不符`)
    }
    if (totalCycles < stageCount + instCount - 1) {
      out.push(`总周期 ${totalCycles} 少于理想流水线的 k+n−1 = ${stageCount + instCount - 1}`)
    }
    return out
  },
}

const report = []

/**
 * 取组件的步骤快照。
 * overrides 用于在 created 阶段改写内部 ref，从而跑到组件默认状态覆盖不到的分支。
 * 必须赶在 created 里改：setup 已执行完（ref 存在），而 computed 还是惰性的，
 * 之后再读 steps 才会用新值重算。拿到实例后再改就晚了。
 */
async function loadStepsAndState(Comp, overrides = {})
{
  const captured = []
  const app = createSSRApp({ render: () => h(Comp) })
  app.use(ElementPlus)
  app.provide('__EP_ID_INJECTION__', { prefix: 1, current: 0 })
  for (const [k, v] of Object.entries(ElIcons)) app.component(k, v)
  app.config.warnHandler = () => {}
  app.mixin({
    created() {
      const st = (this.$ || this).setupState
      // mixin 的 created 在根组件上也会触发，而根的 setupState 是不可扩展的空对象，
      // 给它赋值会抛 "object is not extensible"。只改真正持有该 ref 的那个实例。
      if (st) {
        for (const [k, v] of Object.entries(overrides)) {
          if (!Object.prototype.hasOwnProperty.call(st, k)) continue
          // setupState 是 proxyRefs 代理：读 ref 会得到解包后的值，所以 r.value = v 写不进去。
          // 它的 set 陷阱规定「旧值是 ref 而新值不是时，写 ref.value」，因此必须整体赋值。
          st[k] = v
        }
      }
      captured.push(this)
    },
  })
  await renderToString(app)
  // 只按名字取 steps：避免 Object.entries 强制求值被 v-if 挡住的 computed，
  // 那会误报崩溃（某些组件的 3D/2D 分支数据只在对应模式下才合法）
  for (const vm of captured) {
    const st = (vm.$ || vm).setupState
    if (st && Array.isArray(st.steps) && st.steps.length) return { steps: st.steps, state: st }
  }
  return { steps: null, state: null }
}

async function loadSteps(Comp, overrides = {}) {
  return (await loadStepsAndState(Comp, overrides)).steps
}

for (const rel of targets) {
  const entry = { rel, ok: true, steps: 0, issues: [] }
  try {
    const mod = await vite.ssrLoadModule('@/components/' + rel)
    const Comp = mod.default
    if (!Comp) throw new Error('组件无 default 导出')

    const { steps, state } = await loadStepsAndState(Comp)
    if (!steps) throw new Error('未取到 steps（组件可能没用 usePlayer）')

    entry.steps = steps.length
    entry.raw = steps
    entry.issues = checkComponent(rel, steps)

    // 视觉方向断言：重新渲染一次，并在 created 钩子里把播放器定位到指定步骤。
    // 注意：不能在拿到旧实例后改 idx 再 renderToString —— 第二次渲染会新建组件实例，
    // 改的是旧实例的白费功夫。必须赶在渲染前设置。
    const orient = ORIENT[rel]
    if (orient) {
      // 同 VARIANTS：某些错误只在特定选项下才暴露（比如勾选数据冒险后的公式矛盾），
      // 需要连组件内部的 ref 一起改写后再渲染
      const oSteps = orient.set ? await loadSteps(Comp, orient.set) : steps
      const target = orient.pick(oSteps)
      if (target >= 0) {
        const html = await renderAt(Comp, target, orient.set || {})
        const src = fs.readFileSync(path.join(root, 'src/components', rel), 'utf8')
        const errs = orient.check(steps, html, src) || []
        if (process.env.VIS_DEBUG) console.log('[dbg]', rel, 'target', target, 'errs', errs)
        for (const e of errs) entry.issues.push({ code: 'WRONG_ORIENT', level: 'error', msg: e })
      } else {
        entry.issues.push({ code: 'WRONG_ORIENT', level: 'warn', msg: '找不到可用于校验视觉方向的步骤' })
      }
    }

    // 语义断言：结果算得对不对
    const checker = SEMANTIC[rel]
    if (checker) {
      const errs = checker(steps) || []
      for (const e of errs) entry.issues.push({ code: 'WRONG_RESULT', level: 'error', msg: e })
    }

    // computed 级断言：读组件内部的计算值，查数据层面看不到的错误。
    // 这一步放在最后是为了让它在 state 上取值（只登记确定会被求值的纯数值字段）
    const fieldCheck = FIELD_CHECKS[rel]
    if (fieldCheck) {
      const errs = fieldCheck(state, steps) || []
      for (const e of errs) entry.issues.push({ code: 'WRONG_COMPUTED', level: 'error', msg: e })
    }
    // 变体场景：改写内部 ref 后重跑，校验默认状态覆盖不到的分支
    for (const v of VARIANTS[rel] || []) {
      let vSteps = null
      try { vSteps = await loadSteps(Comp, v.set) } catch (e) {
        entry.issues.push({ code: 'VARIANT_CRASH', level: 'error', msg: `变体「${v.name}」崩溃：${String(e.message || e).split('\n')[0].slice(0, 120)}` })
        continue
      }
      if (!vSteps) { entry.issues.push({ code: 'VARIANT_FAIL', level: 'error', msg: `变体「${v.name}」取不到步骤` }); continue }
      const errs = v.check(vSteps) || []
      for (const e of errs) entry.issues.push({ code: 'WRONG_RESULT', level: 'error', msg: `变体「${v.name}」：${e}` })
    }
    entry.ok = !entry.issues.some(i => i.level === 'error')
  } catch (e) {
    entry.ok = false
    entry.issues = [{ code: 'CRASH', msg: String(e.message || e).split('\n')[0].slice(0, 150) }]
  }
  report.push(entry)
}

await vite.close()

/* ------------------------------------------------------------------ */
/* 输出                                                               */
/* ------------------------------------------------------------------ */

if (process.argv.includes('--json') || process.argv.includes('--dump')) {
  // --dump：把每个组件的步骤数据落盘，供人工审查「结果算得对不对」
  if (process.argv.includes('--dump')) {
    fs.mkdirSync(path.join(root, '.vis-dump'), { recursive: true })
    for (const r of report) {
      if (!r.raw) continue
      const name = r.rel.replace(/\W+/g, '_')
      fs.writeFileSync(
        path.join(root, '.vis-dump', name + '.json'),
        JSON.stringify({ rel: r.rel, count: r.raw.length, steps: r.raw }, null, 2)
      )
    }
    console.log('已导出 ' + report.filter(r => r.raw).length + ' 个组件的首/末步到 .vis-dump/')
  } else {
    console.log(JSON.stringify(report, null, 2))
  }
} else {
  const bad = report.filter(r => !r.ok)
  const warn = report.filter(r => r.ok && r.issues.length)
  console.log(`\n=== 可视化动画体检 ===`)
  console.log(`组件总数: ${report.length}   健康: ${report.length - bad.length - warn.length}   有告警: ${warn.length}   有错误: ${bad.length}`)
  if (bad.length) {
    console.log('\n--- 错误 ---')
    for (const r of bad) {
      console.log(`  ✗ ${r.rel}  (${r.steps} 步)`)
      for (const i of r.issues) {
        console.log(`      [${i.code}] ${i.msg}`)
        if (i.samples) for (const s of i.samples) console.log(`          step ${s.step}: ${s.items.map(x => `${x.path}=${x.kind}`).join(', ')}`)
      }
    }
  }
  if (warn.length) {
    console.log('\n--- 告警 ---')
    for (const r of warn) {
      console.log(`  ! ${r.rel}  (${r.steps} 步)`)
      for (const i of r.issues) console.log(`      [${i.code}] ${i.msg}`)
    }
  }
  if (!bad.length) console.log('\n无阻断性错误 ✅')
}
process.exit(report.some(r => !r.ok) ? 1 : 0)
