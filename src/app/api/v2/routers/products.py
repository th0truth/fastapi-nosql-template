from typing import Annotated, Optional, List
from anyio import get_current_task
from fastapi import (
  APIRouter,
  HTTPException,
  Security,
  status,
  Depends,
  Path,
  Query
)
from core.db import MongoClient
from core.schemas.sellers import SellerBase
from core.schemas.products import ProductItem
from api.dependencies import (
  get_mongo_client,
  get_current_user
)
from crud import BaseCRUD

router = APIRouter(tags=["Products"])

@router.get("/{category}/all",
  status_code=status.HTTP_200_OK,
  response_model=List[ProductItem],
  dependencies=[Security(get_current_user, scopes=["admin"])])
async def get_all_products(
  category: Annotated[str, Path()],
  mongo: Annotated[MongoClient, Depends(get_mongo_client)],
  length: Annotated[Optional[int], Query()] = None,
  offset: Annotated[int, Query()] = 0
):
  """
  Returns list of all .
  """
  products_db = mongo.get_database("products")
  if not (products := await BaseCRUD(products_db).read_all(category, offset=offset, length=length)):
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Products not found."
    )
  
  return products

@router.post("/{category}/add",
  status_code=status.HTTP_201_CREATED)
async def add_product(
  category: Annotated[str, Path()],
  user: Annotated[dict, Security(get_mongo_client, scopes=["seller", "admin"])],
  mongo: Annotated[MongoClient, Depends(get_mongo_client)]
):
  """
  Add product to the store.
  """

  products_db = mongo.get_database("products")
  if category not in await products_db.list_collection_names():
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Category not found."
    )