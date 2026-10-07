"""High-performance caching layer with Redis & in-memory fallback.
Avoids redundant API calls and keeps latency low.
"""
import time
import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class CacheManager:
    def __init__(self):
        self._memory_cache: dict[str, tuple[float, Any]] = {}
        self._redis_client = None
        self._redis_connected = False

    async def initialize(self, redis_url: Optional[str] = None):
        """Attempt Redis connection if URL provided; falls back gracefully to in-memory."""
        if redis_url:
            try:
                import redis.asyncio as aioredis
                self._redis_client = aioredis.from_url(redis_url, decode_responses=True)
                await self._redis_client.ping()
                self._redis_connected = True
                logger.info("Successfully connected to Redis cache.")
            except Exception as e:
                logger.warning(f"Redis unavailable ({e}). Using robust In-Memory LRU Cache.")
                self._redis_connected = False
                self._redis_client = None

    async def get(self, key: str) -> Optional[Any]:
        if self._redis_connected and self._redis_client:
            try:
                val = await self._redis_client.get(key)
                if val is not None:
                    return json.loads(val)
            except Exception as e:
                logger.debug(f"Redis get error for {key}: {e}")

        # In-memory check
        item = self._memory_cache.get(key)
        if item is not None:
            expiry, data = item
            if time.time() < expiry:
                return data
            else:
                del self._memory_cache[key]
        return None

    async def set(self, key: str, value: Any, ttl_seconds: int = 300) -> bool:
        if self._redis_connected and self._redis_client:
            try:
                await self._redis_client.setex(key, ttl_seconds, json.dumps(value))
                return True
            except Exception as e:
                logger.debug(f"Redis set error for {key}: {e}")

        # In-memory store
        expiry = time.time() + ttl_seconds
        # Evict old items if cache exceeds 5000 items
        if len(self._memory_cache) > 5000:
            now = time.time()
            expired_keys = [k for k, (exp, _) in self._memory_cache.items() if exp < now]
            for k in expired_keys:
                del self._memory_cache[k]
        self._memory_cache[key] = (expiry, value)
        return True

    async def delete(self, key: str):
        if self._redis_connected and self._redis_client:
            try:
                await self._redis_client.delete(key)
            except Exception:
                pass
        self._memory_cache.pop(key, None)

    async def clear_pattern(self, pattern: str):
        """Clear keys matching pattern."""
        if self._redis_connected and self._redis_client:
            try:
                keys = await self._redis_client.keys(pattern)
                if keys:
                    await self._redis_client.delete(*keys)
            except Exception:
                pass
        # In-memory simple prefix match
        prefix = pattern.replace("*", "")
        keys_to_del = [k for k in self._memory_cache.keys() if prefix in k]
        for k in keys_to_del:
            del self._memory_cache[k]


cache = CacheManager()
