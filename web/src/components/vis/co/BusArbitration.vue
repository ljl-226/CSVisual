<template>
  <VisFrame title="总线仲裁与传输 · 链式 / 计数查询 / 独立请求" desc="多个主设备争用总线时，由总线控制器按仲裁方式把总线使用权授予一个设备，随后经历申请—寻址—传输—结束四个阶段" :player="player" :status-text="statusText" back-to="/knowledge/53">
    <template #extra>
      <el-select v-model="arb" size="small" style="width:150px" @change="player.reset()">
        <el-option value="chain" label="链式查询" />
        <el-option value="counter" label="计数器定时查询" />
        <el-option value="indep" label="独立请求" />
      </el-select>
      <el-select v-model="reqKey" size="small" style="width:130px" @change="player.reset()">
        <el-option value="13" label="设备1 + 设备3" />
        <el-option value="02" label="设备0 + 设备2" />
        <el-option value="123" label="设备1+2+3" />
      </el-select>
      <el-button size="small" plain @click="player.reset()">重置</el-button>
    </template>
    <div class="ba-wrap">
      <svg :width="W" :height="H" class="ba-svg">
        <!-- 总线控制器 -->
        <rect x="14" y="14" width="632" height="46" rx="8" fill="#eef3ff" stroke="#3b6ef6" stroke-width="1.6" />
        <text x="26" y="34" font-size="12" font-weight="700" fill="#3b6ef6">总线控制器（集中式仲裁）</text>
        <text x="26" y="50" font-size="10.5" fill="#5a6474">{{ arbNote }}</text>
        <text x="630" y="34" font-size="11" text-anchor="end" :fill="cur.bs >= 0 ? '#e05252' : '#22a06b'">BS 总线忙 = {{ cur.bs >= 0 ? 1 : 0 }}</text>
        <text x="630" y="50" font-size="11" text-anchor="end" fill="#5a6474">当前主设备：{{ cur.grantee >= 0 ? '设备' + cur.grantee : '无' }}</text>

        <!-- 三条信号线 -->
        <g v-for="(l, k) in lanes" :key="l.t">
          <line x1="30" :y1="l.y" x2="634" :y2="l.y" stroke="#dfe4ec" stroke-width="2" />
          <text x="632" :y="l.y - 6" font-size="10" text-anchor="end" fill="#8b95a3">{{ l.t }}</text>
          <line v-for="i in 4" :key="'s' + i"
                :x1="devX(i - 1)" :y1="l.y" :x2="devX(i - 1)" y2="150"
                :stroke="stubColor(k, i - 1)" stroke-width="2" />
        </g>
        <!-- 链式查询：BG 串行下传箭头 -->
        <g v-if="arb === 'chain'">
          <text v-for="i in 3" :key="'g' + i" :x="(devX(i - 1) + devX(i)) / 2" y="108" text-anchor="middle"
                font-size="12" :fill="cur.chainTo >= i ? '#22a06b' : '#c8d3e6'">▶</text>
        </g>
        <!-- 计数器：地址线上的计数值 -->
        <g v-if="arb === 'counter'">
          <rect x="300" y="92" width="60" height="24" rx="4" fill="#fff3e0" stroke="#e8a13a" />
          <text x="330" y="108" text-anchor="middle" font-size="12" font-weight="700" fill="#a5701a">地址 {{ cur.counterAt < 0 ? '—' : cur.counterAt }}</text>
        </g>

        <!-- 设备 -->
        <g v-for="i in 4" :key="'d' + i">
          <rect :x="14 + (i - 1) * 158" y="150" width="148" height="62" rx="8"
                :fill="cur.grantee === i - 1 ? '#dcf3e7' : '#fff'"
                :stroke="cur.grantee === i - 1 ? '#22a06b' : (cur.dev[i - 1].br ? '#e8a13a' : '#dfe4ec')" stroke-width="1.8" />
          <text :x="88 + (i - 1) * 158" y="170" text-anchor="middle" font-size="12" font-weight="700" fill="#1f2733">设备 {{ i - 1 }}</text>
          <text :x="30 + (i - 1) * 158" y="188" font-size="10.5" :fill="cur.dev[i - 1].br ? '#e05252' : '#b6bfcc'">BR{{ i - 1 }} = {{ cur.dev[i - 1].br }}</text>
          <text :x="98 + (i - 1) * 158" y="188" font-size="10.5" :fill="cur.dev[i - 1].bg ? '#22a06b' : '#b6bfcc'">BG{{ i - 1 }} = {{ cur.dev[i - 1].bg }}</text>
          <text :x="88 + (i - 1) * 158" y="203" text-anchor="middle" font-size="10" :fill="cur.grantee === i - 1 ? '#176b48' : '#8b95a3'">
            {{ cur.grantee === i - 1 ? '占用总线（主设备）' : (cur.dev[i - 1].br ? '等待授权' : '空闲') }}
          </text>
        </g>

        <!-- 传输四阶段 -->
        <text x="14" y="234" font-size="12" font-weight="700" fill="#1f2733">总线传输的四个阶段</text>
        <g v-for="(p, i) in PHASES" :key="p">
          <rect :x="14 + i * 160" y="242" width="148" height="30" rx="6"
                :fill="cur.phaseIdx === i ? '#e6eeff' : '#f7f9fc'" :stroke="cur.phaseIdx === i ? '#3b6ef6' : '#eef1f6'" />
          <text :x="88 + i * 160" y="262" text-anchor="middle" font-size="11.5" :fill="cur.phaseIdx === i ? '#3b6ef6' : '#8b95a3'">{{ i + 1 }}. {{ p }}</text>
        </g>
        <text x="14" y="290" font-size="10.5" fill="#8b95a3">总线上传送：{{ cur.busAddr || '—' }}　{{ cur.busData || '' }}</text>
      </svg>
      <div class="ba-panel">
        <div class="info-row"><span>仲裁方式</span><b style="color:var(--brand)">{{ arbName }}</b></div>
        <div class="info-row"><span>提出请求的设备</span><b style="color:var(--warning)">{{ cur.reqSet.map(i => '设备' + i).join('、') }}</b></div>
        <div class="info-row"><span>获得总线的主设备</span><b style="color:var(--success)">{{ cur.grantee >= 0 ? '设备' + cur.grantee : '—' }}</b></div>
        <div class="info-row"><span>当前阶段</span><b>{{ cur.phaseIdx >= 0 ? PHASES[cur.phaseIdx] : '总线空闲' }}</b></div>
        <el-divider />
        <div class="tbl">
          <div class="tbl-head"><span>方式</span><span>控制线数</span><span>优先级</span></div>
          <div v-for="c in COMPARE" :key="c.n" class="tbl-row" :class="{ active: c.k === arb }">
            <span>{{ c.n }}</span><span>{{ c.w }}</span><span>{{ c.p }}</span>
          </div>
        </div>
        <p class="tip small muted">
          考点：① 链式查询只需 <b>3 条</b>线（BS/BR/BG），但优先级由物理位置固定，且对电路故障敏感（前面设备坏掉则后面全部失效）；
          ② 计数器定时查询需 <b>log₂n</b> 条设备地址线，改计数起始值即可改变优先级；
          ③ 独立请求需 <b>2n</b> 条线，响应最快且优先级可灵活设定，代价是线数最多。
        </p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#e8a13a"></i> BR 总线请求线（有效）</span>
      <span><i class="dot" style="background:#22a06b"></i> BG 总线同意线（有效）</span>
      <span><i class="dot" style="background:#e05252"></i> BS 总线忙 / 正在传输</span> <span><i class="dot" style="background:#3b6ef6"></i> 当前所处传输阶段</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'
