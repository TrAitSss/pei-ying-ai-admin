<template>
  <div class="suppliers-page">
    <div class="page-header">
      <h1 class="page-title">供应商搜索</h1>
      <p class="page-desc">按名称、类别或标签搜索供应商</p>
    </div>

    <div class="search-box">
      <svg class="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#6b7280" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
      <input
        v-model="searchQuery"
        class="search-input"
        placeholder="搜索供应商名称、类别..."
        @input="handleSearch"
      />
      <button v-if="searchQuery" class="search-clear" @click="clearSearch">×</button>
      <button class="add-btn" @click="openAdd">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        新增
      </button>
    </div>

    <div v-if="loading" class="loading-state">加载中...</div>

    <div v-else-if="suppliers.length === 0" class="empty-state">
      <p>{{ searchQuery ? '没有找到匹配的供应商' : '暂无供应商数据' }}</p>
    </div>

    <div v-else class="supplier-list">
      <div
        v-for="s in suppliers"
        :key="s.id"
        class="supplier-card"
        :class="{ expanded: expandedId === s.id }"
      >
        <div class="supplier-main" @click="toggleExpand(s.id)">
          <div class="supplier-info">
            <h3 class="supplier-name">{{ s.name }}</h3>
            <div class="supplier-meta">
              <span class="meta-tag" v-if="s.category">{{ s.category }}</span>
              <span class="meta-text" v-if="s.contact_person">{{ s.contact_person }}</span>
              <span class="meta-text" v-if="s.phone">{{ s.phone }}</span>
            </div>
            <div class="supplier-tags" v-if="s.tags && s.tags.length > 0">
              <span class="tag" v-for="tag in s.tags.slice(0, 5)" :key="tag">{{ tag }}</span>
            </div>
          </div>
          <div class="supplier-actions" @click.stop>
            <button class="icon-btn" @click="editSupplier(s)" title="编辑">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            </button>
            <button class="icon-btn danger" @click="deleteSupplier(s.id)" title="删除">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
            </button>
          </div>
        </div>

        <div v-if="expandedId === s.id" class="supplier-detail">
          <div class="detail-grid">
            <div class="detail-item" v-if="s.email">
              <span class="detail-label">邮箱</span>
              <span class="detail-value">{{ s.email }}</span>
            </div>
            <div class="detail-item" v-if="s.address">
              <span class="detail-label">地址</span>
              <span class="detail-value">{{ s.address }}</span>
            </div>
            <div class="detail-item" v-if="s.notes">
              <span class="detail-label">备注</span>
              <span class="detail-value">{{ s.notes }}</span>
            </div>
          </div>

          <div v-if="s.quotation_history && s.quotation_history.length > 0" class="history-section">
            <h4 class="detail-title">历史报价</h4>
            <div class="history-list">
              <div class="history-item" v-for="(h, i) in s.quotation_history" :key="i">
                <span class="history-date">{{ h.date }}</span>
                <span class="history-item-name">{{ h.item }}</span>
                <span class="history-price">HK$ {{ h.price }} × {{ h.qty }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 新增/编辑弹窗 -->
    <div v-if="showDialog" class="modal-overlay" @click.self="showDialog = false">
      <div class="modal">
        <h2 class="modal-title">{{ editingId ? '编辑供应商' : '新增供应商' }}</h2>
        <div class="modal-body">
          <div class="form-row"><label>名称 *</label><input v-model="form.name" placeholder="供应商名称" /></div>
          <div class="form-row"><label>类别</label><input v-model="form.category" placeholder="例如：办公设备、清洁服务" /></div>
          <div class="form-row"><label>联系人</label><input v-model="form.contact_person" placeholder="联系人姓名" /></div>
          <div class="form-row"><label>电话</label><input v-model="form.phone" placeholder="联系电话" /></div>
          <div class="form-row"><label>邮箱</label><input v-model="form.email" placeholder="电子邮箱" /></div>
          <div class="form-row"><label>地址</label><textarea v-model="form.address" rows="2" placeholder="地址"></textarea></div>
          <div class="form-row"><label>备注</label><textarea v-model="form.notes" rows="2" placeholder="备注信息"></textarea></div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="showDialog = false">取消</button>
          <button class="submit-btn" @click="saveSupplier">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../api/axios'

const suppliers = ref([])
const loading = ref(false)
const showDialog = ref(false)
const editingId = ref(null)
const expandedId = ref(null)
const searchQuery = ref('')
let searchTimer = null

const form = reactive({ name: '', category: '', contact_person: '', phone: '', email: '', address: '', notes: '' })

onMounted(loadSuppliers)

async function loadSuppliers() {
  loading.value = true
  try {
    const res = await api.get('/suppliers', { params: searchQuery.value ? { q: searchQuery.value } : {} })
    suppliers.value = res.data
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

function handleSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(loadSuppliers, 300)
}

function clearSearch() {
  searchQuery.value = ''
  loadSuppliers()
}

function toggleExpand(id) {
  expandedId.value = expandedId.value === id ? null : id
}

function openAdd() {
  editingId.value = null
  Object.assign(form, { name: '', category: '', contact_person: '', phone: '', email: '', address: '', notes: '' })
  showDialog.value = true
}

function editSupplier(row) {
  editingId.value = row.id
  Object.assign(form, { name: row.name, category: row.category || '', contact_person: row.contact_person || '', phone: row.phone || '', email: row.email || '', address: row.address || '', notes: row.notes || '' })
  showDialog.value = true
}

async function saveSupplier() {
  if (!form.name) { alert('请填写供应商名称'); return }
  try {
    if (editingId.value) {
      await api.put(`/suppliers/${editingId.value}`, form)
    } else {
      await api.post('/suppliers', form)
    }
    showDialog.value = false
    loadSuppliers()
  } catch (e) { alert('保存失败') }
}

async function deleteSupplier(id) {
  if (!confirm('确定删除此供应商？')) return
  try {
    await api.delete(`/suppliers/${id}`)
    loadSuppliers()
  } catch (e) { alert('删除失败') }
}
</script>

<style scoped>
.suppliers-page { max-width: 900px; }
.page-header { margin-bottom: 28px; }
.page-title { font-size: 26px; font-weight: 600; color: #ececec; margin-bottom: 4px; }
.page-desc { font-size: 14px; color: #6b7280; }

.search-box { display: flex; align-items: center; background: #2f2f2f; border: 1px solid #3f3f3f; border-radius: 12px; padding: 4px 16px; margin-bottom: 20px; transition: border-color 0.15s; }
.search-box:focus-within { border-color: #10a37f; }
.search-icon { flex-shrink: 0; margin-right: 10px; }
.search-input { flex: 1; background: none; border: none; color: #ececec; font-size: 15px; outline: none; padding: 10px 0; }
.search-input::placeholder { color: #4a4a4a; }
.search-clear { background: none; border: none; color: #6b7280; font-size: 20px; cursor: pointer; padding: 4px 8px; }
.search-clear:hover { color: #ececec; }
.add-btn { display: flex; align-items: center; gap: 5px; background: #10a37f; border: none; color: white; padding: 8px 16px; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 500; white-space: nowrap; margin-left: 8px; }
.add-btn:hover { background: #0d8c6d; }

.supplier-list { display: flex; flex-direction: column; gap: 8px; }
.supplier-card { background: #2f2f2f; border: 1px solid #3f3f3f; border-radius: 12px; overflow: hidden; transition: border-color 0.15s; }
.supplier-card:hover { border-color: #4a4a4a; }
.supplier-card.expanded { border-color: #10a37f; }
.supplier-main { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; cursor: pointer; }
.supplier-info { flex: 1; min-width: 0; }
.supplier-name { font-size: 16px; font-weight: 600; color: #ececec; margin-bottom: 6px; }
.supplier-meta { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.meta-tag { background: rgba(16,163,127,0.12); color: #10a37f; padding: 2px 10px; border-radius: 6px; font-size: 12px; font-weight: 500; }
.meta-text { font-size: 13px; color: #6b7280; }
.supplier-tags { display: flex; gap: 6px; margin-top: 8px; flex-wrap: wrap; }
.tag { background: #262626; color: #9ca3af; padding: 2px 8px; border-radius: 4px; font-size: 11px; }

.supplier-actions { display: flex; gap: 6px; flex-shrink: 0; margin-left: 16px; }
.icon-btn { background: none; border: 1px solid #3f3f3f; color: #9ca3af; width: 34px; height: 34px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.15s; }
.icon-btn:hover { background: #383838; color: #ececec; border-color: #4a4a4a; }
.icon-btn.danger:hover { color: #ef4444; border-color: rgba(239,68,68,0.3); background: rgba(239,68,68,0.1); }

.supplier-detail { border-top: 1px solid #3f3f3f; padding: 20px; background: #262626; }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }
.detail-item { display: flex; flex-direction: column; gap: 3px; }
.detail-label { font-size: 12px; color: #6b7280; }
.detail-value { font-size: 14px; color: #ececec; }
.detail-title { font-size: 14px; font-weight: 600; color: #ececec; margin-bottom: 10px; }
.history-list { display: flex; flex-direction: column; gap: 6px; }
.history-item { display: flex; align-items: center; gap: 16px; padding: 8px 12px; background: #2f2f2f; border-radius: 8px; font-size: 13px; }
.history-date { color: #6b7280; width: 100px; flex-shrink: 0; }
.history-item-name { flex: 1; color: #ececec; }
.history-price { color: #10a37f; font-weight: 600; white-space: nowrap; }

.loading-state, .empty-state { text-align: center; padding: 60px 0; color: #4a4a4a; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { background: #2f2f2f; border: 1px solid #3f3f3f; border-radius: 16px; width: 90%; max-width: 560px; max-height: 90vh; overflow-y: auto; }
.modal-title { font-size: 18px; font-weight: 600; color: #ececec; padding: 20px 24px 0; }
.modal-body { padding: 20px 24px; display: flex; flex-direction: column; gap: 12px; }
.modal-footer { padding: 0 24px 20px; display: flex; justify-content: flex-end; gap: 10px; }
.form-row { display: flex; flex-direction: column; gap: 5px; }
.form-row label { font-size: 13px; color: #9ca3af; font-weight: 500; }
.form-row input, .form-row textarea { background: #1e1e1e; border: 1px solid #3f3f3f; border-radius: 8px; padding: 10px 14px; color: #ececec; font-size: 14px; outline: none; transition: border-color 0.15s; font-family: inherit; }
.form-row input:focus, .form-row textarea:focus { border-color: #10a37f; }
.form-row input::placeholder, .form-row textarea::placeholder { color: #4a4a4a; }
.form-row textarea { resize: vertical; }
.cancel-btn { background: #2f2f2f; border: 1px solid #3f3f3f; color: #ececec; padding: 9px 20px; border-radius: 8px; cursor: pointer; font-size: 14px; }
.cancel-btn:hover { background: #383838; }
.submit-btn { background: #10a37f; border: none; color: white; padding: 9px 20px; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 500; }
.submit-btn:hover { background: #0d8c6d; }
</style>
