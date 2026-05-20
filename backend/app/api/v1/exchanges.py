from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user_id, encrypt_api_key, decrypt_api_key
from app.models.exchange import ExchangeConnection, ExchangeStatus
from app.schemas.exchange import ExchangeConnectionCreate, ExchangeConnectionResponse, ExchangeConnectionUpdate
from app.services.exchange_service import ExchangeService
import uuid

router = APIRouter()


@router.get("/", response_model=list[ExchangeConnectionResponse])
async def list_exchanges(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ExchangeConnection).where(ExchangeConnection.user_id == uuid.UUID(user_id))
    )
    return [ExchangeConnectionResponse.model_validate(e) for e in result.scalars().all()]


@router.post("/", response_model=ExchangeConnectionResponse, status_code=201)
async def create_exchange(
    payload: ExchangeConnectionCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    # Verify the keys work before saving
    service = ExchangeService(
        exchange_id=payload.exchange_id,
        api_key=payload.api_key,
        api_secret=payload.api_secret,
        passphrase=payload.passphrase,
        testnet=payload.is_testnet,
    )
    is_valid, error = await service.verify_connection()

    conn = ExchangeConnection(
        user_id=uuid.UUID(user_id),
        exchange_id=payload.exchange_id,
        label=payload.label,
        encrypted_api_key=encrypt_api_key(payload.api_key),
        encrypted_api_secret=encrypt_api_key(payload.api_secret),
        encrypted_passphrase=encrypt_api_key(payload.passphrase) if payload.passphrase else None,
        is_testnet=payload.is_testnet,
        status=ExchangeStatus.ACTIVE if is_valid else ExchangeStatus.ERROR,
        error_message=error,
        allow_withdrawals=False,  # SECURITY: never allow withdrawals
    )
    db.add(conn)
    await db.commit()
    await db.refresh(conn)
    return ExchangeConnectionResponse.model_validate(conn)


@router.get("/{connection_id}", response_model=ExchangeConnectionResponse)
async def get_exchange(
    connection_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ExchangeConnection).where(
            ExchangeConnection.id == connection_id,
            ExchangeConnection.user_id == uuid.UUID(user_id),
        )
    )
    conn = result.scalar_one_or_none()
    if not conn:
        raise HTTPException(status_code=404, detail="Exchange connection not found")
    return ExchangeConnectionResponse.model_validate(conn)


@router.patch("/{connection_id}", response_model=ExchangeConnectionResponse)
async def update_exchange(
    connection_id: uuid.UUID,
    payload: ExchangeConnectionUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ExchangeConnection).where(
            ExchangeConnection.id == connection_id,
            ExchangeConnection.user_id == uuid.UUID(user_id),
        )
    )
    conn = result.scalar_one_or_none()
    if not conn:
        raise HTTPException(status_code=404, detail="Exchange connection not found")

    for field, value in payload.model_dump(exclude_none=True).items():
        if field == "allow_withdrawals":
            continue  # SECURITY: never allow setting withdrawals to True via API
        setattr(conn, field, value)
    await db.commit()
    await db.refresh(conn)
    return ExchangeConnectionResponse.model_validate(conn)


@router.delete("/{connection_id}", status_code=204)
async def delete_exchange(
    connection_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ExchangeConnection).where(
            ExchangeConnection.id == connection_id,
            ExchangeConnection.user_id == uuid.UUID(user_id),
        )
    )
    conn = result.scalar_one_or_none()
    if not conn:
        raise HTTPException(status_code=404, detail="Exchange connection not found")
    await db.delete(conn)
    await db.commit()


@router.post("/{connection_id}/verify", response_model=dict)
async def verify_exchange(
    connection_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ExchangeConnection).where(
            ExchangeConnection.id == connection_id,
            ExchangeConnection.user_id == uuid.UUID(user_id),
        )
    )
    conn = result.scalar_one_or_none()
    if not conn:
        raise HTTPException(status_code=404, detail="Exchange connection not found")

    service = ExchangeService(
        exchange_id=conn.exchange_id,
        api_key=decrypt_api_key(conn.encrypted_api_key),
        api_secret=decrypt_api_key(conn.encrypted_api_secret),
        passphrase=decrypt_api_key(conn.encrypted_passphrase) if conn.encrypted_passphrase else None,
        testnet=conn.is_testnet,
    )
    is_valid, error = await service.verify_connection()
    conn.status = ExchangeStatus.ACTIVE if is_valid else ExchangeStatus.ERROR
    conn.error_message = error
    await db.commit()

    return {"valid": is_valid, "error": error}


@router.get("/{connection_id}/balance")
async def get_balance(
    connection_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ExchangeConnection).where(
            ExchangeConnection.id == connection_id,
            ExchangeConnection.user_id == uuid.UUID(user_id),
        )
    )
    conn = result.scalar_one_or_none()
    if not conn:
        raise HTTPException(status_code=404, detail="Exchange connection not found")

    service = ExchangeService(
        exchange_id=conn.exchange_id,
        api_key=decrypt_api_key(conn.encrypted_api_key),
        api_secret=decrypt_api_key(conn.encrypted_api_secret),
        passphrase=decrypt_api_key(conn.encrypted_passphrase) if conn.encrypted_passphrase else None,
        testnet=conn.is_testnet,
    )
    balance = await service.get_balance()
    return balance
