from typing import Optional
from pydantic import BaseModel, Field

from .etc import PyObjectId

class ProductItem(BaseModel):
  id: Optional[PyObjectId] = Field(alias="_id", default=None)
  name: str
  date: str