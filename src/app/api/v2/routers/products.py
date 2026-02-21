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
from core.schemas.products import ProductCreate, ProductItem, ProductUpdate
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
  user: Annotated[dict, Security(get_current_user, scopes=["seller"])],
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
  Returns list of all products in a category.
  """
  products_db = mongo.get_database("products")
  if not (products := await ProductCRUD(products_db).read_all(category, offset=offset, length=length)):
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Products not found."
    )
  
  return products


@router.get("/{category}/{product_id}",
  status_code=status.HTTP_200_OK,
  response_model=ProductItem,
  dependencies=[Depends(limit_dependency)])
async def get_product(
  category: Annotated[str, Path()],
  product_id: Annotated[str, Path()],
  mongo: Annotated[MongoClient, Depends(get_mongo_client)],
):
  """
  Returns product by ID.
  """
  products_db = mongo.get_database("products")
  if not (product := await ProductCRUD(products_db).get_product(category, product_id)):
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Product not found."
    )
  
  return product


@router.patch("/{category}/{product_id}",
  status_code=status.HTTP_200_OK,
  dependencies=[Security(get_current_user, scopes=["seller"])])
async def update_product(
  category: Annotated[str, Path()],
  product_id: Annotated[str, Path()],
  product_update: Annotated[ProductUpdate, Body()],
  user: Annotated[dict, Security(get_current_user, scopes=["seller"])],
  mongo: Annotated[MongoClient, Depends(get_mongo_client)],
):
  """
  Updates product by ID.
  """
  products_db = mongo.get_database("products")
  
  if not (await ProductCRUD(products_db).update_product(category, product_id, product_update.model_dump(exclude_unset=True))):
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Product not found."
    )
  
  return {"message": "The product has been updated."}


@router.delete("/{category}/{product_id}",
  status_code=status.HTTP_200_OK,
  dependencies=[Security(get_current_user, scopes=["admin", "seller"])])
async def delete_product(
  category: Annotated[str, Path()],
  product_id: Annotated[str, Path()],
  user: Annotated[dict, Security(get_current_user, scopes=["admin", "seller"])],
  mongo: Annotated[MongoClient, Depends(get_mongo_client)],
):
  """
  Deletes product by ID.
  """
  products_db = mongo.get_database("products")
  
  if not await ProductCRUD(products_db).delete_product(category, product_id):
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Product not found."
    )
  
  return {"message": "The product was deleted successfully."}