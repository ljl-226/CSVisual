<template>
  <div class="auth-page">
    <!-- 登录 / 注册 / 找回三页没有顶栏，这里单独放一个开关 -->
    <button class="auth-theme" :aria-label="isDark ? '切换到白天模式' : '切换到夜晚模式'" @click="onToggleTheme">
      <el-icon><Sunny v-if="!isDark" /><Moon v-else /></el-icon>
      <span>{{ isDark ? '白天' : '夜晚' }}</span>
    </button>
    <div class="auth-box">
      <div class="auth-left">
        <span class="glow glow-a"></span>
        <span class="glow glow-b"></span>
        <div class="auth-left-inner">
          <div class="brand">
            <BrandLogo size="lg" />
            <h1>CSVisual</h1>
          </div>
          <h2>计算机专业多学科<br />可视化智能学习平台</h2>
          <!-- 卖点写给「第一次打开网站的学生」看：
               原来是「计算机核心课 + 数理基础 + Web 前端全学科知识点动画」「智能学习 Agent 答疑」
               这类课程名词堆叠 + 技术黑话（学生不知道 Agent 是什么）。
               改成「打开网站能干什么」，每条一个具体场景，一口气能读完。 -->
          <ul class="features">
            <li>数据结构、组成原理、高数这些课，知识点都有动画可以看</li>
            <li>有不懂的直接问，它边讲边把对应的动画打开给你</li>
            <li>配了练习题：做完当场判分，错在哪、怎么补都告诉你</li>
          </ul>
          <!-- 只留最能一眼看懂的三项：动画、课程、在线运行语言。
               知识点/配套练习/算法题挪到课程中心展示，登录页摆六格反而没人看完 -->
          <div class="stat-row">
            <div class="stat">
              <b>{{ stats.visualizations || '—' }}</b><span>可视化动画</span>
            </div>
            <i class="stat-sep"></i>
            <div class="stat">
              <b>{{ stats.courses || '—' }}</b><span>门课程</span>
            </div>
            <i class="stat-sep"></i>
            <div class="stat">
              <b>{{ stats.languages || '—' }}</b><span>种语言在线运行</span>
            </div>
          </div>
          <div class="course-tags">
            <span>数据结构与算法</span><span>计算机网络</span><span>操作系统</span><span>计算机组成原理</span>
            <span>高等数学</span><span>线性代数</span><span>概率统计</span><span>大学物理</span><span>离散数学</span>
            <span>Web 前端（HTML/CSS/JS）</span>
          </div>
        </div>
      </div>
      <div class="auth-right">
        <h3>{{ title }}</h3>
        <p class="sub">{{ sub }}</p>
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { statsApi } from '@/api'
import { getTheme, toggleTheme } from '@/utils/theme'
import BrandLogo from '@/components/BrandLogo.vue'

defineProps({
  title: { type: String, default: '账号登录' },
  sub: { type: String, default: '' }
})

const isDark = ref(getTheme() === 'dark')
function onToggleTheme() {
  isDark.value = toggleTheme() === 'dark'
}

