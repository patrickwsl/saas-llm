from datetime import datetime

from pydantic import BaseModel, Field


class AgentCreate(BaseModel):
    """Payload de entrada para criação de agente."""

    name: str
    slug: str | None = None
    model: str | None = None
    prompt: str | None = None
    user_id: int | None = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    max_tokens: int | None = Field(default=None, ge=1, le=128000)
    rag_top_k: int = Field(default=5, ge=1, le=50)


class AgentUpdate(BaseModel):
    """Atualização parcial de agente (playground / admin)."""

    name: str | None = None
    model: str | None = None
    prompt: str | None = None
    api_key: str | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    top_p: float | None = Field(default=None, ge=0.0, le=1.0)
    max_tokens: int | None = Field(default=None, ge=1, le=128000)
    rag_top_k: int | None = Field(default=None, ge=1, le=50)


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
    temperature: float
    top_p: float
    max_tokens: int | None
    rag_top_k: int

    model_config = {"from_attributes": True}
