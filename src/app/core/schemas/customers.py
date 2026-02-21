from typing import Optional
from pydantic import BaseModel
from .user import UserPrivate

class CustomerBase(UserPrivate):
  role: str = "customers"
  scopes: list = [
    "customer"
  ]

class CustomerUpdate(BaseModel):
  first_name: Optional[str] = None
  middle_name: Optional[str] = None
  last_name: Optional[str] = None