"""
Pytest configuration and shared fixtures.
"""
import sys
from pathlib import Path

# Add src and src/app directories to Python path for imports
# The codebase uses relative imports (e.g., "from core.config"), so we need
# both src (for app.* imports) and src/app (for relative imports) on the path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
src_app_path = project_root / "src" / "app"
if str(src_app_path) not in sys.path:
    sys.path.insert(0, str(src_app_path))
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import pytest
import json
from typing import AsyncGenerator, Dict, Any, Optional
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from httpx import AsyncClient
# ASGITransport is available in httpx >= 0.24.0
try:
    from httpx import ASGITransport
    HAS_ASGI_TRANSPORT = True
except ImportError:
    HAS_ASGI_TRANSPORT = False
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.mongo_client import AsyncMongoClient
import redis.asyncio as aioredis

from app.main import app
from app.core.db import MongoClient, RedisClient
from app.core.security.jwt import OAuthJWTBearer
from app.core.schemas.user import UserBase, UserPrivate
from app.core.schemas.sellers import SellerBase
from app.core.schemas.products import ProductItem
from app.api.dependencies import get_mongo_client, get_redis_client


# ============================================================================
# Mock Database Fixtures
# ============================================================================
# 
# Mocking Strategy:
# 1. MongoDB: Mock AsyncMongoClient -> Mock Database -> Mock Collections
# 2. Redis: Mock aioredis.Redis client
# 3. Use FastAPI dependency_overrides to inject mocks into the app
# 4. Tests configure mock return values for specific operations
# 
# This approach:
# - No real database instances required
# - Fast test execution
# - Deterministic test results
# - Full control over database responses

@pytest.fixture
def mock_redis_client():
    """Mock Redis client using AsyncMock."""
    mock_client = AsyncMock(spec=aioredis.Redis)
    return mock_client


@pytest.fixture
def mock_mongo_database():
    """Mock MongoDB database with collections.
    
    Creates a mock database that can return mock collections.
    Collections are accessed via db[collection_name] syntax.
    """
    mock_db = AsyncMock(spec=AsyncDatabase)
    
    # Mock collections - each collection is a separate AsyncMock
    mock_users_collection = AsyncMock(spec=AsyncCollection)
    mock_sellers_collection = AsyncMock(spec=AsyncCollection)
    mock_user_collection = AsyncMock(spec=AsyncCollection)  # For role-based collections
    mock_admin_collection = AsyncMock(spec=AsyncCollection)
    mock_products_collection = AsyncMock(spec=AsyncCollection)
    mock_electronics_collection = AsyncMock(spec=AsyncCollection)
    mock_clothing_collection = AsyncMock(spec=AsyncCollection)
    
    # Setup collection access via db[collection_name]
    def get_collection(name: str):
        collection_map = {
            "users": mock_users_collection,
            "sellers": mock_sellers_collection,
            "user": mock_user_collection,  # Role-based collection
            "admin": mock_admin_collection,  # Role-based collection
            "products": mock_products_collection,
            "electronics": mock_electronics_collection,
            "clothing": mock_clothing_collection,
        }
        return collection_map.get(name, AsyncMock(spec=AsyncCollection))
    
    mock_db.__getitem__ = MagicMock(side_effect=get_collection)
    mock_db.list_collection_names = AsyncMock(return_value=["users", "sellers", "user", "admin", "products", "electronics", "clothing"])
    
    return mock_db


@pytest.fixture
def mock_mongo_client(mock_mongo_database):
    """Mock AsyncMongoClient instance.
    
    This is the top-level MongoDB client that has a get_database() method.
    Returns the mock_database when get_database() is called.
    """
    mock_client = AsyncMock(spec=AsyncMongoClient)
    mock_client.get_database = MagicMock(return_value=mock_mongo_database)
    return mock_client


@pytest.fixture
async def override_mongo_dependency(mock_mongo_client):
    """Override MongoDB dependency with mock."""
    async def _get_mongo_client():
        yield mock_mongo_client
    
    app.dependency_overrides[get_mongo_client] = _get_mongo_client
    yield mock_mongo_client
    app.dependency_overrides.clear()


@pytest.fixture
async def override_redis_dependency(mock_redis_client):
    """Override Redis dependency with mock."""
    async def _get_redis_client():
        yield mock_redis_client
    
    app.dependency_overrides[get_redis_client] = _get_redis_client
    yield mock_redis_client
    app.dependency_overrides.clear()


# ============================================================================
# Test Client Fixtures
# ============================================================================