// 统计数字由后端实时给出，避免写死之后和实际课程/语言数量脱节。
// 放在壳里统一取：登录 / 注册 / 找回三页共用左栏，各自不再重复请求。
const stats = ref({})
onMounted(async () => {
  try {
    const res = await statsApi.overview()
    stats.value = (res && res.data) || {}
  } catch (e) {
    // 统计失败不能影响登录功能：静默忽略，数字位显示「—」
    stats.value = {}
  }
})
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex; align-items: center; justify-content: center;
  background: var(--grad-page), var(--bg);
  padding: 20px;
}
.auth-theme {
  position: fixed; top: 18px; right: 20px; z-index: 10;
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 12px; border-radius: 20px; font-size: 12px;
  background: var(--card); border: 1px solid var(--border);
  color: var(--text-2); cursor: pointer; box-shadow: var(--shadow);
  transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
}
.auth-theme:hover { color: var(--brand); border-color: var(--brand-3); }
.auth-box {
  width: 840px; max-width: 100%;
  /* 四个认证页（登录/注册/找回/临时密码）共用这个壳：
     给一个统一的 min-height，页面间切换时盒子不再跳高跳矮。
     用 min-height 而不是 height——将来某页内容更多时仍能撑开，不会被裁。
     数值取「紧凑版四页里最高的那一页」（找回密码页），改动页面内容后要重测一次。 */
  min-height: 450px;
  background: var(--card); border-radius: 16px; overflow: hidden;
  box-shadow: 0 12px 40px rgba(31,39,51,0.1);
  display: grid; grid-template-columns: 1fr 1fr;
}
.auth-left {
  position: relative; overflow: hidden;
  background: linear-gradient(158deg, #2f5fe0 0%, var(--brand) 45%, #6f9bff 100%);
  color: #fff; padding: 28px 28px;
}
.glow { position: absolute; border-radius: 50%; pointer-events: none; }
.glow-a {
  width: 300px; height: 300px; right: -90px; top: -110px;
  background: radial-gradient(circle, rgba(255,255,255,0.20) 0%, rgba(255,255,255,0) 68%);
}
.glow-b {
  width: 240px; height: 240px; left: -80px; bottom: -90px;
  background: radial-gradient(circle, rgba(130,255,215,0.18) 0%, rgba(130,255,215,0) 70%);
}
.auth-left-inner {
  position: relative; height: 100%;
  display: flex; flex-direction: column; gap: 12px;
}
.brand { display: flex; align-items: center; gap: 10px; }
.brand h1 { font-size: 21px; margin: 0; letter-spacing: 0.4px; }
.auth-left h2 { font-size: 19px; line-height: 1.5; margin: 2px 0 0; font-weight: 600; }
.features { list-style: none; padding: 0; margin: 2px 0 0; }
.features li {
  line-height: 1.95; font-size: 12.5px; opacity: 0.94;
  padding-left: 19px; position: relative;
}
.features li::before {
  content: '✓'; position: absolute; left: 0; font-weight: 700; opacity: 0.9;
}
/* 三项数据一行排开。原先拆成两行、且第二行字号更小，
   信息层级反而更乱；现在统一成一行 + 细分隔线。 */
.stat-row {
  display: flex; align-items: stretch; gap: 6px; margin: 2px 0;
  flex-wrap: nowrap;
}
.stat {
  flex: 1 1 0; min-width: 0; text-align: center; padding: 8px 4px; border-radius: 10px;
  background: rgba(255,255,255,0.14); border: 1px solid rgba(255,255,255,0.2);
  backdrop-filter: blur(6px);
}
.stat b { display: block; font-size: 17px; font-variant-numeric: tabular-nums; line-height: 1.2; }
.stat span {
  font-size: 11px; opacity: 0.88; display: block; line-height: 1.35;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
/* 细分隔线：用 i 而不是 border-right，避免最后一格多出一条线 */
.stat-sep {
  flex: 0 0 1px; align-self: center; height: 26px;
  background: linear-gradient(180deg, transparent, rgba(255,255,255,0.34), transparent);
}
/* 「种语言在线运行」这类长文案在窄屏会撑破格子，缩一号字 */
@media (max-width: 1400px) {
  .stat span { font-size: 10.5px; }
  .stat b { font-size: 16px; }
}
/* 真的很窄就允许折成两行，保证数字可读 —— 强行不折会把数字挤没 */
@media (max-width: 900px) {
  .stat-row { flex-wrap: wrap; }
  .stat { flex: 1 1 30%; }
  .stat-sep { display: none; }
}
.course-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: auto; }
.course-tags span {
  background: rgba(255,255,255,0.16); border: 1px solid rgba(255,255,255,0.28);
  padding: 3px 9px; border-radius: 20px; font-size: 11.5px;
}
.auth-right { padding: 28px 32px 30px; display: flex; flex-direction: column; }
.auth-right h3 { font-size: 19px; margin: 0 0 4px; }
.auth-right .sub { margin: 0 0 14px; font-size: 12px; color: var(--text-3); min-height: 16px; line-height: 1.45; }
/* 登录 / 注册 / 找回 三页共用的主按钮与底部链接区，样式放在壳里，
   避免三个页面各写一份、改一次漏两个。
   表单项的间距也在这里统一：Element Plus 在大号表单下留 22px 地平线，
   放两三个输入框就把页面撑得很长，收到 13px 观感更紧凑。 */
.auth-right :deep(.el-form-item) { margin-bottom: 13px; }
.auth-right :deep(.submit) {
  width: 100%; margin-top: 2px; height: 40px; font-size: 14.5px; font-weight: 600;
  border: none; box-shadow: 0 5px 16px rgba(59,110,246,0.3);
}
.auth-right :deep(.submit:hover) { box-shadow: 0 8px 22px rgba(59,110,246,0.38); }
.auth-right :deep(.bottom) { margin-top: 13px; text-align: center; font-size: 12.5px; color: var(--text-2); }
.auth-right :deep(.bottom) > span { margin-left: 10px; white-space: nowrap; }
/* split 变体：两端对齐（登录 / 找回页左右各一组链接），
   比居中排更稳 —— 下方靠右的兜底入口能与「立即注册」右缘对成一条线 */
.auth-right :deep(.bottom.split) { display: flex; justify-content: space-between; align-items: center; }
.auth-right :deep(.bottom.split) > span { margin-left: 0; }
/* 兜底入口（申请临时密码）：小一号、靠右下，不抢主视线；
   样式收在壳里，登录 / 找回两页共用，不再各写一份 */
.auth-right :deep(.side-entry) { margin-top: 6px; text-align: right; font-size: 12px; line-height: 1.6; }
.auth-right :deep(.side-entry) > span { margin-right: 6px; }
/* 分隔「演示账号」那类附属区块：默认 24px 上下留白太松 */
.auth-right :deep(.el-divider) { margin: 14px 0 10px; }
.auth-right :deep(.el-divider__text) { font-size: 11.5px; }

/* ---------- 响应式 ----------
 * ≤900：左半的品牌宣传panel 收起（它是装饰性的，手机上留着只会把表单推到首屏外），
 *        表单铺满整宽。表单本身在 360 宽下也能完整显示。
 */
@media (max-width: 900px) {
  .auth-box { grid-template-columns: 1fr; width: 100%; max-width: 520px; border-radius: 14px; min-height: 0; }
  .auth-left { display: none; }
  .auth-right { padding: 28px 24px 32px; }
}
@media (max-width: 480px) {
  .auth-box { max-width: 100%; border-radius: 12px; }
  .auth-right { padding: 22px 16px 26px; }
  .auth-right h3 { font-size: 18px; }
  .auth-theme { padding: 5px 10px; font-size: 11px; }
}
@media (max-width: 360px) {
  .auth-right { padding: 18px 12px 22px; }
}
</style>
