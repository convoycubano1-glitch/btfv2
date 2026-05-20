from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.core.websocket_manager import ws_manager
from app.core.security import decode_token
from app.services.exchange_service import ExchangeService
import asyncio
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/connect")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
):
    """
    Main WebSocket endpoint.
    Sends: price updates, bot status, trade notifications, P&L updates.
    """
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=4001)
            return
    except Exception:
        await websocket.close(code=4001)
        return

    await ws_manager.connect(websocket, user_id)
    try:
        # Send welcome message
        await websocket.send_text(json.dumps({
            "type": "connected",
            "message": "Connected to TradeBotHub Pro real-time feed",
            "user_id": user_id,
        }))

        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                message = json.loads(data)

                msg_type = message.get("type")

                if msg_type == "subscribe_price":
                    symbol = message.get("symbol", "BTC/USDT")
                    exchange = message.get("exchange", "binance")
                    ws_manager.subscribe_to_channel(user_id, f"price:{exchange}:{symbol}")
                    await websocket.send_text(json.dumps({
                        "type": "subscribed",
                        "channel": f"price:{exchange}:{symbol}",
                    }))

                elif msg_type == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))

            except asyncio.TimeoutError:
                # Send heartbeat
                await websocket.send_text(json.dumps({"type": "heartbeat"}))

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: user={user_id}")
    finally:
        await ws_manager.disconnect(websocket, user_id)


@router.websocket("/market")
async def market_feed(
    websocket: WebSocket,
    symbol: str = Query("BTC/USDT"),
    exchange: str = Query("binance"),
):
    """Public market data WebSocket — no auth required."""
    await websocket.accept()
    try:
        while True:
            try:
                # In production: stream from exchange via CCXT pro or Redis pub/sub
                ticker = await ExchangeService.get_public_ticker(exchange, symbol)
                await websocket.send_text(json.dumps({
                    "type": "ticker",
                    "symbol": symbol,
                    "exchange": exchange,
                    "data": ticker,
                }))
                await asyncio.sleep(2)
            except Exception as e:
                await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
                await asyncio.sleep(5)
    except WebSocketDisconnect:
        pass
