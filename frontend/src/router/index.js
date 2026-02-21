import { createRouter, createWebHistory } from 'vue-router'
import LeaderboardView from '../views/LeaderboardView.vue'
import ChartsView from '../views/ChartsView.vue'

const routes = [
  {
    path: '/',
    redirect: '/leaderboard'
  },
  {
    path: '/leaderboard',
    name: 'leaderboard',
    component: LeaderboardView
  },
  {
    path: '/chart',
    name: 'chart',
    component: ChartsView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
