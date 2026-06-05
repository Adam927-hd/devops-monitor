import pytest
import httpx

from api.models import Server
from api.poller import poll_server


def _make_store(status="unknown") -> tuple[str, dict]:
    server = Server(id="test-id", name="test", host="localhost", port=9999, status=status)
    return "test-id", {"test-id": server}


@pytest.mark.asyncio
async def test_poll_server_up(respx_mock):
    sid, store = _make_store()
    respx_mock.get("http://localhost:9999/health").mock(return_value=httpx.Response(200))
    await poll_server(sid, "http://localhost:9999", store)
    assert store[sid].status == "UP"


@pytest.mark.asyncio
async def test_poll_server_degraded(respx_mock):
    sid, store = _make_store()
    respx_mock.get("http://localhost:9999/health").mock(return_value=httpx.Response(500))
    await poll_server(sid, "http://localhost:9999", store)
    assert store[sid].status == "DEGRADED"


@pytest.mark.asyncio
async def test_poll_server_down_on_connect_error(respx_mock):
    sid, store = _make_store()
    respx_mock.get("http://localhost:9999/health").mock(side_effect=httpx.ConnectError("refused"))
    await poll_server(sid, "http://localhost:9999", store)
    assert store[sid].status == "DOWN"
