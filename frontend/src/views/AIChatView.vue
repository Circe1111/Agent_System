<template>
  <div class="chat-page">
    <!-- 左侧历史会话栏 -->
    <div class="chat-sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <el-button type="primary" @click="startNewChat" :disabled="isLoading" class="new-chat-btn">
          <el-icon><Plus /></el-icon>
          开启新对话
        </el-button>
        <el-button text @click="sidebarCollapsed = !sidebarCollapsed" class="toggle-btn">
          <el-icon><Fold v-if="!sidebarCollapsed" /><Expand v-else /></el-icon>
        </el-button>
      </div>
      <div class="session-list">
        <div v-if="sessionList.length === 0" class="empty-sessions">
          <span>暂无历史对话</span>
        </div>
        <div
          v-for="session in sessionList"
          :key="session.session_id"
          class="session-item"
          :class="{ active: currentSessionId === session.session_id }"
          @click="switchToSession(session.session_id)"
        >
          <div class="session-preview">{{ session.preview || '新对话' }}</div>
          <div class="session-meta">
            <span class="session-time">{{ formatSessionTime(session.last_time) }}</span>
            <span class="session-count">{{ session.msg_count }} 条消息</span>
          </div>
          <el-button
            text
            size="small"
            type="danger"
            class="delete-session-btn"
            @click.stop="handleDeleteSession(session.session_id)"
          >
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 右侧对话区 -->
    <div class="chat-main">
      <!-- 侧边栏收起后，显示展开按钮 -->
      <div v-if="sidebarCollapsed" class="expand-sidebar-btn" @click="sidebarCollapsed = false">
        <el-icon><Expand /></el-icon>
      </div>
      <div class="chat-header">
        <h2>AI学习助手</h2>
        <el-button type="danger" @click="clearChat" size="small" plain>清空当前对话</el-button>
      </div>

      <div class="chat-messages" ref="messagesContainer">
        <div v-if="chatHistory.length === 0" class="empty-chat">
          <el-empty description="开始与AI学习助手对话吧！" :image-size="120" />
        </div>

        <div v-if="isLoadingHistory" class="loading-history">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载历史对话中...</span>
        </div>

        <div
          v-for="(message, index) in chatHistory"
          :key="index"
          class="message"
          :class="{ 'user-message': message.role === 'user', 'ai-message': message.role === 'ai' }"
        >
          <template v-if="message.role === 'ai'">
            <div class="message-content ai-content" v-html="renderContent(message)" />
          </template>
          <template v-else>
            <div class="message-header user-header">
              <span class="role-name">{{ userStore.userInfo?.username || '我' }}</span>
              <el-avatar :size="32" :src="userAvatar">{{ userInitials }}</el-avatar>
            </div>
            <div class="message-content user-content" v-html="renderContent(message)" />
            <div class="message-time user-time">{{ formatTime(message.timestamp) }}</div>
          </template>
        </div>

        <div v-if="isLoading" class="loading-indicator">
          <div class="typing-bubble">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <div class="chat-input">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :autosize="{ minRows: 2, maxRows: 6 }"
          placeholder="输入您的问题..."
          @keydown.enter="handleEnter"
          ref="inputRef"
        />
        <el-button class="send-btn" @click="sendMessage" :loading="isLoading">
          发送
        </el-button>
      </div>

      <div class="suggestions">
        <span class="suggestion-title">快速提问：</span>
        <el-tag
          v-for="(suggestion, index) in suggestions"
          :key="index"
          type="info"
          size="small"
          style="margin-right: 8px; cursor: pointer"
          @click="useSuggestion(suggestion)"
        >
          {{ suggestion }}
        </el-tag>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import { useUserStore } from '@/stores'
import { ElMessage, ElMessageBox } from 'element-plus'
import { chatStream } from '@/api/api'
import { Plus, Fold, Expand, Delete, Loading } from '@element-plus/icons-vue'

const userStore = useUserStore()

const userAvatar = computed(() => userStore.userInfo?.avatar || '')
const userInitials = computed(() => {
  const name = userStore.userInfo?.username || ''
  return name.slice(0, 2).toUpperCase()
})

const inputMessage = ref('')
const isLoading = ref(false)
const isLoadingHistory = ref(false)
const messagesContainer = ref(null)
const inputRef = ref(null)
const sidebarCollapsed = ref(false)
const sessionId = ref(Date.now().toString())

