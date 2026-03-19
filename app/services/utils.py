import re


def slugify(value: str) -> str:
    """Normaliza texto para formato slug com caracteres ASCII simples."""
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9\s-]", "", value)
    value = re.sub(r"[\s-]+", "-", value).strip("-")
    return value or "agent"

