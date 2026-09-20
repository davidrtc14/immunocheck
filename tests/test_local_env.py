from __future__ import annotations

from pathlib import Path

import pytest

from immunocheck.local_env import read_local_env


def test_reads_only_allowed_values_without_expansion(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "# local\n"
        "TELEGRAM_BOT_TOKEN='123:token-seguro'\n"
        "OLLAMA_MODEL=qwen3:8b\n"
        "UNKNOWN=$(comando-nao-executado)\n",
        "utf-8",
    )

    values = read_local_env(env_file)

    assert values == {
        "TELEGRAM_BOT_TOKEN": "123:token-seguro",
        "OLLAMA_MODEL": "qwen3:8b",
    }


def test_rejects_duplicate_or_malformed_allowed_configuration(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("TELEGRAM_BOT_TOKEN=a\nTELEGRAM_BOT_TOKEN=b\n", "utf-8")

    with pytest.raises(ValueError, match="mais de uma vez"):
        read_local_env(env_file)


def test_rejects_unclosed_quotes(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text('TELEGRAM_BOT_TOKEN="incompleto\n', "utf-8")

    with pytest.raises(ValueError, match="Aspas não fechadas"):
        read_local_env(env_file)
