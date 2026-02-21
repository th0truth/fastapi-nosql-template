from typing import List, Optional
from core.database import MongoClient
from crud import UserCRUD, ProductCRUD

async def get_users(role: str) -> List[dict]:
  """Fetch all users by role."""
  if not MongoClient._client:
    await MongoClient.connect()
  
  users_db = MongoClient._client.get_database("users")
  return await UserCRUD(users_db).read_all(role)

async def get_user(username: str) -> Optional[dict]:
  """Fetch user by username."""
  if not MongoClient._client:
    await MongoClient.connect()
    
  users_db = MongoClient._client.get_database("users")
  return await UserCRUD(users_db).find(username=username)

async def get_products(category: str) -> List[dict]:
  """Fetch products by category."""
  if not MongoClient._client:
    await MongoClient.connect()
    
  products_db = MongoClient._client.get_database("products")
  return await ProductCRUD(products_db).read_all(category)