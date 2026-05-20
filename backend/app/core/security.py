from datetime import datetime, timedelta, timezone
from typing import Any, Optional
import uuid
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx
from app.core.config import settings

# ── Password hashing ─────────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── JWT ──────────────────────────────────────────────────────────────────────
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# ── Clerk JWKS ───────────────────────────────────────────────────────────────
# Derived from publishable key: flying-cowbird-41.clerk.accounts.dev
CLERK_JWKS_URL = "https://flying-cowbird-41.clerk.accounts.dev/.well-known/jwks.json"
_jwks_cache: Optional[dict] = None


async def _get_clerk_jwks() -> dict:
    global _jwks_cache
    if _jwks_cache is None:
        async with httpx.AsyncClient() as client:
            resp = await client.get(CLERK_JWKS_URL, timeout=5.0)
            resp.raise_for_status()
            _jwks_cache = resp.json()
    return _jwks_cache


async def verify_clerk_token(token: str) -> dict[str, Any]:
    try:
        header = jwt.get_unverified_header(token)
        jwks = await _get_clerk_jwks()
        keys = {k["kid"]: k for k in jwks.get("keys", [])}
        key = keys.get(header.get("kid"))
        if not key:
            # Refresh cache and retry once
            global _jwks_cache
            _jwks_cache = None
            jwks = await _get_clerk_jwks()
            keys = {k["kid"]: k for k in jwks.get("keys", [])}
            key = keys.get(header.get("kid"))
        if not key:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown signing key")
        payload = jwt.decode(token, key, algorithms=["RS256"])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Clerk token",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ── Fernet encryption (for API keys) ─────────────────────────────────────────
_fernet: Optional[Fernet] = None


def get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        if not settings.ENCRYPTION_KEY:
            key = Fernet.generate_key()
        else:
            key = settings.ENCRYPTION_KEY.encode()
        _fernet = Fernet(key)
    return _fernet


# ── Password utilities ────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── Token utilities ───────────────────────────────────────────────────────────
def create_access_token(subject: str, extra: dict[str, Any] | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(subject), "exp": expire, "type": "access"}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": str(subject), "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_id(
    token: str = Depends(oauth2_scheme),
) -> str:
    """Verify Clerk JWT and return the Clerk subject (user ID string)."""
    payload = await verify_clerk_token(token)
    clerk_sub: str = payload.get("sub")
    if not clerk_sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: missing sub")
    return clerk_sub


async def get_or_create_user(clerk_sub: str, db: AsyncSession) -> "User":
    """Look up or auto-provision a backend User record for a Clerk user."""
    from app.models.user import User

    result = await db.execute(select(User).where(User.supabase_id == clerk_sub))
    user = result.scalar_one_or_none()
    if user:
        return user

    # Auto-create user on first API call after Clerk sign-up
    email = f"{clerk_sub}@clerk.user"
    username = f"user_{str(uuid.uuid4())[:8]}"
    user = User(
        supabase_id=clerk_sub,
        email=email,
        username=username,
        is_verified=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# ── API key encryption ────────────────────────────────────────────────────────
def encrypt_api_key(plain_key: str) -> str:
    """Encrypt an exchange API key for safe storage."""
    return get_fernet().encrypt(plain_key.encode()).decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an exchange API key for use."""
    return get_fernet().decrypt(encrypted_key.encode()).decode()
