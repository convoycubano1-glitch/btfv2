import { useState } from 'react'
import { AlertTriangle, X } from 'lucide-react'

export default function Disclaimer() {
  const [dismissed, setDismissed] = useState(
    () => sessionStorage.getItem('disclaimer_dismissed') === '1'
  )

  if (dismissed) return null

  return (
    <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50 w-full max-w-2xl px-4">
      <div className="flex items-start gap-3 bg-trading-yellow/10 border border-trading-yellow/30 rounded-xl p-4">
        <AlertTriangle size={18} className="text-trading-yellow shrink-0 mt-0.5" />
        <div className="flex-1 min-w-0">
          <p className="text-xs text-gray-300 leading-relaxed">
            <span className="font-semibold text-trading-yellow">Risk Disclaimer: </span>
            Algorithmic trading involves significant risk. Past performance is not indicative of future results.
            Never trade with money you cannot afford to lose. This platform is for educational purposes.
            Always start with paper trading mode.
          </p>
        </div>
        <button
          onClick={() => {
            sessionStorage.setItem('disclaimer_dismissed', '1')
            setDismissed(true)
          }}
          className="text-gray-400 hover:text-white shrink-0"
        >
          <X size={16} />
        </button>
      </div>
    </div>
  )
}
