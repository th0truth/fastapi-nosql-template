from typing import Optional

from .user import UserPrivate

class SellerBase(UserPrivate):
  role: str = "seller"
  scopes: list = [
    "seller"
  ]
  business_email: Optional[str] = None
  business_address: Optional[str] = None
  identity_card: str
  business_name: str
  storefront_name: str
  address: str