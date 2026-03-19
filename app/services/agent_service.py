from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import generate_api_key
from app.db.session import get_db
from app.models.agent import Agent
from app.schemas.agent import AgentCreate
from app.services.utils import slugify


class AgentService:
    """Regras de negócio para criação, listagem e validação de agentes."""

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create_agent(self, payload: AgentCreate) -> Agent:
        """Cria agente garantindo slug único e geração de API key quando ausente."""
        base_slug = slugify(payload.slug) if payload.slug else slugify(payload.name)
        slug = base_slug
        i = 2
        while self.db.scalar(select(Agent).where(Agent.slug == slug)) is not None:
            slug = f"{base_slug}-{i}"
            i += 1

        agent = Agent(
            name=payload.name,
            slug=slug,
            api_key=(payload.api_key.strip() if payload.api_key and payload.api_key.strip() else generate_api_key()),
            model=(payload.model.strip() if payload.model and payload.model.strip() else "gpt-4o-mini"),
            prompt=payload.prompt,
            user_id=payload.user_id,
        )
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        return agent

    def list_agents(self) -> list[Agent]:
        """Lista agentes ordenados do mais recente para o mais antigo."""
        return list(self.db.scalars(select(Agent).order_by(Agent.id.desc())).all())

    def get_agent_by_slug(self, slug: str) -> Agent | None:
        """Busca agente por slug único."""
        return self.db.scalar(select(Agent).where(Agent.slug == slug))

    def get_agent_by_slug_and_key(self, slug: str, api_key: str) -> Agent:
        """Valida acesso público do agente por slug + API key."""
        agent = self.db.scalar(select(Agent).where(Agent.slug == slug))
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        if agent.api_key != api_key:
            raise HTTPException(status_code=403, detail="Invalid API key")
        return agent

