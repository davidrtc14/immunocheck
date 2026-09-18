"""Estruturas puras para consolidar o preflight de uma entrega."""

from __future__ import annotations

from collections.abc import Mapping, Sequence


def summarize_readiness(
    checks: Sequence[Mapping[str, object]],
    human_gates: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    """Separa prontidão técnica de autorizações humanas obrigatórias."""

    if not checks:
        raise ValueError("O preflight precisa conter verificações técnicas.")
    names = [check.get("name") for check in checks]
    if any(not isinstance(name, str) or not name for name in names):
        raise ValueError("Toda verificação precisa de um nome.")
    if len(names) != len(set(names)):
        raise ValueError("Os nomes das verificações precisam ser únicos.")
    if any(not isinstance(check.get("passed"), bool) for check in checks):
        raise ValueError("Toda verificação precisa de resultado booleano.")
    if any(not isinstance(check.get("required"), bool) for check in checks):
        raise ValueError("Toda verificação precisa declarar se é obrigatória.")

    required = [check for check in checks if check["required"] is True]
    failed_required = [str(check["name"]) for check in required if check["passed"] is False]
    open_human_gates = [
        str(gate["name"])
        for gate in human_gates
        if gate.get("completed") is not True
    ]
    technical_ready = not failed_required
    release_ready = technical_ready and not open_human_gates
    return {
        "technical_ready": technical_ready,
        "release_ready": release_ready,
        "required_checks": len(required),
        "passed_required_checks": len(required) - len(failed_required),
        "failed_required_checks": failed_required,
        "open_human_gates": open_human_gates,
        "classification": (
            "ready_for_main"
            if release_ready
            else "technical_blockers"
            if not technical_ready
            else "release_candidate_blocked_by_human_gates"
        ),
    }
