import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig( {
  plugins: [ vue() ],
  server: {
    host: true, // Necessário para o Docker expor a rede
    port: 5173,
    watch: {
      usePolling: true // <--- ADICIONE ISSO PARA O WINDOWS RECONHECER MUDANÇAS
    }
  },
  resolve: {
    alias: {
      '@': fileURLToPath( new URL( './src', import.meta.url ) )
    }
  }
} )