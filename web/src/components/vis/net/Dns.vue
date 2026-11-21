<template>
  <VisFrame
    :title="isRecursive ? 'DNS 域名解析 · 递归查询' : 'DNS 域名解析 · 迭代查询'"
    :desc="isRecursive ? '每一级服务器受托继续查询，结果沿原路逐级返回' : '本地服务器自己依次问：根 → 顶级域 .com → 权威服务器，每次拿到下一步的地址'"
    :player="player" :status-text="statusText" back-to="/knowledge/42"
  >
    <template #extra>
      <el-select v-model="mode" size="small" style="width:120px">
        <el-option value="iterative" label="迭代查询" />
        <el-option value="recursive" label="递归查询" />
      </el-select>
      <el-button size="small" plain @click="player.reset()">重播</el-button>
    </template>

    <div class="dns-wrap">
      <svg width="630" height="360" class="dns-svg">
        <defs>
          <marker v-for="mk in markers" :key="mk.id" :id="mk.id" markerWidth="9" markerHeight="9" refX="8" refY="3" orient="auto">
            <path d="M0,0 L8,3 L0,6 z" :fill="mk.color" />
          </marker>
        </defs>

        <!-- 服务器节点 -->
        <g v-for="(n, i) in nodes" :key="'n' + i">
          <rect :x="n.x" :y="n.y" :width="n.w" height="58" rx="8"
            :fill="i === curNode ? '#eef3ff' : '#fff'" :stroke="i === curNode ? '#3b6ef6' : '#c8d3e6'"
            :stroke-width="i === curNode ? 3 : 1.5" />
          <text :x="n.x + n.w / 2" :y="n.y + 24" text-anchor="middle" font-size="13" font-weight="600" fill="#1f2733">{{ n.name }}</text>
          <text :x="n.x + n.w / 2" :y="n.y + 42" text-anchor="middle" font-size="11" fill="#8b95a3">{{ n.sub }}</text>
          <text v-if="cacheCount[i]" :x="n.x + n.w / 2" :y="n.y + 72" text-anchor="middle" font-size="11" fill="#176b48">缓存 {{ cacheCount[i] }} 条</text>
        </g>

        <!-- 查询报文（历史报文淡化，最后一条高亮并标注） -->
        <g v-for="m in visible" :key="'m' + m.i">
          <line :x1="m.x1" :y1="m.y1" :x2="m.x2" :y2="m.y2" :stroke="m.color" :stroke-width="m.last ? 2.6 : 1.6"
            :opacity="m.opacity" :marker-end="`url(#${m.marker})`" />
          <g v-if="m.last">
            <rect :x="m.lx" :y="m.ly - 14" :width="m.w" height="20" rx="4" fill="#fff" :stroke="m.color" stroke-width="1.1" />
            <text :x="m.lx + m.w / 2" :y="m.ly" text-anchor="middle" font-size="11" :fill="m.color" font-weight="600">{{ m.label }}</text>
          </g>
        </g>
      </svg>

      <div class="dns-panel">
        <div class="info-row"><span>待解析域名</span><b>y.abc.com</b></div>
        <div class="info-row"><span>查询方式</span><b style="color:var(--brand)">{{ isRecursive ? '递归查询' : '迭代查询' }}</b></div>
        <div class="info-row"><span>当前交互方</span><b>{{ activeName }}</b></div>
        <div class="info-row"><span>报文/回答类型</span><b>{{ lastType }}</b></div>
        <div class="info-row"><span>查询类型 · TTL</span><b>A 记录 · {{ ttl }}</b></div>
        <div class="info-row"><span>解析结果</span><b :style="{ color: resultIp === '—' ? 'var(--text-2)' : 'var(--success)' }">{{ resultIp }}</b></div>
        <el-divider />
        <div class="panel-title">各级缓存（写入顺序）</div>
        <div class="cache-box">
          <div v-for="(c, i) in cur.cache" :key="i" class="cache-item">
            <el-tag size="small" type="success" effect="plain">#{{ i + 1 }}</el-tag> {{ c.nodeName }}：{{ c.text }}
          </div>
          <span v-if="!cur.cache.length" class="small muted">尚无缓存记录</span>
        </div>
        <div class="tip small muted">
          主机 → 本地域名服务器：<b>递归查询</b>；本地域名服务器 → 各级服务器：通常为<b>迭代查询</b>（谢希仁《计算机网络》图 6-4）。
        </div>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> 主机 ⇄ 本地服务器</span>
      <span><i class="dot" style="background:#8b5cf6"></i> 查询报文</span>
      <span><i class="dot" style="background:#22a06b"></i> 引用 / 回送</span>
      <span><i class="dot" style="background:#e8a13a"></i> 权威回答</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

const mode = ref('iterative')
const isRecursive = computed(() => mode.value === 'recursive')
const RESULT = '153.17.239.5'

