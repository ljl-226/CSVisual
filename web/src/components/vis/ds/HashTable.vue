<template>
  <VisFrame title="哈希表 · 散列与冲突处理" desc="除留余数法定位桶位；冲突时用拉链法挂链表，或用开放地址法线性探测下一个空位" :player="player" :status-text="statusText" back-to="/knowledge/33">
    <template #extra>
      <el-select v-model="mSize" size="small" style="width:110px" @change="player.reset()">
        <el-option :value="7" label="表长 m = 7" />
        <el-option :value="11" label="表长 m = 11" />
        <el-option :value="13" label="表长 m = 13" />
      </el-select>
      <el-radio-group v-model="method" size="small" @change="player.reset()">
        <el-radio-button value="chain">拉链法</el-radio-button>
        <el-radio-button value="probe">线性探测</el-radio-button>
      </el-radio-group>
    </template>

    <!-- 自定义关键字序列：装填哪些 key 不再写死，学生想研究哪组冲突就配哪组 -->
    <div class="init-bar">
      <span class="init-label">关键字序列</span>
      <el-input v-model="keysInput" size="small" class="init-input"
        placeholder="如 19,14,23,1,68（逗号或空格分隔，最多 14 个）"
        @keyup.enter="applyKeys" />
      <el-button size="small" type="primary" plain @click="applyKeys">重新装填</el-button>
    </div>

    <div class="ht-wrap">
      <svg :width="W" :height="H" class="ht-svg">
        <!-- 表头 -->
        <text :x="12" :y="16" font-size="12" fill="#8b95a3">
          散列函数 H(key) = key mod {{ mSize }}　|　已插入 {{ cur.inserted }} / {{ keys.length }} 个关键字
        </text>

        <g v-for="(slot, i) in cur.slots" :key="'s'+i">
          <!-- 桶编号 -->
          <rect :x="idxX" :y="rowY(i)" :width="46" :height="rowH - 4" rx="5"
                :fill="cur.hl === i ? '#3b6ef6' : '#f6f8fb'" :stroke="cur.hl === i ? '#3b6ef6' : '#c8d3e6'" stroke-width="1.5" />
          <text :x="idxX + 23" :y="rowY(i) + (rowH - 4) / 2 + 4" text-anchor="middle" font-size="12"
                :fill="cur.hl === i ? '#fff' : '#5a6577'" font-weight="600">{{ i }}</text>

          <!-- 拉链法：链表结点 -->
          <template v-if="method === 'chain'">
            <g v-for="(k, j) in slot" :key="'c'+i+'-'+j">
              <line v-if="j > 0" :x1="nodeX(j) - 8" :y1="rowY(i) + (rowH - 4) / 2" :x2="nodeX(j)" :y2="rowY(i) + (rowH - 4) / 2"
                    stroke="#8b95a3" stroke-width="1.5" />
              <rect :x="nodeX(j)" :y="rowY(i)" :width="42" :height="rowH - 4" rx="5"
                    :fill="k === cur.key ? '#dcf3e7' : '#fff'" :stroke="k === cur.key ? '#22a06b' : '#c8d3e6'" stroke-width="1.5" />
              <text :x="nodeX(j) + 21" :y="rowY(i) + (rowH - 4) / 2 + 4" text-anchor="middle" font-size="12"
                    :fill="k === cur.key ? '#176b48' : '#1f2733'" font-weight="600">{{ k }}</text>
            </g>
            <text v-if="!slot.length" :x="nodeX(0)" :y="rowY(i) + (rowH - 4) / 2 + 4" font-size="11" fill="#c0c8d4">空</text>
          </template>

          <!-- 线性探测：单格 -->
          <template v-else>
            <rect :x="nodeX(0)" :y="rowY(i)" :width="46" :height="rowH - 4" rx="5"
                  :fill="slot.length ? (slot[0] === cur.key ? '#dcf3e7' : '#fff') : '#fbfcfe'"
                  :stroke="slot.length ? (slot[0] === cur.key ? '#22a06b' : '#c8d3e6') : '#e3e8f0'" stroke-width="1.5" />
            <text :x="nodeX(0) + 23" :y="rowY(i) + (rowH - 4) / 2 + 4" text-anchor="middle" font-size="12"
                  :fill="slot.length ? '#1f2733' : '#c0c8d4'">{{ slot.length ? slot[0] : '空' }}</text>
            <!-- 探测箭头 -->
            <text v-if="cur.probeIdx === i && !slot.length" :x="nodeX(0) + 56" :y="rowY(i) + (rowH - 4) / 2 + 4"
                  font-size="11" fill="#f2994a">← 探测到此空位</text>
          </template>
        </g>
      </svg>

      <div class="ht-panel">
        <div class="formula"><code>H(key) = key mod {{ mSize }}　　α（装填因子）= n / m</code></div>
        <el-divider />
        <div class="info-row"><span>当前关键字 key</span><b style="color:var(--brand)">{{ cur.key ?? '—' }}</b></div>
        <div class="info-row"><span>散列地址 H(key)</span><b>{{ cur.h ?? '—' }}</b></div>
        <div class="info-row"><span>是否发生冲突</span>
          <el-tag size="small" :type="cur.conflict ? 'danger' : 'success'">{{ cur.conflict ? '冲突' : '无冲突' }}</el-tag>
        </div>
        <div class="info-row" v-if="method === 'probe'"><span>本轮探测次数</span><b>{{ cur.probes ?? 0 }}</b></div>
        <div class="info-row"><span>已装填关键字 n</span><b>{{ cur.inserted }}</b></div>
        <div class="info-row"><span>装填因子 α</span><b>{{ (cur.inserted / mSize).toFixed(3) }}</b></div>
        <div class="info-row"><span>累计冲突次数</span><b style="color:#e05252">{{ totalConflict }}</b></div>
        <el-divider />
        <div class="tbl">
          <div class="tbl-head"><span>key</span><span>H(key)</span><span>冲突</span></div>
          <div v-for="(s, i) in player.steps.value" :key="i" class="tbl-row" :class="{ active: i === player.idx.value }" @click="player.seek(i)">
            <span>{{ s.key }}</span><span>{{ s.h }}</span>
            <span :style="{ color: s.conflict ? '#e05252' : '#22a06b' }">{{ s.conflict ? '是' : '否' }}</span>
          </div>
        </div>
        <p class="small muted tip">
          {{ method === 'chain'
            ? '拉链法：同义词挂在同一个桶的链表上，不会「抢占」别人的位置，删除方便；缺点是额外指针空间。'
            : '线性探测：冲突时向后逐个找空位，实现简单、缓存友好，但容易「聚集」，删除需做墓碑标记。' }}
          装填因子 α 越接近 1，冲突越频繁，实际应用中常保持 α ≤ 0.75 并适时扩容。
        </p>
      </div>
    </div>

    <template #legend>
      <span><i class="dot" style="background:#3b6ef6"></i> 当前散列到的桶</span>
      <span><i class="dot" style="background:#22a06b"></i> 刚插入的关键字</span>
      <span><i class="dot" style="background:#f2994a"></i> 探测位置</span>
    </template>
  </VisFrame>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import VisFrame from '../VisFrame.vue'
