import asyncio

import httpx

from api.models import Server


async def poll_server(server_id: str, url: str, store: dict[str, Server]) -> None:
    """Check the health of one server and update its status in store."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{url}/health")
        store[server_id].status = "UP" if response.status_code == 200 else "DEGRADED"
    except (httpx.ConnectError, httpx.TimeoutException, Exception):
        store[server_id].status = "DOWN"


async def run_poll_loop(store: dict[str, Server], interval: int = 10) -> None:
    """Continuously poll all servers every `interval` seconds."""
    while True:
        if store:
            await asyncio.gather(
                *(poll_server(sid, srv.base_url(), store) for sid, srv in store.items())
            )
        await asyncio.sleep(interval)
