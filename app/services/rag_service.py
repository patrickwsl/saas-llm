from typing import List, Tuple

from fastapi import HTTPException
from openai import OpenAI

from app.config.logger import get_logger
from app.core.config import settings
from app.services.embedding_service import EmbeddingService

log = get_logger(__name__)


class RagService:
    """Executa fluxo de RAG: embedding da pergunta, busca vetorial e geração."""

    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY não configurada")
        self._client = OpenAI(api_key=settings.openai_api_key)
        self._embedder = EmbeddingService()
        self._default_model = settings.openai_model

    def _get_collection(self, agent_id: int):
        """Obtém a coleção vetorial isolada por agente."""
        from chromadb import PersistentClient

        client = PersistentClient(path=settings.chroma_dir)
        name = f"agent_{agent_id}"
        return client.get_or_create_collection(name=name)

    def answer_question(
        self,
        agent_id: int,
        question: str,
        *,
        prompt: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        top_p: float = 1.0,
        max_tokens: int | None = None,
        rag_top_k: int = 5,
    ) -> Tuple[str, List[str]]:
        """Gera resposta baseada em contexto recuperado da base vetorial."""
        q = question.strip()
        if not q:
            log.warning("rag: pergunta vazia rejeitada", extra={"agent_id": agent_id})
            raise HTTPException(status_code=400, detail="Pergunta vazia")

        collection = self._get_collection(agent_id)

        q_embed = self._embedder.embed_texts([q])[0]
        n_results = max(1, min(rag_top_k, 50))
        results = collection.query(query_embeddings=[q_embed], n_results=n_results)

        docs: List[str] = []
        sources: List[str] = []
        if results and results.get("documents"):
            docs_raw = results["documents"][0]
            metas = results.get("metadatas", [[]])[0]
            docs = [str(d) for d in docs_raw]
            filenames = {m.get("filename") for m in metas if isinstance(m, dict) and m.get("filename")}
            sources = sorted(filenames)

        log.info(
            "rag: busca vetorial concluída",
            extra={
                "agent_id": agent_id,
                "rag_top_k": n_results,
                "chunk_hits": len(docs),
                "distinct_sources": len(sources),
            },
        )

        context = "\n\n".join(docs) if docs else "Nenhum contexto relevante encontrado na base de conhecimento."

        system_prompt = (
            prompt
            or "Você é um assistente que responde apenas com base no contexto fornecido. "
            "Se não encontrar a resposta no contexto, diga que não sabe em vez de inventar."
        )

        chat_model = (model or "").strip() or self._default_model
        kwargs: dict = {
            "model": chat_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Contexto:\n{context}\n\nPergunta do usuário: {q}",
                },
            ],
            "temperature": temperature,
            "top_p": top_p,
        }
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        completion = self._client.chat.completions.create(**kwargs)

        answer = completion.choices[0].message.content or ""
        out = answer.strip()
        log.info(
            "rag: resposta do modelo recebida",
            extra={
                "agent_id": agent_id,
                "model": chat_model,
                "answer_chars": len(out),
                "source_count": len(sources),
            },
        )
        return out, sources

