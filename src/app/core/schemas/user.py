from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr
from .utils import PASSWORDstr

class UserInitial(BaseModel):
  first_name: str
  middle_name: str
  last_name: str

class UserBase(UserInitial):
  username: str
  email: EmailStr
  role: str
  account_date: datetime

class UserPrivate(UserBase):
  account_date: datetime
  email: Optional[EmailStr] = None
  password: Optional[PASSWORDstr] = None
  scopes: list

class UserUpdate(BaseModel):
  first_name: str = None
  middle_name: str = None
  last_name: str = None
  role: str = None
  scopes: list = None