<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>智学系统</h2>
          <p>基于大模型的个性化学习平台</p>
        </div>
      </template>

      <el-form
        :model="loginForm"
        :rules="rules"
        ref="loginFormRef"
        label-width="80px"
        class="login-form"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            prefix-icon="User"
            clearable
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" style="width: 100%" @click="handleLogin" :loading="loading">
            登录
          </el-button>
        </el-form-item>

        <div class="other-options">
          <el-checkbox v-model="rememberMe">记住我</el-checkbox>
          <el-link type="primary" @click="handleRegister">注册账号</el-link>
        </div>
      </el-form>

      <div class="demo-login">
        <p>演示账号：</p>
        <el-tag type="success">学生：student1 / 123456</el-tag>
        <el-tag type="warning">管理员：admin / admin123</el-tag>
      </div>
    </el-card>
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
        ElMessage.error(error?.message || '登录失败，请检查账号密码或后端接口')
        console.error(error)
      } finally {
        loading.value = false
      }
    }
  })
}

const handleRegister = () => {
  ElMessage.info('注册功能开发中，请联系管理员')
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 450px;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.card-header {
  text-align: center;
  padding: 20px 0;
}

.card-header h2 {
  margin: 0 0 10px 0;
  color: #1a365d;
  font-size: 2rem;
}

.card-header p {
  margin: 0;
  color: #718096;
  font-size: 0.9rem;
}

.login-form {
  padding: 20px 40px;
}

.other-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  padding: 0 10px;
}

.demo-login {
  margin-top: 20px;
  padding: 15px;
  background-color: #f0f9ff;
  border-radius: 8px;
  text-align: center;
}

.demo-login p {
  margin: 0 0 10px 0;
  color: #4a5568;
  font-weight: bold;
}

.demo-login .el-tag {
  margin: 5px;
}
</style>
