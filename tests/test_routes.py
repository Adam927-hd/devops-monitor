import pytest
from fastapi.testclient import TestClient

from api.main import app, _servers

VALID_KEY = "dev-secret-key"


@pytest.fixture(autouse=True)
def clear_store():
    """Reset the in-memory store between tests."""
    _servers.clear()
    yield
    _servers.clear()


client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_metrics_returns_cpu():
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "cpu_percent" in resp.json()


def test_post_server_no_key_returns_403():
    resp = client.post("/servers", json={"name": "s1", "host": "localhost", "port": 9000})
    assert resp.status_code == 403


def test_post_server_with_key_returns_201_and_appears_in_list():
    resp = client.post(
        "/servers",
        json={"name": "s1", "host": "localhost", "port": 9000},
        headers={"X-API-Key": VALID_KEY},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "s1"
    assert data["status"] == "unknown"

    list_resp = client.get("/servers")
    assert list_resp.status_code == 200
    ids = [s["id"] for s in list_resp.json()]
    assert data["id"] in ids


def test_get_nonexistent_server_returns_404():
    resp = client.get("/servers/does-not-exist")
    assert resp.status_code == 404
