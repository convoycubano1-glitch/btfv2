import clsx from 'clsx'
import { TrendingUp, TrendingDown } from 'lucide-react'

export default function StatsCard({ title, value, change, changeLabel, icon: Icon, iconColor = 'text-brand-400', loading = false }) {
  const isPositive = change >= 0

  if (loading) {
    return (
      <div className="card">
        <div className="skeleton h-4 w-24 mb-3 rounded" />
        <div className="skeleton h-8 w-32 mb-2 rounded" />
        <div className="skeleton h-3 w-20 rounded" />
      </div>
    )
  }

  return (
    <div className="card hover:border-surface-300 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <span className="text-sm text-gray-400 font-medium">{title}</span>
        {Icon && (
          <div className={clsx('p-2 rounded-lg bg-surface-100', iconColor)}>
            <Icon size={16} />
          </div>
        )}
      </div>
      <p className="stat-value text-white mb-1">{value}</p>
      {change !== undefined && (
        <div className={clsx('flex items-center gap-1 text-xs font-medium', isPositive ? 'text-trading-green' : 'text-trading-red')}>
          {isPositive ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
          <span>{isPositive ? '+' : ''}{change?.toFixed(2)}%</span>
          {changeLabel && <span className="text-gray-500 font-normal">{changeLabel}</span>}
        </div>
      )}
    </div>
  )
}
