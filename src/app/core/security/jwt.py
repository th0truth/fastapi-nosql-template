from datetime import datetime, timedelta, timezone
from core.database import RedisClient
from typing import Optional
import uuid
import jwt

from core.logger import logger
from core.config import settings

# https://www.iana.org/assignments/jwt/jwt.xhtml#claims


class OAuthJWTBearer:
  """
    JSON Web Token (JWT) is a compact, URL-safe means of representing
    claims to be transferred between two parties.
  """

  @staticmethod
  def encode(payload: dict) -> dict:
    """Encodes a given payload into a JWT,
    Args:
        payload (dict): 
    Returns:
      dict:
        - jwt
        - jti
    """
    jti = str(uuid.uuid4().hex)
    payload.update(
      {"jti": jti,
      "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
      "iat": datetime.now(tz=timezone.utc)})
    return {
      "jwt": jwt.encode(payload=payload, key=settings.PRIVATE_KEY_PEM, algorithm=settings.JWT_ALGORITHM),
      "jti": jti
    }
  
  @staticmethod
  def decode(token: str) -> Optional[dict]:
    """
    Decodes a JWT, returning the payload.
    """
    try:
      return jwt.decode(jwt=token, key=settings.PUBLIC_KEY_PEM, algorithms=settings.JWT_ALGORITHM)
    except (jwt.DecodeError, jwt.ExpiredSignatureError) as e:
      logger.exception({"message": "Unable to decode a JWT.", "detail": str(e)}, exc_info=False)
      return
      
  @staticmethod
  async def refresh(payload: dict) -> str:
    """
    Refreshes the claims of a JWT, updating expiry time.
    """
    jti = str(uuid.uuid4().hex)
    payload.update(
      {"jti": jti, "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)})
    return jwt.encode(payload=payload, key=settings.PRIVATE_KEY_PEM, algorithm=settings.JWT_ALGORITHM)
  
  @staticmethod
  async def add_jti_to_blacklist(redis: RedisClient, *, jti: str, exp: int) -> bool:
    """
    Adds `jti` to the blacklist.
    """
    now = int(datetime.now(tz=timezone.utc).timestamp())
    ttl = exp - now
    if ttl < 0:
      logger.warning(f"Token with jti={jti} is already expired. Skipping blacklist.")
      return False
      
    # Store jti in the blacklist entry in Redis
    await redis.setex(f"session:blacklist:jti:{jti}", ttl, "Revoked")
    return True
  
  @staticmethod
  async def is_jti_in_blacklist(redis: RedisClient, *, jti: str) -> bool:
    """
    Checks if the `jti` is in blacklist.
    """
    return await redis.exists(f"session:blacklist:jti:{jti}")
