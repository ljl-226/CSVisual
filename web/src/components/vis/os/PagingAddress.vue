<template>
  <VisFrame title="分页存储管理 · 地址变换与快表 TLB" desc="逻辑地址 = 页号 P | 页内偏移 d；查页表把 P 换成物理块号 b，页内偏移原样照搬即拼成物理地址；缺页时由 OS 调页后重新执行该指令" :player="player" :status-text="statusText" back-to="/knowledge/50">
    <template #extra>
      <el-select v-model="pageSize" size="small" style="width:120px" @change="player.reset()">
        <el-option :value="512" label="512 B" /><el-option :value="1024" label="1 KB" /><el-option :value="2048" label="2 KB" /><el-option :value="4096" label="4 KB" />
      </el-select>
      <el-input v-model="addrText" size="small" style="width:110px" placeholder="逻辑地址" />
      <el-button size="small" @click="applyAddr">应用</el-button>
      <el-button size="small" plain @click="resetAll">重置</el-button>
    </template>
    <div class="pg-wrap">
      <svg :width="W" :height="H" class="pg-svg">
        <!-- ① 逻辑地址：按位拆成页号与页内偏移（说明文字拆成三行，不再横向冲出方框压到快表区） -->
        <rect x="14" y="14" width="212" height="122" rx="8" :fill="cur.stage === 'split' ? '#eef3ff' : '#fff'" :stroke="cur.stage === 'split' ? '#3b6ef6' : '#dfe4ec'" stroke-width="1.6" />
        <text x="24" y="32" font-size="12" font-weight="700" fill="#1f2733">① 逻辑地址（16 位）</text>
        <text x="24" y="50" font-size="10" fill="#8b95a3">A={{ cur.A }}　页号 P={{ cur.P >= 0 ? cur.P : '—' }}　偏移 d={{ cur.d >= 0 ? cur.d : '—' }}</text>
        <rect v-for="(c, i) in laBits.pn" :key="'lp'+i" :x="24 + i * 11.4" y="58" width="10.4" height="18" rx="2" :fill="splitDone ? '#e6eeff' : '#f2f4f8'" :stroke="splitDone ? '#cfe0ff' : '#e3e8f0'" />
        <text v-for="(c, i) in laBits.pn" :key="'lt'+i" :x="29 + i * 11.4" y="71" font-size="10" :fill="splitDone ? '#3b6ef6' : '#a7b0c0'">{{ c }}</text>
        <rect v-for="(c, i) in laBits.off" :key="'lo'+i" :x="24 + (laBits.pn.length + i) * 11.4" y="58" width="10.4" height="18" rx="2" :fill="splitDone ? '#fff3e0' : '#f2f4f8'" :stroke="splitDone ? '#f5d6a8' : '#e3e8f0'" />
        <text v-for="(c, i) in laBits.off" :key="'lot'+i" :x="29 + (laBits.pn.length + i) * 11.4" y="71" font-size="10" :fill="splitDone ? '#a5701a' : '#a7b0c0'">{{ c }}</text>
        <text x="24" y="90" font-size="10" fill="#3b6ef6">页号 {{ 16 - cur.b }} 位</text>
        <text x="24" y="104" font-size="10" fill="#a5701a">偏移 {{ cur.b }} 位（页大小 L = {{ cur.L }} B）</text>
        <text x="24" y="118" font-size="10" fill="#8b95a3">P = A div L，d = A mod L</text>
        <!-- ② 快表 -->
        <rect x="252" y="14" width="170" height="122" rx="8" :fill="cur.stage === 'tlb' ? '#eef3ff' : '#fff'" :stroke="cur.stage === 'tlb' ? '#3b6ef6' : '#dfe4ec'" stroke-width="1.6" />
        <text x="262" y="32" font-size="12" font-weight="700" fill="#1f2733">② 快表 TLB（相联存储）</text>
        <rect v-for="(e, i) in cur.tlb" :key="'t'+i" x="262" :y="40 + i * 18" width="150" height="16" rx="3" :fill="e.page === cur.P ? '#dcf3e7' : '#f7f9fc'" :stroke="e.page === cur.P ? '#22a06b' : '#eef1f6'" />
        <text v-for="(e, i) in cur.tlb" :key="'tt'+i" x="268" :y="52 + i * 18" font-size="10" :fill="e.page === cur.P ? '#176b48' : '#5a6474'">页 {{ e.page }} → 块 {{ e.block }}</text>
        <text x="262" y="132" font-size="11" font-weight="700" :fill="cur.tlbHit ? '#22a06b' : '#e05252'">{{ cur.tlbHit ? '✓ TLB 命中，不访主存页表' : '✗ TLB 未命中，需访主存页表' }}</text>
        <!-- ③ 主存页表：缺页时会追加一行（最多 7 行），行距按文字实际包围盒 14px 预留 -->
        <rect x="448" y="14" width="198" height="122" rx="8" :fill="cur.stage === 'pt' ? '#eef3ff' : '#fff'" :stroke="cur.stage === 'pt' ? '#3b6ef6' : '#dfe4ec'" stroke-width="1.6" />
        <text x="458" y="32" font-size="12" font-weight="700" fill="#1f2733">③ 主存页表（页号→块号|有效位）</text>
        <rect v-for="(e, i) in cur.pt" :key="'p'+i" x="458" :y="37 + i * 14" width="178" height="14" :fill="e.page === cur.P ? '#fff3e0' : 'none'" />
        <text v-for="(e, i) in cur.pt" :key="'pt'+i" x="464" :y="47 + i * 14" font-size="10" :fill="e.valid ? '#1f2733' : '#e05252'">{{ e.page }} → 块 {{ e.valid ? e.block : '—' }} | 有效位 {{ e.valid ? 1 : 0 }}</text>
        <!-- 箭头 -->
        <line x1="226" y1="70" x2="250" y2="70" :stroke="cur.stage === 'tlb' ? '#3b6ef6' : '#c8d3e6'" stroke-width="2" marker-end="url(#pg-a)" />
        <line x1="424" y1="70" x2="446" y2="70" :stroke="cur.stage === 'pt' ? '#3b6ef6' : '#c8d3e6'" stroke-width="2" marker-end="url(#pg-a)" />
        <polyline points="547,136 547,144 120,144 120,152" fill="none" :stroke="cur.stage === 'pa' ? '#3b6ef6' : '#c8d3e6'" stroke-width="2" marker-end="url(#pg-a)" />
        <!-- ④ 物理地址 -->
        <rect x="14" y="152" width="212" height="72" rx="8" :fill="cur.stage === 'pa' ? '#f2ecff' : '#fff'" :stroke="cur.stage === 'pa' ? '#8b5cf6' : '#dfe4ec'" stroke-width="1.6" />
        <text x="24" y="170" font-size="12" font-weight="700" fill="#1f2733">④ 物理地址</text>
        <text x="24" y="187" font-size="11" fill="#5a6474">块号 {{ cur.block < 0 ? '—' : cur.block }} × {{ cur.L }} + {{ cur.d }} = <tspan font-weight="700" fill="#8b5cf6">{{ cur.pa < 0 ? '—' : cur.pa }}</tspan></text>
        <rect v-for="(c, i) in paBits.blk" :key="'bp'+i" :x="24 + i * paCw" y="192" width="10" height="17" rx="2" fill="#f2ecff" stroke="#d6ccf7" />
        <text v-for="(c, i) in paBits.blk" :key="'bt'+i" :x="29 + i * paCw" y="205" font-size="10" fill="#8b5cf6">{{ c }}</text>
        <rect v-for="(c, i) in paBits.off" :key="'bo'+i" :x="24 + (paBits.blk.length + i) * paCw" y="192" width="10" height="17" rx="2" fill="#fff3e0" stroke="#f5d6a8" />
        <text v-for="(c, i) in paBits.off" :key="'bot'+i" :x="29 + (paBits.blk.length + i) * paCw" y="205" font-size="10" fill="#a5701a">{{ c }}</text>
        <!-- 缺页中断处理流程：4 步横向排成一行（纵向排第 3、4 步会掉出画布被裁） -->
        <rect x="252" y="152" width="394" height="72" rx="8" :fill="cur.fault ? '#fdeaea' : '#fff'" :stroke="cur.stage === 'fault' ? '#e05252' : '#dfe4ec'" stroke-width="1.6" />
        <text x="262" y="170" font-size="12" font-weight="700" :fill="cur.fault ? '#a32c2c' : '#8b95a3'">缺页中断处理程序（{{ cur.fault ? '本次已触发' : '本次未触发' }}）</text>
        <rect v-for="(s, i) in faultSteps" :key="'f'+i" :x="262 + i * 94" y="180" width="88" height="20" rx="4" :fill="cur.fault && cur.faultStep >= i ? '#fdeaea' : '#f7f9fc'" :stroke="cur.fault && cur.faultStep >= i ? '#e05252' : '#eef1f6'" />
        <text v-for="(s, i) in faultSteps" :key="'ft'+i" :x="306 + i * 94" y="194" text-anchor="middle" font-size="10" :fill="cur.fault && cur.faultStep >= i ? '#a32c2c' : '#8b95a3'">{{ s }}{{ i < 3 ? ' ▸' : '' }}</text>
        <text x="262" y="214" font-size="10" fill="#8b95a3">缺页中断后进程阻塞，调页完成再唤醒并重新执行该指令</text>
        <defs><marker id="pg-a" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 z" fill="#c8d3e6" /></marker></defs>
      </svg>
      <div class="pg-panel">
        <div class="info-row"><span>页号 P（A div L）</span><b style="color:var(--brand)">{{ cur.P }}</b></div>
        <div class="info-row"><span>页内偏移 d（A mod L）</span><b style="color:var(--warning)">{{ cur.d }}</b></div>
        <div class="info-row"><span>物理块号 b</span><b :style="{ color: cur.block < 0 ? '#e05252' : '#8b5cf6' }">{{ cur.block < 0 ? '缺页' : cur.block }}</b></div>
        <div class="info-row"><span>物理地址</span><b>{{ cur.pa < 0 ? '—' : cur.pa }}</b></div>
        <div class="info-row"><span>本次访存次数</span><b>{{ cur.accesses }}</b></div>
        <div class="info-row"><span>快表命中</span><el-tag size="small" :type="cur.tlbHit ? 'success' : 'warning'">{{ cur.tlbHit ? '命中' : '未命中' }}</el-tag></div>
        <p class="tip small muted">考点：① 分页的作业地址空间是一维的，地址变换由 MMU 硬件自动完成；② 页面大小必须是 2 的整数次幂，使"除 / 取模"退化为"截取高低位"；③ 快表命中可省去一次主存访存，未命中则先访页表再访目标单元；④ 缺页中断属内中断，一条指令执行期间可能产生多次缺页；⑤ 页表始址与页表长度存放在页表寄存器 PTR 中，进程切换时由内核改写 PTR。</p>
      </div>
    </div>
    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> 页号 / 当前变换阶段</span>
      <span><i class="dot" style="background:#e8a13a"></i> 页内偏移（逻辑与物理完全相同）</span>
      <span><i class="dot" style="background:#8b5cf6"></i> 物理块号</span>
      <span><i class="dot" style="background:#22a06b"></i> 快表命中 / 有效位 = 1</span>
      <span><i class="dot" style="background:#e05252"></i> 缺页中断（有效位 = 0）</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'
