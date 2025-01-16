import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import ChatView from '@/views/ChatView.vue'
import BeginView from '@/views/BeginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      children: [
        {
          path: 'chat/:id', // 动态路径，传递 chat id
          name: 'chat',
          component: ChatView,
          props: true, // 将路由参数传递给组件
        },
        {
          path: '',
          name: 'begin',
          component: BeginView,
        }
      ]
    },
  ],
})

export default router
