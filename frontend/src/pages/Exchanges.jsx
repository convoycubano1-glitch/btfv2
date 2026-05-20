import { useState, useEffect } from 'react'
import { Plus, Plug2, CheckCircle, XCircle, Trash2, RefreshCw } from 'lucide-react'
import Modal from '../components/common/Modal'
import Badge from '../components/common/Badge'
import api from '../services/api'
import { EXCHANGES } from '../utils/constants'
import { formatRelative } from '../utils/formatters'
import toast from 'react-hot-toast'

function ExchangeModal({ isOpen, onClose, onCreated }) {
  const [form, setForm] = useState({ exchange_id: 'binance', label: '', api_key: '', api_secret: '', passphrase: '', is_testnet: true })
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    try {
      await api.post('/exchanges/', form)
      toast.success('Exchange connected!')
      onCreated()
      onClose()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Connection failed')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Connect Exchange">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="label">Exchange</label>
          <select className="input" value={form.exchange_id} onChange={(e) => setForm({ ...form, exchange_id: e.target.value })}>
            {EXCHANGES.map((ex) => <option key={ex.id} value={ex.id}>{ex.logo} {ex.name}</option>)}
          </select>
        </div>
        <div>
          <label className="label">Label (e.g. "My Binance")</label>
          <input className="input" value={form.label} onChange={(e) => setForm({ ...form, label: e.target.value })} required placeholder="Main Account" />
        </div>
        <div>
          <label className="label">API Key</label>
          <input className="input font-mono text-xs" value={form.api_key} onChange={(e) => setForm({ ...form, api_key: e.target.value })} required placeholder="API key" autoComplete="off" />
        </div>
        <div>
          <label className="label">API Secret</label>
          <input type="password" className="input font-mono text-xs" value={form.api_secret} onChange={(e) => setForm({ ...form, api_secret: e.target.value })} required placeholder="API secret" autoComplete="off" />
        </div>
        {['kucoin', 'okx', 'coinbase'].includes(form.exchange_id) && (
          <div>
            <label className="label">Passphrase</label>
            <input type="password" className="input font-mono text-xs" value={form.passphrase} onChange={(e) => setForm({ ...form, passphrase: e.target.value })} />
          </div>
        )}
        <label className="flex items-center gap-3 cursor-pointer">
          <input type="checkbox" checked={form.is_testnet} onChange={(e) => setForm({ ...form, is_testnet: e.target.checked })} className="w-4 h-4 rounded" />
          <div>
            <span className="text-sm text-white">Use Testnet/Sandbox</span>
            <p className="text-xs text-gray-400">Recommended for testing. No real funds.</p>
          </div>
        </label>
        <div className="bg-surface-100 rounded-lg p-3 text-xs text-gray-400 space-y-1">
          <p className="font-medium text-white">Security Notice:</p>
          <p>• API keys are encrypted with AES-256 before storage</p>
          <p>• Withdrawal permissions are permanently disabled</p>
          <p>• Only read and trade permissions are used</p>
        </div>
        <button type="submit" disabled={submitting} className="btn-primary w-full">
          {submitting ? 'Verifying connection...' : 'Connect Exchange'}
        </button>
      </form>
    </Modal>
  )
}

export default function Exchanges() {
  const [connections, setConnections] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [verifying, setVerifying] = useState(null)

  async function load() {
    const { data } = await api.get('/exchanges/')
    setConnections(data)
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  async function verify(id) {
    setVerifying(id)
    try {
      const { data } = await api.post(`/exchanges/${id}/verify`)
      toast.success('Connection verified!')
      load()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Verification failed')
    } finally {
      setVerifying(null)
    }
  }

  async function remove(id) {
    try {
      await api.delete(`/exchanges/${id}`)
      setConnections(connections.filter((c) => c.id !== id))
      toast.success('Exchange removed')
    } catch {
      toast.error('Failed to remove exchange')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Exchange Connections</h2>
          <p className="text-gray-400 text-sm mt-1">Connect your exchange API keys. Withdrawal permissions are always disabled.</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-primary flex items-center gap-2">
          <Plus size={16} /> Connect Exchange
        </button>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2].map((i) => <div key={i} className="skeleton h-32 rounded-xl" />)}
        </div>
      ) : connections.length === 0 ? (
        <div className="card text-center py-12">
          <Plug2 size={40} className="mx-auto text-gray-600 mb-3" />
          <h3 className="font-semibold text-white mb-1">No exchanges connected</h3>
          <p className="text-gray-400 text-sm mb-4">Connect a testnet account to start paper trading</p>
          <button onClick={() => setShowModal(true)} className="btn-primary">Connect Exchange</button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {connections.map((conn) => {
            const exchange = EXCHANGES.find((ex) => ex.id === conn.exchange_id)
            return (
              <div key={conn.id} className="card hover:border-surface-300 transition-colors">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-surface-100 rounded-xl flex items-center justify-center text-xl">
                      {exchange?.logo || '🔗'}
                    </div>
                    <div>
                      <h3 className="font-semibold text-white">{conn.label}</h3>
                      <p className="text-xs text-gray-400 capitalize">{exchange?.name || conn.exchange_id}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Badge variant={conn.status === 'active' ? 'green' : conn.status === 'error' ? 'red' : 'gray'}>
                      {conn.status}
                    </Badge>
                    {conn.is_testnet && <Badge variant="yellow">Testnet</Badge>}
                  </div>
                </div>
                <div className="text-xs text-gray-500 mb-4">
                  {conn.last_verified_at ? `Verified ${formatRelative(conn.last_verified_at)}` : 'Never verified'}
                  {conn.error_message && <p className="text-trading-red mt-1">{conn.error_message}</p>}
                </div>
                <div className="flex gap-2">
                  <button onClick={() => verify(conn.id)} disabled={verifying === conn.id} className="btn-secondary flex-1 flex items-center justify-center gap-2 text-xs py-1.5">
                    <RefreshCw size={13} className={verifying === conn.id ? 'animate-spin' : ''} />
                    Verify
                  </button>
                  <button onClick={() => remove(conn.id)} className="btn-secondary text-trading-red hover:bg-trading-red/10 text-xs py-1.5 px-3">
                    <Trash2 size={13} />
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}

      <ExchangeModal isOpen={showModal} onClose={() => setShowModal(false)} onCreated={load} />
    </div>
  )
}
