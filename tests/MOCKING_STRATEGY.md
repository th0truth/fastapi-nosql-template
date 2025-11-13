# Database Mocking Strategy for Tests

## Overview

This test suite uses **unittest.mock** to mock MongoDB and Redis dependencies. **No real database instances are required** - all database interactions are simulated using Python mocks.

## Mocking Architecture

### MongoDB Mocking

The MongoDB mocking follows a 3-level hierarchy:

```
AsyncMongoClient (mock_mongo_client)
    ↓ get_database()
AsyncDatabase (mock_mongo_database)
    ↓ [collection_name]
AsyncCollection (mock_users_collection, etc.)
    ↓ find_one(), insert_one(), etc.
Mock Results
```

#### Fixtures:

1. **`mock_mongo_client`**: Mocks the top-level `AsyncMongoClient`
   - Has `get_database()` method that returns `mock_mongo_database`
   - Used by FastAPI dependency injection

2. **`mock_mongo_database`**: Mocks the `AsyncDatabase` object
   - Contains multiple mock collections (users, sellers, products, etc.)
   - Collections accessed via `db[collection_name]` syntax
   - Has `list_collection_names()` method

3. **Mock Collections**: Individual `AsyncCollection` mocks
   - Each collection (users, sellers, etc.) is a separate `AsyncMock`
   - Methods like `find_one()`, `insert_one()`, `update_one()` are mocked
   - Tests configure return values for these methods

#### Example Usage:

```python
async def test_login_success(
    mock_mongo_client,
    override_mongo_dependency,
    test_user
):
    # Get the mock database
    mock_db = mock_mongo_client.get_database("users")
    
    # Get a specific collection
    mock_users_collection = mock_db["users"]
    
    # Configure the mock to return a user
    user_in_db = test_user.copy()
    user_in_db["password"] = Hash.hash("testpassword123")
    mock_users_collection.find_one = AsyncMock(return_value=user_in_db)
    
    # Now when the code calls collection.find_one(), it returns our mock data
```

### Redis Mocking

Redis mocking is simpler - we mock the `aioredis.Redis` client directly.

#### Fixtures:

1. **`mock_redis_client`**: Mocks the `aioredis.Redis` client
   - All Redis operations (get, setex, delete, exists) are mocked
   - Tests configure return values for specific operations

#### Example Usage:

```python
async def test_login_success(
    mock_redis_client,
    override_redis_dependency
):
    # Configure Redis to return a cached value
    mock_redis_client.get = AsyncMock(return_value=json.dumps(cached_user))
    
    # Or configure it to return None (cache miss)
    mock_redis_client.get = AsyncMock(return_value=None)
    
    # Configure setex for cache writes
    mock_redis_client.setex = AsyncMock(return_value=True)
```

## Dependency Injection

The mocks are injected into FastAPI using **dependency overrides**:

### `override_mongo_dependency` Fixture

```python
@pytest.fixture
async def override_mongo_dependency(mock_mongo_client):
    """Override MongoDB dependency with mock."""
    async def _get_mongo_client():
        yield mock_mongo_client
    
    app.dependency_overrides[get_mongo_client] = _get_mongo_client
    yield mock_mongo_client
    app.dependency_overrides.clear()  # Cleanup after test
```

This replaces the real `get_mongo_client()` dependency with our mock.

### `override_redis_dependency` Fixture

```python
@pytest.fixture
async def override_redis_dependency(mock_redis_client):
    """Override Redis dependency with mock."""
    async def _get_redis_client():
        yield mock_redis_client
    
    app.dependency_overrides[get_redis_client] = _get_redis_client
    yield mock_redis_client
    app.dependency_overrides.clear()  # Cleanup after test
```

## Complete Test Example

```python
@pytest.mark.asyncio
async def test_login_success(
    async_client: AsyncClient,
    override_mongo_dependency,      # Injects mock MongoDB
    override_redis_dependency,      # Injects mock Redis
    mock_mongo_client,              # Access to mock client
    mock_redis_client,              # Access to mock Redis
    test_user                        # Test data factory
):
    # 1. Setup MongoDB mock
    mock_db = mock_mongo_client.get_database("users")
    mock_users_collection = mock_db["users"]
    
    # Configure what find_one() returns
    user_in_db = test_user.copy()
    user_in_db["password"] = Hash.hash("testpassword123")
    mock_users_collection.find_one = AsyncMock(return_value=user_in_db)
    
    # 2. Setup Redis mock
    mock_redis_client.setex = AsyncMock(return_value=True)
    
    # 3. Make the actual API call
    response = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "testpassword123"}
    )
    
    # 4. Assertions
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert mock_redis_client.setex.called  # Verify Redis was called
```

## Benefits of This Approach

1. **No External Dependencies**: Tests run without MongoDB or Redis installed
2. **Fast Execution**: No network I/O or database operations
3. **Deterministic**: Tests always return the same results
4. **Isolated**: Each test is independent
5. **Full Control**: Easy to test error cases, edge cases, and different scenarios
6. **CI/CD Friendly**: No need to set up database services in CI

## Common Mock Patterns

### MongoDB Patterns

```python
# User found
mock_collection.find_one = AsyncMock(return_value=user_dict)

# User not found
mock_collection.find_one = AsyncMock(return_value=None)

# Insert operation
mock_collection.insert_one = AsyncMock(return_value=None)

# Update operation
mock_collection.find_one_and_update = AsyncMock(return_value=updated_user)

# Delete operation
delete_result = MagicMock()
delete_result.deleted_count = 1
mock_collection.delete_one = AsyncMock(return_value=delete_result)
```

### Redis Patterns

```python
# Cache hit
mock_redis.get = AsyncMock(return_value=json.dumps(cached_data))

# Cache miss
mock_redis.get = AsyncMock(return_value=None)

# Set cache
mock_redis.setex = AsyncMock(return_value=True)

# Check if key exists (for blacklist)
mock_redis.exists = AsyncMock(return_value=1)  # Exists
mock_redis.exists = AsyncMock(return_value=0)  # Doesn't exist

# Delete cache
mock_redis.delete = AsyncMock(return_value=1)
```

## Helper Functions

The `conftest.py` includes helper functions for common setups:

- `setup_mongo_user_find()`: Quick setup for user lookup mocks
- `setup_redis_cache()`: Quick setup for Redis cache mocks

## Best Practices

1. **Always use dependency override fixtures**: Don't manually override dependencies
2. **Configure mocks per test**: Each test should set up its own mock behavior
3. **Verify mock calls**: Use `assert mock.called` to verify interactions
4. **Clean up**: The override fixtures automatically clean up after each test
5. **Use factories**: Use `UserFactory`, `ProductFactory` for consistent test data

