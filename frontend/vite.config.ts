import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'
import mkcert from 'vite-plugin-mkcert'

export default defineConfig({
  base: "/vasoactive_drug_speed_estimatior_frontend/",
  server: { 
    port: 3000,
    host: true,
    strictPort: true,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        secure: false,
      },
    },
    watch: {
      usePolling: true,
    }, 
  },
  plugins: [
    react(),
    mkcert(),
    VitePWA({
      registerType: "autoUpdate",
      devOptions: {
        enabled: true,
      },
      includeAssets: ["favicon.ico", "apple-touch-icon.png", "favicon-16x16.png", "favicon-32x32.png"],
      manifest: {
        name: "Калькулятор скорости инфузии вазоактивных препаратов",
        short_name: "VasoactiveDrugs",
        description: "Сервис для расчёта скорости инфузии вазоактивных препаратов",
        start_url: "/vasoactive_drug_speed_estimatior_frontend/",
        scope: "/vasoactive_drug_speed_estimatior_frontend/",
        display: "standalone",
        background_color: "#ffffff",
        theme_color: "#0033a0",
        icons: [
          { 
            src: "/vasoactive_drug_speed_estimatior_frontend/pwa-192x192.png", 
            sizes: "192x192", 
            type: "image/png",
            purpose: "any maskable"
          },
          { 
            src: "/vasoactive_drug_speed_estimatior_frontend/pwa-512x512.png", 
            sizes: "512x512", 
            type: "image/png",
            purpose: "any maskable"
          },
          {
            src: "/vasoactive_drug_speed_estimatior_frontend/apple-touch-icon.png",
            sizes: "180x180",
            type: "image/png"
          }
        ],
      },
    }),
  ],
})
