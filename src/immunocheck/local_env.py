"""Leitura mínima e explícita da configuração local ignorada pelo Git."""

from __future__ import annotations

from pathlib import Path

ALLOWED_LOCAL_KEYS = frozenset(
    {
        "TELEGRAM_BOT_TOKEN",
        "TESSERACT_CMD",
        "OLLAMA_BASE_URL",
        "OLLAMA_MODEL",
        "PIPELINE_VERSION",
        "RETRIEVAL_MODE",
        "LOG_LEVEL",
        # Modo demonstração (ADR-057).
        "LLM_BACKEND",
        "LLM_API_KEY",
        "LLM_API_MODEL",
        "LLM_API_BASE_URL",
        "LLM_API_RESPONSE_FORMAT",
        "LLM_API_EXTRA_JSON",
        "TELEGRAM_ALLOWED_CHAT_IDS",
    }
)


def read_local_env(path: Path) -> dict[str, str]:
    """Lê somente chaves permitidas, sem expansão ou execução de conteúdo."""

    if not path.is_file():
        raise FileNotFoundError("Arquivo .env local não encontrado.")
    values: dict[str, str] = {}
    for line_number, raw_line in enumerate(path.read_text("utf-8-sig").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, raw_value = line.partition("=")
        key = key.strip()
        if not separator or not key:
            raise ValueError(f"Linha {line_number} do .env possui formato inválido.")
        if key not in ALLOWED_LOCAL_KEYS:
            continue
        if key in values:
            raise ValueError(f"A chave {key} aparece mais de uma vez no .env.")
        values[key] = _unquote(raw_value.strip(), line_number)
    return values


def _unquote(value: str, line_number: int) -> str:
    if not value:
        return ""
    if value[0] not in {'"', "'"}:
        return value
    if len(value) < 2 or value[-1] != value[0]:
        raise ValueError(f"Aspas não fechadas na linha {line_number} do .env.")
    return value[1:-1]
