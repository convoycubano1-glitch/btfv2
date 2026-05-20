import ccxt.async_support as ccxt
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ExchangeService:
    """CCXT-based exchange integration service."""

    # Exchanges that support testnet
    TESTNET_SUPPORTED = {"binance", "bybit", "okx"}

    def __init__(
        self,
        exchange_id: str,
        api_key: str,
        api_secret: str,
        passphrase: Optional[str] = None,
        testnet: bool = True,
    ):
        self.exchange_id = exchange_id
        self.exchange = self._create_exchange(exchange_id, api_key, api_secret, passphrase, testnet)

    def _create_exchange(
        self,
        exchange_id: str,
        api_key: str,
        api_secret: str,
        passphrase: Optional[str],
        testnet: bool,
    ):
        exchange_class = getattr(ccxt, exchange_id, None)
        if not exchange_class:
            raise ValueError(f"Unsupported exchange: {exchange_id}")

        config = {
            "apiKey": api_key,
            "secret": api_secret,
            "enableRateLimit": True,
            "options": {"defaultType": "spot"},
        }
        if passphrase:
            config["password"] = passphrase

        exchange = exchange_class(config)

        if testnet and exchange_id in self.TESTNET_SUPPORTED:
            exchange.set_sandbox_mode(True)

        return exchange

    async def verify_connection(self) -> Tuple[bool, Optional[str]]:
        """Verify API keys are valid by fetching balance."""
        try:
            await self.exchange.fetch_balance()
            return True, None
        except ccxt.AuthenticationError as e:
            return False, f"Authentication failed: {str(e)}"
        except ccxt.PermissionDenied as e:
            return False, f"Permission denied: {str(e)}"
        except Exception as e:
            return False, str(e)
        finally:
            await self.exchange.close()

    async def get_balance(self) -> dict:
        """Fetch account balance."""
        try:
            balance = await self.exchange.fetch_balance()
            # Return only non-zero balances
            non_zero = {
                currency: {
                    "free": data["free"],
                    "used": data["used"],
                    "total": data["total"],
                }
                for currency, data in balance["total"].items()
                if data > 0
            } if "total" in balance else {}
            return {"balances": non_zero, "exchange": self.exchange_id}
        finally:
            await self.exchange.close()

    async def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 500,
        since: Optional[int] = None,
    ) -> list:
        """Fetch OHLCV candlestick data."""
        try:
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=limit)
            return [
                {
                    "timestamp": candle[0],
                    "open": candle[1],
                    "high": candle[2],
                    "low": candle[3],
                    "close": candle[4],
                    "volume": candle[5],
                }
                for candle in ohlcv
            ]
        finally:
            await self.exchange.close()

    async def fetch_ticker(self, symbol: str) -> dict:
        """Fetch current ticker price."""
        try:
            ticker = await self.exchange.fetch_ticker(symbol)
            return {
                "symbol": symbol,
                "last": ticker["last"],
                "bid": ticker["bid"],
                "ask": ticker["ask"],
                "volume": ticker["quoteVolume"],
                "change_24h": ticker["percentage"],
                "high_24h": ticker["high"],
                "low_24h": ticker["low"],
            }
        finally:
            await self.exchange.close()

    async def create_market_order(
        self,
        symbol: str,
        side: str,  # "buy" or "sell"
        amount: float,
    ) -> dict:
        """
        Place a market order.
        SECURITY: Withdrawals are NEVER executed through this service.
        """
        try:
            order = await self.exchange.create_market_order(symbol, side, amount)
            logger.info(f"Order placed: {side} {amount} {symbol} — id={order.get('id')}")
            return {
                "order_id": order.get("id"),
                "symbol": symbol,
                "side": side,
                "amount": order.get("amount"),
                "price": order.get("average") or order.get("price"),
                "status": order.get("status"),
                "timestamp": order.get("timestamp"),
            }
        finally:
            await self.exchange.close()

    async def create_limit_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        price: float,
    ) -> dict:
        """Place a limit order."""
        try:
            order = await self.exchange.create_limit_order(symbol, side, amount, price)
            return {
                "order_id": order.get("id"),
                "symbol": symbol,
                "side": side,
                "amount": order.get("amount"),
                "price": price,
                "status": order.get("status"),
            }
        finally:
            await self.exchange.close()

    async def cancel_order(self, order_id: str, symbol: str) -> dict:
        """Cancel an open order."""
        try:
            result = await self.exchange.cancel_order(order_id, symbol)
            return {"cancelled": True, "order_id": order_id}
        except Exception as e:
            return {"cancelled": False, "error": str(e)}
        finally:
            await self.exchange.close()

    @staticmethod
    async def get_public_ticker(exchange_id: str, symbol: str) -> dict:
        """Fetch ticker without authentication (public endpoint)."""
        exchange_class = getattr(ccxt, exchange_id, None)
        if not exchange_class:
            return {"error": f"Unknown exchange: {exchange_id}"}
        exchange = exchange_class({"enableRateLimit": True})
        try:
            ticker = await exchange.fetch_ticker(symbol)
            return {
                "symbol": symbol,
                "last": ticker.get("last"),
                "bid": ticker.get("bid"),
                "ask": ticker.get("ask"),
                "change_24h": ticker.get("percentage"),
                "volume": ticker.get("quoteVolume"),
            }
        except Exception as e:
            return {"error": str(e)}
        finally:
            await exchange.close()
