from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from .utils import PyObjectId


class StudentBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    student_id: str
    enrollment_date: datetime
    status: str = "active"


class StudentItem(StudentBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)


class StudentCreate(StudentBase):
    created_at: datetime


class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None