@pytest.fixture
def client():
    """Synchronous test client."""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Asynchronous test client."""
    # Use ASGITransport for httpx >= 0.24.0
    if HAS_ASGI_TRANSPORT:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
    else:
        # Fallback: Use TestClient wrapped in async methods for older httpx versions
        # This maintains the async interface while using sync TestClient internally
        from fastapi.testclient import TestClient
        
        class AsyncTestClientWrapper:
            """Async wrapper around TestClient for compatibility."""
            def __init__(self, sync_client: TestClient):
                self._client = sync_client
            
            async def get(self, *args, **kwargs):
                return self._client.get(*args, **kwargs)
            
            async def post(self, *args, **kwargs):
                return self._client.post(*args, **kwargs)
            
            async def patch(self, *args, **kwargs):
                return self._client.patch(*args, **kwargs)
            
            async def delete(self, *args, **kwargs):
                return self._client.delete(*args, **kwargs)
            
            async def put(self, *args, **kwargs):
                return self._client.put(*args, **kwargs)
            
            async def __aenter__(self):
                return self
            
            async def __aexit__(self, *args):
                pass
        
        client = TestClient(app)
        wrapper = AsyncTestClientWrapper(client)
        yield wrapper


# ============================================================================
# Test Data Factories
# ============================================================================

class UserFactory:
    """Factory for creating test user data."""
    
    @staticmethod
    def create_user(
        username: str = "testuser",
        email: str = "test@example.com",
        role: str = "user",
        password: str = "testpassword123",
        scopes: list = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a test user dictionary."""
        if scopes is None:
            scopes = ["user"]
        
        user = {
            "username": username,
            "email": email,
            "role": role,
            "password": password,
            "scopes": scopes,
            "first_name": kwargs.get("first_name", "Test"),
            "middle_name": kwargs.get("middle_name", "Middle"),
            "last_name": kwargs.get("last_name", "User"),
            "account_date": kwargs.get("account_date", datetime.now(timezone.utc)),
            **kwargs
        }
        return user
    
    @staticmethod
    def create_admin_user(**kwargs) -> Dict[str, Any]:
        """Create an admin user."""
        return UserFactory.create_user(
            username=kwargs.get("username", "admin"),
            email=kwargs.get("email", "admin@example.com"),
            role="admin",
            scopes=["admin"],
            **kwargs
        )
    
    @staticmethod
    def create_seller_user(**kwargs) -> Dict[str, Any]:
        """Create a seller user."""
        return UserFactory.create_user(
            username=kwargs.get("username", "seller"),
            email=kwargs.get("email", "seller@example.com"),
            role="sellers",
            scopes=["seller"],
            business_name=kwargs.get("business_name", "Test Business"),
            storefront_name=kwargs.get("storefront_name", "Test Store"),
            identity_card=kwargs.get("identity_card", "ID123456"),
            address=kwargs.get("address", "123 Test St"),
            **kwargs
        )


class ProductFactory:
    """Factory for creating test product data."""
    
    @staticmethod
    def create_product(
        brand: str = "TestBrand",
        title: str = "Test Product",
        description: str = "Test Description",
        price: int = 100,
        category: str = "electronics",
        **kwargs
    ) -> Dict[str, Any]:
        """Create a test product dictionary."""
        return {
            "_id": kwargs.get("_id", "507f1f77bcf86cd799439011"),
            "brand": brand,
            "title": title,
            "description": description,
            "price": price,
            "category": category,
            "date": kwargs.get("date", datetime.now(timezone.utc)),
            **kwargs
        }


# ============================================================================
# Authentication Fixtures
# ============================================================================

@pytest.fixture
def test_user() -> Dict[str, Any]:
    """Standard test user."""
    return UserFactory.create_user()


@pytest.fixture
def test_admin_user() -> Dict[str, Any]:
    """Admin test user."""
    return UserFactory.create_admin_user()


@pytest.fixture
def test_seller_user() -> Dict[str, Any]:
    """Seller test user."""
    return UserFactory.create_seller_user()


@pytest.fixture
def auth_token(test_user: Dict[str, Any]) -> str:
    """Generate a JWT token for test user."""
    payload = {
        "sub": test_user["username"],
        "role": test_user["role"],
        "scopes": test_user["scopes"]
    }
    token_data = OAuthJWTBearer.encode(payload=payload)
    return token_data["jwt"]


@pytest.fixture
def admin_token(test_admin_user: Dict[str, Any]) -> str:
    """Generate a JWT token for admin user."""
    payload = {
        "sub": test_admin_user["username"],
        "role": test_admin_user["role"],
        "scopes": test_admin_user["scopes"]
    }
    token_data = OAuthJWTBearer.encode(payload=payload)
    return token_data["jwt"]


@pytest.fixture
def seller_token(test_seller_user: Dict[str, Any]) -> str:
    """Generate a JWT token for seller user."""
    payload = {
        "sub": test_seller_user["username"],
        "role": test_seller_user["role"],
        "scopes": test_seller_user["scopes"]
    }
    token_data = OAuthJWTBearer.encode(payload=payload)
    return token_data["jwt"]


@pytest.fixture
def expired_token() -> str:
    """Generate an expired JWT token."""
    payload = {
        "sub": "testuser",
        "role": "user",
        "scopes": ["user"],
        "exp": datetime.now(timezone.utc) - timedelta(minutes=10),
        "iat": datetime.now(timezone.utc) - timedelta(minutes=20)
    }
    from app.core.config import settings
    import jwt
    return jwt.encode(payload=payload, key=settings.PRIVATE_KEY_PEM, algorithm=settings.JWT_ALGORITHM)


# ============================================================================
# Mock Setup Helpers
# ============================================================================

def setup_mongo_user_find(mock_db: AsyncMock, user: Dict[str, Any], found: bool = True):
    """Setup MongoDB find mock for user lookup."""
    mock_collection = AsyncMock()
    if found:
        mock_collection.find_one = AsyncMock(return_value=user)
    else:
        mock_collection.find_one = AsyncMock(return_value=None)
    
    def get_collection(name: str):
        if name in ["users", "sellers", "admin"]:
            return mock_collection
        return AsyncMock()
    
    mock_db.__getitem__ = MagicMock(side_effect=get_collection)
    mock_db.list_collection_names = AsyncMock(return_value=["users", "sellers", "admin"])


def setup_redis_cache(mock_redis: AsyncMock, key: str, value: Optional[str] = None):
    """Setup Redis cache mock."""
    if value:
        mock_redis.get = AsyncMock(return_value=value)
    else:
        mock_redis.get = AsyncMock(return_value=None)
    mock_redis.setex = AsyncMock(return_value=True)
    mock_redis.delete = AsyncMock(return_value=1)
    mock_redis.exists = AsyncMock(return_value=0)
    mock_redis.setex = AsyncMock(return_value=True)

