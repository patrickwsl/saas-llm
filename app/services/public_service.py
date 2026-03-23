from fastapi import Depends
from sqlalchemy.orm import Session

from app.config.logger import get_logger
from app.db.session import get_db
from app.schemas.public import PublicAnswerOut, PublicQuestionIn
from app.services.agent_service import AgentService
from app.services.rag_service import RagService

log = get_logger(__name__)


class PublicService:
    """Orquestra validação do agente e execução do RAG no endpoint público."""

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.agents = AgentService(db)
        self.rag = RagService()

    def answer(self, slug: str, api_key: str, payload: PublicQuestionIn) -> PublicAnswerOut:
        """Retorna resposta do agente com fontes para a pergunta recebida."""
        agent = self.agents.get_agent_by_slug_and_key(slug=slug, api_key=api_key)
        q = payload.question.strip()
        log.info(
            "pergunta pública recebida",
            extra={
                "agent_id": agent.id,
                "slug": slug,
                "question_chars": len(q),
                "model": agent.model,
            },
        )
        raw = payload.model_dump(exclude_unset=True)

        def _float_param(key: str, fallback: float) -> float:
            match key in raw:
                case False:
                    return fallback
                case True:
                    match raw[key]:
                        case None:
                            return fallback
                        case v:
                            return float(v)

        temperature = _float_param("temperature", agent.temperature)
        top_p = _float_param("top_p", agent.top_p)

        match "max_tokens" in raw:
            case False:
                max_tokens = agent.max_tokens
            case True:
                max_tokens = raw["max_tokens"]

        match "rag_top_k" in raw:
            case False:
                rag_top_k = agent.rag_top_k
            case True:
                match raw["rag_top_k"]:
                    case None:
                        rag_top_k = agent.rag_top_k
                    case rk:
                        rag_top_k = int(rk)

        match "prompt" in raw:
            case False:
                prompt = agent.prompt
            case True:
                match raw["prompt"]:
                    case None:
                        prompt = agent.prompt
                    case p:
                        prompt = p

        answer, sources = self.rag.answer_question(
            agent_id=agent.id,
            question=payload.question,
            prompt=prompt,
            model=agent.model,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            rag_top_k=rag_top_k,
        )
        log.info(
            "resposta pública gerada",
            extra={
                "agent_id": agent.id,
                "slug": slug,
                "source_count": len(sources),
                "answer_chars": len(answer),
            },
        )
        return PublicAnswerOut(answer=answer, sources=sources)

