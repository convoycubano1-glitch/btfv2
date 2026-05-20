import { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, Activity } from 'lucide-react'
import api from '../services/api'
import Badge from '../components/common/Badge'
import { formatCurrency, formatPct, formatDatetime } from '../utils/formatters'
import { PageLoader } from '../components/common/LoadingSpinner'

export default function Trading() {
  const [trades, setTrades] = useState([])
  const [activeBots, setActiveBots] = useState([])
  const [loading, setLoading] = useState(true)
  const [mode, setMode] = useState('all')

  useEffect(() => {
    Promise.all([
      api.get('/trading/trades'),
      api.get('/trading/active-bots'),
    ]).then(([t, b]) => {
      setTrades(t.data.items || t.data || [])
      setActiveBots(b.data || [])
    }).finally(() => setLoading(false))
  }, [])

  const filtered = mode === 'all' ? trades : trades.filter((t) => t.mode === mode)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Live Trading Monitor</h2>
          <p className="text-xs text-trading-yellow mt-1">⚠️ For informational purposes only. Not financial advice.</p>
        </div>
        <div className="flex gap-2">
          {['all', 'paper', 'live'].map((m) => (
            <button key={m} onClick={() => setMode(m)} className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-colors ${mode === m ? 'bg-brand-500 text-white' : 'text-gray-400 hover:text-white bg-surface-100'}`}>
              {m}
            </button>
          ))}
        </div>
      </div>

      {/* Active bots summary */}
      {activeBots.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {activeBots.slice(0, 4).map((bot) => (
            <div key={bot.id} className="card-sm">
              <div className="flex items-center gap-2 mb-2">
                <span className="w-2 h-2 bg-trading-green rounded-full animate-pulse" />
                <span className="text-xs font-medium text-white truncate">{bot.name}</span>
              </div>
              <p className="text-xs text-gray-400">{bot.symbol}</p>
              <p className={`text-sm font-mono font-semibold ${(bot.total_pnl_pct ?? 0) >= 0 ? 'text-trading-green' : 'text-trading-red'}`}>
                {formatPct(bot.total_pnl_pct)}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Trade table */}
      <div className="card overflow-x-auto">
        <div className="flex items-center gap-2 mb-4">
          <Activity size={18} className="text-brand-400" />
          <h3 className="font-semibold text-white">Trade History ({filtered.length})</h3>
        </div>

        {loading ? <PageLoader /> : filtered.length === 0 ? (
          <p className="text-gray-500 text-sm text-center py-8">No trades found</p>
        ) : (
          <table className="w-full text-sm min-w-[700px]">
            <thead>
              <tr className="text-gray-500 text-xs border-b border-surface-200">
                {['Symbol', 'Side', 'Mode', 'Entry', 'Exit', 'Qty', 'PnL', 'Status', 'Opened'].map((h) => (
                  <th key={h} className={`pb-2 font-medium ${h === 'Symbol' || h === 'Side' ? 'text-left' : 'text-right'}`}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-200">
              {filtered.map((t) => (
                <tr key={t.id} className="hover:bg-surface-100 transition-colors">
                  <td className="py-2.5 font-mono font-medium text-white">{t.symbol}</td>
                  <td className="py-2.5">
                    <span className={`flex items-center gap-1 text-xs font-medium w-fit ${t.side === 'buy' ? 'text-trading-green' : 'text-trading-red'}`}>
                      {t.side === 'buy' ? <TrendingUp size={11} /> : <TrendingDown size={11} />}
                      {t.side.toUpperCase()}
                    </span>
                  </td>
                  <td className="py-2.5 text-right"><Badge variant={t.mode === 'live' ? 'green' : 'yellow'}>{t.mode}</Badge></td>
                  <td className="py-2.5 text-right font-mono text-gray-300">{formatCurrency(t.entry_price)}</td>
                  <td className="py-2.5 text-right font-mono text-gray-400">{t.exit_price ? formatCurrency(t.exit_price) : '—'}</td>
                  <td className="py-2.5 text-right font-mono text-gray-400">{t.quantity}</td>
                  <td className={`py-2.5 text-right font-mono font-semibold ${(t.pnl_pct ?? 0) >= 0 ? 'text-trading-green' : 'text-trading-red'}`}>
                    {t.pnl_pct !== null ? formatPct(t.pnl_pct) : '—'}
                  </td>
                  <td className="py-2.5 text-right"><Badge variant={t.status === 'open' ? 'blue' : t.status === 'closed' ? 'gray' : 'red'}>{t.status}</Badge></td>
                  <td className="py-2.5 text-right text-gray-500 text-xs">{formatDatetime(t.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
