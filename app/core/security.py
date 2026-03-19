import secrets

from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Gera hash seguro de senha usando bcrypt."""
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Valida senha em texto puro contra o hash persistido."""
    return pwd_context.verify(password, password_hash)


def generate_api_key() -> str:
    """Cria chave de API aleatória para acesso aos agentes."""
    return secrets.token_urlsafe(32)

