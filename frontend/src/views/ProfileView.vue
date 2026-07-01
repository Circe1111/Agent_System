<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <el-col :xs="24" :lg="8">
        <el-card class="user-card">
          <div class="card-title-row">
            <span class="card-title">用户信息</span>
            <el-button type="danger" plain @click="handleLogout">退出登录</el-button>
          </div>

          <div class="avatar-section">
            <el-avatar :size="96" :src="userAvatar" class="user-avatar">
              {{ userInitials }}
            </el-avatar>
            <div class="user-summary">
              <h2>{{ userInfo.username }}</h2>
              <div class="user-badges">
                <el-tag :type="roleTagType">{{ roleText }}</el-tag>
                <el-tag type="success">{{
                  userInfo.role === 'admin' ? '管理员' : '学习者'
                }}</el-tag>
              </div>
              <p class="user-bio">{{ userInfo.bio || '这个人还没有填写简介。' }}</p>
            </div>
          </div>

          <div class="contact-list">
            <div class="contact-item">
              <span>邮箱</span>
              <strong>{{ userInfo.email || '未填写' }}</strong>
            </div>
            <div class="contact-item">
              <span>手机号</span>
              <strong>{{ userInfo.phone || '未填写' }}</strong>
            </div>
            <div class="contact-item">
              <span>账号</span>
              <strong>{{ userInfo.username }}</strong>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="16">
        <el-card header="个人资料" class="edit-card">
          <el-form :model="profileForm" label-width="90px">
            <el-form-item label="昵称">
              <el-input v-model="profileForm.username" placeholder="请输入昵称" />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="profileForm.email" placeholder="请输入邮箱" />
            </el-form-item>
            <el-form-item label="手机号">
              <el-input v-model="profileForm.phone" placeholder="请输入手机号" />
            </el-form-item>
            <el-form-item label="简介">
              <el-input
                v-model="profileForm.bio"
                type="textarea"
                :rows="3"
                placeholder="介绍一下自己"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveUserInfo">保存资料</el-button>
              <el-button @click="resetUserInfo">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const defaultUserInfo = {
  username: '用户',
  role: 'student',
  avatar: '',
  email: '',
  phone: '',
  bio: '这个人还没有填写简介。',
}

const userInfo = computed(() => userStore.userInfo || defaultUserInfo)
const roleText = computed(() => {
  const role = userInfo.value.role || 'student'
  const map = { admin: '管理员', teacher: '教师', student: '学生' }
  return map[role] || '学生'
})
const roleTagType = computed(() => {
  const role = userInfo.value.role || 'student'
  if (role === 'admin') return 'danger'
  if (role === 'teacher') return 'warning'
  return 'success'
})
const userInitials = computed(() => {
  const name = userInfo.value.username || '用户'
  return name.slice(0, 2).toUpperCase()
})
const userAvatar = computed(() => userInfo.value.avatar || '')

const profileForm = reactive({
  username: '',
  email: '',
  phone: '',
  bio: '',
})

const syncProfileForm = () => {
  profileForm.username = userInfo.value.username || '用户'
  profileForm.email = userInfo.value.email || ''
  profileForm.phone = userInfo.value.phone || ''
  profileForm.bio = userInfo.value.bio || ''
}

const saveUserInfo = () => {
  userStore.setUserInfo({
    ...(userStore.userInfo || defaultUserInfo),
    username: profileForm.username || '用户',
    email: profileForm.email,
    phone: profileForm.phone,
    bio: profileForm.bio,
  })
  ElMessage.success('个人资料已保存')
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
  ElMessage.success('已退出登录')
}

const resetUserInfo = () => {
  syncProfileForm()
}

onMounted(() => {
  syncProfileForm()
})

watch(
  userInfo,
  () => {
    syncProfileForm()
  },
  { deep: true },
)
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.user-card,
.edit-card,
.section-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.card-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-title {
  font-size: 1rem;
  font-weight: bold;
  color: #1a365d;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.user-avatar {
  background: linear-gradient(135deg, #409eff, #66b1ff);
  font-size: 1.2rem;
  font-weight: bold;
}

.user-summary h2 {
  margin: 0 0 8px 0;
  color: #1a365d;
}

.user-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.user-bio {
  margin: 0;
  color: #64748b;
}

.contact-list {
  border-top: 1px solid #e5e7eb;
  padding-top: 12px;
}

.contact-item {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  color: #334155;
}

.stat-card {
  margin-bottom: 20px;
  text-align: center;
}

.stat-title {
  color: #64748b;
  font-size: 0.9rem;
  margin-bottom: 8px;
}

.stat-value {
  color: #1a365d;
  font-size: 1.3rem;
  font-weight: bold;
  margin-bottom: 6px;
}

.stat-footer {
  color: #94a3b8;
  font-size: 0.85rem;
}

.profile-section {
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 20px;
}

.profile-section h3 {
  margin: 0 0 15px 0;
  color: #1a365d;
}

.progress-text {
  text-align: center;
  margin-top: 10px;
  font-weight: bold;
  color: #4a5568;
}

.error-preferences {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}
</style>
