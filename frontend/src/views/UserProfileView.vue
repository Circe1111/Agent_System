<template>
  <div class="preferences-container">
    <!-- 四象限布局 -->
    <div class="quadrant-grid">
      <!-- 左上：知识基础 -->
      <el-card class="pref-card quadrant-card knowledge-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon><TrendCharts /></el-icon>
            <span>知识基础</span>
          </div>
        </template>
        <div class="knowledge-ring">
          <el-progress
            type="dashboard"
            :percentage="computedKnowledgeBase || 0"
            :color="knowledgeColor"
            :stroke-width="12"
          >
            <span class="ring-label">{{ computedKnowledgeBase || 0 }}%</span>
          </el-progress>
          <p class="ring-hint">综合知识掌握程度</p>
        </div>
        <el-divider />
        <div class="knowledge-detail">
          <div v-for="kp in knowledgePoints" :key="kp.name" class="detail-row">
            <span>{{ kp.name }}</span>
            <el-progress :percentage="kp.level" :stroke-width="6" :color="kp.color" />
          </div>
          <div v-if="knowledgePoints.length === 0" class="empty-hint" style="text-align:center;padding:16px">
            通过AI对话积累知识数据
          </div>
        </div>
      </el-card>

      <!-- 右上：学习目标 -->
      <el-card class="pref-card quadrant-card goals-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon><Flag /></el-icon>
            <span>学习目标</span>
            <span v-if="activeGoalsCourse" class="topic-tag">{{ extractTopic(activeGoalsCourse) }}</span>
          </div>
        </template>
        <div v-if="pathCourses.length === 0" class="empty-hint">在下方编辑区填写学习目标，自动生成学习阶段</div>
        <template v-else>
          <div v-if="pathCourses.length > 1" class="goals-tabs">
            <span
              v-for="course in pathCourses"
              :key="course"
              class="goals-tab"
              :class="{ active: course === activeGoalsCourse }"
              @click="activeGoalsCourse = course"
            >
              {{ extractTopic(course) || course }}
            </span>
          </div>
          <el-timeline>
            <el-timeline-item
              v-for="(goal, idx) in learningGoals"
              :key="idx"
              :timestamp="goal.deadline"
              :color="goal.achieved ? '#67c23a' : '#a8d8ea'"
              :hollow="!goal.achieved"
            >
              <div class="goal-item" :class="{ achieved: goal.achieved }">
                <h4>{{ goal.title }}</h4>
                <p>{{ goal.description }}</p>
              </div>
            </el-timeline-item>
          </el-timeline>
        </template>
      </el-card>

      <!-- 左下：我的薄弱点 -->
      <el-card class="pref-card quadrant-card weak-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon><Warning /></el-icon>
            <span>我的薄弱点</span>
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
              :color="point.color"
            />
          </div>
          <div v-if="weakPoints.length === 0" class="empty-hint" style="text-align:center;padding:16px">
            通过AI对话发现薄弱知识点
          </div>
        </div>
      </el-card>

      <!-- 右下：AI学习风格分析 -->
      <el-card class="pref-card quadrant-card vark-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon><Brush /></el-icon>
            <span>学习风格</span>
            <el-button
              size="small"
              type="primary"
              text
              :loading="styleLoading"
              @click="fetchStyleAnalysis"
              class="style-refresh-btn"
            >
              <el-icon><Refresh /></el-icon>
              {{ styleAnalysis ? '重新分析' : '开始分析' }}
            </el-button>
          </div>
        </template>

        <!-- 无分析结果 -->
        <div v-if="!styleAnalysis" class="empty-hint">
          <p>开始与AI助手对话，系统将在每次对话后自动分析你的学习风格</p>
          <p class="empty-hint-sub">也可以点击「开始分析」按钮手动触发</p>
        </div>

        <!-- 有分析结果 -->
        <div v-else class="style-analysis-body">
          <!-- 认知风格标签 -->
          <div class="style-header">
            <span class="style-label">{{ styleAnalysis.style_label }}</span>
            <el-tag size="small" type="info" effect="plain">
              置信度 {{ Math.round((styleAnalysis.confidence || 0) * 100) }}%
            </el-tag>
          </div>

          <!-- 风格描述 -->
          <p class="style-desc">{{ styleAnalysis.style_description }}</p>

          <!-- 优势 -->
          <div class="style-section">
            <div class="style-section-title">优势</div>
            <div class="style-tags">
              <el-tag
                v-for="(s, i) in styleAnalysis.strengths"
                :key="'s-' + i"
                size="small"
                type="success"
                effect="plain"
                class="style-item-tag"
              >{{ s }}</el-tag>
            </div>
          </div>

          <!-- 不足 -->
          <div class="style-section" v-if="styleAnalysis.weaknesses && styleAnalysis.weaknesses.length">
            <div class="style-section-title">待提升</div>
            <div class="style-tags">
              <el-tag
                v-for="(w, i) in styleAnalysis.weaknesses"
                :key="'w-' + i"
                size="small"
                type="warning"
                effect="plain"
                class="style-item-tag"
              >{{ w }}</el-tag>
            </div>
          </div>

          <!-- 学习建议 -->
          <div class="style-section" v-if="styleAnalysis.study_tips && styleAnalysis.study_tips.length">
            <div class="style-section-title">学习建议</div>
            <div class="study-tips-list">
              <div class="study-tip-item" v-for="(tip, i) in styleAnalysis.study_tips" :key="'tip-' + i">
                <span class="tip-index">{{ i + 1 }}</span>
                <div class="tip-content">
                  <div class="tip-title">{{ tip.tip }}</div>
                  <div class="tip-detail">{{ tip.detail }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 推荐工具 -->
          <div class="style-section" v-if="styleAnalysis.recommended_tools && styleAnalysis.recommended_tools.length">
            <div class="style-section-title">推荐工具</div>
            <div class="style-tags">
              <el-tag
                v-for="(t, i) in styleAnalysis.recommended_tools"
                :key="'t-' + i"
                size="small"
                effect="plain"
                class="style-item-tag tool-tag"
              >{{ t }}</el-tag>
            </div>
          </div>

          <!-- 分析总结 -->
          <el-divider style="margin: 10px 0" />
          <div class="style-summary">
            <el-icon><InfoFilled /></el-icon>
            <span>{{ styleAnalysis.analysis_summary }}</span>
          </div>
        </div>
      </el-card>
    </div>

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
import { reactive, ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores'
import { ElMessage } from 'element-plus'
import { getLearningProfile, updateLearningProfile, analyzeLearningStyle } from '@/api/api'
import { TrendCharts, Brush, Flag, Warning, Edit, Refresh, InfoFilled } from '@element-plus/icons-vue'

const userStore = useUserStore()
const learningProfile = computed(() => userStore.currentProfile)

// 后端字段 → 前端字段映射
const backendToFrontend = (portrait) => {
  if (!portrait || typeof portrait !== 'object') return {}
  const rawJson = portrait.raw_json || {}
  return {
    knowledgeBase: typeof portrait.knowledge_level === 'string' ? 
      (parseInt(portrait.knowledge_level) || 65) : (portrait.knowledge_level || 65),
    cognitiveStyle: portrait.learning_preference || portrait.cognitiveStyle || '',
    errorPreferences: portrait.weak_knowledge ? 
      (typeof portrait.weak_knowledge === 'string' ? 
        portrait.weak_knowledge.split(',').filter(Boolean) : []) : [],
    learningGoals: portrait.study_goal || portrait.learningGoals || '',
    preferredLearningStyle: portrait.learning_style || portrait.preferredLearningStyle || '',
    currentProgress: portrait.knowledge_level ? 
      (parseInt(portrait.knowledge_level) || 50) : 50,
    weakPointCounts: rawJson.weak_point_counts || {},
    varkScores: rawJson.vark_scores || null,
    varkHistory: rawJson.vark_history || [],
    username: portrait.username || '',
    name: portrait.name || '',
    major: portrait.major || '',
    course: portrait.course || '',
    study_time: portrait.study_time || '',
    raw_json: rawJson,
  }
}

const editForm = reactive({
  cognitiveStyle: learningProfile.value.cognitiveStyle,
  learningGoals: learningProfile.value.learningGoals,
  preferredLearningStyle: learningProfile.value.preferredLearningStyle,
})

const styleAnalysis = computed(() => {
  return learningProfile.value?.raw_json?.style_analysis || null
})
const styleLoading = ref(false)

const fetchStyleAnalysis = async () => {
  styleLoading.value = true
  try {
    const res = await analyzeLearningStyle()
    const payload = res?.data || {}
    const analysis = payload.data?.style_analysis || payload.style_analysis || null
    if (analysis) {
      if (!learningProfile.value.raw_json) learningProfile.value.raw_json = {}
      learningProfile.value.raw_json.style_analysis = analysis
    }
  } catch (err) {
    console.warn('获取学习风格分析失败:', err?.message || err)
    ElMessage.warning('学习风格分析失败，请稍后重试')
  } finally {
    styleLoading.value = false
  }
}

const knowledgeColor = computed(() => {
  const score = learningProfile.value.knowledgeBase
  if (score >= 80) return '#67c23a'
  if (score >= 60) return '#e6a23c'
  return '#f56c6c'
})

const updateProfile = async () => {
  const goalChanged = editForm.learningGoals !== learningProfile.value.learningGoals

  // 1) 先保存到 localStorage（本地持久化，确保切换页面不丢失）
  const updatedProfile = {
    ...learningProfile.value,
    cognitiveStyle: editForm.cognitiveStyle,
    learningGoals: editForm.learningGoals,
    preferredLearningStyle: editForm.preferredLearningStyle,
    // 学习目标改变时，重置进度为 0
    knowledgeBase: goalChanged ? 0 : learningProfile.value.knowledgeBase,
  }
  userStore.setLearningProfile(updatedProfile)

  // 目标改变时，切换到新的学习目标
  if (goalChanged && editForm.learningGoals) {
    activeGoalsCourse.value = editForm.learningGoals
  }

  // 2) 同步到后端
  try {
    const res = await updateLearningProfile(updatedProfile)
    const payload = res?.data || {}
    const portrait =
      payload.data?.portrait ||
      payload.portrait ||
      payload.data ||
      payload
    if (portrait && typeof portrait === 'object') {
      const frontendProfile = backendToFrontend(portrait)
      // 如果目标改变了，强制重置进度
      if (goalChanged) {
        frontendProfile.knowledgeBase = 0
      }
      userStore.setLearningProfile(frontendProfile)
    }
    ElMessage.success(goalChanged ? '学习目标已更新，进度已重置' : '偏好设置已保存')
  } catch (err) {
    console.error('同步到服务器失败：', err)
    ElMessage.warning('已保存到本地，但同步到服务器失败，请检查网络')
  }

  // 目标改变时，清除旧的学习路径缓存
  if (goalChanged) {
    localStorage.removeItem(`${lsPathHistoryKey.value}_${learningProfile.value.learningGoals || 'default'}`)
  }
}

const resetForm = () => {
  editForm.cognitiveStyle = learningProfile.value.cognitiveStyle
  editForm.learningGoals = learningProfile.value.learningGoals
  editForm.preferredLearningStyle = learningProfile.value.preferredLearningStyle
}

onMounted(async () => {
  initActiveCourse()
  // 1) 先从 store（含 localStorage）恢复编辑表单
  const local = userStore.currentProfile
  const localKnowledge = local?.knowledgeBase ?? 0
  if (local) {
    editForm.cognitiveStyle = local.cognitiveStyle ?? editForm.cognitiveStyle
    editForm.learningGoals = local.learningGoals ?? editForm.learningGoals
    editForm.preferredLearningStyle = local.preferredLearningStyle ?? editForm.preferredLearningStyle
  }

  // 2) 尝试从后端同步最新数据
  try {
    const res = await getLearningProfile()
    const payload = res?.data || {}
    const portrait =
      payload.data?.portrait ||
      payload.portrait ||
      payload.data ||
      payload
    console.log('[UserProfileView] 后端返回原始画像:', portrait)
    if (portrait && typeof portrait === 'object') {
      const frontendProfile = backendToFrontend(portrait)
      console.log('[UserProfileView] 转换后前端格式:', frontendProfile)
      // knowledgeBase 以本地 store 为准（学习路径进度由本地维护）
      // 后端只同步其他字段（学习目标、认知风格等）
      frontendProfile.knowledgeBase = localKnowledge
      userStore.setLearningProfile(frontendProfile)
      editForm.cognitiveStyle = frontendProfile.cognitiveStyle ?? editForm.cognitiveStyle
      editForm.learningGoals = frontendProfile.learningGoals ?? editForm.learningGoals
      editForm.preferredLearningStyle = frontendProfile.preferredLearningStyle ?? editForm.preferredLearningStyle
    }
  } catch (err) {
    console.warn('从服务器同步画像失败，使用本地缓存：', err?.message || err)
  }
})

// Mock data for new display sections
const cognitiveStyles = ['视觉型学习者', '听觉型学习者', '动觉型学习者', '读写型学习者']

// 提取学习目标中的核心主题
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

// 根据主题关键词生成学习阶段
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

// 根据主题匹配阶段模板
const getStagesForTopic = (topic) => {
  const lower = topic.toLowerCase()
  for (const [key, stages] of Object.entries(stageTemplates)) {
    if (lower.includes(key.toLowerCase()) || key.toLowerCase().includes(lower)) {
      return stages
    }
  }
  return ['基础入门', '核心知识', '进阶提升', '综合应用', '项目实战']
}

// 从学习路径历史中读取所有课程
const lsPathHistoryKey = computed(() => {
  const uid = userStore.userInfo?.id || userStore.userInfo?.username || 'anonymous'
  return `user_${uid}_learningPathHistory`
})

const pathCourses = computed(() => {
  try {
    const raw = localStorage.getItem(lsPathHistoryKey.value)
    if (!raw) return []
    const history = JSON.parse(raw)
    return Object.keys(history).sort((a, b) => {
      const ta = history[a]?.createdAt || ''
      const tb = history[b]?.createdAt || ''
      return ta.localeCompare(tb)
    })
  } catch { return [] }
})

// 当前选中的课程（默认最新）
const activeGoalsCourse = ref('')

const initActiveCourse = () => {
  const courses = pathCourses.value
  if (courses.length > 0) {
    activeGoalsCourse.value = courses[courses.length - 1] // 最新添加的
  } else {
    activeGoalsCourse.value = learningProfile.value.learningGoals || ''
  }
}

// 动态学习目标（根据选中的课程实时更新）
const learningTopic = computed(() => {
  return extractTopic(activeGoalsCourse.value || '')
})

const learningGoals = computed(() => {
  const goalText = activeGoalsCourse.value || ''
  const topic = extractTopic(goalText)
  const stages = getStagesForTopic(topic || goalText)

  let progress = 0
  try {
    const raw = localStorage.getItem(lsPathHistoryKey.value)
    if (raw) {
      const history = JSON.parse(raw)
      const activeEntry = history[goalText]
      if (activeEntry && activeEntry.steps) {
        const completed = activeEntry.steps.filter(s => s.status === 'completed').length
        progress = Math.round((completed / activeEntry.steps.length) * 100)
      }
    }
  } catch { /* ignore */ }

  const now = new Date()
  const year = now.getFullYear()
  const q = Math.ceil((now.getMonth() + 1) / 3)

  return stages.map((title, idx) => {
    const perStage = 100 / stages.length
    const threshold = (idx + 1) * perStage
    const achieved = progress >= threshold
    const quarter = q + idx
    const qYear = year + Math.floor((quarter - 1) / 4)
    const qNum = ((quarter - 1) % 4) + 1
    return {
      title,
      description: `阶段${idx + 1}：${achieved ? '已掌握' : '学习中'} — ${title}`,
      deadline: `${qYear} Q${qNum}`,
      achieved,
    }
  })
})

const knowledgePoints = computed(() => {
  const colors = ['#a8d8ea', '#aa96da', '#fcbad3', '#ffe0b2', '#b5ead7', '#c4b5fd', '#fda4af', '#a3e635']

  try {
    const raw = localStorage.getItem(lsPathHistoryKey.value)
    if (!raw) return []
    const history = JSON.parse(raw)
    const entries = Object.entries(history)
    if (entries.length === 0) return []

    return entries.map(([goal, data], idx) => {
      const steps = data.steps || []
      const completed = steps.filter(s => s.status === 'completed').length
      const total = steps.length || 1
      const level = Math.round((completed / total) * 100)
      return {
        name: goal,
        level,
        color: colors[idx % colors.length],
      }
    })
  } catch {
    return []
  }
})

const computedKnowledgeBase = computed(() => {
  if (knowledgePoints.value.length === 0) return 0
  const sum = knowledgePoints.value.reduce((s, kp) => s + kp.level, 0)
  return Math.round(sum / knowledgePoints.value.length)
})

const weakPoints = computed(() => {
  const errors = learningProfile.value.errorPreferences || []
  const counts = learningProfile.value.weakPointCounts || {}
  if (errors.length === 0) return []
  const total = errors.reduce((sum, name) => sum + (counts[name] || 1), 0)
  const colors = ['#fcbad3', '#ffe0b2', '#a8d8ea', '#aa96da', '#b5ead7']
  return errors.map((name, idx) => {
    const count = counts[name] || 1
    const level = Math.round((count / total) * 100)
    return {
      name,
      count,
      level,
      color: colors[idx % colors.length],
    }
  })
})

const varkHistory = computed(() => {
  return learningProfile.value.varkHistory || []
})

const varkData = computed(() => {
  const scores = learningProfile.value.varkScores
  if (!scores) return { scores: null, dominant: '', reason: '', items: [], triggerWords: [] }
  const map = {
    V: { label: '视觉型', color: '#6366f1', desc: '喜欢图表、流程图、示意图等可视化信息' },
    A: { label: '听觉型', color: '#f59e0b', desc: '喜欢听讲、讨论、口头解释' },
    R: { label: '读写型', color: '#10b981', desc: '喜欢阅读文字、做笔记、写总结' },
    K: { label: '动觉型', color: '#ef4444', desc: '喜欢动手实践、操作、实验' },
  }
  const items = ['V', 'A', 'R', 'K'].map(k => ({
    key: k,
    label: map[k].label,
    color: map[k].color,
    desc: map[k].desc,
    pct: Math.round((scores[k] || 0) * 100),
  }))
  const maxItem = items.reduce((a, b) => (a.pct > b.pct ? a : b), items[0])
  return {
    scores,
    dominant: maxItem.label,
    reason: scores.reason || '',
    items,
    triggerWords: scores.trigger_words || [],
  }
})

const getVarkDominant = (entry) => {
  const items = [
    { key: 'V', label: '视觉型', val: entry.V || 0 },
    { key: 'A', label: '听觉型', val: entry.A || 0 },
    { key: 'R', label: '读写型', val: entry.R || 0 },
    { key: 'K', label: '动觉型', val: entry.K || 0 },
  ]
  const max = items.reduce((a, b) => (a.val > b.val ? a : b), items[0])
  return max.label
}

const formatVarkTime = (ts) => {
  if (!ts) return ''
  try {
    const d = new Date(ts)
    return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  } catch { return ts }
}

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

.quadrant-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.quadrant-card {
  display: flex;
  flex-direction: column;
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

.topic-tag {
  font-size: 0.75rem;
  color: #1a365d;
  background: rgba(26, 54, 93, 0.08);
  padding: 2px 10px;
  border-radius: 12px;
  font-weight: 500;
  margin-left: 8px;
}

.goals-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.goals-tab {
  padding: 4px 12px;
  border-radius: 16px;
  background: #f0f4ff;
  color: #4a5568;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.goals-tab:hover {
  background: #dbeafe;
  color: #1253D2;
}

.goals-tab.active {
  background: #1253D2;
  color: #ffffff;
  border-color: #1253D2;
}

.empty-hint {
  text-align: center;
  color: #8fa4b8;
  padding: 32px 16px;
  font-size: 0.9rem;
}

.empty-hint-sub {
  font-size: 0.8rem;
  color: #b0c4d8;
  margin-top: 4px;
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

.edit-card {
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

/* AI 学习风格分析 */
.style-refresh-btn {
  margin-left: auto;
  font-size: 0.8rem;
}

.style-analysis-body {
  padding: 4px 0;
}

.style-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.style-label {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1253D2;
  background: linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%);
  padding: 4px 14px;
  border-radius: 20px;
}

.style-desc {
  font-size: 0.85rem;
  color: #5a7d9a;
  line-height: 1.6;
  margin-bottom: 14px;
  padding: 10px 12px;
  background: #f8fbff;
  border-radius: 10px;
  border-left: 3px solid #1253D2;
}

.style-section {
  margin-bottom: 12px;
}

.style-section-title {
  font-size: 0.82rem;
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 6px;
}

.style-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.style-item-tag {
  font-size: 0.78rem;
  border-radius: 10px;
}

.tool-tag {
  background: #f0fdf4;
  border-color: #bbf7d0;
  color: #166534;
}

.study-tips-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.study-tip-item {
  display: flex;
  gap: 10px;
  padding: 8px 10px;
  background: #f9fafb;
  border-radius: 10px;
  align-items: flex-start;
}

.tip-index {
  flex-shrink: 0;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #1253D2;
  color: #fff;
  font-size: 0.75rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 1px;
}

.tip-content {
  flex: 1;
}

.tip-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 2px;
}

.tip-detail {
  font-size: 0.78rem;
  color: #6b7280;
  line-height: 1.5;
}

.style-summary {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 0.8rem;
  color: #8fa4b8;
  line-height: 1.5;
}

.style-summary .el-icon {
  color: #1253D2;
  margin-top: 2px;
  flex-shrink: 0;
}
</style>