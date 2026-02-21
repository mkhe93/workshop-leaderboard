import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => ({
  server: {
      host: '0.0.0.0',
      port: loadEnv(mode, process.cwd()).VITE_LEADERBOARD_FRONTEND_PORT,
      allowedHosts: [
          "localhost",
          `${loadEnv(mode, process.cwd()).VITE_WORKSHOP_USER}-leaderboard-frontend.workshop.devboost.com`
        ],
    },
  plugins: [
    vue()
  ]
  })
)
