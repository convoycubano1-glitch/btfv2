from typing import Any
from app.core.config import settings


class RiskManager:
    """
    Risk management validation and position sizing utilities.
    All bots must pass risk checks before going live.
    """

    MAX_POSITION_SIZE_PCT = 0.10    # max 10% of portfolio per trade
    MAX_STOP_LOSS_PCT = 0.10        # max 10% stop loss
    MIN_STOP_LOSS_PCT = 0.001       # min 0.1% stop loss
    MAX_DAILY_LOSS_PCT = 0.20       # max 20% daily loss limit
    MAX_OPEN_TRADES = 10

    @classmethod
    def validate_bot_risk(cls, bot_params: dict[str, Any]) -> dict:
        """
        Validate risk parameters before a bot goes live.
        Returns {"passed": bool, "reason": str | None, "warnings": list}
        """
        warnings = []
        failures = []

        max_pos = bot_params.get("max_position_size_pct", 0.02)
        stop_loss = bot_params.get("stop_loss_pct", 0.02)
        daily_loss = bot_params.get("max_daily_loss_pct", 0.05)
        open_trades = bot_params.get("max_open_trades", 1)

        # Hard limits
        if max_pos > cls.MAX_POSITION_SIZE_PCT:
            failures.append(
                f"Position size {max_pos*100:.1f}% exceeds max allowed {cls.MAX_POSITION_SIZE_PCT*100:.0f}%"
            )
        if stop_loss > cls.MAX_STOP_LOSS_PCT:
            failures.append(
                f"Stop loss {stop_loss*100:.1f}% exceeds max allowed {cls.MAX_STOP_LOSS_PCT*100:.0f}%"
            )
        if stop_loss < cls.MIN_STOP_LOSS_PCT:
            failures.append(
                f"Stop loss {stop_loss*100:.3f}% is too tight (min {cls.MIN_STOP_LOSS_PCT*100:.1f}%)"
            )
        if daily_loss > cls.MAX_DAILY_LOSS_PCT:
            failures.append(
                f"Daily loss limit {daily_loss*100:.1f}% exceeds max allowed {cls.MAX_DAILY_LOSS_PCT*100:.0f}%"
            )
        if open_trades > cls.MAX_OPEN_TRADES:
            failures.append(
                f"Max open trades {open_trades} exceeds platform limit {cls.MAX_OPEN_TRADES}"
            )

        # Warnings
        if max_pos > 0.05:
            warnings.append("Position size > 5% is high risk")
        if stop_loss > 0.05:
            warnings.append("Stop loss > 5% is aggressive")
        if not bot_params.get("stop_loss_pct"):
            warnings.append("No stop loss set — highly recommended for live trading")

        if failures:
            return {"passed": False, "reason": "; ".join(failures), "warnings": warnings}
        return {"passed": True, "reason": None, "warnings": warnings}

    @staticmethod
    def calculate_position_size(
        account_size: float,
        risk_pct: float,
        entry_price: float,
        stop_loss: float,
    ) -> dict:
        """
        Calculate position size using the fixed risk model.
        Risk amount = account_size * risk_pct / 100
        Position size = risk_amount / |entry - stop_loss|
        """
        risk_amount = account_size * (risk_pct / 100)
        price_risk = abs(entry_price - stop_loss)
        if price_risk == 0:
            return {"error": "Entry price and stop loss cannot be equal"}

        position_size = risk_amount / price_risk
        position_value = position_size * entry_price
        actual_risk_pct = (position_value / account_size) * 100

        return {
            "position_size": round(position_size, 6),
            "position_value_usd": round(position_value, 2),
            "risk_amount_usd": round(risk_amount, 2),
            "risk_pct": round(actual_risk_pct, 2),
            "risk_reward_ratio": round(
                abs(stop_loss - entry_price) / abs(entry_price - stop_loss), 2
            ) if price_risk > 0 else None,
        }

    @staticmethod
    def get_risk_guidelines() -> list[dict]:
        return [
            {
                "rule": "Never risk more than 1-2% of your account per trade",
                "severity": "critical",
            },
            {
                "rule": "Always use a stop loss",
                "severity": "critical",
            },
            {
                "rule": "Never trade without a tested strategy",
                "severity": "high",
            },
            {
                "rule": "Start with paper trading, not live",
                "severity": "high",
            },
            {
                "rule": "Never invest more than you can afford to lose",
                "severity": "critical",
            },
            {
                "rule": "Diversify across multiple strategies and assets",
                "severity": "medium",
            },
            {
                "rule": "Use the emergency stop if markets behave unexpectedly",
                "severity": "high",
            },
            {
                "rule": "Review bot performance weekly",
                "severity": "medium",
            },
        ]

    @staticmethod
    def check_daily_loss_limit(current_daily_pnl_pct: float, max_daily_loss_pct: float) -> bool:
        """Returns True if bot should be paused due to daily loss limit breach."""
        return current_daily_pnl_pct <= -abs(max_daily_loss_pct)
