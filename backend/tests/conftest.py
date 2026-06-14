import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture(scope="session")
def event_loop():
    """Tạo event loop dùng chung cho tất cả test trong session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def client():
    """
    Tạo AsyncClient test cho FastAPI app.
    Sử dụng ASGITransport để gọi trực tiếp ASGI app
    mà không cần chạy server thật.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as ac:
        yield ac

@pytest.fixture
def sample_chat_request():
    """Dữ liệu mẫu cho chat request."""
    return {
        "question": "Năm 2026 phòng Đào tạo chi tiêu thế nào?",
        "department_id": None,
        "fiscal_year": 2026
    }
