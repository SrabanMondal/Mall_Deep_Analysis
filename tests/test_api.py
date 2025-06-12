import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi.testclient import TestClient
from api.main import app
import pytest

@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def sample_request():
    return {
        "customer_name": "Micky",
        "cart": ["Item1"],
        "category": None
    }

def test_recommend_endpoint(test_client, sample_request):
    response = test_client.post("/recommend", json=sample_request)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "recommendations" in response.json()
    assert isinstance(response.json()["recommendations"], list)
    assert len(response.json()["recommendations"]) <= 8

def test_recommend_endpoint_no_cart(test_client):
    response = test_client.post("/recommend", json={
        "customer_name": "Micky",
        "cart": None,
        "category": None
    })
    assert response.status_code == 200
    assert isinstance(response.json()["recommendations"], list)

def test_recommend_endpoint_invalid_user(test_client):
    response = test_client.post("/recommend", json={
        "customer_name": "Unknown",
        "cart": None,
        "category": None
    })
    assert response.status_code == 200
    assert isinstance(response.json()["recommendations"], list)

def test_recommend_endpoint_category(test_client):
    response = test_client.post("/recommend", json={
        "customer_name": "Micky",
        "cart": None,
        "category": "Binders"
    })
    assert response.status_code == 200
    assert isinstance(response.json()["recommendations"], list)
