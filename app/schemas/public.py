from pydantic import BaseModel


class PublicQuestionIn(BaseModel):
    """Pergunta enviada ao endpoint público do agente."""

    question: str


class PublicAnswerOut(BaseModel):
    """Resposta do agente com fontes utilizadas no contexto."""

    answer: str
    sources: list[str] = []

