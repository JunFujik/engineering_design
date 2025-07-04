import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

export default defineConfig({
  plugins: [svelte()],
  server: {
    port: 3001,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://backend:5000',
        changeOrigin: true
      }
    }
  },
  optimizeDeps: {
    exclude: ['svelte-navigator']
  },
  build: {
    target: 'esnext'
  },
  esbuild: {
    target: 'esnext'
  }
})