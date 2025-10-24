"""
Tests for FastAPI endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "endpoints" in data


def test_health():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_list_countries():
    """Test countries listing endpoint."""
    response = client.get("/countries")
    assert response.status_code == 200
    data = response.json()
    assert "countries" in data


def test_optimize_endpoint():
    """Test optimization endpoint."""
    payload = {
        "workers": [
            {
                "id": 1,
                "name": "Test Worker",
                "country": "US",
                "skills": ["morning", "afternoon"],
                "max_shifts_per_week": 5,
                "unavailable_days": []
            }
        ],
        "num_days": 7,
        "shift_requirements": {
            "morning": 1,
            "afternoon": 1,
            "night": 0
        },
        "track_experiment": False
    }
    
    response = client.post("/optimize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_validate_endpoint():
    """Test validation endpoint."""
    payload = {
        "schedule": [
            {
                "day": 0,
                "shifts": {
                    "morning": [{"worker_id": 1, "worker_name": "Test", "country": "US"}]
                }
            }
        ],
        "workers": [
            {
                "id": 1,
                "name": "Test",
                "country": "US",
                "skills": ["morning"],
                "max_shifts_per_week": 5,
                "unavailable_days": []
            }
        ]
    }
    
    response = client.post("/validate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "valid" in data
    assert "violations" in data
