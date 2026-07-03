<template>
  <div class="path-container">
    <el-card :header="pageTitle || '个性化学习路径'">
      <!-- 历史路径切换 -->
      <div v-if="historyKeys.length > 1" class="history-tabs">
        <span
          v-for="key in historyKeys"
          :key="key"
          class="history-tab"
          :class="{ active: key === activeGoal }"
          @click="switchToPath(key)"
        >
          {{ key }}
        </span>
      </div>

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
import { updateLearningProfile, getLearningPaths, saveLearningPath } from '@/api/api'

const userStore = useUserStore()
const route = useRoute()
const generating = ref(false)

// === 提取学习目标中的核心主题 ===
const extractTopic = (goalText) => {
  if (!goalText) return ''
  const patterns = ['掌握', '学习', '精通', '完成', '入门', '深入']
  for (const p of patterns) {
    if (goalText.includes(p)) {
      const idx = goalText.indexOf(p) + p.length
      return goalText.slice(idx).replace(/[的之]/, '').trim() || goalText
    }
  }
  return goalText
}

// === 阶段模板（与偏好页一致）===
const stageTemplates = {
  python: ['Python基础语法', 'Python面向对象', 'Python Web开发', 'Python数据分析', 'Python项目实战'],
  java: ['Java基础语法', 'Java面向对象', 'Java Web开发', 'Spring框架', 'Java微服务实战'],
  'c++': ['C++基础语法', 'C++面向对象', 'STL与模板', 'C++内存管理', 'C++项目实战'],
  javascript: ['JS基础语法', 'DOM与事件', '异步编程', '前端框架', '全栈项目实战'],
  '编译原理': ['词法分析', '语法分析', '语义分析', '代码优化', '编译器实现'],
  '机器学习': ['数学基础', '监督学习', '无监督学习', '深度学习', '模型部署实战'],
  '深度学习': ['神经网络基础', 'CNN卷积网络', 'RNN序列模型', 'Transformer', '大模型应用'],
  '数据结构': ['线性表', '树与图', '查找排序', '高级数据结构', '算法设计实战'],
  算法: ['基础算法', '分治与贪心', '动态规划', '图论算法', '算法竞赛实战'],
  '数据库': ['SQL基础', '表设计与范式', '索引与优化', '事务与并发', '分布式数据库'],
  '操作系统': ['进程管理', '内存管理', '文件系统', '设备管理', 'OS内核实战'],
  '计算机网络': ['网络基础', '传输层协议', '应用层协议', '网络安全', '网络编程实战'],
  前端: ['HTML/CSS基础', 'JavaScript核心', 'Vue/React框架', '工程化构建', '全栈项目实战'],
  后端: ['语言基础', 'Web框架', '数据库操作', '中间件与架构', '微服务实战'],
  '全栈': ['前端基础', '后端基础', '数据库设计', '系统架构', '全栈项目实战'],
}

const getStagesForTopic = (topic) => {
  const lower = topic.toLowerCase()
  for (const [key, stages] of Object.entries(stageTemplates)) {
    if (lower.includes(key.toLowerCase()) || key.toLowerCase().includes(lower)) {
      return stages
    }
  }
  return ['基础入门', '核心知识', '进阶提升', '综合应用', '项目实战']
}

// === 学习目标描述映射 ===
const getDescriptionForStage = (title) => {
  const descs = {
    '词法分析': '正则表达式、有限自动机、词法记号识别',
    '语法分析': '上下文无关文法、LL(1)分析、LR分析',
    '语义分析': '属性文法、类型检查、符号表管理',
    '代码优化': '基本块划分、数据流分析、循环优化',
    '编译器实现': '中间代码生成、目标代码生成、综合实验',
    'Python基础语法': '变量、数据类型、控制流与函数定义',
    'Python面向对象': '类与对象、继承、多态、封装',
    'Python Web开发': 'Flask/Django框架、REST API设计',
    'Python数据分析': 'NumPy/Pandas数据处理与可视化',
    'Python项目实战': '完整项目搭建、部署与性能优化',
    '数学基础': '线性代数、概率论、微积分核心概念',
    '监督学习': '线性回归、决策树、SVM、集成学习',
    '无监督学习': '聚类、降维、关联规则挖掘',
    '深度学习': '神经网络、反向传播、CNN/RNN架构',
    '模型部署实战': '模型导出、API服务、性能调优',
  }
  return descs[title] || `深入学习${title}相关知识，掌握核心概念与实践技能`
}

