<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="login-header">
          <h2>培英中学 AI 行政管理平台</h2>
          <p>请登录以继续</p>
        </div>
      </template>
      <el-form :model="form" @submit.prevent="handleLogin">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" style="width: 100%">登录</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  username: '',
  password: ''
})

async function handleLogin() {
  try {
    const params = new URLSearchParams()
    params.append('username', form.username)
    params.append('password', form.password)
    
    const res = await axios.post('/api/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    
    authStore.setToken(res.data.access_token)
    
    const userRes = await axios.get('/api/auth/me', {
      headers: { Authorization: `Bearer ${res.data.access_token}` }
    })
    authStore.setUser(userRes.data)
    
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '登录失败')
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a365d 0%, #2b6cb0 100%);
}
.login-card {
  width: 400px;
}
.login-header {
  text-align: center;
}
.login-header h2 {
  margin-bottom: 8px;
  color: #1a365d;
}
.login-header p {
  color: #666;
  font-size: 14px;
}
</style>
