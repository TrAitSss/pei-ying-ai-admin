<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-logo">
        <div class="logo-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#10a37f" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/>
          </svg>
        </div>
        <h1 class="login-title">培英中学</h1>
        <p class="login-subtitle">AI 行政管理平台</p>
      </div>

      <form class="login-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label>用户名</label>
          <input
            v-model="form.username"
            type="text"
            placeholder="请输入用户名"
            autocomplete="username"
            :disabled="loading"
          />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            autocomplete="current-password"
            :disabled="loading"
          />
        </div>
        <div v-if="error" class="login-error">{{ error }}</div>
        <button type="submit" class="login-btn" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/axios'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const error = ref('')

const form = reactive({ username: '', password: '' })

async function handleLogin() {
  error.value = ''
  if (!form.username || !form.password) {
    error.value = '请输入用户名和密码'
    return
  }
  loading.value = true
  try {
    const params = new URLSearchParams()
    params.append('username', form.username)
    params.append('password', form.password)
    const res = await api.post('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    authStore.setToken(res.data.access_token)
    const userRes = await api.get('/auth/me', {
      headers: { Authorization: `Bearer ${res.data.access_token}` }
    })
    authStore.setUser(userRes.data)
    router.push('/dashboard')
  } catch (err) {
    error.value = err.response?.data?.detail || '用户名或密码错误'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #212121;
  padding: 20px;
}
.login-card {
  width: 100%;
  max-width: 400px;
  background: #2f2f2f;
  border: 1px solid #3f3f3f;
  border-radius: 16px;
  padding: 40px 32px;
}
.login-logo {
  text-align: center;
  margin-bottom: 32px;
}
.logo-icon {
  width: 56px;
  height: 56px;
  background: rgba(16, 163, 127, 0.1);
  border-radius: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}
.login-title {
  font-size: 24px;
  font-weight: 600;
  color: #ececec;
  margin-bottom: 4px;
}
.login-subtitle {
  font-size: 14px;
  color: #9ca3af;
}
.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.form-group label {
  font-size: 14px;
  color: #9ca3af;
  font-weight: 500;
}
.form-group input {
  background: #1e1e1e;
  border: 1px solid #3f3f3f;
  border-radius: 10px;
  padding: 12px 16px;
  font-size: 15px;
  color: #ececec;
  outline: none;
  transition: border-color 0.2s;
}
.form-group input:focus {
  border-color: #10a37f;
}
.form-group input::placeholder {
  color: #4a4a4a;
}
.form-group input:disabled {
  opacity: 0.5;
}
.login-error {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
}
.login-btn {
  background: #10a37f;
  color: white;
  border: none;
  border-radius: 10px;
  padding: 12px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
  margin-top: 8px;
}
.login-btn:hover {
  background: #0d8c6d;
}
.login-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>