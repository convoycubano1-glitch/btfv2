import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { TrendingUp, TrendingDown, ChevronRight } from 'lucide-react'
import api from '../../services/api'
import { formatCurrency, formatPct, formatRelative } from '../../utils/formatters'
import Badge from '../common/Badge'

export default function RecentTrades() {
  const [trades, setTrades] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/trading/trades?limit=8').then(({ data }) => {
      setTrades(data.items || data || [])
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-white">Recent Trades</h3>
        <Link to="/trading" className="text-xs text-brand-400 hover:text-brand-300 flex items-center gap-1">
          View all <ChevronRight size={12} />
        </Link>
      </div>

      {loading ? (
        <div className="space-y-2">
          {[1,2,3,4].map(i => <div key={i} className="skeleton h-10 rounded" />)}
        </div>
      ) : trades.length === 0 ? (
        <p className="text-gray-500 text-sm text-center py-6">No trades yet</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-500 text-xs border-b border-surface-200">
                <th className="text-left pb-2 font-medium">Pair</th>
                <th className="text-left pb-2 font-medium">Side</th>
                <th className="text-right pb-2 font-medium">Entry</th>
                <th className="text-right pb-2 font-medium">PnL</th>
                <th className="text-right pb-2 font-medium">Mode</th>
                <th className="text-right pb-2 font-medium">When</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-200">
              {trades.map((t) => (
                <tr key={t.id} className="hover:bg-surface-100 transition-colors">
                  <td className="py-2.5 font-mono font-medium text-white">{t.symbol}</td>
                  <td className="py-2.5">
                    <span className={`flex items-center gap-1 text-xs font-medium ${t.side === 'buy' ? 'text-trading-green' : 'text-trading-red'}`}>
                      {t.side === 'buy' ? <TrendingUp size={11} /> : <TrendingDown size={11} />}
                      {t.side.toUpperCase()}
                    </span>
                  </td>
                  <td className="py-2.5 text-right font-mono text-gray-300">{formatCurrency(t.entry_price)}</td>
                  <td className={`py-2.5 text-right font-mono font-semibold ${(t.pnl_pct ?? 0) >= 0 ? 'text-trading-green' : 'text-trading-red'}`}>
                    {t.pnl_pct !== null ? formatPct(t.pnl_pct) : '—'}
                  </td>
                  <td className="py-2.5 text-right">
                    <Badge variant={t.mode === 'live' ? 'green' : 'yellow'}>{t.mode}</Badge>
                  </td>
                  <td className="py-2.5 text-right text-gray-500 text-xs">{formatRelative(t.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
