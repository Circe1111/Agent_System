import { defineStore } from 'pinia'
import { login, register, getUserInfo, getSessionList, getSessionConversations, deleteSession as deleteSessionApi, getLearningProfile } from '@/api/api'
import { ElMessage } from 'element-plus'
import router from '@/router'

export const useUserStore = defineStore('user', {
  state: () => {
    const savedToken = localStorage.getItem('token')
    const savedUserInfo = localStorage.getItem('userInfo')
    const userId = savedUserInfo ? (JSON.parse(savedUserInfo).id || JSON.parse(savedUserInfo).username || 'anonymous') : 'anonymous'
    const prefix = `user_${userId}_`

    const savedProfile = localStorage.getItem(prefix + 'learningProfile')
    const savedChat = localStorage.getItem(prefix + 'chatHistory')
    return {
      userInfo: savedUserInfo ? JSON.parse(savedUserInfo) : null,
      token: savedToken || null,
      learningProfile: savedProfile ? JSON.parse(savedProfile) : {
        knowledgeBase: 0,
        cognitiveStyle: '',
        errorPreferences: [],
        learningGoals: '',
        preferredLearningStyle: '',
        currentProgress: 0,
      },
      chatHistory: savedChat ? JSON.parse(savedChat) : [],
      learningResources: [],
      learningPath: [],
      sessionList: [],
      currentSessionId: null,
      isLoadingHistory: false,
    }
  },
  actions: {
    _lsKey(base) {
      const uid = this.userInfo?.id || this.userInfo?.username || 'anonymous'
      return `user_${uid}_${base}`
    },
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
      localStorage.setItem(this._lsKey('learningProfile'), JSON.stringify(profile))
    },
    addChatMessage(message) {
      this.chatHistory.push(message)
      localStorage.setItem(this._lsKey('chatHistory'), JSON.stringify(this.chatHistory))
    },
    clearChat() {
      this.chatHistory = []
      localStorage.removeItem(this._lsKey('chatHistory'))
    },
    setLearningResources(resources) {
      this.learningResources = resources
      localStorage.setItem(this._lsKey('learningResources'), JSON.stringify(resources))
    },
    setLearningPath(path) {
      this.learningPath = path
      localStorage.setItem(this._lsKey('learningPath'), JSON.stringify(path))
    },

    // ===== 会话管理方法 =====
    setCurrentSessionId(sessionId) {
      this.currentSessionId = sessionId
    },

    startNewSession() {
      this.currentSessionId = Date.now().toString()
      this.chatHistory = []
      localStorage.removeItem(this._lsKey('chatHistory'))
    },

    async loadSessionList() {
      try {
        const res = await getSessionList()
        const payload = res?.data || {}
        this.sessionList = payload.data?.sessions || payload.sessions || []
      } catch (err) {
        console.warn('加载会话列表失败：', err?.message || err)
      }
    },

    async loadSessionConversations(sessionId) {
      this.isLoadingHistory = true
      try {
        const res = await getSessionConversations(sessionId)
        const payload = res?.data || {}
        const conversations = payload.data || payload
        const list = Array.isArray(conversations) ? conversations : (conversations?.list || [])
        this.chatHistory = list.map(item => ({
          role: item.role === 'assistant' ? 'ai' : 'user',
          content: item.content,
          timestamp: item.create_time || new Date().toISOString(),
        }))
        this.currentSessionId = sessionId
        localStorage.setItem(this._lsKey('chatHistory'), JSON.stringify(this.chatHistory))
      } catch (err) {
        console.warn('加载会话对话失败：', err?.message || err)
      } finally {
        this.isLoadingHistory = false
      }
    },

    async deleteSession(sessionId) {
      try {
        await deleteSessionApi(sessionId)
        this.sessionList = this.sessionList.filter(s => s.session_id !== sessionId)
        if (this.currentSessionId === sessionId) {
          this.startNewSession()
        }
      } catch (err) {
        console.warn('删除会话失败：', err?.message || err)
      }
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
        await this.fetchLearningProfile()
        router.push('/chat')
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

    // ===== 获取用户画像 =====
    async fetchLearningProfile() {
      if (!this.token) return
      try {
        const res = await getLearningProfile()
        const payload = res?.data || {}
        const portrait = payload.data?.portrait || payload.portrait || payload.data || payload
        
        console.log('[fetchLearningProfile] 后端返回画像:', portrait)
        
        if (portrait && typeof portrait === 'object') {
          const rawJson = portrait.raw_json || {}
          const frontendProfile = {
            knowledgeBase: typeof portrait.knowledge_level === 'string' ? 
              (parseInt(portrait.knowledge_level) || 65) : (portrait.knowledge_level || 65),
            cognitiveStyle: portrait.learning_preference || portrait.cognitiveStyle || '',
            errorPreferences: portrait.weak_knowledge ? 
              (typeof portrait.weak_knowledge === 'string' ? 
                portrait.weak_knowledge.split(',').filter(Boolean) : []) : [],
            learningGoals: portrait.study_goal || portrait.learningGoals || '',
            preferredLearningStyle: portrait.learning_style || portrait.preferredLearningStyle || '',
            currentProgress: portrait.knowledge_level ? 
              (parseInt(portrait.knowledge_level) || 50) : 50,
            varkScores: rawJson.vark_scores || null,
            varkHistory: rawJson.vark_history || [],
            rawJson: rawJson,
          }
          console.log('[fetchLearningProfile] 转换后前端格式:', frontendProfile)
          this.setLearningProfile(frontendProfile)
        } else {
          console.warn('[fetchLearningProfile] 后端返回格式不对:', portrait)
        }
      } catch (err) {
        console.error('[fetchLearningProfile] 获取失败:', err)
        ElMessage.warning('获取用户偏好失败，请刷新页面重试')
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
      this.sessionList = []
      this.currentSessionId = null
      this.isLoadingHistory = false

      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
    },
  },
  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.userInfo?.role === 'admin',
    currentProfile: (state) => state.learningProfile,
  },
})