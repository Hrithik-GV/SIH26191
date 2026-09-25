from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert data["status"] == "online"
    assert data["health"] == "/health"


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "timestamp" in data
    assert "database" in data
    assert "services" in data
    assert "version" in data


def test_api_v1_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]


def test_ping_endpoint():
    response = client.get("/api/v1/ping")
    assert response.status_code == 200
    data = response.json()
    assert data["ping"] == "pong"
    assert data["status"] == "online"
