<template>
  <div class="resources-container">
    <el-card>
      <template #header>
        <div class="header">
          <div>
            <h2>学习资源中心</h2>
            <p class="subtitle">按知识库目录结构分组展示，点击分组展开查看文件</p>
          </div>
          <div class="filters">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索文件..."
              @input="applyFilters"
              style="width: 220px; margin-right: 10px"
            />
            <el-button type="primary" @click="refreshResources" :loading="loading">刷新</el-button>
          </div>
        </div>
      </template>

      <div class="content-layout">
        <div class="courses-panel">
          <h3>课程列表</h3>
          <el-skeleton v-if="loadingCourses" :rows="4" animated />
          <div v-else class="course-list">
            <div
              v-for="course in courses"
              :key="course.id"
              class="course-item"
              :class="{ active: selectedCourseDir === course.dir_name }"
              @click="selectCourse(course)"
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
                <span>{{ course.resource_count }} 个文件</span>
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
              <el-tag type="success" size="small">{{ totalFileCount }} 个文件</el-tag>
            </div>
            <div v-if="selectedCourse.bilibili_url" class="bilibili-link">
              <el-icon :size="16" color="#fb7299"><VideoPlay /></el-icon>
              <span>B站推荐教程：</span>
              <a :href="selectedCourse.bilibili_url" target="_blank" rel="noopener">{{ selectedCourse.bilibili_title }}</a>
            </div>
          </div>

          <el-skeleton v-if="loadingFiles" :rows="5" animated />

          <div v-else-if="filteredGroups.length" class="group-tree">
            <div
              v-for="group in filteredGroups"
              :key="group.name"
              class="group-panel"
            >
              <div class="group-header" @click="toggleGroup(group.name)">
                <div class="group-header-left">
                  <el-icon class="group-arrow" :class="{ expanded: expandedGroups[group.name] }">
                    <ArrowRight />
                  </el-icon>
                  <span class="group-name">{{ group.name }}</span>
                  <el-tag size="small" type="info">{{ group.file_count }} 个文件</el-tag>
                </div>
              </div>

              <div class="group-body" v-show="expandedGroups[group.name]">
                <div
                  v-for="child in group.children"
                  :key="group.name + '-' + (child.name || 'root')"
                  class="sub-group"
                >
                  <div
                    v-if="child.name"
                    class="sub-group-header"
                    @click="toggleSubGroup(group.name + '/' + child.name)"
                  >
                    <el-icon class="sub-arrow" :class="{ expanded: expandedSubGroups[group.name + '/' + child.name] }">
                      <ArrowRight />
                    </el-icon>
                    <span class="sub-group-name">{{ child.name }}</span>
                    <el-tag size="small" class="tag-light">{{ child.file_count }} 个文件</el-tag>
                  </div>

                  <div
                    class="sub-group-files"
                    :class="{ 'no-header': !child.name }"
                    v-show="!child.name || expandedSubGroups[group.name + '/' + child.name]"
                  >
                    <div
                      v-for="file in child.files"
                      :key="file.relative_path"
                      class="resource-item"
                    >
                      <div class="resource-main">
                        <div class="resource-icon" :class="'icon-' + file.file_type">
                          <span>{{ file.file_type.toUpperCase() }}</span>
                        </div>
                        <div class="resource-info">
                          <h4>{{ file.title }}</h4>
                          <p>{{ file.type_label }} · {{ file.size_display }}</p>
                        </div>
                      </div>

                      <div class="resource-actions">
                        <el-button type="primary" size="small" @click="viewResource(file)">预览</el-button>
                        <el-button type="info" size="small" @click="downloadResource(file)">下载</el-button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <el-empty v-else description="当前课程下暂无匹配文件" />
        </div>
      </div>
    </el-card>

    <el-dialog
      v-model="previewVisible"
      :title="previewFileData?.title || '文件预览'"
      width="80%"
      top="3vh"
      destroy-on-close
    >
      <div class="preview-box">
        <div class="preview-header">
          <el-tag :type="getFileTypeTag(previewFileData?.file_type)" size="small">
            {{ previewFileData?.type_label }}
          </el-tag>
          <span class="preview-meta">{{ previewFileData?.size_display }}</span>
          <span v-if="previewLoading" class="preview-meta">加载中...</span>
        </div>
        <div v-if="previewLoading" style="text-align:center; padding: 60px;">
          <el-icon class="is-loading" :size="32"><Loading /></el-icon>
          <p style="margin-top: 12px; color: #718096;">正在加载预览内容...</p>
        </div>
        <div v-else-if="previewError" class="preview-error">
          <el-icon :size="48" color="#e53e3e"><WarningFilled /></el-icon>
          <p>{{ previewError }}</p>
          <el-button type="primary" size="small" @click="downloadResource(previewFileData)">直接下载查看</el-button>
        </div>
        <pre v-else-if="previewContent" class="preview-text">{{ previewContent }}</pre>
        <div v-else class="preview-empty">
          <el-icon :size="48" color="#cbd5e0"><Document /></el-icon>
          <p>暂无预览内容</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="previewVisible = false">关闭</el-button>
        <el-button type="primary" @click="downloadResource(previewFileData)">下载</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getLearningResources, getCourseFiles, downloadFile, previewFile } from '@/api/api'
