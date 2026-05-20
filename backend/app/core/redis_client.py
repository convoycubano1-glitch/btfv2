import redis.asyncio as aioredis
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class RedisClient:
    def __init__(self):
        self._client: aioredis.Redis | None = None

    async def connect(self):
        self._client = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        logger.info("Redis connected.")

    async def disconnect(self):
        if self._client:
            await self._client.aclose()
            logger.info("Redis disconnected.")

    @property
    def client(self) -> aioredis.Redis:
        if not self._client:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self._client

    # ── Convenience helpers ───────────────────────────────────────────────────
    async def get(self, key: str) -> str | None:
        return await self.client.get(key)

    async def set(self, key: str, value: str, ex: int | None = None):
        await self.client.set(key, value, ex=ex)

    async def delete(self, key: str):
        await self.client.delete(key)

    async def publish(self, channel: str, message: str):
        await self.client.publish(channel, message)

    async def subscribe(self, channel: str):
        pubsub = self.client.pubsub()
        await pubsub.subscribe(channel)
        return pubsub

    async def lpush(self, key: str, *values):
        await self.client.lpush(key, *values)

    async def lrange(self, key: str, start: int, end: int):
        return await self.client.lrange(key, start, end)

    async def expire(self, key: str, seconds: int):
        await self.client.expire(key, seconds)

    async def hset(self, name: str, mapping: dict):
        await self.client.hset(name, mapping=mapping)

    async def hgetall(self, name: str) -> dict:
        return await self.client.hgetall(name)


redis_client = RedisClient()
