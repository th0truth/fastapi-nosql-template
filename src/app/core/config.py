from pydantic_settings import BaseSettings, SettingsConfigDict
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

from pydantic import BaseModel, AnyUrl, BeforeValidator, computed_field
from typing import Any, TypeVar, Annotated, List, Dict, Optional

# Define a generic type variable
ModelType = TypeVar("TypeModel", bound=BaseModel)

# Parse middleware cors
def parse_cors(v: Any) -> List[str] | str:
  if isinstance(v, str) and not v.startswith("["):
    # Filter out comments (starting with #) and empty strings
    return [
      item.strip() 
      for item in v.split(",") 
      if item.strip() and not item.strip().startswith("#")
    ]
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
      extra="ignore"
  	)
    
  # App settings
  NAME: str = "FastAPI-NoSQL-Template"
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
  MONGO_HOSTNAME: str = "localhost"
  MONGO_PORT: int = 27017
  MONGO_USERNAME: str = "root"
  MONGO_PASSWORD: str = "root"
  MONGO_DATABASE: str = "nosql"
  MONGO_MAX_POOL_SIZE: int = 100
  MONGO_MIN_POOL_SIZE: int = 10
  MONGO_CONNECT_TIMEOUT_MS: int = 10000
  MONGO_SERVER_SELECTION_TIMEOUT_MS: int = 10000
  MONGO_RETRY_WRITES: bool = True

  @computed_field  # type: ignore[prop-decorator]
  @property
  def MONGO_URI(self) -> str:
    """Intelligently construct MongoDB URI."""
    if ".mongodb.net" in self.MONGO_HOSTNAME:
      # Atlas connection
      return f"mongodb+srv://{self.MONGO_USERNAME}:{self.MONGO_PASSWORD}@{self.MONGO_HOSTNAME}/{self.MONGO_DATABASE}"
    else:
      # Local/Standard connection
      auth = f"{self.MONGO_USERNAME}:{self.MONGO_PASSWORD}@" if self.MONGO_USERNAME and self.MONGO_PASSWORD else ""
      return f"mongodb://{auth}{self.MONGO_HOSTNAME}:{self.MONGO_PORT}/{self.MONGO_DATABASE}"
    
  # Redis settings
  REDIS_HOST: str = "localhost"
  REDIS_PORT: int = 6379
  REDIS_USERNAME: str = ""
  REDIS_PASSWORD: str = ""
  REDIS_DB: int = 0  
  
  CACHE_EXPIRE_MINUTES: int = 60
  
  # Rate limits
  RATE_LIMIT_ANONYMOUS: str = "100/minute"
  RATE_LIMIT_SELLER: str = "500/minute"
  RATE_LIMIT_CUSTOMER: str = "200/minute"

  # Google settings (OAuth)
  GOOGLE_CLIENT_ID: Optional[str] = None
  GOOGLE_CLIENT_SECRET: Optional[str] = None
  GOOGLE_FRONTEND_REDIRECT: Optional[str] = None

  SECRET_KEY: str = "changeme"


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
  JWT_EXPIRE_MINUTES: int = 60

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

if settings.REDIS_USERNAME or settings.REDIS_PASSWORD:
  REDIS_URI = f"redis://{settings.REDIS_USERNAME}:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
else:
  REDIS_URI = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"