import os

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

_EXPECTED_KEY = os.getenv("API_KEY", "dev-secret-key")


async def verify_api_key(api_key: str = Security(_api_key_header)) -> str:
    """Raise 403 if the X-API-Key header is missing or invalid."""
    if api_key != _EXPECTED_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key",
        )
    return api_key
