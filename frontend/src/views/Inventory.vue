<template>
  <div>
    <h2>库存管理 <el-tag>M6</el-tag></h2>
    
    <el-row :gutter="20" class="mb-4">
      <el-col :span="6">
        <el-card :body-style="{ padding: '20px' }">
          <div style="text-align: center">
            <div style="font-size: 28px; font-weight: bold; color: #e53e3e">{{ lowStockCount }}</div>
            <div style="color: #666; margin-top: 8px">库存预警</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card :body-style="{ padding: '20px' }">
          <div style="text-align: center">
            <div style="font-size: 28px; font-weight: bold; color: #2b6cb0">{{ items.length }}</div>
            <div style="color: #666; margin-top: 8px">物品总数</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card class="mb-4">
      <el-button type="primary" @click="showDialog = true">新增物品</el-button>
      <el-button @click="loadLowStock">查看预警</el-button>
    </el-card>
    
    <el-card>
      <el-table :data="items" v-loading="loading">
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="category" label="类别" width="120" />
        <el-table-column prop="current_quantity" label="当前库存" width="100">
          <template #default="{ row }">
            <span :style="{ color: row.current_quantity <= row.min_quantity ? '#e53e3e' : '#333' }">
              {{ row.current_quantity }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="min_quantity" label="最低库存" width="100" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="location" label="存放位置" />
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button size="small" @click="showCountDialog(row)">盘点</el-button>
            <el-button type="danger" size="small" @click="deleteItem(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <el-dialog v-model="showDialog" title="新增物品" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称" required><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="类别"><el-input v-model="form.category" /></el-form-item>
        <el-form-item label="存放位置"><el-input v-model="form.location" /></el-form-item>
        <el-form-item label="当前库存"><el-input-number v-model="form.current_quantity" :min="0" /></el-form-item>
        <el-form-item label="最低库存"><el-input-number v-model="form.min_quantity" :min="0" /></el-form-item>
        <el-form-item label="单位"><el-input v-model="form.unit" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="saveItem">保存</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="countDialogVisible" title="库存盘点" width="400px">
      <el-form label-width="100px">
        <el-form-item label="实际数量">
          <el-input-number v-model="countForm.new_quantity" :min="0" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="countForm.note" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="countDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCount">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../api/axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const items = ref([])
const loading = ref(false)
const showDialog = ref(false)
const countDialogVisible = ref(false)
const currentItem = ref(null)
const lowStockCount = ref(0)

const form = reactive({ name: '', category: '', location: '', current_quantity: 0, min_quantity: 0, unit: '' })
const countForm = reactive({ new_quantity: 0, note: '' })

onMounted(() => {
  loadItems()
  loadLowStock()
})

async function loadItems() {
  loading.value = true
  try {
    const res = await api.get('/inventory/items')
    items.value = res.data
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

async function loadLowStock() {
  try {
    const res = await api.get('/inventory/items/low-stock')
    lowStockCount.value = res.data.total
  } catch (e) {
    console.error(e)
  }
}

async function saveItem() {
  try {
    await api.post('/inventory/items', form)
    ElMessage.success('添加成功')
    showDialog.value = false
    loadItems()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

function showCountDialog(row) {
  currentItem.value = row
  countForm.new_quantity = row.current_quantity
  countForm.note = ''
  countDialogVisible.value = true
}

async function submitCount() {
  try {
    await api.post(`/inventory/items/${currentItem.value.id}/count`, null, {
      params: { new_quantity: countForm.new_quantity, note: countForm.note }
    })
    ElMessage.success('盘点完成')
    countDialogVisible.value = false
    loadItems()
  } catch (e) {
    ElMessage.error('盘点失败')
  }
}

async function deleteItem(id) {
  try {
    await ElMessageBox.confirm('确定删除?', '提示', { type: 'warning' })
    await api.delete(`/inventory/items/${id}`)
    ElMessage.success('已删除')
    loadItems()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}
</script>

<style scoped>
.mb-4 { margin-bottom: 20px; }
</style>
