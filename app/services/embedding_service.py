from typing import Iterable, List

from openai import OpenAI

from app.core.config import settings


class EmbeddingService:
    """Cliente de embeddings OpenAI utilizado no pipeline de indexação e busca."""

    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY não configurada no .env")
        self._client = OpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_embedding_model

    def embed_texts(self, texts: Iterable[str]) -> List[List[float]]:
        """Gera vetores para uma lista de textos."""
        texts = [t or "" for t in texts]
        if not texts:
            return []
        resp = self._client.embeddings.create(model=self._model, input=texts)
        return [d.embedding for d in resp.data]

