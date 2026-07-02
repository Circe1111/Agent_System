import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const LOGIN_PATH = import.meta.env.VITE_LOGIN_PATH || '/user/login'
const USER_INFO_PATH = import.meta.env.VITE_USER_INFO_PATH || '/user/info'
const USE_MOCK_LOGIN = import.meta.env.VITE_USE_MOCK_LOGIN === 'true'

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
    const body = response.data
    if (body && body.code !== undefined && body.code !== 200) {
      console.error('业务错误:', body.msg)
      return Promise.reject(new Error(body.msg || '请求失败'))
    }
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }

    const status = error.response?.status
    const msg = error.response?.data?.msg || error.message || '请求失败'
    const wrappedError = new Error(msg)
    wrappedError.status = status
    wrappedError.originalError = error
    return Promise.reject(wrappedError)
  },
)

// ====== 以下是实际调用的接口 ======

// 1. 登录接口：默认请求后端 /user/login
// 后端返回: { access_token, token_type: "bearer" }
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

  // 后端使用 application/x-www-form-urlencoded（OAuth2 Password Flow）
  // 通过 URLSearchParams 发送 username / password
  const formBody = new URLSearchParams()
  formBody.append('username', username)
  formBody.append('password', password)

  return api.post(LOGIN_PATH, formBody, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  }).then((response) => {
    const body = response?.data || {}
    if (body?.data?.token) {
      response.data = {
        ...body,
        token: body.data.token,
      }
    }
    return response
  })
}

// 1.5 注册接口：POST /user/register
// 后端使用 JSON body（UserCreate Pydantic 模型），与登录的 form-urlencoded 不同
export const register = (username, password, nickname) => {
  return api.post('/user/register', { username, password, nickname })
}

// 2. 获取当前用户信息：默认请求后端 /user/info
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

// 3. 获取当前用户的学习画像：GET /portrait/me
export const getLearningProfile = () => {
  return api.get('/portrait/me')
}

// 4. 更新学习画像：POST /portrait/update
export const updateLearningProfile = (profile) => {
  return api.post('/portrait/update', profile)
}

// 5. AI 对话（SSE 流式）：POST /api/v1/chat/stream
// EventSource 不支持 POST，所以用 fetch + ReadableStream 手写解析
// 入参:
//   message    - 用户消息
//   sessionId  - 会话ID（可空，空时由前端生成）
//   onChunk    - 每段 chunk 到达时的回调 (data) => {}
//   onDone     - 流结束回调 () => {}
//   onError    - 错误回调 (err) => {}
export async function chatStream(message, sessionId, onChunk, onDone, onError) {
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`${API_BASE_URL}/api/v1/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
      },
      body: JSON.stringify({
        user_content: message,
        session_id: sessionId || Date.now().toString(),
      }),
    })

    if (!response.ok) {
      const err = new Error('HTTP ' + response.status)
      if (onError) onError(err)
      return
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) {
        if (buffer) {
          processChunk(buffer)
        }
        if (onDone) onDone()
        break
      }
      buffer += decoder.decode(value, { stream: true })
      const segments = buffer.split(/\r?\n\r?\n/)
      buffer = segments.pop() || ''
      for (const segment of segments) {
        processChunk(segment)
      }
    }

    function processChunk(chunk) {
      const lines = String(chunk)
        .split(/\r?\n/)
        .map((line) => line.trim())
        .filter((line) => line && !line.startsWith(':'))

      for (const line of lines) {
        const payload = parseSseLine(line)
        if (!payload || !onChunk) continue

        if (typeof payload === 'object' && payload !== null) {
          onChunk(payload)
        } else if (typeof payload === 'string') {
          onChunk({ content: payload })
        }
      }
    }

    function parseSseLine(raw) {
      let text = String(raw).trim()
      if (!text) return null

      if (text.startsWith('data:')) {
        text = text.slice(5).trim()
      }
      if (!text) return null

      if (text.startsWith('data:')) {
        return parseSseLine(text)
      }

      try {
        return JSON.parse(text)
      } catch {
        const jsonStart = text.indexOf('{')
        const jsonEnd = text.lastIndexOf('}')
        if (jsonStart >= 0 && jsonEnd > jsonStart) {
          try {
            return JSON.parse(text.slice(jsonStart, jsonEnd + 1))
          } catch {
            // fall through
          }
        }
      }

      return text
    }
  } catch (err) {
    if (onError) onError(err)
    else console.error('chatStream error:', err)
  }
}
// ====== 以下接口暂时保留，等C的其他模块文件出来后再改 ======
// （D的AI接口、资源接口等，目前路径不确定，先留着占位）

// 发送AI对话消息（非流式，保留作为回退）
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

// 获取用户 LLM 设置：GET /user/settings
export const fetchSettings = () => api.get('/user/settings')

// 保存用户 LLM 设置：PUT /user/settings
export const saveSettings = (data) => api.put('/user/settings', data)

export default api