const suggestions = [
  '如何构建我的学习画像？',
  '请为我规划人工智能基础课程的学习路径',
  '生成一个关于机器学习的练习题',
  '解释深度学习中的反向传播算法',
  '推荐一些适合初学者的学习资源',
]

const sessionList = computed(() => userStore.sessionList)
const currentSessionId = computed(() => userStore.currentSessionId)

// 渲染内容（支持Markdown和URL超链接）
const renderContent = (message) => {
  if (!message?.content) return ''
  const escapeHtml = (value) => value.replace(/[&<>"']/g, (ch) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]))
  let content = escapeHtml(message.content)
  const urlRegex = /https?:\/\/[^\s<>"']+/g
  content = content.replace(urlRegex, (url) => {
    return `<a href="${url}" target="_blank" style="color: #3182ce; text-decoration: underline;">${url}</a>`
  })
  content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  content = content.replace(/\*(.*?)\*/g, '<em>$1</em>')
  content = content.replace(/`(.*?)`/g, '<code>$1</code>')
  content = content.replace(/\n/g, '<br>')
  return content
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const formatSessionTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前'
  if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前'
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTo({
        top: messagesContainer.value.scrollHeight,
        behavior: 'smooth',
      })
    }
  })
}

// 开启新对话
const startNewChat = () => {
  userStore.startNewSession()
  sessionId.value = userStore.currentSessionId
  inputMessage.value = ''
  ElMessage.success('已开启新对话')
}

// 切换到历史会话
const switchToSession = async (sessId) => {
  if (isLoading.value) return
  await userStore.loadSessionConversations(sessId)
  sessionId.value = sessId
  scrollToBottom()
}

// 删除会话
const handleDeleteSession = async (sessId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个对话记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await userStore.deleteSession(sessId)
    if (userStore.currentSessionId === sessId) {
      sessionId.value = userStore.currentSessionId
    }
    ElMessage.success('对话已删除')
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 发送消息
const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message || isLoading.value) return

  if (!currentSessionId.value) {
    startNewChat()
  }

  const userMessage = {
    role: 'user',
    content: message,
    timestamp: new Date().toISOString(),
  }
  userStore.addChatMessage(userMessage)
  inputMessage.value = ''
  isLoading.value = true

  const aiMessage = {
    role: 'ai',
    content: '',
    timestamp: new Date().toISOString(),
  }
  userStore.addChatMessage(aiMessage)
  const aiIndex = userStore.chatHistory.length - 1

  scrollToBottom()

  chatStream(
    message,
    sessionId.value,
    (chunk) => {
      if (chunk.type === 'error') {
        ElMessage.error(chunk.msg || 'AI 服务暂时不可用，请稍后重试')
        return
      }
      let piece =
        chunk?.content ??
        chunk?.text ??
        chunk?.delta ??
        chunk?.message ??
        (typeof chunk === 'string' ? chunk : '')
      if (piece === undefined || piece === null) return
      piece = String(piece)

      piece = piece
        .replace(/\bdata:\s*/g, '')
        .replace(/\{\s*"type"\s*:\s*"delta"\s*,\s*"content"\s*:\s*/g, '')
        .replace(/\}\s*$/g, '')
        .replace(/^\s*[:]+\s*/g, '')

      if (!piece.trim()) return
      const current = userStore.chatHistory[aiIndex]
      if (current) {
        const nextContent = (current.content || '') + String(piece)
        userStore.chatHistory[aiIndex] = {
          ...current,
          content: nextContent,
          timestamp: new Date().toISOString(),
        }
        scrollToBottom()
      }
    },
    () => {
      isLoading.value = false
      refreshSessionList()
      scrollToBottom()
    },
    (err) => {
      console.error('chatStream error:', err)
      const current = userStore.chatHistory[aiIndex]
      if (current) {
        userStore.chatHistory[aiIndex] = {
          ...current,
          content: (current.content || '') + '\n\n[错误] AI 回复失败：' + (err?.message || '未知错误'),
          timestamp: new Date().toISOString(),
        }
      }
      ElMessage.error('AI 回复失败，请稍后重试')
      isLoading.value = false
    },
  )
}

// 刷新会话列表
const refreshSessionList = () => {
  userStore.loadSessionList()
}

