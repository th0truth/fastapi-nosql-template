from fastapi import APIRouter

from core.config import settings

# Import API routers
from .v1 import api_v1_router
from .v2 import api_v2_router

# Initilize main router
api_main_router = APIRouter()

# Include API routers to the main router
api_main_router.include_router(api_v1_router, prefix=settings.API_V1_STR)
api_main_router.include_router(api_v2_router, prefix=settings.API_V2_STR)