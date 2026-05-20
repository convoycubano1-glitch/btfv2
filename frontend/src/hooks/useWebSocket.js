import { useEffect, useCallback } from 'react'
import { useSelector } from 'react-redux'
import wsService from '../services/websocket'

export function useWebSocket() {
  const { token } = useSelector((s) => s.auth)
  const connected = useSelector((s) => s.market.connected)

  useEffect(() => {
    wsService.connect(token)
    return () => {} // Don't disconnect on component unmount; managed globally
  }, [token])

  const subscribe = useCallback((symbol) => {
    wsService.subscribe(symbol)
  }, [])

  const on = useCallback((type, handler) => {
    return wsService.on(type, handler)
  }, [])

  return { connected, subscribe, on }
}
