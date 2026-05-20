import { useState, useEffect } from 'react'
import { Plus, Signal, TrendingUp, TrendingDown, Eye, Trash2 } from 'lucide-react'
import Modal from '../components/common/Modal'
import Badge from '../components/common/Badge'
import api from '../services/api'
import { TIMEFRAMES, POPULAR_PAIRS } from '../utils/constants'
import { formatCurrency, formatRelative } from '../utils/formatters'
import toast from 'react-hot-toast'
import { PageLoader } from '../components/common/LoadingSpinner'

function CreateSignalModal({ isOpen, onClose, onCreated }) {
  const [form, setForm] = useState({
    title: '', symbol: 'BTC/USDT', signal_type: 'buy', timeframe: '1h',
    entry_price: '', stop_loss: '', take_profit_1: '', take_profit_2: '',
    description: '', is_free: true, price_usd: 0,
  })
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    try {
      const payload = { ...form }
      ;['entry_price', 'stop_loss', 'take_profit_1', 'take_profit_2', 'price_usd'].forEach((k) => {
        if (payload[k]) payload[k] = parseFloat(payload[k])
      })
      await api.post('/signals/', payload)
      toast.success('Signal created!')
      onCreated()
      onClose()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create signal')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create Signal" size="lg">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="label">Title *</label>
          <input className="input" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required placeholder="BTC Long — Strong support bounce" />
        </div>
        <div className="grid grid-cols-3 gap-3">
          <div>
            <label className="label">Symbol *</label>
            <input className="input" value={form.symbol} onChange={(e) => setForm({ ...form, symbol: e.target.value.toUpperCase() })} required />
          </div>
          <div>
            <label className="label">Direction</label>
            <select className="input" value={form.signal_type} onChange={(e) => setForm({ ...form, signal_type: e.target.value })}>
              <option value="buy">Long (BUY)</option>
              <option value="sell">Short (SELL)</option>
            </select>
          </div>
          <div>
            <label className="label">Timeframe</label>
            <select className="input" value={form.timeframe} onChange={(e) => setForm({ ...form, timeframe: e.target.value })}>
              {TIMEFRAMES.map((tf) => <option key={tf.value} value={tf.value}>{tf.label}</option>)}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">Entry Price *</label>
            <input type="number" step="any" className="input" value={form.entry_price} onChange={(e) => setForm({ ...form, entry_price: e.target.value })} required />
          </div>
          <div>
            <label className="label">Stop Loss *</label>
            <input type="number" step="any" className="input" value={form.stop_loss} onChange={(e) => setForm({ ...form, stop_loss: e.target.value })} required />
          </div>
          <div>
            <label className="label">Take Profit 1 *</label>
            <input type="number" step="any" className="input" value={form.take_profit_1} onChange={(e) => setForm({ ...form, take_profit_1: e.target.value })} required />
          </div>
          <div>
            <label className="label">Take Profit 2</label>
            <input type="number" step="any" className="input" value={form.take_profit_2} onChange={(e) => setForm({ ...form, take_profit_2: e.target.value })} />
          </div>
        </div>
        <div>
          <label className="label">Description</label>
          <textarea className="input resize-none h-20" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Explain your analysis..." />
        </div>
        <div className="flex gap-6">
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" checked={form.is_free} onChange={(e) => setForm({ ...form, is_free: e.target.checked })} className="w-4 h-4 rounded" />
            <span className="text-sm text-white">Free signal</span>
          </label>
          {!form.is_free && (
            <div>
              <label className="label">Price (USD/mo)</label>
              <input type="number" className="input w-28" value={form.price_usd} onChange={(e) => setForm({ ...form, price_usd: e.target.value })} min="1" />
            </div>
          )}
        </div>
        <button type="submit" disabled={submitting} className="btn-primary w-full">
          {submitting ? 'Creating...' : 'Create Signal'}
        </button>
      </form>
    </Modal>
  )
}

export default function Signals() {
  const [signals, setSignals] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)

  async function load() {
    const { data } = await api.get('/signals/my')
    setSignals(data)
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  async function publish(id) {
    try {
      await api.patch(`/signals/${id}/publish`)
      toast.success('Signal published!')
      load()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to publish')
    }
  }

  async function remove(id) {
    try {
      await api.delete(`/signals/${id}`)
      setSignals(signals.filter((s) => s.id !== id))
      toast.success('Signal deleted')
    } catch { toast.error('Failed to delete') }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">My Signals</h2>
          <p className="text-sm text-gray-400 mt-1">Create and publish trading signals to the marketplace</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-primary flex items-center gap-2">
          <Plus size={16} /> New Signal
        </button>
      </div>

      {loading ? <PageLoader /> : signals.length === 0 ? (
        <div className="card text-center py-12">
          <Signal size={40} className="mx-auto text-gray-600 mb-3" />
          <h3 className="font-semibold text-white">No signals yet</h3>
          <p className="text-gray-400 text-sm mb-4">Create your first signal and share it with the community</p>
          <button onClick={() => setShowModal(true)} className="btn-primary">Create Signal</button>
        </div>
      ) : (
        <div className="space-y-3">
          {signals.map((signal) => (
            <div key={signal.id} className="card hover:border-surface-300 transition-colors">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {signal.signal_type === 'buy' ? <TrendingUp size={18} className="text-trading-green" /> : <TrendingDown size={18} className="text-trading-red" />}
                  <div>
                    <p className="font-semibold text-white">{signal.title}</p>
                    <p className="text-xs text-gray-400">{signal.symbol} · {signal.timeframe} · Entry: {formatCurrency(signal.entry_price)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={signal.is_published ? 'green' : 'gray'}>{signal.is_published ? 'Published' : 'Draft'}</Badge>
                  <Badge variant={signal.is_free ? 'green' : 'blue'}>{signal.is_free ? 'Free' : `$${signal.price_usd}/mo`}</Badge>
                  {!signal.is_published && (
                    <button onClick={() => publish(signal.id)} className="btn-primary text-xs py-1 px-3">Publish</button>
                  )}
                  <button onClick={() => remove(signal.id)} className="p-2 text-gray-400 hover:text-trading-red hover:bg-trading-red/10 rounded-lg transition-colors">
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <CreateSignalModal isOpen={showModal} onClose={() => setShowModal(false)} onCreated={load} />
    </div>
  )
}
