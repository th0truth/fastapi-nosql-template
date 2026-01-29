from httpx import ASGITransport, AsyncClient
import pytest

from app.main import app

@pytest.mark.io
async def async_client():
  async with AsyncClient(
    transport=ASGITransport(app=app), base_url="http://test"
  ) as _client:
    return _client
