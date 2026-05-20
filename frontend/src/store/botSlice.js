import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../services/api'
import toast from 'react-hot-toast'

export const fetchBots = createAsyncThunk('bots/fetchAll', async () => {
  const { data } = await api.get('/bots/')
  return data
})

export const createBot = createAsyncThunk('bots/create', async (payload, { rejectWithValue }) => {
  try {
    const { data } = await api.post('/bots/', payload)
    return data
  } catch (err) {
    return rejectWithValue(err.response?.data?.detail || 'Failed to create bot')
  }
})

export const startBot = createAsyncThunk('bots/start', async (botId, { rejectWithValue }) => {
  try {
    const { data } = await api.post(`/bots/${botId}/start`)
    return data
  } catch (err) {
    return rejectWithValue(err.response?.data?.detail || 'Failed to start bot')
  }
})

export const pauseBot = createAsyncThunk('bots/pause', async (botId) => {
  const { data } = await api.post(`/bots/${botId}/pause`)
  return data
})

export const stopBot = createAsyncThunk('bots/stop', async (botId) => {
  const { data } = await api.post(`/bots/${botId}/stop`)
  return data
})

export const deleteBot = createAsyncThunk('bots/delete', async (botId) => {
  await api.delete(`/bots/${botId}`)
  return botId
})

const botSlice = createSlice({
  name: 'bots',
  initialState: {
    items: [],
    loading: false,
    error: null,
  },
  reducers: {
    updateBotFromWS(state, { payload }) {
      const idx = state.items.findIndex((b) => b.id === payload.id)
      if (idx !== -1) state.items[idx] = { ...state.items[idx], ...payload }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchBots.pending, (state) => { state.loading = true })
      .addCase(fetchBots.fulfilled, (state, { payload }) => {
        state.loading = false
        state.items = payload
      })
      .addCase(fetchBots.rejected, (state) => { state.loading = false })
      .addCase(createBot.fulfilled, (state, { payload }) => {
        state.items.unshift(payload)
        toast.success('Bot created successfully')
      })
      .addCase(createBot.rejected, (_, { payload }) => {
        toast.error(payload || 'Failed to create bot')
      })
      .addCase(startBot.fulfilled, (state, { payload }) => {
        const idx = state.items.findIndex((b) => b.id === payload.id)
        if (idx !== -1) state.items[idx] = payload
        toast.success('Bot started')
      })
      .addCase(startBot.rejected, (_, { payload }) => {
        toast.error(payload || 'Failed to start bot')
      })
      .addCase(pauseBot.fulfilled, (state, { payload }) => {
        const idx = state.items.findIndex((b) => b.id === payload.id)
        if (idx !== -1) state.items[idx] = payload
        toast('Bot paused', { icon: '⏸' })
      })
      .addCase(stopBot.fulfilled, (state, { payload }) => {
        const idx = state.items.findIndex((b) => b.id === payload.id)
        if (idx !== -1) state.items[idx] = payload
        toast('Bot stopped', { icon: '⏹' })
      })
      .addCase(deleteBot.fulfilled, (state, { payload }) => {
        state.items = state.items.filter((b) => b.id !== payload)
        toast.success('Bot deleted')
      })
  },
})

export const { updateBotFromWS } = botSlice.actions
export default botSlice.reducer
