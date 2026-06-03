from dataclasses import dataclass, field
from pydantic import BaseModel, field_validator


@dataclass
class Server:
    id: str
    name: str
    host: str
    port: int
    status: str = "unknown"

    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


class ServerIn(BaseModel):
    name: str
    host: str
    port: int

    @field_validator("port")
    @classmethod
    def port_range(cls, v: int) -> int:
        if not (1 <= v <= 65535):
            raise ValueError("port must be between 1 and 65535")
        return v


class ServerOut(BaseModel):
    id: str
    name: str
    host: str
    port: int
    status: str
