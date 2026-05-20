import { useState, useEffect } from 'react'
import { BarChart3 } from 'lucide-react'
import {
  ResponsiveContainer, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend
} from 'recharts'
import api from '../services/api'
import { formatCurrency, formatPct } from '../utils/formatters'
import { PageLoader } from '../components/common/LoadingSpinner'

const PERIODS = ['7d', '30d', '90d', '1y']

export default function Reports() {
  const [perf, setPerf] = useState(null)
  const [byStrategy, setByStrategy] = useState([])
  const [loading, setLoading] = useState(true)
  const [period, setPeriod] = useState('30d')

  useEffect(() => {
    setLoading(true)
    Promise.all([
      api.get(`/reports/performance?period=${period}`),
      api.get('/reports/trades-by-strategy'),
    ]).then(([p, s]) => {
      setPerf(p.data)
      setByStrategy(s.data || [])
    }).catch(() => {}).finally(() => setLoading(false))
  }, [period])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Performance Reports</h2>
          <p className="text-xs text-trading-yellow mt-1">⚠️ Historical data only. Not indicative of future performance.</p>
        </div>
        <div className="flex gap-1">
          {PERIODS.map((p) => (
            <button key={p} onClick={() => setPeriod(p)} className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${period === p ? 'bg-brand-500 text-white' : 'text-gray-400 hover:text-white bg-surface-100'}`}>
              {p}
            </button>
          ))}
        </div>
      </div>

      {loading ? <PageLoader /> : (
        <>
          {/* Summary stats */}
          {perf && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                ['Total Return', formatPct(perf.total_return_pct), perf.total_return_pct >= 0],
                ['Total Trades', perf.total_trades, null],
                ['Win Rate', formatPct(perf.win_rate_pct), null],
                ['Sharpe Ratio', perf.sharpe_ratio?.toFixed(2) ?? '—', null],
                ['Profit Factor', perf.profit_factor?.toFixed(2) ?? '—', (perf.profit_factor ?? 1) >= 1],
                ['Max Drawdown', formatPct(-Math.abs(perf.max_drawdown_pct ?? 0)), false],
                ['Avg Win', formatPct(perf.avg_win_pct), true],
                ['Avg Loss', formatPct(perf.avg_loss_pct), false],
              ].map(([k, v, pos]) => (
                <div key={k} className="card-sm text-center">
                  <p className="text-xs text-gray-400 mb-1">{k}</p>
                  <p className={`font-mono font-bold ${pos === null ? 'text-white' : pos ? 'text-trading-green' : 'text-trading-red'}`}>{v}</p>
                </div>
              ))}
            </div>
          )}

          {/* Equity curve */}
          {perf?.equity_curve?.length > 0 && (
            <div className="card">
              <h3 className="font-semibold text-white mb-4">Portfolio Equity Curve</h3>
              <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={perf.equity_curve}>
                  <defs>
                    <linearGradient id="reportGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2a2d3a" />
                  <XAxis dataKey="date" tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={(v) => v?.slice(5, 10)} />
                  <YAxis tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={(v) => `$${(v/1000).toFixed(1)}k`} />
                  <Tooltip
                    contentStyle={{ background: '#1a1d27', border: '1px solid #2a2d3a', borderRadius: 8, fontSize: 12 }}
                    labelStyle={{ color: '#9ca3af' }}
                  />
                  <Area type="monotone" dataKey="equity" stroke="#6366f1" strokeWidth={2} fill="url(#reportGrad)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* By strategy */}
          {byStrategy.length > 0 && (
            <div className="card">
              <h3 className="font-semibold text-white mb-4">Performance by Strategy</h3>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={byStrategy}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2a2d3a" />
                  <XAxis dataKey="strategy" tick={{ fill: '#6b7280', fontSize: 10 }} axisLine={false} />
                  <YAxis tick={{ fill: '#6b7280', fontSize: 10 }} axisLine={false} tickFormatter={(v) => `${v}%`} />
                  <Tooltip contentStyle={{ background: '#1a1d27', border: '1px solid #2a2d3a', borderRadius: 8, fontSize: 12 }} />
                  <Bar dataKey="total_pnl_pct" name="PnL %" fill="#6366f1" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </>
      )}
    </div>
  )
}
