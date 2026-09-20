"""Inicia o bot usando o `.env` local sem imprimir credenciais."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from immunocheck.local_env import read_local_env
from immunocheck.telegram import main as telegram_main

REPOSITORY = Path(__file__).resolve().parents[1]


def main() -> int:
    try:
        local_values = read_local_env(REPOSITORY / ".env")
        for key, value in local_values.items():
            if value:
                os.environ.setdefault(key, value)
        if not os.getenv("TELEGRAM_BOT_TOKEN", "").strip():
            raise ValueError("Preencha TELEGRAM_BOT_TOKEN no arquivo .env local.")
    except (FileNotFoundError, UnicodeError, ValueError) as exc:
        print(f"Configuração local inválida: {exc}", file=sys.stderr)
        return 2
    return telegram_main()


if __name__ == "__main__":
    raise SystemExit(main())
