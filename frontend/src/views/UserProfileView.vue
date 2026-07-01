<template>
  <div class="preferences-container">
    <h2 class="page-title">学习偏好</h2>

    <el-row :gutter="20">
      <!-- 知识基础 — progress ring -->
      <el-col :xs="24" :md="12">
        <el-card class="pref-card knowledge-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><TrendCharts /></el-icon>
              <span>知识基础</span>
            </div>
          </template>
          <div class="knowledge-ring">
            <el-progress
              type="dashboard"
              :percentage="learningProfile.knowledgeBase || 65"
              :color="knowledgeColor"
              :stroke-width="12"
            >
              <span class="ring-label">{{ learningProfile.knowledgeBase || 65 }}%</span>
            </el-progress>
            <p class="ring-hint">综合知识掌握程度</p>
          </div>
          <el-divider />
          <div class="knowledge-detail">
            <div class="detail-row">
              <span>Python基础</span>
              <el-progress :percentage="75" :stroke-width="6" color="#a8d8ea" />
            </div>
            <div class="detail-row">
              <span>数据结构</span>
              <el-progress :percentage="60" :stroke-width="6" color="#aa96da" />
            </div>
            <div class="detail-row">
              <span>算法</span>
              <el-progress :percentage="45" :stroke-width="6" color="#fcbad3" />
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 认知风格 — tags -->
      <el-col :xs="24" :md="12">
        <el-card class="pref-card style-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Brush /></el-icon>
              <span>认知风格</span>
            </div>
          </template>
          <div class="style-tags">
            <el-tag
              v-for="style in cognitiveStyles"
              :key="style"
              size="large"
              class="style-tag"
              :type="style === learningProfile.cognitiveStyle ? '' : 'info'"
              :color="style === learningProfile.cognitiveStyle ? '#a8d8ea' : ''"
            >
              {{ style }}
            </el-tag>
          </div>
          <p class="style-desc">
            当前认知风格：<strong>{{ learningProfile.cognitiveStyle || '视觉型学习者' }}</strong>
          </p>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 学习目标 — milestones -->
      <el-col :xs="24" :md="12">
        <el-card class="pref-card goals-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Flag /></el-icon>
              <span>学习目标</span>
            </div>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="(goal, idx) in learningGoals"
              :key="idx"
              :timestamp="goal.deadline"
              :color="goal.achieved ? '#a8d8ea' : '#e8e8e8'"
              :hollow="!goal.achieved"
            >
              <div class="goal-item" :class="{ achieved: goal.achieved }">
                <h4>{{ goal.title }}</h4>
                <p>{{ goal.description }}</p>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>

      <!-- 易错点偏好 + 学习风格 -->
      <el-col :xs="24" :md="12">
        <!-- 易错点 -->
        <el-card class="pref-card weak-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Warning /></el-icon>
              <span>易错点偏好</span>
            </div>
          </template>
          <div class="weak-list">
            <div v-for="point in weakPoints" :key="point.name" class="weak-item">
              <div class="weak-header">
                <span class="weak-name">{{ point.name }}</span>
                <span class="weak-count">{{ point.count }}次</span>
              </div>
              <el-progress
                :percentage="point.level"
                :stroke-width="8"
                :color="point.level > 70 ? '#fcbad3' : point.level > 40 ? '#ffe0b2' : '#a8d8ea'"
              />
            </div>
          </div>
        </el-card>

        <!-- 学习风格偏好 — rating bars -->
        <el-card class="pref-card" shadow="hover" style="margin-top: 20px">
          <template #header>
            <div class="card-header">
              <el-icon><Star /></el-icon>
              <span>学习风格偏好</span>
            </div>
          </template>
          <div class="style-bars">
            <div v-for="item in learningStylePrefs" :key="item.name" class="style-bar-item">
              <div class="bar-label">
                <span>{{ item.name }}</span>
                <span class="bar-value">{{ item.score }}/10</span>
              </div>
              <el-progress
                :percentage="item.score * 10"
                :stroke-width="14"
                :color="item.color"
                :striped="true"
                :striped-flow="true"
              />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 编辑区域 -->
    <el-row style="margin-top: 20px">
      <el-col :span="24">
        <el-card class="pref-card edit-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Edit /></el-icon>
              <span>偏好编辑</span>
            </div>
          </template>
          <el-form :model="editForm" label-width="120px">
            <el-form-item label="认知风格">
              <el-select v-model="editForm.cognitiveStyle" placeholder="选择认知风格">
                <el-option label="视觉型学习者" value="视觉型学习者" />
                <el-option label="听觉型学习者" value="听觉型学习者" />
                <el-option label="动觉型学习者" value="动觉型学习者" />
                <el-option label="读写型学习者" value="读写型学习者" />
              </el-select>
            </el-form-item>
            <el-form-item label="学习目标">
              <el-input v-model="editForm.learningGoals" placeholder="例如：掌握Python全栈开发" />
            </el-form-item>
            <el-form-item label="偏好学习方式">
              <el-select v-model="editForm.preferredLearningStyle" placeholder="选择偏好方式">
                <el-option label="视频教程" value="视频教程" />
                <el-option label="文档阅读" value="文档阅读" />
                <el-option label="实践项目" value="实践项目" />
                <el-option label="互动练习" value="互动练习" />
                <el-option label="小组讨论" value="小组讨论" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="updateProfile">保存偏好</el-button>
              <el-button @click="resetForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { reactive, computed, onMounted, ref } from 'vue'