const W = 660
const H = 300
const PHASES = ['申请（仲裁）', '寻址', '传输', '结束']
const COMPARE = [
  { k: 'chain', n: '链式查询', w: '3 条（BS/BR/BG）', p: '离控制器近者优先' },
  { k: 'counter', n: '计数器查询', w: 'log₂n + 2 条', p: '计数起始值可设' },
  { k: 'indep', n: '独立请求', w: '2n 条', p: '排队器灵活设定' }
]
const REQ_PRESETS = { '13': [1, 3], '02': [0, 2], '123': [1, 2, 3] }
const arb = ref('chain')
const reqKey = ref('13')
const devX = i => 14 + i * 158 + 74
const lanes = [{ t: 'BR 总线请求线', y: 78 }, { t: 'BG 总线同意 / 设备地址线', y: 104 }, { t: 'BS 总线忙线', y: 130 }]
const arbName = computed(() => COMPARE.find(c => c.k === arb.value).n)
const arbNote = computed(() => ({
  chain: 'BG 信号从控制器出发，沿设备链串行下传，遇到第一个有请求的设备就被截获',
  counter: '控制器用计数器在设备地址线上依次送出地址，设备把自己的编号与地址比较，相符且有请求者响应',
  indep: '每台设备都有独立的 BRi 与 BGi 线，控制器内的排队器按预设优先级直接选中一台设备'
}[arb.value]))
const steps = computed(() => {
  const out = []
  const reqSet = [...REQ_PRESETS[reqKey.value]]
  const dev = Array.from({ length: 4 }, () => ({ br: 0, bg: 0 }))
  let bs = -1, grantee = -1, phaseIdx = -1, chainTo = -1, counterAt = -1
  function snap(desc, extra = {}) {
    out.push({ dev: dev.map(d => ({ ...d })), bs, grantee, phaseIdx, reqSet: [...reqSet], arb: arb.value, chainTo, counterAt, busAddr: '', busData: '', ...extra, desc })
  }
  snap('初始：总线空闲（BS = 0），4 台设备均无总线请求')
  reqSet.forEach(i => { dev[i].br = 1 })
  snap(`① 申请阶段：设备 ${reqSet.join('、')} 同时置各自的 BR = 1，向总线控制器发出总线请求；控制器在 BS = 0（总线空闲）时才启动仲裁`, { phaseIdx: 0 })
  // 仲裁：三种方式决定优先级与响应过程
  let win = -1
  if (arb.value === 'chain') {
    for (let i = 0; i < 4; i++) {
      chainTo = i
      if (dev[i].br) {
        win = i; dev[i].bg = 1; bs = i; grantee = i
        snap(`② 仲裁（链式查询）：BG 沿设备链传到设备 ${i}，它有请求 → 截获 BG 不再下传，置 BS = 1、撤消 BR，成为主设备`, { phaseIdx: 0, grantee: i })
        break
      }
      snap(`② 仲裁（链式查询）：BG 传到设备 ${i}，它无请求 → BG 继续往下一台设备传递`, { phaseIdx: 0 })
    }
  } else if (arb.value === 'counter') {
    for (let i = 0; i < 4; i++) {
      counterAt = i
      if (dev[i].br) {
        win = i; dev[i].bg = 1; bs = i; grantee = i
        snap(`② 仲裁（计数器定时查询）：计数器送出地址 ${i}，设备 ${i} 比较相符且有请求 → 响应，停止计数，成为主设备`, { phaseIdx: 0, grantee: i })
        break
      }
      snap(`② 仲裁（计数器定时查询）：计数器送出地址 ${i}，设备 ${i} 无请求 → 计数器加 1，继续查询下一台`, { phaseIdx: 0 })
    }
  } else {
    win = reqSet[reqSet.length - 1]   // 排队器本例设为"设备编号大者优先"
    snap(`② 仲裁（独立请求）：4 条 BRi 同时送入排队器，排队器按预设优先级（编号大者优先）在 {${reqSet.join('、')}} 中选中设备 ${win}，置 BG${win} = 1 —— 无需逐台查询，响应速度最快`, { phaseIdx: 0 })
    dev[win].bg = 1; bs = win; grantee = win
    snap(`② 仲裁（独立请求）：设备 ${win} 收到 BG${win}，撤消 BR${win} 并置 BS = 1，取得总线使用权`, { phaseIdx: 0, grantee: win })
  }
  // 传输四阶段（连续为每台请求设备服务）
  let addr = 0x20
  const queue = [...reqSet].sort((a, b) => (arb.value === 'indep' ? b - a : a - b))
  queue.forEach((k, qi) => {
    if (qi > 0) snap(`控制器重新仲裁：设备 ${k} 仍在等待 → 按${arb.value === 'indep' ? '排队器优先级' : (arb.value === 'chain' ? '链式次序' : '计数次序')}把总线授予它`, { phaseIdx: 0, grantee: k, chainTo: k, counterAt: k })
    bs = k; grantee = k; dev[k].bg = 1
    snap(`③ 寻址阶段：主设备 ${k} 把从设备地址 ${addr.toString(16).toUpperCase()}H 与读命令送到地址总线和控制总线，所有从设备识别地址`, { phaseIdx: 1, grantee: k, busAddr: `地址 ${addr.toString(16).toUpperCase()}H + 读命令` })
    const data = 'D' + (k + 1) + 'H'
    snap(`④ 传输阶段：主从设备经数据总线传送数据 ${data}；此时 BS = 1，其它设备即使有请求也只能等待`, { phaseIdx: 2, grantee: k, busAddr: `地址 ${addr.toString(16).toUpperCase()}H`, busData: `数据 ${data}` })
    dev[k].br = 0; dev[k].bg = 0
    snap(`⑤ 结束阶段：主设备 ${k} 撤消总线请求与相关信息，释放 BS，总线归还控制器；控制器再为剩下的请求设备重新仲裁`, { phaseIdx: 3, grantee: k })
    bs = -1; grantee = -1; addr += 0x10
  })
  snap(`全部请求处理完毕：总线重新回到空闲状态（BS = 0）。集中式仲裁把"谁用总线"的决定权交给总线控制器，避免多个主设备同时驱动总线造成冲突`, { phaseIdx: -1 })
  return out
})
const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)
// 竖线（设备与信号线的连接）颜色：BR 有请求为橙、BG 被授权为绿、BS 为红
function stubColor(k, i) {
  const d = cur.value.dev[i]
  if (k === 0) return d.br ? '#e8a13a' : '#eef1f6'
  if (k === 1) {
    if (cur.value.arb === 'chain') return cur.value.chainTo >= i ? '#22a06b' : '#eef1f6'
    if (cur.value.arb === 'counter') return cur.value.counterAt === i ? '#22a06b' : '#eef1f6'
    return d.bg ? '#22a06b' : '#eef1f6'
  }
  return cur.value.bs >= 0 && cur.value.grantee === i ? '#e05252' : '#eef1f6'
}
</script>

<style scoped>
.ba-wrap { display: flex; gap: 18px; align-items: flex-start; flex-wrap: wrap; }
.ba-svg { background: #fbfcff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.ba-panel { flex: 1; min-width: 280px; }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.tbl { font-size: 12px; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
.tbl-head { display: grid; grid-template-columns: 1.1fr 1.3fr 1.3fr; background: #f6f8fb; padding: 7px 10px; font-weight: 600; }
.tbl-row { display: grid; grid-template-columns: 1.1fr 1.3fr 1.3fr; padding: 6px 10px; border-top: 1px solid #f0f2f6; }
.tbl-row.active { background: var(--brand-light); color: var(--brand); font-weight: 600; }
.tip { margin-top: 10px; line-height: 1.8; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
