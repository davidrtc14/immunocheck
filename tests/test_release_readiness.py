from __future__ import annotations

import pytest

from immunocheck.release_readiness import summarize_readiness


def test_readiness_distinguishes_technical_state_from_human_gates() -> None:
    summary = summarize_readiness(
        [
            {"name": "tests", "passed": True, "required": True},
            {"name": "database", "passed": True, "required": True},
        ],
        [{"name": "institutional", "completed": False}],
    )

    assert summary["technical_ready"] is True
    assert summary["release_ready"] is False
    assert summary["classification"] == "release_candidate_blocked_by_human_gates"
    assert summary["open_human_gates"] == ["institutional"]


def test_required_failure_blocks_technical_readiness() -> None:
    summary = summarize_readiness(
        [{"name": "tests", "passed": False, "required": True}],
        [],
    )

    assert summary["technical_ready"] is False
    assert summary["release_ready"] is False
    assert summary["failed_required_checks"] == ["tests"]
    assert summary["classification"] == "technical_blockers"


def test_all_gates_closed_allows_main() -> None:
    summary = summarize_readiness(
        [{"name": "tests", "passed": True, "required": True}],
        [{"name": "live_demo", "completed": True}],
    )

    assert summary["release_ready"] is True
    assert summary["classification"] == "ready_for_main"


@pytest.mark.parametrize(
    "checks",
    (
        [],
        [{"name": "", "passed": True, "required": True}],
        [{"name": "a", "passed": True, "required": True}] * 2,
        [{"name": "a", "passed": "yes", "required": True}],
    ),
)
def test_invalid_checks_are_rejected(checks: list[dict[str, object]]) -> None:
    with pytest.raises(ValueError):
        summarize_readiness(checks, [])
