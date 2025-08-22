from fastapi import APIRouter
from .routers import (
  auth,
  user,
  users
)

# Initilize v1 router
api_v1_router = APIRouter()

# Include routers
api_v1_router.include_router(auth.router, prefix="/auth")
api_v1_router.include_router(user.router, prefix="/user")
api_v1_router.include_router(users.router, prefix="/users")