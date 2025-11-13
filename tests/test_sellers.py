"""
Tests for sellers endpoints.
"""
import pytest
from unittest.mock import AsyncMock
from fastapi import status
from httpx import AsyncClient

from app.core.security.utils import Hash
from tests.conftest import UserFactory


@pytest.mark.asyncio
@pytest.mark.sellers
class TestCreateSeller:
    """Tests for POST /api/v1/sellers endpoint."""
    
    async def test_create_seller_success(
        self,
        async_client: AsyncClient,
        override_mongo_dependency,
        mock_mongo_client
    ):
        """Test successful seller account creation."""
        # Setup MongoDB mocks
        mock_db = mock_mongo_client.get_database("users")
        mock_sellers_collection = mock_db["sellers"]
        
        # Mock find_one to return None (seller doesn't exist)
        mock_sellers_collection.find_one = AsyncMock(return_value=None)
        
        # Mock insert_one for seller creation
        mock_sellers_collection.insert_one = AsyncMock(return_value=None)
        
        seller_data = UserFactory.create_seller_user()
        
        response = await async_client.post(
            "/api/v1/sellers",
            json={
                "username": seller_data["username"],
                "email": seller_data["email"],
                "password": "sellerpassword123",
                "first_name": seller_data["first_name"],
                "middle_name": seller_data["middle_name"],
                "last_name": seller_data["last_name"],
                "identity_card": seller_data["identity_card"],
                "business_name": seller_data["business_name"],
                "storefront_name": seller_data["storefront_name"],
                "address": seller_data["address"],
                "role": "sellers",
                "scopes": ["seller"]
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert "seller account was created successfully" in response.json()["message"]
        assert mock_sellers_collection.insert_one.called
    
    async def test_create_seller_already_exists(
        self,
        async_client: AsyncClient,
        override_mongo_dependency,
        mock_mongo_client
    ):
        """Test creating seller with existing username."""
        # Setup MongoDB mocks
        mock_db = mock_mongo_client.get_database("users")
        mock_sellers_collection = mock_db["sellers"]
        
        # Mock find_one to return existing seller
        existing_seller = UserFactory.create_seller_user()
        mock_sellers_collection.find_one = AsyncMock(return_value=existing_seller)
        
        seller_data = UserFactory.create_seller_user()
        
        response = await async_client.post(
            "/api/v1/sellers",
            json={
                "username": seller_data["username"],
                "email": seller_data["email"],
                "password": "sellerpassword123",
                "first_name": seller_data["first_name"],
                "middle_name": seller_data["middle_name"],
                "last_name": seller_data["last_name"],
                "identity_card": seller_data["identity_card"],
                "business_name": seller_data["business_name"],
                "storefront_name": seller_data["storefront_name"],
                "address": seller_data["address"],
                "role": "sellers",
                "scopes": ["seller"]
            }
        )
        
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "User already exists" in response.json()["detail"]
    
    async def test_create_seller_invalid_data(
        self,
        async_client: AsyncClient,
        override_mongo_dependency,
        mock_mongo_client
    ):
        """Test creating seller with invalid data."""
        # Setup MongoDB mocks
        mock_db = mock_mongo_client.get_database("users")
        mock_sellers_collection = mock_db["sellers"]
        
        # Mock find_one to return None
        mock_sellers_collection.find_one = AsyncMock(return_value=None)
        
        # Missing required fields
        response = await async_client.post(
            "/api/v1/sellers",
            json={
                "username": "seller1",
                # Missing required fields
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

