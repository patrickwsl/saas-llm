from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.public import PublicAnswerOut
from app.services.agent_service import AgentService
from app.services.rag_service import RagService


class PublicService:
    """Orquestra validação do agente e execução do RAG no endpoint público."""

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.agents = AgentService(db)
        self.rag = RagService()

    def answer(self, slug: str, api_key: str, question: str) -> PublicAnswerOut:
        """Retorna resposta do agente com fontes para a pergunta recebida."""
        agent = self.agents.get_agent_by_slug_and_key(slug=slug, api_key=api_key)
        answer, sources = self.rag.answer_question(agent_id=agent.id, question=question, prompt=agent.prompt)
        return PublicAnswerOut(answer=answer, sources=sources)

