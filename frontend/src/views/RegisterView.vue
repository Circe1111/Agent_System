<template>
  <div class="register-container">
    <div class="header">
      <div class="logo">
        <span class="logo-icon">EA</span>
        <div class="logo-text">
          <span class="logo-title">Edu_Agent</span>
          <span class="logo-subtitle">AI-POWERED LEARNING PLATFORM</span>
        </div>
      </div>
      <div class="welcome-text">注册 Edu_Agent 账号</div>
    </div>

    <div class="register-card-wrapper">
      <el-card class="register-card">
        <div class="card-header">
          <h3>创建账号</h3>
          <p>注册您的学习账户</p>
        </div>

        <el-form
          :model="registerForm"
          :rules="rules"
          ref="registerFormRef"
          label-width="0"
          class="register-form"
        >
          <el-form-item prop="username">
            <el-input
              v-model="registerForm.username"
              placeholder="请输入用户名"
              prefix-icon="User"
              clearable
              class="register-input"
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="registerForm.password"
              type="password"
              placeholder="请输入密码"
              prefix-icon="Lock"
              show-password
              clearable
              class="register-input"
            />
          </el-form-item>

          <el-form-item prop="confirmPassword">
            <el-input
              v-model="registerForm.confirmPassword"
              type="password"
              placeholder="请再次输入密码"
              prefix-icon="Lock"
              show-password
              clearable
              class="register-input"
            />
          </el-form-item>

          <el-form-item prop="nickname">
            <el-input
              v-model="registerForm.nickname"
              placeholder="请输入昵称（选填）"
              prefix-icon="UserFilled"
              clearable
              class="register-input"
            />
          </el-form-item>

          <el-form-item>
            <el-button class="register-btn" @click="handleRegister" :loading="loading">
              注册
            </el-button>
          </el-form-item>

          <div class="login-link">
            <span>已有账号？</span>
            <el-link type="primary" @click="goToLogin">去登录</el-link>
          </div>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores'
import { ElMessage } from 'element-plus'
import { User, Lock, UserFilled } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const registerFormRef = ref(null)
const loading = ref(false)

const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  nickname: '',
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' },
  ],
  nickname: [
    { max: 20, message: '昵称长度不能超过 20 个字符', trigger: 'blur' },
  ],
}

const handleRegister = async () => {
  if (!registerFormRef.value) return

  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.register(
          registerForm.username,
          registerForm.password,
          registerForm.nickname
        )
        ElMessage.success('注册成功，已自动登录！')
      } catch (error) {
        const msg = error?.message || '注册失败，请稍后重试'
        ElMessage.error(msg)
        console.error('register error:', error)
      } finally {
        loading.value = false
      }
    }
  })
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.register-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #ffffff;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  background: #ffffff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  position: relative;
  z-index: 1;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 48px;
  height: 48px;
  background: #1253D2;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-weight: bold;
  font-size: 20px;
  box-shadow: 0 4px 12px rgba(18, 83, 210, 0.25);
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.logo-title {
  font-size: 20px;
  font-weight: bold;
  color: #1a365d;
}

.logo-subtitle {
  font-size: 10px;
  color: #5a7a9a;
  letter-spacing: 1px;
}

.welcome-text {
  font-size: 18px;
  color: #1a365d;
  font-weight: 500;
}

.register-card-wrapper {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
}

.register-card {
  width: 480px;
  border-radius: 16px;
  box-shadow: 0 2px 60px rgba(0, 0, 0,0.2);
}

.card-header {
  text-align: center;
  padding: 20px 0 10px;
}

.card-header h3 {
  margin: 0 0 8px 0;
  color: #1a365d;
  font-size: 1.5rem;
}

.card-header p {
  margin: 0;
  color: #718096;
  font-size: 0.9rem;
}

.register-form {
  padding: 10px 40px 30px;
}

.register-input {
  height: 44px;
}

.register-input :deep(.el-input__wrapper) {
  background: #ffffff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.10), 0 1px 4px rgba(0, 0, 0, 0.06);
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

.register-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.14), 0 2px 6px rgba(0, 0, 0, 0.08);
  border-color: #cbd5e0;
}

.register-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 6px 28px rgba(18, 83, 210, 0.25), 0 2px 8px rgba(18, 83, 210, 0.15);
  border-color: #1253D2;
}

.register-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  background: #1253D2;
  border-color: #1253D2;
  color: #ffffff;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.register-btn:hover {
  background: #0e45b0;
  border-color: #0e45b0;
}

.register-btn:active {
  background: #0b378f;
  border-color: #0b378f;
}

.register-btn.is-loading {
  background: #1253D2;
  border-color: #1253D2;
}

.login-link {
  text-align: center;
  margin-top: 10px;
  color: #718096;
  font-size: 0.9rem;
}
</style>