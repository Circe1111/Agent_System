import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/login',
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/ProfileView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/SettingsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/user-profile',
    name: 'UserProfile',
    component: () => import('../views/UserProfileView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/chat',
    name: 'AIChat',
    component: () => import('../views/AIChatView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/path',
    name: 'LearningPath',
    component: () => import('../views/LearningPathView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/resources',
    name: 'Resources',
    component: () => import('../views/ResourcesView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/AdminView.vue'),
    meta: { requiresAuth: true, admin: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const userRole = localStorage.getItem('userRole') || 'student'

  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.meta.admin && userRole !== 'admin') {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
