from typing import Optional
from pydantic import BaseModel

from .user import UserPrivate

class SellerBase(UserPrivate):
  role: str = "sellers"
  scopes: list = [
    "seller"
  ]
  business_email: Optional[str] = None
  business_address: Optional[str] = None
  identity_card: str
  business_name: str
  storefront_name: str
  address: str

class SellerUpdate(BaseModel):
  first_name: Optional[str] = None
  middle_name: Optional[str] = None
  last_name: Optional[str] = None
  business_email: Optional[str] = None
  business_address: Optional[str] = None
  identity_card: Optional[str] = None
  business_name: Optional[str] = None
  storefront_name: Optional[str] = None
  address: Optional[str] = None