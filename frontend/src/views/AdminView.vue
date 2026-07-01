<template>
  <div class="admin-container">
    <el-tabs v-model="activeTab" type="border-card">
      <el-tab-pane label="用户管理" name="users">
        <el-card>
          <template #header>
            <div class="tab-header">
              <h3>用户管理</h3>
              <el-button type="primary" @click="addUser">新增用户</el-button>
            </div>
          </template>

          <el-table :data="users" style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="username" label="用户名" />
            <el-table-column prop="email" label="邮箱" />
            <el-table-column prop="role" label="角色">
              <template #default="{ row }">
                <el-tag :type="getRoleType(row.role)">{{ row.role }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="createTime" label="创建时间" />
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button size="small" @click="editUser(row)">编辑</el-button>
                <el-button size="small" type="danger" @click="deleteUser(row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="资源管理" name="resources">
        <el-card>
          <template #header>
            <div class="tab-header">
              <h3>资源管理</h3>
              <el-button type="primary" @click="addResource">新增资源</el-button>
            </div>
          </template>

          <el-table :data="adminResources" style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="type" label="类型">
              <template #default="{ row }">
                <el-tag :type="getResourceTypeTag(row.type)">{{
                  getResourceTypeName(row.type)
                }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="difficulty" label="难度">
              <template #default="{ row }">
                <el-tag :type="getResourceDifficultyTag(row.difficulty)">{{
                  row.difficulty
                }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="viewCount" label="浏览量" width="100" />
            <el-table-column prop="likeCount" label="点赞数" width="100" />
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button size="small" @click="editResource(row)">编辑</el-button>
                <el-button size="small" type="danger" @click="deleteResource(row.id)"
                  >删除</el-button
                >
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="系统统计" name="stats">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-item">
                <div class="stat-number">{{ stats.totalUsers }}</div>
                <div class="stat-label">总用户数</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-item">
                <div class="stat-number">{{ stats.totalResources }}</div>
                <div class="stat-label">资源总数</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-item">
                <div class="stat-number">{{ stats.dailyActive }}</div>
                <div class="stat-label">日活跃用户</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-item">
                <div class="stat-number">{{ stats.monthlyGrowth }}%</div>
                <div class="stat-label">月增长率</div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-card header="系统健康状态" style="margin-top: 20px">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="CPU使用率">
              <el-progress :percentage="cpuUsage" :color="getCpuColor(cpuUsage)" />
            </el-descriptions-item>
            <el-descriptions-item label="内存使用率">
              <el-progress :percentage="memoryUsage" :color="getMemoryColor(memoryUsage)" />
            </el-descriptions-item>
            <el-descriptions-item label="数据库连接数">{{ dbConnections }}</el-descriptions-item>
            <el-descriptions-item label="API响应时间">{{ apiResponseTime }}ms</el-descriptions-item>
            <el-descriptions-item label="系统状态">
              <el-tag :type="systemStatus.type">{{ systemStatus.text }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="最后更新">{{ lastUpdate }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 用户编辑对话框 -->
    <el-dialog v-model="userDialogVisible" title="编辑用户" width="500px">
      <el-form :model="currentEditUser" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="currentEditUser.username" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="currentEditUser.email" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="currentEditUser.role">
            <el-option label="学生" value="student" />
            <el-option label="教师" value="teacher" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="userDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveUser">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 资源编辑对话框 -->
    <el-dialog v-model="resourceDialogVisible" title="编辑资源" width="600px">
      <el-form :model="currentEditResource" label-width="100px">
        <el-form-item label="标题">
          <el-input v-model="currentEditResource.title" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="currentEditResource.type">
            <el-option label="文档" value="document" />
            <el-option label="视频" value="video" />
            <el-option label="代码" value="code" />
            <el-option label="练习" value="exercise" />
          </el-select>
        </el-form-item>
        <el-form-item label="难度">
          <el-select v-model="currentEditResource.difficulty">
            <el-option label="初级" value="beginner" />
            <el-option label="中级" value="intermediate" />
            <el-option label="高级" value="advanced" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="currentEditResource.description" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="resourceDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveResource">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const activeTab = ref('users')

// 模拟用户数据
const users = ref([
  { id: 1, username: 'admin', email: 'admin@example.com', role: 'admin', createTime: '2024-01-01' },
  {
    id: 2,
    username: 'teacher1',
    email: 'teacher1@example.com',
    role: 'teacher',
    createTime: '2024-01-02',
  },
  {
    id: 3,
    username: 'student1',
    email: 'student1@example.com',
    role: 'student',
    createTime: '2024-01-03',
  },
  {
    id: 4,
    username: 'student2',
    email: 'student2@example.com',
    role: 'student',
    createTime: '2024-01-04',
  },
])

// 模拟资源数据
const adminResources = ref([
  {
    id: 1,
    title: 'Python基础教程',
    type: 'document',
    difficulty: 'beginner',
    viewCount: 1200,
    likeCount: 85,
  },
  {
    id: 2,
    title: '机器学习实战',
    type: 'video',
    difficulty: 'intermediate',
    viewCount: 850,
    likeCount: 60,
  },
  {
    id: 3,
    title: '深度学习代码',
    type: 'code',
    difficulty: 'advanced',
    viewCount: 600,
    likeCount: 45,
  },
  {
    id: 4,
    title: '算法练习题',
    type: 'exercise',
    difficulty: 'intermediate',
    viewCount: 950,
    likeCount: 70,
  },
])

// 统计数据
const stats = ref({
  totalUsers: 1250,
  totalResources: 342,
  dailyActive: 234,
  monthlyGrowth: 12.5,
})

// 系统状态
const cpuUsage = 45
const memoryUsage = 62
const dbConnections = 12
const apiResponseTime = 85
const lastUpdate = new Date().toLocaleString()

const systemStatus = computed(() => {
  if (cpuUsage > 80 || memoryUsage > 85) {
    return { type: 'danger', text: '警告' }
  } else if (cpuUsage > 60 || memoryUsage > 70) {
    return { type: 'warning', text: '注意' }
  } else {
    return { type: 'success', text: '正常' }
  }
})

// 对话框相关
const userDialogVisible = ref(false)
const resourceDialogVisible = ref(false)
const currentEditUser = ref({})
const currentEditResource = ref({})

const getRoleType = (role) => {
  const roles = {
    admin: 'danger',
    teacher: 'warning',
    student: 'success',
  }
  return roles[role] || 'info'
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

const getResourceDifficultyTag = (difficulty) => {
  const difficulties = {
    beginner: 'success',
    intermediate: 'warning',
    advanced: 'danger',
  }
  return difficulties[difficulty] || 'info'
}

const getCpuColor = (usage) => {
  if (usage > 80) return '#f56c6c'
  if (usage > 60) return '#e6a23c'
  return '#67c23a'
}

const getMemoryColor = (usage) => {
  if (usage > 85) return '#f56c6c'
  if (usage > 70) return '#e6a23c'
  return '#67c23a'
}

const addUser = () => {
  currentEditUser.value = { username: '', email: '', role: 'student' }
  userDialogVisible.value = true
}

const editUser = (user) => {
  currentEditUser.value = { ...user }
  userDialogVisible.value = true
}

const deleteUser = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个用户吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    const index = users.value.findIndex((u) => u.id === id)
    if (index > -1) {
      users.value.splice(index, 1)
      ElMessage.success('删除成功')
    }
  } catch (error) {
    // 用户取消删除
  }
}

const saveUser = () => {
  if (currentEditUser.value.id) {
    // 编辑现有用户
    const index = users.value.findIndex((u) => u.id === currentEditUser.value.id)
    if (index > -1) {
      users.value[index] = { ...currentEditUser.value }
    }
  } else {
    // 添加新用户
    const newUser = {
      ...currentEditUser.value,
      id: Math.max(...users.value.map((u) => u.id)) + 1,
      createTime: new Date().toLocaleDateString(),
    }
    users.value.push(newUser)
  }

  userDialogVisible.value = false
  ElMessage.success('保存成功')
}

const addResource = () => {
  currentEditResource.value = {
    title: '',
    type: 'document',
    difficulty: 'beginner',
    description: '',
  }
  resourceDialogVisible.value = true
}

const editResource = (resource) => {
  currentEditResource.value = { ...resource }
  resourceDialogVisible.value = true
}

const deleteResource = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个资源吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    const index = adminResources.value.findIndex((r) => r.id === id)
    if (index > -1) {
      adminResources.value.splice(index, 1)
      ElMessage.success('删除成功')
    }
  } catch (error) {
    // 用户取消删除
  }
}

const saveResource = () => {
  if (currentEditResource.value.id) {
    // 编辑现有资源
    const index = adminResources.value.findIndex((r) => r.id === currentEditResource.value.id)
    if (index > -1) {
      adminResources.value[index] = { ...currentEditResource.value }
    }
  } else {
    // 添加新资源
    const newResource = {
      ...currentEditResource.value,
      id: Math.max(...adminResources.value.map((r) => r.id)) + 1,
      viewCount: 0,
      likeCount: 0,
    }
    adminResources.value.push(newResource)
  }

  resourceDialogVisible.value = false
  ElMessage.success('保存成功')
}
</script>

<style scoped>
.admin-container {
  padding: 20px;
}

.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
