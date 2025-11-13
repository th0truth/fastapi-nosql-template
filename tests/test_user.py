"""
Tests for user endpoints (current user operations).
"""
import pytest
import json
from unittest.mock import AsyncMock
from fastapi import status
from httpx import AsyncClient

from app.main import app
from app.core.security.utils import Hash
from tests.conftest import UserFactory


@pytest.mark.asyncio
@pytest.mark.users
class TestGetCurrentUser:
    """Tests for GET /api/v1/user/me endpoint."""
    
    async def test_get_current_user_success(
        self,
        async_client: AsyncClient,
        test_user,
        auth_token
    ):
        """Test getting current user profile."""
        # Mock get_current_user dependency
        from app.api.dependencies import get_current_user
        async def mock_get_current_user():
            return test_user
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            response = await async_client.get(
                "/api/v1/user/me",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["username"] == test_user["username"]
            assert "password" not in data
        finally:
            app.dependency_overrides.clear()
    
    async def test_get_current_user_unauthorized(
        self,
        async_client: AsyncClient
    ):
        """Test getting current user without authentication."""
        response = await async_client.get("/api/v1/user/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
@pytest.mark.users
class TestUpdateEmail:
    """Tests for PATCH /api/v1/user/email/update endpoint."""
    
    async def test_update_email_success(
        self,
        async_client: AsyncClient,
        override_mongo_dependency,
        override_redis_dependency,
        mock_mongo_client,
        mock_redis_client,
        test_user,
        auth_token
    ):
        """Test successful email update."""
        # Setup mocks
        mock_db = mock_mongo_client.get_database("users")
        mock_users_collection = mock_db["users"]
        
        # Mock user in database
        user_in_db = test_user.copy()
        user_in_db["password"] = Hash.hash("testpassword123")
        
        # Mock find_one to return user (for authentication check)
        mock_users_collection.find_one = AsyncMock(return_value=user_in_db)
        
        # Mock find_one_and_update for email update
        updated_user = user_in_db.copy()
        updated_user["email"] = {"address": "newemail@example.com", "is_verified": False}
        mock_users_collection.find_one_and_update = AsyncMock(return_value=updated_user)
        
        # Mock Redis delete
        mock_redis_client.delete = AsyncMock(return_value=1)
        
        # Mock get_current_user dependency
        from app.api.dependencies import get_current_user
        async def mock_get_current_user():
            return test_user
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            response = await async_client.patch(
                "/api/v1/user/email/update",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={"email": "newemail@example.com", "password": "testpassword123"}
            )
            
            assert response.status_code == status.HTTP_200_OK
            assert "Email added" in response.json()["message"]
            assert mock_redis_client.delete.called
        finally:
            app.dependency_overrides.clear()
    
    async def test_update_email_invalid_password(
        self,
        async_client: AsyncClient,
        override_mongo_dependency,
        override_redis_dependency,
        mock_mongo_client,
        test_user,
        auth_token
    ):
        """Test email update with invalid password."""
        mock_db = mock_mongo_client.get_database("users")
        mock_users_collection = mock_db["users"]
        
        # Mock user in database with different password
        user_in_db = test_user.copy()
        user_in_db["password"] = Hash.hash("correctpassword")
        
        # Mock find_one to return user
        mock_users_collection.find_one = AsyncMock(return_value=user_in_db)
        
        # Mock get_current_user dependency
        from app.api.dependencies import get_current_user
        async def mock_get_current_user():
            return test_user
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            response = await async_client.patch(
                "/api/v1/user/email/update",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={"email": "newemail@example.com", "password": "wrongpassword"}
            )
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Couldn't validate credentials" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()
    
    async def test_update_email_already_exists(
        self,
        async_client: AsyncClient,
        override_mongo_dependency,
        override_redis_dependency,
        mock_mongo_client,
        test_user,
        auth_token
    ):
        """Test email update with email already in use."""
        mock_db = mock_mongo_client.get_database("users")
        mock_users_collection = mock_db["users"]
        
        # Mock find to return existing user (email already exists)
        existing_user = {"username": "otheruser", "email": "newemail@example.com"}
        mock_users_collection.find_one = AsyncMock(return_value=existing_user)
        
        # Mock get_current_user dependency
        from app.api.dependencies import get_current_user
        async def mock_get_current_user():
            return test_user
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            response = await async_client.patch(
                "/api/v1/user/email/update",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={"email": "newemail@example.com", "password": "testpassword123"}
            )
            
            assert response.status_code == status.HTTP_409_CONFLICT
            assert "already associated" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.users
class TestUpdatePassword:
    """Tests for PATCH /api/v1/user/password/update endpoint."""
    
    async def test_update_password_success(
        self,
        async_client: AsyncClient,
        override_mongo_dependency,
        mock_mongo_client,
        test_user,
        auth_token
    ):
        """Test successful password update."""
        mock_db = mock_mongo_client.get_database("users")
        mock_users_collection = mock_db["users"]
        
        # Mock user in database
        user_in_db = test_user.copy()
        user_in_db["password"] = Hash.hash("oldpassword")
        
        # Mock find_one to return user (for authentication check)
        mock_users_collection.find_one = AsyncMock(return_value=user_in_db)
        
        # Mock find_one_and_update for password update
        updated_user = user_in_db.copy()
        updated_user["password"] = Hash.hash("newpassword123")
        mock_users_collection.find_one_and_update = AsyncMock(return_value=updated_user)
        
        # Mock get_current_user dependency
        from app.api.dependencies import get_current_user
        async def mock_get_current_user():
            return test_user
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            response = await async_client.patch(
                "/api/v1/user/password/update",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={"current_password": "oldpassword", "new_password": "newpassword123"}
            )
            
            assert response.status_code == status.HTTP_200_OK
            assert "password was updated" in response.json()["message"]
        finally:
            app.dependency_overrides.clear()
    
    async def test_update_password_invalid_current_password(
        self,
        async_client: AsyncClient,
        override_mongo_dependency,
        mock_mongo_client,
        test_user,
        auth_token
    ):
        """Test password update with invalid current password."""
        mock_db = mock_mongo_client.get_database("users")
        mock_users_collection = mock_db["users"]
        
        # Mock user in database
        user_in_db = test_user.copy()
        user_in_db["password"] = Hash.hash("correctpassword")
        
        # Mock find_one to return user
        mock_users_collection.find_one = AsyncMock(return_value=user_in_db)
        
        # Mock get_current_user dependency
        from app.api.dependencies import get_current_user
        async def mock_get_current_user():
            return test_user
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            response = await async_client.patch(
                "/api/v1/user/password/update",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={"current_password": "wrongpassword", "new_password": "newpassword123"}
            )
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Couldn't validate credentials" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.users
class TestPasswordRecovery:
    """Tests for PATCH /api/v1/user/password/recovery endpoint."""
    
    async def test_password_recovery_success(
        self,
        async_client: AsyncClient,
        override_mongo_dependency,
        mock_mongo_client
    ):
        """Test successful password recovery."""
        mock_db = mock_mongo_client.get_database("users")
        mock_users_collection = mock_db["users"]
        
        # Mock user in database
        user_in_db = {"username": "testuser", "email": "test@example.com", "role": "user"}
        
        # Mock find_one to return user
        mock_users_collection.find_one = AsyncMock(return_value=user_in_db)
        
        # Mock find_one_and_update for password update
        updated_user = user_in_db.copy()
        updated_user["password"] = Hash.hash("newpassword123")
        mock_users_collection.find_one_and_update = AsyncMock(return_value=updated_user)
        
        response = await async_client.patch(
            "/api/v1/user/password/recovery",
            json={"email": "test@example.com", "new_password": "newpassword123"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert "password has been recovered" in response.json()["message"]
    
    async def test_password_recovery_user_not_found(
        self,
        async_client: AsyncClient,
        override_mongo_dependency,
        mock_mongo_client
    ):
        """Test password recovery with non-existent user."""
        mock_db = mock_mongo_client.get_database("users")
        mock_users_collection = mock_db["users"]
        
        # Mock find_one to return None
        mock_users_collection.find_one = AsyncMock(return_value=None)
        
        # Mock find_one_and_update to return None (user not found)
        mock_users_collection.find_one_and_update = AsyncMock(return_value=None)
        
        response = await async_client.patch(
            "/api/v1/user/password/recovery",
            json={"email": "nonexistent@example.com", "new_password": "newpassword123"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in response.json()["detail"]

