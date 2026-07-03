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
        <el-menu-item index="chat" @click="navigateTo('/chat')">
          <el-icon><ChatLineRound /></el-icon>
          <span v-if="!isCollapse">AI对话</span>
        </el-menu-item>

        <el-menu-item index="profile" @click="navigateTo('/profile')">
          <el-icon><User /></el-icon>
          <span v-if="!isCollapse">个人中心</span>
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
const activeMenu = ref('chat')

const username = computed(() => userStore.userInfo?.username || '用户')
const userAvatar = computed(() => userStore.userInfo?.avatar || '')
const isAdmin = computed(() => userStore.isAdmin)
const pageTitle = computed(() => {
  const titles = {
    '/chat': 'AI智能对话',
    '/profile': '个人中心',
    '/user-profile': '偏好',
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
  if (path.includes('/chat')) activeMenu.value = 'chat'
  else if (path.includes('/profile')) activeMenu.value = 'profile'
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
  border-right: 1px solid rgba(255, 255, 255, 0.08);
}

.logo-container {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0f2340;
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-container:hover {
  opacity: 0.9;
}

.logo-text {
  color: #ffffff;
  font-size: 1.125rem;
  font-weight: 700;
  letter-spacing: 2px;
}

.nav-menu {
  border-right: none !important;
}
/* Override Element Plus menu defaults */
.nav-menu :deep(.el-menu-item) {
  color: #cbd5e0 !important;
  border-radius: 8px;
  margin: 4px 8px;
  height: 48px;
  line-height: 48px;
  transition: all 0.2s ease;
}
.nav-menu :deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.08) !important;
  color: #ffffff !important;
}
.nav-menu :deep(.el-menu-item.is-active) {
  background: rgba(99, 179, 237, 0.2) !important;
  color: #63b3ed !important;
  font-weight: 600;
}
.nav-menu :deep(.el-sub-menu) {
  color: #cbd5e0 !important;
}
.nav-menu :deep(.el-sub-menu__title) {
  color: #cbd5e0 !important;
  border-radius: 8px;
  margin: 4px 8px;
  height: 48px;
  line-height: 48px;
}
.nav-menu :deep(.el-sub-menu__title:hover) {
  background: rgba(255, 255, 255, 0.08) !important;
  color: #ffffff !important;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #1a365d;
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.2);
  padding: 0 16px;
  height: 64px;
}

.header-left {
  display: flex;
  align-items: center;
}

.collapse-btn {
  font-size: 1.25rem;
  color: #ffffff;
  margin-right: 16px;
  padding: 8px;
}

.collapse-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.page-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #ffffff;
  line-height: 1;
}

.header-right {
  display: flex;
  align-items: center;
  padding: 8px 0;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
  transition: background 0.2s;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.1);
}

.username {
  margin-left: 8px;
  color: #ffffff;
  font-weight: 500;
  font-size: 0.875rem;
}

.main-content {
  padding: 24px;
  background-color: var(--bg-page);
  min-height: calc(100vh - 128px);
}

.footer {
  background-color: #ffffff;
  box-shadow: 0 -2px 16px rgba(168, 216, 234, 0.08);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0 24px;
  height: 64px;
  color: #718096;
  font-size: 0.875rem;
}
</style>