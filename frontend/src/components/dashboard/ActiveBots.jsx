import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Bot, Play, Pause, Square, ChevronRight } from 'lucide-react'
import { useBot } from '../../hooks/useBot'
import Badge from '../common/Badge'
import { formatRelative, formatPct } from '../../utils/formatters'
import clsx from 'clsx'

const STATUS_VARIANT = { active: 'green', paused: 'yellow', error: 'red', stopped: 'gray', draft: 'gray' }

export default function ActiveBots() {
  const { bots, loading, loadBots, start, pause, stop } = useBot()

  useEffect(() => { loadBots() }, [])

  const activeBots = bots.filter((b) => ['active', 'paused', 'error'].includes(b.status))

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-white">Active Bots</h3>
        <Link to="/bots" className="text-xs text-brand-400 hover:text-brand-300 flex items-center gap-1">
          View all <ChevronRight size={12} />
        </Link>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => <div key={i} className="skeleton h-14 rounded-lg" />)}
        </div>
      ) : activeBots.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <Bot size={32} className="mx-auto mb-2 opacity-40" />
          <p className="text-sm">No active bots</p>
          <Link to="/bots" className="text-brand-400 text-xs hover:underline mt-1 block">Create your first bot →</Link>
        </div>
      ) : (
        <div className="space-y-2">
          {activeBots.map((bot) => (
            <div key={bot.id} className="flex items-center justify-between p-3 bg-surface-100 rounded-lg hover:bg-surface-200 transition-colors">
              <div className="flex items-center gap-3 min-w-0">
                <div className={clsx('w-2 h-2 rounded-full shrink-0', {
                  'bg-trading-green animate-pulse': bot.status === 'active',
                  'bg-trading-yellow': bot.status === 'paused',
                  'bg-trading-red': bot.status === 'error',
                })} />
                <div className="min-w-0">
                  <p className="text-sm font-medium text-white truncate">{bot.name}</p>
                  <p className="text-xs text-gray-400">{bot.symbol} · {bot.timeframe}</p>
                </div>
              </div>
              <div className="flex items-center gap-3 shrink-0 ml-3">
                <div className="text-right hidden sm:block">
                  <p className={clsx('text-sm font-mono font-semibold', bot.total_pnl >= 0 ? 'text-trading-green' : 'text-trading-red')}>
                    {formatPct(bot.total_pnl_pct)}
                  </p>
                  <Badge variant={STATUS_VARIANT[bot.status] || 'gray'}>{bot.status}</Badge>
                </div>
                <div className="flex gap-1">
                  {bot.status === 'paused' && (
                    <button onClick={() => start(bot.id)} className="p-1.5 text-trading-green hover:bg-trading-green/10 rounded transition-colors" title="Start">
                      <Play size={14} />
                    </button>
                  )}
                  {bot.status === 'active' && (
                    <button onClick={() => pause(bot.id)} className="p-1.5 text-trading-yellow hover:bg-trading-yellow/10 rounded transition-colors" title="Pause">
                      <Pause size={14} />
                    </button>
                  )}
                  <button onClick={() => stop(bot.id)} className="p-1.5 text-gray-400 hover:text-trading-red hover:bg-trading-red/10 rounded transition-colors" title="Stop">
                    <Square size={14} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
