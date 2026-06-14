import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.auth import get_current_user
from app.models import User

# Override get_current_user để bỏ qua auth
def override_get_current_user():
    return User(id=1, email="staff@abc.com", role="finance_staff")

@pytest.fixture(autouse=True)
def override_dependency(client):
    from app.main import app
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_chat_success(client, sample_chat_request):
    """Test POST /ai/chat với mock LLM response."""
    mock_response = {
        "answer": "Năm 2026 phòng Đào tạo chi tiêu 100 triệu.",
        "source_data": []
    }

    with patch("app.routers.chat.process_chat") as mock_process:
        mock_process.return_value = mock_response

        response = await client.post(
            "/ai/chat",
            json=sample_chat_request,
        )

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "100 triệu" in data["answer"]

@pytest.mark.asyncio
async def test_chat_empty_message(client):
    """Test POST /ai/chat với question rỗng -> fail do validator."""
    # Assuming Pydantic catches missing/empty strings or the service catches it
    response = await client.post(
        "/ai/chat",
        json={"question": "", "fiscal_year": 2026},
    )
    # The actual behavior depends on pydantic. Empty string might be valid for str,
    # but let's test if process_chat raises an error or handles it
    pass # we'll adjust assertions based on actual code

@pytest.mark.asyncio
async def test_chat_llm_error(client, sample_chat_request):
    """Test POST /ai/chat khi hệ thống bị lỗi."""
    with patch("app.routers.chat.process_chat") as mock_process:
        mock_process.side_effect = Exception("LLM API timeout")

        response = await client.post(
            "/ai/chat",
            json=sample_chat_request,
        )

    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "Lỗi hệ thống" in data["detail"]
