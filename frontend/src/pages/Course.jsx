import { useState } from 'react'
import { GraduationCap, BookOpen, CheckCircle, Clock, ChevronRight, Play } from 'lucide-react'

const MODULES = [
  {
    id: 1, title: 'Algorithmic Trading Fundamentals',
    lessons: [
      { id: 'l1', title: 'What is Algorithmic Trading?', duration: '8 min', free: true },
      { id: 'l2', title: 'Market Microstructure Basics', duration: '12 min', free: true },
      { id: 'l3', title: 'Order Types and Execution', duration: '15 min', free: false },
      { id: 'l4', title: 'Risk vs Reward Fundamentals', duration: '10 min', free: false },
    ]
  },
  {
    id: 2, title: 'Technical Indicators',
    lessons: [
      { id: 'l5', title: 'Moving Averages (SMA, EMA)', duration: '14 min', free: true },
      { id: 'l6', title: 'Momentum Oscillators (RSI, MACD)', duration: '18 min', free: false },
      { id: 'l7', title: 'Bollinger Bands & Volatility', duration: '16 min', free: false },
      { id: 'l8', title: 'Volume Analysis', duration: '12 min', free: false },
    ]
  },
  {
    id: 3, title: 'Strategy Development',
    lessons: [
      { id: 'l9', title: 'Trend Following Strategies', duration: '20 min', free: false },
      { id: 'l10', title: 'Mean Reversion Strategies', duration: '18 min', free: false },
      { id: 'l11', title: 'Breakout Strategies', duration: '16 min', free: false },
      { id: 'l12', title: 'Grid Trading Explained', duration: '14 min', free: false },
    ]
  },
  {
    id: 4, title: 'Backtesting & Optimization',
    lessons: [
      { id: 'l13', title: 'How to Backtest Properly', duration: '22 min', free: false },
      { id: 'l14', title: 'Avoiding Overfitting', duration: '18 min', free: false },
      { id: 'l15', title: 'Walk-Forward Analysis', duration: '20 min', free: false },
      { id: 'l16', title: 'Reading Backtest Metrics', duration: '15 min', free: false },
    ]
  },
  {
    id: 5, title: 'Risk Management',
    lessons: [
      { id: 'l17', title: 'Position Sizing Formulas', duration: '16 min', free: false },
      { id: 'l18', title: 'Maximum Drawdown Control', duration: '14 min', free: false },
      { id: 'l19', title: 'Portfolio Diversification', duration: '18 min', free: false },
      { id: 'l20', title: 'Psychology & Discipline', duration: '12 min', free: false },
    ]
  },
]

const LESSON_CONTENT = {
  l1: {
    title: 'What is Algorithmic Trading?',
    content: `
Algorithmic trading (also called automated trading or algo trading) is the use of computer programs to execute trading orders automatically based on predefined rules.

**Key Benefits:**
- Eliminates emotional decision-making
- Executes trades at optimal speeds
- Can monitor multiple markets simultaneously
- Backtestable against historical data

**How It Works:**
1. You define entry and exit rules (strategy)
2. The algorithm scans markets for signals
3. When conditions are met, orders are placed automatically
4. Risk management rules are applied to every trade

**Important Disclaimer:**
⚠️ Algorithmic trading does NOT guarantee profits. Markets are complex and unpredictable. Always start with paper trading and never risk money you cannot afford to lose.

**Getting Started on TradeBotHub Pro:**
1. Connect a testnet exchange account
2. Create a bot with paper trading mode
3. Backtest your chosen strategy
4. Monitor performance for at least 30 days before going live
    `,
  },
  l5: {
    title: 'Moving Averages (SMA, EMA)',
    content: `
Moving averages are among the most widely used technical indicators. They smooth out price data to identify trends.

**Simple Moving Average (SMA):**
Arithmetic mean of prices over N periods.
Formula: SMA = (P1 + P2 + ... + PN) / N

**Exponential Moving Average (EMA):**
Gives more weight to recent prices, making it more responsive.
Formula: EMA = Price × K + EMA_prev × (1 − K), where K = 2/(N+1)

**EMA Crossover Strategy:**
- When fast EMA (e.g. 9) crosses above slow EMA (e.g. 21) → BUY signal
- When fast EMA crosses below slow EMA → SELL signal

**Best Practices:**
- Use on trending markets (ADX > 25)
- Combine with volume confirmation
- Avoid ranging/sideways markets

⚠️ Past performance of any strategy is not indicative of future results.
    `,
  },
}

