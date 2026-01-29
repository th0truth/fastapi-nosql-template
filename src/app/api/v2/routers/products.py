from typing import Annotated, Optional, List
from fastapi import (
  APIRouter,
  HTTPException,
  Security,
  status,
  Depends,
  Path,
  Query,
  Body
)
from core.database import MongoClient
from core.schemas.products import ProductCreate, ProductItem
from core.schemas.sellers import SellerBase
from api.dependencies import (
  get_mongo_client,
  get_current_user
)
from api.dependencies import limit_dependency
from crud import ProductCRUD

router = APIRouter(tags=["Products"])


@router.post("/",
  status_code=status.HTTP_201_CREATED,
  dependencies=[Depends(limit_dependency)],
  response_model=ProductItem)
async def create_product(
  product: Annotated[ProductCreate, Body()],
  user: Annotated[dict, Security(get_mongo_client, scopes=["seller"])],
  mongo: Annotated[MongoClient, Depends(get_mongo_client)]
):
  """
  Add product to the store.
  """

  products_db = mongo.get_database("products")
  if product.category not in await products_db.list_collection_names():
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Category not found."
    )
  
  await ProductCRUD(products_db).create(product.category, product)
  return product


@router.get("/{category}",
  status_code=status.HTTP_200_OK,
  response_model=List[ProductItem],
  dependencies=[Security(get_current_user, scopes=["admin"]), Depends(limit_dependency)])
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
  if not (products := await ProductCRUD(products_db).read_all(category, offset=offset, length=length)):
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Products not found."
    )
  
  return products