const W = 660
const H = 238
// 页表：页 3 的有效位为 0，用于演示缺页中断；快表初始只装 2 项
const PT = [
  { page: 0, block: 5, valid: true }, { page: 1, block: 8, valid: true }, { page: 2, block: 3, valid: true },
  { page: 3, block: -1, valid: false }, { page: 4, block: 10, valid: true }, { page: 5, block: 1, valid: true }]
const TLB_INIT = [{ page: 0, block: 5 }, { page: 4, block: 10 }]
const faultSteps = ['保护现场', '找空闲块', '磁盘调页', '改页表恢复']
const pageSize = ref(1024)
const addrText = ref('2500')
const addr = ref(2500)
const bin = (v, n) => (v >>> 0).toString(2).padStart(n, '0').slice(-n)
const steps = computed(() => {
  const out = []
  const L = pageSize.value
  const b = Math.round(Math.log2(L))
  const A = addr.value
  const P = Math.floor(A / L)
  const d = A % L
  const tlb = TLB_INIT.map(e => ({ ...e }))
  const pt = PT.map(e => ({ ...e }))
  let block = -1, pa = -1, accesses = 0, fault = false, tlbHit = false, faultStep = -1
  function snap(desc, extra = {}) {
    out.push({ A, L, b, P, d, block, pa, accesses, fault, tlbHit, faultStep, tlb: tlb.map(e => ({ ...e })), pt: pt.map(e => ({ ...e })), stage: 'split', ...extra, desc })
  }
  // 初始步：还没做拆分，P / d 必须留空，否则下一步「① 拆分逻辑地址」画面毫无变化
  snap(`初始：逻辑地址 A = ${A}，页面大小 L = ${L} B = 2^${b} → 地址结构为「页号 ${16 - b} 位 | 页内偏移 ${b} 位」`, { stage: 'init', P: -1, d: -1 })
  snap(`① 拆分逻辑地址：页号 P = A div L = ${P}，页内偏移 d = A mod L = ${d}（硬件直接按位截取，无需真正做除法）`, { stage: 'split' })
  const hit = tlb.find(e => e.page === P)
  if (hit) {
    tlbHit = true; block = hit.block
    snap(`② 用页号 ${P} 并行比较快表所有项 → 命中！直接读出物理块号 ${block}，省去一次访问主存页表的时间`, { stage: 'tlb' })
  } else {
    accesses++
    snap(`② 用页号 ${P} 并行比较快表 → 未命中，必须访问主存中的页表（本次第 ${accesses} 次访存）`, { stage: 'tlb' })
    const e = pt.find(x => x.page === P)
    if (e && e.valid) {
      block = e.block
      if (tlb.length >= 4) tlb.shift()
      tlb.push({ page: P, block: e.block })
      snap(`③ 查页表：页表始址(PTR) + 页号 ${P} × 页表项长度 定位到页表项，有效位 = 1 → 物理块号 ${block}；同时把该项写入快表（快表满则按置换策略淘汰）`, { stage: 'pt' })
    } else {
      fault = true
      snap(`③ 查页表：页 ${P} 的有效位 = 0 → 该页尚未调入内存，MMU 触发缺页中断，CPU 转入操作系统内核`, { stage: 'fault', faultStep: 0 })
      const nb = 6
      faultStep = 1
      snap(`④ 缺页中断处理 1/4：保护被中断进程的 CPU 现场，进程由运行态变为阻塞态，OS 查得该页在外存的位置`, { stage: 'fault', faultStep: 1 })
      faultStep = 2
      snap(`⑤ 缺页中断处理 2/4：为缺页分配一个空闲物理块（本例分配 ${nb} 号块）；若无空闲块，则先按页面置换算法（如 LRU）淘汰一页，被淘汰页若已修改还需写回外存`, { stage: 'fault', faultStep: 2 })
      const ent = e || { page: P, block: -1, valid: false }
      if (!e) pt.push(ent)
      ent.block = nb; ent.valid = true
      faultStep = 3
      accesses++
      snap(`⑥ 缺页中断处理 3/4：启动磁盘 I/O 把该页读入 ${nb} 号物理块，页表项改为「有效位 = 1，块号 = ${nb}」，同时写入快表`, { stage: 'pt', faultStep: 3 })
      if (tlb.length >= 4) tlb.shift()
      tlb.push({ page: P, block: nb })
      block = nb
      snap(`⑦ 缺页中断处理 4/4：恢复现场，被阻塞进程转为就绪，重新执行刚才被中断的那条指令（重新做一次地址变换）`, { stage: 'tlb', faultStep: 3 })
    }
  }
  pa = block * L + d
  snap(`⑧ 拼装物理地址：物理地址 = 块号 × 页面大小 + 页内偏移 = ${block} × ${L} + ${d} = ${pa}。可见页内偏移原样照搬，只有页号被替换成块号`, { stage: 'pa' })
  accesses++
  snap(`⑨ 用物理地址 ${pa} 访问内存单元取到操作数（第 ${accesses} 次访存）。本次共访存 ${accesses} 次${hit ? '（快表命中，最理想只需 1 次）' : '（含 1 次查页表）'}`, { stage: 'mem' })
  return out
})
const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
/** 逻辑地址是否已拆出页号与页内偏移（初始步还没有） */
const splitDone = computed(() => cur.value.stage !== 'init' && cur.value.P >= 0)
const statusText = computed(() => cur.value.desc)
const laBits = computed(() => {
  const s = bin(cur.value.A, 16)
  const n = 16 - cur.value.b
  return { pn: s.slice(0, n).split(''), off: s.slice(n).split('') }
})
const paBits = computed(() => cur.value.block < 0 ? { blk: [], off: [] } : { blk: bin(cur.value.block, 5).split(''), off: bin(cur.value.d, cur.value.b).split('') })
const paCw = computed(() => Math.min(11.4, 190 / Math.max(1, 5 + cur.value.b)))
// 输入兜底：地址必须 ≥0 且落在 16 位逻辑地址空间内
function applyAddr() {
  const v = Number(addrText.value)
  addr.value = Number.isFinite(v) ? Math.min(Math.max(0, Math.round(v)), 65535) : 2500
  addrText.value = String(addr.value)
  player.reset()
}
function resetAll() { pageSize.value = 1024; addrText.value = '2500'; addr.value = 2500; player.reset() }
</script>

<style scoped>
.pg-wrap { display: flex; gap: 18px; align-items: flex-start; flex-wrap: wrap; }
.pg-svg { background: #fbfcff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.pg-panel { flex: 1; min-width: 260px; }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.tip { margin-top: 10px; line-height: 1.8; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
