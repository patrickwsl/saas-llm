from pydantic import BaseModel


class DocumentOut(BaseModel):
    """Dados de documento retornados pelas rotas de upload/listagem."""

    id: int
    filename: str
    path: str
    status: str
    agent_id: int

    model_config = {"from_attributes": True}

