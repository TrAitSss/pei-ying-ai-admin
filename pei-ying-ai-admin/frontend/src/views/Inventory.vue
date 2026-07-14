<template>
  <div class="inventory-page">
    <div class="page-header">
      <h1 class="page-title">库存管理</h1>
      <p class="page-desc">查看库存状态，处理预警，记录盘点</p>
    </div>

    <div class="stats-row">
      <div class="mini-stat">
        <span class="mini-stat-value">{{ items.length }}</span>
        <span class="mini-stat-label">物品总数</span>
      </div>
      <div class="mini-stat warning">
        <span class="mini-stat-value">{{ lowStockItems.length }}</span>
        <span class="mini-stat-label">库存预警</span>
      </div>
      <div class="mini-stat">
        <button class="add-btn" @click="showDialog = true">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          新增物品
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">加载中...</div>

    <div v-else class="inventory-grid">
      <div
        v-for="item in sortedItems"
        :key="item.id"
        class="inv-card"
        :class="{ low: item.current_quantity <= item.min_quantity }"
      >
        <div class="inv-main">
          <div class="inv-info">
            <div class="inv-name-row">
              <h3 class="inv-name">{{ item.name }}</h3>
              <span class="inv-category">{{ item.category }}</span>
              <span v-if="item.current_quantity <= item.min_quantity" class="low-badge">库存不足</span>
            </div>
            <div class="inv-meta">
              <span>{{ item.location }}</span>
              <span>·</span>
              <span>单价 HK$ {{ item.unit_price || '-' }}</span>
            </div>
          </div>
          <div class="inv-quantity">
            <div class="qty-number" :class="{ danger: item.current_quantity <= item.min_quantity }">
              {{ item.current_quantity }} <span class="qty-unit">{{ item.unit }}</span>
            </div>
            <div class="qty-label">当前库存</div>
          </div>
        </div>

        <div class="inv-bar-section">
          <div class="bar-label">
            <span>库存量</span>
            <span>{{ item.current_quantity }} / {{ item.min_quantity }} (最低)</span>
          </div>
          <div class="bar-track">
            <div
              class="bar-fill"
              :class="{ low: item.current_quantity <= item.min_quantity }"
              :style="{ width: Math.min(100, (item.current_quantity / Math.max(1, item.min_quantity * 2)) * 100) + '%' }"
            ></div>
            <div v-if="item.min_quantity > 0" class="bar-min" :style="{ left: (item.min_quantity / Math.max(1, item.min_quantity * 2) * 100) + '%' }"></div>
          </div>
        </div>

        <div v-if="countingId === item.id" class="count-section">
          <div class="count-row">
            <label>实际数量</label>
            <input
              type="number"
              v-model.number="countForm.new_quantity"
              :min="0"
              class="count-input"
              @keyup.enter="submitCount(item)"
            />
            <button class="count-confirm" @click="submitCount(item)">确认盘点</button>
            <button class="count-cancel" @click="countingId = null">取消</button>
          </div>
          <input v-model="countForm.note" placeholder="备注（可选）" class="count-note" />
        </div>

        <div class="inv-actions">
          <button class="action-btn" @click="startCount(item)">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            盘点
          </button>
          <button class="action-btn danger" @click="deleteItem(item.id)">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
            删除
          </button>
        </div>
      </div>
    </div>

    <!-- 新增物品弹窗 -->
    <div v-if="showDialog" class="modal-overlay" @click.self="showDialog = false">
      <div class="modal">
        <h2 class="modal-title">新增物品</h2>
        <div class="modal-body">
          <div class="form-row"><label>名称 *</label><input v-model="form.name" placeholder="物品名称" /></div>
          <div class="form-row"><label>类别</label><input v-model="form.category" placeholder="例如：纸张、文具" /></div>
          <div class="form-row"><label>存放位置</label><input v-model="form.location" placeholder="存放位置" /></div>
          <div class="form-row-2col">
            <div class="form-row"><label>当前库存</label><input type="number" v-model.number="form.current_quantity" :min="0" /></div>
            <div class="form-row"><label>最低库存</label><input type="number" v-model.number="form.min_quantity" :min="0" /></div>
          </div>
          <div class="form-row-2col">
            <div class="form-row"><label>单位</label><input v-model="form.unit" placeholder="箱、包、个..." /></div>
            <div class="form-row"><label>单价 (HK$)</label><input type="number" v-model.number="form.unit_price" :min="0" step="0.01" /></div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="showDialog = false">取消</button>
          <button class="submit-btn" @click="saveItem">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '../api/axios'

