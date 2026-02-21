from fastapi import APIRouter
from .routers import (
  health,
  google_auth,
  auth,
  user,
  users,
  sellers,
  customers,
  admin
)

# Initialize v1 router
api_v1_router = APIRouter()

# Include routers
api_v1_router.include_router(health.router, prefix="/health")
api_v1_router.include_router(google_auth.router, prefix="/auth")
api_v1_router.include_router(auth.router, prefix="/auth")
api_v1_router.include_router(user.router, prefix="/user")
api_v1_router.include_router(users.router, prefix="/users")
api_v1_router.include_router(sellers.router, prefix="/sellers")
api_v1_router.include_router(customers.router, prefix="/customers")
api_v1_router.include_router(admin.router, prefix="/admin")