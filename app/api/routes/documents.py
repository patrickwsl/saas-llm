from fastapi import APIRouter, Depends, File, UploadFile

from app.schemas.document import DocumentOut
from app.services.document_service import DocumentService


router = APIRouter()


@router.post("/agents/{agent_id}/documents", response_model=DocumentOut)
async def upload_document(
    agent_id: int,
    file: UploadFile = File(...),
    service: DocumentService = Depends(),
):
    """Recebe arquivo para a base de conhecimento e inicia indexação."""
    return await service.upload_document(agent_id=agent_id, file=file)

