from fastapi import APIRouter
from .routers import (
  auth,
  user,
  users
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(user.router, prefix="/user")
api_router.include_router(users.router, prefix="/users")