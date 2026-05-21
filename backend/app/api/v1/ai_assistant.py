from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from app.core.security import get_current_user_id
from app.services.ai_assistant import AIAssistant
from app.core.limiter import limiter

router = APIRouter()


class ChatMessage(BaseModel):
    message: str
    context: dict = {}


class ChatResponse(BaseModel):
    reply: str
    disclaimer: str = (
        "⚠️ This AI assistant is for educational purposes only. "
        "It does not provide financial advice. Always do your own research."
    )


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat_with_ai(
    request: Request,
    payload: ChatMessage,
    user_id: str = Depends(get_current_user_id),
):
    """Chat with the AI trading assistant."""
    assistant = AIAssistant()
    reply = await assistant.chat(
        user_id=user_id,
        message=payload.message,
        context=payload.context,
    )
    return ChatResponse(reply=reply)


@router.get("/strategy-suggestion")
async def suggest_strategy(
    symbol: str,
    timeframe: str,
    market_condition: str = "trending",
    user_id: str = Depends(get_current_user_id),
):
    """Get AI-powered strategy recommendations based on market conditions."""
    assistant = AIAssistant()
    suggestion = await assistant.suggest_strategy(
        symbol=symbol,
        timeframe=timeframe,
        market_condition=market_condition,
    )
    return {
        "suggestion": suggestion,
        "disclaimer": "AI suggestions are not financial advice.",
    }


@router.get("/explain-strategy/{strategy_type}")
async def explain_strategy(
    strategy_type: str,
    user_id: str = Depends(get_current_user_id),
):
    """Get a plain-language explanation of a strategy."""
    assistant = AIAssistant()
    explanation = await assistant.explain_strategy(strategy_type)
    return {"strategy": strategy_type, "explanation": explanation}
