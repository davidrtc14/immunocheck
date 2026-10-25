"""Modo demonstração remota (ADR-057): a pipeline v7 com o modelo de linguagem servido por uma API.

`bootstrap.py` está congelado, e todas as versões criam o cliente de LLM pela mesma função,
`_build_llm_client`. Com `LLM_BACKEND=api`, `install_api_backend()` troca essa função por uma que
devolve o cliente de API, envolvido no mesmo controle de contexto. Corpus, BGE-M3 (na CPU), roteamento,
verificação da v7 e referências por metadados não mudam. Não é o sistema avaliado no TCC.
"""

from __future__ import annotations

import json
import os
from collections.abc import Mapping

from immunocheck import bootstrap
from immunocheck.infrastructure.api_llm import OpenAICompatibleClient
from immunocheck.infrastructure.context_budget import ContextBudgetClient

BACKENDS = ("ollama", "api")
DEFAULT_API_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_CONTEXT_TOKENS = 8_192

DEMO_NOTICE = (
    "⚠️ MODO DEMONSTRAÇÃO: nesta versão, o texto analisado é enviado a um serviço externo de "
    "inteligência artificial, que pode conservá-lo conforme a política dele. Envie apenas alegações "
    "gerais sobre vacinas, sem dados pessoais ou de saúde. Esta versão não é a avaliada no TCC."
)


def resolve_backend(environ: Mapping[str, str] | None = None) -> str:
    env = os.environ if environ is None else environ
    backend = env.get("LLM_BACKEND", "ollama").strip().lower() or "ollama"
    if backend not in BACKENDS:
        raise ValueError(f"LLM_BACKEND deve ser um de: {', '.join(BACKENDS)}.")
    return backend


def is_demo_mode(environ: Mapping[str, str] | None = None) -> bool:
    return resolve_backend(environ) == "api"


def build_api_client(
    environ: Mapping[str, str] | None = None, *, temperature: float = 0.0
) -> ContextBudgetClient:
    env = os.environ if environ is None else environ
    raw_extra = env.get("LLM_API_EXTRA_JSON", "").strip()
    try:
        extra = json.loads(raw_extra) if raw_extra else {}
    except json.JSONDecodeError as exc:
        raise ValueError("LLM_API_EXTRA_JSON deve ser um objeto JSON.") from exc
    if not isinstance(extra, dict):
        # ValueError, como os demais erros de configuração que `telegram.main` reporta.
        raise ValueError("LLM_API_EXTRA_JSON deve ser um objeto JSON.")  # noqa: TRY004
    try:
        context_tokens = int(env.get("LLM_API_CONTEXT_TOKENS", str(DEFAULT_CONTEXT_TOKENS)))
    except ValueError as exc:
        raise ValueError("LLM_API_CONTEXT_TOKENS deve ser um inteiro.") from exc
    client = OpenAICompatibleClient(
        api_key=env.get("LLM_API_KEY", ""),
        model=env.get("LLM_API_MODEL", ""),
        base_url=env.get("LLM_API_BASE_URL", DEFAULT_API_BASE_URL).strip() or DEFAULT_API_BASE_URL,
        temperature=temperature,
        response_format=env.get("LLM_API_RESPONSE_FORMAT", "json_schema").strip() or "json_schema",
        extra_body=extra,
    )
    # O mesmo orçamento de contexto do Qwen3-8B local mantém os prompts idênticos aos da v7.
    return ContextBudgetClient(client, context_tokens=context_tokens)


def install_api_backend(environ: Mapping[str, str] | None = None) -> None:
    """Faz todas as pipelines montadas a partir daqui usarem a API; valida a configuração já."""

    build_api_client(environ)

    def api_llm_client(
        *,
        model: str | None,
        base_url: str | None,
        think: bool = False,
        temperature: float = 0.0,
    ) -> ContextBudgetClient:
        del model, base_url, think  # o modelo da API vem de LLM_API_MODEL
        return build_api_client(environ, temperature=temperature)

    bootstrap._build_llm_client = api_llm_client
