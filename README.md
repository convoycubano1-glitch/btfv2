# TradeBotHub Pro

> Professional SaaS Algorithmic Trading Platform

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![React](https://img.shields.io/badge/react-18+-61DAFB)

---

## Overview

TradeBotHub Pro is a full-stack SaaS platform that enables traders to:
- Connect exchange accounts securely via API
- Create, test and deploy algorithmic trading bots
- Backtest strategies with historical data
- Trade live or in paper mode
- Buy/sell trading signals in a marketplace
- Learn algorithmic trading through integrated courses

---

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite + Tailwind CSS |
| Backend | Python FastAPI |
| Trading | CCXT |
| Backtesting | vectorbt + Backtrader + pandas |
| Indicators | pandas-ta |
| Database | PostgreSQL |
| Cache / PubSub | Redis |
| Real-time | WebSockets |
| Payments | Stripe |
| Auth | Supabase Auth |
| Containerization | Docker + Docker Compose |

---

## Project Structure

```
tradebothub-pro/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── api/v1/             # REST endpoints
│   │   ├── core/               # Config, DB, Security, Redis
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/           # Business logic
│   │   ├── strategies/         # 12 trading strategies
│   │   └── workers/            # Background workers
│   ├── migrations/             # SQL migrations
│   ├── main.py
│   └── requirements.txt
├── frontend/                   # React + Vite app
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Route pages
│   │   ├── store/              # Redux Toolkit state
│   │   ├── services/           # API + WebSocket clients
│   │   ├── hooks/              # Custom React hooks
│   │   └── utils/              # Helpers & constants
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml
└── .env.example
```

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### 1. Clone & Configure

```bash
git clone <repo>
cd tradebothub-pro
cp .env.example .env
# Edit .env with your API keys
```

### 2. Start with Docker

```bash
docker-compose up -d
```

Services will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### 3. Development Mode

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate         # Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## Modules

| # | Module | Description |
|---|--------|-------------|
| 1 | Dashboard | Portfolio overview, P&L, active bots |
| 2 | Exchanges | Connect Binance, Coinbase, Kraken, etc. |
| 3 | API Key Management | AES-256 encrypted key storage |
| 4 | Strategy Engine | Execute custom strategies |
| 5 | Bot Builder | Visual drag-and-drop bot configurator |
| 6 | Strategy Library | 12 pre-built strategies |
| 7 | Backtesting | Historical performance testing |
| 8 | Paper Trading | Risk-free simulated trading |
| 9 | Live Trading | Real order execution |
| 10 | Risk Management | Stop-loss, position sizing, drawdown limits |
| 11 | Signal Marketplace | Buy/browse signals |
| 12 | Signal Selling | Publish and monetize your signals |
| 13 | Algo Course | Structured learning path |
| 14 | AI Assistant | GPT-powered trading assistant |
| 15 | Reports | P&L reports, trade analytics |
| 16 | Subscriptions | Stripe-powered plans (Free/Pro/Elite) |

---

## Strategies

1. **EMA Crossover** — Fast/slow EMA trend following
2. **RSI Mean Reversion** — Overbought/oversold signals
3. **MACD Momentum** — Momentum-based entries
4. **Bollinger Bands Reversal** — Band squeeze/breakout
5. **Breakout Strategy** — Support/resistance breakout
6. **Smart DCA** — Dollar-cost averaging with dynamic sizing
7. **Grid Trading** — Automated grid order placement
8. **Volatility Breakout** — ATR-based volatility entries
9. **Portfolio Rebalancing** — Multi-asset rebalancing
10. **Arbitrage Monitor** — Cross-exchange spread detection
11. **Trend Following Multi-TF** — Multi-timeframe trend
12. **Smart Scalping** — High-frequency short-term entries

---

## Security

- API keys encrypted with AES-256 (Fernet)
- Withdrawal permissions blocked by default
- Paper trading enabled by default
- Risk validation before bot activation
- Emergency stop button to pause all bots
- JWT authentication with refresh tokens
- Rate limiting on all endpoints
- SQL injection protection via ORM
- Input validation via Pydantic

---

## Subscription Plans

| Plan | Price | Features |
|------|-------|---------|
| Free | $0/mo | 1 bot, paper trading, basic strategies |
| Pro | $29/mo | 5 bots, live trading, all strategies, backtesting |
| Elite | $99/mo | Unlimited bots, signals marketplace, AI assistant, priority support |

---

## Disclaimer

> **TradeBotHub Pro does not provide financial advice.** All trading involves risk of loss. Past performance is not indicative of future results. Use at your own risk.

---

## License

MIT © 2026 TradeBotHub Pro
