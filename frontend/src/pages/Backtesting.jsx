import { useState, useEffect } from 'react'
import { FlaskConical, Play, TrendingUp, TrendingDown } from 'lucide-react'
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'
import api from '../services/api'
import { STRATEGY_TYPES, TIMEFRAMES, POPULAR_PAIRS } from '../utils/constants'
import { formatCurrency, formatPct, formatDate, statusColor } from '../utils/formatters'
import Badge from '../components/common/Badge'
import { PageLoader } from '../components/common/LoadingSpinner'
import toast from 'react-hot-toast'

export default function Backtesting() {
  const [backtests, setBacktests] = useState([])
  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)
  const [form, setForm] = useState({
    name: 'EMA BTC 30d',
    symbol: 'BTC/USDT',
    timeframe: '1h',
    strategy_type: 'ema_crossover',
    start_date: '2024-01-01',
    end_date: '2024-06-01',
    initial_capital: 10000,
    parameters: {},
  })

  async function load() {
    const { data } = await api.get('/backtesting/')
    setBacktests(data)
    setLoading(false)
  }
  useEffect(() => { load() }, [])

  async function runBacktest(e) {
    e.preventDefault()
    setRunning(true)
    try {
      const { data } = await api.post('/backtesting/', {
        ...form,
        start_date: new Date(form.start_date).toISOString(),
        end_date: new Date(form.end_date).toISOString(),
        initial_capital: parseFloat(form.initial_capital),
      })
      toast.success('Backtest started!')
      await load()
      // Poll for completion
      let attempts = 0
      const poll = setInterval(async () => {
        attempts++
        const { data: bt } = await api.get(`/backtesting/${data.id}`)
        if (bt.status === 'completed' || bt.status === 'failed' || attempts > 60) {
          clearInterval(poll)
          await load()
          if (bt.status === 'completed') {
            setSelected(bt)
            toast.success('Backtest complete!')
          }
        }
      }, 3000)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to run backtest')
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
      {/* Form */}
      <div className="xl:col-span-1">
        <div className="card">
          <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
            <FlaskConical size={18} className="text-brand-400" />
            New Backtest
          </h3>
          <form onSubmit={runBacktest} className="space-y-3">
            <div>
              <label className="label">Name</label>
              <input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
            </div>
            <div>
              <label className="label">Strategy</label>
              <select className="input" value={form.strategy_type} onChange={(e) => setForm({ ...form, strategy_type: e.target.value })}>
                {STRATEGY_TYPES.filter(s => s.value !== 'custom').map((s) => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="label">Symbol</label>
              <input className="input" value={form.symbol} onChange={(e) => setForm({ ...form, symbol: e.target.value.toUpperCase() })} />
            </div>
            <div>
              <label className="label">Timeframe</label>
              <select className="input" value={form.timeframe} onChange={(e) => setForm({ ...form, timeframe: e.target.value })}>
                {TIMEFRAMES.map((tf) => <option key={tf.value} value={tf.value}>{tf.label}</option>)}
              </select>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="label">Start Date</label>
                <input type="date" className="input" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} />
              </div>
              <div>
                <label className="label">End Date</label>
                <input type="date" className="input" value={form.end_date} onChange={(e) => setForm({ ...form, end_date: e.target.value })} />
              </div>
            </div>
            <div>
              <label className="label">Initial Capital (USD)</label>
              <input type="number" className="input" value={form.initial_capital} onChange={(e) => setForm({ ...form, initial_capital: e.target.value })} min="100" />
            </div>
            <button type="submit" disabled={running} className="btn-primary w-full flex items-center justify-center gap-2">
              <Play size={15} />
              {running ? 'Running...' : 'Run Backtest'}
            </button>
          </form>
        </div>
      </div>

      {/* Results */}
      <div className="xl:col-span-2 space-y-4">
        {selected && selected.status === 'completed' && (
          <div className="card space-y-4">
            <h3 className="font-semibold text-white">{selected.name} — Results</h3>
            {/* Metrics */}
            <div className="grid grid-cols-3 gap-3">
              {[
                ['Return', formatPct(selected.total_return_pct), selected.total_return_pct >= 0],
                ['Sharpe', selected.sharpe_ratio?.toFixed(2) ?? '—', null],
                ['Max DD', formatPct(-selected.max_drawdown_pct), false],
                ['Win Rate', formatPct(selected.win_rate_pct), null],
                ['Trades', selected.total_trades, null],
                ['Profit Factor', selected.profit_factor?.toFixed(2) ?? '—', selected.profit_factor >= 1],
              ].map(([k, v, pos]) => (
                <div key={k} className="bg-surface-100 rounded-lg p-3 text-center">
                  <p className="text-xs text-gray-400 mb-1">{k}</p>
                  <p className={`font-mono font-semibold text-sm ${pos === null ? 'text-white' : pos ? 'text-trading-green' : 'text-trading-red'}`}>{v}</p>
                </div>
              ))}
            </div>
            {/* Equity curve */}
            {selected.equity_curve?.length > 0 && (
              <div>
                <p className="text-sm font-medium text-gray-400 mb-2">Equity Curve</p>
                <ResponsiveContainer width="100%" height={200}>
                  <AreaChart data={selected.equity_curve}>
                    <defs>
                      <linearGradient id="btGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2a2d3a" />
                    <XAxis dataKey="date" tick={{ fill: '#6b7280', fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={(v) => v?.slice(5, 10)} />
                    <YAxis tick={{ fill: '#6b7280', fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={(v) => `$${(v/1000).toFixed(1)}k`} />
                    <Area type="monotone" dataKey="equity" stroke="#6366f1" strokeWidth={2} fill="url(#btGrad)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        )}

        {/* History list */}
        <div className="card">
          <h3 className="font-semibold text-white mb-4">Backtest History</h3>
          {loading ? <PageLoader /> : backtests.length === 0 ? (
            <p className="text-gray-500 text-sm text-center py-6">No backtests yet. Run your first test!</p>
          ) : (
            <div className="space-y-2">
              {backtests.map((bt) => (
                <button key={bt.id} onClick={() => bt.status === 'completed' && setSelected(bt)} className="w-full text-left flex items-center justify-between p-3 bg-surface-100 hover:bg-surface-200 rounded-lg transition-colors">
                  <div>
                    <p className="font-medium text-white text-sm">{bt.name}</p>
                    <p className="text-xs text-gray-400">{bt.symbol} · {bt.timeframe} · {bt.strategy_type}</p>
                  </div>
                  <div className="text-right flex items-center gap-3">
                    {bt.status === 'completed' && (
                      <span className={`font-mono text-sm font-semibold ${(bt.total_return_pct ?? 0) >= 0 ? 'text-trading-green' : 'text-trading-red'}`}>
                        {formatPct(bt.total_return_pct)}
                      </span>
                    )}
                    <Badge variant={bt.status === 'completed' ? 'blue' : bt.status === 'failed' ? 'red' : 'yellow'}>
                      {bt.status}
                    </Badge>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
