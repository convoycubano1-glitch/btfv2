import axios from 'axios'

const api = axios.create({
  baseURL: `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
})

// ── Clerk token getter (set by ClerkTokenSync in App.jsx) ─────────────────────
let _clerkGetToken = null
export function setClerkGetToken(fn) {
  _clerkGetToken = fn
}

// ── Request interceptor — attach Clerk token ──────────────────────────────────
api.interceptors.request.use(
  async (config) => {
    if (_clerkGetToken) {
      const token = await _clerkGetToken()
      if (token) config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ── Response interceptor — handle 401 ─────────────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(error)
)

export default api
