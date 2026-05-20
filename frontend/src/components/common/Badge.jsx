import clsx from 'clsx'

const VARIANTS = {
  green: 'bg-trading-green/10 text-trading-green border-trading-green/20',
  red: 'bg-trading-red/10 text-trading-red border-trading-red/20',
  yellow: 'bg-trading-yellow/10 text-trading-yellow border-trading-yellow/20',
  blue: 'bg-trading-blue/10 text-trading-blue border-trading-blue/20',
  purple: 'bg-purple-400/10 text-purple-400 border-purple-400/20',
  gray: 'bg-surface-100 text-gray-400 border-surface-200',
}

export default function Badge({ children, variant = 'gray', className = '' }) {
  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-full border',
        VARIANTS[variant],
        className
      )}
    >
      {children}
    </span>
  )
}
