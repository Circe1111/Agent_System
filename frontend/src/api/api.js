import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const LOGIN_PATH = import.meta.env.VITE_LOGIN_PATH || '/user/login'
const USER_INFO_PATH = import.meta.env.VITE_USER_INFO_PATH || '/user/info'
const USE_MOCK_LOGIN = import.meta.env.VITE_USE_MOCK_LOGIN !== 'false'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器（自动塞Token）
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// 响应拦截器（处理401和业务错误码）
api.interceptors.response.use(
  (response) => {
    // 如果后端返回的 code !== 0，说明业务失败
    if (response.data.code !== undefined && response.data.code !== 0) {
      console.error('业务错误:', response.data.msg)
      return Promise.reject(new Error(response.data.msg || '请求失败'))
    }
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

// ====== 以下是实际调用的接口 ======

// 1. 登录接口：默认请求后端 /auth/login
export const login = (username, password) => {
  if (USE_MOCK_LOGIN) {
    console.log('[单机模式] 登录账号:', username, '密码:', password)
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          data: {
            token: 'fake-token-123456',
          },
        })
      }, 500)
    })
  }

  return api.post(LOGIN_PATH, null, {
    params: {
      username,
      password,
    },
  })
}

// 2. 获取当前用户信息：默认请求后端 /auth/me
export const getUserInfo = () => {
  if (USE_MOCK_LOGIN) {
    console.log('[单机模式] 获取用户信息')
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          data: {
            id: 1,
            username: '前端测试员',
            role: 'admin',
            avatar: 'https://picsum.photos/200',
            email: 'test@example.com',
          },
        })
      }, 300)
    })
  }

  return api.get(USER_INFO_PATH)
}

// ====== 以下接口暂时保留，等C的其他模块文件出来后再改 ======
// （D的AI接口、资源接口等，目前路径不确定，先留着占位）

// 获取学习画像
export const getLearningProfile = (userId) => {
  return api.get(`/profiles/${userId}`)
}

// 更新学习画像
export const updateLearningProfile = (userId, profile) => {
  return api.put(`/profiles/${userId}`, profile)
}

// 发送AI对话消息
export const sendAIChatMessage = (message, context = {}) => {
  return api.post('/ai/chat', { message, context })
}

// 获取学习资源
export const getLearningResources = (filters = {}) => {
  return api.get('/resources', { params: filters })
}

// 生成学习路径
export const generateLearningPath = (profile) => {
  return api.post('/path/generate', profile)
}

// 管理后台 - 获取用户列表
export const getUsers = () => {
  return api.get('/admin/users')
}

// 管理后台 - 获取资源统计
export const getResourceStats = () => {
  return api.get('/admin/stats/resources')
}

export default api
