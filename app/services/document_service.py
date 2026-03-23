import os
from pathlib import Path

from fastapi import Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config.logger import get_logger
from app.core.config import settings
from app.db.session import get_db
from app.models.agent import Agent
from app.models.document import Document
from app.services.embedding_service import EmbeddingService

log = get_logger(__name__)


def _read_plaintext(path: Path) -> str:
    """Lê ficheiro de texto; PDFs são extraídos com pypdf (read_text em binário corrompe o RAG)."""
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        parts: list[str] = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                parts.append(t)
        return "\n\n".join(parts).strip()
    return path.read_text(encoding="utf-8", errors="ignore")


def _simple_chunk(text: str, max_chars: int = 1200) -> list[str]:
    """Divide texto em blocos aproximados para indexação vetorial."""
    text = text.replace("\r\n", "\n")
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        match len(current) + len(para) + 2 <= max_chars:
            case True:
                current = f"{current}\n\n{para}" if current else para
            case False:
                if current:
                    chunks.append(current)
                match len(para) <= max_chars:
                    case True:
                        current = para
                    case False:
                        for i in range(0, len(para), max_chars):
                            chunks.append(para[i : i + max_chars])
                        current = ""
    if current:
        chunks.append(current)
    return chunks


class DocumentService:
    """Gerencia upload, leitura e indexação vetorial de documentos."""

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    async def upload_document(self, agent_id: int, file: UploadFile) -> Document:
        """Salva arquivo em disco, cria registro e dispara processamento."""
        agent = self.db.scalar(select(Agent).where(Agent.id == agent_id))
        if not agent:
            log.warning("upload rejeitado: agente não encontrado", extra={"agent_id": agent_id})
            raise HTTPException(status_code=404, detail="Agent not found")

        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)

        safe_name = os.path.basename(file.filename or "document")
        target_path = upload_dir / safe_name

        content = await file.read()
        target_path.write_bytes(content)

        doc = Document(
            filename=safe_name,
            path=str(target_path),
            status="pending",
            agent_id=agent.id,
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)

        log.info(
            "documento enviado",
            extra={"document_id": doc.id, "agent_id": agent.id, "document_filename": safe_name},
        )
        self.process_document(doc)
        return doc

    def process_document(self, doc: Document) -> None:
        """Lê o documento, gera embeddings e persiste chunks no Chroma."""
        from chromadb import PersistentClient

        path = Path(doc.path)
        if not path.exists():
            log.error(
                "arquivo do documento ausente em disco",
                extra={"document_id": doc.id, "path": str(path)},
            )
            raise HTTPException(status_code=400, detail="Arquivo do documento não encontrado")

        doc.status = "processing"
        self.db.add(doc)
        self.db.commit()

        try:
            raw = _read_plaintext(path)
            chunks = _simple_chunk(raw, max_chars=1500)
            if not chunks:
                log.info(
                    "processamento concluído sem chunks (texto vazio)",
                    extra={"document_id": doc.id, "agent_id": doc.agent_id},
                )
                doc.status = "done"
                self.db.commit()
                return

            log.info(
                "indexando documento",
                extra={
                    "document_id": doc.id,
                    "agent_id": doc.agent_id,
                    "chunk_count": len(chunks),
                },
            )

            embedder = EmbeddingService()
            vectors = embedder.embed_texts(chunks)

            client = PersistentClient(path=settings.chroma_dir)
            collection_name = f"agent_{doc.agent_id}"
            collection = client.get_or_create_collection(name=collection_name)

            ids = [f"{doc.id}:{i}" for i in range(len(chunks))]
            metadatas = [
                {
                    "agent_id": doc.agent_id,
                    "document_id": doc.id,
                    "chunk_index": i,
                    "filename": doc.filename,
                }
                for i in range(len(chunks))
            ]

            collection.upsert(ids=ids, embeddings=vectors, metadatas=metadatas, documents=chunks)

            doc.status = "done"
            self.db.add(doc)
            self.db.commit()
            log.info(
                "documento indexado",
                extra={"document_id": doc.id, "agent_id": doc.agent_id, "chunk_count": len(chunks)},
            )
        except Exception:
            log.exception(
                "falha ao processar documento",
                extra={"document_id": doc.id, "agent_id": doc.agent_id},
            )
            raise

