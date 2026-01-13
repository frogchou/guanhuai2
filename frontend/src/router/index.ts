import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: () => import('../views/Login.vue') },
    { path: '/', component: () => import('../views/PersonaList.vue'), meta: { requiresAuth: true } },
    { path: '/personas/new', component: () => import('../views/PersonaCreate.vue'), meta: { requiresAuth: true } },
    { path: '/chat/:id', component: () => import('../views/Chat.vue'), meta: { requiresAuth: true } },
  ]
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.token) {
    next('/login')
  } else {
    next()
  }
})

export default router
