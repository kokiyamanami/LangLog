import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "LangLog API is running"}

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_test_endpoint(client):
    payload = {"key": "value", "test": "data"}
    response = client.post("/api/v1/test", json=payload)
    assert response.status_code == 200
    assert response.json() == {"received": payload}
