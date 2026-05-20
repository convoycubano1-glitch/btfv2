import { useEffect, useState } from 'react'
import { Plus, Bot } from 'lucide-react'
import { useBot } from '../hooks/useBot'
import BotCard from '../components/bots/BotCard'
import BotBuilder from '../components/bots/BotBuilder'
import { PageLoader } from '../components/common/LoadingSpinner'

export default function Bots() {
  const { bots, loading, loadBots } = useBot()
  const [showBuilder, setShowBuilder] = useState(false)

  useEffect(() => { loadBots() }, [])

  const byStatus = {
    active: bots.filter((b) => b.status === 'active'),
    paused: bots.filter((b) => b.status === 'paused'),
    other: bots.filter((b) => !['active', 'paused'].includes(b.status)),
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Trading Bots</h2>
          <p className="text-sm text-gray-400 mt-1">
            {bots.length} total · {byStatus.active.length} active
          </p>
        </div>
        <button onClick={() => setShowBuilder(true)} className="btn-primary flex items-center gap-2">
          <Plus size={16} /> New Bot
        </button>
      </div>

      {loading ? (
        <PageLoader />
      ) : bots.length === 0 ? (
        <div className="card text-center py-16">
          <Bot size={48} className="mx-auto text-gray-600 mb-3" />
          <h3 className="font-semibold text-white text-lg mb-1">No bots yet</h3>
          <p className="text-gray-400 text-sm mb-6">Create your first automated trading bot. Starts in paper mode.</p>
          <button onClick={() => setShowBuilder(true)} className="btn-primary">
            Create First Bot
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {byStatus.active.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
                <span className="w-2 h-2 bg-trading-green rounded-full animate-pulse" />
                Active ({byStatus.active.length})
              </h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {byStatus.active.map((b) => <BotCard key={b.id} bot={b} />)}
              </div>
            </div>
          )}
          {byStatus.paused.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-400 mb-3">Paused ({byStatus.paused.length})</h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {byStatus.paused.map((b) => <BotCard key={b.id} bot={b} />)}
              </div>
            </div>
          )}
          {byStatus.other.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-400 mb-3">Other ({byStatus.other.length})</h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {byStatus.other.map((b) => <BotCard key={b.id} bot={b} />)}
              </div>
            </div>
          )}
        </div>
      )}

      <BotBuilder isOpen={showBuilder} onClose={() => setShowBuilder(false)} />
    </div>
  )
}
