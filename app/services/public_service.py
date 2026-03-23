from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.public import PublicAnswerOut, PublicQuestionIn
from app.services.agent_service import AgentService
from app.services.rag_service import RagService


class PublicService:
    """Orquestra validação do agente e execução do RAG no endpoint público."""

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.agents = AgentService(db)
        self.rag = RagService()

    def answer(self, slug: str, api_key: str, payload: PublicQuestionIn) -> PublicAnswerOut:
        """Retorna resposta do agente com fontes para a pergunta recebida."""
        agent = self.agents.get_agent_by_slug_and_key(slug=slug, api_key=api_key)
        raw = payload.model_dump(exclude_unset=True)

        def _float_param(key: str, fallback: float) -> float:
            if key not in raw:
                return fallback
            v = raw[key]
            return fallback if v is None else float(v)

        temperature = _float_param("temperature", agent.temperature)
        top_p = _float_param("top_p", agent.top_p)

        if "max_tokens" not in raw:
            max_tokens = agent.max_tokens
        else:
            max_tokens = raw["max_tokens"]

        if "rag_top_k" not in raw:
            rag_top_k = agent.rag_top_k
        else:
            rk = raw["rag_top_k"]
            rag_top_k = agent.rag_top_k if rk is None else int(rk)
        answer, sources = self.rag.answer_question(
            agent_id=agent.id,
            question=payload.question,
            prompt=agent.prompt,
            model=agent.model,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            rag_top_k=rag_top_k,
        )
        return PublicAnswerOut(answer=answer, sources=sources)

