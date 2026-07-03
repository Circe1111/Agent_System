<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const showNavbar = computed(() => route.path !== '/login' && route.path !== '/register')
const isAuthenticated = computed(() => userStore.isAuthenticated)
const isAdmin = computed(() => userStore.isAdmin)
const username = computed(() => userStore.userInfo?.username || '用户')
const userAvatar = computed(() => userStore.userInfo?.avatar || '')
const userRole = computed(() => {
  const role = userStore.userInfo?.role || 'student'
  if (role === 'admin') return '管理员'
  if (role === 'teacher') return '教师'
  return '学生'
})

const goHome = () => {
  if (userStore.isAuthenticated) {
    router.push('/chat')
  } else {
    router.push('/login')
  }
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
  ElMessage.success('已退出登录')
}

const handleCommand = (cmd) => {
  if (cmd === 'settings') router.push('/settings')
  else if (cmd === 'logout') handleLogout()
}
</script>

<template>
  <div class="app-shell">
    <header v-if="showNavbar" class="top-nav">
      <div class="brand" @click="goHome">
        <span class="brand-icon">◎</span>
        <span>智学系统</span>
      </div>

      <nav class="nav-links" v-if="isAuthenticated">
        <router-link to="/chat" class="nav-link">AI对话</router-link>
        <router-link to="/path" class="nav-link">学习路径</router-link>
        <router-link to="/resources" class="nav-link">学习资源</router-link>
        <router-link to="/user-profile" class="nav-link">偏好</router-link>
        <router-link v-if="isAdmin" to="/admin" class="nav-link">管理后台</router-link>
      </nav>

      <div class="nav-actions">
        <router-link v-if="!isAuthenticated" to="/login" class="login-link">登录</router-link>
        <el-dropdown
          v-if="isAuthenticated"
          trigger="click"
          @command="handleCommand"
        >
          <div class="user-menu-trigger">
            <el-avatar :size="32" :src="userAvatar" class="nav-avatar">{{
              username.slice(0, 1)
            }}</el-avatar>
            <div class="user-meta">
              <div class="user-name">{{ username }}</div>
              <div class="user-role">{{ userRole }}</div>
            </div>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile" @click="router.push('/profile')"
                >个人中心</el-dropdown-item
              >
              <el-dropdown-item command="settings">设置</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <main class="page-content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: var(--bg-page, #fafcfe);
}

.top-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: #1253D2;
  color: #ffffff;
  box-shadow: 0 2px 16px rgba(18, 83, 210, 0.25);
}

.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.3rem;
  font-weight: bold;
  cursor: pointer;
  color: #ffffff;
}

.brand-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
}

.nav-links {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.nav-link,
.login-link {
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  font-size: 1.15rem;
  font-weight: 500;
  transition: color 0.2s ease;
}

.nav-link:hover,
.login-link:hover {
  color: #ffffff;
}

.nav-link.router-link-active {
  color: #ffffff;
  font-weight: bold;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-menu-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.15);
  cursor: pointer;
}

.nav-avatar {
  background: rgba(255, 255, 255, 0.25);
}

.user-meta {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.user-name {
  font-size: 0.92rem;
  font-weight: 600;
  color: #ffffff;
}

.user-role {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
}

.page-content {
  min-height: calc(100vh - 64px);
  background: var(--bg-page, #fafcfe);
}

@media (max-width: 900px) {
  .top-nav {
    flex-wrap: wrap;
    gap: 16px;
  }

  .nav-links {
    width: 100%;
    justify-content: center;
  }
}
</style>