import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

from app.main import app
from app.database import Base, get_db
from app.auth import get_current_user
from app.models import GeneratedReport, User

def override_get_current_user():
    return User(id=1, email="admin@abc.com", role="admin")

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_reports.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def override_dependencies():
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(get_db, None)

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Setup test database
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Add a mock report
    mock_report = GeneratedReport(
        title="Báo cáo Test 1",
        report_type="yearly",
        fiscal_year=2026,
        content_markdown="# Nội dung test",
        raw_data_json="{}"
    )
    db.add(mock_report)
    db.commit()
    db.close()
    
    yield
    # Teardown test database
    Base.metadata.drop_all(bind=engine)

def test_get_reports():
    response = client.get("/reports")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["title"] == "Báo cáo Test 1"

@patch("app.routers.reports.generate_ai_insights")
@patch("app.routers.reports.fetch_report_data")
def test_generate_report(mock_fetch_data, mock_ai_insights):
    # Mock return values for internal functions
    mock_fetch_data.return_value = {
        "summary": {
            "total_planned": 1000,
            "total_actual": 500,
            "usage_rate_percent": 50.0,
            "pending_payments_count": 0,
            "pending_payments_amount": 0,
            "over_budget_count": 0
        },
        "over_budget_programs": [],
        "large_payments": [],
        "department_budgets": []
    }
    mock_ai_insights.return_value = {
        "comments": "Mocked comment",
        "recommendations": "Mocked recommendation"
    }

    # Request body
    payload = {
        "fiscal_year": 2026,
        "report_type": "yearly"
    }

    response = client.post("/reports/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "id" in data
    assert "Executive Financial Dashboard - Năm 2026" in data["title"]
    assert data["raw_data_json"] is not None

def test_get_report_by_id():
    response = client.get("/reports/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Báo cáo Test 1"

def test_get_report_not_found():
    response = client.get("/reports/9999")
    assert response.status_code == 404
