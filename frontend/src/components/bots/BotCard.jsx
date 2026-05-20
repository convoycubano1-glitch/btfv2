import { useState } from 'react'
import { useBot } from '../../hooks/useBot'
import { useSelector } from 'react-redux'
import api from '../../services/api'
import Badge from '../common/Badge'
import { formatPct, formatRelative } from '../../utils/formatters'
import { Play, Pause, Square, Trash2, Bot as BotIcon, ChevronDown, ChevronUp } from 'lucide-react'
import clsx from 'clsx'

const STATUS_VARIANT = { active: 'green', paused: 'yellow', error: 'red', stopped: 'gray', draft: 'gray' }

export default function BotCard({ bot }) {
  const { start, pause, stop, remove } = useBot()
  const [expanded, setExpanded] = useState(false)

  return (
    <div className={clsx('card hover:border-surface-300 transition-colors', bot.status === 'error' && 'border-trading-red/30')}>
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3 min-w-0">
          <div className={clsx('p-2 rounded-lg shrink-0', {
            'bg-trading-green/10': bot.status === 'active',
            'bg-trading-yellow/10': bot.status === 'paused',
            'bg-trading-red/10': bot.status === 'error',
            'bg-surface-100': ['stopped', 'draft'].includes(bot.status),
          })}>
            <BotIcon size={18} className={clsx({
              'text-trading-green': bot.status === 'active',
              'text-trading-yellow': bot.status === 'paused',
              'text-trading-red': bot.status === 'error',
              'text-gray-400': ['stopped', 'draft'].includes(bot.status),
            })} />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <h3 className="font-semibold text-white truncate">{bot.name}</h3>
              <Badge variant={STATUS_VARIANT[bot.status] || 'gray'}>{bot.status}</Badge>
              <Badge variant={bot.mode === 'live' ? 'green' : 'yellow'}>{bot.mode}</Badge>
            </div>
            <p className="text-xs text-gray-400 mt-0.5">{bot.symbol} · {bot.timeframe}</p>
          </div>
        </div>

        <div className="flex items-center gap-1 shrink-0 ml-3">
          {bot.status === 'active' && (
            <button onClick={() => pause(bot.id)} className="p-2 text-trading-yellow hover:bg-trading-yellow/10 rounded-lg transition-colors" title="Pause">
              <Pause size={15} />
            </button>
          )}
          {(bot.status === 'paused' || bot.status === 'draft' || bot.status === 'stopped') && (
            <button onClick={() => start(bot.id)} className="p-2 text-trading-green hover:bg-trading-green/10 rounded-lg transition-colors" title="Start">
              <Play size={15} />
            </button>
          )}
          {bot.status !== 'stopped' && (
            <button onClick={() => stop(bot.id)} className="p-2 text-gray-400 hover:text-white hover:bg-surface-100 rounded-lg transition-colors" title="Stop">
              <Square size={15} />
            </button>
          )}
          <button onClick={() => remove(bot.id)} className="p-2 text-gray-400 hover:text-trading-red hover:bg-trading-red/10 rounded-lg transition-colors" title="Delete">
            <Trash2 size={15} />
          </button>
          <button onClick={() => setExpanded(!expanded)} className="p-2 text-gray-400 hover:text-white hover:bg-surface-100 rounded-lg transition-colors">
            {expanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
          </button>
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-4 gap-3 mt-4 pt-4 border-t border-surface-200">
        <div>
          <p className="stat-label">Total PnL</p>
          <p className={clsx('font-mono font-semibold text-sm', bot.total_pnl_pct >= 0 ? 'text-trading-green' : 'text-trading-red')}>
            {formatPct(bot.total_pnl_pct)}
          </p>
        </div>
        <div>
          <p className="stat-label">Trades</p>
          <p className="text-sm font-semibold text-white">{bot.total_trades}</p>
        </div>
        <div>
          <p className="stat-label">Win Rate</p>
          <p className="text-sm font-semibold text-white">
            {bot.total_trades > 0 ? ((bot.winning_trades / bot.total_trades) * 100).toFixed(0) : '—'}%
          </p>
        </div>
        <div>
          <p className="stat-label">Last Run</p>
          <p className="text-sm text-gray-400">{formatRelative(bot.last_run_at)}</p>
        </div>
      </div>

      {/* Expanded details */}
      {expanded && (
        <div className="mt-4 pt-4 border-t border-surface-200 grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
          <div className="flex justify-between"><span className="text-gray-400">Stop Loss</span><span className="text-white font-mono">{(bot.stop_loss_pct * 100).toFixed(1)}%</span></div>
          <div className="flex justify-between"><span className="text-gray-400">Take Profit</span><span className="text-white font-mono">{(bot.take_profit_pct * 100).toFixed(1)}%</span></div>
          <div className="flex justify-between"><span className="text-gray-400">Position Size</span><span className="text-white font-mono">{(bot.max_position_size_pct * 100).toFixed(1)}%</span></div>
          <div className="flex justify-between"><span className="text-gray-400">Max Daily Loss</span><span className="text-white font-mono">{(bot.max_daily_loss_pct * 100).toFixed(1)}%</span></div>
          <div className="flex justify-between"><span className="text-gray-400">Max Open Trades</span><span className="text-white font-mono">{bot.max_open_trades}</span></div>
          {bot.error_message && (
            <div className="col-span-2 text-trading-red text-xs bg-trading-red/10 rounded p-2 mt-1">
              {bot.error_message}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
