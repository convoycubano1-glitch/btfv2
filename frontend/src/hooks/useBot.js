import { useDispatch, useSelector } from 'react-redux'
import { useCallback } from 'react'
import { fetchBots, createBot, startBot, pauseBot, stopBot, deleteBot } from '../store/botSlice'

export function useBot() {
  const dispatch = useDispatch()
  const { items: bots, loading } = useSelector((s) => s.bots)

  const loadBots = useCallback(() => dispatch(fetchBots()), [dispatch])
  const addBot = useCallback((data) => dispatch(createBot(data)), [dispatch])
  const start = useCallback((id) => dispatch(startBot(id)), [dispatch])
  const pause = useCallback((id) => dispatch(pauseBot(id)), [dispatch])
  const stop = useCallback((id) => dispatch(stopBot(id)), [dispatch])
  const remove = useCallback((id) => dispatch(deleteBot(id)), [dispatch])

  return { bots, loading, loadBots, addBot, start, pause, stop, remove }
}