// 五个参与者：主机 → 本地域名服务器 → 根 → 顶级域(.com) → 权威服务器(abc.com)
const nodes = [
  { name: '主机 m.xyz.com', sub: 'DNS 客户进程', x: 16, y: 146, w: 152, h: 58 },
  { name: '本地域名服务器', sub: 'dns.xyz.com', x: 196, y: 146, w: 152, h: 58 },
  { name: '根域名服务器', sub: 'root（集群任播）', x: 434, y: 26, w: 180, h: 58 },
  { name: '顶级域服务器', sub: 'dns.com（负责 .com）', x: 434, y: 146, w: 180, h: 58 },
  { name: '权威域名服务器', sub: 'dns.abc.com', x: 434, y: 266, w: 180, h: 58 }
]
const markers = [
  { id: 'dns-blue', color: '#3b6ef6' }, { id: 'dns-purple', color: '#8b5cf6' },
  { id: 'dns-green', color: '#22a06b' }, { id: 'dns-orange', color: '#e8a13a' }
]

// 迭代查询：本地服务器一级一级地问，每次只拿到「下一步该问谁」
const ITER_MSGS = [
  { from: 0, to: 1, marker: 'dns-blue', color: '#3b6ef6', type: '递归查询（委托本地服务器）', label: '递归查询 y.abc.com 的 IP 地址' },
  { from: 1, to: 2, marker: 'dns-purple', color: '#8b5cf6', type: '查询报文', label: '向根服务器查询 y.abc.com' },
  { from: 2, to: 1, marker: 'dns-green', color: '#22a06b', type: '引用回答 referral', label: '返回：去找顶级域 dns.com（195.10.10.10）', cache: { node: 1, text: '.com 顶级域服务器地址' } },
  { from: 1, to: 3, marker: 'dns-purple', color: '#8b5cf6', type: '查询报文', label: '向 dns.com 查询 y.abc.com' },
  { from: 3, to: 1, marker: 'dns-green', color: '#22a06b', type: '引用回答 referral', label: '返回：去找权威服务器 dns.abc.com（200.1.1.1）', cache: { node: 1, text: 'dns.abc.com 权威服务器地址' } },
  { from: 1, to: 4, marker: 'dns-purple', color: '#8b5cf6', type: '查询报文', label: '向 dns.abc.com 查询 y.abc.com' },
  { from: 4, to: 1, marker: 'dns-orange', color: '#e8a13a', type: '权威回答 + 授权回答', label: `权威回答：y.abc.com A = ${RESULT}，TTL = 600s`, cache: { node: 1, text: `y.abc.com A ${RESULT}` } },
  { from: 1, to: 0, marker: 'dns-blue', color: '#3b6ef6', type: '解析结果（非权威）', label: `把结果返回主机：${RESULT}`, cache: { node: 0, text: `y.abc.com A ${RESULT}` } }
]

// 递归查询：每级服务器受托继续往下查，答案沿原路径层层回送
const REC_MSGS = [
  { from: 0, to: 1, marker: 'dns-blue', color: '#3b6ef6', type: '递归查询', label: '请求本地服务器递归解析 y.abc.com' },
  { from: 1, to: 2, marker: 'dns-purple', color: '#8b5cf6', type: '递归委托', label: '本地服务器请求根继续递归查询' },
  { from: 2, to: 3, marker: 'dns-purple', color: '#8b5cf6', type: '递归委托', label: '根把请求继续交给 .com 顶级域服务器' },
  { from: 3, to: 4, marker: 'dns-purple', color: '#8b5cf6', type: '递归委托', label: '.com 把请求交给权威服务器 dns.abc.com' },
  { from: 4, to: 3, marker: 'dns-orange', color: '#e8a13a', type: '权威回答', label: `权威回答：y.abc.com A = ${RESULT}，TTL = 600s` },
  { from: 3, to: 2, marker: 'dns-green', color: '#22a06b', type: '递归回送', label: 'dns.com 沿原路返回结果' },
  { from: 2, to: 1, marker: 'dns-green', color: '#22a06b', type: '递归回送 + 写缓存', label: '根沿原路返回，本地服务器写入缓存', cache: { node: 1, text: `y.abc.com A ${RESULT}` } },
  { from: 1, to: 0, marker: 'dns-blue', color: '#3b6ef6', type: '解析结果 + 写缓存', label: `返回主机，主机写入本机缓存：${RESULT}`, cache: { node: 0, text: `y.abc.com A ${RESULT}` } }
]

