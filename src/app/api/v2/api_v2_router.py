from fastapi import APIRouter
from .routers import (
  products
)

# Initilize v2 router
api_v2_router = APIRouter()

# Include routers
api_v2_router.include_router(products.router, prefix="/products")