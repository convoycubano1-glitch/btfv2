import { configureStore } from '@reduxjs/toolkit'
import authReducer from './authSlice'
import botReducer from './botSlice'
import marketReducer from './marketSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    bots: botReducer,
    market: marketReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({ serializableCheck: false }),
})
