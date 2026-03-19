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

