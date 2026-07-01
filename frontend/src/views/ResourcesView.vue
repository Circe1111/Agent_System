<template>
  <div class="resources-container">
    <el-card>
      <template #header>
        <div class="header">
          <div>
            <h2>学习资源中心</h2>
            <p class="subtitle">选择课程后查看对应资源，文件可预览或下载</p>
          </div>
          <div class="filters">
            <el-select
              v-model="filterType"
              placeholder="资源类型"
              @change="applyFilters"
              style="margin-right: 10px"
            >
              <el-option label="全部" value="" />
              <el-option label="文档" value="document" />
              <el-option label="视频" value="video" />
              <el-option label="代码" value="code" />
              <el-option label="练习" value="exercise" />
            </el-select>

            <el-select
              v-model="filterDifficulty"
              placeholder="难度等级"
              @change="applyFilters"
              style="margin-right: 10px"
            >
              <el-option label="全部" value="" />
              <el-option label="初级" value="beginner" />
              <el-option label="中级" value="intermediate" />
              <el-option label="高级" value="advanced" />
            </el-select>

            <el-input
              v-model="searchKeyword"
              placeholder="搜索资源..."
              @input="applyFilters"
              style="width: 200px; margin-right: 10px"
            />

            <el-button type="primary" @click="refreshResources">刷新</el-button>
          </div>
        </div>
      </template>

      <div class="content-layout">
        <div class="courses-panel">
          <h3>课程列表</h3>
          <div class="course-list">
            <div
              v-for="course in courses"
              :key="course.id"
              class="course-item"
              :class="{ active: selectedCourseId === course.id }"
              @click="selectCourse(course.id)"
            >
              <div class="course-title-row">
                <h4>{{ course.title }}</h4>
                <el-tag
                  :type="course.level === '初级' ? 'success' : course.level === '中级' ? 'warning' : 'danger'"
                  size="small"
                >
                  {{ course.level }}
                </el-tag>
              </div>
              <p>{{ course.description }}</p>
              <div class="course-meta">
                <span>{{ course.category }}</span>
                <span>{{ course.resourceCount }} 个资源</span>
              </div>
            </div>
          </div>
        </div>

        <div class="resources-panel">
          <div class="course-info">
            <h3>{{ selectedCourse.title }}</h3>
            <p>{{ selectedCourse.description }}</p>
            <div class="course-tags">
              <el-tag type="info" size="small">{{ selectedCourse.category }}</el-tag>
              <el-tag type="primary" size="small">{{ selectedCourse.level }}</el-tag>
            </div>
          </div>

          <div v-if="filteredResources.length" class="resource-list">
            <div
              v-for="resource in filteredResources"
              :key="resource.id"
              class="resource-item"
            >
              <div class="resource-main">
                <div class="resource-icon" :class="getFileTypeClass(resource.fileType)">
                  <span>{{ getFileTypeIcon(resource.fileType) }}</span>
                </div>
                <div class="resource-info">
                  <h4>{{ resource.title }}</h4>
                  <p>{{ resource.description }}</p>
                </div>
              </div>

              <div class="resource-actions">
                <el-button type="primary" size="small" @click="viewResource(resource)">预览</el-button>
                <el-button type="info" size="small" @click="downloadResource(resource)">下载</el-button>
              </div>
            </div>
          </div>

          <el-empty v-else description="当前课程下暂无匹配资源" />
        </div>
      </div>
    </el-card>

    <el-dialog v-model="previewVisible" :title="previewResource?.title || '资源预览'" width="700px">
      <div class="preview-box">
        <div class="preview-header">
          <el-tag :type="getFileTypeTag(previewResource?.fileType)" size="small">
            {{ getFileTypeName(previewResource?.fileType) }}
          </el-tag>
          <span class="preview-meta">{{ previewResource?.description }}</span>
        </div>
        <div class="preview-content" v-html="previewContent"></div>
      </div>
      <template #footer>
        <el-button @click="previewVisible = false">关闭</el-button>
        <el-button type="primary" @click="downloadResource(previewResource)">下载</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

