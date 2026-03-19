from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Agent(Base):
    """Entidade de agente com configuração de acesso e prompt base."""

    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    api_key: Mapped[str] = mapped_column(String(255), index=True)
    model: Mapped[str] = mapped_column(String(64), default="gpt-4o-mini", server_default=text("'gpt-4o-mini'"))
    prompt: Mapped[str | None] = mapped_column(String, nullable=True)

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User | None"] = relationship(back_populates="agents")
    documents: Mapped[list["Document"]] = relationship(
        back_populates="agent",
        cascade="all, delete-orphan",
    )

