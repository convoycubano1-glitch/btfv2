import axios from 'axios'

const api = axios.create({
  baseURL: `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
})

// ── Request interceptor — attach token ────────────────────────────────────────
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('tbh_token')
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
  },
  (error) => Promise.reject(error)
)

// ── Response interceptor — handle 401 ─────────────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refresh = localStorage.getItem('tbh_refresh')

      if (refresh) {
        try {
          const { data } = await axios.post(
            `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/auth/refresh`,
            { refresh_token: refresh }
          )
          localStorage.setItem('tbh_token', data.access_token)
          localStorage.setItem('tbh_refresh', data.refresh_token)
          api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`
          originalRequest.headers['Authorization'] = `Bearer ${data.access_token}`
          return api(originalRequest)
        } catch {
          localStorage.removeItem('tbh_token')
          localStorage.removeItem('tbh_refresh')
          window.location.href = '/login'
        }
      }
    }

    return Promise.reject(error)
  }
)

export default api
