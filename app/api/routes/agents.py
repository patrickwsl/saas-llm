from fastapi import APIRouter, Depends

from app.schemas.agent import AgentCreate, AgentOut, AgentUpdate
from app.services.agent_service import AgentService


router = APIRouter()


@router.post("", response_model=AgentOut)
def create_agent(payload: AgentCreate, service: AgentService = Depends()):
    """Cria um novo agente com dados de configuração."""
    return service.create_agent(payload)


@router.get("", response_model=list[AgentOut])
def list_agents(service: AgentService = Depends()):
    """Lista todos os agentes cadastrados."""
    return service.list_agents()


@router.patch("/{agent_id}", response_model=AgentOut)
def update_agent(agent_id: int, payload: AgentUpdate, service: AgentService = Depends()):
    """Atualiza configuração do agente (ex.: parâmetros salvos pelo playground)."""
    return service.update_agent(agent_id, payload)

