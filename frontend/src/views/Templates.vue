<template>
  <div class="templates-page">
    <div class="page-header">
      <h1 class="page-title">文书生成</h1>
      <p class="page-desc">选择模板，填写内容，一键生成标书或报价单</p>
    </div>

    <div class="filter-bar">
      <div class="filter-tabs">
        <button class="filter-tab" :class="{ active: activeTab === 'templates' }" @click="activeTab = 'templates'">模板列表</button>
        <button class="filter-tab" :class="{ active: activeTab === 'documents' }" @click="activeTab = 'documents'; loadDocuments()">已生成文档</button>
      </div>
      <button v-if="activeTab === 'templates'" class="add-btn" @click="showDialog = true">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        新增模板
      </button>
    </div>

    <!-- 模板列表 -->
    <div v-if="activeTab === 'templates'">
      <div class="tpl-grid">
        <div v-for="tpl in filteredTemplates" :key="tpl.id" class="tpl-card" :class="{ expanded: expandedId === tpl.id }" @click="expandCard(tpl)">
          <div class="tpl-header">
            <div class="tpl-type-tag" :class="tpl.template_type">{{ typeLabel(tpl.template_type) }}</div>
            <h3 class="tpl-name">{{ tpl.name }}</h3>
            <p class="tpl-desc">{{ tpl.description }}</p>
          </div>
          <div v-if="expandedId === tpl.id" class="tpl-form-area" @click.stop>
            <div class="form-title">填写文档信息</div>
            <div class="gen-form">
              <div class="form-row">
                <label>文档标题</label>
                <input v-model="genForm.title" placeholder="例如：2026年音响设备采购标书" />
              </div>
              <div class="form-row" v-for="v in tpl.variables" :key="v.name">
                <label>{{ v.label || v.name }}{{ v.default ? '（默认: ' + v.default + '）' : '' }}</label>
                <input v-model="genForm.variables_data[v.name]" :placeholder="v.default || v.label || v.name" />
              </div>
              <div class="form-actions">
                <button class="cancel-btn" @click="expandedId = null">取消</button>
                <button class="submit-btn" @click="submitGenerate(tpl)" :disabled="generating">
                  {{ generating ? '生成中...' : '生成文档' }}
                </button>
              </div>
            </div>
          </div>
          <div v-else class="tpl-action">
            <button class="use-btn">使用此模板 →</button>
          </div>
        </div>
      </div>
      <div v-if="filteredTemplates.length === 0 && !loading" class="empty-state"><p>没有找到模板</p></div>
    </div>

    <!-- 已生成文档 -->
    <div v-if="activeTab === 'documents'">
      <div v-if="documents.length === 0" class="empty-state"><p>还没有生成过文档</p></div>
      <div v-else class="doc-grid">
        <div v-for="doc in documents" :key="doc.id" class="doc-card">
          <div class="doc-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#10a37f" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
          </div>
          <div class="doc-info">
            <div class="doc-title">{{ doc.title }}</div>
            <div class="doc-date">{{ formatDate(doc.created_at) }}</div>
          </div>
          <button class="download-btn" @click="downloadDoc(doc)">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            下载
          </button>
        </div>
      </div>
    </div>

    <!-- 新增模板弹窗 -->
    <div v-if="showDialog" class="modal-overlay" @click.self="showDialog = false">
      <div class="modal">
        <h2 class="modal-title">新增模板</h2>
        <div class="modal-body">
          <div class="form-row"><label>名称</label><input v-model="form.name" placeholder="模板名称" /></div>
          <div class="form-row"><label>类型</label><select v-model="form.template_type"><option value="tender">标书</option><option value="quotation">报价单</option></select></div>
          <div class="form-row"><label>描述</label><textarea v-model="form.description" rows="2" placeholder="模板用途说明"></textarea></div>
          <div class="form-row"><label>模板内容</label><textarea v-model="form.content" rows="8" placeholder="使用 {{ 变量名 }} 语法"></textarea></div>
        </div>
        <div class="modal-footer"><button class="cancel-btn" @click="showDialog = false">取消</button><button class="submit-btn" @click="saveTemplate">保存模板</button></div>
      </div>
    </div>

    <!-- 生成成功提示 -->
    <div v-if="successDoc" class="modal-overlay" @click.self="successDoc = null">
      <div class="modal" style="max-width:420px;text-align:center;">
        <div style="padding:32px 24px 24px;">
          <div style="width:56px;height:56px;background:rgba(16,163,127,0.12);border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 16px;">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#10a37f" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
          </div>
          <h2 style="font-size:18px;font-weight:600;color:#ececec;margin-bottom:8px;">文档生成成功</h2>
          <p style="font-size:14px;color:#9ca3af;margin-bottom:20px;">{{ successDoc.title }}.docx 已准备好</p>
          <div style="display:flex;gap:10px;justify-content:center;">
            <button class="cancel-btn" @click="successDoc = null">关闭</button>
            <button class="submit-btn" @click="downloadDoc(successDoc)">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              下载文档
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '../api/axios'

