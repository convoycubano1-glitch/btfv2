import { useLocation } from 'react-router-dom'
import { Bell, Wifi, WifiOff, LogOut, User } from 'lucide-react'
import { useSelector } from 'react-redux'
import { useAuth } from '../../hooks/useAuth'
import EmergencyStop from '../common/EmergencyStop'
import { formatCurrency } from '../../utils/formatters'

const PAGE_TITLES = {
  '/dashboard': 'Dashboard',
  '/exchanges': 'Exchange Connections',
  '/bots': 'Trading Bots',
  '/strategies': 'Strategy Library',
  '/backtesting': 'Backtesting Engine',
  '/trading': 'Live Trading',
  '/marketplace': 'Signal Marketplace',
  '/signals': 'My Signals',
  '/course': 'Algo Trading Course',
  '/reports': 'Performance Reports',
  '/subscription': 'Subscription',
  '/ai': 'AI Assistant',
  '/settings': 'Settings',
}

export default function Header() {
  const { pathname } = useLocation()
  const { user, signOut } = useAuth()
  const connected = useSelector((s) => s.market.connected)
  const title = PAGE_TITLES[pathname] || 'TradeBotHub Pro'

  return (
    <header className="flex items-center justify-between px-6 py-4 border-b border-surface-200 bg-surface-50 shrink-0">
      <div>
        <h1 className="text-lg font-semibold text-white">{title}</h1>
        <p className="text-xs text-gray-500">
          {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
        </p>
      </div>

      <div className="flex items-center gap-3">
        {/* WS Status */}
        <div className={`flex items-center gap-1.5 text-xs font-medium px-2 py-1 rounded-full ${connected ? 'text-trading-green bg-trading-green/10' : 'text-gray-500 bg-surface-100'}`}>
          {connected ? <Wifi size={12} /> : <WifiOff size={12} />}
          {connected ? 'Live' : 'Offline'}
        </div>

        {/* Emergency Stop */}
        <EmergencyStop compact />

        {/* Notifications */}
        <button className="relative p-2 text-gray-400 hover:text-white hover:bg-surface-100 rounded-lg transition-colors">
          <Bell size={18} />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-trading-red rounded-full" />
        </button>

        {/* User Menu */}
        <div className="flex items-center gap-2 pl-3 border-l border-surface-200">
          <div className="w-8 h-8 bg-brand-500 rounded-full flex items-center justify-center text-white text-sm font-semibold">
            {user?.username?.[0]?.toUpperCase() || 'U'}
          </div>
          <div className="hidden sm:block text-left">
            <p className="text-sm font-medium text-white leading-tight">{user?.username || 'User'}</p>
            <p className="text-xs text-brand-400 capitalize">{user?.subscription?.plan || 'free'}</p>
          </div>
          <button
            onClick={signOut}
            className="p-2 text-gray-400 hover:text-trading-red hover:bg-trading-red/10 rounded-lg transition-colors ml-1"
            title="Sign out"
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </header>
  )
}
