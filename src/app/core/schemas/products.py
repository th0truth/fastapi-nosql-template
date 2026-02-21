from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from .utils import PyObjectId

class ProductBase(BaseModel):
  category: str
  item: str
  brand: str
  title: str
  description: str
  price: int

class ProductItem(ProductBase):
  id: Optional[PyObjectId] = Field(alias="_id", default=None)
  category: str

class ProductCreate(ProductBase):
  date: datetime

class ProductUpdate(BaseModel):
  item: Optional[str] = None
  brand: Optional[str] = None
  title: Optional[str] = None
  description: Optional[str] = None
  price: Optional[int] = None