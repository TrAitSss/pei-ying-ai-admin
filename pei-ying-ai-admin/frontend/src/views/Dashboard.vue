<template>
  <div class="dashboard">
    <div class="page-header">
      <div>
        <h1 class="page-title">{{ greeting }}，{{ authStore.user?.full_name || 'Steven' }}</h1>
        <p class="page-desc">{{ todayStr }} · 工作台概览</p>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card" v-for="stat in stats" :key="stat.key">
        <div class="stat-icon" :style="{ background: stat.bg }">
          <span v-html="stat.icon"></span>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
      </div>
    </div>

    <!-- 库存预警 -->
    <div v-if="alerts.length > 0" class="alert-section">
      <div class="section-header">
        <h2 class="section-title" style="color: #ef4444">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -3px; margin-right: 6px;"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
          库存预警
        </h2>
        <button class="text-btn" @click="$router.push('/inventory')">去处理 →</button>
      </div>
      <div class="alert-list">
        <div class="alert-item" v-for="a in alerts" :key="a.name">
          <span class="alert-name">{{ a.name }}</span>
          <span class="alert-detail">当前 {{ a.current }} / 最低 {{ a.minimum }}</span>
          <span class="alert-badge">缺 {{ a.shortage }}</span>
        </div>
      </div>
    </div>

    <!-- 下方两列 -->
    <div class="bottom-grid">
      <!-- 最近文档 -->
      <div class="panel">
        <h2 class="section-title">最近生成的文档</h2>
        <div v-if="recentDocs.length > 0" class="doc-list">
          <div class="doc-item" v-for="doc in recentDocs" :key="doc.id">
            <div class="doc-info">
              <div class="doc-name">{{ doc.title || '未命名文档' }}</div>
              <div class="doc-meta">{{ formatDate(doc.created_at) }}</div>
            </div>
            <span class="status-tag" :class="doc.status">{{ statusLabel(doc.status) }}</span>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>暂无文档记录</p>
          <button class="text-btn" @click="$router.push('/templates')">生成第一份 →</button>
        </div>
      </div>

      <!-- 快速入口 -->
      <div class="panel">
        <h2 class="section-title">快速操作</h2>
        <div class="quick-grid">
          <div class="quick-card" @click="$router.push('/templates')">
            <div class="quick-icon" style="background: rgba(59, 130, 246, 0.12)">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><line x1="9" y1="15" x2="15" y2="15"/></svg>
            </div>
            <div class="quick-text">
              <div class="quick-name">生成文书</div>
              <div class="quick-desc">选择模板，快速生成标书和报价单</div>
            </div>
          </div>
          <div class="quick-card" @click="$router.push('/suppliers')">
            <div class="quick-icon" style="background: rgba(16, 163, 127, 0.12)">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#10a37f" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            </div>
            <div class="quick-text">
              <div class="quick-name">搜索供应商</div>
              <div class="quick-desc">按类别或关键词查找供应商</div>
            </div>
          </div>
          <div class="quick-card" @click="$router.push('/inventory')">
            <div class="quick-icon" style="background: rgba(245, 158, 11, 0.12)">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg>
            </div>
            <div class="quick-text">
              <div class="quick-name">库存盘点</div>
              <div class="quick-desc">查看库存状态和处理预警</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api/axios'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const stats = ref([
  { key: 'suppliers', label: '供应商', value: 0, icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>', bg: 'rgba(16,163,127,0.12)', color: '#10a37f' },
  { key: 'templates', label: '文书模板', value: 0, icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>', bg: 'rgba(59,130,246,0.12)', color: '#3b82f6' },
  { key: 'inventory', label: '库存物品', value: 0, icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg>', bg: 'rgba(245,158,11,0.12)', color: '#f59e0b' },
  { key: 'lowStock', label: '库存预警', value: 0, icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>', bg: 'rgba(239,68,68,0.12)', color: '#ef4444' },
])
const alerts = ref([])
const recentDocs = ref([])

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return '上午好'
  if (h < 18) return '下午好'
  return '晚上好'
})

const todayStr = computed(() => {
  const d = new Date()
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
})