import { Loading, WarningFilled, Document, ArrowRight, VideoPlay } from '@element-plus/icons-vue'

const courses = ref([])
const courseGroups = ref([])
const selectedCourseDir = ref('')
const selectedCourse = ref({ title: '请选择课程', description: '', category: '', level: '' })
const searchKeyword = ref('')
const loading = ref(false)
const loadingCourses = ref(false)
const loadingFiles = ref(false)
const expandedGroups = ref({})
const expandedSubGroups = ref({})
const previewVisible = ref(false)
const previewFileData = ref(null)
const previewContent = ref('')
const previewLoading = ref(false)
const previewError = ref('')

const totalFileCount = computed(() => {
  return courseGroups.value.reduce((sum, g) => sum + (g.file_count || 0), 0)
})

const filteredGroups = computed(() => {
  if (!searchKeyword.value) return courseGroups.value

  const keyword = searchKeyword.value.toLowerCase()

  return courseGroups.value
    .map((group) => {
      const matchedChildren = group.children
        .map((child) => {
          const matchedFiles = child.files.filter(
            (f) => f.title.toLowerCase().includes(keyword)
          )
          return matchedFiles.length > 0
            ? { ...child, files: matchedFiles, file_count: matchedFiles.length }
            : null
        })
        .filter(Boolean)

      if (matchedChildren.length === 0) return null

      return {
        ...group,
        children: matchedChildren,
        file_count: matchedChildren.reduce((s, c) => s + c.file_count, 0),
      }
    })
    .filter(Boolean)
})

const toggleGroup = (name) => {
  expandedGroups.value[name] = !expandedGroups.value[name]
}

const toggleSubGroup = (key) => {
  expandedSubGroups.value[key] = !expandedSubGroups.value[key]
}

const fetchCourses = async () => {
  loadingCourses.value = true
  try {
    const res = await getLearningResources()
    const data = res?.data?.data || {}
    courses.value = (data.courses || []).map((c) => ({ ...c }))
    if (courses.value.length > 0 && !selectedCourseDir.value) {
      selectCourse(courses.value[0])
    }
  } catch (err) {
    console.error('获取课程列表失败:', err)
    ElMessage.warning('无法获取课程列表，请检查后端服务是否启动')
  } finally {
    loadingCourses.value = false
  }
}

const selectCourse = async (course) => {
  selectedCourseDir.value = course.dir_name
  selectedCourse.value = course
  searchKeyword.value = ''
  expandedGroups.value = {}
  expandedSubGroups.value = {}
  await fetchCourseFiles(course.dir_name)
}

const fetchCourseFiles = async (courseName) => {
  loadingFiles.value = true
  courseGroups.value = []
  try {
    const res = await getCourseFiles(courseName)
    const data = res?.data?.data || {}
    courseGroups.value = data.groups || []
    // 默认展开所有分组
    courseGroups.value.forEach((g) => {
      expandedGroups.value[g.name] = true
      g.children.forEach((c) => {
        if (c.name) {
          expandedSubGroups.value[g.name + '/' + c.name] = true
        }
      })
    })
  } catch (err) {
    console.error('获取文件列表失败:', err)
    ElMessage.error('获取文件列表失败')
  } finally {
    loadingFiles.value = false
  }
}

const viewResource = async (file) => {
  previewFileData.value = file
  previewVisible.value = true
  previewContent.value = ''
  previewError.value = ''
  previewLoading.value = true

  if (file.file_type === 'text') {
    try {
      const res = await previewFile(selectedCourseDir.value, file.relative_path)
      const data = res?.data?.data || {}
      if (res?.data?.code === 200 && data.content) {
        previewContent.value = data.content
      } else {
        previewError.value = data?.error || '预览失败，请下载后查看'
      }
    } catch (err) {
      previewError.value = '预览请求失败，请下载后查看'
    }
  } else {
    previewError.value = `${file.type_label}文件不支持在线预览，请点击下载按钮下载后查看`
  }
  previewLoading.value = false
}

