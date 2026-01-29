from pydantic_settings import BaseSettings, SettingsConfigDict
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

from pydantic import BaseModel, AnyUrl, BeforeValidator, computed_field
from typing import Any, TypeVar, Annotated, List, Dict

# Define a generic type variable
ModelType = TypeVar("TypeModel", bound=BaseModel)

# Parse middleware cors
def parse_cors(v: Any) -> List[str] | str:
  if isinstance(v, str) and not v.startswith("["):
    return [i.strip() for i in v.split(",")]
  elif isinstance(v, list | str):
    return v
  raise ValueError(v)

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

  FRONTEND_HOST: str = "http://localhost:8000"

  BACKEND_CORS_ORIGINS: Annotated[
    List[AnyUrl] | str, BeforeValidator(parse_cors)
  ] = []
  
  @computed_field  # type: ignore[prop-decorator]
  @property
  def all_cors_origins(self) -> List[str]:
    return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
      self.FRONTEND_HOST
    ]

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
  
  # Rate limits
  RATE_LIMIT_ANONYMOUS: str
  RATE_LIMIT_SELLER: str
  RATE_LIMIT_CUSTOMER: str

  @computed_field  # type: ignore[prop-decorator]
  @property
  def RATE_LIMITS(self) -> Dict[str, str]:
    return {
    "anonymous": self.RATE_LIMIT_ANONYMOUS,
    "sellers": self.RATE_LIMIT_SELLER,
    "customers": self.RATE_LIMIT_ANONYMOUS
  }

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

REDIS_URI = f"redis://{settings.REDIS_USERNAME}:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"