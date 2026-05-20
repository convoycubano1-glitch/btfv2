import { useState, useRef, useEffect } from 'react'
import { Sparkles, Send, User, Bot, AlertTriangle } from 'lucide-react'
import api from '../services/api'
import { STRATEGY_TYPES } from '../utils/constants'
import LoadingSpinner from '../components/common/LoadingSpinner'

function Message({ msg }) {
  const isUser = msg.role === 'user'
  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${isUser ? 'bg-brand-500' : 'bg-surface-100'}`}>
        {isUser ? <User size={14} className="text-white" /> : <Bot size={14} className="text-brand-400" />}
      </div>
      <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm ${isUser ? 'bg-brand-500 text-white rounded-tr-sm' : 'bg-surface-100 text-gray-300 rounded-tl-sm'}`}>
        <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
        {msg.disclaimer && (
          <div className="flex items-center gap-1.5 mt-2 pt-2 border-t border-surface-200 text-xs text-trading-yellow">
            <AlertTriangle size={11} />
            <span>{msg.disclaimer}</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default function AIAssistant() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hi! I'm your AI trading assistant. I can explain strategies, help you optimize your bots, and answer questions about algorithmic trading.\n\nNote: I don't provide financial advice or trading signals. Always do your own research.",
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [suggestion, setSuggestion] = useState(null)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function sendMessage(e) {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMsg = { role: 'user', content: input }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const { data } = await api.post('/ai/chat', {
        message: input,
        context: messages.slice(-6).map((m) => ({ role: m.role, content: m.content })),
      })
      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: data.response,
        disclaimer: data.disclaimer,
      }])
    } catch (err) {
      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
      }])
    } finally {
      setLoading(false)
    }
  }

  async function getSuggestion() {
    try {
      const { data } = await api.get('/ai/strategy-suggestion?account_size=10000&risk_tolerance=medium&experience_level=beginner')
      setSuggestion(data)
    } catch {}
  }

  return (
    <div className="grid grid-cols-1 xl:grid-cols-4 gap-6 h-[calc(100vh-12rem)]">
      {/* Chat */}
      <div className="xl:col-span-3 flex flex-col card">
        <div className="flex items-center gap-3 mb-4 pb-4 border-b border-surface-200 shrink-0">
          <div className="p-2 bg-brand-500/10 rounded-xl">
            <Sparkles size={18} className="text-brand-400" />
          </div>
          <div>
            <h3 className="font-semibold text-white">AI Trading Assistant</h3>
            <p className="text-xs text-gray-400">Educational purposes only. Not financial advice.</p>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto space-y-4 pr-2">
          {messages.map((msg, i) => <Message key={i} msg={msg} />)}
          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-surface-100 flex items-center justify-center">
                <Bot size={14} className="text-brand-400" />
              </div>
              <div className="bg-surface-100 rounded-2xl rounded-tl-sm px-4 py-3">
                <LoadingSpinner size="sm" />
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <form onSubmit={sendMessage} className="flex gap-3 mt-4 pt-4 border-t border-surface-200 shrink-0">
          <input
            className="input flex-1"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about strategies, risk management, backtesting..."
            disabled={loading}
          />
          <button type="submit" disabled={loading || !input.trim()} className="btn-primary px-4">
            <Send size={16} />
          </button>
        </form>
      </div>

      {/* Sidebar */}
      <div className="xl:col-span-1 space-y-4">
        <div className="card">
          <h3 className="font-semibold text-white text-sm mb-3">Quick Questions</h3>
          <div className="space-y-2">
            {[
              'What is the EMA crossover strategy?',
              'How do I set a proper stop loss?',
              'Explain Sharpe ratio',
              'What is paper trading?',
              'How to avoid overfitting?',
            ].map((q) => (
              <button
                key={q}
                onClick={() => setInput(q)}
                className="w-full text-left text-xs text-gray-400 hover:text-white hover:bg-surface-100 p-2 rounded-lg transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
        </div>

        <div className="card">
          <h3 className="font-semibold text-white text-sm mb-3">Strategy Explainer</h3>
          <select className="input text-xs mb-2" onChange={(e) => {
            if (e.target.value) setInput(`Explain the ${e.target.value} strategy in detail`)
          }}>
            <option value="">Select strategy...</option>
            {STRATEGY_TYPES.filter(s => s.value !== 'custom').map((s) => (
              <option key={s.value} value={s.label}>{s.label}</option>
            ))}
          </select>
        </div>

        <div className="card text-xs text-gray-500 space-y-1">
          <p className="font-medium text-gray-400">Disclaimer</p>
          <p>AI responses are for educational purposes only. Never make trading decisions based solely on AI suggestions.</p>
        </div>
      </div>
    </div>
  )
}
