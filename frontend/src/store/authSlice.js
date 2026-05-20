import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../services/api'

const TOKEN_KEY = 'tbh_token'
const REFRESH_KEY = 'tbh_refresh'

export const login = createAsyncThunk('auth/login', async (credentials, { rejectWithValue }) => {
  try {
    const { data } = await api.post('/auth/login', credentials)
    localStorage.setItem(TOKEN_KEY, data.access_token)
    localStorage.setItem(REFRESH_KEY, data.refresh_token)
    api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`
    return data
  } catch (err) {
    return rejectWithValue(err.response?.data?.detail || 'Login failed')
  }
})

export const register = createAsyncThunk('auth/register', async (payload, { rejectWithValue }) => {
  try {
    const { data } = await api.post('/auth/register', payload)
    localStorage.setItem(TOKEN_KEY, data.access_token)
    localStorage.setItem(REFRESH_KEY, data.refresh_token)
    api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`
    return data
  } catch (err) {
    return rejectWithValue(err.response?.data?.detail || 'Registration failed')
  }
})

export const fetchMe = createAsyncThunk('auth/fetchMe', async (_, { rejectWithValue }) => {
  try {
    const { data } = await api.get('/auth/me')
    return data
  } catch (err) {
    return rejectWithValue(err.response?.data?.detail)
  }
})

export const emergencyStop = createAsyncThunk('auth/emergencyStop', async () => {
  const { data } = await api.post('/auth/emergency-stop')
  return data
})

const storedToken = localStorage.getItem(TOKEN_KEY)
if (storedToken) {
  api.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`
}

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: null,
    token: storedToken || null,
    loading: false,
    error: null,
  },
  reducers: {
    logout(state) {
      state.user = null
      state.token = null
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(REFRESH_KEY)
      delete api.defaults.headers.common['Authorization']
    },
    clearError(state) {
      state.error = null
    },
    updateUser(state, action) {
      state.user = { ...state.user, ...action.payload }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => { state.loading = true; state.error = null })
      .addCase(login.fulfilled, (state, { payload }) => {
        state.loading = false
        state.token = payload.access_token
        state.user = payload.user
      })
      .addCase(login.rejected, (state, { payload }) => {
        state.loading = false
        state.error = payload
      })
      .addCase(register.pending, (state) => { state.loading = true; state.error = null })
      .addCase(register.fulfilled, (state, { payload }) => {
        state.loading = false
        state.token = payload.access_token
        state.user = payload.user
      })
      .addCase(register.rejected, (state, { payload }) => {
        state.loading = false
        state.error = payload
      })
      .addCase(fetchMe.fulfilled, (state, { payload }) => {
        state.user = payload
      })
      .addCase(emergencyStop.fulfilled, (state) => {
        if (state.user) state.user.emergency_stop_active = true
      })
  },
})

export const { logout, clearError, updateUser } = authSlice.actions
export default authSlice.reducer
