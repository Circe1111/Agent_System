<template>
  <div class="path-container">
    <el-card :header="$route.query.courseName || '个性化学习路径'">
      <el-row :gutter="20">
        <el-col :span="16">
          <div class="path-steps">
            <el-timeline>
              <el-timeline-item
                v-for="(step, index) in learningPath"
                :key="index"
                :timestamp="step.date"
                :color="getStepColor(step.status)"
                :size="step.status === 'completed' ? 'large' : 'normal'"
              >
                <el-card>
                  <div class="step-content">
                    <h4>{{ step.title }}</h4>
                    <p>{{ step.description }}</p>
                    <div class="step-meta">
                      <el-tag :type="getStepType(step.status)" size="small">
                        {{ getStatusText(step.status) }}
                      </el-tag>
                      <span class="step-duration">{{ step.duration }}分钟</span>
                    </div>
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </div>
        </el-col>

        <el-col :span="8">
          <el-card header="路径统计">
            <div class="path-stats">
              <div class="stat-item">
                <span class="label">总步骤数：</span>
                <span class="value">{{ learningPath.length }}</span>
              </div>
              <div class="stat-item">
                <span class="label">已完成：</span>
                <span class="value">{{ completedSteps }}</span>
              </div>
              <div class="stat-item">
                <span class="label">进行中：</span>
                <span class="value">{{ inProgressSteps }}</span>
              </div>
              <div class="stat-item">
                <span class="label">总时长：</span>
                <span class="value">{{ totalTime }}分钟</span>
              </div>
              <div class="progress-bar">
                <el-progress
                  :percentage="completionRate"
                  :stroke-width="20"
                  :color="progressColor"
                />
                <span class="progress-text">{{ completionRate }}% 完成</span>
              </div>
            </div>
          </el-card>

          <el-card header="操作" style="margin-top: 20px">
            <el-button type="primary" @click="generatePath" :loading="generating">
              重新生成路径
            </el-button>
            <el-button
              type="success"
              @click="startNextStep"
              :disabled="currentStepIndex >= learningPath.length"
            >
              开始下一步
            </el-button>
            <el-button type="warning" @click="goBackStep" :disabled="!canGoBack">
              返回上一步
            </el-button>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const route = useRoute()
const generating = ref(false)

const getDefaultPath = (courseId) => {
  const paths = {
    '1': [
      { id: 1, title: 'Python基础语法', description: '变量、数据类型、控制流', status: 'completed', date: '2024-01-01', duration: 60 },
      { id: 2, title: '函数与模块', description: '函数定义、参数传递、模块导入', status: 'completed', date: '2024-01-03', duration: 90 },
      { id: 3, title: '面向对象编程', description: '类、对象、继承、封装', status: 'in-progress', date: '2024-01-05', duration: 75 },
      { id: 4, title: '文件操作', description: '文件读写、异常处理', status: 'pending', date: '2024-01-07', duration: 45 },
      { id: 5, title: '常用库实战', description: 'requests、json、datetime', status: 'pending', date: '2024-01-10', duration: 60 },
    ],
    '2': [
      { id: 1, title: '监督学习概述', description: '回归与分类问题定义', status: 'completed', date: '2024-02-01', duration: 45 },
      { id: 2, title: '线性回归', description: '最小二乘法、梯度下降', status: 'completed', date: '2024-02-03', duration: 90 },
      { id: 3, title: '决策树与随机森林', description: '信息增益、集成学习', status: 'in-progress', date: '2024-02-05', duration: 120 },
      { id: 4, title: 'SVM支持向量机', description: '核函数、软间隔', status: 'pending', date: '2024-02-08', duration: 90 },
      { id: 5, title: '神经网络入门', description: '感知机、反向传播', status: 'pending', date: '2024-02-10', duration: 120 },
    ],
    '3': [
      { id: 1, title: '神经网络基础', description: '激活函数、损失函数', status: 'completed', date: '2024-03-01', duration: 60 },
      { id: 2, title: 'CNN卷积网络', description: '卷积层、池化层', status: 'completed', date: '2024-03-03', duration: 90 },
      { id: 3, title: 'RNN与LSTM', description: '序列建模、门控机制', status: 'in-progress', date: '2024-03-05', duration: 120 },
      { id: 4, title: 'Transformer架构', description: '自注意力、位置编码', status: 'pending', date: '2024-03-08', duration: 150 },
      { id: 5, title: '模型部署', description: 'ONNX、TensorRT', status: 'pending', date: '2024-03-12', duration: 90 },
    ],
  }
  return paths[courseId] || paths['1']
}

const learningPath = ref([])

onMounted(() => {
  const courseId = route.query.courseId || '1'
  const stored = localStorage.getItem(`learningPath_${courseId}`)
  if (stored) {
    try {
      learningPath.value = JSON.parse(stored)
    } catch {
      learningPath.value = getDefaultPath(courseId)
    }
  } else {
    learningPath.value = getDefaultPath(courseId)
  }
})

