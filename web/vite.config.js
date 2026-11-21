import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:3000',
        changeOrigin: true
      },
      // 头像等用户上传的静态文件由后端提供，dev 模式下同样要转发过去，
      // 否则 <img src="/uploads/..."> 在 5173 上直接 404
      '/uploads': {
        target: 'http://localhost:3000',
        changeOrigin: true
      }
    }
  }
})