// 处理回车键
const handleEnter = (event) => {
  if (event.shiftKey) return
  event.preventDefault()
  sendMessage()
}

// 清空当前对话
const clearChat = () => {
  userStore.clearChat()
  sessionId.value = Date.now().toString()
  userStore.setCurrentSessionId(sessionId.value)
  ElMessage.success('当前对话已清空')
}

// 使用建议
const useSuggestion = (suggestion) => {
  inputMessage.value = suggestion
  nextTick(() => {
    inputRef.value?.focus()
  })
}

// 获取聊天历史
const chatHistory = computed(() => userStore.chatHistory)

// 页面加载时初始化
onMounted(async () => {
  await userStore.loadSessionList()
  if (!currentSessionId.value) {
    userStore.startNewSession()
    sessionId.value = userStore.currentSessionId
  }
  scrollToBottom()
})
</script>

<style scoped>
.chat-page {
  height: calc(100vh - 120px);
  display: flex;
  gap: 0;
}

/* ===== 左侧历史会话栏 ===== */
.chat-sidebar {
  width: 280px;
  min-width: 280px;
  background: #f8fafc;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.chat-sidebar.collapsed {
  width: 0;
  min-width: 0;
  overflow: hidden;
  border-right: none;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.new-chat-btn {
  flex: 1;
  border-radius: 8px;
}

.toggle-btn {
  flex-shrink: 0;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.empty-sessions {
  text-align: center;
  color: #a0aec0;
  padding: 40px 16px;
  font-size: 0.9rem;
}

.session-item {
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  position: relative;
  transition: background 0.2s;
  margin-bottom: 4px;
}

.session-item:hover {
  background: #e8f4f8;
}

.session-item.active {
  background: #dbeafe;
  border: 1px solid #93c5fd;
}

.session-preview {
  font-size: 0.9rem;
  color: #2d3748;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding-right: 28px;
  margin-bottom: 4px;
}

.session-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #a0aec0;
}

.delete-session-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  opacity: 0;
  transition: opacity 0.2s;
}

.session-item:hover .delete-session-btn {
  opacity: 1;
}

/* ===== 右侧对话区 ===== */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  position: relative;
}

.expand-sidebar-btn {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 48px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-left: none;
  border-radius: 0 8px 8px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  transition: background 0.2s;
  color: #718096;
}

.expand-sidebar-btn:hover {
  background: #e8f4f8;
  color: #3182ce;
}

.chat-container {
  display: none;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  flex-shrink: 0;
}

.chat-header h2 {
  margin: 0;
  font-size: 1.2rem;
  color: #2d3748;
}

.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #f8fafc;
}

.loading-history {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  color: #718096;
}

.message {
  margin-bottom: 20px;
  width: fit-content;
  max-width: 80%;
  animation: fadeIn 0.3s ease;
}

.user-message {
  margin-left: auto;
}

.ai-message {
  margin-right: auto;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-header {
  justify-content: flex-end;
  margin-bottom: 8px;
}

.role-name {
  font-weight: bold;
  color: #2c5282;
}

.message-content {
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
  word-break: break-word;
}

.ai-content {
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.user-content {
  background-color: #63b3ed;
  color: white;
  border-top-right-radius: 4px;
}

.message-time {
  text-align: right;
  font-size: 0.8rem;
  color: #718096;
  margin-top: 5px;
}

.chat-input {
  display: flex;
  padding: 20px;
  background-color: white;
  border-top: 1px solid #e9ecef;
  flex-shrink: 0;
  gap: 8px;
}

.send-btn {
  background: #1253D2;
  border-color: #1253D2;
  color: #ffffff;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.send-btn:hover {
  background: #0e45b0;
  border-color: #0e45b0;
}

.send-btn:active {
  background: #0b378f;
  border-color: #0b378f;
}

.suggestions {
  padding: 0 20px 20px;
  flex-shrink: 0;
}

.suggestion-title {
  color: #718096;
  margin-right: 10px;
}

.loading-indicator {
  padding: 10px;
  margin-bottom: 20px;
}

.typing-bubble {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  background: white;
  border-radius: 999px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.typing-bubble span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #63b3ed;
  animation: bounce 1.2s infinite ease-in-out;
}

.typing-bubble span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-bubble span:nth-child(3) {
  animation-delay: 0.4s;
}

.empty-chat {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0.6); }
  40% { transform: scale(1); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>