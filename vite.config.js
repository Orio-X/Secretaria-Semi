import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import path from 'path'

// https://vitejs/dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },

  // ADICIONE ESTE BLOCO DE CÓDIGO AQUI
  server: {
    proxy: {
      // Qualquer requisição que comece com /api será redirecionada
      '/api': {
        // O endereço do seu backend Django em execução
        target: 'http://127.0.0.1:8000', 
        
        // Necessário para o backend aceitar a requisição
        changeOrigin: true, 
      },
    }
  }
})