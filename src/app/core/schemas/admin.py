from .user import UserPrivate

class AdminBase(UserPrivate):
  role: str = "admins"
  scopes: list = [
    "admin"
  ]