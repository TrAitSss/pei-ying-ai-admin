<template>
  <div>
    <h2>供应商管理 <el-tag>M6</el-tag></h2>
    
    <el-card class="mb-4">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="搜索">
          <el-input v-model="searchForm.q" placeholder="名称/类别/标签" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="showDialog = true">新增供应商</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card>
      <el-table :data="suppliers" v-loading="loading">
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="category" label="类别" width="120" />
        <el-table-column prop="contact_person" label="联系人" width="120" />
        <el-table-column prop="phone" label="电话" width="150" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="editSupplier(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="deleteSupplier(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <el-dialog v-model="showDialog" :title="editingId ? '编辑供应商' : '新增供应商'" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称" required><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="类别"><el-input v-model="form.category" /></el-form-item>
        <el-form-item label="联系人"><el-input v-model="form.contact_person" /></el-form-item>
        <el-form-item label="电话"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
        <el-form-item label="地址"><el-input v-model="form.address" type="textarea" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.notes" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="saveSupplier">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../api/axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const suppliers = ref([])
const loading = ref(false)
const showDialog = ref(false)
const editingId = ref(null)

const searchForm = reactive({ q: '' })
const form = reactive({
  name: '', category: '', contact_person: '', phone: '', email: '', address: '', notes: '', tags: []
})

onMounted(loadSuppliers)

async function loadSuppliers() {
  loading.value = true
  try {
    const res = await api.get('/suppliers', { params: searchForm })
    suppliers.value = res.data
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  loadSuppliers()
}

function editSupplier(row) {
  editingId.value = row.id
  Object.assign(form, row)
  showDialog.value = true
}

async function saveSupplier() {
  try {
    if (editingId.value) {
      await api.put(`/suppliers/${editingId.value}`, form)
      ElMessage.success('更新成功')
    } else {
      await api.post('/suppliers', form)
      ElMessage.success('添加成功')
    }
    showDialog.value = false
    resetForm()
    loadSuppliers()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

async function deleteSupplier(id) {
  try {
    await ElMessageBox.confirm('确定删除?', '提示', { type: 'warning' })
    await api.delete(`/suppliers/${id}`)
    ElMessage.success('已删除')
    loadSuppliers()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

function resetForm() {
  editingId.value = null
  Object.assign(form, { name: '', category: '', contact_person: '', phone: '', email: '', address: '', notes: '', tags: [] })
}
</script>

<style scoped>
.mb-4 { margin-bottom: 20px; }
</style>
