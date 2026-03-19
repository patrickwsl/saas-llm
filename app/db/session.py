from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


def _database_url() -> str:
    """Retorna URL de conexão configurada, com fallback local SQLite."""
    if settings.database_url and settings.database_url.strip():
        return settings.database_url
    return "sqlite:///./local.db"


engine = create_engine(_database_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Classe base para todos os modelos SQLAlchemy."""

    pass


def get_db():
    """Dependency FastAPI para abrir/fechar sessão de banco por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

