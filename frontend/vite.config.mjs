import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import tailwindcss from '@tailwindcss/vite';
const isProd = process.env.NODE_ENV === 'production';
const backendPort = isProd ? 8000 : 8003;
console.log('Vite 代理后端端口:', backendPort);
export default defineConfig({
  plugins: [vue(), tailwindcss()],
  esbuild: { jsx: 'automatic', jsxImportSource: 'react' },
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: `http://127.0.0.1:${backendPort}`,
        changeOrigin: true
      }
    }
  },
  resolve: {
    alias: {
      '@': '/src'
    }
  }
});