import { useUserStore } from '@/stores'
import { ElMessage } from 'element-plus'
import { getLearningProfile, updateLearningProfile } from '@/api/api'
import { TrendCharts, Brush, Flag, Warning, Star, Edit } from '@element-plus/icons-vue'

const userStore = useUserStore()
const learningProfile = computed(() => userStore.currentProfile)

const editForm = reactive({
  cognitiveStyle: learningProfile.value.cognitiveStyle,
  learningGoals: learningProfile.value.learningGoals,
  preferredLearningStyle: learningProfile.value.preferredLearningStyle,
})

const knowledgeColor = computed(() => {
  const score = learningProfile.value.knowledgeBase
  if (score >= 80) return '#67c23a'
  if (score >= 60) return '#e6a23c'
  return '#f56c6c'
})

const updateProfile = async () => {
  // 1) 乐观更新本地 store
  userStore.setLearningProfile({
    ...learningProfile.value,
    cognitiveStyle: editForm.cognitiveStyle,
    learningGoals: editForm.learningGoals,
    preferredLearningStyle: editForm.preferredLearningStyle,
  })

  // 2) 调用真实接口（POST /portrait/update）
  try {
    const res = await updateLearningProfile({
      ...learningProfile.value,
      cognitiveStyle: editForm.cognitiveStyle,
      learningGoals: editForm.learningGoals,
      preferredLearningStyle: editForm.preferredLearningStyle,
    })
    const payload = res?.data || {}
    const portrait =
      payload.data?.portrait ||
      payload.portrait ||
      payload.data ||
      payload
    if (portrait && typeof portrait === 'object') {
      userStore.setLearningProfile(portrait)
    }
    ElMessage.success('学习画像更新成功！')
  } catch (err) {
    console.error('更新学习画像失败：', err)
    ElMessage.error(err?.message || '更新学习画像失败，请稍后重试')
  }
}

const resetForm = () => {
  editForm.cognitiveStyle = learningProfile.value.cognitiveStyle
  editForm.learningGoals = learningProfile.value.learningGoals
  editForm.preferredLearningStyle = learningProfile.value.preferredLearningStyle
}

onMounted(async () => {
  // 进入页面时拉一次真实画像（GET /portrait/me）
  try {
    const res = await getLearningProfile()
    const payload = res?.data || {}
    const portrait =
      payload.data?.portrait ||
      payload.portrait ||
      payload.data ||
      payload
    if (portrait && typeof portrait === 'object') {
      userStore.setLearningProfile(portrait)
      // 同步回填编辑表单
      editForm.cognitiveStyle = portrait.cognitiveStyle ?? editForm.cognitiveStyle
      editForm.learningGoals = portrait.learningGoals ?? editForm.learningGoals
      editForm.preferredLearningStyle =
        portrait.preferredLearningStyle ?? editForm.preferredLearningStyle
    }
  } catch (err) {
    // 拉取失败不阻塞页面
    console.warn('拉取学习画像失败：', err?.message || err)
  }
})

