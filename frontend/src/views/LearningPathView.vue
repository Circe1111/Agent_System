<template>
  <div class="path-container">
    <el-card header="个性化学习路径">
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
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '@/stores'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const generating = ref(false)

// 模拟学习路径数据
const learningPath = ref([
  {
    id: 1,
    title: 'Python基础语法',
    description: '学习Python的基本语法、变量、数据类型等基础知识',
    status: 'completed',
    date: '2024-01-01',
    duration: 60,
  },
  {
    id: 2,
    title: '数据结构与算法',
    description: '掌握Python中的列表、字典、集合等数据结构的使用',
    status: 'completed',
    date: '2024-01-03',
    duration: 90,
  },
  {
    id: 3,
    title: '函数与模块',
    description: '学习函数定义、参数传递、模块导入等高级特性',
    status: 'in-progress',
    date: '2024-01-05',
    duration: 75,
  },
  {
    id: 4,
    title: '面向对象编程',
    description: '理解类、对象、继承、封装等OOP概念',
    status: 'pending',
    date: '2024-01-07',
    duration: 120,
  },
  {
    id: 5,
    title: '文件操作与异常处理',
    description: '学习文件读写、异常处理机制',
    status: 'pending',
    date: '2024-01-10',
    duration: 45,
  },
])

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
    // 模拟重新生成路径
    await new Promise((resolve) => setTimeout(resolve, 1000))

    // 重置状态
    learningPath.value.forEach((step, index) => {
      if (index < 2) {
        step.status = 'completed'
      } else if (index === 2) {
        step.status = 'in-progress'
      } else {
        step.status = 'pending'
      }
    })

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