// === 根据学习目标生成学习路径 ===
const buildPathFromGoal = (goalText) => {
  const t = extractTopic(goalText)
  const stages = getStagesForTopic(t || goalText)
  const today = new Date().toISOString().split('T')[0]
  return stages.map((title, idx) => ({
    id: idx + 1,
    title,
    description: getDescriptionForStage(title),
    status: idx === 0 ? 'in-progress' : 'pending',
    date: today,
    duration: 45 + idx * 15,
  }))
}

// === 读取用户学习目标 ===
const learningGoal = computed(() => {
  return userStore.currentProfile?.learningGoals || ''
})

const topic = computed(() => extractTopic(learningGoal.value || ''))

const pageTitle = computed(() => {
  return '个性化学习路径'
})

// === 学习路径历史记录 ===
const HISTORY_KEY = computed(() => {
  const uid = userStore.userInfo?.id || userStore.userInfo?.username || 'anonymous'
  return `user_${uid}_learningPathHistory`
})
const activeGoal = ref(learningGoal.value || '默认目标')

const learningPathHistory = ref({})

const historyKeys = computed(() => Object.keys(learningPathHistory.value))

const learningPath = computed(() => {
  return learningPathHistory.value[activeGoal.value]?.steps || []
})

const loadHistory = () => {
  try {
    const raw = localStorage.getItem(HISTORY_KEY.value)
    if (raw) {
      learningPathHistory.value = JSON.parse(raw)
    }
  } catch { /* ignore */ }
}

const saveHistory = () => {
  localStorage.setItem(HISTORY_KEY.value, JSON.stringify(learningPathHistory.value))
}

const syncToBackend = async (goal, steps) => {
  try {
    await saveLearningPath(goal, steps)
  } catch (err) {
    console.warn('同步学习路径到后端失败:', err?.message || err)
  }
}

const loadFromBackend = async () => {
  try {
    const res = await getLearningPaths()
    const payload = res?.data || {}
    const paths = payload.data?.paths || payload.paths || []
    if (paths.length > 0) {
      const merged = { ...learningPathHistory.value }
      paths.forEach((p) => {
        if (p.goal && p.steps) {
          if (!merged[p.goal] || new Date(p.updated_at) > new Date(merged[p.goal].createdAt || 0)) {
            merged[p.goal] = {
              steps: p.steps,
              createdAt: p.updated_at || p.created_at || new Date().toISOString(),
            }
          }
        }
      })
      learningPathHistory.value = merged
      saveHistory()
    }
  } catch (err) {
    console.warn('从后端加载学习路径失败:', err?.message || err)
  }
}

const ensurePath = (goal) => {
  if (!goal) goal = '默认目标'
  if (!learningPathHistory.value[goal]) {
    learningPathHistory.value[goal] = {
      steps: buildPathFromGoal(goal),
      createdAt: new Date().toISOString(),
    }
    saveHistory()
    syncToBackend(goal, learningPathHistory.value[goal].steps)
  }
}

const switchToPath = (goal) => {
  activeGoal.value = goal
  if (goal === learningGoal.value) {
    syncProgressToProfile()
  }
}

// === 监听学习目标变化，自动创建/切换路径 ===
watch(learningGoal, (newGoal, oldGoal) => {
  if (!newGoal) return
  const goal = newGoal.trim()
  if (goal === activeGoal.value) return

  ensurePath(goal)
  activeGoal.value = goal
  syncProgressToProfile()
})

onMounted(async () => {
  loadHistory()
  await loadFromBackend()
  const goal = learningGoal.value || '默认目标'
  ensurePath(goal)
  activeGoal.value = goal
  syncProgressToProfile()
})

const completedSteps = computed(
  () => learningPath.value.filter((step) => step.status === 'completed').length,
)