import { usePlayer } from '../usePlayer'

// 关键字序列由学生自己定 —— 以前 12 个 key 写死，想研究「换一组数会怎么冲突」只能干瞪眼。
const MAX_KEYS = 14
const keysInput = ref('19,14,23,1,68,20,84,27,55,11,10,79')
const keys = ref([19, 14, 23, 1, 68, 20, 84, 27, 55, 11, 10, 79])

function applyKeys() {
  const raw = String(keysInput.value || '')
  const vals = raw
    .split(/[,，、\s]+/)
    .map(s => s.trim())
    .filter(Boolean)
    .map(Number)
  if (!vals.length || vals.some(isNaN)) {
    ElMessage.warning('关键字要是数字，用逗号或空格分隔，例如 19,14,23')
    return
  }
  if (vals.length > MAX_KEYS) {
    ElMessage.warning(`关键字最多 ${MAX_KEYS} 个，再多表格就放不下了`)
    return
  }
  keys.value = vals
  player.reset()
  // 自动播一遍装填过程：一个 key 一个 key 散列进表
  player.play()
}

const mSize = ref(11)
const method = ref('chain')

const W = 560
const rowH = 27
const idxX = 24
const nodeX = j => 96 + j * 52
const H = computed(() => 30 + mSize.value * rowH + 10)
function rowY(i) { return 26 + i * rowH }

