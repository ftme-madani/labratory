import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'icons/*.svg'],
      manifest: {
        name: 'آزمایشگاه مجازی هوشمند علوم تجربی',
        short_name: 'آزما‌علوم',
        description: 'سامانه هوشمند و تعاملی آزمایش‌های علوم تجربی دوره متوسطه اول و دوم',
        theme_color: '#0B192C',
        background_color: '#0B192C',
        display: 'standalone',
        orientation: 'portrait',
        dir: 'rtl',
        lang: 'fa',
        start_url: '/',
        icons: [
          {
            src: '/icons/icon-192.svg',
            sizes: '192x192',
            type: 'image/svg+xml'
          },
          {
            src: '/icons/icon-512.svg',
            sizes: '512x512',
            type: 'image/svg+xml'
          },
          {
            src: '/icons/icon-512.svg',
            sizes: '512x512',
            type: 'image/svg+xml',
            purpose: 'any maskable'
          }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2,json}'],
        runtimeCaching: [
          {
            urlPattern: ({ request }) => request.destination === 'image',
            handler: 'CacheFirst',
            options: {
              cacheName: 'lab-images-cache',
              expiration: {
                maxEntries: 60,
                maxAgeSeconds: 30 * 24 * 60 * 60 // 30 روز
              }
            }
          },
          {
            urlPattern: ({ url }) => url.pathname.startsWith('/api/experiments'),
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'lab-experiments-api-cache',
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 24 * 60 * 60 // 1 روز
              }
            }
          }
        ]
      }
    })
  ],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  },
  preview: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
})
