import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',  // Allow connections from outside Docker container
    proxy: {
      '/api': {
        // In Docker use 'backend:8000', locally use 'localhost:8000'
        target: process.env.VITE_API_URL || 'http://backend:8000',
        changeOrigin: true,
        cookieDomainRewrite: '',
      },
    },
  },
})
