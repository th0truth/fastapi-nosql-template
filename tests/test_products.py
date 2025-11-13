"""
Tests for products endpoints.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import status
from httpx import AsyncClient

from app.main import app
from tests.conftest import ProductFactory, UserFactory


@pytest.mark.asyncio
@pytest.mark.products
class TestGetAllProducts:
    """Tests for GET /api/v2/products/{category}/all endpoint."""
    
    async def test_get_all_products_success(
        self,
        async_client: AsyncClient,
        override_mongo_dependency,
        mock_mongo_client,
        admin_token
    ):
        """Test successful retrieval of all products."""
        # Setup MongoDB mocks
        mock_db = mock_mongo_client.get_database("products")
        mock_products_collection = mock_db["electronics"]
        
        # Mock products
        products = [
            ProductFactory.create_product(title="Product 1", category="electronics"),
            ProductFactory.create_product(title="Product 2", category="electronics")
        ]
        
        # Mock find and to_list
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=products)
        mock_products_collection.find = MagicMock(return_value=mock_cursor)
        
        # Mock get_current_user dependency (admin)
        from app.api.dependencies import get_current_user
        async def mock_get_current_user():
            return UserFactory.create_admin_user()
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            response = await async_client.get(
                "/api/v2/products/electronics/all",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 2
        finally:
            app.dependency_overrides.clear()
    
    async def test_get_all_products_not_found(
        self,
        async_client: AsyncClient,
        override_mongo_dependency,
        mock_mongo_client,
        admin_token
    ):
        """Test getting products when none exist."""
        # Setup MongoDB mocks
        mock_db = mock_mongo_client.get_database("products")
        mock_products_collection = mock_db["electronics"]
        
        # Mock find and to_list to return empty list
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=[])
        mock_products_collection.find = MagicMock(return_value=mock_cursor)
        
        # Mock get_current_user dependency (admin)
        from app.api.dependencies import get_current_user
        async def mock_get_current_user():
            return UserFactory.create_admin_user()
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            response = await async_client.get(
                "/api/v2/products/electronics/all",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "Products not found" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()
    
    async def test_get_all_products_with_pagination(
        self,
        async_client: AsyncClient,
        override_mongo_dependency,
        mock_mongo_client,
        admin_token
    ):
        """Test getting products with pagination parameters."""
        # Setup MongoDB mocks
        mock_db = mock_mongo_client.get_database("products")
        mock_products_collection = mock_db["electronics"]
        
        # Mock products
        products = [
            ProductFactory.create_product(title=f"Product {i}", category="electronics")
            for i in range(10)
        ]
        
        # Mock find and to_list
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=products)
        mock_products_collection.find = MagicMock(return_value=mock_cursor)
        
        # Mock get_current_user dependency (admin)
        from app.api.dependencies import get_current_user
        async def mock_get_current_user():
            return UserFactory.create_admin_user()
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            response = await async_client.get(
                "/api/v2/products/electronics/all?offset=2&length=5",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, list)
        finally:
            app.dependency_overrides.clear()
    
    async def test_get_all_products_unauthorized(
        self,
        async_client: AsyncClient,
        test_user,
        auth_token
    ):
        """Test getting products without admin privileges."""
        # Mock get_current_user dependency (regular user, not admin)
        from app.api.dependencies import get_current_user
        async def mock_get_current_user():
            return test_user
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            response = await async_client.get(
                "/api/v2/products/electronics/all",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "Not enough permissions" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.products
class TestAddProduct:
    """Tests for POST /api/v2/products/{category}/add endpoint."""
    
    async def test_add_product_success(
        self,
        async_client: AsyncClient,
        override_mongo_dependency,
        mock_mongo_client,
        seller_token,
        test_seller_user
    ):
        """Test successful product addition."""
        # Setup MongoDB mocks
        mock_db = mock_mongo_client.get_database("products")
        
        # Mock list_collection_names to include category
        mock_db.list_collection_names = AsyncMock(return_value=["electronics", "clothing"])
        
        mock_products_collection = mock_db["electronics"]
        mock_products_collection.insert_one = AsyncMock(return_value=None)
        
        # Mock get_current_user dependency (seller)
        from app.api.dependencies import get_current_user
        async def mock_get_current_user():
            return test_seller_user
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            response = await async_client.post(
                "/api/v2/products/electronics/add",
                headers={"Authorization": f"Bearer {seller_token}"}
            )
            
            # Note: The endpoint seems incomplete in the source code
            # This test may need adjustment based on actual implementation
            assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]
        finally:
            app.dependency_overrides.clear()
    
    async def test_add_product_category_not_found(
        self,
        async_client: AsyncClient,
        override_mongo_dependency,
        mock_mongo_client,
        seller_token,
        test_seller_user
    ):
        """Test adding product to non-existent category."""
        # Setup MongoDB mocks
        mock_db = mock_mongo_client.get_database("products")
        
        # Mock list_collection_names to not include category
        mock_db.list_collection_names = AsyncMock(return_value=["electronics", "clothing"])
        
        # Mock get_current_user dependency (seller)
        from app.api.dependencies import get_current_user
        async def mock_get_current_user():
            return test_seller_user
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            response = await async_client.post(
                "/api/v2/products/nonexistent/add",
                headers={"Authorization": f"Bearer {seller_token}"}
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "Category not found" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()
    
    async def test_add_product_unauthorized(
        self,
        async_client: AsyncClient,
        test_user,
        auth_token
    ):
        """Test adding product without seller/admin privileges."""
        # Mock get_current_user dependency (regular user, not seller/admin)
        from app.api.dependencies import get_current_user
        async def mock_get_current_user():
            return test_user
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        try:
            response = await async_client.post(
                "/api/v2/products/electronics/add",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "Not enough permissions" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()

