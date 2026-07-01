<template>
  <el-container class="layout-container">
    <el-aside
      :width="isCollapse ? '64px' : '200px'"
      class="sidebar"
      :class="{ collapsed: isCollapse }"
    >
      <div class="logo-container" @click="toggleSidebar">
        <span v-if="!isCollapse" class="logo-text">智学系统</span>
      </div>

      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :collapse-transition="false"
        background-color="#1a365d"
        text-color="#e2e8f0"
        active-text-color="#63b3ed"
        class="nav-menu"
      >
        <el-menu-item index="dashboard" @click="navigateTo('/dashboard')">
          <el-icon><House /></el-icon>
          <span v-if="!isCollapse">首页</span>
        </el-menu-item>

        <el-menu-item index="profile" @click="navigateTo('/profile')">
          <el-icon><User /></el-icon>
          <span v-if="!isCollapse">个人中心</span>
        </el-menu-item>

        <el-menu-item index="chat" @click="navigateTo('/chat')">
          <el-icon><ChatLineRound /></el-icon>
          <span v-if="!isCollapse">AI对话</span>
        </el-menu-item>

        <el-menu-item index="user-profile" @click="navigateTo('/user-profile')">
          <el-icon><DataAnalysis /></el-icon>
          <span v-if="!isCollapse">偏好</span>
        </el-menu-item>

        <el-menu-item index="path" @click="navigateTo('/path')">
          <el-icon><Guide /></el-icon>
          <span v-if="!isCollapse">学习路径</span>
        </el-menu-item>

        <el-menu-item index="resources" @click="navigateTo('/resources')">
          <el-icon><Document /></el-icon>
          <span v-if="!isCollapse">学习资源</span>
        </el-menu-item>

        <el-sub-menu index="admin" v-if="isAdmin">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span v-if="!isCollapse">管理后台</span>
          </template>
          <el-menu-item index="admin-users" @click="navigateTo('/admin')">
            <el-icon><UserFilled /></el-icon>
            <span v-if="!isCollapse">用户管理</span>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-button type="text" class="collapse-btn" @click="toggleSidebar">
            <el-icon><Fold v-if="!isCollapse" /><Expand v-else /></el-icon>
          </el-button>
          <span class="page-title">{{ pageTitle }}</span>
        </div>

        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32" :src="userAvatar" />
              <span v-if="!isCollapse" class="username">{{ username }}</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="settings">设置</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>

      <el-footer class="footer">
        <span>© 2024 基于大模型的个性化资源生成与学习多智能体系统</span>
      </el-footer>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores'
import { ElMessage } from 'element-plus'
import {
  House,
  User,
  ChatLineRound,
  Guide,
  Document,
  Setting,
  UserFilled,
  Fold,
  Expand,
  DataAnalysis,
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const isCollapse = ref(false)
const activeMenu = ref('dashboard')

const username = computed(() => userStore.userInfo?.username || '用户')
const userAvatar = computed(() => userStore.userInfo?.avatar || '')
const isAdmin = computed(() => userStore.isAdmin)
const pageTitle = computed(() => {
  const titles = {
    '/dashboard': '系统首页',
    '/profile': '个人中心',
    '/user-profile': '偏好',
    '/chat': 'AI智能对话',
    '/path': '个性化学习路径',
    '/resources': '学习资源中心',
    '/admin': '管理后台',
    '/settings': '系统设置',
  }
  return titles[route.path] || '智学系统'
})

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

const navigateTo = (path) => {
  router.push(path)
}

const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
      userStore.logout()
      router.push('/login')
      ElMessage.success('已退出登录')
      break
  }
}

const updateActiveMenu = () => {
  const path = route.path
  if (path.includes('/dashboard')) activeMenu.value = 'dashboard'
  else if (path.includes('/profile')) activeMenu.value = 'profile'
  else if (path.includes('/chat')) activeMenu.value = 'chat'
  else if (path.includes('/user-profile')) activeMenu.value = 'user-profile'
  else if (path.includes('/path')) activeMenu.value = 'path'
  else if (path.includes('/resources')) activeMenu.value = 'resources'
  else if (path.includes('/admin')) activeMenu.value = 'admin'
  else if (path.includes('/settings')) activeMenu.value = 'settings'
}

onMounted(() => {
  if (!userStore.isAuthenticated) {
    router.push('/login')
    return
  }

  updateActiveMenu()
})

// 监听路由变化
router.afterEach(() => {
  updateActiveMenu()
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #1a365d;
  transition: width 0.3s ease;
  height: 100vh;
  overflow-x: hidden;
}

.logo-container {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #2c5282;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logo-container:hover {
  background-color: #3182ce;
}

.logo-text {
  color: white;
  font-size: 1.2rem;
  font-weight: bold;
}

.nav-menu {
  border-right: none;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 0 20px;
  height: 60px;
}

.collapse-btn {
  font-size: 1.2rem;
  color: #4a5568;
  margin-right: 15px;
}

.page-title {
  font-size: 1.2rem;
  font-weight: bold;
  color: #1a365d;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin-left: 8px;
  color: #4a5568;
  font-weight: 500;
}

.main-content {
  padding: 20px;
  background-color: #f7fafc;
  min-height: calc(100vh - 120px);
}

.footer {
  background-color: white;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  color: #718096;
  font-size: 0.9rem;
}
</style>
