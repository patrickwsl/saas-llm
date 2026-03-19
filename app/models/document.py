from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Document(Base):
    """Arquivo enviado para compor a base de conhecimento de um agente."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    path: Mapped[str] = mapped_column(String(1024))
    status: Mapped[str] = mapped_column(String(32), default="pending")

    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id"), index=True)
    agent: Mapped["Agent"] = relationship(back_populates="documents")

