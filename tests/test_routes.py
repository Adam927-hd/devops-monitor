import pytest
from fastapi.testclient import TestClient

from api.main import app, _servers

VALID_KEY = "dev-secret-key"


@pytest.fixture(autouse=True)
def clear_store():
    _servers.clear()
    yield
    _servers.clear()


client = TestClient(app)


def _create_server(name="s1", host="localhost", port=9000):
    return client.post(
        "/servers",
        json={"name": name, "host": host, "port": port},
        headers={"X-API-Key": VALID_KEY},
    )


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
    resp = _create_server()
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "s1"
    assert data["status"] == "unknown"

    list_resp = client.get("/servers")
    assert list_resp.status_code == 200
    ids = [s["id"] for s in list_resp.json()]
    assert data["id"] in ids


def test_get_server_by_id():
    created = _create_server().json()
    resp = client.get(f"/servers/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_get_nonexistent_server_returns_404():
    resp = client.get("/servers/does-not-exist")
    assert resp.status_code == 404


def test_delete_server_with_key():
    created = _create_server().json()
    resp = client.delete(f"/servers/{created['id']}", headers={"X-API-Key": VALID_KEY})
    assert resp.status_code == 204
    assert client.get(f"/servers/{created['id']}").status_code == 404


def test_delete_server_no_key_returns_403():
    created = _create_server().json()
    resp = client.delete(f"/servers/{created['id']}")
    assert resp.status_code == 403


def test_delete_nonexistent_server_returns_404():
    resp = client.delete("/servers/does-not-exist", headers={"X-API-Key": VALID_KEY})
    assert resp.status_code == 404


def test_check_server_triggers_health_check():
    created = _create_server().json()
    resp = client.post(f"/servers/{created['id']}/check")
    assert resp.status_code == 200
    assert resp.json()["server_id"] == created["id"]


def test_check_nonexistent_server_returns_404():
    resp = client.post("/servers/does-not-exist/check")
    assert resp.status_code == 404


def test_list_servers_filter_by_status():
    _create_server(name="s1")
    list_resp = client.get("/servers?status=unknown")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1


def test_post_server_invalid_port_returns_422():
    resp = client.post(
        "/servers",
        json={"name": "s1", "host": "localhost", "port": 99999},
        headers={"X-API-Key": VALID_KEY},
    )
    assert resp.status_code == 422
