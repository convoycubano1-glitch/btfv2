import { useState } from 'react'
import { TrendingUp, TrendingDown, Star, Lock } from 'lucide-react'
import Badge from '../common/Badge'
import { formatCurrency, formatPct, formatRelative } from '../../utils/formatters'
import api from '../../services/api'
import toast from 'react-hot-toast'

export default function SignalCard({ signal, onSubscribe }) {
  const [subscribing, setSubscribing] = useState(false)

  async function handleSubscribe() {
    setSubscribing(true)
    try {
      await api.post(`/marketplace/${signal.id}/subscribe`)
      toast.success('Subscribed to signal!')
      onSubscribe?.()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Subscription failed')
    } finally {
      setSubscribing(false)
    }
  }

  const isBuy = signal.signal_type === 'buy'
  const rr = signal.risk_reward_ratio

  return (
    <div className="card hover:border-surface-300 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className={`p-1.5 rounded-lg ${isBuy ? 'bg-trading-green/10' : 'bg-trading-red/10'}`}>
            {isBuy ? <TrendingUp size={16} className="text-trading-green" /> : <TrendingDown size={16} className="text-trading-red" />}
          </div>
          <div>
            <h3 className="font-semibold text-white text-sm">{signal.title}</h3>
            <p className="text-xs text-gray-500 font-mono">{signal.symbol} · {signal.timeframe}</p>
          </div>
        </div>
        <div className="flex flex-col items-end gap-1">
          <Badge variant={isBuy ? 'green' : 'red'}>{signal.signal_type.toUpperCase()}</Badge>
          {signal.is_free ? (
            <Badge variant="green">FREE</Badge>
          ) : (
            <Badge variant="blue">${signal.price_usd}/mo</Badge>
          )}
        </div>
      </div>

      {/* Price targets */}
      <div className="grid grid-cols-3 gap-2 my-3 text-xs">
        <div className="bg-surface-100 rounded-lg p-2 text-center">
          <p className="text-gray-500 mb-0.5">Entry</p>
          <p className="text-white font-mono font-semibold">{formatCurrency(signal.entry_price)}</p>
        </div>
        <div className="bg-trading-red/5 border border-trading-red/20 rounded-lg p-2 text-center">
          <p className="text-gray-500 mb-0.5">Stop Loss</p>
          <p className="text-trading-red font-mono font-semibold">{formatCurrency(signal.stop_loss)}</p>
        </div>
        <div className="bg-trading-green/5 border border-trading-green/20 rounded-lg p-2 text-center">
          <p className="text-gray-500 mb-0.5">TP1</p>
          <p className="text-trading-green font-mono font-semibold">{formatCurrency(signal.take_profit_1)}</p>
        </div>
      </div>

      <div className="flex items-center justify-between text-xs text-gray-400 mb-3">
        <div className="flex items-center gap-1">
          <Star size={11} className="text-trading-yellow" />
          <span>{signal.subscribers_count} subscribers</span>
        </div>
        {rr && (
          <span className="font-mono">R:R {rr.toFixed(2)}</span>
        )}
        <span>{formatRelative(signal.created_at)}</span>
      </div>

      <button
        onClick={handleSubscribe}
        disabled={subscribing}
        className={`w-full py-2 rounded-lg text-sm font-medium transition-all ${signal.is_free ? 'btn-success' : 'btn-primary'}`}
      >
        {subscribing ? 'Subscribing...' : signal.is_free ? 'Get Free Signal' : `Subscribe · $${signal.price_usd}/mo`}
      </button>
    </div>
  )
}
