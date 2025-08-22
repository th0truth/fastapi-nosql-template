from typing import Annotated
from fastapi import (
  HTTPException,
  APIRouter,
  status,
  Depends,
  Body
)
from core.schemas.etc import UpdateEmail, UpdatePassword, PasswordRecovery
from core.security.utils import Hash
from core.db import MongoClient
from redis.asyncio import Redis
from api.dependencies import (
  get_mongo_client,
  get_redis_client,
  get_current_user
)

router = APIRouter(tags=["Items"])

@router.get("/items")
async def get_items():
  pass