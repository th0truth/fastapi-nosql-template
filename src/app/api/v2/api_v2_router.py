from fastapi import APIRouter
from .routers import (
  items
)

# Initilize v2 router
api_v2_router = APIRouter()

# Include routers
api_v2_router.include_router(items.router, prefix="/items")