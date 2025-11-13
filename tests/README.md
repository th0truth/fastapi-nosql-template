# Test Suite Documentation

This directory contains a comprehensive test suite for the FastAPI NoSQL template application.

## Overview

The test suite provides:
- **Complete coverage** of all FastAPI path operations
- **Async-safe tests** using pytest-asyncio and httpx.AsyncClient
- **Mocked external dependencies** (MongoDB and Redis) - no real database instances required
- **Reusable fixtures** for test data, authentication, and database mocks
- **Parametrized tests** and factory-based test data generation

## Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures and test configuration
├── test_auth.py         # Authentication endpoints tests
├── test_user.py         # Current user endpoints tests
├── test_users.py        # Admin user management endpoints tests
├── test_sellers.py      # Seller endpoints tests
├── test_products.py     # Product endpoints tests
└── README.md            # This file
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

### Run specific test file
```bash
pytest tests/test_auth.py
```

### Run specific test class
```bash
pytest tests/test_auth.py::TestAuthLogin
```

### Run specific test
```bash
pytest tests/test_auth.py::TestAuthLogin::test_login_success
```

### Run with markers
```bash
pytest -m auth          # Run only auth tests
pytest -m users         # Run only user-related tests
pytest -m "not auth"    # Run all except auth tests
```

## Test Coverage

The test suite aims for ≥90% coverage of the API layer. Coverage reports are generated in:
- Terminal output (with `--cov-report=term-missing`)
- HTML report (in `htmlcov/` directory)
- XML report (for CI integration)

## Fixtures

### Database Fixtures
- `mock_mongo_client`: Mock AsyncMongoClient instance
- `mock_mongo_database`: Mock MongoDB database with collections
- `mock_redis_client`: Mock Redis client
- `override_mongo_dependency`: Override MongoDB dependency in FastAPI app
- `override_redis_dependency`: Override Redis dependency in FastAPI app

### Test Client Fixtures
- `client`: Synchronous TestClient
- `async_client`: Asynchronous AsyncClient

### Authentication Fixtures
- `test_user`: Standard test user dictionary
- `test_admin_user`: Admin test user dictionary
- `test_seller_user`: Seller test user dictionary
- `auth_token`: JWT token for test user
- `admin_token`: JWT token for admin user
- `seller_token`: JWT token for seller user
- `expired_token`: Expired JWT token for testing

### Test Data Factories
- `UserFactory`: Factory for creating test user data
- `ProductFactory`: Factory for creating test product data

## Test Categories

Tests are organized by endpoint groups:

1. **Authentication** (`test_auth.py`)
   - Login
   - Token refresh
   - Logout

2. **Current User** (`test_user.py`)
   - Get current user profile
   - Update email
   - Update password
   - Password recovery

3. **User Management** (`test_users.py`) - Admin only
   - Read user by username
   - Read all users by role
   - Update user
   - Delete user

4. **Sellers** (`test_sellers.py`)
   - Create seller account

5. **Products** (`test_products.py`)
   - Get all products by category
   - Add product

## Mocking Strategy

### MongoDB
- All MongoDB operations are mocked using `AsyncMock`
- Collections are mocked to return test data
- Database operations (find_one, insert_one, update_one, delete_one) are mocked

### Redis
- Redis operations are mocked using `AsyncMock`
- Cache operations (get, setex, delete, exists) are mocked
- Token blacklist operations are mocked

### Authentication
- JWT tokens are generated using the actual OAuthJWTBearer class
- User authentication is mocked at the database level
- `get_current_user` dependency is overridden for testing

## Best Practices

1. **Isolation**: Each test is independent and doesn't rely on other tests
2. **Clear naming**: Test names clearly describe what is being tested
3. **Arrange-Act-Assert**: Tests follow the AAA pattern
4. **Edge cases**: Tests cover success, failure, and edge cases
5. **Error handling**: Tests verify proper error responses and status codes

## CI Integration

Tests run automatically on:
- Push to main/develop branches
- Pull requests to main/develop branches
- Multiple Python versions (3.11, 3.12)

Coverage reports are uploaded to Codecov for tracking.

## Troubleshooting

### Tests failing with import errors
Make sure you're running tests from the project root and the `app` package is installed:
```bash
pip install -e .
```

### Async test warnings
Ensure `pytest-asyncio` is installed and `asyncio_mode = auto` is set in `pytest.ini`.

### Coverage not working
Make sure `pytest-cov` is installed:
```bash
pip install pytest-cov
```

## Contributing

When adding new endpoints:
1. Create corresponding test file or add to existing one
2. Use existing fixtures where possible
3. Mock all external dependencies
4. Test success, failure, and edge cases
5. Aim for ≥90% coverage of the new code
6. Update this README if adding new test categories

