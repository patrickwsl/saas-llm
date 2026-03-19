from datetime import datetime

from pydantic import BaseModel


class AgentCreate(BaseModel):
    """Payload de entrada para criação de agente."""

    name: str
    slug: str | None = None
    api_key: str | None = None
    model: str | None = None
    prompt: str | None = None
    user_id: int | None = None


class AgentOut(BaseModel):
    """Representação pública de um agente na API."""

    id: int
    name: str
    slug: str
    api_key: str
    model: str
    prompt: str | None
    user_id: int | None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}

