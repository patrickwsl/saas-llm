## saas-llm (backend RAG MVP)

Backend SaaS para criação de agentes de IA com RAG (FastAPI + PostgreSQL + Chroma).

### Pré-requisitos

- Python 3.11+
- PostgreSQL rodando localmente (ou via Docker)

### Setup rápido

Crie um ambiente virtual e instale dependências:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Crie seu `.env` a partir do exemplo:

```bash
copy .env.example .env
```

Rode a API:

```bash
uvicorn app.main:app --reload
```

Abra a documentação:
- Swagger: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

### Chaves: `X-API-Key` vs `OPENAI_API_KEY`

- **`OPENAI_API_KEY`** (no `.env`): fica só no servidor. O backend usa para embeddings, chat e modelos OpenAI. Quem chama o endpoint público **não** envia essa chave.
- **`X-API-Key`** (header em `POST /public/agent/{slug}`): é a chave do **agente** armazenada no banco (`agents.api_key`), gerada na criação do agente. O cliente externo envia essa chave para autenticar a chamada **à sua API**; o servidor valida contra o agente identificado pelo `slug`.

