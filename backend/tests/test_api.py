"""API integration tests for authentication and platform endpoints."""
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "mongodb"


@pytest.mark.asyncio
async def test_login_with_seeded_admin(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@suraksha.gov.in", "password": "Admin@12345"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body


@pytest.mark.asyncio
async def test_scam_analysis_requires_auth(client: AsyncClient):
    response = await client.post(
        "/api/v1/scam/analyse",
        json={"content": "CBI digital arrest transfer money now", "channel": "chat"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_scam_analysis_with_token(client: AsyncClient):
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@suraksha.gov.in", "password": "Admin@12345"},
    )
    token = login.json()["access_token"]
    response = await client.post(
        "/api/v1/scam/analyse",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "content": "CBI officer says you are under digital arrest. Transfer money.",
            "channel": "chat",
            "language": "en",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["risk_score"] >= 75
    assert "digital_arrest" in data["scam_types"]


@pytest.mark.asyncio
async def test_analytics_summary(client: AsyncClient):
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@suraksha.gov.in", "password": "Admin@12345"},
    )
    token = login.json()["access_token"]
    response = await client.get(
        "/api/v1/analytics/summary",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_reports" in data
    assert "by_category" in data


@pytest.mark.asyncio
async def test_authenticated_user_can_create_a_valid_safety_report(client: AsyncClient):
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@suraksha.gov.in", "password": "Admin@12345"},
    )
    token = login.json()["access_token"]
    response = await client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "category": "phishing",
            "title": "Suspicious UPI payment request",
            "description": "The sender requested an immediate UPI payment through an unknown link.",
            "channel": "web",
            "district": "Bengaluru",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Suspicious UPI payment request"
    assert body["status"] == "submitted"
