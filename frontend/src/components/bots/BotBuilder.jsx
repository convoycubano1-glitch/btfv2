import { useState, useEffect } from 'react'
import { useBot } from '../../hooks/useBot'
import Modal from '../common/Modal'
import { EXCHANGES, TIMEFRAMES, STRATEGY_TYPES, POPULAR_PAIRS } from '../../utils/constants'
import api from '../../services/api'
import toast from 'react-hot-toast'

const STEPS = ['Strategy', 'Symbol & Timeframe', 'Risk Settings', 'Review']

const DEFAULTS = {
  name: '',
  strategy_type: 'ema_crossover',
  symbol: 'BTC/USDT',
  timeframe: '1h',
  mode: 'paper',
  exchange_connection_id: '',
  max_position_size_pct: 0.02,
  stop_loss_pct: 0.02,
  take_profit_pct: 0.04,
  max_open_trades: 1,
  max_daily_loss_pct: 0.05,
  parameters: {},
}

export default function BotBuilder({ isOpen, onClose }) {
  const { addBot } = useBot()
  const [step, setStep] = useState(0)
  const [form, setForm] = useState(DEFAULTS)
  const [exchanges, setExchanges] = useState([])
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (isOpen) {
      api.get('/exchanges/').then(({ data }) => setExchanges(data)).catch(() => {})
      setStep(0)
      setForm(DEFAULTS)
    }
  }, [isOpen])

  function update(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  async function handleSubmit() {
    setSubmitting(true)
    try {
      // Build strategy_id if needed — for now pass type in parameters
      const payload = {
        ...form,
        exchange_connection_id: form.exchange_connection_id || undefined,
        parameters: { strategy_type: form.strategy_type },
      }
      const result = await addBot(payload)
      if (!result.error) onClose()
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create New Bot" size="lg">
      {/* Step indicator */}
      <div className="flex items-center gap-2 mb-6">
        {STEPS.map((s, i) => (
          <div key={s} className="flex items-center gap-2 flex-1 last:flex-none">
            <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-colors ${i <= step ? 'bg-brand-500 text-white' : 'bg-surface-100 text-gray-400'}`}>
              {i < step ? '✓' : i + 1}
            </div>
            <span className={`text-xs ${i === step ? 'text-white' : 'text-gray-500'} hidden sm:block`}>{s}</span>
            {i < STEPS.length - 1 && <div className={`flex-1 h-px ${i < step ? 'bg-brand-500' : 'bg-surface-200'}`} />}
          </div>
        ))}
      </div>

      {/* Step 0 — Strategy */}
      {step === 0 && (
        <div className="space-y-4">
          <div>
            <label className="label">Bot Name *</label>
            <input className="input" value={form.name} onChange={(e) => update('name', e.target.value)} placeholder="e.g. BTC EMA Bot" />
          </div>
          <div>
            <label className="label">Strategy *</label>
            <select className="input" value={form.strategy_type} onChange={(e) => update('strategy_type', e.target.value)}>
              {STRATEGY_TYPES.filter(s => s.value !== 'custom').map((s) => (
                <option key={s.value} value={s.value}>{s.label} ({s.category})</option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Trading Mode</label>
            <div className="flex gap-3">
              {['paper', 'live'].map((m) => (
                <button
                  key={m}
                  onClick={() => update('mode', m)}
                  className={`flex-1 py-2 rounded-lg text-sm font-medium border transition-colors capitalize ${form.mode === m ? 'bg-brand-500 text-white border-brand-500' : 'bg-surface-100 text-gray-400 border-surface-200 hover:text-white'}`}
                >
                  {m === 'paper' ? '📄 Paper Trading' : '⚡ Live Trading'}
                </button>
              ))}
            </div>
            {form.mode === 'live' && (
              <p className="text-xs text-trading-yellow mt-2">⚠️ Live trading uses real funds. Ensure you understand the risks.</p>
            )}
          </div>
        </div>
      )}

      {/* Step 1 — Symbol & Timeframe */}
      {step === 1 && (
        <div className="space-y-4">
          <div>
            <label className="label">Trading Pair *</label>
            <input className="input" value={form.symbol} onChange={(e) => update('symbol', e.target.value.toUpperCase())} placeholder="BTC/USDT" />
            <div className="flex flex-wrap gap-1.5 mt-2">
              {POPULAR_PAIRS.map((p) => (
                <button key={p} onClick={() => update('symbol', p)} className={`text-xs px-2 py-1 rounded border transition-colors ${form.symbol === p ? 'border-brand-500 text-brand-400' : 'border-surface-200 text-gray-400 hover:text-white'}`}>
                  {p}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="label">Timeframe *</label>
            <div className="grid grid-cols-5 gap-2">
              {TIMEFRAMES.map((tf) => (
                <button key={tf.value} onClick={() => update('timeframe', tf.value)} className={`py-2 rounded-lg text-xs font-medium border transition-colors ${form.timeframe === tf.value ? 'bg-brand-500 text-white border-brand-500' : 'bg-surface-100 text-gray-400 border-surface-200 hover:text-white'}`}>
                  {tf.value}
                </button>
              ))}
            </div>
          </div>
          {form.mode === 'live' && (
            <div>
              <label className="label">Exchange Connection</label>
              <select className="input" value={form.exchange_connection_id} onChange={(e) => update('exchange_connection_id', e.target.value)}>
                <option value="">Select exchange...</option>
                {exchanges.map((ex) => (
                  <option key={ex.id} value={ex.id}>{ex.label} ({ex.exchange_id})</option>
                ))}
              </select>
            </div>
          )}
        </div>
      )}

      {/* Step 2 — Risk */}
      {step === 2 && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Position Size (%)</label>
              <input type="number" className="input" min="0.1" max="10" step="0.1" value={(form.max_position_size_pct * 100).toFixed(1)} onChange={(e) => update('max_position_size_pct', parseFloat(e.target.value) / 100)} />
              <p className="text-xs text-gray-500 mt-1">Max: 10%</p>
            </div>
            <div>
              <label className="label">Stop Loss (%)</label>
              <input type="number" className="input" min="0.1" max="10" step="0.1" value={(form.stop_loss_pct * 100).toFixed(1)} onChange={(e) => update('stop_loss_pct', parseFloat(e.target.value) / 100)} />
            </div>
            <div>
              <label className="label">Take Profit (%)</label>
              <input type="number" className="input" min="0.1" max="50" step="0.1" value={(form.take_profit_pct * 100).toFixed(1)} onChange={(e) => update('take_profit_pct', parseFloat(e.target.value) / 100)} />
            </div>
            <div>
              <label className="label">Max Daily Loss (%)</label>
              <input type="number" className="input" min="1" max="20" step="0.5" value={(form.max_daily_loss_pct * 100).toFixed(1)} onChange={(e) => update('max_daily_loss_pct', parseFloat(e.target.value) / 100)} />
              <p className="text-xs text-gray-500 mt-1">Max: 20%</p>
            </div>
          </div>
          <div>
            <label className="label">Max Open Trades</label>
            <input type="number" className="input" min="1" max="10" value={form.max_open_trades} onChange={(e) => update('max_open_trades', parseInt(e.target.value))} />
          </div>
          <p className="text-xs text-trading-yellow p-3 bg-trading-yellow/10 rounded-lg">
            ⚠️ Risk Disclaimer: These settings directly affect your capital exposure. Conservative settings recommended.
          </p>
        </div>
      )}

      {/* Step 3 — Review */}
      {step === 3 && (
        <div className="space-y-3">
          <div className="bg-surface-100 rounded-xl p-4 space-y-2.5 text-sm">
            {[
              ['Name', form.name],
              ['Strategy', STRATEGY_TYPES.find(s => s.value === form.strategy_type)?.label],
              ['Symbol', form.symbol],
              ['Timeframe', form.timeframe],
              ['Mode', form.mode.toUpperCase()],
              ['Stop Loss', `${(form.stop_loss_pct * 100).toFixed(1)}%`],
              ['Take Profit', `${(form.take_profit_pct * 100).toFixed(1)}%`],
              ['Position Size', `${(form.max_position_size_pct * 100).toFixed(1)}%`],
              ['Max Daily Loss', `${(form.max_daily_loss_pct * 100).toFixed(1)}%`],
            ].map(([k, v]) => (
              <div key={k} className="flex justify-between">
                <span className="text-gray-400">{k}</span>
                <span className="text-white font-medium">{v}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="flex justify-between mt-6 pt-4 border-t border-surface-200">
        <button onClick={step === 0 ? onClose : () => setStep(step - 1)} className="btn-secondary">
          {step === 0 ? 'Cancel' : '← Back'}
        </button>
        {step < STEPS.length - 1 ? (
          <button
            onClick={() => setStep(step + 1)}
            disabled={step === 0 && !form.name}
            className="btn-primary"
          >
            Next →
          </button>
        ) : (
          <button onClick={handleSubmit} disabled={submitting} className="btn-primary">
            {submitting ? 'Creating...' : '✓ Create Bot'}
          </button>
        )}
      </div>
    </Modal>
  )
}