const templates = ref([])
const documents = ref([])
const loading = ref(false)
const generating = ref(false)
const showDialog = ref(false)
const expandedId = ref(null)
const filterType = ref('')
const activeTab = ref('templates')
const successDoc = ref(null)

const form = reactive({ name: '', template_type: 'tender', description: '', content: '' })
const genForm = reactive({ title: '', variables_data: {} })

const filteredTemplates = computed(() => {
  if (!filterType.value) return templates.value
  return templates.value.filter(t => t.template_type === filterType.value)
})

onMounted(loadTemplates)

async function loadTemplates() {
  loading.value = true
  try { const res = await api.get('/templates'); templates.value = res.data } catch (e) { console.error(e) } finally { loading.value = false }
}

async function loadDocuments() {
  try { const res = await api.get('/templates/documents/list'); documents.value = res.data } catch (e) { console.error(e) }
}

function typeLabel(t) { return { tender: '标书', quotation: '报价单' }[t] || t }

function formatDate(s) {
  if (!s) return ''
  const d = new Date(s)
  return `${d.getMonth()+1}/${d.getDate()} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}

function expandCard(tpl) {
  if (expandedId.value === tpl.id) { expandedId.value = null; return }
  expandedId.value = tpl.id
  genForm.title = ''
  genForm.variables_data = {}
  if (tpl.variables) { tpl.variables.forEach(v => { genForm.variables_data[v.name] = v.default || '' }) }
}

async function submitGenerate(tpl) {
  if (!genForm.title) { alert('请填写文档标题'); return }
  generating.value = true
  try {
    const res = await api.post(`/templates/${tpl.id}/generate`, {
      template_id: tpl.id, title: genForm.title, variables_data: genForm.variables_data
    })
    successDoc.value = res.data
    expandedId.value = null
  } catch (e) {
    alert('生成失败: ' + (e.response?.data?.detail || '未知错误'))
  } finally { generating.value = false }
}

async function downloadDoc(doc) {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(doc.download_url, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('下载失败')
    const blob = await res.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${doc.title}.docx`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch (e) {
    alert('下载失败: ' + e.message)
  }
}

async function saveTemplate() {
  if (!form.name) { alert('请填写模板名称'); return }
  try { await api.post('/templates', form); showDialog.value = false; form.name=''; form.description=''; form.content=''; loadTemplates() } catch (e) { alert('保存失败') }
}
</script>

