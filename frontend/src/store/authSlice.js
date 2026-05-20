import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../services/api'

// Only remaining thunk: emergency stop (still hits our backend)
export const emergencyStop = createAsyncThunk('auth/emergencyStop', async () => {
  const { data } = await api.post('/auth/emergency-stop')
  return data
})

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    emergencyStopActive: false,
    loading: false,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(emergencyStop.pending, (state) => { state.loading = true })
      .addCase(emergencyStop.fulfilled, (state) => {
        state.loading = false
        state.emergencyStopActive = true
      })
      .addCase(emergencyStop.rejected, (state) => { state.loading = false })
  },
})

export default authSlice.reducer
