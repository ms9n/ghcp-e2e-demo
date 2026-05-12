import pytest
from app.main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_index(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"GHCP E2E Demo" in resp.data


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "healthy"


def test_calculate_success(client):
    resp = client.get("/calculate?a=10&b=2")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["result"] == 5.0


def test_calculate_missing_params(client):
    resp = client.get("/calculate")
    assert resp.status_code == 400


def test_calculate_division_by_zero(client):
    resp = client.get("/calculate?a=10&b=0")
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"] == "Division by zero"


def test_favicon(client):
    resp = client.get("/favicon.ico")
    assert resp.status_code == 204


def test_not_found_returns_404(client):
    resp = client.get("/nonexistent-route")
    assert resp.status_code == 404
    data = resp.get_json()
    assert data["error"] == "NotFound"
