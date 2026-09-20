import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    // En desarrollo, el frontend corre en :5173 y el backend FastAPI en :8000.
    // Este proxy evita configurar CORS/URLs absolutas: /api/* se reenvía al backend real.
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    // Se compila directo a la carpeta que FastAPI sirve como estáticos (ver main.py, un nivel arriba).
    outDir: '../static',
    emptyOutDir: true,
  },
})
