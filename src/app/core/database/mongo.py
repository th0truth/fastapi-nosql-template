from pymongo.asynchronous.mongo_client import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase 
from pymongo.errors import (
  ConfigurationError,
  ConnectionFailure,
  OperationFailure
)
from typing import Optional

from core.security.utils import DBConnection

from core.logger import logger
from core.config import settings

class MongoClient(DBConnection):
  _instance: Optional["MongoClient"] = None
  _client: Optional[AsyncMongoClient] = None

  def __new__(cls, *args, **kwargs):
    """Implement singleton pattern."""
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance

  @classmethod
  def get_database(cls, name: str) -> AsyncDatabase:
    """Get a MongoDB database."""
    if cls._client is None:
      raise ConnectionFailure("[x] Not connected to MongoDB.")
    return cls._client.get_database(name or settings.MONGO_DATABASE)

  @classmethod
  async def connect(cls):
    """
    Establish MongoDB connection.
    """
    try:
      cls._client = AsyncMongoClient(
        settings.MONGO_URI,
        maxPoolSize=settings.MONGO_MAX_POOL_SIZE,
        minPoolSize=settings.MONGO_MIN_POOL_SIZE,
        connectTimeoutMS=settings.MONGO_CONNECT_TIMEOUT_MS,
        serverSelectionTimeoutMS=settings.MONGO_SERVER_SELECTION_TIMEOUT_MS,
        retryWrites=settings.MONGO_RETRY_WRITES
      )
      await cls._client.admin.command("ping")
      logger.info("[+] Successfully connected to MongoDB.")
    except (ConfigurationError, OperationFailure) as e:
      logger.error({"message": "[x] Failed to connect to MongoDB.", "detail": str(e)}, exc_info=True)
      return

  @classmethod
  async def close(cls):
    """
    Close MongoDB connection.
    """
    if cls._client is not None:
      try:
        await cls._client.aclose()
        logger.info("[+] MongoDB connection closed.")
      except Exception as e:
        logger.error({"msg": "[x] Error closing MongoDB connection.", "detail": str(e)})
      finally:
        cls._client = None