const inProgressSteps = computed(
  () => learningPath.value.filter((step) => step.status === 'in-progress').length,
)

const totalTime = computed(() => learningPath.value.reduce((sum, step) => sum + step.duration, 0))

const completionRate = computed(() =>
  learningPath.value.length > 0
    ? Math.round((completedSteps.value / learningPath.value.length) * 100)
    : 0,
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
    await new Promise((resolve) => setTimeout(resolve, 1000))

    const newPath = buildPathFromGoal(activeGoal.value).map((step, index) => ({
      ...step,
      id: index + 1,
      status: 'pending',
      date: new Date().toISOString().split('T')[0],
    }))
    if (newPath.length > 0) newPath[0].status = 'in-progress'

    learningPathHistory.value[activeGoal.value] = {
      steps: newPath,
      createdAt: new Date().toISOString(),
    }
    saveHistory()
    syncToBackend(activeGoal.value, newPath)
    ElMessage.success('学习路径重新生成成功！')
    syncProgressToProfile()
  } catch (error) {
    ElMessage.error('生成路径失败')
  } finally {
    generating.value = false
  }
}

const startNextStep = () => {
  const nextIndex = learningPath.value.findIndex((step) => step.status === 'pending')
  if (nextIndex >= 0) {
    if (currentStepIndex.value >= 0) {
      learningPath.value[currentStepIndex.value].status = 'completed'
    }
    learningPath.value[nextIndex].status = 'in-progress'
    saveHistory()
    syncToBackend(activeGoal.value, learningPath.value)
    ElMessage.success(`开始学习：${learningPath.value[nextIndex].title}`)
    syncProgressToProfile()
  } else if (currentStepIndex.value >= 0) {
    // 最后一步：没有 pending 了，直接标记当前步为完成
    learningPath.value[currentStepIndex.value].status = 'completed'
    saveHistory()
    syncToBackend(activeGoal.value, learningPath.value)
    ElMessage.success('全部学习路径已完成！')
    syncProgressToProfile()
  }
}

const goBackStep = () => {
  const inProgressIdx = learningPath.value.findIndex((s) => s.status === 'in-progress')
  if (inProgressIdx >= 0) {
    learningPath.value[inProgressIdx].status = 'pending'
    if (inProgressIdx > 0) {
      learningPath.value[inProgressIdx - 1].status = 'in-progress'
    }
    saveHistory()
    syncToBackend(activeGoal.value, learningPath.value)
    ElMessage.success(`已返回：${learningPath.value[Math.max(0, inProgressIdx - 1)].title}`)
  } else {
    const lastCompleted = [...learningPath.value].reverse().findIndex((s) => s.status === 'completed')
    if (lastCompleted >= 0) {
      const idx = learningPath.value.length - 1 - lastCompleted
      learningPath.value[idx].status = 'in-progress'
      saveHistory()
      syncToBackend(activeGoal.value, learningPath.value)
      ElMessage.success(`已返回：${learningPath.value[idx].title}`)
    } else {
      ElMessage.info('没有可以回退的步骤')
    }
  }
  syncProgressToProfile()
}

// 同步学习路径进度到偏好设置（本地 + 后端）— 仅当 activeGoal 匹配当前学习目标时同步
const syncProgressToProfile = async () => {
  if (activeGoal.value !== learningGoal.value) return
  const currentProfile = userStore.currentProfile
  if (!currentProfile) return
  const updatedProfile = {
    ...currentProfile,
    knowledgeBase: completionRate.value,
  }
  userStore.setLearningProfile(updatedProfile)
  try {
    await updateLearningProfile(updatedProfile)
  } catch (err) {
    console.warn('同步进度到后端失败:', err)
  }
}
</script>

<style scoped>
.path-container {
  padding: 20px;
}

.history-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.history-tab {
  padding: 6px 16px;
  border-radius: 20px;
  background: #f0f4ff;
  color: #4a5568;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.history-tab:hover {
  background: #dbeafe;
  color: #1253D2;
}

.history-tab.active {
  background: #1253D2;
  color: #ffffff;
  border-color: #1253D2;
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