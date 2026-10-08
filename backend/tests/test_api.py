"""
Integration tests for FastAPI endpoints.
"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "A11yLens API"
    assert "version" in data

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_badge_svg_endpoint():
    response = client.get("/api/badge?score=95&grade=A%2B")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")
    assert b"95%" in response.content

def test_remediate_endpoint():
    response = client.post("/api/remediate", json={
        "html": '<img src="profile.png">',
        "rule_id": "IMG_ALT_MISSING",
        "wcag": "1.1.1",
        "message": "Missing alt",
        "suggestion": "Add alt"
    })
    assert response.status_code == 200
    data = response.json()
    assert "remediated_code" in data
    assert "alt=" in data["remediated_code"]
    assert "explanation" in data
