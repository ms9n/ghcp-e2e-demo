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
    data = resp.get_json()
    assert data["app"] == "ghcp-e2e-demo"
    assert data["status"] == "running"


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
    assert resp.status_code == 500
    data = resp.get_json()
    assert data["error"] == "ZeroDivisionError"


def test_favicon_with_malformed_query_params(client):
    resp = client.get("/favicon.ico?a=10&b=2```````````````````````````````")
    assert resp.status_code == 204
    assert resp.data == b""