// Mock data for new display sections
const cognitiveStyles = ['视觉型学习者', '听觉型学习者', '动觉型学习者', '读写型学习者']

const learningGoals = ref([
  { title: '完成Python基础课程', description: '掌握变量、数据类型、控制流', deadline: '2024 Q1', achieved: true },
  { title: '独立完成一个Web项目', description: '使用Vue3 + FastAPI搭建全栈应用', deadline: '2024 Q2', achieved: true },
  { title: '掌握机器学习基础', description: '理解监督学习、无监督学习核心算法', deadline: '2024 Q3', achieved: false },
  { title: '完成毕业设计', description: '基于大模型的智能教育系统', deadline: '2024 Q4', achieved: false },
])

const weakPoints = ref([
  { name: '递归算法', count: 12, level: 78 },
  { name: 'SQL联表查询', count: 8, level: 62 },
  { name: '异步编程', count: 15, level: 85 },
  { name: '正则表达式', count: 6, level: 45 },
])

const learningStylePrefs = ref([
  { name: '视频学习', score: 9, color: '#a8d8ea' },
  { name: '文档阅读', score: 6, color: '#aa96da' },
  { name: '动手实践', score: 8, color: '#fcbad3' },
  { name: '小组讨论', score: 4, color: '#ffe0b2' },
  { name: '刷题练习', score: 7, color: '#b5ead7' },
])
</script>

<style scoped>
.preferences-container {
  padding: 4px;
}

.page-title {
  font-size: 1.6rem;
  font-weight: 700;
  color: #4a5568;
  margin: 0 0 24px 0;
  letter-spacing: -0.5px;
}

.pref-card {
  border-radius: 20px;
  border: none;
  box-shadow: 0 2px 16px rgba(168, 216, 234, 0.15);
  transition: all 0.3s ease;
  background: #ffffff;
  margin-bottom: 0;
}

.pref-card:hover {
  box-shadow: 0 4px 24px rgba(168, 216, 234, 0.25);
  transform: translateY(-2px);
}

.pref-card :deep(.el-card__header) {
  background: linear-gradient(135deg, #f8fbff 0%, #f0f7ff 100%);
  border-bottom: 1px solid #e8f4f8;
  padding: 16px 20px;
  border-radius: 20px 20px 0 0;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1rem;
  font-weight: 600;
  color: #5a7d9a;
}

.card-header .el-icon {
  color: #89c4d9;
  font-size: 1.1rem;
}

/* Knowledge ring */
.knowledge-ring {
  text-align: center;
  padding: 10px 0;
}

.ring-label {
  font-size: 1.4rem;
  font-weight: 700;
  color: #4a5568;
}

.ring-hint {
  color: #8fa4b8;
  font-size: 0.9rem;
  margin-top: 8px;
}

.knowledge-detail {
  padding: 0 10px;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 14px;
}

.detail-row span {
  min-width: 80px;
  font-size: 0.9rem;
  color: #5a7d9a;
}

/* Style tags */
.style-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 10px 0;
}

.style-tag {
  border-radius: 12px;
  padding: 6px 16px;
  font-size: 0.9rem;
}

.style-desc {
  margin-top: 16px;
  color: #8fa4b8;
  font-size: 0.9rem;
}

.style-desc strong {
  color: #5a7d9a;
}

/* Goals timeline */
.goal-item h4 {
  margin: 0 0 4px 0;
  color: #5a7d9a;
  font-size: 0.95rem;
}

.goal-item p {
  margin: 0;
  color: #8fa4b8;
  font-size: 0.85rem;
}

.goal-item.achieved h4 {
  color: #89c4d9;
}

/* Weak points */
.weak-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.weak-item {
  padding: 0 4px;
}

.weak-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.weak-name {
  font-size: 0.9rem;
  color: #5a7d9a;
}

.weak-count {
  font-size: 0.8rem;
  color: #a0b5c8;
}

/* Style bars */
.style-bars {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 4px 0;
}

.style-bar-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.bar-label {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  color: #5a7d9a;
}

.bar-value {
  font-weight: 600;
  color: #89c4d9;
}

/* Edit form */
.edit-card :deep(.el-form-item__label) {
  color: #5a7d9a;
  font-weight: 500;
}
</style>
