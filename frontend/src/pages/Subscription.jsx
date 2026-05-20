import { useState, useEffect } from 'react'
import { CreditCard, Check, Zap, Crown } from 'lucide-react'
import api from '../services/api'
import { PLAN_FEATURES } from '../utils/constants'
import { formatDate } from '../utils/formatters'
import Badge from '../components/common/Badge'
import toast from 'react-hot-toast'
import { PageLoader } from '../components/common/LoadingSpinner'

const PLAN_ICONS = { free: Zap, pro: CreditCard, elite: Crown }
const PLAN_VARIANT = { free: 'gray', pro: 'blue', elite: 'purple' }

export default function Subscription() {
  const [subscription, setSubscription] = useState(null)
  const [loading, setLoading] = useState(true)
  const [checkingOut, setCheckingOut] = useState(null)

  useEffect(() => {
    api.get('/subscriptions/my').then(({ data }) => setSubscription(data)).finally(() => setLoading(false))
  }, [])

  async function checkout(plan) {
    setCheckingOut(plan)
    try {
      const { data } = await api.post('/subscriptions/checkout', { plan })
      window.location.href = data.url
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Checkout failed')
      setCheckingOut(null)
    }
  }

  async function cancel() {
    try {
      await api.post('/subscriptions/cancel')
      toast.success('Subscription cancelled')
      const { data } = await api.get('/subscriptions/my')
      setSubscription(data)
    } catch {
      toast.error('Failed to cancel')
    }
  }

  const currentPlan = subscription?.plan || 'free'

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white">Subscription Plans</h2>
        <p className="text-sm text-gray-400 mt-1">Upgrade to unlock live trading, more bots, and AI assistance</p>
      </div>

      {loading ? <PageLoader /> : (
        <>
          {/* Current subscription info */}
          {subscription && (
            <div className="card border-brand-500/20 bg-brand-500/5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Current Plan</p>
                  <p className="text-lg font-bold text-white capitalize flex items-center gap-2 mt-1">
                    {currentPlan}
                    <Badge variant={PLAN_VARIANT[currentPlan]}>{currentPlan}</Badge>
                  </p>
                  {subscription.current_period_end && (
                    <p className="text-xs text-gray-400 mt-1">
                      {subscription.cancel_at_period_end ? 'Cancels' : 'Renews'} {formatDate(subscription.current_period_end)}
                    </p>
                  )}
                </div>
                {currentPlan !== 'free' && !subscription.cancel_at_period_end && (
                  <button onClick={cancel} className="btn-secondary text-xs text-trading-red hover:bg-trading-red/10">
                    Cancel Plan
                  </button>
                )}
              </div>
            </div>
          )}

          {/* Plan cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {Object.entries(PLAN_FEATURES).map(([planKey, plan]) => {
              const Icon = PLAN_ICONS[planKey]
              const isActive = currentPlan === planKey
              const isUpgrade = ['free', 'pro'].indexOf(planKey) > ['free', 'pro'].indexOf(currentPlan)

              return (
                <div key={planKey} className={`card flex flex-col ${isActive ? 'border-brand-500/40 bg-brand-500/5' : ''} ${planKey === 'pro' ? 'relative' : ''}`}>
                  {planKey === 'pro' && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-brand-500 text-white text-xs font-semibold px-3 py-1 rounded-full">
                      Most Popular
                    </div>
                  )}
                  <div className="flex items-center gap-3 mb-4">
                    <div className={`p-2.5 rounded-xl ${planKey === 'elite' ? 'bg-purple-500/10' : planKey === 'pro' ? 'bg-brand-500/10' : 'bg-surface-100'}`}>
                      <Icon size={20} className={plan.color} />
                    </div>
                    <div>
                      <h3 className={`font-bold text-lg ${plan.color}`}>{plan.name}</h3>
                      <p className="text-white font-semibold">
                        {plan.price === 0 ? 'Free' : `$${plan.price}/mo`}
                      </p>
                    </div>
                  </div>

                  <ul className="space-y-2 flex-1 mb-6">
                    {[
                      `${plan.bots === -1 ? 'Unlimited' : plan.bots} bot${plan.bots !== 1 ? 's' : ''}`,
                      `${plan.backtests === -1 ? 'Unlimited' : plan.backtests} backtests/mo`,
                      plan.live_trading ? 'Live trading' : 'Paper trading only',
                      plan.signals ? 'Signal marketplace' : 'No signal access',
                      plan.ai_assistant ? 'AI Assistant' : 'No AI access',
                    ].map((feat) => (
                      <li key={feat} className="flex items-center gap-2 text-sm">
                        <Check size={14} className={plan.price === 0 && !feat.includes('Unlimited') ? 'text-gray-500' : 'text-trading-green'} />
                        <span className={feat.includes('only') || feat.includes('No ') ? 'text-gray-500' : 'text-gray-300'}>{feat}</span>
                      </li>
                    ))}
                  </ul>

                  {isActive ? (
                    <button disabled className="btn-secondary w-full opacity-60 cursor-default">Current Plan</button>
                  ) : planKey === 'free' ? (
                    <button disabled className="btn-secondary w-full opacity-50 cursor-default">Downgrade</button>
                  ) : (
                    <button
                      onClick={() => checkout(planKey)}
                      disabled={checkingOut === planKey}
                      className={planKey === 'elite' ? 'w-full py-2.5 rounded-xl font-semibold text-sm bg-gradient-to-r from-purple-600 to-brand-500 text-white hover:opacity-90 transition-opacity' : 'btn-primary w-full py-2.5'}
                    >
                      {checkingOut === planKey ? 'Redirecting...' : `Upgrade to ${plan.name}`}
                    </button>
                  )}
                </div>
              )
            })}
          </div>
        </>
      )}
    </div>
  )
}
