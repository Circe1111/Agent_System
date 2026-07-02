import { defineStore } from 'pinia'
import { login, register, getUserInfo } from '@/api/api'
import router from '@/router'

export const useUserStore = defineStore('user', {
  state: () => ({
    userInfo: null,
    token: null,
    learningProfile: {
      knowledgeBase: 0,
      cognitiveStyle: '',
      errorPreferences: [],
      learningGoals: '',
      preferredLearningStyle: '',
      currentProgress: 0,
    },
    chatHistory: [],
    learningResources: [],
    learningPath: [],
  }),
  actions: {
    // ----- 原有的方法（保留不动） -----
    setUserInfo(userInfo) {
      this.userInfo = userInfo
      localStorage.setItem('userInfo', JSON.stringify(userInfo))
    },
    setToken(token) {
      this.token = token
      localStorage.setItem('token', token)
    },
    setLearningProfile(profile) {
      this.learningProfile = profile
      localStorage.setItem('learningProfile', JSON.stringify(profile))
    },
    addChatMessage(message) {
      this.chatHistory.push(message)
      localStorage.setItem('chatHistory', JSON.stringify(this.chatHistory))
    },
    clearChat() {
      this.chatHistory = []
      localStorage.removeItem('chatHistory')
    },
    setLearningResources(resources) {
      this.learningResources = resources
      localStorage.setItem('learningResources', JSON.stringify(resources))
    },
    setLearningPath(path) {
      this.learningPath = path
      localStorage.setItem('learningPath', JSON.stringify(path))
    },

    // ===== 登录方法 =====
    async login(loginForm) {
      try {
        const res = await login(loginForm.username, loginForm.password)
        const payload = res?.data || {}
        const token = payload.token
          || payload.accessToken
          || payload.access_token
          || payload.data?.token
          || payload.data?.accessToken
          || payload.data?.access_token
          || payload.data?.data?.token
          || payload.data?.data?.accessToken
          || payload.data?.data?.access_token

        if (!token) {
          throw new Error('登录接口未返回 token')
        }

        this.setToken(token)
        await this.fetchUserInfo()
        router.push('/dashboard')
        return Promise.resolve(res)
      } catch (error) {
        return Promise.reject(error)
      }
    },

    // ===== 注册方法 =====
    async register(username, password, nickname) {
      const res = await register(username, password, nickname || '')
      if (res.data.code === 200) {
        // Auto-login after successful registration
        await this.login({ username, password })
      }
    },

    // ===== 获取用户信息方法 =====
    async fetchUserInfo() {
      if (!this.token) return
      try {
        const res = await getUserInfo()
        const payload = res?.data || {}
        const userInfo = payload.user || payload.data?.user || payload.data?.data?.user || payload.data || payload.data?.data || payload
        this.setUserInfo(userInfo)
        return Promise.resolve(res)
      } catch (error) {
        return Promise.reject(error)
      }
    },

    // ----- 原有的 logout（保留不动） -----
    logout() {
      this.userInfo = null
      this.token = null
      this.learningProfile = {
        knowledgeBase: 0,
        cognitiveStyle: '',
        errorPreferences: [],
        learningGoals: '',
        preferredLearningStyle: '',
        currentProgress: 0,
      }
      this.chatHistory = []
      this.learningResources = []
      this.learningPath = []

      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      localStorage.removeItem('learningProfile')
      localStorage.removeItem('chatHistory')
      localStorage.removeItem('learningResources')
      localStorage.removeItem('learningPath')
    },
  },
  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.userInfo?.role === 'admin',
    currentProfile: (state) => state.learningProfile,
  },
})
