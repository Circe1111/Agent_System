<template>
  <div class="chat-container">
    <div class="chat-header">
      <h2>AI学习助手</h2>
      <el-button type="danger" @click="clearChat" size="small">清空对话</el-button>
    </div>

    <div class="chat-messages" ref="messagesContainer">
      <div v-if="chatHistory.length === 0" class="empty-chat">
        <el-empty description="开始与AI学习助手对话吧！">
          <el-button type="primary" @click="sendInitialMessage">开始对话</el-button>
        </el-empty>
      </div>

      <div
        v-for="(message, index) in chatHistory"
        :key="index"
        class="message"
        :class="{ 'user-message': message.role === 'user', 'ai-message': message.role === 'ai' }"
      >
        <div class="message-header">
          <el-avatar :size="32" :icon="message.role === 'user' ? 'User' : 'ChatDotRound'" />
          <span class="role-name">{{ message.role === 'user' ? '我' : 'AI助手' }}</span>
        </div>

        <div class="message-content" v-html="renderContent(message)" />

        <div class="message-time">{{ formatTime(message.timestamp) }}</div>
      </div>

      <div v-if="isLoading" class="loading-indicator">
        <el-skeleton :rows="2" animated />
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
      <el-button type="primary" @click="sendMessage" :loading="isLoading" style="margin-left: 10px">
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
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { useUserStore } from '@/stores'
import { ElMessage } from 'element-plus'
import { chatStream } from '@/api/api'

const userStore = useUserStore()
const inputMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref(null)
const inputRef = ref(null)
// 单个 SSE 会话 ID，跨多次发送复用，便于后端做多轮上下文
const sessionId = ref(Date.now().toString())

const suggestions = [
  '如何构建我的学习画像？',
  '请为我规划人工智能基础课程的学习路径',
  '生成一个关于机器学习的练习题',
  '解释深度学习中的反向传播算法',
  '推荐一些适合初学者的学习资源',
]

// 渲染内容（支持Markdown）
const renderContent = (message) => {
  let content = message.content
  // 简单的Markdown渲染
  content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  content = content.replace(/\*(.*?)\*/g, '<em>$1</em>')
  content = content.replace(/`(.*?)`/g, '<code>$1</code>')
  content = content.replace(/\n/g, '<br>')
  return content
}

// 格式化时间
const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 发送消息
const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message || isLoading.value) return

  // 添加用户消息
  const userMessage = {
    role: 'user',
    content: message,
    timestamp: new Date().toISOString(),
  }
  userStore.addChatMessage(userMessage)
  inputMessage.value = ''
  isLoading.value = true

  // 先插入一个空的 AI 消息占位，stream 时持续 append 内容
  const aiMessage = {
    role: 'ai',
    content: '',
    timestamp: new Date().toISOString(),
  }
  userStore.addChatMessage(aiMessage)
  const aiIndex = userStore.chatHistory.length - 1

  nextTick(() => {
    scrollToBottom()
  })

  // 用 chatStream 走真实 SSE，onChunk 时追加到刚插入的 AI 消息
  chatStream(
    message,
    sessionId.value,
    (chunk) => {
      if (chunk.type === 'error') {
        ElMessage.error(chunk.msg || 'AI 服务暂时不可用，请稍后重试')
        return
      }
      // 兼容多种后端字段：content / text / delta / message
      const piece =
        chunk.content ??
        chunk.text ??
        chunk.delta ??
        chunk.message ??
        (typeof chunk === 'string' ? chunk : '')
      if (!piece) return
      const current = userStore.chatHistory[aiIndex]
      if (current) {
        current.content = (current.content || '') + piece
        // 触发 store 内的 chatHistory 响应式更新（push 后已生效，但原地修改需重写）
        userStore.chatHistory.splice(aiIndex, 1, { ...current })
        nextTick(() => {
          scrollToBottom()
        })
      }
    },
    () => {
      // onDone
      isLoading.value = false
      nextTick(() => {
        scrollToBottom()
      })
    },
    (err) => {
      // onError
      console.error('chatStream error:', err)
      const current = userStore.chatHistory[aiIndex]
      if (current) {
        current.content =
          (current.content || '') +
          '\n\n[错误] AI 回复失败：' + (err?.message || '未知错误')
        userStore.chatHistory.splice(aiIndex, 1, { ...current })
      }
      ElMessage.error('AI 回复失败，请稍后重试')
      isLoading.value = false
    },
  )
}

// 处理回车键
const handleEnter = (event) => {
  if (event.shiftKey) return // Shift+Enter 换行
  event.preventDefault()
  sendMessage()
}

// 清空对话
const clearChat = () => {
  userStore.clearChat()
  ElMessage.success('对话已清空')
}

// 使用建议
const useSuggestion = (suggestion) => {
  inputMessage.value = suggestion
  nextTick(() => {
    inputRef.value?.focus()
  })
}

// 初始消息
const sendInitialMessage = () => {
  inputMessage.value =
    '你好！我是您的AI学习助手。请告诉我您想学习什么内容，或者有什么问题需要帮助？'
  sendMessage()
}

// 获取聊天历史
const chatHistory = computed(() => userStore.chatHistory)

// 自动滚动到底部
nextTick(() => {
  scrollToBottom()
})
</script>

<style scoped>
.chat-container {
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #f8fafc;
}

.message {
  margin-bottom: 20px;
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
  margin-bottom: 8px;
}

.role-name {
  margin-left: 10px;
  font-weight: bold;
  color: #2c5282;
}

.message-content {
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
}

.user-message .message-content {
  background-color: #63b3ed;
  color: white;
  border-top-right-radius: 4px;
}

.ai-message .message-content {
  background-color: white;
  border: 1px solid #e2e8f0;
  border-top-left-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
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
}

.suggestions {
  padding: 0 20px 20px;
  border-top: 1px solid #e9ecef;
}

.suggestion-title {
  color: #718096;
  margin-right: 10px;
}

.loading-indicator {
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 20px;
}

.empty-chat {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
