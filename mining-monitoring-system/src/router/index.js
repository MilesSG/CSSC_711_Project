import { createRouter, createWebHistory } from 'vue-router'
import MonitorView from '../views/MonitorView.vue'
import SurroundView from '../views/SurroundView.vue'
import MainView from '../views/MainView.vue'
import ObstacleDetection from '../views/ObstacleDetection.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'monitor',
      component: MonitorView
    },
    {
      path: '/surround',
      name: 'surround',
      component: SurroundView
    },
    {
      path: '/main',
      name: 'main',
      component: MainView
    },
    {
      path: '/obstacle',
      name: 'obstacle',
      component: ObstacleDetection
    }
  ]
})

export default router 