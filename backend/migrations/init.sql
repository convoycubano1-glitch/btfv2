-- TradeBotHub Pro — Initial Database Schema
-- Run this on first setup or via Docker entrypoint

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ── Enums ──────────────────────────────────────────────────────────────────

CREATE TYPE user_role AS ENUM ('user', 'pro', 'elite', 'admin');
CREATE TYPE exchange_status AS ENUM ('active', 'inactive', 'error');
CREATE TYPE bot_status AS ENUM ('draft', 'active', 'paused', 'stopped', 'error');
CREATE TYPE trading_mode AS ENUM ('paper', 'live');
CREATE TYPE trade_status AS ENUM ('pending', 'open', 'closed', 'cancelled', 'failed');
CREATE TYPE trade_side AS ENUM ('buy', 'sell');
CREATE TYPE trade_mode AS ENUM ('paper', 'live');
CREATE TYPE signal_type AS ENUM ('buy', 'sell', 'hold');
CREATE TYPE signal_status AS ENUM ('active', 'expired', 'cancelled');
CREATE TYPE subscription_plan AS ENUM ('free', 'pro', 'elite');
CREATE TYPE subscription_status AS ENUM ('active', 'cancelled', 'past_due', 'trialing', 'expired');
CREATE TYPE backtest_status AS ENUM ('pending', 'running', 'completed', 'failed');
CREATE TYPE strategy_type AS ENUM (
    'ema_crossover', 'rsi_mean_reversion', 'macd_momentum', 'bollinger_bands',
    'breakout', 'dca', 'grid_trading', 'volatility_breakout',
    'portfolio_rebalancing', 'arbitrage_monitor', 'trend_following', 'smart_scalping', 'custom'
);

-- ── Users ──────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    supabase_id VARCHAR(255) UNIQUE,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255),
    full_name VARCHAR(255),
    avatar_url VARCHAR(500),
    role user_role DEFAULT 'user' NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    emergency_stop_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- ── Exchange Connections ────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS exchange_connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    exchange_id VARCHAR(50) NOT NULL,
    label VARCHAR(100) NOT NULL,
    encrypted_api_key TEXT NOT NULL,
    encrypted_api_secret TEXT NOT NULL,
    encrypted_passphrase TEXT,
    is_testnet BOOLEAN DEFAULT TRUE,
    allow_trading BOOLEAN DEFAULT TRUE,
    allow_withdrawals BOOLEAN DEFAULT FALSE NOT NULL,  -- SECURITY: always false
    status exchange_status DEFAULT 'inactive',
    last_verified_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_exchange_connections_user_id ON exchange_connections(user_id);

