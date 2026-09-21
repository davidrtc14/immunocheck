from pathlib import Path

from scripts.release_preflight import REPOSITORY, _resolve_output_path


def test_resolves_relative_output_against_repository() -> None:
    assert _resolve_output_path(Path("output/preflight.json")) == (
        REPOSITORY / "output/preflight.json"
    )


def test_preserves_absolute_output_path(tmp_path: Path) -> None:
    output = tmp_path / "preflight.json"

    assert _resolve_output_path(output) == output
