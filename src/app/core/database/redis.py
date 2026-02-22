from typing import Optional
import redis.asyncio as aioredis

from core.security.utils import DBConnection

from core.logger import logger
from core.config import settings


class RedisClient(DBConnection):
  _instance: Optional["RedisClient"] = None
  _client: Optional[aioredis.Redis] = None

  @classmethod
  def __new__(cls, *args, **kwargs):
    """Implement singleton pattern."""
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance
  
  @classmethod
  async def connect(cls):
    """
    Establish Redis connection.
    """
    try:
      cls._client = aioredis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        username=settings.REDIS_USERNAME,
        password=settings.REDIS_PASSWORD,
        decode_responses=True,
        db=settings.REDIS_DB
      )
      alive = await cls._client.ping()
      if not alive:
        logger.error({"message": f"Couldn't connect to Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}."}, exc_info=True)
        return
      logger.info("[+] Successfully connected to Redis.")
      return cls._instance
    except aioredis.ConnectionError as e:
      logger.error({"message": "An error occured while connecting to Redis.", "detail": str(e)})
      return
  
  @classmethod
  async def close(cls):
    """
    Close Redis connection.
    """
    if cls._client is not None:
      try:
        await cls._client.aclose()
        logger.info("[+] Redis connection closed.")
      except Exception as e:
        logger.error({"message": "[x] Error closing Redis connection.", "detail": str(e)}, exc_info=True)
      finally:
        cls._client = None

  # Proxy methods to the underlying Redis client
  def __getattr__(self, name) -> aioredis.Redis:
    """Delegate attribute access to the underlying Redis client."""
    if self._client is None:
      raise RuntimeError("Redis client not connected. Call connect() first.")
    return getattr(self._client, name)

  async def get(self, key: str) -> Optional[str]:
    "Return the value at key name, or None if the key doesn't exist"
    return await self._client.get(key)
  
  async def setex(self, key: str, time: int, value: str) -> bool:
    """Set the value of key name to value that expires in time seconds."""
    return await self._client.setex(key, time, value)
  
  async def delete(self, *keys: str):
    """Delete keys from Redis."""
    return await self._client.delete(*keys)
  
  async def exists(self, *keys: str) -> int:
    """Check if keys exist."""
    return await self._client.exists(*keys)
