import { useState, useEffect } from 'react'
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine
} from 'recharts'
import api from '../../services/api'
import { formatCurrency } from '../../utils/formatters'
import { PageLoader } from '../common/LoadingSpinner'

const PERIODS = ['7d', '30d', '90d', '1y']

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  const val = payload[0]?.value
  return (
    <div className="card-sm text-xs">
      <p className="text-gray-400 mb-1">{label}</p>
      <p className="text-white font-semibold">{formatCurrency(val)}</p>
    </div>
  )
}

export default function PortfolioChart() {
  const [data, setData] = useState([])
  const [period, setPeriod] = useState('30d')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      setLoading(true)
      try {
        const { data: resp } = await api.get(`/reports/performance?period=${period}`)
        if (resp.equity_curve) {
          setData(resp.equity_curve.map((p) => ({
            date: new Date(p.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
            equity: p.equity,
          })))
        }
      } catch {
        setData([])
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [period])

  const firstVal = data[0]?.equity || 10000
  const lastVal = data[data.length - 1]?.equity || firstVal
  const isPositive = lastVal >= firstVal

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h3 className="font-semibold text-white">Portfolio Equity</h3>
          <p className={`text-sm font-medium mt-0.5 ${isPositive ? 'text-trading-green' : 'text-trading-red'}`}>
            {formatCurrency(lastVal)} {isPositive ? '▲' : '▼'} {(((lastVal - firstVal) / firstVal) * 100).toFixed(2)}%
          </p>
        </div>
        <div className="flex gap-1">
          {PERIODS.map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${period === p ? 'bg-brand-500 text-white' : 'text-gray-400 hover:text-white hover:bg-surface-100'}`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="h-48 flex items-center justify-center">
          <PageLoader />
        </div>
      ) : data.length === 0 ? (
        <div className="h-48 flex items-center justify-center text-gray-500 text-sm">
          No equity data yet. Start trading to see your curve.
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={data}>
            <defs>
              <linearGradient id="equityGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={isPositive ? '#00d395' : '#ff4d4f'} stopOpacity={0.2} />
                <stop offset="95%" stopColor={isPositive ? '#00d395' : '#ff4d4f'} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a2d3a" />
            <XAxis dataKey="date" tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={(v) => `$${(v / 1000).toFixed(1)}k`} />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine y={firstVal} stroke="#4b5563" strokeDasharray="4 4" />
            <Area
              type="monotone"
              dataKey="equity"
              stroke={isPositive ? '#00d395' : '#ff4d4f'}
              strokeWidth={2}
              fill="url(#equityGrad)"
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
