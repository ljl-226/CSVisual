<template>
  <VisFrame title="进程同步 · 信号量与 wait/signal 原语" desc="记录型信号量：wait(S) 使 S.value--，<0 则进程阻塞入等待队列；signal(S) 使 S.value++，≤0 则唤醒队首等待者" :player="player" :status-text="statusText" back-to="/knowledge/47">
    <template #extra>
      <el-select v-model="mode" size="small" style="width:150px" @change="player.reset()">
        <el-option value="pc" label="生产者-消费者" />
        <el-option value="rw" label="读者-写者" />
        <el-option value="dp" label="哲学家进餐" />
      </el-select>
      <el-button size="small" plain @click="player.reset()">重置</el-button>
    </template>
    <div class="sp-wrap">
      <svg :width="W" :height="H" class="sp-svg">
        <!-- 角色：进程 -->
        <g v-for="(a, i) in ACTORS[mode]" :key="a">
          <circle :cx="30 + i * 48" :cy="36" r="16" :fill="cur.actor === a ? '#e6eeff' : '#fff'" :stroke="cur.actor === a ? '#3b6ef6' : '#c8d3e6'" stroke-width="2" />
          <text :x="30 + i * 48" :y="41" text-anchor="middle" font-size="12" font-weight="700" fill="#1f2733">{{ a }}</text>
          <text :x="30 + i * 48" :y="65" text-anchor="middle" font-size="10" :fill="blockedActors.includes(a) ? '#e05252' : '#b6bfcc'">{{ blockedActors.includes(a) ? '阻塞' : '就绪' }}</text>
        </g>
        <!-- 信号量卡片：名称 / 类型 / 当前值 / 等待队列 -->
        <g v-for="(s, i) in cur.sems" :key="s.name">
          <rect x="12" :y="78 + i * 44" width="252" height="38" rx="6" :fill="cur.focus === s.name ? '#eef3ff' : '#fff'" :stroke="cur.focus === s.name ? '#3b6ef6' : '#dfe4ec'" stroke-width="1.6" />
          <text x="22" :y="94 + i * 44" font-size="12" font-weight="700" fill="#1f2733">{{ s.name }}</text>
          <text x="22" :y="108 + i * 44" font-size="9.5" fill="#8b95a3">{{ s.kind }} · {{ s.note }}</text>
          <circle :cx="168" :cy="97 + i * 44" r="14" :fill="valFill(s.val)" />
          <text :x="168" :y="102 + i * 44" text-anchor="middle" font-size="14" font-weight="700" fill="#fff">{{ s.val }}</text>
          <text x="192" :y="108 + i * 44" font-size="10" :fill="s.queue.length ? '#e05252' : '#b6bfcc'">L：{{ s.queue.length ? s.queue.join(' → ') : '空' }}</text>
        </g>
        <!-- 生产者-消费者：循环缓冲区 -->
        <g v-if="mode === 'pc'">
          <text x="290" y="26" font-size="12" font-weight="700" fill="#1f2733">循环缓冲区（容量 3）</text>
          <g v-for="(b, i) in cur.buffer" :key="i">
            <rect :x="290 + i * 112" y="78" width="100" height="52" rx="6" :fill="b ? '#dcf3e7' : '#f7f9fc'" :stroke="b ? '#22a06b' : '#dfe4ec'" stroke-width="1.6" />
            <text :x="340 + i * 112" :y="106" text-anchor="middle" font-size="12" :fill="b ? '#176b48' : '#b6bfcc'">{{ b ? '产品 #' + b : '空' }}</text>
            <text v-if="cur.inIdx === i" :x="340 + i * 112" y="70" text-anchor="middle" font-size="10" fill="#3b6ef6">in ↑</text>
            <text v-if="cur.outIdx === i" :x="340 + i * 112" y="146" text-anchor="middle" font-size="10" fill="#e8a13a">out ↑</text>
          </g>
        </g>
        <!-- 读者-写者：读者计数与共享文件 -->
        <g v-if="mode === 'rw'">
          <text x="290" y="26" font-size="12" font-weight="700" fill="#1f2733">共享文件与读者计数</text>
          <rect x="290" y="78" width="150" height="52" rx="6" fill="#eef3ff" stroke="#3b6ef6" stroke-width="1.6" />
          <text x="365" y="120" text-anchor="middle" font-size="20" font-weight="700" fill="#3b6ef6">{{ cur.readcount }}</text>
          <rect x="455" y="78" width="186" height="52" rx="6" :fill="cur.file === '空闲' ? '#f7f9fc' : '#fff3e0'" :stroke="cur.file === '空闲' ? '#dfe4ec' : '#e8a13a'" stroke-width="1.6" />
          <text x="548" y="120" text-anchor="middle" font-size="13" font-weight="700" :fill="cur.file === '空闲' ? '#8b95a3' : '#a5701a'">{{ cur.file || '空闲' }}</text>
        </g>
        <!-- 哲学家进餐：圆桌与筷子（筷子 i 位于 P(i) 与 P(i+1) 之间） -->
        <g v-if="mode === 'dp'">
          <text x="290" y="20" font-size="12" font-weight="700" fill="#1f2733">圆桌 · 筷子 i 位于 P(i) 与 P(i+1) 之间</text>
          <line v-for="i in 5" :key="'c' + i" :x1="SEAT[i - 1].x" :y1="SEAT[i - 1].y" :x2="SEAT[i % 5].x" :y2="SEAT[i % 5].y" :stroke="cur.chop[i - 1] ? '#e05252' : '#c8d3e6'" :stroke-width="cur.chop[i - 1] ? 3.5 : 2" :stroke-dasharray="cur.chop[i - 1] ? '' : '5,4'" />
          <text v-for="i in 5" :key="'ct' + i" :x="(SEAT[i - 1].x + SEAT[i % 5].x) / 2" :y="(SEAT[i - 1].y + SEAT[i % 5].y) / 2 - 4" text-anchor="middle" font-size="10" :fill="cur.chop[i - 1] ? '#a32c2c' : '#8b95a3'">{{ cur.chop[i - 1] ? '被 ' + cur.chop[i - 1] + ' 持有' : 'c' + (i - 1) }}</text>
          <g v-for="(p, i) in SEAT" :key="'p' + i">
            <circle :cx="p.x" :cy="p.y" r="24" :fill="cur.actor === 'P' + i ? '#e6eeff' : '#fff'" :stroke="eating('P' + i) ? '#22a06b' : (blockedActors.includes('P' + i) ? '#e05252' : '#c8d3e6')" stroke-width="2" />
            <text :x="p.x" :y="p.y + 5" text-anchor="middle" font-size="12" font-weight="700" fill="#1f2733">P{{ i }}</text>
          </g>
        </g>
      </svg>
      <div class="sp-panel">
        <div class="info-row"><span>当前原语</span><b style="color:var(--brand)">{{ cur.action || '—' }}</b></div>
        <div class="info-row"><span>执行结果</span><el-tag size="small" :type="resultTag.type">{{ resultTag.text }}</el-tag></div>
        <div class="code">wait(S)：S.value--；若 S.value &lt; 0 则 block(S.L)<br />signal(S)：S.value++；若 S.value ≤ 0 则 wakeup(S.L)</div>
        <div class="rule"><b>互斥信号量</b>初值 1（如 mutex），wait/signal 必须成对夹住临界区；<b>同步信号量</b>初值取资源数（如 empty=N、full=0），用来安排前驱后继的执行顺序。</div>
        <p class="tip small muted">{{ modeNote }}</p>
      </div>
    </div>
    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> 正在执行的进程</span>
      <span><i class="dot" style="background:#22a06b"></i> value &gt; 0，有空闲资源</span>
      <span><i class="dot" style="background:#e8a13a"></i> value = 0，恰好用完</span> <span><i class="dot" style="background:#e05252"></i> value &lt; 0，有进程阻塞等待</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'