const courses = ref([
  {
    id: 1,
    title: 'Python基础',
    description: '适合零基础用户，帮助你快速掌握 Python 的核心语法与实践能力。',
    category: '编程',
    level: '初级',
    resourceCount: 4,
    resources: [
      {
        id: 101,
        title: 'Python 基础课件.pdf',
        type: 'document',
        fileType: 'pdf',
        description: '包含基础语法、函数与文件操作的 PDF 课件。',
        difficulty: 'beginner',
        level: '初级',
        duration: 25,
        rating: 4.6,
        tags: ['Python', '基础', '课件'],
        isFavorite: false,
        previewText: '这是 Python 基础课件的预览内容，后端接口准备好后可以直接替换为真实 PDF/文档内容。',
      },
      {
        id: 102,
        title: 'Python 练习题.doc',
        type: 'exercise',
        fileType: 'doc',
        description: '适合巩固知识点的 Word 练习题。',
        difficulty: 'beginner',
        level: '初级',
        duration: 20,
        rating: 4.3,
        tags: ['Python', '练习', 'Word'],
        isFavorite: false,
        previewText: '练习题内容将从后端接口返回，当前先展示模拟内容。',
      },
      {
        id: 103,
        title: 'Python 速查笔记.txt',
        type: 'document',
        fileType: 'text',
        description: '用于查阅常用语法和函数的文本笔记。',
        difficulty: 'beginner',
        level: '初级',
        duration: 10,
        rating: 4.4,
        tags: ['Python', '速查', '笔记'],
        isFavorite: true,
        previewText: 'print("Hello World")\nfor i in range(3):\n    print(i)',
      },
      {
        id: 104,
        title: 'Python 学习路线.ppt',
        type: 'document',
        fileType: 'ppt',
        description: '一份带有学习路线和重点模块的 PPT。',
        difficulty: 'beginner',
        level: '初级',
        duration: 15,
        rating: 4.7,
        tags: ['Python', '路线图', 'PPT'],
        isFavorite: false,
        previewText: '本节介绍 Python 学习路径：基础语法 → 数据结构 → 文件操作 → 框架应用。',
      },
    ],
  },
  {
    id: 2,
    title: '计算机网络',
    description: '重点讲解网络协议、TCP/IP 和常见网络问题分析。',
    category: '基础课',
    level: '中级',
    resourceCount: 3,
    resources: [
      {
        id: 201,
        title: '网络协议总结.pdf',
        type: 'document',
        fileType: 'pdf',
        description: '网络协议和数据传输的核心要点总结。',
        difficulty: 'intermediate',
        level: '中级',
        duration: 30,
        rating: 4.5,
        tags: ['网络', '协议', 'PDF'],
        isFavorite: false,
        previewText: 'TCP / IP、HTTP / HTTPS、DNS、端口和路由相关知识摘要。',
      },
      {
        id: 202,
        title: '网络实验指导.docx',
        type: 'exercise',
        fileType: 'doc',
        description: '课堂实验步骤和思考题。',
        difficulty: 'intermediate',
        level: '中级',
        duration: 25,
        rating: 4.2,
        tags: ['实验', '网络', '文档'],
        isFavorite: false,
        previewText: '实验一：查看本机 IP 配置；实验二：利用 ping 和 tracert 排查问题。',
      },
      {
        id: 203,
        title: '网络拓扑图.ppt',
        type: 'document',
        fileType: 'ppt',
        description: '网络结构与拓扑展示。',
        difficulty: 'intermediate',
        level: '中级',
        duration: 20,
        rating: 4.6,
        tags: ['拓扑', 'PPT', '网络'],
        isFavorite: true,
        previewText: '本节展示局域网、交换机、路由器和外部网络之间的连接关系。',
      },
    ],
  },
  {
    id: 3,
    title: '编译原理',
    description: '系统学习词法分析、语法分析、语义分析和代码生成。',
    category: '专业课',
    level: '高级',
    resourceCount: 3,
    resources: [
      {
        id: 301,
        title: '编译原理导论.pdf',
        type: 'document',
        fileType: 'pdf',
        description: '编译原理课程整体框架与核心概念。',
        difficulty: 'advanced',
        level: '高级',
        duration: 35,
        rating: 4.7,
        tags: ['编译', '理论', 'PDF'],
        isFavorite: false,
        previewText: '编译过程包括词法分析、语法分析、语义分析、中间代码生成和目标代码生成。',
      },
      {
        id: 302,
        title: 'LR(1)分析法.ppt',
        type: 'document',
        fileType: 'ppt',
        description: '介绍 LR(1) 语法分析方法和推导过程。',
        difficulty: 'advanced',
        level: '高级',
        duration: 25,
        rating: 4.5,
        tags: ['语法分析', 'LR(1)', 'PPT'],
        isFavorite: false,
        previewText: '通过项集构造和状态转移表理解 LR(1) 的分析流程。',
      },
      {
        id: 303,
        title: '编译实验说明.txt',
        type: 'exercise',
        fileType: 'text',
        description: '编译器实验的步骤说明和注意事项。',
        difficulty: 'advanced',
        level: '高级',
        duration: 20,
        rating: 4.3,
        tags: ['实验', '编译', '文本'],
        isFavorite: true,
        previewText: '实验要求：实现简单词法分析器，并输出 token 序列。',
      },
    ],
  },
  {
    id: 4,
    title: '人工神经网络',
    description: '基于神经网络的理论基础、训练方法与实践案例。',
    category: '人工智能',
    level: '中级',
    resourceCount: 3,
    resources: [
      {
        id: 401,
        title: '神经网络基础.pdf',
        type: 'document',
        fileType: 'pdf',
        description: '介绍感知机、激活函数和多层网络结构。',
        difficulty: 'intermediate',
        level: '中级',
        duration: 30,
        rating: 4.6,
        tags: ['神经网络', '基础', 'PDF'],
        isFavorite: false,
        previewText: '神经网络由输入层、隐藏层和输出层构成，使用反向传播进行训练。',
      },
      {
        id: 402,
        title: '训练技巧.doc',
        type: 'exercise',
        fileType: 'doc',
        description: '介绍训练集划分、正则化和优化策略。',
        difficulty: 'intermediate',
        level: '中级',
        duration: 25,
        rating: 4.4,
        tags: ['训练', '优化', 'Word'],
        isFavorite: false,
        previewText: '学习率、批大小、正则化和早停策略对模型效果有重要影响。',
      },
      {
        id: 403,
        title: '案例演示.ppt',
        type: 'document',
        fileType: 'ppt',
        description: '展示一个简单的神经网络分类案例。',
        difficulty: 'intermediate',
        level: '中级',
        duration: 20,
        rating: 4.8,
        tags: ['案例', 'PPT', '神经网络'],
        isFavorite: true,
        previewText: '该案例展示如何用 PyTorch 构建一个手写数字识别模型。',
      },
    ],
  },
])

