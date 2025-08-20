import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: "0.0.0.0",
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
  // Increase timeouts to accommodate longer backend processing (e.g., Telegram throttling)
  // Values are in milliseconds and are passed to http-proxy
  timeout: 180000,        // socket inactivity timeout (3 minutes)
  proxyTimeout: 180000,   // upstream response timeout (3 minutes)
      },
    },
  },
})
