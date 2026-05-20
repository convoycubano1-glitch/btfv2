import { useDispatch, useSelector } from 'react-redux'
import { useCallback, useEffect } from 'react'
import { login, register, logout, fetchMe, emergencyStop } from '../store/authSlice'
import wsService from '../services/websocket'

export function useAuth() {
  const dispatch = useDispatch()
  const { user, token, loading, error } = useSelector((s) => s.auth)

  useEffect(() => {
    if (token && !user) {
      dispatch(fetchMe())
    }
  }, [token, user, dispatch])

  const signIn = useCallback((creds) => dispatch(login(creds)), [dispatch])
  const signUp = useCallback((data) => dispatch(register(data)), [dispatch])
  const signOut = useCallback(() => {
    wsService.disconnect()
    dispatch(logout())
  }, [dispatch])
  const triggerEmergencyStop = useCallback(() => dispatch(emergencyStop()), [dispatch])

  return {
    user,
    token,
    loading,
    error,
    isAuthenticated: !!token,
    signIn,
    signUp,
    signOut,
    triggerEmergencyStop,
  }
}
