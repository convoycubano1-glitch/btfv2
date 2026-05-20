import { useSelector } from 'react-redux'
import { useWebSocket } from './useWebSocket'

export function useMarket() {
  const tickers = useSelector((s) => s.market.tickers)
  const connected = useSelector((s) => s.market.connected)
  const { subscribe } = useWebSocket()

  const getTicker = (symbol) => tickers[symbol] || null
  const getPrice = (symbol) => tickers[symbol]?.last || null
  const getChange = (symbol) => tickers[symbol]?.change_24h || 0

  return { tickers, connected, subscribe, getTicker, getPrice, getChange }
}
