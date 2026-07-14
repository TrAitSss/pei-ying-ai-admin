<template>
  <div class="templates-page">
    <div class="page-header">
      <h1 class="page-title">文书生成</h1>
      <p class="page-desc">选择模板、填写内容、一键生成标书或报价单</p>
    </div>

    <!-- ========== Tab 切换 ========== -->
    <div class="tab-bar">
      <button class="tab-btn" :class="{ active: activeTab === 'templates' }" @click="switchTab('templates')">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        模板列表
      </button>
      <button class="tab-btn" :class="{ active: activeTab === 'documents' }" @click="switchTab('documents')">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="9" y1="15" x2="15" y2="15"/></svg>
        已生成文档 <span v-if="docCount" class="tab-badge">{{ docCount }}</span>
      </button>
      <button class="tab-btn" :class="{ active: activeTab === 'upload' }" @click="switchTab('upload')">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
        上传模板
      </button>
    </div>

    <!-- ========== 模板列表 ========== -->
    <div v-if="activeTab === 'templates'">
      <div class="filter-bar">
        <div class="filter-tabs">
          <button class="filter-tab" :class="{ active: filterType === '' }" @click="filterType = ''">全部</button>
          <button class="filter-tab" :class="{ active: filterType === 'tender' }" @click="filterType = 'tender'">标书</button>
          <button class="filter-tab" :class="{ active: filterType === 'quotation' }" @click="filterType = 'quotation'">报价单</button>
        </div>
        <button class="add-btn" @click="openEditor()">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          新增模板
        </button>
      </div>

      <div class="tpl-grid">
        <div v-for="tpl in filteredTemplates" :key="tpl.id" class="tpl-card" :class="{ expanded: expandedId === tpl.id }">
          <div class="tpl-card-top" @click="expandCard(tpl)">
            <div class="tpl-card-left">
              <div class="tpl-type-tag" :class="tpl.template_type">{{ typeLabel(tpl.template_type) }}</div>
              <h3 class="tpl-name">{{ tpl.name }}</h3>
              <p class="tpl-desc">{{ tpl.description || '暂无描述' }}</p>
              <div v-if="tpl.variables && tpl.variables.length" class="tpl-vars">
                <span class="var-chip" v-for="v in tpl.variables.slice(0, 5)" :key="v.name">{{ br(v.name) }}</span>
                <span v-if="tpl.variables.length > 5" class="var-more">+{{ tpl.variables.length - 5 }}</span>
              </div>
            </div>
            <div class="tpl-card-actions" @click.stop>
              <button class="icon-btn edit" title="编辑模板" @click="openEditor(tpl)">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
              </button>
              <button class="icon-btn del" title="删除模板" @click="confirmDeleteTemplate(tpl)">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
              </button>
            </div>
          </div>

          <div v-if="expandedId === tpl.id" class="tpl-form-area">
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

      <div v-if="filteredTemplates.length === 0 && !loading" class="empty-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        <p>暂无模板，点击右上角创建</p>
      </div>
    </div>

    <!-- ========== 已生成文档 ========== -->
    <div v-if="activeTab === 'documents'">
      <div class="doc-list" v-if="documents.length > 0">
        <div v-for="doc in documents" :key="doc.id" class="doc-card">
          <div class="doc-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          </div>
          <div class="doc-info">
            <h4 class="doc-title">{{ doc.title }}</h4>
            <p class="doc-meta">{{ formatDate(doc.created_at) }} · 状态: {{ statusLabel(doc.status) }}</p>
          </div>
          <div class="doc-actions">
            <button class="doc-btn download" @click="downloadDoc(doc)">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              下载
            </button>
            <button class="doc-btn del" @click="confirmDeleteDoc(doc)">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
            </button>
          </div>
        </div>
      </div>
      <div v-else class="empty-state">
        <p>暂无已生成的文档</p>
      </div>
    </div>

    <!-- ========== 上传模板 ========== -->
    <div v-if="activeTab === 'upload'">
      <div class="upload-area" @click="triggerFileInput" @dragover.prevent="dragOver = true" @dragleave="dragOver = false" @drop.prevent="handleDrop" :class="{ dragging: dragOver, hasFile: uploadFile }">
        <input type="file" ref="fileInput" accept=".docx" style="display:none" @change="handleFileSelect" />
        <div v-if="!uploadFile" class="upload-prompt">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
          <p class="upload-text">点击或拖拽 .docx 文件到此处</p>
          <p class="upload-hint">系统会自动识别文件中的 {{ br('变量名') }} 占位符</p>
        </div>
        <div v-else class="upload-file-info">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#10a37f" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
          <span class="upload-filename">{{ uploadFile.name }}</span>
          <button class="upload-remove" @click.stop="uploadFile = null">移除</button>
        </div>
      </div>

      <div v-if="uploadFile" class="upload-form">
        <div class="form-row"><label>模板名称</label><input v-model="uploadForm.name" placeholder="给模板起个名字" /></div>
        <div class="form-row">
          <label>类型</label>
          <select v-model="uploadForm.template_type">
            <option value="tender">标书</option>
            <option value="quotation">报价单</option>
          </select>
        </div>
        <div class="form-row"><label>描述（可选）</label><textarea v-model="uploadForm.description" rows="2" placeholder="模板用途说明"></textarea></div>
        <button class="submit-btn full" @click="uploadTemplate" :disabled="uploading">
          {{ uploading ? '上传中...' : '上传并创建模板' }}
        </button>
      </div>

      <div class="upload-tips">
        <h4>上传说明</h4>
        <p>1. 在你的 Word 文档中，用 <code>{{ br('变量名') }}</code> 标记需要替换的内容</p>
        <p>2. 例如：<code>{{ br('project_name') }}</code> 会在生成时替换为实际项目名称</p>
        <p>3. 上传后系统会自动识别所有变量，你可以直接使用该模板生成文档</p>
      </div>
    </div>

    <!-- ========== 可视化编辑器弹窗 ========== -->
    <div v-if="showEditor" class="editor-overlay" @click.self="closeEditor">
      <div class="editor-modal">
        <div class="editor-header">
          <h2>{{ editingId ? '编辑模板' : '新增模板' }}</h2>
          <button class="close-btn" @click="closeEditor">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>

        <div class="editor-meta">
          <div class="meta-row">
            <input v-model="editorForm.name" placeholder="模板名称" class="meta-input" />
            <select v-model="editorForm.template_type" class="meta-select">
              <option value="tender">标书</option>
              <option value="quotation">报价单</option>
            </select>
          </div>
          <input v-model="editorForm.description" placeholder="模板描述（可选）" class="meta-input" />
        </div>

        <!-- 格式工具栏 -->
        <div class="toolbar">
          <button class="tool-btn" title="一级标题" @click="insertAtCursor('# ')"><strong>H1</strong></button>
          <button class="tool-btn" title="二级标题" @click="insertAtCursor('## ')"><strong>H2</strong></button>
          <button class="tool-btn" title="三级标题" @click="insertAtCursor('### ')"><strong>H3</strong></button>
          <span class="tool-divider"></span>
          <button class="tool-btn" title="粗体" @click="wrapSelection('**', '**')"><strong>B</strong></button>
          <button class="tool-btn" title="斜体" @click="wrapSelection('*', '*')" style="font-style:italic">I</button>
          <span class="tool-divider"></span>
          <button class="tool-btn" title="无序列表" @click="insertAtCursor('- ')">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
          </button>
          <button class="tool-btn" title="有序列表" @click="insertAtCursor('1. ')">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="10" y1="6" x2="21" y2="6"/><line x1="10" y1="12" x2="21" y2="12"/><line x1="10" y1="18" x2="21" y2="18"/><path d="M4 6h1v4M4 10h2M6 18H4c0-1 2-2 2-3s-1-1.5-2-1"/></svg>
          </button>
          <button class="tool-btn" title="表格" @click="insertTable()">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/></svg>
          </button>
          <button class="tool-btn" title="分割线" @click="insertAtCursor('\n---\n')">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"/></svg>
          </button>
          <span class="tool-divider"></span>
          <button class="tool-btn var-btn" title="插入变量" @click="insertVariable()">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
            变量
          </button>
        </div>

        <!-- 编辑器 + 预览 -->
        <div class="editor-body">
          <div class="editor-pane">
            <div class="pane-label">模板内容</div>
            <textarea ref="editorTextarea" v-model="editorForm.content" class="editor-textarea"
              placeholder="在此编写模板内容...

