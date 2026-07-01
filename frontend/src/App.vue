<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const showNavbar = computed(() => route.path !== '/login')
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
    router.push('/dashboard')
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
        <router-link to="/dashboard" class="nav-link">首页</router-link>
        <router-link to="/chat" class="nav-link">AI对话</router-link>
        <router-link to="/path" class="nav-link">学习路径</router-link>
        <router-link to="/resources" class="nav-link">学习资源</router-link>
        <router-link to="/user-profile" class="nav-link">用户画像</router-link>
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
  background: #f7f8fc;
}

.top-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 24px;
  background: linear-gradient(90deg, #1a365d 0%, #2b6cb0 100%);
  color: #fff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.12);
}

.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
}

.brand-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.18);
}

.nav-links {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.nav-link,
.login-link {
  color: #e2e8f0;
  text-decoration: none;
  font-size: 0.95rem;
}

.nav-link:hover,
.login-link:hover {
  color: #fff;
}

.nav-link.router-link-active {
  color: #fff;
  font-weight: bold;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-menu-trigger {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 8px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  cursor: pointer;
}

.nav-avatar {
  background: linear-gradient(135deg, #63b3ed, #3182ce);
}

.user-meta {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.user-name {
  font-size: 0.92rem;
  font-weight: 600;
}

.user-role {
  font-size: 0.75rem;
  color: #e2e8f0;
}

.page-content {
  min-height: calc(100vh - 64px);
}

@media (max-width: 900px) {
  .top-nav {
    flex-wrap: wrap;
    gap: 12px;
  }

  .nav-links {
    width: 100%;
    justify-content: center;
  }
}
</style>
