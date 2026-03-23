from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import generate_api_key
from app.db.session import get_db
from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentUpdate
from app.services.utils import slugify


class AgentService:
    """Regras de negócio para criação, listagem e validação de agentes."""

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create_agent(self, payload: AgentCreate) -> Agent:
        """Cria agente garantindo slug único e API key gerada no servidor."""
        base_slug = slugify(payload.slug) if payload.slug else slugify(payload.name)
        slug = base_slug
        i = 2
        while self.db.scalar(select(Agent).where(Agent.slug == slug)) is not None:
            slug = f"{base_slug}-{i}"
            i += 1

        agent = Agent(
            name=payload.name,
            slug=slug,
            api_key=generate_api_key(),
            model=(payload.model.strip() if payload.model and payload.model.strip() else "gpt-4o-mini"),
            prompt=payload.prompt,
            user_id=payload.user_id,
            temperature=payload.temperature,
            top_p=payload.top_p,
            max_tokens=payload.max_tokens,
            rag_top_k=payload.rag_top_k,
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

    def get_agent(self, agent_id: int) -> Agent:
        """Retorna agente por id ou 404."""
        agent = self.db.scalar(select(Agent).where(Agent.id == agent_id))
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return agent

    def update_agent(self, agent_id: int, payload: AgentUpdate) -> Agent:
        """Aplica apenas campos informados no payload."""
        agent = self.get_agent(agent_id)
        data = payload.model_dump(exclude_unset=True)
        if "api_key" in data and data["api_key"] is not None:
            data["api_key"] = data["api_key"].strip()
            if not data["api_key"]:
                del data["api_key"]
        if "model" in data and data["model"] is not None:
            data["model"] = data["model"].strip()
            if not data["model"]:
                del data["model"]
        for key, value in data.items():
            setattr(agent, key, value)
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        return agent

    def get_agent_by_slug_and_key(self, slug: str, api_key: str) -> Agent:
        """Valida acesso público do agente por slug + API key."""
        agent = self.db.scalar(select(Agent).where(Agent.slug == slug))
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        if agent.api_key != api_key:
            raise HTTPException(status_code=403, detail="Invalid API key")
        return agent

