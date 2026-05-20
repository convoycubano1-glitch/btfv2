import { useState, useEffect } from 'react'
import { ShoppingBag, Search } from 'lucide-react'
import SignalCard from '../components/marketplace/SignalCard'
import api from '../services/api'
import { PageLoader } from '../components/common/LoadingSpinner'

export default function Marketplace() {
  const [signals, setSignals] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [freeOnly, setFreeOnly] = useState(false)

  async function load() {
    const params = new URLSearchParams()
    if (search) params.set('symbol', search.toUpperCase())
    if (freeOnly) params.set('free_only', 'true')
    const { data } = await api.get(`/marketplace/?${params}`)
    setSignals(data)
    setLoading(false)
  }

  useEffect(() => { load() }, [search, freeOnly])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white">Signal Marketplace</h2>
        <p className="text-sm text-gray-400 mt-1">
          Professional trading signals from verified traders. ⚠️ Always do your own research.
        </p>
      </div>

      {/* Filters */}
      <div className="flex gap-3 flex-wrap">
        <div className="relative flex-1 min-w-[200px]">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            className="input pl-9"
            placeholder="Filter by symbol (BTC, ETH...)"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <label className="flex items-center gap-2 cursor-pointer card-sm py-2">
          <input type="checkbox" checked={freeOnly} onChange={(e) => setFreeOnly(e.target.checked)} className="w-4 h-4 rounded" />
          <span className="text-sm text-white">Free signals only</span>
        </label>
      </div>

      {loading ? (
        <PageLoader />
      ) : signals.length === 0 ? (
        <div className="card text-center py-12">
          <ShoppingBag size={40} className="mx-auto text-gray-600 mb-3" />
          <h3 className="font-semibold text-white">No signals available</h3>
          <p className="text-gray-400 text-sm mt-1">Check back soon or adjust your filters</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {signals.map((s) => (
            <SignalCard key={s.id} signal={s} onSubscribe={load} />
          ))}
        </div>
      )}
    </div>
  )
}
