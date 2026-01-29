from .user import UserPrivate

class CustomerBase(UserPrivate):
  role: str = "customers"
  scopes: list = [
    "customer"
  ]