<style scoped>
.templates-page { max-width: 900px; }
.page-header { margin-bottom: 28px; }
.page-title { font-size: 26px; font-weight: 600; color: #ececec; margin-bottom: 4px; }
.page-desc { font-size: 14px; color: #6b7280; }
.filter-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.filter-tabs { display: flex; gap: 6px; }
.filter-tab { background: #2f2f2f; border: 1px solid #3f3f3f; color: #9ca3af; padding: 7px 16px; border-radius: 8px; cursor: pointer; font-size: 13px; transition: all 0.15s; }
.filter-tab.active { background: #10a37f; color: white; border-color: #10a37f; }
.filter-tab:hover:not(.active) { background: #383838; color: #ececec; }
.add-btn { display: flex; align-items: center; gap: 6px; background: none; border: 1px solid #3f3f3f; color: #ececec; padding: 7px 16px; border-radius: 8px; cursor: pointer; font-size: 13px; transition: all 0.15s; }
.add-btn:hover { border-color: #10a37f; color: #10a37f; }
.tpl-grid { display: flex; flex-direction: column; gap: 12px; }
.tpl-card { background: #2f2f2f; border: 1px solid #3f3f3f; border-radius: 12px; cursor: pointer; transition: border-color 0.15s; overflow: hidden; }
.tpl-card:hover { border-color: #4a4a4a; }
.tpl-card.expanded { border-color: #10a37f; cursor: default; }
.tpl-header { padding: 20px; }
.tpl-type-tag { display: inline-block; padding: 2px 10px; border-radius: 6px; font-size: 12px; font-weight: 500; margin-bottom: 10px; }
.tpl-type-tag.tender { background: rgba(59,130,246,0.15); color: #3b82f6; }
.tpl-type-tag.quotation { background: rgba(16,163,127,0.15); color: #10a37f; }
.tpl-name { font-size: 17px; font-weight: 600; color: #ececec; margin-bottom: 6px; }
.tpl-desc { font-size: 13px; color: #6b7280; line-height: 1.5; }
.tpl-action { padding: 0 20px 16px; }
.use-btn { background: none; border: none; color: #10a37f; font-size: 14px; font-weight: 500; cursor: pointer; padding: 0; }
.use-btn:hover { text-decoration: underline; }
.tpl-form-area { border-top: 1px solid #3f3f3f; padding: 20px; background: #262626; }
.form-title { font-size: 14px; font-weight: 600; color: #ececec; margin-bottom: 16px; }
.gen-form { display: flex; flex-direction: column; gap: 12px; }
.form-row { display: flex; flex-direction: column; gap: 5px; }
.form-row label { font-size: 13px; color: #9ca3af; font-weight: 500; }
.form-row input, .form-row textarea, .form-row select { background: #1e1e1e; border: 1px solid #3f3f3f; border-radius: 8px; padding: 10px 14px; color: #ececec; font-size: 14px; outline: none; transition: border-color 0.15s; font-family: inherit; }
.form-row input:focus, .form-row textarea:focus, .form-row select:focus { border-color: #10a37f; }
.form-row input::placeholder, .form-row textarea::placeholder { color: #4a4a4a; }
.form-row textarea { resize: vertical; }
.form-row select { cursor: pointer; }
.form-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 8px; }
.cancel-btn { background: #2f2f2f; border: 1px solid #3f3f3f; color: #ececec; padding: 9px 20px; border-radius: 8px; cursor: pointer; font-size: 14px; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; }
.cancel-btn:hover { background: #383838; }
.submit-btn { background: #10a37f; border: none; color: white; padding: 9px 20px; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 500; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; }
.submit-btn:hover { background: #0d8c6d; }
.submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.doc-grid { display: flex; flex-direction: column; gap: 8px; }
.doc-card { display: flex; align-items: center; gap: 14px; background: #2f2f2f; border: 1px solid #3f3f3f; border-radius: 12px; padding: 16px 20px; }
.doc-card:hover { border-color: #4a4a4a; }
.doc-icon { width: 44px; height: 44px; background: rgba(16,163,127,0.12); border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.doc-info { flex: 1; }
.doc-title { font-size: 15px; font-weight: 500; color: #ececec; }
.doc-date { font-size: 12px; color: #6b7280; margin-top: 2px; }
.download-btn { display: flex; align-items: center; gap: 6px; background: rgba(16,163,127,0.12); color: #10a37f; padding: 8px 16px; border-radius: 8px; font-size: 13px; font-weight: 500; border: none; cursor: pointer; transition: all 0.15s; flex-shrink: 0; }
.download-btn:hover { background: rgba(16,163,127,0.2); }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { background: #2f2f2f; border: 1px solid #3f3f3f; border-radius: 16px; width: 90%; max-width: 600px; max-height: 90vh; overflow-y: auto; }
.modal-title { font-size: 18px; font-weight: 600; color: #ececec; padding: 20px 24px 0; }
.modal-body { padding: 20px 24px; display: flex; flex-direction: column; gap: 12px; }
.modal-footer { padding: 0 24px 20px; display: flex; justify-content: flex-end; gap: 10px; }
.empty-state { text-align: center; padding: 60px 0; color: #4a4a4a; }
</style>