import { createSlice } from '@reduxjs/toolkit'

const marketSlice = createSlice({
  name: 'market',
  initialState: {
    tickers: {},      // { "BTC/USDT": { last, change_24h, volume, ... } }
    connected: false,
  },
  reducers: {
    updateTicker(state, { payload }) {
      state.tickers[payload.symbol] = payload
    },
    setConnected(state, { payload }) {
      state.connected = payload
    },
    bulkUpdateTickers(state, { payload }) {
      payload.forEach((t) => { state.tickers[t.symbol] = t })
    },
  },
})

export const { updateTicker, setConnected, bulkUpdateTickers } = marketSlice.actions
export default marketSlice.reducer
