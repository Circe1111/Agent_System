<template>
  <div class="login-container">
    <div class="header">
      <div class="logo">
        <span class="logo-icon">EA</span>
        <div class="logo-text">
          <span class="logo-title">Edu_Agent</span>
          <span class="logo-subtitle">AI-POWERED LEARNING PLATFORM</span>
        </div>
      </div>
      <div class="welcome-text">欢迎登录 Edu_Agent</div>
    </div>

    <div class="main-content">
      <div class="login-card">
        <div class="card-header">
          <h3>账号登录</h3>
          <p>欢迎回来，请登录您的账号</p>
        </div>

        <el-form
          :model="loginForm"
          :rules="rules"
          ref="loginFormRef"
          label-width="0"
          class="login-form"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="用户名/邮箱/手机号"
              prefix-icon="User"
              clearable
              class="login-input"
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="密码"
              prefix-icon="Lock"
              show-password
              clearable
              class="login-input"
            />
          </el-form-item>

          <div class="form-options">
            <el-checkbox v-model="rememberMe">记住我</el-checkbox>
            <el-link type="primary" @click="handleForgotPassword">忘记密码?</el-link>
          </div>

          <el-form-item>
            <el-button type="primary" style="width: 100%; height: 44px; font-size: 16px;" @click="handleLogin" :loading="loading">
              立即登录
            </el-button>
          </el-form-item>

          <div class="register-link">
            <span>还没有账号？</span>
            <el-link type="primary" @click="handleRegister">注册账号</el-link>
          </div>
        </el-form>

        <div class="demo-login">
          <p>演示账号：</p>
          <el-tag type="success">学生：student1 / 123456</el-tag>
          <el-tag type="warning">管理员：admin / admin123</el-tag>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const loginFormRef = ref(null)
const loading = ref(false)
const rememberMe = ref(true)

const loginForm = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' },
  ],
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true

      try {
        await userStore.login(loginForm)
        userStore.setLearningProfile({
          knowledgeBase: 60,
          cognitiveStyle: '视觉型',
          errorPreferences: ['概念理解', '计算错误'],
          learningGoals: '掌握人工智能基础知识',
          preferredLearningStyle: '案例学习',
          currentProgress: 30,
        })
        ElMessage.success('登录成功！')
      } catch (error) {
        const msg = error?.message || '登录失败，请检查账号密码或后端接口'
        ElMessage.error(msg)
        console.error('login error:', error)
      } finally {
        loading.value = false
      }
    }
  })
}

const handleRegister = () => {
  router.push('/register')
}

const handleForgotPassword = () => {
  ElMessage.info('忘记密码功能开发中')
}
</script>

<style scoped>
.login-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  background: rgba(255, 255, 255, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 48px;
  height: 48px;
  background: white;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #667eea;
  font-size: 20px;
  font-weight: bold;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.logo-title {
  font-size: 20px;
  font-weight: bold;
  color: white;
}

.logo-subtitle {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.7);
  letter-spacing: 1px;
}

.welcome-text {
  font-size: 18px;
  color: white;
  font-weight: 500;
}

.main-content {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
}

.login-card {
  width: 420px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  padding: 35px;
}

.card-header {
  text-align: center;
  margin-bottom: 30px;
}

.card-header h3 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #1a365d;
  font-weight: bold;
}

.card-header p {
  margin: 0;
  color: #718096;
  font-size: 14px;
}

.login-form {
  padding: 0;
}

.login-input {
  height: 48px;
  border-radius: 10px;
  font-size: 15px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 18px 0;
}

.register-link {
  text-align: center;
  color: #718096;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.demo-login {
  margin-top: 20px;
  padding: 18px;
  background-color: #f0f9ff;
  border-radius: 10px;
  text-align: center;
}

.demo-login p {
  margin: 0 0 12px 0;
  color: #4a5568;
  font-weight: bold;
  font-size: 14px;
}

.demo-login .el-tag {
  margin: 6px;
  font-size: 12px;
}
</style>