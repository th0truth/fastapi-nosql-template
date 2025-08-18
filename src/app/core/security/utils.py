from passlib.context import CryptContext

class Hash:
  context = CryptContext(schemes=["argon2"], deprecated="auto")

  @classmethod
  def hash(cls, plain: str) -> str:
    """Return hashed password."""
    return cls.context.hash(secret=plain)
          
  @classmethod
  def verify(cls, plain: str, hashed: str) -> bool:
    """Return bool type of the verified password."""
    return cls.context.verify(secret=plain, hash=hashed)