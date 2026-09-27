from pathlib import Path

ROOT = Path(__file__).parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text("utf-8")


def test_current_guides_identify_v3_as_active_and_v1_as_historical() -> None:
    readme = _read("README.md")
    architecture = _read("docs/ARCHITECTURE.md")
    reproduction = _read("docs/REPRODUCTION_AND_DEMO.md")

    assert "v3" in readme and "padrão local do bot e da CLI" in readme
    assert "BGE-M3" in architecture and "Top 15" in architecture
    assert "PIPELINE_VERSION=v1" in architecture
    assert "Esses comandos usam a v3" in reproduction
    assert "v3 descartada" not in reproduction


def test_delivery_package_links_to_existing_evidence() -> None:
    required = (
        "docs/PROJECT_BRIEF.md",
        "docs/ARCHITECTURE.md",
        "docs/ARCHITECTURE_DECISIONS.md",
        "docs/RESEARCH_PROTOCOL.md",
        "docs/CORPUS_DATASET_PHASE5.md",
        "evaluation/results/test/FINAL_TEST_REPORT.md",
        "evaluation/refinement_v2/CONSOLIDATION_REPORT.md",
        "evaluation/refinement_v3/confirmatory/RESULTS.md",
        "docs/V3_INTEGRATION.md",
        "evaluation/results/performance/OPERATIONAL_PERFORMANCE_REPORT.md",
        "docs/PRIVACY_AND_ETHICS.md",
        "docs/REPRODUCTION_AND_DEMO.md",
        "evaluation/results/release/v3_integration_preflight.json",
    )

    package = _read("docs/TCC_DELIVERY_PACKAGE.md")
    for relative_path in required:
        assert (ROOT / relative_path).is_file(), relative_path
        assert f"`{relative_path}`" in package


def test_delivery_package_keeps_institutional_gate_open() -> None:
    package = _read("docs/TCC_DELIVERY_PACKAGE.md")

    assert "gate institucional permanece aberto" in package
    assert "não piloto público" in package
    assert "sem validação clínica independente" in package


def test_manuscript_preserves_results_sources_and_limitations() -> None:
    manuscript = _read("docs/TCC_MANUSCRIPT_DRAFT.md")

    assert "[NOME COMPLETO DO AUTOR]" in manuscript
    assert "[NOME E TITULAÇÃO DO ORIENTADOR]" in manuscript
    for result in ("0,416", "0,846", "0,625", "0,833", "19,35"):
        assert result in manuscript
    assert "sem validação clínica independente" in manuscript
    assert "não autorizam uso clínico ou implantação pública" in manuscript
    assert "https://arxiv.org/abs/2005.11401" in manuscript
    assert "https://aclanthology.org/2024.findings-acl.137/" in manuscript
    for evidence in (
        "evaluation/results/test/FINAL_TEST_REPORT.md",
        "evaluation/refinement_v3/confirmatory/RESULTS.md",
        "evaluation/results/performance/OPERATIONAL_PERFORMANCE_REPORT.md",
    ):
        assert (ROOT / evidence).is_file(), evidence
        assert evidence in manuscript


def test_defense_plan_prevents_overclaiming_and_keeps_demo_bounded() -> None:
    defense = _read("docs/DEFENSE_PLAN.md")
    normalized = " ".join(defense.split())

    assert "somente o autor interage com o bot" in normalized
    assert "não comparar diretamente métricas de conjuntos diferentes" in normalized
    assert "sem validação clínica independente" in normalized
    assert "não teve validação clínica independente" in normalized
