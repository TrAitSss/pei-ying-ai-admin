<template>
  <div class="dashboard">
    <h2>Steven 工作台</h2>
    
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6" v-for="stat in stats" :key="stat.key">
        <el-card class="stat-card" :body-style="{ padding: '20px' }">
          <div class="stat-value" :style="{ color: stat.color }">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 库存预警 -->
    <el-card v-if="alerts.length > 0" class="mb-4" style="margin-top: 20px">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span style="color: #e53e3e; font-weight: bold">库存预警（{{ alerts.length }} 项）</span>
          <el-button size="small" @click="$router.push('/inventory')">去处理</el-button>
        </div>
      </template>
      <el-table :data="alerts" size="small">
        <el-table-column prop="name" label="物品" />
        <el-table-column prop="current" label="当前库存" width="100" />
        <el-table-column prop="minimum" label="最低库存" width="100" />
        <el-table-column prop="shortage" label="缺口" width="100">
          <template #default="{ row }">
            <span style="color: #e53e3e; font-weight: bold">-{{ row.shortage }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header><span>最近生成的文档</span></template>
          <el-timeline v-if="recentDocs.length > 0">
            <el-timeline-item
              v-for="doc in recentDocs"
              :key="doc.id"
              :type="doc.status === 'approved' ? 'success' : 'primary'"
            >
              <p style="font-weight: 500">{{ doc.title }}</p>
              <p style="color: #999; font-size: 12px">
                <el-tag size="small" :type="statusType(doc.status)">{{ doc.status }}</el-tag>
                {{ doc.created_at }}
              </p>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无文档" :image-size="60" />
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header><span>快速入口</span></template>
          <div class="quick-links">
            <el-card shadow="hover" class="quick-card" @click="$router.push('/templates')">
              <el-icon style="font-size: 32px; color: #2b6cb0"><DocumentCopy /></el-icon>
              <div style="margin-top: 8px; font-weight: 500">生成标书/报价单</div>
              <div style="font-size: 12px; color: #999; margin-top: 4px">选择模板，填空生成</div>
            </el-card>
            <el-card shadow="hover" class="quick-card" @click="$router.push('/suppliers')">
              <el-icon style="font-size: 32px; color: #38a169"><Shop /></el-icon>
              <div style="margin-top: 8px; font-weight: 500">搜索供应商</div>
              <div style="font-size: 12px; color: #999; margin-top: 4px">按类别/关键词查找</div>
            </el-card>
            <el-card shadow="hover" class="quick-card" @click="$router.push('/inventory')">
              <el-icon style="font-size: 32px; color: #d69e2e"><Box /></el-icon>
              <div style="margin-top: 8px; font-weight: 500">库存盘点</div>
              <div style="font-size: 12px; color: #999; margin-top: 4px">记录数量，查看预警</div>
            </el-card>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/axios'

const stats = ref([
  { key: 'suppliers', label: '供应商', value: 0, color: '#38a169' },
  { key: 'templates', label: '标书模板', value: 0, color: '#2b6cb0' },
  { key: 'inventory', label: '库存物品', value: 0, color: '#d69e2e' },
  { key: 'lowStock', label: '库存预警', value: 0, color: '#e53e3e' },
])

const alerts = ref([])
const recentDocs = ref([])

onMounted(async () => {
  try {
    const res = await api.get('/dashboard/stats')
    const d = res.data
    stats.value = [
      { key: 'suppliers', label: '供应商', value: d.suppliers?.total || 0, color: '#38a169' },
      { key: 'templates', label: '标书模板', value: d.templates?.total || 0, color: '#2b6cb0' },
      { key: 'inventory', label: '库存物品', value: d.inventory?.total || 0, color: '#d69e2e' },
      { key: 'lowStock', label: '库存预警', value: d.inventory?.low_stock || 0, color: '#e53e3e' },
    ]
    
    const alertRes = await api.get('/dashboard/low-stock-alerts')
    alerts.value = alertRes.data
    
    const docRes = await api.get('/dashboard/recent-documents')
    recentDocs.value = docRes.data
  } catch (e) {
    console.error('加载仪表盘失败', e)
  }
})

function statusType(s) {
  const map = { draft: 'info', pending_approval: 'warning', approved: 'success', rejected: 'danger' }
  return map[s] || 'info'
}
</script>

<style scoped>
.dashboard h2 { margin-bottom: 20px; color: #1a365d; }
.stats-row { margin-bottom: 20px; }
.stat-card { text-align: center; }
.stat-value { font-size: 36px; font-weight: bold; margin-bottom: 8px; }
.stat-label { color: #666; font-size: 14px; }
.mb-4 { margin-bottom: 20px; }
.quick-links { display: flex; flex-direction: column; gap: 12px; }
.quick-card { cursor: pointer; text-align: center; padding: 16px; }
.quick-card:hover { border-color: #2b6cb0; }
</style>