onMounted(async () => {
  try {
    const res = await api.get('/dashboard/stats')
    const d = res.data
    stats.value[0].value = d.suppliers?.total || 0
    stats.value[1].value = d.templates?.total || 0
    stats.value[2].value = d.inventory?.total || 0
    stats.value[3].value = d.inventory?.low_stock || 0
  } catch (e) { console.error(e) }
  try {
    const alertRes = await api.get('/dashboard/low-stock-alerts')
    alerts.value = alertRes.data
  } catch (e) { console.error(e) }
  try {
    const docRes = await api.get('/dashboard/recent-documents')
    recentDocs.value = docRes.data
  } catch (e) { console.error(e) }
})

function formatDate(s) {
  if (!s) return ''
  const d = new Date(s)
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function statusLabel(s) {
  const m = { draft: '草稿', pending_approval: '待审批', approved: '已通过', rejected: '已拒绝' }
  return m[s] || s
}
</script>

<style scoped>
.dashboard { max-width: 1100px; }

.page-header { margin-bottom: 32px; }
.page-title { font-size: 26px; font-weight: 600; color: #ececec; margin-bottom: 4px; }
.page-desc { font-size: 14px; color: #6b7280; }

.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 28px; }
.stat-card { background: #2f2f2f; border: 1px solid #3f3f3f; border-radius: 12px; padding: 20px; display: flex; align-items: center; gap: 16px; }
.stat-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-icon :deep(svg) { color: inherit; }
.stat-value { font-size: 28px; font-weight: 700; color: #ececec; line-height: 1.2; }
.stat-label { font-size: 13px; color: #6b7280; margin-top: 2px; }

.alert-section { background: rgba(239,68,68,0.06); border: 1px solid rgba(239,68,68,0.2); border-radius: 12px; padding: 20px; margin-bottom: 28px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.section-title { font-size: 16px; font-weight: 600; color: #ececec; }
.text-btn { background: none; border: none; color: #10a37f; cursor: pointer; font-size: 14px; font-weight: 500; padding: 4px 0; }
.text-btn:hover { text-decoration: underline; }

.alert-list { display: flex; flex-direction: column; gap: 8px; }
.alert-item { display: flex; align-items: center; gap: 12px; background: #2f2f2f; border-radius: 8px; padding: 12px 16px; }
.alert-name { flex: 1; font-size: 14px; color: #ececec; }
.alert-detail { font-size: 13px; color: #9ca3af; }
.alert-badge { background: rgba(239,68,68,0.15); color: #ef4444; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }

.bottom-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.panel { background: #2f2f2f; border: 1px solid #3f3f3f; border-radius: 12px; padding: 20px; }
.panel .section-title { margin-bottom: 16px; }

.doc-list { display: flex; flex-direction: column; gap: 2px; }
.doc-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; border-radius: 8px; }
.doc-item:hover { background: #383838; }
.doc-name { font-size: 14px; color: #ececec; }
.doc-meta { font-size: 12px; color: #6b7280; margin-top: 2px; }
.status-tag { padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 500; }
.status-tag.draft { background: rgba(107,114,128,0.2); color: #9ca3af; }
.status-tag.pending_approval { background: rgba(245,158,11,0.15); color: #f59e0b; }
.status-tag.approved { background: rgba(16,163,127,0.15); color: #10a37f; }
.status-tag.rejected { background: rgba(239,68,68,0.15); color: #ef4444; }

.empty-state { text-align: center; padding: 24px 0; color: #4a4a4a; }
.empty-state p { margin-bottom: 8px; }

.quick-grid { display: flex; flex-direction: column; gap: 10px; }
.quick-card { display: flex; align-items: center; gap: 14px; padding: 14px; border-radius: 10px; cursor: pointer; transition: background 0.15s; }
.quick-card:hover { background: #383838; }
.quick-icon { width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.quick-name { font-size: 14px; font-weight: 500; color: #ececec; }
.quick-desc { font-size: 12px; color: #6b7280; margin-top: 2px; }

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .bottom-grid { grid-template-columns: 1fr; }
}
</style>