const items = ref([])
const loading = ref(false)
const showDialog = ref(false)
const countingId = ref(null)
const countForm = reactive({ new_quantity: 0, note: '' })

const form = reactive({ name: '', category: '', location: '', current_quantity: 0, min_quantity: 0, unit: '', unit_price: null })

const lowStockItems = computed(() => items.value.filter(i => i.current_quantity <= i.min_quantity))
const sortedItems = computed(() => {
  return [...items.value].sort((a, b) => {
    const aLow = a.current_quantity <= a.min_quantity ? 0 : 1
    const bLow = b.current_quantity <= b.min_quantity ? 0 : 1
    return aLow - bLow
  })
})

onMounted(loadItems)

async function loadItems() {
  loading.value = true
  try {
    const res = await api.get('/inventory/items')
    items.value = res.data
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

function startCount(item) {
  countingId.value = item.id
  countForm.new_quantity = item.current_quantity
  countForm.note = ''
}

async function submitCount(item) {
  try {
    await api.post(`/inventory/items/${item.id}/count`, null, {
      params: { new_quantity: countForm.new_quantity, note: countForm.note }
    })
    countingId.value = null
    loadItems()
  } catch (e) { alert('盘点失败') }
}

async function saveItem() {
  if (!form.name) { alert('请填写物品名称'); return }
  try {
    await api.post('/inventory/items', form)
    showDialog.value = false
    Object.assign(form, { name: '', category: '', location: '', current_quantity: 0, min_quantity: 0, unit: '', unit_price: null })
    loadItems()
  } catch (e) { alert('保存失败') }
}

async function deleteItem(id) {
  if (!confirm('确定删除此物品？')) return
  try {
    await api.delete(`/inventory/items/${id}`)
    loadItems()
  } catch (e) { alert('删除失败') }
}
</script>

<style scoped>
.inventory-page { max-width: 900px; }
.page-header { margin-bottom: 28px; }
.page-title { font-size: 26px; font-weight: 600; color: #ececec; margin-bottom: 4px; }
.page-desc { font-size: 14px; color: #6b7280; }

.stats-row { display: flex; gap: 12px; margin-bottom: 24px; align-items: center; }
.mini-stat { background: #2f2f2f; border: 1px solid #3f3f3f; border-radius: 10px; padding: 14px 20px; display: flex; align-items: center; gap: 8px; }
.mini-stat.warning { border-color: rgba(239,68,68,0.3); }
.mini-stat-value { font-size: 22px; font-weight: 700; color: #ececec; }
.mini-stat.warning .mini-stat-value { color: #ef4444; }
.mini-stat-label { font-size: 13px; color: #6b7280; }
.add-btn { display: flex; align-items: center; gap: 5px; background: #10a37f; border: none; color: white; padding: 10px 18px; border-radius: 10px; cursor: pointer; font-size: 14px; font-weight: 500; }
.add-btn:hover { background: #0d8c6d; }

.inventory-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.inv-card { background: #2f2f2f; border: 1px solid #3f3f3f; border-radius: 12px; padding: 18px; transition: border-color 0.15s; }
.inv-card:hover { border-color: #4a4a4a; }
.inv-card.low { border-color: rgba(239,68,68,0.4); background: rgba(239,68,68,0.04); }

.inv-main { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 14px; }
.inv-name-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 6px; }
.inv-name { font-size: 15px; font-weight: 600; color: #ececec; }
.inv-category { background: rgba(107,114,128,0.2); color: #9ca3af; padding: 2px 8px; border-radius: 4px; font-size: 11px; }
.low-badge { background: rgba(239,68,68,0.15); color: #ef4444; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.inv-meta { font-size: 12px; color: #6b7280; display: flex; gap: 6px; }
.inv-quantity { text-align: right; }
.qty-number { font-size: 24px; font-weight: 700; color: #10a37f; line-height: 1.2; }
.qty-number.danger { color: #ef4444; }
.qty-unit { font-size: 14px; font-weight: 400; }
.qty-label { font-size: 11px; color: #6b7280; margin-top: 2px; }

.inv-bar-section { margin-bottom: 14px; }
.bar-label { display: flex; justify-content: space-between; font-size: 11px; color: #6b7280; margin-bottom: 5px; }
.bar-track { position: relative; height: 6px; background: #1e1e1e; border-radius: 3px; overflow: visible; }
.bar-fill { height: 100%; background: #10a37f; border-radius: 3px; transition: width 0.3s; }
.bar-fill.low { background: #ef4444; }
.bar-min { position: absolute; top: -3px; width: 2px; height: 12px; background: #f59e0b; border-radius: 1px; }

.count-section { background: #1e1e1e; border-radius: 8px; padding: 14px; margin-bottom: 12px; display: flex; flex-direction: column; gap: 8px; }
.count-row { display: flex; align-items: center; gap: 8px; }
.count-row label { font-size: 13px; color: #9ca3af; width: 70px; flex-shrink: 0; }
.count-input { background: #2f2f2f; border: 1px solid #3f3f3f; border-radius: 6px; padding: 6px 10px; color: #ececec; font-size: 14px; width: 80px; outline: none; }
.count-input:focus { border-color: #10a37f; }
.count-confirm { background: #10a37f; border: none; color: white; padding: 6px 14px; border-radius: 6px; cursor: pointer; font-size: 13px; }
.count-cancel { background: none; border: 1px solid #3f3f3f; color: #9ca3af; padding: 6px 14px; border-radius: 6px; cursor: pointer; font-size: 13px; }
.count-note { background: #2f2f2f; border: 1px solid #3f3f3f; border-radius: 6px; padding: 8px 10px; color: #ececec; font-size: 13px; outline: none; font-family: inherit; }
.count-note::placeholder { color: #4a4a4a; }

.inv-actions { display: flex; gap: 8px; }
.action-btn { display: flex; align-items: center; gap: 5px; background: none; border: 1px solid #3f3f3f; color: #9ca3af; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; transition: all 0.15s; }
.action-btn:hover { background: #383838; color: #ececec; border-color: #4a4a4a; }
.action-btn.danger:hover { color: #ef4444; border-color: rgba(239,68,68,0.3); }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { background: #2f2f2f; border: 1px solid #3f3f3f; border-radius: 16px; width: 90%; max-width: 560px; max-height: 90vh; overflow-y: auto; }
.modal-title { font-size: 18px; font-weight: 600; color: #ececec; padding: 20px 24px 0; }
.modal-body { padding: 20px 24px; display: flex; flex-direction: column; gap: 12px; }
.modal-footer { padding: 0 24px 20px; display: flex; justify-content: flex-end; gap: 10px; }
.form-row { display: flex; flex-direction: column; gap: 5px; }
.form-row label { font-size: 13px; color: #9ca3af; font-weight: 500; }
.form-row input, .form-row textarea { background: #1e1e1e; border: 1px solid #3f3f3f; border-radius: 8px; padding: 10px 14px; color: #ececec; font-size: 14px; outline: none; transition: border-color 0.15s; font-family: inherit; }
.form-row input:focus { border-color: #10a37f; }
.form-row input::placeholder { color: #4a4a4a; }
.form-row-2col { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.cancel-btn { background: #2f2f2f; border: 1px solid #3f3f3f; color: #ececec; padding: 9px 20px; border-radius: 8px; cursor: pointer; font-size: 14px; }
.cancel-btn:hover { background: #383838; }
.submit-btn { background: #10a37f; border: none; color: white; padding: 9px 20px; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 500; }
.submit-btn:hover { background: #0d8c6d; }

.loading-state { text-align: center; padding: 60px 0; color: #4a4a4a; }

@media (max-width: 768px) {
  .inventory-grid { grid-template-columns: 1fr; }
}
</style>
