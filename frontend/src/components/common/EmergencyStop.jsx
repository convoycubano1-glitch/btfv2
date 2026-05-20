import { useState } from 'react'
import { OctagonX } from 'lucide-react'
import { useAuth } from '../../hooks/useAuth'
import toast from 'react-hot-toast'
import clsx from 'clsx'

export default function EmergencyStop({ compact = false }) {
  const { triggerEmergencyStop, user } = useAuth()
  const [confirming, setConfirming] = useState(false)

  async function handleEmergencyStop() {
    if (!confirming) {
      setConfirming(true)
      setTimeout(() => setConfirming(false), 3000)
      return
    }
    try {
      await triggerEmergencyStop()
      toast.error('🚨 Emergency Stop activated — all bots paused', { duration: 8000 })
      setConfirming(false)
    } catch {
      toast.error('Failed to trigger emergency stop')
    }
  }

  if (compact) {
    return (
      <button
        onClick={handleEmergencyStop}
        className={clsx(
          'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200',
          confirming
            ? 'bg-trading-red text-white animate-pulse'
            : user?.emergency_stop_active
            ? 'bg-trading-red/20 text-trading-red border border-trading-red/30'
            : 'bg-trading-red/10 text-trading-red hover:bg-trading-red hover:text-white'
        )}
        title={confirming ? 'Click again to confirm' : 'Emergency Stop'}
      >
        <OctagonX size={14} />
        {confirming ? 'Confirm?' : user?.emergency_stop_active ? 'STOPPED' : 'E-Stop'}
      </button>
    )
  }

  return (
    <div className="card border-trading-red/30">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-white flex items-center gap-2">
            <OctagonX size={18} className="text-trading-red" />
            Emergency Stop
          </h3>
          <p className="text-sm text-gray-400 mt-1">
            Immediately pause all active trading bots. Use only in emergencies.
          </p>
        </div>
        <button
          onClick={handleEmergencyStop}
          className={clsx(
            'px-6 py-3 rounded-xl font-bold text-sm transition-all duration-200',
            confirming
              ? 'bg-trading-red text-white scale-105 shadow-lg shadow-trading-red/30 animate-pulse'
              : 'bg-trading-red/10 text-trading-red border border-trading-red/30 hover:bg-trading-red hover:text-white'
          )}
        >
          {confirming ? '⚠️ CLICK TO CONFIRM' : '🛑 STOP ALL BOTS'}
        </button>
      </div>
    </div>
  )
}