const mode = ref('pc')
const W = 660
const H = 250
// 哲学家围坐圆桌（正五边形），筷子 i 位于 P(i) 与 P((i+1)%5) 之间
const SEAT = Array.from({ length: 5 }, (_, i) => {
  const a = -Math.PI / 2 + (i * 2 * Math.PI) / 5
  return { x: 470 + 76 * Math.cos(a), y: 140 + 76 * Math.sin(a) }
})
const ACTORS = { pc: ['P', 'C'], rw: ['R1', 'R2', 'W'], dp: ['P0', 'P1', 'P2', 'P3', 'P4'] }
// 原语简写：w=wait，s=signal，x=临界区动作
const w = (a, s) => ({ a, op: 'wait', s })
const sg = (a, s) => ({ a, op: 'signal', s })
const act = (a, fn) => ({ a, op: 'act', fn })
const putAct = st => { st.cnt++; const p = st.in; st.buffer[p] = st.cnt; st.in = (st.in + 1) % 3; return `把产品 #${st.cnt} 放入 buffer[${p}]，in 指针移到 ${st.in}` }
const getAct = st => { const p = st.out; const v = st.buffer[p]; st.buffer[p] = null; st.out = (st.out + 1) % 3; return `从 buffer[${p}] 取走产品 #${v}，out 指针移到 ${st.out}` }
/* 各模式的原语执行脚本；P 在缓冲区满时阻塞，由 C 取走一件后 signal(empty) 唤醒 */
function buildOps(m) {
  const o = []
  if (m === 'pc') {
    const put = () => [w('P', 'empty'), w('P', 'mutex'), act('P', putAct), sg('P', 'mutex'), sg('P', 'full')]
    const get = () => [w('C', 'full'), w('C', 'mutex'), act('C', getAct), sg('C', 'mutex'), sg('C', 'empty')]
    o.push(...put(), ...put(), ...get(), ...put(), ...put())
    o.push(w('P', 'empty'))                 // 缓冲区已满 → P 在此阻塞
    o.push(...get())                        // C 取走一件 → signal(empty) 唤醒 P
    o.push(w('P', 'mutex'), act('P', st => { st.cnt++; const p = st.in; st.buffer[p] = st.cnt; st.in = (st.in + 1) % 3; return `被唤醒后进入临界区，把产品 #${st.cnt} 放入 buffer[${p}]` }), sg('P', 'mutex'), sg('P', 'full'))
  } else if (m === 'rw') {
    o.push(
      w('R1', 'rmutex'), act('R1', st => { st.readcount++; st.file = 'R1 正在读'; return `readcount 由 ${st.readcount - 1} 增为 ${st.readcount}，是第一个读者，须抢 wmutex 挡住写者` }),
      w('R1', 'wmutex'), sg('R1', 'rmutex'),
      w('R2', 'rmutex'), act('R2', st => { st.readcount++; st.file = 'R1、R2 并发读'; return `readcount 增为 ${st.readcount}，第二个读者无需再抢 wmutex，可直接读` }), sg('R2', 'rmutex'),
      w('W', 'wmutex'),                     // wmutex 已被读者占用 → 写者阻塞
      w('R1', 'rmutex'), act('R1', st => { st.readcount--; st.file = st.readcount ? 'R2 正在读' : '空闲'; return `读完退出，readcount 由 ${st.readcount + 1} 减为 ${st.readcount}` }), sg('R1', 'rmutex'),
      w('R2', 'rmutex'), act('R2', st => { st.readcount--; return `readcount 减为 ${st.readcount}，最后一个读者须释放 wmutex` }), sg('R2', 'wmutex'), sg('R2', 'rmutex'),
      act('W', st => { st.file = 'W 正在写（独占）'; return '被唤醒，独占修改共享文件，其它读写进程均被挡住' }), sg('W', 'wmutex'))
  } else {
    o.push(w('P0', 'chop[0]'), w('P0', 'chop[1]'), act('P0', () => '同时拿到左右两支筷子，开始进餐'), sg('P0', 'chop[0]'), sg('P0', 'chop[1]'))
    for (let i = 0; i < 5; i++) o.push(w('P' + i, 'chop[' + i + ']'))            // 每人先拿左筷
    for (let i = 0; i < 5; i++) o.push(w('P' + i, 'chop[' + ((i + 1) % 5) + ']')) // 再拿右筷 → 全部阻塞
  }
  return o
}
const steps = computed(() => {
  const m = mode.value
  const out = []
  let sems, st
  if (m === 'pc') {
    sems = [{ name: 'empty', val: 3, kind: '同步', note: '空缓冲单元数' }, { name: 'full', val: 0, kind: '同步', note: '已生产产品数' }, { name: 'mutex', val: 1, kind: '互斥', note: '缓冲区互斥访问' }]
    st = { buffer: [null, null, null], in: 0, out: 0, cnt: 0 }
  } else if (m === 'rw') {
    sems = [{ name: 'rmutex', val: 1, kind: '互斥', note: '保护 readcount' }, { name: 'wmutex', val: 1, kind: '互斥', note: '读写/写写互斥' }]
    st = { readcount: 0, file: '空闲' }
  } else {
    sems = Array.from({ length: 5 }, (_, i) => ({ name: `chop[${i}]`, val: 1, kind: '互斥', note: `第 ${i} 支筷子` }))
    st = { chop: Array.from({ length: 5 }, () => null) }
  }
  sems.forEach(s => { s.queue = [] })
  const blockedOn = {}
  const chopIdx = name => { const r = /^chop\[(\d)\]$/.exec(name); return r ? +r[1] : -1 }
  function snap(desc, extra = {}) {
    const base = {
      sems: sems.map(s => ({ ...s, queue: [...s.queue] })),
      buffer: [...(st.buffer || [])], inIdx: st.in, outIdx: st.out,
      chop: [...(st.chop || [])], actor: null, action: '—', focus: null, result: 'ok'
    }
    // readcount / file 只在读者-写者模式下存在。哲学家就餐模式下它们无意义，
    // 硬塞进快照会得到 undefined，界面上渲染成空白。
    if (m === 'rw') { base.readcount = st.readcount; base.file = st.file }
    out.push({ ...base, ...extra, desc })
  }
  snap('初始状态：' + sems.map(s => `${s.name}=${s.val}`).join('，') + '；尚无进程阻塞')
  for (const op of buildOps(m)) {
    if (blockedOn[op.a]) continue                       // 阻塞中的进程被挂起，不再往下执行
    const s = sems.find(x => x.name === op.s)
    if (op.op === 'wait') {
      s.val--
      if (s.val < 0) {
        s.queue.push(op.a); blockedOn[op.a] = s.name
        snap(`${op.a} 执行 wait(${s.name})：${s.name} 由 ${s.val + 1} 减为 ${s.val} < 0 → 资源不足，${op.a} 自我阻塞并挂入 ${s.name}.L 等待队列`, { actor: op.a, action: `wait(${s.name})`, focus: s.name, result: 'block' })
      } else {
        const ci = chopIdx(s.name)
        if (ci >= 0) st.chop[ci] = op.a
        snap(`${op.a} 执行 wait(${s.name})：${s.name} 由 ${s.val + 1} 减为 ${s.val} → ${s.kind === '互斥' ? '拿到锁，进入临界区' : '消耗一个资源，继续执行'}`, { actor: op.a, action: `wait(${s.name})`, focus: s.name, result: 'ok' })
      }
    } else if (op.op === 'signal') {
      s.val++
      const wk = s.val <= 0 ? s.queue.shift() : null
      if (wk) delete blockedOn[wk]
      const ci = chopIdx(s.name)
      if (ci >= 0) st.chop[ci] = null
      snap(wk
        ? `${op.a} 执行 signal(${s.name})：${s.name} 由 ${s.val - 1} 加为 ${s.val} ≤ 0 → 队列中仍有等待者，唤醒队首进程 ${wk}`
        : `${op.a} 执行 signal(${s.name})：${s.name} 由 ${s.val - 1} 加为 ${s.val}${s.kind === '互斥' ? '，释放锁，退出临界区' : '，归还一个资源'}`,
        { actor: op.a, action: `signal(${s.name})`, focus: s.name, result: wk ? 'wake' : 'ok' })
    } else {
      const d = op.fn(st)
      snap(`${op.a} 在临界区内：${d}`, { actor: op.a, action: '临界区操作', focus: null, result: 'cs' })
    }
  }
  if (m === 'dp') snap('5 位哲学家各持左筷并等待右筷 → 形成环路等待，死锁！解法：①至多允许 4 人同时拿筷 ②左右筷同时可用才拿（AND 型信号量）③奇偶号按不同先后顺序拿', { result: 'dead' })
  return out
})
const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
const blockedActors = computed(() => cur.value.sems.flatMap(s => s.queue))
const eating = a => cur.value.chop && cur.value.chop.filter(c => c === a).length === 2
const valFill = v => (v < 0 ? '#e05252' : v === 0 ? '#e8a13a' : '#22a06b')
const resultTag = computed(() => ({
  ok: { text: '正常执行', type: 'success' }, cs: { text: '临界区操作', type: 'primary' },
  block: { text: '阻塞入队', type: 'danger' }, wake: { text: '唤醒等待者', type: 'warning' }, dead: { text: '已死锁', type: 'danger' }
}[cur.value.result] || { text: '正常执行', type: 'success' }))
const modeNote = computed(() => ({
  pc: '生产者-消费者：empty/full 是同步信号量，管"缓冲区满则停产、空则停取"的执行顺序；mutex 是互斥信号量，管一次只允许一个进程碰缓冲区。wait(mutex) 必须紧邻临界区，否则降低并发度甚至死锁。',
  rw: '读者-写者：允许多个读者并发读，写者必须独占。readcount 记录当前读者数并用 rmutex 保护；只有第一个读者抢 wmutex、最后一个读者释放 wmutex，即"读者优先"（会造成写者饥饿）。',
  dp: '哲学家进餐：每支筷子都是初值为 1 的互斥信号量。若 5 人同时拿起左筷，则每人都在等右筷，形成环路等待 → 死锁。'
}[mode.value]))
</script>

<style scoped>
.sp-wrap { display: flex; gap: 18px; align-items: flex-start; flex-wrap: wrap; }
.sp-svg { background: #fbfcff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.sp-panel { flex: 1; min-width: 260px; }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.code, .rule { margin-top: 10px; font-size: 12px; line-height: 1.9; color: var(--text-2); }
.code { background: #f2f4f8; border-radius: 6px; padding: 8px 10px; font-family: Consolas, monospace; }
.tip { margin-top: 10px; line-height: 1.8; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