-- ── Strategies ──────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS strategies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    strategy_type strategy_type NOT NULL,
    default_parameters JSONB DEFAULT '{}',
    custom_code TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    is_built_in BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Bots ────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS bots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    exchange_connection_id UUID REFERENCES exchange_connections(id),
    strategy_id UUID REFERENCES strategies(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    mode trading_mode DEFAULT 'paper' NOT NULL,
    status bot_status DEFAULT 'draft',
    parameters JSONB DEFAULT '{}',
    max_position_size_pct FLOAT DEFAULT 0.02,
    stop_loss_pct FLOAT DEFAULT 0.02,
    take_profit_pct FLOAT DEFAULT 0.04,
    max_open_trades INTEGER DEFAULT 1,
    max_daily_loss_pct FLOAT DEFAULT 0.05,
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    total_pnl FLOAT DEFAULT 0.0,
    total_pnl_pct FLOAT DEFAULT 0.0,
    last_run_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_bots_user_id ON bots(user_id);
CREATE INDEX idx_bots_status ON bots(status);

-- ── Trades ──────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    bot_id UUID REFERENCES bots(id),
    exchange_connection_id UUID REFERENCES exchange_connections(id),
    exchange_order_id VARCHAR(100),
    symbol VARCHAR(20) NOT NULL,
    side trade_side NOT NULL,
    mode trade_mode DEFAULT 'paper',
    status trade_status DEFAULT 'pending',
    entry_price FLOAT,
    exit_price FLOAT,
    quantity FLOAT NOT NULL,
    notional_value FLOAT,
    stop_loss FLOAT,
    take_profit FLOAT,
    pnl FLOAT,
    pnl_pct FLOAT,
    fees FLOAT DEFAULT 0.0,
    strategy_name VARCHAR(100),
    signal_data JSONB,
    opened_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_trades_user_id ON trades(user_id);
CREATE INDEX idx_trades_bot_id ON trades(bot_id);
CREATE INDEX idx_trades_status ON trades(status);
CREATE INDEX idx_trades_created_at ON trades(created_at DESC);

-- ── Signals ─────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    creator_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    symbol VARCHAR(20) NOT NULL,
    signal_type signal_type NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    entry_price FLOAT NOT NULL,
    stop_loss FLOAT NOT NULL,
    take_profit_1 FLOAT,
    take_profit_2 FLOAT,
    take_profit_3 FLOAT,
    risk_reward_ratio FLOAT,
    is_free BOOLEAN DEFAULT TRUE,
    price_usd FLOAT DEFAULT 0.0,
    is_published BOOLEAN DEFAULT FALSE,
    status signal_status DEFAULT 'active',
    subscribers_count INTEGER DEFAULT 0,
    hit_tp1 BOOLEAN,
    hit_tp2 BOOLEAN,
    hit_stop_loss BOOLEAN,
    final_pnl_pct FLOAT,
    tags JSONB DEFAULT '[]',
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_signals_creator_id ON signals(creator_id);
CREATE INDEX idx_signals_is_published ON signals(is_published);

-- ── Signal Subscriptions ────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS signal_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subscriber_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stripe_subscription_id VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Subscriptions (Platform Plans) ─────────────────────────────────────────

CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    plan subscription_plan DEFAULT 'free',
    status subscription_status DEFAULT 'active',
    stripe_customer_id VARCHAR(255) UNIQUE,
    stripe_subscription_id VARCHAR(255) UNIQUE,
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Backtests ────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS backtests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    strategy_id UUID REFERENCES strategies(id),
    name VARCHAR(200) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    strategy_type VARCHAR(50) NOT NULL,
    parameters JSONB DEFAULT '{}',
    start_date TIMESTAMPTZ NOT NULL,
    end_date TIMESTAMPTZ NOT NULL,
    initial_capital FLOAT DEFAULT 10000.0,
    status backtest_status DEFAULT 'pending',
    final_equity FLOAT,
    total_return_pct FLOAT,
    annualized_return_pct FLOAT,
    max_drawdown_pct FLOAT,
    sharpe_ratio FLOAT,
    sortino_ratio FLOAT,
    win_rate_pct FLOAT,
    total_trades INTEGER,
    winning_trades INTEGER,
    losing_trades INTEGER,
    avg_win_pct FLOAT,
    avg_loss_pct FLOAT,
    profit_factor FLOAT,
    expectancy FLOAT,
    trade_log JSONB,
    equity_curve JSONB,
    error_message TEXT,
    duration_seconds FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_backtests_user_id ON backtests(user_id);

-- ── Updated at trigger ──────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE PROCEDURE update_updated_at();
CREATE TRIGGER update_bots_updated_at BEFORE UPDATE ON bots FOR EACH ROW EXECUTE PROCEDURE update_updated_at();
CREATE TRIGGER update_exchange_connections_updated_at BEFORE UPDATE ON exchange_connections FOR EACH ROW EXECUTE PROCEDURE update_updated_at();
CREATE TRIGGER update_signals_updated_at BEFORE UPDATE ON signals FOR EACH ROW EXECUTE PROCEDURE update_updated_at();
CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions FOR EACH ROW EXECUTE PROCEDURE update_updated_at();
