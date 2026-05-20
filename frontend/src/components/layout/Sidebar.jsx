import { NavLink, useLocation } from 'react-router-dom'
import { useState } from 'react'
import {
  LayoutDashboard, Plug2, Bot, Cpu, FlaskConical, BarChart3,
  ShoppingBag, Signal, GraduationCap, LineChart, CreditCard,
  Sparkles, Settings, ChevronLeft, ChevronRight, Zap
} from 'lucide-react'
import clsx from 'clsx'

const NAV_ITEMS = [
  { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/exchanges', icon: Plug2, label: 'Exchanges' },
  { path: '/bots', icon: Bot, label: 'Bots' },
  { path: '/strategies', icon: Cpu, label: 'Strategies' },
  { path: '/backtesting', icon: FlaskConical, label: 'Backtesting' },
  { path: '/trading', icon: BarChart3, label: 'Live Trading' },
  { path: '/marketplace', icon: ShoppingBag, label: 'Marketplace' },
  { path: '/signals', icon: Signal, label: 'My Signals' },
  { path: '/course', icon: GraduationCap, label: 'Algo Course' },
  { path: '/reports', icon: LineChart, label: 'Reports' },
  { path: '/subscription', icon: CreditCard, label: 'Subscription' },
  { path: '/ai', icon: Sparkles, label: 'AI Assistant' },
  { path: '/settings', icon: Settings, label: 'Settings' },
]

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <aside
      className={clsx(
        'flex flex-col bg-surface-50 border-r border-surface-200 transition-all duration-300 shrink-0',
        collapsed ? 'w-16' : 'w-60'
      )}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-surface-200">
        <div className="w-8 h-8 bg-brand-500 rounded-lg flex items-center justify-center shrink-0">
          <Zap size={16} className="text-white" />
        </div>
        {!collapsed && (
          <div className="min-w-0">
            <p className="font-bold text-white text-sm leading-tight">TradeBotHub</p>
            <p className="text-brand-400 text-xs font-medium">Pro</p>
          </div>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4 px-2 overflow-y-auto">
        {NAV_ITEMS.map(({ path, icon: Icon, label }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg mb-1 transition-all duration-150 group',
                isActive
                  ? 'bg-brand-500/15 text-brand-400 border border-brand-500/20'
                  : 'text-gray-400 hover:bg-surface-100 hover:text-gray-200'
              )
            }
            title={collapsed ? label : undefined}
          >
            <Icon size={18} className="shrink-0" />
            {!collapsed && <span className="text-sm font-medium truncate">{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="flex items-center justify-center p-3 border-t border-surface-200 text-gray-400 hover:text-gray-200 transition-colors"
      >
        {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
      </button>
    </aside>
  )
}