const steps = computed(() => {
  const list = isRecursive.value ? REC_MSGS : ITER_MSGS
  const out = []
  let cache = []
  function snap(desc, extra = {}) {
    out.push({ upto: 0, cache: cache.map(c => ({ ...c })), curNode: -1, type: '—', resultIp: '—', ttl: '—', desc, ...extra })
  }

  snap('初始：主机要访问 y.abc.com，先查浏览器缓存 → hosts 文件 → 本机 DNS 缓存，均未命中', { curNode: 0 })
  // 只有拿到 A 记录才谈得上「解析出 IP」。曾经只要 m.cache 存在就显示最终结果，
  // 而根/TLD 返回的 referral 也带 cache（缓存的是下一级服务器地址，不是 A 记录），
  // 于是第 3 步还写着「引用回答」，「解析结果」一栏却已经把最终 IP 显示出来了。
  const isARecord = m => !!m.cache && /\sA\s/.test(String(m.cache.text || ''))
  list.forEach((m, i) => {
    const got = isARecord(m)
    snap(`第 ${i + 1} 次报文：${nodes[m.from].name} → ${nodes[m.to].name}，${m.type}`, {
      upto: i + 1, curNode: m.to, type: m.type, resultIp: got ? RESULT : '—', ttl: got ? '600s' : '—'
    })
    // 收到回答后按服务器/主机分别写入缓存，供下次命中直接返回
    if (m.cache) {
      cache.push({ ...m.cache, nodeName: nodes[m.cache.node].name })
      snap(`写入缓存：${nodes[m.cache.node].name} 记录「${m.cache.text}」，下次同样域名可直接命中（未过期则不再外出查询）`, {
        upto: i + 1, curNode: m.cache.node, type: '缓存写入', resultIp: got ? RESULT : '—', ttl: got ? '600s' : '—'
      })
    }
  })
  snap(`解析完成：y.abc.com = ${RESULT}，共发出 ${list.length} 次查询报文。域名服务器的层次结构保证名字全网唯一`, {
    upto: list.length, curNode: -1, type: '完成', resultIp: RESULT, ttl: '600s'
  })
  return out
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || steps.value[0])
const statusText = computed(() => cur.value.desc)

const curNode = computed(() => cur.value.curNode ?? -1)
const activeName = computed(() => (curNode.value >= 0 ? nodes[curNode.value].name : '—'))
const lastType = computed(() => cur.value.type || '—')
const resultIp = computed(() => cur.value.resultIp || '—')
const ttl = computed(() => cur.value.ttl || '—')

const cacheCount = computed(() => {
  const arr = [0, 0, 0, 0, 0]
  ;(cur.value.cache || []).forEach(c => { arr[c.node]++ })
  return arr
})

const DNS_W = 630
const DNS_H = 360

// 估算文本宽度：全角按 1 字宽，其余按 0.56 字宽
function textW(s, fs) {
  let w = 0
  for (const ch of String(s)) w += /[\u2e80-\u9fff\uff00-\uffef]/.test(ch) ? fs : fs * 0.56
  return Math.ceil(w)
}
function hitBox(a, b) {
  return !(a.x + a.w <= b.x || b.x + b.w <= a.x || a.y + a.h <= b.y || b.y + b.h <= a.y)
}
// 标签框避让：先水平夹进画布，再沿连线中点上下试探，直到不与任何服务器方框相交。
// 以前直接钉在中点上，长标签（如 250~546px）会整块压在服务器方框的文字上
function placeLabel(mx, my, w) {
  const h = 20
  const lx = Math.max(8, Math.min(DNS_W - w - 8, mx - w / 2))
  const box = { x: lx, y: 0, w, h }
  for (const d of [0, 26, -26, 52, -52, 78, -78, 104, -104, 130, -130]) {
    const ly = my + d
    box.y = ly - 14
    if (box.y < 6 || box.y + h > DNS_H - 6) continue
    if (!nodes.some(n => hitBox(box, n))) return { lx, ly }
  }
  return { lx, ly: my }
}

const visible = computed(() => {
  const list = (isRecursive.value ? REC_MSGS : ITER_MSGS).slice(0, cur.value.upto || 0)
  const cnt = {}
  return list.map((m, i) => {
    const key = Math.min(m.from, m.to) + '-' + Math.max(m.from, m.to)
    const lane = (cnt[key] = (cnt[key] || 0) + 1)
    const off = (lane - 1) * 13 - 6
    const a = nodes[m.from]
    const b = nodes[m.to]
    const mx = (a.x + a.w / 2 + b.x + b.w / 2) / 2
    const my = (a.y + a.h / 2 + b.y + b.h / 2) / 2
    const w = Math.max(140, textW(m.label, 11) + 18)
    const { lx, ly } = placeLabel(mx, my + off, w)
    return {
      ...m, i,
      x1: a.x + a.w / 2, y1: a.y + a.h / 2 + off,
      x2: b.x + b.w / 2, y2: b.y + b.h / 2 + off,
      lx, ly, w,
      last: i === list.length - 1, opacity: i === list.length - 1 ? 1 : 0.3
    }
  })
})
</script>

<style scoped>
.dns-wrap { display: flex; gap: 24px; align-items: flex-start; flex-wrap: wrap; }
.dns-svg { background: #fbfcff; border-radius: 8px; flex-shrink: 0; }
.dns-panel { flex: 1; min-width: 260px; }
.panel-title { font-size: 13px; font-weight: 600; margin-bottom: 6px; color: var(--text-2); }
.info-row { display: flex; justify-content: space-between; gap: 10px; padding: 4px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.cache-box { border: 1px dashed var(--border); border-radius: 8px; padding: 8px; min-height: 60px; background: #fbfcff; }
.cache-item { font-size: 12px; line-height: 2; color: var(--text-2); display: flex; align-items: center; gap: 6px; }
.tip { margin-top: 10px; line-height: 1.8; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