export default function Course() {
  const [activeLesson, setActiveLesson] = useState(null)
  const [completedLessons, setCompletedLessons] = useState(new Set())
  const [expandedModule, setExpandedModule] = useState(1)

  function openLesson(lesson) {
    if (!lesson.free) return
    setActiveLesson(lesson)
  }

  function complete(lessonId) {
    setCompletedLessons(new Set([...completedLessons, lessonId]))
  }

  const totalLessons = MODULES.reduce((sum, m) => sum + m.lessons.length, 0)
  const progress = (completedLessons.size / totalLessons) * 100

  return (
    <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
      {/* Module list */}
      <div className="xl:col-span-1 space-y-4">
        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <GraduationCap size={22} className="text-brand-400" />
            <div>
              <h3 className="font-semibold text-white">Algo Trading Course</h3>
              <p className="text-xs text-gray-400">{completedLessons.size}/{totalLessons} lessons</p>
            </div>
          </div>
          <div className="w-full bg-surface-200 rounded-full h-2 mb-4">
            <div className="bg-brand-500 h-2 rounded-full transition-all" style={{ width: `${progress}%` }} />
          </div>
        </div>

        {MODULES.map((module) => (
          <div key={module.id} className="card overflow-hidden">
            <button
              className="w-full flex items-center justify-between text-left"
              onClick={() => setExpandedModule(expandedModule === module.id ? null : module.id)}
            >
              <div className="flex items-center gap-3">
                <div className="w-7 h-7 bg-brand-500/20 rounded-lg flex items-center justify-center text-xs font-bold text-brand-400">
                  {module.id}
                </div>
                <span className="font-medium text-white text-sm">{module.title}</span>
              </div>
              <ChevronRight size={15} className={`text-gray-400 transition-transform ${expandedModule === module.id ? 'rotate-90' : ''}`} />
            </button>

            {expandedModule === module.id && (
              <div className="mt-3 space-y-1">
                {module.lessons.map((lesson) => (
                  <button
                    key={lesson.id}
                    onClick={() => openLesson(lesson)}
                    disabled={!lesson.free}
                    className={`w-full flex items-center justify-between p-2 rounded-lg text-xs text-left transition-colors ${activeLesson?.id === lesson.id ? 'bg-brand-500/20 text-brand-300' : lesson.free ? 'hover:bg-surface-100 text-gray-300' : 'opacity-50 cursor-not-allowed text-gray-500'}`}
                  >
                    <div className="flex items-center gap-2">
                      {completedLessons.has(lesson.id) ? (
                        <CheckCircle size={13} className="text-trading-green" />
                      ) : (
                        <Play size={13} className="text-gray-400" />
                      )}
                      <span>{lesson.title}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-gray-500">{lesson.duration}</span>
                      {!lesson.free && <span className="text-brand-400 text-xs">🔒 Pro</span>}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Lesson viewer */}
      <div className="xl:col-span-2">
        {activeLesson ? (
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">{activeLesson.title}</h3>
              <div className="flex items-center gap-2 text-xs text-gray-400">
                <Clock size={13} />
                {activeLesson.duration}
              </div>
            </div>
            <div className="prose prose-invert max-w-none text-gray-300 text-sm leading-relaxed whitespace-pre-line">
              {LESSON_CONTENT[activeLesson.id]?.content || 'Lesson content loading...'}
            </div>
            {!completedLessons.has(activeLesson.id) && (
              <button onClick={() => complete(activeLesson.id)} className="btn-success mt-6 flex items-center gap-2">
                <CheckCircle size={16} /> Mark as Complete
              </button>
            )}
          </div>
        ) : (
          <div className="card text-center py-16">
            <BookOpen size={48} className="mx-auto text-gray-600 mb-3" />
            <h3 className="font-semibold text-white">Select a lesson to begin</h3>
            <p className="text-gray-400 text-sm mt-1">Free lessons are marked with a play icon</p>
          </div>
        )}
      </div>
    </div>
  )
}
