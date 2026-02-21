from typing import Annotated, List, Optional
from fastapi import (
  HTTPException,
  APIRouter,
  status,
  Depends,
  Body,
  Security,
  Path
)
import json
from datetime import timedelta

from core.logger import logger
from core.config import settings
from core.database import MongoClient, RedisClient
from core.schemas.customers import CustomerBase, CustomerUpdate
from api.dependencies import (
  get_mongo_client,
  get_redis_client,
  get_current_user
)
from api.dependencies import limit_dependency
from crud import UserCRUD

router = APIRouter(tags=["Customers"])


@router.post("",
  status_code=status.HTTP_201_CREATED,
  dependencies=[Depends(limit_dependency)])
async def create_customer_account(
  create_customer: Annotated[CustomerBase, Body()],
  mongo: Annotated[MongoClient, Depends(get_mongo_client)],
):
  """
  Creates a customer account.
  """
  users_db = mongo.get_database("users")
  if await UserCRUD(users_db).find(username=create_customer.username):
    raise HTTPException(
      status_code=status.HTTP_409_CONFLICT,
      detail="User already exists."
    )
  
  # Create a customer account
  await UserCRUD(users_db).create(create_customer)

  return {"message": "The customer account was created successfully."}


@router.get("",
  status_code=status.HTTP_200_OK,
  response_model=List[CustomerBase],
  dependencies=[Security(get_current_user, scopes=["admin"]), Depends(limit_dependency)])
async def read_customers(
  mongo: Annotated[MongoClient, Depends(get_mongo_client)],   
):
  """
  Returns all customers.
  """
  users_db = mongo.get_database("users")
  return await UserCRUD(users_db).read_all("customers")


@router.get("/{username}",
  status_code=status.HTTP_200_OK,
  response_model=CustomerBase,
  dependencies=[Security(get_current_user, scopes=["admin"]), Depends(limit_dependency)])
async def read_customer(
  username: Annotated[str, Path()],
  mongo: Annotated[MongoClient, Depends(get_mongo_client)],
  redis: Annotated[RedisClient, Depends(get_redis_client)]
):
  """
  Returns customer profile by `username`.
  """
  redis_key = f"cache:user:{username}:profile"
  
  # Check if user data exists in Redis cache
  if (user_cache := await redis.get(redis_key)):
    try:
      # Parse user data to the JSON format
      user = json.loads(user_cache)
    except json.JSONDecodeError as e:
      logger.error({"message": "[x] An error occured while decoding customer's data from Redis cache.", "detail": str(e)}, exc_info=True)
      pass
  else:
    # Check if user exists in MongoDB
    users_db = mongo.get_database("users")
    if not (user := await UserCRUD(users_db).find(username=username)):
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Customer not found."
      )
      
    # Store user data in Redis cache 
    await redis.setex(redis_key, timedelta(minutes=settings.CACHE_EXPIRE_MINUTES).seconds, json.dumps(user, default=str))
  
  return user


@router.patch("/{username}",
  status_code=status.HTTP_200_OK,
  dependencies=[Security(get_current_user, scopes=["admin"])])
async def update_customer(
  username: Annotated[str, Path()],
  update_customer: Annotated[CustomerUpdate, Body()],
  mongo: Annotated[MongoClient, Depends(get_mongo_client)],
  redis: Annotated[RedisClient, Depends(get_redis_client)]
):
  """
  Updates customer data by `username`.
  """
  users_db = mongo.get_database("users")
  
  # Update the customer data
  if not (await UserCRUD(users_db).update(username=username, update=update_customer.model_dump(exclude_unset=True))):
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Customer not found."
    )
  
  # Delete user profile from Redis cache
  await redis.delete(f"cache:user:{username}:profile")

  return {"message": "The customer account has been updated."}


@router.delete("/{username}",
  status_code=status.HTTP_200_OK,
  dependencies=[Security(get_current_user, scopes=["admin"]), Depends(limit_dependency)])
async def delete_customer(
  username: Annotated[str, Path()],
  mongo: Annotated[MongoClient, Depends(get_mongo_client)],
  redis: Annotated[RedisClient, Depends(get_redis_client)]
):
  """
  Deletes an existing customer account.
  """

  # Delete the customer account
  users_db = mongo.get_database("users")
  if not await UserCRUD(users_db).delete(username=username):
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Customer not found."
    )

  # Delete user profile from Redis cache
  await redis.delete(f"cache:user:{username}:profile")

  return {"message": "The customer account was deleted successfully."}