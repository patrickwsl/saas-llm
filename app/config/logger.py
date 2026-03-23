"""
Logging estruturado: JSON para agregadores (Datadog, CloudWatch, ELK, Loki, etc.)
e formato console para desenvolvimento.

Uso típico:
    from app.config.logger import get_logger, log_context

    log = get_logger(__name__)
    log.info("documento processado", extra={"document_id": doc_id})

    with log_context(request_id="abc", user_id="u1"):
        log.info("dentro do request")

Campos fixos no JSON: ts, level, logger, msg, service, env.
`extra` em log calls e o dicionário de `log_context` são mesclados no objeto JSON.
"""

from __future__ import annotations

import json
import logging
import sys
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any, Iterator

# Atributos internos do LogRecord — não exportar como campos de negócio no JSON.
_LOG_RECORD_RESERVED: frozenset[str] = frozenset(
    {
        "name",
        "msg",
        "args",
        "created",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "module",
        "msecs",
        "message",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "thread",
        "threadName",
        "exc_info",
        "exc_text",
        "stack_info",
        "taskName",
    }
)

_log_context_var: ContextVar[dict[str, Any] | None] = ContextVar(
    "app_log_context", default=None
)


def get_log_context() -> dict[str, Any]:
    ctx = _log_context_var.get()
    return dict(ctx) if ctx else {}


@contextmanager
def log_context(**fields: Any) -> Iterator[None]:
    """Mescla campos no contexto atual (útil em middleware FastAPI / tasks)."""
    base = get_log_context()
    token = _log_context_var.set({**base, **fields})
    try:
        yield
    finally:
        _log_context_var.reset(token)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


class JsonFormatter(logging.Formatter):
    """Uma linha JSON por evento; compatível com pipelines que consomem stdout."""

    def __init__(self, service: str, env: str) -> None:
        super().__init__()
        self._service = service
        self._env = env

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "service": self._service,
            "env": self._env,
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        ctx = get_log_context()
        if ctx:
            payload["context"] = ctx

        for key, value in record.__dict__.items():
            if key in _LOG_RECORD_RESERVED or key.startswith("_"):
                continue
            payload[key] = value

        return json.dumps(payload, default=str, ensure_ascii=False)


class ConsoleFormatter(logging.Formatter):
    """Leitura humana no terminal."""

    def __init__(self) -> None:
        super().__init__(fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    def format(self, record: logging.LogRecord) -> str:
        line = super().format(record)
        ctx = get_log_context()
        if ctx:
            line = f"{line} | context={json.dumps(ctx, default=str, ensure_ascii=False)}"
        return line


def configure_logging() -> None:
    """Idempotente: reconfigura o root handler (útil em reload do uvicorn)."""
    from app.core.config import settings

    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    root = logging.getLogger()
    root.setLevel(level)

    for h in list(root.handlers):
        root.removeHandler(h)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    if settings.log_format == "json":
        handler.setFormatter(JsonFormatter(service=settings.service_name, env=settings.env))
    else:
        handler.setFormatter(ConsoleFormatter())

    root.addHandler(handler)

    # Bibliotecas ruidosas: ajuste fino opcional
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
