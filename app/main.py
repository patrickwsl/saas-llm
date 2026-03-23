from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.config.logger import configure_logging
from app.api.routes.agents import router as agents_router
from app.api.routes.documents import router as documents_router
from app.api.routes.public import router as public_router
from app.db.session import Base, engine
from app.models import agent as _agent_model  # noqa: F401
from app.models import document as _document_model  # noqa: F401
from app.models import user as _user_model  # noqa: F401


app = FastAPI(title="saas-llm backend (RAG MVP)")


@app.on_event("startup")
def on_startup():
    """Inicializa esquema relacional e ajustes de compatibilidade do banco."""
    configure_logging()
    Base.metadata.create_all(bind=engine)
    _ensure_schema()


def _ensure_schema() -> None:
    """Aplica alterações simples de esquema quando Alembic não está em uso."""
    with engine.begin() as conn:
        dialect = engine.dialect.name
        if dialect == "postgresql":
            conn.execute(
                text(
                    "ALTER TABLE agents "
                    "ADD COLUMN IF NOT EXISTS model VARCHAR(64) NOT NULL DEFAULT 'gpt-4o-mini'"
                )
            )
            conn.execute(
                text(
                    "ALTER TABLE agents "
                    "ADD COLUMN IF NOT EXISTS temperature DOUBLE PRECISION NOT NULL DEFAULT 0.7"
                )
            )
            conn.execute(
                text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS top_p DOUBLE PRECISION NOT NULL DEFAULT 1.0")
            )
            conn.execute(text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS max_tokens INTEGER"))
            conn.execute(
                text("ALTER TABLE agents ADD COLUMN IF NOT EXISTS rag_top_k INTEGER NOT NULL DEFAULT 5")
            )
        elif dialect == "sqlite":
            # SQLite pode falhar quando a coluna já existe; nesse caso a operação é ignorada.
            for stmt in (
                "ALTER TABLE agents ADD COLUMN model VARCHAR(64) DEFAULT 'gpt-4o-mini'",
                "ALTER TABLE agents ADD COLUMN temperature REAL DEFAULT 0.7",
                "ALTER TABLE agents ADD COLUMN top_p REAL DEFAULT 1.0",
                "ALTER TABLE agents ADD COLUMN max_tokens INTEGER",
                "ALTER TABLE agents ADD COLUMN rag_top_k INTEGER DEFAULT 5",
            ):
                try:
                    conn.execute(text(stmt))
                except Exception:
                    pass


@app.get("/health")
def health():
    """Healthcheck simples para monitoramento."""
    return {"status": "ok"}


app.include_router(agents_router, prefix="/agents", tags=["agents"])
app.include_router(documents_router, tags=["documents"])
app.include_router(public_router, prefix="/public", tags=["public"])

app.mount("/", StaticFiles(directory="app/static", html=True), name="static")

