import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// GitHub Pages publica el sitio bajo /ModaStock/.
// En otros proveedores (Vercel, Render, etc.) se conserva la raíz /.
export default defineConfig({
  base: process.env.GITHUB_PAGES === 'true' ? '/ModaStock/' : '/',
  plugins: [react()],
  server: { port: 5173 },
})
