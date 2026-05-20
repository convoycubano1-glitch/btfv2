import { format, formatDistanceToNow, parseISO } from 'date-fns'

export function formatCurrency(value, decimals = 2, currency = 'USD') {
  if (value === null || value === undefined) return '—'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value)
}

export function formatPct(value, decimals = 2) {
  if (value === null || value === undefined) return '—'
  const formatted = value.toFixed(decimals)
  const sign = value > 0 ? '+' : ''
  return `${sign}${formatted}%`
}

export function formatNumber(value, decimals = 4) {
  if (value === null || value === undefined) return '—'
  if (Math.abs(value) >= 1_000_000) return `${(value / 1_000_000).toFixed(2)}M`
  if (Math.abs(value) >= 1_000) return `${(value / 1_000).toFixed(2)}K`
  return value.toFixed(decimals)
}

export function formatDate(dateStr, fmt = 'MMM d, yyyy') {
  if (!dateStr) return '—'
  try {
    const date = typeof dateStr === 'string' ? parseISO(dateStr) : dateStr
    return format(date, fmt)
  } catch {
    return '—'
  }
}

export function formatRelative(dateStr) {
  if (!dateStr) return '—'
  try {
    const date = typeof dateStr === 'string' ? parseISO(dateStr) : dateStr
    return formatDistanceToNow(date, { addSuffix: true })
  } catch {
    return '—'
  }
}

export function formatDatetime(dateStr) {
  return formatDate(dateStr, 'MMM d, yyyy HH:mm')
}

export function pnlClass(value) {
  if (!value) return 'text-gray-400'
  return value > 0 ? 'text-trading-green' : 'text-trading-red'
}

export function statusColor(status) {
  const map = {
    active: 'badge-green',
    running: 'badge-green',
    completed: 'badge-blue',
    paused: 'badge-yellow',
    stopped: 'text-gray-400',
    error: 'badge-red',
    failed: 'badge-red',
    draft: 'text-gray-400',
    open: 'badge-blue',
    closed: 'text-gray-400',
    live: 'badge-green',
    paper: 'badge-yellow',
    free: 'badge-green',
    pro: 'badge-blue',
    elite: 'text-purple-400 bg-purple-400/10 text-xs font-medium px-2 py-0.5 rounded-full',
  }
  return map[status] || 'text-gray-400'
}
