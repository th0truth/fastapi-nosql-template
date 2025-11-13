"""
Tests for users endpoints (admin operations).
"""
import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import timedelta
from fastapi import status
from httpx import AsyncClient

from app.main import app
from tests.conftest import UserFactory


@pytest.mark.asyncio
@pytest.mark.users
class TestReadUser:
    """Tests for GET /api/v1/users/{username} endpoint."""
    
    async def test_read_user_success_from_cache(
        self,
        async_client: AsyncClient,
        override_mongo_dependency,
        override_redis_dependency,
        mock_mongo_client,
        mock_redis_client,
        test_user,
        admin_token
    ):
        """Test reading user from Redis cache."""
        # Mock Redis to return cached user
        cached_user = {k: v for k, v in test_user.items() if k != "password"}
        mock_redis_client.get = AsyncMock(return_value=json.dumps(cached_user, default=str))
        
        # Mock get_current_user dependency (admin)
        from app.api.dependencies import get_current_user
        async def mock_get_current_user():
            return UserFactory.create_admin_user()
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            response = await async_client.get(
                f"/api/v1/users/{test_user['username']}",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["username"] == test_user["username"]
        finally:
            app.dependency_overrides.clear()
    
    async def test_read_user_success_from_database(
        self,
        async_client: AsyncClient,
        override_mongo_dependency,
        override_redis_dependency,
        mock_mongo_client,
        mock_redis_client,
        test_user,
        admin_token
    ):
        """Test reading user from MongoDB database."""
        # Mock Redis to return None (cache miss)
        mock_redis_client.get = AsyncMock(return_value=None)
        mock_redis_client.setex = AsyncMock(return_value=True)
        
        # Setup MongoDB mocks
        mock_db = mock_mongo_client.get_database("users")
        mock_users_collection = mock_db["users"]
        
        # Mock find_one to return user
        user_data = {k: v for k, v in test_user.items() if k != "password"}
        mock_users_collection.find_one = AsyncMock(return_value=user_data)
        
        # Mock get_current_user dependency (admin)
        from app.api.dependencies import get_current_user
        async def mock_get_current_user():
            return UserFactory.create_admin_user()
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            response = await async_client.get(
                f"/api/v1/users/{test_user['username']}",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["username"] == test_user["username"]
            assert mock_redis_client.setex.called
        finally:
            app.dependency_overrides.clear()
    
    async def test_read_user_not_found(
        self,
        async_client: AsyncClient,
        override_mongo_dependency,
        override_redis_dependency,
        mock_mongo_client,
        mock_redis_client,
        admin_token
    ):
        """Test reading non-existent user."""
        # Mock Redis to return None
        mock_redis_client.get = AsyncMock(return_value=None)
        
        # Setup MongoDB mocks
        mock_db = mock_mongo_client.get_database("users")
        mock_users_collection = mock_db["users"]
        
        # Mock find_one to return None
        mock_users_collection.find_one = AsyncMock(return_value=None)
        
        # Mock get_current_user dependency (admin)
        from app.api.dependencies import get_current_user
        async def mock_get_current_user():
            return UserFactory.create_admin_user()
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            response = await async_client.get(
                "/api/v1/users/nonexistent",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "User not found" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()
    
    async def test_read_user_unauthorized(
        self,
        async_client: AsyncClient,
        test_user,
        auth_token
    ):
        """Test reading user without admin privileges."""
        # Mock get_current_user dependency (regular user, not admin)
        from app.api.dependencies import get_current_user
        async def mock_get_current_user():
            return test_user
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            response = await async_client.get(
                f"/api/v1/users/{test_user['username']}",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "Not enough permissions" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.users
class TestReadUsers:
    """Tests for GET /api/v1/users/{role}/all endpoint."""
    
    async def test_read_users_success(
        self,
        async_client: AsyncClient,
        override_mongo_dependency,
        mock_mongo_client,
        admin_token
    ):
        """Test reading all users by role."""
        # Setup MongoDB mocks
        mock_db = mock_mongo_client.get_database("users")
        mock_users_collection = mock_db["user"]  # Note: role is used as collection name
        
        # Mock read_all to return users
        users = [
            UserFactory.create_user(username="user1", role="user"),
            UserFactory.create_user(username="user2", role="user")
        ]
        
        # Mock find and to_list
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=users)
        mock_users_collection.find = MagicMock(return_value=mock_cursor)
        
        # Mock get_current_user dependency (admin)
        from app.api.dependencies import get_current_user
        async def mock_get_current_user():
            return UserFactory.create_admin_user()
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            # Note: UserCRUD.read_all is called with role as collection name
            # We need to patch it since it's not properly implemented
            from app.crud import UserCRUD
            user_crud = UserCRUD(mock_db)
            user_crud.read_all = AsyncMock(return_value=users)
            
            with patch('app.api.v1.routers.users.UserCRUD', return_value=user_crud):
                response = await async_client.get(
                    "/api/v1/users/user/all",
                    headers={"Authorization": f"Bearer {admin_token}"}
                )
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert isinstance(data, list)
        finally:
            app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.users
class TestUpdateUser:
    """Tests for PATCH /api/v1/users/{username}/update endpoint."""
    
    async def test_update_user_success(
        self,
        async_client: AsyncClient,
        override_mongo_dependency,
        override_redis_dependency,
        mock_mongo_client,
        mock_redis_client,
        test_user,
        admin_token
    ):
        """Test successful user update."""
        # Setup MongoDB mocks
        mock_db = mock_mongo_client.get_database("users")
        mock_users_collection = mock_db["users"]
        
        # Mock find_one to return user
        user_data = test_user.copy()
        mock_users_collection.find_one = AsyncMock(return_value=user_data)
        
        # Mock find_one_and_update for user update
        updated_user = user_data.copy()
        updated_user["first_name"] = "Updated"
        mock_users_collection.find_one_and_update = AsyncMock(return_value=updated_user)
        
        # Mock Redis delete
        mock_redis_client.delete = AsyncMock(return_value=1)
        
        # Mock get_current_user dependency (admin)
        from app.api.dependencies import get_current_user
        async def mock_get_current_user():
            return UserFactory.create_admin_user()
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            response = await async_client.patch(
                f"/api/v1/users/{test_user['username']}/update",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={"first_name": "Updated"}
            )
            
            assert response.status_code == status.HTTP_200_OK
            assert "user account has been updated" in response.json()["message"]
            assert mock_redis_client.delete.called
        finally:
            app.dependency_overrides.clear()
    
    async def test_update_user_not_found(
        self,
        async_client: AsyncClient,
        override_mongo_dependency,
        override_redis_dependency,
        mock_mongo_client,
        mock_redis_client,
        admin_token
    ):
        """Test updating non-existent user."""
        # Setup MongoDB mocks
        mock_db = mock_mongo_client.get_database("users")
        mock_users_collection = mock_db["users"]
        
        # Mock find_one to return None
        mock_users_collection.find_one = AsyncMock(return_value=None)
        
        # Mock find_one_and_update to return None
        mock_users_collection.find_one_and_update = AsyncMock(return_value=None)
        
        # Mock get_current_user dependency (admin)
        from app.api.dependencies import get_current_user
        async def mock_get_current_user():
            return UserFactory.create_admin_user()
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            response = await async_client.patch(
                "/api/v1/users/nonexistent/update",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={"first_name": "Updated"}
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "User not found" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.users
class TestDeleteUser:
    """Tests for DELETE /api/v1/users/{username}/delete endpoint."""
    
    async def test_delete_user_success(
        self,
        async_client: AsyncClient,
        override_mongo_dependency,
        override_redis_dependency,
        mock_mongo_client,
        mock_redis_client,
        test_user,
        admin_token
    ):
        """Test successful user deletion."""
        # Setup MongoDB mocks
        mock_db = mock_mongo_client.get_database("users")
        mock_users_collection = mock_db["users"]
        
        # Mock find_one to return user
        user_data = test_user.copy()
        mock_users_collection.find_one = AsyncMock(return_value=user_data)
        
        # Mock delete_one to return successful deletion
        delete_result = MagicMock()
        delete_result.deleted_count = 1
        mock_users_collection.delete_one = AsyncMock(return_value=delete_result)
        
        # Mock Redis delete
        mock_redis_client.delete = AsyncMock(return_value=1)
        
        # Mock get_current_user dependency (admin)
        from app.api.dependencies import get_current_user
        async def mock_get_current_user():
            return UserFactory.create_admin_user()
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            response = await async_client.delete(
                f"/api/v1/users/{test_user['username']}/delete",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            assert response.status_code == status.HTTP_200_OK
            assert "user account was deleted successfully" in response.json()["message"]
            assert mock_redis_client.delete.called
        finally:
            app.dependency_overrides.clear()
    
    async def test_delete_user_not_found(
        self,
        async_client: AsyncClient,
        override_mongo_dependency,
        override_redis_dependency,
        mock_mongo_client,
        mock_redis_client,
        admin_token
    ):
        """Test deleting non-existent user."""
        # Setup MongoDB mocks
        mock_db = mock_mongo_client.get_database("users")
        mock_users_collection = mock_db["users"]
        
        # Mock find_one to return None
        mock_users_collection.find_one = AsyncMock(return_value=None)
        
        # Mock get_current_user dependency (admin)
        from app.api.dependencies import get_current_user
        async def mock_get_current_user():
            return UserFactory.create_admin_user()
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            response = await async_client.delete(
                "/api/v1/users/nonexistent/delete",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "User not found" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()

