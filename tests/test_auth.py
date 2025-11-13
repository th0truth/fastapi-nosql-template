"""
Tests for authentication endpoints.
"""
import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import timedelta
from fastapi import status
from httpx import AsyncClient

from app.main import app
from app.core.security.jwt import OAuthJWTBearer
from app.core.security.utils import Hash
from tests.conftest import UserFactory


@pytest.mark.asyncio
@pytest.mark.auth
class TestAuthLogin:
    """Tests for POST /api/v1/auth/login endpoint."""
    
    async def test_login_success(
        self,
        async_client: AsyncClient,
        override_mongo_dependency,
        override_redis_dependency,
        mock_mongo_client,
        mock_redis_client,
        test_user
    ):
        """Test successful login with valid credentials."""
        # Setup mocks
        mock_db = mock_mongo_client.get_database("users")
        mock_users_collection = mock_db["users"]
        
        # Mock user in database with hashed password
        user_in_db = test_user.copy()
        user_in_db["password"] = Hash.hash("testpassword123")
        
        # Mock find_one to return user
        mock_users_collection.find_one = AsyncMock(return_value=user_in_db)
        
        # Mock Redis setex
        mock_redis_client.setex = AsyncMock(return_value=True)
        
        # Make request
        form_data = {
            "username": test_user["username"],
            "password": "testpassword123"
        }
        
        response = await async_client.post(
            "/api/v1/auth/login",
            data=form_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["role"] == test_user["role"]
        assert mock_redis_client.setex.called
    
    async def test_login_invalid_credentials(
        self,
        async_client: AsyncClient,
        override_mongo_dependency,
        override_redis_dependency,
        mock_mongo_client,
        test_user
    ):
        """Test login with invalid credentials."""
        mock_db = mock_mongo_client.get_database("users")
        mock_users_collection = mock_db["users"]
        
        # Mock user in database
        user_in_db = test_user.copy()
        user_in_db["password"] = Hash.hash("correctpassword")
        
        # Mock find_one to return user
        mock_users_collection.find_one = AsyncMock(return_value=user_in_db)
        
        form_data = {
            "username": test_user["username"],
            "password": "wrongpassword"
        }
        
        response = await async_client.post(
            "/api/v1/auth/login",
            data=form_data
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Couldn't validate credentials" in response.json()["detail"]
    
    async def test_login_user_not_found(
        self,
        async_client: AsyncClient,
        override_mongo_dependency,
        override_redis_dependency,
        mock_mongo_client
    ):
        """Test login with non-existent user."""
        mock_db = mock_mongo_client.get_database("users")
        mock_users_collection = mock_db["users"]
        
        # Mock find_one to return None
        mock_users_collection.find_one = AsyncMock(return_value=None)
        
        form_data = {
            "username": "nonexistent",
            "password": "password123"
        }
        
        response = await async_client.post(
            "/api/v1/auth/login",
            data=form_data
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
@pytest.mark.auth
class TestAuthToken:
    """Tests for POST /api/v1/auth/token endpoint."""
    
    async def test_token_refresh_success(
        self,
        async_client: AsyncClient,
        override_redis_dependency,
        mock_redis_client,
        auth_token,
        test_user
    ):
        """Test successful token refresh."""
        # Mock Redis - token not in blacklist
        mock_redis_client.exists = AsyncMock(return_value=0)
        mock_redis_client.setex = AsyncMock(return_value=True)
        
        response = await async_client.post(
            "/api/v1/auth/token",
            headers={"Authorization": json.dumps({"access_token": auth_token, "token_type": "bearer"})}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["role"] == test_user["role"]
        # Verify token was added to blacklist
        assert mock_redis_client.setex.called
    
    async def test_token_refresh_invalid_token(
        self,
        async_client: AsyncClient,
        override_redis_dependency,
        mock_redis_client
    ):
        """Test token refresh with invalid token."""
        response = await async_client.post(
            "/api/v1/auth/token",
            headers={"Authorization": json.dumps({"access_token": "invalid_token", "token_type": "bearer"})}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid token" in response.json()["detail"]
    
    async def test_token_refresh_revoked_token(
        self,
        async_client: AsyncClient,
        override_redis_dependency,
        mock_redis_client,
        auth_token
    ):
        """Test token refresh with revoked token."""
        # Mock Redis - token in blacklist
        mock_redis_client.exists = AsyncMock(return_value=1)
        
        response = await async_client.post(
            "/api/v1/auth/token",
            headers={"Authorization": json.dumps({"access_token": auth_token, "token_type": "bearer"})}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Token has been revoked" in response.json()["detail"]
    
    async def test_token_refresh_expired_token(
        self,
        async_client: AsyncClient,
        override_redis_dependency,
        mock_redis_client,
        expired_token
    ):
        """Test token refresh with expired token."""
        response = await async_client.post(
            "/api/v1/auth/token",
            headers={"Authorization": json.dumps({"access_token": expired_token, "token_type": "bearer"})}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
@pytest.mark.auth
class TestAuthLogout:
    """Tests for POST /api/v1/auth/logout endpoint."""
    
    async def test_logout_success(
        self,
        async_client: AsyncClient,
        override_redis_dependency,
        mock_redis_client,
        auth_token,
        test_user
    ):
        """Test successful logout."""
        # Mock Redis - token not in blacklist
        mock_redis_client.exists = AsyncMock(return_value=0)
        mock_redis_client.setex = AsyncMock(return_value=True)
        
        # Mock get_current_user dependency
        from app.api.dependencies import get_current_user
        async def mock_get_current_user():
            return test_user
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            response = await async_client.post(
                "/api/v1/auth/logout",
                headers={"Authorization": json.dumps({"access_token": auth_token, "token_type": "bearer"})}
            )
            
            assert response.status_code == status.HTTP_200_OK
            assert "Successfully logged out" in response.json()["message"]
            assert mock_redis_client.setex.called
        finally:
            app.dependency_overrides.clear()
    
    async def test_logout_revoked_token(
        self,
        async_client: AsyncClient,
        override_redis_dependency,
        mock_redis_client,
        auth_token,
        test_user
    ):
        """Test logout with already revoked token."""
        # Mock Redis - token in blacklist
        mock_redis_client.exists = AsyncMock(return_value=1)
        
        # Mock get_current_user dependency
        from app.api.dependencies import get_current_user
        async def mock_get_current_user():
            return test_user
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            response = await async_client.post(
                "/api/v1/auth/logout",
                headers={"Authorization": json.dumps({"access_token": auth_token, "token_type": "bearer"})}
            )
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Token has been revoked" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()
    
    async def test_logout_unauthorized(
        self,
        async_client: AsyncClient,
        override_redis_dependency,
        mock_redis_client
    ):
        """Test logout without authentication."""
        response = await async_client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": json.dumps({"access_token": "invalid_token", "token_type": "bearer"})}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