const steps = computed(() => {
  const m = mSize.value
  const slots = Array.from({ length: m }, () => [])
  const out = []
  for (const key of keys.value) {
    const h = key % m
    if (method.value === 'chain') {
      const conflict = slots[h].length > 0
      slots[h].push(key)
      out.push({
        key, h, conflict, hl: h, probeIdx: -1, probes: 1,
        slots: slots.map(s => [...s]), inserted: out.filter(s => s.conflict !== null).length + 1,
        desc: `插入 ${key}：H(${key}) = ${key} mod ${m} = ${h}${conflict ? `，桶 ${h} 已有元素，发生冲突 → 挂到链尾` : '，桶为空 → 直接放入'}`
      })
    } else {
      let pos = h
      let probes = 1
      let conflict = slots[h].length > 0
      while (slots[pos].length && probes <= m) {
        pos = (pos + 1) % m
        probes++
      }
      const full = slots[pos].length > 0
      if (!full) slots[pos].push(key)
      out.push({
        key, h, conflict, hl: h, probeIdx: pos, probes,
        slots: slots.map(s => [...s]), inserted: out.filter(s => s.h !== undefined).length + 1,
        desc: full
          ? `插入 ${key} 失败：表已满`
          : `插入 ${key}：H = ${h}${conflict ? `，位置被占 → 线性探测 ${probes} 次后落到 ${pos}` : '，位置为空 → 直接放入'}`
      })
    }
  }
  // 修正 inserted（按已成功插入的元素数计）
  let n = 0
  return out.map(s => { n++; return { ...s, inserted: n } })
})

const player = usePlayer(steps)
const cur = computed(() => player.current.value || { slots: [], key: null, h: null, hl: -1, probeIdx: -1, inserted: 0 })
const statusText = computed(() => cur.value.desc)
const totalConflict = computed(() => steps.value.filter(s => s.conflict).length)
</script>

<style scoped>
.ht-wrap { display: flex; gap: 18px; align-items: flex-start; flex-wrap: wrap; }

/* 自定义关键字工具行：跟画布放在一起，语义上属于「配置这张表」 */
.init-bar {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 12px; flex-wrap: wrap;
}
.init-label { font-size: 12px; color: var(--text-2); white-space: nowrap; }
.init-input { width: 280px; }
.ht-svg { background: #fcfdff; border: 1px solid var(--border); border-radius: 10px; flex-shrink: 0; }
.ht-panel { flex: 1; min-width: 300px; }
.formula code { background: #f2f4f8; padding: 8px 10px; border-radius: 6px; display: block; font-size: 12px; line-height: 1.7; }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; font-size: 13px; border-bottom: 1px dashed #f0f2f6; }
.tbl { font-size: 12px; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
.tbl-head { display: grid; grid-template-columns: 1fr 1fr 1fr; background: #f6f8fb; padding: 7px 10px; font-weight: 600; }
.tbl-row { display: grid; grid-template-columns: 1fr 1fr 1fr; padding: 6px 10px; border-top: 1px solid #f0f2f6; cursor: pointer; }
.tbl-row:hover { background: #f6f8fb; }
.tbl-row.active { background: var(--brand-light); color: var(--brand); font-weight: 600; }
.tip { margin-top: 10px; line-height: 1.7; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
