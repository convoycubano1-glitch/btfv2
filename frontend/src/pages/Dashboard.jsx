import { useEffect, useState } from 'react'
import { Bot, TrendingUp, Activity, DollarSign, Zap } from 'lucide-react'
import StatsCard from '../components/dashboard/StatsCard'
import PortfolioChart from '../components/dashboard/PortfolioChart'
import ActiveBots from '../components/dashboard/ActiveBots'
import RecentTrades from '../components/dashboard/RecentTrades'
import EmergencyStop from '../components/common/EmergencyStop'
import api from '../services/api'
import { formatCurrency, formatPct } from '../utils/formatters'
import { useSelector } from 'react-redux'

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const bots = useSelector((s) => s.bots.items)

  useEffect(() => {
    api.get('/trading/portfolio-summary').then(({ data }) => setSummary(data)).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const activeBots = bots.filter((b) => b.status === 'active').length

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Stats row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Total Portfolio"
          value={summary ? formatCurrency(summary.total_equity) : '—'}
          change={summary?.total_pnl_pct}
          changeLabel="all time"
          icon={DollarSign}
          iconColor="text-trading-green"
          loading={loading}
        />
        <StatsCard
          title="Active Bots"
          value={activeBots.toString()}
          icon={Bot}
          iconColor="text-brand-400"
          loading={loading}
        />
        <StatsCard
          title="Total PnL"
          value={summary ? formatCurrency(summary.total_pnl) : '—'}
          change={summary?.total_pnl_pct}
          changeLabel="return"
          icon={TrendingUp}
          iconColor={summary?.total_pnl >= 0 ? 'text-trading-green' : 'text-trading-red'}
          loading={loading}
        />
        <StatsCard
          title="Total Trades"
          value={summary?.total_trades?.toString() ?? '—'}
          icon={Activity}
          iconColor="text-trading-blue"
          loading={loading}
        />
      </div>

      {/* Portfolio chart */}
      <PortfolioChart />

      {/* Bottom grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ActiveBots />
        <RecentTrades />
      </div>

      {/* Emergency Stop */}
      <EmergencyStop />
    </div>
  )
}
