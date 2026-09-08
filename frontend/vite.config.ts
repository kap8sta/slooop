import { defineConfig } from 'vite';

const proxy = {
  '/api': {
    target: 'http://localhost:8080',
    changeOrigin: true,
  },
  '/ws': {
    target: 'http://localhost:8080',
    ws: true,
  },
};

export default defineConfig({
  define: {
    global: 'globalThis',
  },
  server: {
    port: 5173,
    proxy,
  },
  preview: {
    port: 5173,
    proxy,
  },
});
