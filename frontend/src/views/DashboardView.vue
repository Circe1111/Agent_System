<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-number">{{ learningProfile.currentProgress }}%</div>
            <div class="stat-label">学习进度</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-number">{{ completedLessons }}</div>
            <div class="stat-label">已完成课程</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-number">{{ unreadMessages }}</div>
            <div class="stat-label">未读消息</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-number">{{ totalResources }}</div>
            <div class="stat-label">资源总数</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card header="最近学习">
          <el-table :data="recentLearning" style="width: 100%">
            <el-table-column prop="title" label="课程名称" />
            <el-table-column prop="progress" label="进度" width="100">
              <template #default="{ row }">
                <el-progress :percentage="row.progress" :stroke-width="10" />
              </template>
            </el-table-column>
            <el-table-column prop="lastStudyTime" label="最后学习" width="150" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="学习画像">
          <div class="profile-summary">
            <div class="profile-item">
              <span class="label">知识基础：</span>
              <el-progress
                :percentage="learningProfile.knowledgeBase"
                :stroke-width="8"
                status="success"
              />
            </div>
            <div class="profile-item">
              <span class="label">认知风格：</span>
              <el-tag type="info">{{ learningProfile.cognitiveStyle }}</el-tag>
            </div>
            <div class="profile-item">
              <span class="label">学习目标：</span>
              <el-tag type="warning">{{ learningProfile.learningGoals }}</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useUserStore } from '@/stores'

const userStore = useUserStore()

const learningProfile = computed(() => userStore.currentProfile)

// 模拟数据
const completedLessons = 5
const unreadMessages = 3
const totalResources = 128

const recentLearning = [
  { title: 'Python基础入门', progress: 85, lastStudyTime: '2小时前' },
  { title: '机器学习概论', progress: 60, lastStudyTime: '昨天' },
  { title: '深度学习基础', progress: 30, lastStudyTime: '3天前' },
]
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.stat-card {
  text-align: center;
}

.stat-item {
  padding: 20px 0;
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  color: #1a365d;
}

.stat-label {
  color: #718096;
  margin-top: 10px;
}

.profile-summary {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.profile-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.label {
  font-weight: bold;
  color: #4a5568;
  min-width: 80px;
}
</style>
