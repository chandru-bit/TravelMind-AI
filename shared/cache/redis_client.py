import os
import json
import logging
from typing import Optional, Any

logger = logging.getLogger("redis-cache")

class RedisCache:
    """Redis Cache wrapper with seamless in-memory fallback if Redis is unavailable."""

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://redis:6379/0")
        self.client = None
        self._memory_cache = {}
        self._init_redis()

    def _init_redis(self):
        try:
            import redis
            self.client = redis.Redis.from_url(self.redis_url, socket_timeout=2, decode_responses=True)
            self.client.ping()
            logger.info("Successfully connected to Redis at %s", self.redis_url)
        except Exception as e:
            logger.warning("Redis unavailable (%s). Falling back to in-memory fallback cache.", str(e))
            self.client = None

    def get(self, key: str) -> Optional[Any]:
        if self.client:
            try:
                val = self.client.get(key)
                if val:
                    return json.loads(val)
            except Exception as e:
                logger.warning("Redis get error for key %s: %s", key, str(e))
        
        # Fallback memory check
        return self._memory_cache.get(key)

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> bool:
        serialized = json.dumps(value)
        if self.client:
            try:
                self.client.setex(key, ttl_seconds, serialized)
                return True
            except Exception as e:
                logger.warning("Redis set error for key %s: %s", key, str(e))
        
        # Fallback memory store
        self._memory_cache[key] = value
        return True

    def delete(self, key: str) -> bool:
        if self.client:
            try:
                self.client.delete(key)
            except Exception:
                pass
        self._memory_cache.pop(key, None)
        return True

# Singleton cache instance
cache = RedisCache()