watch(
  learningPath,
  (val) => {
    const courseId = route.query.courseId || '1'
    localStorage.setItem(`learningPath_${courseId}`, JSON.stringify(val))
  },
  { deep: true },
)

const completedSteps = computed(
  () => learningPath.value.filter((step) => step.status === 'completed').length,
)

const inProgressSteps = computed(
  () => learningPath.value.filter((step) => step.status === 'in-progress').length,
)

const totalTime = computed(() => learningPath.value.reduce((sum, step) => sum + step.duration, 0))

const completionRate = computed(() =>
  Math.round((completedSteps.value / learningPath.value.length) * 100),
)

const currentStepIndex = computed(() => {
  const inProgress = learningPath.value.findIndex((step) => step.status === 'in-progress')
  return inProgress >= 0 ? inProgress : -1
})

const progressColor = computed(() => {
  if (completionRate.value >= 80) return '#67c23a'
  if (completionRate.value >= 50) return '#e6a23c'
  return '#f56c6c'
})

const canGoBack = computed(() => {
  // Can go back if there's an in-progress or completed step (not if everything is pending)
  return learningPath.value.some((s) => s.status === 'completed' || s.status === 'in-progress')
})

const getStepColor = (status) => {
  switch (status) {
    case 'completed':
      return '#67c23a'
    case 'in-progress':
      return '#409eff'
    default:
      return '#c0c4cc'
  }
}

const getStepType = (status) => {
  switch (status) {
    case 'completed':
      return 'success'
    case 'in-progress':
      return 'warning'
    default:
      return 'info'
  }
}

const getStatusText = (status) => {
  const texts = {
    completed: '已完成',
    'in-progress': '进行中',
    pending: '待开始',
  }
  return texts[status] || status
}

const generatePath = async () => {
  generating.value = true
  try {
    // Simulate API call: POST /path/generate with courseId
    // TODO: Replace with real API call when backend endpoint is ready
    // const res = await generateLearningPath({ courseId: route.query.courseId })
    await new Promise((resolve) => setTimeout(resolve, 1000))

    // Replace entire path with new generated data (simulated)
    const courseId = route.query.courseId || '1'
    const newPath = getDefaultPath(courseId).map((step, index) => ({
      ...step,
      id: index + 1,
      status: 'pending', // All reset to pending
      date: new Date().toISOString().split('T')[0],
    }))
    // Set first step as in-progress
    if (newPath.length > 0) newPath[0].status = 'in-progress'

    learningPath.value = newPath
    ElMessage.success('学习路径重新生成成功！')
  } catch (error) {
    ElMessage.error('生成路径失败')
  } finally {
    generating.value = false
  }
}

const startNextStep = () => {
  const nextIndex = learningPath.value.findIndex((step) => step.status === 'pending')
  if (nextIndex >= 0) {
    // 标记当前步骤为已完成
    if (currentStepIndex.value >= 0) {
      learningPath.value[currentStepIndex.value].status = 'completed'
    }
    // 标记下一个步骤为进行中
    learningPath.value[nextIndex].status = 'in-progress'
    ElMessage.success(`开始学习：${learningPath.value[nextIndex].title}`)
  }
}

const goBackStep = () => {
  // Find the in-progress step (current), mark it as pending
  const inProgressIdx = learningPath.value.findIndex((s) => s.status === 'in-progress')
  if (inProgressIdx >= 0) {
    learningPath.value[inProgressIdx].status = 'pending'
    // Also revert the previous completed step to in-progress
    if (inProgressIdx > 0) {
      learningPath.value[inProgressIdx - 1].status = 'in-progress'
    }
    ElMessage.success(`已返回：${learningPath.value[Math.max(0, inProgressIdx - 1)].title}`)
  } else {
    // No in-progress step — revert the last completed step
    const lastCompleted = [...learningPath.value].reverse().findIndex((s) => s.status === 'completed')
    if (lastCompleted >= 0) {
      const idx = learningPath.value.length - 1 - lastCompleted
      learningPath.value[idx].status = 'in-progress'
      ElMessage.success(`已返回：${learningPath.value[idx].title}`)
    } else {
      ElMessage.info('没有可以回退的步骤')
    }
  }
}
</script>

<style scoped>
.path-container {
  padding: 20px;
}

.path-steps {
  padding: 20px 0;
}

.step-content h4 {
  margin: 0 0 8px 0;
  color: #1a365d;
}

.step-content p {
  margin: 0 0 10px 0;
  color: #4a5568;
  line-height: 1.5;
}

.step-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.step-duration {
  color: #718096;
  font-size: 0.9rem;
}

.path-stats {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.label {
  color: #4a5568;
  font-weight: 500;
}

.value {
  font-weight: bold;
  color: #1a365d;
}

.progress-bar {
  margin-top: 15px;
}

.progress-text {
  display: block;
  text-align: center;
  margin-top: 10px;
  font-weight: bold;
  color: #4a5568;
}
</style>
