<template>
  <!-- 品牌图标：图片本身自带圆角和透明通道，这里只负责尺寸与阴影。
       为什么用 <img> 而不是文字「CS」：文字版在窄屏下字形会随 font-size 抖动，
       且和浏览器/系统字体绑定 —— 换台机器「CS」两个字就不一样粗了。 -->
  <img class="brand-logo" :class="size" :src="src" alt="CSVisual" :width="px" :height="px" />
</template>

<script setup>
/**
 * 全站统一的品牌 logo。
 *
 * 图标由 tools/extract_logo.py 从设计稿抠出（透明 PNG + 圆角），
 * 顶栏、抽屉、页脚、登录页共用同一个文件，避免各处画得不一样。
 */
import { computed } from 'vue'

const props = defineProps({
  // sm 用于抽屉等空间紧张的位置，md 用于页脚，lg 用于登录页
  size: { type: String, default: 'md' }
})

const SIZES = { sm: 24, md: 34, lg: 38 }
const px = computed(() => SIZES[props.size] || SIZES.md)
// vite 会把 public/ 下的文件原样拷到 dist 根目录，用绝对路径引用最稳
const src = '/logo.png'
</script>

<style scoped>
.brand-logo {
  display: block;
  flex-shrink: 0;
  object-fit: contain;
  /* 图片自带圆角，这里只补投影让 logo 从白色/深色背景上浮起来 */
  box-shadow: 0 4px 12px rgba(59, 110, 246, 0.32);
}
.brand-logo.sm { box-shadow: none; }
</style>
