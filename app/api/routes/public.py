from fastapi import APIRouter, Depends, Header, HTTPException

from app.schemas.public import PublicQuestionIn, PublicAnswerOut
from app.services.public_service import PublicService


router = APIRouter()


@router.post("/agent/{slug}", response_model=PublicAnswerOut)
def ask_public_agent(
    slug: str,
    payload: PublicQuestionIn,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    service: PublicService = Depends(),
):
    """Endpoint público para consultar um agente por slug."""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key header")
    return service.answer(slug=slug, api_key=x_api_key, payload=payload)

