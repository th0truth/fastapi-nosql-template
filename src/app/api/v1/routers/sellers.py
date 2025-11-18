from typing import Annotated
from fastapi import (
  HTTPException,
  APIRouter,
  status,
  Depends,
  Body
)
from core.db import MongoClient
from core.schemas.sellers import SellerBase
from api.dependencies import (
  get_mongo_client
)
from crud import UserCRUD

router = APIRouter(tags=["Sellers"])


@router.post("",
  status_code=status.HTTP_201_CREATED)
async def create_seller_account(
  create_seller: Annotated[SellerBase, Body()],
  mongo: Annotated[MongoClient, Depends(get_mongo_client)],
):
  """
  Creates a seller account.
  """
  users_db = mongo.get_database("users")
  if await UserCRUD(users_db).find(username=create_seller.username):
    raise HTTPException(
      status_code=status.HTTP_409_CONFLICT,
      detail="User already exists."
    )
  
  # Create a seller account
  await UserCRUD(users_db).create(create_seller)

  return {"message": "The seller account was created successfully."}