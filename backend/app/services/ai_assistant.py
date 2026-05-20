from openai import AsyncOpenAI
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a knowledgeable algorithmic trading assistant for TradeBotHub Pro.
You help users understand trading strategies, technical analysis, and bot configuration.

IMPORTANT RULES:
1. NEVER provide specific financial advice or tell users to buy/sell specific assets
2. ALWAYS include the disclaimer that past performance doesn't guarantee future results
3. Focus on education and explaining concepts clearly
4. When discussing strategies, explain the logic, not specific trade recommendations
5. If asked about get-rich-quick schemes, warn about the risks involved

You have expertise in:
- Technical analysis (EMA, RSI, MACD, Bollinger Bands, ATR, etc.)
- Algorithmic trading strategies
- Risk management principles
- Backtesting methodology
- Python trading libraries (CCXT, pandas-ta, vectorbt)
"""


class AIAssistant:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    async def chat(self, user_id: str, message: str, context: dict = {}) -> str:
        if not self.client:
            return (
                "AI Assistant is not configured. "
                "Please set OPENAI_API_KEY in your environment to enable this feature."
            )

        try:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]

            # Add context if provided
            if context.get("current_strategy"):
                messages.append({
                    "role": "system",
                    "content": f"User is currently working with strategy: {context['current_strategy']}",
                })

            messages.append({"role": "user", "content": message})

            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                max_tokens=800,
                temperature=0.7,
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"AI assistant error: {e}")
            return f"AI assistant temporarily unavailable. Please try again later."

    async def suggest_strategy(
        self,
        symbol: str,
        timeframe: str,
        market_condition: str,
    ) -> str:
        if not self.client:
            return "AI features require OPENAI_API_KEY configuration."

        prompt = (
            f"Based on a {market_condition} market for {symbol} on {timeframe} timeframe, "
            f"which algorithmic trading strategy from this list would generally be most appropriate: "
            f"EMA Crossover, RSI Mean Reversion, MACD Momentum, Bollinger Bands Reversal, "
            f"Breakout Strategy, DCA, Grid Trading, Volatility Breakout? "
            f"Explain your reasoning briefly. Remember: this is educational only."
        )
        return await self.chat(user_id="system", message=prompt)

    async def explain_strategy(self, strategy_type: str) -> str:
        if not self.client:
            return "AI features require OPENAI_API_KEY configuration."

        prompt = (
            f"Explain the {strategy_type} trading strategy in simple terms. "
            f"Cover: 1) How it works, 2) What indicators it uses, "
            f"3) When it tends to perform well, 4) Its main risks. "
            f"Keep it educational and under 200 words."
        )
        return await self.chat(user_id="system", message=prompt)