const filterType = ref('')
const filterDifficulty = ref('')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(6)
const selectedCourseId = ref(courses.value[0].id)
const previewVisible = ref(false)
const previewResource = ref(null)
const previewContent = ref('')

const selectedCourse = computed(() => {
  return courses.value.find((item) => item.id === selectedCourseId.value) || courses.value[0]
})

const filteredResources = computed(() => {
  let result = selectedCourse.value.resources || []

  if (filterType.value) {
    result = result.filter((item) => item.type === filterType.value)
  }

  if (filterDifficulty.value) {
    result = result.filter((item) => item.difficulty === filterDifficulty.value)
  }

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(
      (item) =>
        item.title.toLowerCase().includes(keyword) ||
        item.description.toLowerCase().includes(keyword) ||
        item.tags.some((tag) => tag.toLowerCase().includes(keyword)),
    )
  }

  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return result.slice(start, end)
})

const selectCourse = (courseId) => {
  selectedCourseId.value = courseId
  filterType.value = ''
  filterDifficulty.value = ''
  searchKeyword.value = ''
  currentPage.value = 1
}

const getResourceTypeTag = (type) => {
  const types = {
    document: 'primary',
    video: 'success',
    code: 'warning',
    exercise: 'danger',
  }
  return types[type] || 'info'
}

const getResourceTypeName = (type) => {
  const names = {
    document: '文档',
    video: '视频',
    code: '代码',
    exercise: '练习',
  }
  return names[type] || type
}

const getFileTypeName = (fileType) => {
  const names = {
    pdf: 'PDF',
    doc: 'Word',
    ppt: 'PPT',
    text: '文本',
  }
  return names[fileType] || fileType || '文件'
}

