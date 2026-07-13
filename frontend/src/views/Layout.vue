<template>
  <el-container class="layout-container">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <span>Steven AI 助手</span>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        background-color="#1a365d"
        text-color="#fff"
        active-text-color="#63b3ed"
        class="sidebar-menu"
      >
        <el-menu-item v-for="route in menuRoutes" :key="route.path" :index="route.path">
          <el-icon><component :is="route.meta.icon" /></el-icon>
          <span>{{ route.meta.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header class="header">
        <div class="header-right">
          <span class="username">{{ authStore.user?.full_name || authStore.user?.username }}</span>
          <el-button type="danger" size="small" @click="handleLogout">退出</el-button>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const menuRoutes = computed(() => {
  const layout = route.matched.find(r => r.path === '/')
  return layout?.children?.filter(r => r.meta?.title) || []
})

function handleLogout() {
  authStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
}
.sidebar {
  background: #1a365d;
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  font-weight: bold;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
.sidebar-menu {
  border-right: none;
}
.header {
  background: white;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  box-shadow: 0 1px 4px rgba(0,0,0,0.1);
  z-index: 10;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.username {
  color: #333;
  font-size: 14px;
}
.main-content {
  background: #f5f7fa;
  padding: 20px;
}
</style>
