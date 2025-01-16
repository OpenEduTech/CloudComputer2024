import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  server: {
    proxy: {
      '/config': {
        target: 'http://localhost',  // 替换为你的后端 API 地址
        changeOrigin: true, // 如果需要修改主机头（如跨域时）
        rewrite: (path) => path.replace(/^\/config/, '/config'), // 可选的路径重写
      },
    },
  },
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})
