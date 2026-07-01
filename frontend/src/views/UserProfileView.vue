<template>
  <div class="profile-container">
    <el-card header="学习画像分析" class="section-card">
      <el-row :gutter="20">
        <el-col :xs="24" :md="8">
          <div class="profile-section">
            <h3>知识基础</h3>
            <el-progress
              :percentage="learningProfile.knowledgeBase"
              :stroke-width="20"
              :color="knowledgeColor"
              status="success"
            />
            <p class="progress-text">{{ learningProfile.knowledgeBase }}分</p>
          </div>
        </el-col>

        <el-col :xs="24" :md="8">
          <div class="profile-section">
            <h3>认知风格</h3>
            <el-tag type="info" size="large">{{ learningProfile.cognitiveStyle }}</el-tag>
          </div>
        </el-col>

        <el-col :xs="24" :md="8">
          <div class="profile-section">
            <h3>学习目标</h3>
            <el-tag type="warning" size="large">{{ learningProfile.learningGoals }}</el-tag>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :xs="24" :md="12">
          <div class="profile-section">
            <h3>易错点偏好</h3>
            <div class="error-preferences">
              <el-tag
                v-for="(item, index) in learningProfile.errorPreferences"
                :key="index"
                type="danger"
                style="margin: 5px"
              >
                {{ item }}
              </el-tag>
            </div>
          </div>
        </el-col>

        <el-col :xs="24" :md="12">
          <div class="profile-section">
            <h3>学习风格偏好</h3>
            <el-tag type="success" size="large">{{
              learningProfile.preferredLearningStyle
            }}</el-tag>
          </div>
        </el-col>
      </el-row>

      <el-row style="margin-top: 20px">
        <el-col :span="24">
          <div class="profile-section">
            <h3>学习建议</h3>
            <el-alert title="个性化学习建议" type="info" :closable="false" show-icon>
              <ul>
                <li>
                  建议多进行实践练习，特别是{{
                    learningProfile.errorPreferences.join('、')
                  }}相关的内容
                </li>
                <li>适合{{ learningProfile.preferredLearningStyle }}的学习方式</li>
                <li>
                  当前知识基础{{
                    learningProfile.knowledgeBase >= 70 ? '较好' : '一般'
                  }}，建议循序渐进
                </li>
              </ul>
            </el-alert>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-card header="画像更新" class="section-card">
      <el-form :model="editForm" label-width="120px">
        <el-form-item label="认知风格">
          <el-select v-model="editForm.cognitiveStyle" placeholder="请选择认知风格">
            <el-option label="视觉型" value="视觉型" />
            <el-option label="听觉型" value="听觉型" />
            <el-option label="动觉型" value="动觉型" />
            <el-option label="阅读型" value="阅读型" />
          </el-select>
        </el-form-item>

        <el-form-item label="学习目标">
          <el-input v-model="editForm.learningGoals" placeholder="请输入学习目标" />
        </el-form-item>

        <el-form-item label="学习风格偏好">
          <el-select v-model="editForm.preferredLearningStyle" placeholder="请选择学习风格">
            <el-option label="案例学习" value="案例学习" />
            <el-option label="理论学习" value="理论学习" />
            <el-option label="实践操作" value="实践操作" />
            <el-option label="小组讨论" value="小组讨论" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="updateProfile">更新画像</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, computed } from 'vue'
import { useUserStore } from '@/stores'
import { ElMessage } from 'element-plus'

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

const updateProfile = () => {
  userStore.setLearningProfile({
    ...learningProfile.value,
    cognitiveStyle: editForm.cognitiveStyle,
    learningGoals: editForm.learningGoals,
    preferredLearningStyle: editForm.preferredLearningStyle,
  })
  ElMessage.success('学习画像更新成功！')
}

const resetForm = () => {
  editForm.cognitiveStyle = learningProfile.value.cognitiveStyle
  editForm.learningGoals = learningProfile.value.learningGoals
  editForm.preferredLearningStyle = learningProfile.value.preferredLearningStyle
}
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.section-card {
  margin-bottom: 20px;
  border-radius: 12px;
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
