import { useState, useEffect } from 'react'
import { Cpu, ChevronDown, ChevronUp } from 'lucide-react'
import Badge from '../components/common/Badge'
import { STRATEGY_TYPES } from '../utils/constants'
import api from '../services/api'
import { PageLoader } from '../components/common/LoadingSpinner'

const RISK_VARIANT = { Low: 'green', Medium: 'yellow', High: 'red', Variable: 'blue' }

function StrategyItem({ strategy, registry }) {
  const [open, setOpen] = useState(false)
  const info = STRATEGY_TYPES.find((s) => s.value === strategy.type) || {}

  return (
    <div className="card hover:border-surface-300 transition-colors">
      <div className="flex items-start justify-between cursor-pointer" onClick={() => setOpen(!open)}>
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-brand-500/10 rounded-xl text-brand-400">
            <Cpu size={18} />
          </div>
          <div>
            <h3 className="font-semibold text-white">{strategy.name}</h3>
            <p className="text-xs text-gray-400 mt-0.5">{strategy.description?.slice(0, 80)}...</p>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0 ml-4">
          <Badge variant="blue">{info.category || 'Strategy'}</Badge>
          <Badge variant={RISK_VARIANT[strategy.risk_level] || 'gray'}>{strategy.risk_level} Risk</Badge>
          {open ? <ChevronUp size={16} className="text-gray-400" /> : <ChevronDown size={16} className="text-gray-400" />}
        </div>
      </div>

      {open && (
        <div className="mt-4 pt-4 border-t border-surface-200 space-y-3">
          <p className="text-sm text-gray-300">{strategy.description}</p>
          {strategy.default_parameters && Object.keys(strategy.default_parameters).length > 0 && (
            <div>
              <p className="text-xs font-medium text-gray-400 mb-2">Default Parameters</p>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(strategy.default_parameters).map(([k, v]) => (
                  <div key={k} className="bg-surface-100 rounded-lg px-3 py-2 flex justify-between text-xs">
                    <span className="text-gray-400">{k}</span>
                    <span className="text-white font-mono">{String(v)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default function Strategies() {
  const [registry, setRegistry] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/strategies/built-in').then(({ data }) => {
      setRegistry(Object.values(data))
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white">Strategy Library</h2>
        <p className="text-sm text-gray-400 mt-1">12 built-in algorithmic strategies ready to deploy</p>
      </div>

      {loading ? <PageLoader /> : (
        <div className="space-y-3">
          {registry.map((s) => (
            <StrategyItem key={s.type} strategy={s} registry={registry} />
          ))}
        </div>
      )}
    </div>
  )
}
