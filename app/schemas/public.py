from pydantic import BaseModel, Field


class PublicQuestionIn(BaseModel):
    """Pergunta ao endpoint público; campos opcionais sobrescrevem o perfil do agente."""

    question: str
    prompt: str | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    top_p: float | None = Field(default=None, ge=0.0, le=1.0)
    max_tokens: int | None = Field(default=None, ge=1, le=128000)
    rag_top_k: int | None = Field(default=None, ge=1, le=50)


class PublicAnswerOut(BaseModel):
    """Resposta do agente com fontes utilizadas no contexto."""

    answer: str
    sources: list[str] = []
