# DevOps Monitoring Dashboard

A real-time DevOps monitoring dashboard built with **FastAPI** (backend) and **Streamlit** (frontend).

## Features

- Live CPU, memory, and disk metrics via REST + WebSocket
- Server registry with background health polling
- API key authentication for write endpoints
- Pytest test suite with >70% coverage

## Quick Start

```bash
# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Start the API (terminal 1)
uvicorn api.main:app --reload --port 8000

# Start the dashboard (terminal 2)
streamlit run dashboard/app.py
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_KEY` | `dev-secret-key` | API key for protected endpoints |

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | public | Health check |
| GET | `/metrics` | public | System metrics snapshot |
| WS | `/ws/metrics` | public | Live metrics stream (1 s) |
| POST | `/servers` | key | Register a server |
| GET | `/servers` | public | List servers (optional `?status=UP`) |
| GET | `/servers/{id}` | public | Get one server |
| DELETE | `/servers/{id}` | key | Remove a server |
| POST | `/servers/{id}/check` | public | Trigger immediate health check |

## Tests

```bash
pytest tests/ -v
pytest tests/ --cov=api
```
