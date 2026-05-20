import { useDispatch } from 'react-redux'
import { useCallback } from 'react'
import { useUser, useAuth as useClerkAuth } from '@clerk/react'
import { emergencyStop } from '../store/authSlice'
import wsService from '../services/websocket'

export function useAuth() {
  const dispatch = useDispatch()
  const { user: clerkUser, isLoaded } = useUser()
  const { isSignedIn, signOut: clerkSignOut, getToken } = useClerkAuth()

  const signOut = useCallback(async () => {
    wsService.disconnect()
    await clerkSignOut()
  }, [clerkSignOut])

  const triggerEmergencyStop = useCallback(() => dispatch(emergencyStop()), [dispatch])

  // Map Clerk user to app-compatible shape
  const user = clerkUser ? {
    email: clerkUser.primaryEmailAddress?.emailAddress,
    username: clerkUser.username || clerkUser.firstName || clerkUser.primaryEmailAddress?.emailAddress?.split('@')[0],
    full_name: clerkUser.fullName,
    avatar_url: clerkUser.imageUrl,
    clerk_id: clerkUser.id,
  } : null

  return {
    user,
    isAuthenticated: !!isSignedIn,
    isLoaded,
    loading: !isLoaded,
    error: null,
    signOut,
    getToken,
    triggerEmergencyStop,
  }
}
