<template>
  <div>
    <h2>模板与文书 <el-tag>M6</el-tag></h2>
    
    <el-card class="mb-4">
      <el-button type="primary" @click="showDialog = true">新增模板</el-button>
      <el-select v-model="filterType" placeholder="类型筛选" clearable style="width: 150px; margin-left: 16px">
        <el-option label="全部" value="" />
        <el-option label="标书" value="tender" />
        <el-option label="报价单" value="quotation" />
        <el-option label="通知书" value="notice" />
      </el-select>
    </el-card>
    
    <el-row :gutter="20">
      <el-col :span="8" v-for="tpl in templates" :key="tpl.id">
        <el-card class="template-card" shadow="hover">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>{{ tpl.name }}</span>
              <el-tag size="small">{{ tpl.template_type }}</el-tag>
            </div>
          </template>
          <p style="color: #666; font-size: 14px; margin-bottom: 16px">{{ tpl.description }}</p>
          <el-button type="primary" @click="generateDoc(tpl)">生成文档</el-button>
          <el-button @click="previewTpl(tpl)">预览</el-button>
        </el-card>
      </el-col>
    </el-row>
    
    <el-dialog v-model="showDialog" title="新增模板" width="700px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称" required><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.template_type">
            <el-option label="标书" value="tender" />
            <el-option label="报价单" value="quotation" />
            <el-option label="通知书" value="notice" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" /></el-form-item>
        <el-form-item label="模板内容">
          <el-input v-model="form.content" type="textarea" :rows="10" placeholder="使用 Jinja2 语法，如 {{ project_name }}" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTemplate">保存</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="genDialogVisible" :title="`生成: ${selectedTpl?.name}`" width="600px">
      <el-form label-width="100px">
        <el-form-item label="标题"><el-input v-model="genForm.title" /></el-form-item>
        <el-form-item v-for="v in selectedTpl?.variables" :key="v.name" :label="v.name">
          <el-input v-model="genForm.variables_data[v.name]" />
        </el-form-item>
        <el-form-item label="自定义变量">
          <el-input v-model="customVars" type="textarea" placeholder='{"project_name": "XXX项目"}' />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="genDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitGenerate">生成</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import api from '../api/axios'
import { ElMessage } from 'element-plus'

const templates = ref([])
const loading = ref(false)
const showDialog = ref(false)
const genDialogVisible = ref(false)
const selectedTpl = ref(null)
const filterType = ref('')

const form = reactive({ name: '', template_type: 'tender', description: '', content: '', variables: [] })
const genForm = reactive({ title: '', variables_data: {} })
const customVars = ref('')

const filteredTemplates = computed(() => {
  if (!filterType.value) return templates.value
  return templates.value.filter(t => t.template_type === filterType.value)
})

onMounted(loadTemplates)

async function loadTemplates() {
  loading.value = true
  try {
    const res = await api.get('/templates', { params: { template_type: filterType.value || undefined } })
    templates.value = res.data
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

async function saveTemplate() {
  try {
    await api.post('/templates', form)
    ElMessage.success('添加成功')
    showDialog.value = false
    loadTemplates()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

function generateDoc(tpl) {
  selectedTpl.value = tpl
  genForm.title = ''
  genForm.variables_data = {}
  customVars.value = ''
  genDialogVisible.value = true
}

async function submitGenerate() {
  try {
    let vars = { ...genForm.variables_data }
    if (customVars.value) {
      vars = { ...vars, ...JSON.parse(customVars.value) }
    }
    const res = await api.post(`/templates/${selectedTpl.value.id}/generate`, {
      template_id: selectedTpl.value.id,
      title: genForm.title,
      variables_data: vars
    })
    ElMessage.success('生成成功')
    genDialogVisible.value = false
  } catch (e) {
    ElMessage.error('生成失败')
  }
}

function previewTpl(tpl) {
  ElMessage.info('预览功能开发中')
}
</script>

<style scoped>
.mb-4 { margin-bottom: 20px; }
.template-card { margin-bottom: 20px; }
</style>