使用 {{ 变量名 }} 插入动态内容
格式说明：
# 一级标题
## 二级标题
### 三级标题
**粗体文字**
*斜体文字*
- 无序列表项
1. 有序列表项
| 列1 | 列2 | 列3 |
| 行1 | 行1 | 行1 |
---
（分割线）"
              @input="updatePreview"></textarea>
          </div>

          <div class="preview-pane">
            <div class="pane-label">实时预览</div>
            <div class="preview-content" v-html="previewHtml"></div>
          </div>
        </div>

        <!-- 变量管理 -->
        <div v-if="extractedVars.length > 0" class="var-manager">
          <span class="var-manager-label">检测到的变量：</span>
          <div class="var-list">
            <span class="var-item" v-for="v in extractedVars" :key="v">
              {{ br(v) }}
            </span>
          </div>
        </div>

        <div class="editor-footer">
          <button class="cancel-btn" @click="closeEditor">取消</button>
          <button class="submit-btn" @click="saveTemplate" :disabled="saving">
            {{ saving ? '保存中...' : '保存模板' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ========== 确认删除弹窗 ========== -->
    <div v-if="deleteTarget" class="confirm-overlay" @click.self="deleteTarget = null">
      <div class="confirm-modal">
        <div class="confirm-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        </div>
        <h3 class="confirm-title">确认删除？</h3>
        <p class="confirm-text">{{ deleteTarget.type === 'template' ? '删除模板后无法恢复，确定删除吗？' : '删除文档后无法恢复，确定删除吗？' }}</p>
        <p class="confirm-name">{{ deleteTarget.name }}</p>
        <div class="confirm-actions">
          <button class="cancel-btn" @click="deleteTarget = null">取消</button>
          <button class="danger-btn" @click="executeDelete">确认删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import api from '../api/axios'

// ========== 状态 ==========
const activeTab = ref('templates')
const templates = ref([])
const documents = ref([])
const loading = ref(false)
const generating = ref(false)
const saving = ref(false)
const uploading = ref(false)
const dragOver = ref(false)

const expandedId = ref(null)
const filterType = ref('')

// 生成表单
const genForm = reactive({ title: '', variables_data: {} })

// 上传
const uploadFile = ref(null)
const uploadForm = reactive({ name: '', template_type: 'tender', description: '' })
const fileInput = ref(null)

// 编辑器
const showEditor = ref(false)
const editingId = ref(null)
const editorForm = reactive({ name: '', template_type: 'tender', description: '', content: '' })
const editorTextarea = ref(null)
const previewHtml = ref('')

// 删除确认
const deleteTarget = ref(null)

// ========== 计算属性 ==========
const filteredTemplates = computed(() => {
  if (!filterType.value) return templates.value
  return templates.value.filter(t => t.template_type === filterType.value)
})

const docCount = computed(() => documents.value.length)

const extractedVars = computed(() => {
  const content = editorForm.content || ''
  const matches = content.match(/\{\{\s*(\w+)\s*\}\}/g) || []
  const names = [...new Set(matches.map(m => m.replace(/\{\{\s*|\s*\}\}/g, '').trim()))]
  return names
})

// ========== 生命周期 ==========
onMounted(() => {
  loadTemplates()
  loadDocuments()
})

// ========== 方法 ==========
function switchTab(tab) {
  activeTab.value = tab
  if (tab === 'documents') loadDocuments()
  if (tab === 'templates') loadTemplates()
}

async function loadTemplates() {
  loading.value = true
  try {
    const res = await api.get('/templates')
    templates.value = res.data
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

async function loadDocuments() {
  try {
    const res = await api.get('/templates/documents/list')
    documents.value = res.data
  } catch (e) { console.error(e) }
}

function typeLabel(t) {
  return { tender: '标书', quotation: '报价单' }[t] || t
}

function br(text) {
  return '{{ ' + text + ' }}'
}

function statusLabel(s) {
  return { draft: '草稿', pending_approval: '待审批', approved: '已通过', rejected: '已驳回' }[s] || s
}

function formatDate(d) {
  if (!d) return '-'
  const date = new Date(d)
  return date.toLocaleDateString('zh-CN') + ' ' + date.toTimeString().slice(0, 5)
}

// ========== 模板操作 ==========
function expandCard(tpl) {
  if (expandedId.value === tpl.id) {
    expandedId.value = null
    return
  }
  expandedId.value = tpl.id
  genForm.title = ''
  genForm.variables_data = {}
  if (tpl.variables) {
    tpl.variables.forEach(v => {
      genForm.variables_data[v.name] = v.default || ''
    })
  }
}

async function submitGenerate(tpl) {
  if (!genForm.title) { alert('请填写文档标题'); return }
  generating.value = true
  try {
    await api.post(`/templates/${tpl.id}/generate`, {
      template_id: tpl.id,
      title: genForm.title,
      variables_data: genForm.variables_data
    })
    alert('文档生成成功！可在「已生成文档」中下载')
    expandedId.value = null
    loadDocuments()
  } catch (e) {
    alert('生成失败: ' + (e.response?.data?.detail || '未知错误'))
  } finally {
    generating.value = false
  }
}

// ========== 删除 ==========
function confirmDeleteTemplate(tpl) {
  deleteTarget.value = { type: 'template', id: tpl.id, name: tpl.name }
}

function confirmDeleteDoc(doc) {
  deleteTarget.value = { type: 'document', id: doc.id, name: doc.title }
}

async function executeDelete() {
  if (!deleteTarget.value) return
  const target = deleteTarget.value
  deleteTarget.value = null
  try {
    if (target.type === 'template') {
      await api.delete(`/templates/${target.id}`)
      loadTemplates()
    } else {
      await api.delete(`/templates/documents/${target.id}`)
      loadDocuments()
    }
  } catch (e) {
    alert('删除失败: ' + (e.response?.data?.detail || '未知错误'))
  }
}

// ========== 下载 ==========
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

// ========== 上传 ==========
function triggerFileInput() {
  if (!uploadFile.value) fileInput.value?.click()
}

function handleFileSelect(e) {
  const file = e.target.files[0]
  if (file && file.name.endsWith('.docx')) {
    uploadFile.value = file
    if (!uploadForm.name) uploadForm.name = file.name.replace('.docx', '')
  } else {
    alert('请选择 .docx 格式文件')
  }
  e.target.value = ''
}

function handleDrop(e) {
  dragOver.value = false
  const file = e.dataTransfer.files[0]
  if (file && file.name.endsWith('.docx')) {
    uploadFile.value = file
    if (!uploadForm.name) uploadForm.name = file.name.replace('.docx', '')
  } else {
    alert('请选择 .docx 格式文件')
  }
}

async function uploadTemplate() {
  if (!uploadFile.value) { alert('请先选择文件'); return }
  if (!uploadForm.name) { alert('请填写模板名称'); return }
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', uploadFile.value)
    formData.append('name', uploadForm.name)
    formData.append('template_type', uploadForm.template_type)
    formData.append('description', uploadForm.description)
    await api.post('/templates/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    alert('模板上传成功！已自动识别变量')
    uploadFile.value = null
    uploadForm.name = ''
    uploadForm.description = ''
    uploadForm.template_type = 'tender'
    loadTemplates()
    activeTab.value = 'templates'
  } catch (e) {
    alert('上传失败: ' + (e.response?.data?.detail || '未知错误'))
  } finally {
    uploading.value = false
  }
}

// ========== 可视化编辑器 ==========
function openEditor(tpl = null) {
  if (tpl) {
    editingId.value = tpl.id
    editorForm.name = tpl.name
    editorForm.template_type = tpl.template_type
    editorForm.description = tpl.description || ''
    editorForm.content = tpl.content || ''
  } else {
    editingId.value = null
    editorForm.name = ''
    editorForm.template_type = 'tender'
    editorForm.description = ''
    editorForm.content = ''
  }
  showEditor.value = true
  nextTick(() => {
    updatePreview()
  })
}

function closeEditor() {
  showEditor.value = false
  editingId.value = null
}

async function saveTemplate() {
  if (!editorForm.name) { alert('请填写模板名称'); return }
  if (!editorForm.content) { alert('请填写模板内容'); return }
  saving.value = true
  try {
    const payload = {
      name: editorForm.name,
      template_type: editorForm.template_type,
      description: editorForm.description,
      content: editorForm.content,
      variables: extractedVars.value.map(v => ({ name: v, label: v, default: '' }))
    }
    if (editingId.value) {
      await api.put(`/templates/${editingId.value}`, payload)
    } else {
      await api.post('/templates', payload)
    }
    alert('模板保存成功！')
    closeEditor()
    loadTemplates()
  } catch (e) {
    alert('保存失败: ' + (e.response?.data?.detail || '未知错误'))
  } finally {
    saving.value = false
  }
}

// ========== 工具栏操作 ==========
function insertAtCursor(text) {
  const ta = editorTextarea.value
  if (!ta) {
    editorForm.content += text
    updatePreview()
    return
  }
  const start = ta.selectionStart
  const end = ta.selectionEnd
  editorForm.content = editorForm.content.substring(0, start) + text + editorForm.content.substring(end)
  nextTick(() => {
    ta.focus()
    ta.selectionStart = ta.selectionEnd = start + text.length
    updatePreview()
  })
}

function wrapSelection(before, after) {
  const ta = editorTextarea.value
  if (!ta) return
  const start = ta.selectionStart
  const end = ta.selectionEnd
  const selected = editorForm.content.substring(start, end)
  const newText = before + (selected || '文字') + after
  editorForm.content = editorForm.content.substring(0, start) + newText + editorForm.content.substring(end)
  nextTick(() => {
    ta.focus()
    ta.selectionStart = start + before.length
    ta.selectionEnd = start + before.length + (selected || '文字').length
    updatePreview()
  })
}

function insertTable() {
  const table = '\n| 列标题1 | 列标题2 | 列标题3 |\n| 内容1 | 内容2 | 内容3 |\n| 内容4 | 内容5 | 内容6 |\n'
  insertAtCursor(table)
}

function insertVariable() {
  const name = prompt('请输入变量名称（英文、数字、下划线）:', 'project_name')
  if (name && /^\w+$/.test(name)) {
    insertAtCursor(`{{ ${name} }}`)
  } else if (name) {
    alert('变量名只能包含字母、数字和下划线')
  }
}

// ========== 实时预览 ==========
function updatePreview() {
  const content = editorForm.content || ''
  if (!content.trim()) {
    previewHtml.value = '<p class="preview-empty">在左侧输入内容后，这里会实时显示预览效果</p>'
    return
  }

  // 用占位值替换 {{ variable }}
  let rendered = content
  const varMatches = content.match(/\{\{\s*(\w+)\s*\}\}/g) || []
  const varNames = [...new Set(varMatches.map(m => m.replace(/\{\{\s*|\s*\}\}/g, '').trim()))]
  varNames.forEach(v => {
    rendered = rendered.replace(new RegExp(`\\{\\{\\s*${v}\\s*\\}\\}`, 'g'), `<span class="preview-var">${v}</span>`)
  })

  // 转 HTML
  const lines = rendered.split('\n')
  let html = ''
  let inTable = false
  let tableRows = []

  for (let line of lines) {
    const trimmed = line.trim()

    if (!trimmed) {
      if (inTable) { html += _renderTable(tableRows); tableRows = []; inTable = false }
      continue
    }

    if (trimmed === '---' || trimmed === '***' || trimmed === '___') {
      if (inTable) { html += _renderTable(tableRows); tableRows = []; inTable = false }
      html += '<hr/>'
      continue
    }

    // 表格行
    if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
      if (trimmed.match(/^\|[\s\-:|]+$/)) continue // 跳过分隔行
      inTable = true
      tableRows.push(trimmed)
      continue
    }

    if (inTable) { html += _renderTable(tableRows); tableRows = []; inTable = false }

    // 标题
    if (trimmed.startsWith('### ')) {
      html += `<h3>${_renderInline(trimmed.slice(4).trim())}</h3>`
    } else if (trimmed.startsWith('## ')) {
      html += `<h3>${_renderInline(trimmed.slice(3).trim())}</h3>`
    } else if (trimmed.startsWith('# ')) {
      html += `<h2>${_renderInline(trimmed.slice(2).trim())}</h2>`
    } else if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
      html += `<div class="preview-li">${_renderInline(trimmed.slice(2).trim())}</div>`
    } else if (/^\d+[\.\)]\s/.test(trimmed)) {
      html += `<div class="preview-li num">${_renderInline(trimmed.replace(/^\d+[\.\)]\s/, ''))}</div>`
    } else {
      html += `<p>${_renderInline(trimmed)}</p>`
    }
  }

  if (inTable) html += _renderTable(tableRows)

  previewHtml.value = html
}

function _renderTable(rows) {
  if (!rows.length) return ''
  let html = '<table class="preview-table"><tbody>'
  for (let row of rows) {
    const cells = row.replace(/^\||\|$/g, '').split('|').map(c => c.trim())
    html += '<tr>' + cells.map(c => `<td>${_renderInline(c)}</td>`).join('') + '</tr>'
  }
  html += '</tbody></table>'
  return html
}

function _renderInline(text) {
  // 粗体
  text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  // 斜体
  text = text.replace(/\*(.+?)\*/g, '<em>$1</em>')
  return text
}
</script>

<style scoped>
.templates-page { max-width: 1000px; }
.page-header { margin-bottom: 24px; }
.page-title { font-size: 26px; font-weight: 600; color: #ececec; margin-bottom: 4px; }
.page-desc { font-size: 14px; color: #6b7280; }

/* Tab */
.tab-bar { display: flex; gap: 4px; margin-bottom: 24px; border-bottom: 1px solid #3f3f3f; padding-bottom: 0; }
.tab-btn { display: flex; align-items: center; gap: 6px; background: none; border: none; border-bottom: 2px solid transparent; color: #9ca3af; padding: 10px 18px; cursor: pointer; font-size: 14px; font-weight: 500; transition: all 0.15s; margin-bottom: -1px; }
.tab-btn:hover { color: #ececec; }
.tab-btn.active { color: #10a37f; border-bottom-color: #10a37f; }
.tab-badge { background: #10a37f; color: white; font-size: 11px; padding: 1px 6px; border-radius: 10px; margin-left: 2px; }

/* Filter */
.filter-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.filter-tabs { display: flex; gap: 6px; }
.filter-tab { background: #2f2f2f; border: 1px solid #3f3f3f; color: #9ca3af; padding: 7px 16px; border-radius: 8px; cursor: pointer; font-size: 13px; transition: all 0.15s; }
.filter-tab.active { background: #10a37f; color: white; border-color: #10a37f; }
.filter-tab:hover:not(.active) { background: #383838; color: #ececec; }
.add-btn { display: flex; align-items: center; gap: 6px; background: none; border: 1px solid #3f3f3f; color: #ececec; padding: 7px 16px; border-radius: 8px; cursor: pointer; font-size: 13px; transition: all 0.15s; }
.add-btn:hover { border-color: #10a37f; color: #10a37f; }

/* Template cards */
.tpl-grid { display: flex; flex-direction: column; gap: 12px; }
.tpl-card { background: #2f2f2f; border: 1px solid #3f3f3f; border-radius: 12px; transition: border-color 0.15s; overflow: hidden; }
.tpl-card:hover { border-color: #4a4a4a; }
.tpl-card.expanded { border-color: #10a37f; }

.tpl-card-top { display: flex; justify-content: space-between; align-items: flex-start; padding: 18px 20px; cursor: pointer; }
.tpl-card-left { flex: 1; }
.tpl-type-tag { display: inline-block; padding: 2px 10px; border-radius: 6px; font-size: 12px; font-weight: 500; margin-bottom: 8px; }
.tpl-type-tag.tender { background: rgba(59,130,246,0.15); color: #3b82f6; }
.tpl-type-tag.quotation { background: rgba(16,163,127,0.15); color: #10a37f; }
.tpl-name { font-size: 17px; font-weight: 600; color: #ececec; margin-bottom: 4px; }
.tpl-desc { font-size: 13px; color: #6b7280; line-height: 1.5; margin-bottom: 8px; }
.tpl-vars { display: flex; flex-wrap: wrap; gap: 4px; }
.var-chip { background: #1e1e1e; border: 1px solid #3f3f3f; color: #10a37f; font-size: 11px; padding: 2px 8px; border-radius: 6px; font-family: 'SF Mono', monospace; }
.var-more { font-size: 11px; color: #6b7280; padding: 2px 6px; }

.tpl-card-actions { display: flex; gap: 4px; flex-shrink: 0; }
.icon-btn { width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; background: none; border: 1px solid #3f3f3f; border-radius: 8px; color: #9ca3af; cursor: pointer; transition: all 0.15s; }
.icon-btn:hover { background: #383838; }
.icon-btn.del:hover { color: #ef4444; border-color: #ef4444; }
.icon-btn.edit:hover { color: #10a37f; border-color: #10a37f; }

.tpl-action { padding: 0 20px 14px; }
.use-btn { background: none; border: none; color: #10a37f; font-size: 14px; font-weight: 500; cursor: pointer; padding: 0; }
.use-btn:hover { text-decoration: underline; }

.tpl-form-area { border-top: 1px solid #3f3f3f; padding: 20px; background: #262626; }
.form-title { font-size: 14px; font-weight: 600; color: #ececec; margin-bottom: 16px; }
.gen-form { display: flex; flex-direction: column; gap: 12px; }
.form-row { display: flex; flex-direction: column; gap: 5px; }
.form-row label { font-size: 13px; color: #9ca3af; font-weight: 500; }
.form-row input, .form-row textarea, .form-row select {
  background: #1e1e1e; border: 1px solid #3f3f3f; border-radius: 8px; padding: 10px 14px; color: #ececec; font-size: 14px; outline: none; transition: border-color 0.15s; font-family: inherit;
}
.form-row input:focus, .form-row textarea:focus, .form-row select:focus { border-color: #10a37f; }
.form-row input::placeholder, .form-row textarea::placeholder { color: #4a4a4a; }
.form-row textarea { resize: vertical; }
.form-row select { cursor: pointer; }
.form-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 8px; }

/* Buttons */
.cancel-btn { background: #2f2f2f; border: 1px solid #3f3f3f; color: #ececec; padding: 9px 20px; border-radius: 8px; cursor: pointer; font-size: 14px; transition: all 0.15s; }
.cancel-btn:hover { background: #383838; }
.submit-btn { background: #10a37f; border: none; color: white; padding: 9px 20px; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 500; transition: all 0.15s; }
.submit-btn:hover { background: #0d8c6d; }
.submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.submit-btn.full { width: 100%; padding: 12px; margin-top: 8px; }
.danger-btn { background: #ef4444; border: none; color: white; padding: 9px 20px; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 500; }
.danger-btn:hover { background: #dc2626; }

/* Documents */
.doc-list { display: flex; flex-direction: column; gap: 8px; }
.doc-card { display: flex; align-items: center; gap: 14px; background: #2f2f2f; border: 1px solid #3f3f3f; border-radius: 10px; padding: 14px 18px; transition: border-color 0.15s; }
.doc-card:hover { border-color: #4a4a4a; }
.doc-icon { width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; background: #1e1e1e; border-radius: 8px; color: #10a37f; flex-shrink: 0; }
.doc-info { flex: 1; }
.doc-title { font-size: 15px; font-weight: 600; color: #ececec; margin-bottom: 3px; }
.doc-meta { font-size: 12px; color: #6b7280; }
.doc-actions { display: flex; gap: 6px; flex-shrink: 0; }
.doc-btn { display: flex; align-items: center; gap: 5px; background: #1e1e1e; border: 1px solid #3f3f3f; color: #ececec; padding: 7px 14px; border-radius: 8px; cursor: pointer; font-size: 13px; transition: all 0.15s; }
.doc-btn.download:hover { border-color: #10a37f; color: #10a37f; }
.doc-btn.del:hover { border-color: #ef4444; color: #ef4444; }

/* Upload */
.upload-area { border: 2px dashed #3f3f3f; border-radius: 12px; padding: 48px 24px; text-align: center; cursor: pointer; transition: all 0.15s; margin-bottom: 20px; }
.upload-area:hover, .upload-area.dragging { border-color: #10a37f; background: rgba(16,163,127,0.05); }
.upload-area.hasFile { border-style: solid; border-color: #10a37f; background: rgba(16,163,127,0.05); }
.upload-prompt { color: #6b7280; }
.upload-text { font-size: 15px; color: #9ca3af; margin-top: 12px; }
.upload-hint { font-size: 12px; color: #4a4a4a; margin-top: 6px; }
.upload-file-info { display: flex; align-items: center; gap: 10px; justify-content: center; }
.upload-filename { font-size: 14px; color: #ececec; }
.upload-remove { background: none; border: none; color: #ef4444; cursor: pointer; font-size: 13px; }
.upload-form { background: #2f2f2f; border: 1px solid #3f3f3f; border-radius: 12px; padding: 20px; display: flex; flex-direction: column; gap: 12px; }
.upload-tips { margin-top: 24px; padding: 16px 20px; background: #2f2f2f; border: 1px solid #3f3f3f; border-radius: 10px; }
.upload-tips h4 { font-size: 13px; color: #9ca3af; margin-bottom: 8px; }
.upload-tips p { font-size: 13px; color: #6b7280; line-height: 1.8; }
.upload-tips code { background: #1e1e1e; padding: 1px 6px; border-radius: 4px; color: #10a37f; font-size: 12px; }

/* Editor modal */
.editor-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 20px; }
.editor-modal { background: #1a1a1a; border: 1px solid #3f3f3f; border-radius: 16px; width: 100%; max-width: 1100px; max-height: 92vh; display: flex; flex-direction: column; overflow: hidden; }
.editor-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 24px; border-bottom: 1px solid #3f3f3f; }
.editor-header h2 { font-size: 18px; font-weight: 600; color: #ececec; }
.close-btn { background: none; border: none; color: #9ca3af; cursor: pointer; padding: 4px; border-radius: 6px; transition: all 0.15s; }
.close-btn:hover { background: #2f2f2f; color: #ececec; }

.editor-meta { padding: 16px 24px; border-bottom: 1px solid #3f3f3f; display: flex; flex-direction: column; gap: 10px; }
.meta-row { display: flex; gap: 10px; }
.meta-input { flex: 1; background: #2f2f2f; border: 1px solid #3f3f3f; border-radius: 8px; padding: 9px 14px; color: #ececec; font-size: 14px; outline: none; transition: border-color 0.15s; font-family: inherit; }
.meta-input:focus { border-color: #10a37f; }
.meta-input::placeholder { color: #4a4a4a; }
.meta-select { width: 120px; background: #2f2f2f; border: 1px solid #3f3f3f; border-radius: 8px; padding: 9px 14px; color: #ececec; font-size: 14px; cursor: pointer; outline: none; }

/* Toolbar */
.toolbar { display: flex; align-items: center; gap: 2px; padding: 8px 24px; border-bottom: 1px solid #3f3f3f; background: #222; flex-wrap: wrap; }
.tool-btn { display: flex; align-items: center; gap: 4px; background: none; border: 1px solid transparent; color: #9ca3af; padding: 6px 10px; border-radius: 6px; cursor: pointer; font-size: 13px; transition: all 0.12s; min-width: 30px; justify-content: center; }
.tool-btn:hover { background: #2f2f2f; border-color: #3f3f3f; color: #ececec; }
.tool-btn.var-btn { color: #10a37f; }
.tool-divider { width: 1px; height: 20px; background: #3f3f3f; margin: 0 4px; }

/* Editor body */
.editor-body { display: flex; flex: 1; overflow: hidden; min-height: 350px; }
.editor-pane { flex: 1; display: flex; flex-direction: column; border-right: 1px solid #3f3f3f; }
.preview-pane { flex: 1; display: flex; flex-direction: column; background: #1e1e1e; }
.pane-label { font-size: 12px; color: #6b7280; padding: 8px 16px; border-bottom: 1px solid #2a2a2a; font-weight: 500; }
.editor-textarea { flex: 1; background: #1a1a1a; border: none; color: #ececec; padding: 16px; font-size: 14px; font-family: 'SF Mono', 'Cascadia Code', monospace; line-height: 1.7; resize: none; outline: none; }
.editor-textarea::placeholder { color: #4a4a4a; }
.preview-content { flex: 1; overflow-y: auto; padding: 16px; font-size: 14px; line-height: 1.8; color: #d1d5db; }
.preview-content :deep(h2) { font-size: 20px; font-weight: 700; color: #ececec; margin: 16px 0 8px; padding-bottom: 6px; border-bottom: 1px solid #3f3f3f; }
.preview-content :deep(h3) { font-size: 17px; font-weight: 600; color: #ececec; margin: 14px 0 6px; }
.preview-content :deep(p) { margin: 6px 0; }
.preview-content :deep(strong) { color: #ececec; font-weight: 700; }
.preview-content :deep(em) { color: #9ca3af; font-style: italic; }
.preview-content :deep(hr) { border: none; border-top: 1px solid #3f3f3f; margin: 16px 0; }
.preview-content :deep(.preview-li) { padding-left: 20px; position: relative; }
.preview-content :deep(.preview-li)::before { content: '•'; position: absolute; left: 6px; color: #10a37f; }
.preview-content :deep(.preview-li.num)::before { content: counter(item); counter-increment: item; }
.preview-content :deep(.preview-li.num) { counter-reset: item; }
.preview-content :deep(.preview-table) { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 13px; }
.preview-content :deep(.preview-table td) { border: 1px solid #3f3f3f; padding: 6px 10px; }
.preview-content :deep(.preview-table tr:first-child td) { background: #2f2f2f; font-weight: 600; color: #ececec; }
.preview-content :deep(.preview-var) { background: rgba(16,163,127,0.15); color: #10a37f; padding: 1px 6px; border-radius: 4px; font-family: 'SF Mono', monospace; font-size: 12px; }
.preview-content :deep(.preview-empty) { color: #4a4a4a; text-align: center; margin-top: 40px; }

/* Variable manager */
.var-manager { display: flex; align-items: center; gap: 8px; padding: 10px 24px; border-top: 1px solid #3f3f3f; background: #222; flex-wrap: wrap; }
.var-manager-label { font-size: 12px; color: #6b7280; white-space: nowrap; }
.var-list { display: flex; flex-wrap: wrap; gap: 4px; }
.var-item { background: rgba(16,163,127,0.1); border: 1px solid rgba(16,163,127,0.3); color: #10a37f; font-size: 12px; padding: 3px 10px; border-radius: 6px; font-family: 'SF Mono', monospace; }

.editor-footer { display: flex; justify-content: flex-end; gap: 10px; padding: 14px 24px; border-top: 1px solid #3f3f3f; }

/* Confirm dialog */
.confirm-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 1100; }
.confirm-modal { background: #2f2f2f; border: 1px solid #3f3f3f; border-radius: 16px; padding: 32px; width: 90%; max-width: 400px; text-align: center; }
.confirm-icon { display: flex; justify-content: center; margin-bottom: 16px; }
.confirm-title { font-size: 18px; font-weight: 600; color: #ececec; margin-bottom: 8px; }
.confirm-text { font-size: 14px; color: #9ca3af; margin-bottom: 4px; }
.confirm-name { font-size: 15px; font-weight: 600; color: #ef4444; margin-bottom: 20px; }
.confirm-actions { display: flex; gap: 10px; justify-content: center; }

/* Empty state */
.empty-state { text-align: center; padding: 60px 0; color: #4a4a4a; }
.empty-state svg { margin-bottom: 12px; color: #3f3f3f; }
.empty-state p { font-size: 14px; }
</style>
