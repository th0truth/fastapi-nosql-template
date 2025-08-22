from pydantic_settings import BaseSettings, SettingsConfigDict
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

from pydantic import BaseModel
from typing import TypeVar

# Define a generic type variable
ModelType = TypeVar("TypeModel", bound=BaseModel)

# Generate private key for JWT
private_key = rsa.generate_private_key(
  public_exponent=65537,
  key_size=2048,
  backend=default_backend()
)

class Settings(BaseSettings): 
  model_config = SettingsConfigDict(
    env_file=".env",
    	env_ignore_empty=True,
      extra="ignore",
  	)
    
  # App settings
  NAME: str
  DESCRIPTION: str = ""
  SUMMARY: str = ""
  VERSION: str = "0.0.1"

  # Versions
  API_V1_STR: str = "/api/v1"
  API_V2_STR: str = "/api/v2"

  # MongoDB settings    
  MONGO_HOSTNAME: str
  MONGO_USERNAME: str
  MONGO_PASSWORD: str
  MONGO_DATABASE: str
  MONGO_MAX_POOL_SIZE: int = 100
  MONGO_MIN_POOL_SIZE: int = 10
  MONGO_CONNECT_TIMEOUT_MS: int = 10000
  MONGO_SERVER_SELECTION_TIMEOUT_MS: int = 10000
  MONGO_RETRY_WRITES: bool = True
    
  # Redis settings
  REDIS_HOST: str
  REDIS_PORT: int
  REDIS_USERNAME: str
  REDIS_PASSWORD: str
  REDIS_DB: int = 0  
  
  CACHE_EXPIRE_MINUTES: int
  
  # JWT settings
  JWT_ALGORITHM: str = "RS256"
  JWT_EXPIRE_MINUTES: int

  # Generate private key in PEM format
  PRIVATE_KEY_PEM: bytes = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
  )

  # Generate public key in PEM format   
  PUBLIC_KEY_PEM: bytes = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
  )

settings = Settings()