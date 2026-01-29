from httpx import AsyncClient
import pytest

@pytest.mark.anyio
async def health_check(async_client: AsyncClient):
  response = await async_client.get("/api/v1/health")
  assert response.status_code == 200