# EduAgent 前端文档

> 前端应用：基于 Vue 3 + Element Plus 的个性化学习多智能体系统界面

---

## 目录

1. [技术栈](#1-技术栈)
2. [目录结构](#2-目录结构)
3. [路由配置](#3-路由配置)
4. [状态管理](#4-状态管理)
5. [API 请求](#5-api-请求)
6. [页面组件](#6-页面组件)
7. [样式系统](#7-样式系统)
8. [配置说明](#8-配置说明)
9. [启动方式](#9-启动方式)

---

## 1. 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.5+ | 前端框架 |
| Vite | 8.0+ | 构建工具 |
| Element Plus | 2.14+ | UI 组件库 |
| Vue Router | 5.1+ | 路由管理 |
| Pinia | 3.0+ | 状态管理 |
| Axios | 1.18+ | HTTP 客户端 |
| Marked | 18.0+ | Markdown 渲染 |
| Highlight.js | 11.11+ | 代码高亮 |

---

## 2. 目录结构

```
frontend/
├── public/                 # 静态资源
│   └── favicon.ico         # 网站图标
├── src/                    # 源代码
│   ├── api/                # API 请求封装
│   │   └── api.js          # 所有接口定义
│   ├── assets/             # 静态资源（样式、图片）
│   │   ├── base.css        # 基础样式
│   │   ├── main.css        # 全局样式
│   │   └── logo.svg        # Logo
│   ├── components/         # 可复用组件
│   │   ├── icons/          # 图标组件
│   │   ├── Layout.vue      # 页面布局组件
│   │   ├── HelloWorld.vue  # 示例组件
│   │   ├── TheWelcome.vue  # 欢迎组件
│   │   └── WelcomeItem.vue # 欢迎项组件
│   ├── router/             # 路由配置
│   │   └── index.js        # 路由定义和守卫
│   ├── stores/             # Pinia 状态管理
│   │   ├── index.js        # 用户状态（主要）
│   │   ├── counter.js      # 计数器示例
│   │   └── settings.js     # 设置状态
│   ├── utils/              # 工具函数
│   │   └── markdownRenderer.js    # Markdown 渲染工具
│   ├── views/              # 页面视图组件
│   │   ├── LoginView.vue   # 登录页面
│   │   ├── RegisterView.vue       # 注册页面
│   │   ├── DashboardView.vue      # 首页仪表盘
│   │   ├── AIChatView.vue  # AI 对话页面
│   │   ├── ProfileView.vue # 用户画像页面
│   │   ├── UserProfileView.vue    # 用户信息页面
│   │   ├── LearningPathView.vue   # 学习路径页面
│   │   ├── ResourcesView.vue      # 学习资源页面
│   │   ├── SettingsView.vue       # 系统设置页面
│   │   ├── AdminView.vue   # 管理后台页面
│   │   └── AboutView.vue   # 关于页面
│   ├── App.vue             # 根组件
│   └── main.js             # 应用入口
├── .env.development        # 开发环境变量
├── .prettierrc.json        # Prettier 格式化配置
├── index.html              # HTML 模板
├── jsconfig.json           # JS 配置（路径别名）
├── nginx.conf              # Nginx 配置（生产环境）
├── package.json            # 项目依赖
└── vite.config.js          # Vite 配置
```

---

## 3. 路由配置

### 3.1 路由清单

| 路径 | 名称 | 组件 | 需要登录 | 管理员权限 |
|------|------|------|----------|------------|
| `/` | - | 重定向到 `/login` | 否 | - |
| `/login` | Login | LoginView.vue | 否 | - |
| `/register` | Register | RegisterView.vue | 否 | - |
| `/dashboard` | Dashboard | DashboardView.vue | 是 | 否 |
| `/chat` | AIChat | AIChatView.vue | 是 | 否 |
| `/profile` | Profile | ProfileView.vue | 是 | 否 |
| `/user-profile` | UserProfile | UserProfileView.vue | 是 | 否 |
| `/path` | LearningPath | LearningPathView.vue | 是 | 否 |
| `/resources` | Resources | ResourcesView.vue | 是 | 否 |
| `/settings` | Settings | SettingsView.vue | 是 | 否 |
| `/admin` | Admin | AdminView.vue | 是 | 是 |

### 3.2 路由守卫

前端使用全局路由守卫控制访问权限：

```javascript
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const userRole = localStorage.getItem('userRole') || 'student'

  if (to.meta.requiresAuth && !token) {
    next('/login')           // 未登录，重定向到登录页
  } else if (to.meta.admin && userRole !== 'admin') {
    next('/chat')            // 非管理员访问管理后台，重定向到对话页
  } else {
    next()                   // 正常放行
  }
})
```

### 3.3 路由懒加载

所有页面组件都使用懒加载，减少首屏加载时间：

```javascript
component: () => import('../views/AIChatView.vue')
```

---

## 4. 状态管理

### 4.1 Pinia Store

项目使用 Pinia 管理全局状态，主要的 Store 是 `user`：

```javascript
export const useUserStore = defineStore('user', {
  state: () => ({
    userInfo: null,           // 用户信息
    token: null,              // JWT Token
    learningProfile: {},      // 学习画像
    chatHistory: [],          // 对话历史
    learningResources: [],    // 学习资源
    learningPath: [],         // 学习路径
    sessionList: [],          // 会话列表
    currentSessionId: null,   // 当前会话ID
  }),
  actions: {
    login(loginForm)          // 登录
    register(username, password, nickname)  // 注册
    logout()                  // 退出登录
    fetchUserInfo()           // 获取用户信息
    fetchLearningProfile()    // 获取学习画像
    loadSessionList()         // 加载会话列表
    loadSessionConversations(sessionId)     // 加载会话内容
    deleteSession(sessionId)  // 删除会话
    startNewSession()         // 新建会话
  },
  getters: {
    isAuthenticated           // 是否已登录
    isAdmin                   // 是否管理员
    currentProfile            // 当前学习画像
  }
})
```

### 4.2 数据持久化

状态自动保存到 `localStorage`：

```javascript
// 示例：设置 Token
setToken(token) {
  this.token = token
  localStorage.setItem('token', token)
}
```

---

## 5. API 请求

### 5.1 Axios 配置

前端使用 Axios 封装 API 请求，配置了请求和响应拦截器：

**请求拦截器**：自动添加 Authorization Header

```javascript
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

**响应拦截器**：处理 401 未授权和业务错误

```javascript
api.interceptors.response.use(
  (response) => {
    // 处理业务错误码
    if (body.code !== 200) {
      return Promise.reject(new Error(body.msg))
    }
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

### 5.2 接口清单

| 函数名 | 方法 | 路径 | 说明 |
|--------|------|------|------|
| `login` | POST | `/user/login` | 用户登录 |
| `register` | POST | `/user/register` | 用户注册 |
| `getUserInfo` | GET | `/user/info` | 获取用户信息 |
| `getLearningProfile` | GET | `/portrait/me` | 获取学习画像 |
| `updateLearningProfile` | POST | `/portrait/update` | 更新学习画像 |
| `analyzeLearningStyle` | POST | `/portrait/analyze-style` | 分析学习风格 |
| `getSessionList` | GET | `/conversation/sessions` | 获取会话列表 |
| `getSessionConversations` | GET | `/conversation/session/{id}` | 获取会话内容 |
| `deleteSession` | DELETE | `/conversation/session/{id}` | 删除会话 |
| `chatStream` | POST | `/api/v1/chat/stream` | SSE 流式对话 |
| `getLearningResources` | GET | `/resources/courses` | 获取学习资源 |
| `getLearningPaths` | GET | `/learning-path/list` | 获取学习路径列表 |
| `fetchSettings` | GET | `/user/settings` | 获取用户设置 |
| `saveSettings` | PUT | `/user/settings` | 保存用户设置 |

### 5.3 SSE 流式对话

AI 对话使用 SSE（Server-Sent Events）实现实时消息推送：

```javascript
export async function chatStream(message, sessionId, onChunk, onDone, onError) {
  const response = await fetch(`${API_BASE_URL}/api/v1/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ user_content: message, session_id: sessionId })
  })
  
  const reader = response.body.getReader()
  // 逐块读取并解析 SSE 格式
}
```

---

## 6. 页面组件

### 6.1 页面说明

| 页面 | 说明 | 主要功能 |
|------|------|----------|
| **LoginView** | 登录页 | 用户名/密码登录、跳转注册 |
| **RegisterView** | 注册页 | 用户注册、自动登录 |
| **DashboardView** | 首页仪表盘 | 学习概览、快捷入口 |
| **AIChatView** | AI 对话页 | SSE 流式对话、会话管理、Markdown 渲染 |
| **ProfileView** | 用户画像页 | VARK 雷达图、知识基础、学习目标、薄弱点标签云 |
| **UserProfileView** | 用户信息页 | 用户基本信息、个人资料编辑 |
| **LearningPathView** | 学习路径页 | 时间线展示、学习步骤、统计面板 |
| **ResourcesView** | 学习资源页 | 课程列表、文件目录树、资源下载 |
| **SettingsView** | 系统设置页 | API 密钥配置、模型选择、个性化设置 |
| **AdminView** | 管理后台 | 用户管理、资源统计 |

### 6.2 布局组件

`Layout.vue` 是全局布局组件，包含：
- 顶部导航栏（Logo、导航链接、用户头像）
- 主内容区域
- 响应式设计

---

## 7. 样式系统

### 7.1 样式文件

| 文件 | 说明 |
|------|------|
| `src/assets/base.css` | 基础样式重置（normalize） |
| `src/assets/main.css` | 全局样式（主题色、字体等） |
| 组件内 `<style>` | 组件私有样式（Scoped） |

### 7.2 主题色

项目使用 Element Plus 默认主题，主要颜色：
- 主色：`#409EFF`（蓝色）
- 成功：`#67C23A`
- 警告：`#E6A23C`
- 危险：`#F56C6C`
- 信息：`#909399`

### 7.3 字体

- 中文：`PingFang SC`, `Microsoft YaHei`
- 英文：`Helvetica Neue`, `Arial`

---

## 8. 配置说明

### 8.1 环境变量

前端使用 `.env.development` 文件配置：

```env
# API 基础地址
VITE_API_BASE_URL=http://localhost:8000

# 登录接口路径
VITE_LOGIN_PATH=/user/login

# 用户信息接口路径
VITE_USER_INFO_PATH=/user/info

# 是否使用模拟登录（开发测试）
VITE_USE_MOCK_LOGIN=false
```

### 8.2 Vite 配置

`vite.config.js` 配置了：
- Vue 插件
- Vue DevTools 插件
- 路径别名 `@` 指向 `src/`

```javascript
export default defineConfig({
  plugins: [vue(), vueDevTools()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
```

### 8.3 JSConfig

`jsconfig.json` 配置了路径别名，支持 IDE 智能提示：

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

---

## 9. 启动方式

### 9.1 本地开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器（热更新）
npm run dev

# 访问地址：http://localhost:5173
```

### 9.2 构建生产版本

```bash
cd frontend

# 构建
npm run build

# 产物目录：dist/
```

### 9.3 代码格式化

```bash
npm run format
```

### 9.4 Docker 部署

```bash
cd docker
docker compose up -d
```

---

## 附录：核心文件说明

### main.js

应用入口，负责：
- 创建 Vue 应用
- 注册 Pinia
- 注册 Vue Router
- 导入 Element Plus
- 挂载到 DOM

### App.vue

根组件，包含全局布局和路由视图：

```vue
<template>
  <Layout>
    <router-view />
  </Layout>
</template>
```

### api/api.js

所有 API 接口的统一封装，包含：
- Axios 实例配置
- 请求/响应拦截器
- 所有业务接口定义
- SSE 流式对话实现