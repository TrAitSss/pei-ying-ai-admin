import axios from 'axios'

const api = axios.create({
  baseURL: window.location.origin + '/api',
  timeout: 30000,
})

// 自动给路径加尾部斜杠，避免 307 重定向到 HTTP
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  if (config.url && !config.url.includes('?') && !config.url.endsWith('/')) {
    config.url += '/'
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api