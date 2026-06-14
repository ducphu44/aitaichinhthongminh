import pytest

@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test GET / trả về thông tin API."""
    response = await client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "message" in data or "status" in data

@pytest.mark.asyncio
async def test_health_check(client):
    """Test GET /health trả về status healthy."""
    response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