const downloadResource = (file) => {
  if (!file || !selectedCourseDir.value) return
  const url = downloadFile(selectedCourseDir.value, file.relative_path)
  const link = document.createElement('a')
  link.href = url
  link.download = file.title
  link.click()
  ElMessage.success(`开始下载：${file.title}`)
}

const applyFilters = () => {}

const refreshResources = async () => {
  searchKeyword.value = ''
  loading.value = true
  await fetchCourses()
  if (selectedCourseDir.value) {
    await fetchCourseFiles(selectedCourseDir.value)
  }
  loading.value = false
  ElMessage.success('已刷新课程资源')
}

const getFileTypeTag = (fileType) => {
  const tags = {
    pdf: 'danger',
    doc: 'warning',
    ppt: 'success',
    text: '',
  }
  return tags[fileType] || 'info'
}

onMounted(() => {
  fetchCourses()
})
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
  flex-wrap: wrap;
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
  font-size: 15px;
  color: #1a365d;
}

.course-item p {
  margin: 6px 0;
  font-size: 13px;
  color: #718096;
  line-height: 1.5;
}

.course-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #a0aec0;
}

.course-info {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.course-info h3 {
  margin: 0 0 6px;
  font-size: 18px;
  color: #1a365d;
}

.course-info p {
  margin: 0 0 10px;
  color: #718096;
  font-size: 14px;
}

.course-tags {
  display: flex;
  gap: 8px;
}

.bilibili-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 12px;
  padding: 8px 14px;
  background: #fff5f7;
  border: 1px solid #fcd5e0;
  border-radius: 8px;
  font-size: 13px;
  color: #4a5568;
}

.bilibili-link a {
  color: #fb7299;
  text-decoration: none;
  font-weight: 500;
}

.bilibili-link a:hover {
  text-decoration: underline;
  color: #e85d8a;
}

/* 分组树 */
.group-tree {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.group-panel {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #fff;
  overflow: hidden;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  background: #edf2f7;
  transition: background 0.2s;
  user-select: none;
}

.group-header:hover {
  background: #e2e8f0;
}

.group-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.group-arrow {
  transition: transform 0.2s;
  font-size: 14px;
  color: #718096;
}

.group-arrow.expanded {
  transform: rotate(90deg);
}

.group-name {
  font-weight: 600;
  font-size: 15px;
  color: #2d3748;
}

.group-body {
  padding: 0;
}

/* 子分组 */
.sub-group {
  border-bottom: 1px solid #edf2f7;
}

.sub-group:last-child {
  border-bottom: none;
}

.sub-group-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px 10px 32px;
  cursor: pointer;
  background: #f7fafc;
  transition: background 0.2s;
  user-select: none;
}

.sub-group-header:hover {
  background: #edf2f7;
}

.sub-arrow {
  transition: transform 0.2s;
  font-size: 12px;
  color: #a0aec0;
}

.sub-arrow.expanded {
  transform: rotate(90deg);
}

.sub-group-name {
  font-size: 14px;
  color: #4a5568;
  flex: 1;
}

.tag-light {
  background: #edf2f7 !important;
  border-color: #e2e8f0 !important;
  color: #718096 !important;
}

.sub-group-files {
  padding: 0 16px 8px 48px;
}

.sub-group-files.no-header {
  padding: 8px 16px 8px 32px;
}

/* 文件项 */
.resource-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: #f7fafc;
  border-radius: 8px;
  border: 1px solid #edf2f7;
  margin-bottom: 6px;
  transition: all 0.2s;
}

.resource-item:last-child {
  margin-bottom: 0;
}

.resource-item:hover {
  background: #ebf4ff;
  border-color: #bee3f8;
}

.resource-main {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.resource-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
}

.icon-pdf {
  background: #e53e3e;
}

.icon-doc {
  background: #3182ce;
}

.icon-ppt {
  background: #38a169;
}

.icon-text {
  background: #718096;
}

.resource-info h4 {
  margin: 0 0 2px;
  font-size: 13px;
  color: #1a365d;
  word-break: break-all;
}

.resource-info p {
  margin: 0;
  font-size: 11px;
  color: #a0aec0;
}

.resource-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

/* 预览弹窗 */
.preview-box {
  min-height: 300px;
  max-height: 70vh;
  overflow: auto;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e2e8f0;
}

.preview-meta {
  color: #a0aec0;
  font-size: 13px;
}

.preview-text {
  background: #f7fafc;
  padding: 20px;
  border-radius: 8px;
  white-space: pre-wrap;
  word-break: break-all;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #2d3748;
  max-height: 60vh;
  overflow: auto;
}

.preview-error,
.preview-empty {
  text-align: center;
  padding: 60px 20px;
  color: #718096;
}

.preview-error p,
.preview-empty p {
  margin-top: 12px;
  font-size: 14px;
}
</style>