from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações carregadas do `.env` para infraestrutura e integrações."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    env: str = "local"
    service_name: str = "saas-llm"
    log_level: str = "INFO"
    log_format: str = "console"
    database_url: str | None = None
    app_secret_key: str = "change-me"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    upload_dir: str = "app/uploads"
    chroma_dir: str = "app/chroma"


settings = Settings()