const getFileTypeIcon = (fileType) => {
  const icons = {
    pdf: 'PDF',
    doc: 'DOC',
    ppt: 'PPT',
    text: 'TXT',
  }
  return icons[fileType] || 'FILE'
}

const getFileTypeClass = (fileType) => {
  const classes = {
    pdf: 'icon-pdf',
    doc: 'icon-doc',
    ppt: 'icon-ppt',
    text: 'icon-text',
  }
  return classes[fileType] || 'icon-file'
}

const getResourceDifficultyTag = (difficulty) => {
  const difficulties = {
    beginner: 'success',
    intermediate: 'warning',
    advanced: 'danger',
  }
  return difficulties[difficulty] || 'info'
}

const applyFilters = () => {
  currentPage.value = 1
}

const refreshResources = () => {
  filterType.value = ''
  filterDifficulty.value = ''
  searchKeyword.value = ''
  currentPage.value = 1
  ElMessage.success('已刷新当前课程资源')
}

const viewResource = (resource) => {
  previewResource.value = resource
  previewContent.value = buildPreviewContent(resource)
  previewVisible.value = true
  ElMessage.success(`正在预览：${resource.title}`)
}

const buildPreviewContent = (resource) => {
  const body = resource.previewText || '当前为模拟预览内容，后端接口接入后可替换为真实文件内容。'
  return `<div class="preview-body"><p>${body}</p><p class="preview-hint">后续接入真实 API 后，这里会直接显示 PDF、Word、PPT 或文本内容。</p></div>`
}

const downloadResource = (resource) => {
  if (!resource) return
  const fileName = `${resource.title}.${resource.fileType || 'txt'}`
  const content = resource.previewText || `资源名称：${resource.title}`
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = fileName
  link.click()
  URL.revokeObjectURL(link.href)
  ElMessage.success(`开始下载：${resource.title}`)
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}
</script>

<style scoped>
.resources-container {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.subtitle {
  margin: 6px 0 0;
  color: #718096;
}

.filters {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.content-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 20px;
  margin-top: 20px;
}

.courses-panel,
.resources-panel {
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px;
}

.course-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 12px;
}

.course-item {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px;
  background: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
}

.course-item:hover,
.course-item.active {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.course-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.course-title-row h4 {
  margin: 0;
  font-size: 1rem;
  color: #1a365d;
}

.course-item p {
  margin: 8px 0;
  color: #4a5568;
  font-size: 0.92rem;
}

.course-meta {
  display: flex;
  justify-content: space-between;
  color: #718096;
  font-size: 0.85rem;
}

.course-info {
  margin-bottom: 16px;
}

.course-info h3 {
  margin: 0 0 8px;
  color: #1a365d;
}

.course-info p {
  margin: 0 0 10px;
  color: #4a5568;
}

.course-tags {
  display: flex;
  gap: 8px;
}

.resource-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.resource-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 14px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.2s ease;
}

.resource-item:hover {
  transform: translateY(-2px);
  border-color: #409eff;
  box-shadow: 0 8px 18px rgba(64, 158, 255, 0.12);
}

.resource-main {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.resource-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 700;
  font-size: 0.85rem;
  letter-spacing: 0.04em;
  flex-shrink: 0;
  background: linear-gradient(135deg, #94a3b8, #64748b);
}

.resource-icon.icon-pdf {
  background: linear-gradient(135deg, #f87171, #ef4444);
}

.resource-icon.icon-doc {
  background: linear-gradient(135deg, #60a5fa, #2563eb);
}

.resource-icon.icon-ppt {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
}

.resource-icon.icon-text {
  background: linear-gradient(135deg, #34d399, #10b981);
}

.resource-info h4 {
  margin: 0 0 4px;
  color: #1a365d;
  font-size: 1rem;
}

.resource-info p {
  margin: 0;
  color: #4a5568;
  font-size: 0.92rem;
  line-height: 1.4;
}

.resource-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.resource-actions .el-button {
  transition: all 0.2s ease;
}

.preview-box {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.preview-meta {
  color: #4a5568;
}

.preview-content {
  background: #f8fafc;
  border-radius: 8px;
  padding: 14px;
  min-height: 180px;
  color: #2d3748;
}

.preview-hint {
  color: #718096;
  margin-top: 8px;
}

@media (max-width: 960px) {
  .content-layout {
    grid-template-columns: 1fr;
  }

  .header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
