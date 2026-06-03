import asyncio
import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.responses import JSONResponse

from api.auth import verify_api_key
from api.metrics import get_system_metrics
from api.models import Server, ServerIn, ServerOut
from api.poller import poll_server, run_poll_loop

# In-memory store: server_id -> Server
_servers: dict[str, Server] = {}
_poll_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _poll_task
    _poll_task = asyncio.create_task(run_poll_loop(_servers))
    yield
    if _poll_task:
        _poll_task.cancel()
        try:
            await _poll_task
        except asyncio.CancelledError:
            pass


app = FastAPI(title="DevOps Monitor", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    return get_system_metrics()


@app.websocket("/ws/metrics")
async def ws_metrics(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(get_system_metrics())
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass


@app.post("/servers", response_model=ServerOut, status_code=status.HTTP_201_CREATED)
async def create_server(body: ServerIn, _: str = Depends(verify_api_key)):
    server_id = str(uuid.uuid4())
    server = Server(id=server_id, name=body.name, host=body.host, port=body.port)
    _servers[server_id] = server
    return ServerOut(id=server.id, name=server.name, host=server.host, port=server.port, status=server.status)


@app.get("/servers", response_model=list[ServerOut])
async def list_servers(status: str | None = None):
    servers = list(_servers.values())
    if status:
        servers = [s for s in servers if s.status == status]
    return [ServerOut(id=s.id, name=s.name, host=s.host, port=s.port, status=s.status) for s in servers]


@app.get("/servers/{server_id}", response_model=ServerOut)
async def get_server(server_id: str):
    server = _servers.get(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return ServerOut(id=server.id, name=server.name, host=server.host, port=server.port, status=server.status)


@app.delete("/servers/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server(server_id: str, _: str = Depends(verify_api_key)):
    if server_id not in _servers:
        raise HTTPException(status_code=404, detail="Server not found")
    del _servers[server_id]


@app.post("/servers/{server_id}/check")
async def check_server(server_id: str):
    server = _servers.get(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    asyncio.create_task(poll_server(server_id, server.base_url(), _servers))
    return {"message": "Health check triggered", "server_id": server_id}
