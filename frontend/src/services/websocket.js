import { store } from '../store'
import { updateTicker, setConnected } from '../store/marketSlice'
import { updateBotFromWS } from '../store/botSlice'

const WS_BASE = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/v1/ws'

class WebSocketService {
  constructor() {
    this.ws = null
    this.reconnectTimer = null
    this.reconnectDelay = 2000
    this.maxReconnectDelay = 30000
    this.listeners = new Map()
  }

  connect(token) {
    if (this.ws?.readyState === WebSocket.OPEN) return

    const url = token ? `${WS_BASE}/connect?token=${token}` : `${WS_BASE}/market`
    this.ws = new WebSocket(url)

    this.ws.onopen = () => {
      store.dispatch(setConnected(true))
      this.reconnectDelay = 2000
      console.log('[WS] Connected')
    }

    this.ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        this._dispatch(msg)
      } catch (e) {
        console.error('[WS] Parse error', e)
      }
    }

    this.ws.onclose = () => {
      store.dispatch(setConnected(false))
      console.log('[WS] Disconnected, reconnecting...')
      this._scheduleReconnect(token)
    }

    this.ws.onerror = (err) => {
      console.error('[WS] Error', err)
    }
  }

  _dispatch(msg) {
    // Update Redux for known types
    if (msg.type === 'ticker') {
      store.dispatch(updateTicker(msg))
    } else if (msg.type === 'bot_update') {
      store.dispatch(updateBotFromWS(msg))
    }

    // Notify custom listeners
    const handlers = this.listeners.get(msg.type) || []
    handlers.forEach((fn) => fn(msg))
  }

  on(type, handler) {
    if (!this.listeners.has(type)) this.listeners.set(type, [])
    this.listeners.get(type).push(handler)
    return () => this.off(type, handler)
  }

  off(type, handler) {
    const handlers = this.listeners.get(type) || []
    this.listeners.set(type, handlers.filter((h) => h !== handler))
  }

  send(data) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }

  subscribe(symbol) {
    this.send({ type: 'subscribe_price', symbol })
  }

  disconnect() {
    clearTimeout(this.reconnectTimer)
    this.ws?.close()
    this.ws = null
  }

  _scheduleReconnect(token) {
    clearTimeout(this.reconnectTimer)
    this.reconnectTimer = setTimeout(() => {
      this.reconnectDelay = Math.min(this.reconnectDelay * 1.5, this.maxReconnectDelay)
      this.connect(token)
    }, this.reconnectDelay)
  }
}

const wsService = new WebSocketService()
export default wsService
