from __future__ import annotations

import re
import statistics
import unicodedata
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence

from immunocheck.domain.models import Verdict
from immunocheck.evaluation.end_to_end import EndToEndDatasetError, EndToEndItem
from immunocheck.evaluation.refinement_experiment import (
    REFINEMENT_CONDITIONS,
    validate_refinement_checkpoint,
)

MATERIAL_MARKERS = frozenset(
    {
        "apenas",
        "causa",
        "causam",
        "causar",
        "entao",
        "jamais",
        "logo",
        "maioria",
        "nao",
        "nenhum",
        "nenhuma",
        "nunca",
        "permanente",
        "portanto",
        "prova",
        "provoca",
        "provocam",
        "sem",
        "sempre",
        "somente",
        "todo",
        "todos",
        "toda",
        "todas",
    }
)
RETRIEVAL_DEPTHS = (6, 10, 20, 60)


def analyze_refinement_phase_a(
    records: Sequence[Mapping[str, object]], items: Sequence[EndToEndItem]
) -> dict[str, object]:
    validate_refinement_checkpoint(records, items)
    if len(records) != len(items):
        raise EndToEndDatasetError("O diagnóstico exige a calibração completa.")
    item_by_id = {item.item_id: item for item in items}
    stages: Counter[str] = Counter()
    stage_items: defaultdict[str, list[str]] = defaultdict(list)
    details = []
    label_totals: Counter[str] = Counter()
    label_abstentions: Counter[str] = Counter()
    conclusive = 0
    retrieval_hits = 0
    selection_hits = 0
    exact_extractions = 0
    low_recall = 0
    marker_losses = 0
    recalls = []

    for record in records:
        item_id = _text(record, "item_id")
        item = item_by_id[item_id]
        expected = item.label
        label_totals[expected.value] += 1
        extraction = _mapping(record, "extraction")
        candidate = _condition(record, REFINEMENT_CONDITIONS[1])
        predicted = Verdict(_text(candidate, "verdict"))
        if predicted is Verdict.INSUFFICIENT_EVIDENCE:
            label_abstentions[expected.value] += 1

        extracted = extraction.get("claim")
        recall, marker_loss = _extraction_integrity(
            item.claim, extracted if isinstance(extracted, str) else None
        )
        recalls.append(recall)
        exact_extractions += extracted == item.claim
        low_recall += recall < 0.8
        marker_losses += marker_loss

        retrieved = _string_set(extraction, "retrieved_source_ids")
        selected = _string_set(candidate, "source_ids")
        annotated = set(item.evidence_chunk_ids)
        retrieval_hit = bool(annotated & retrieved) if annotated else None
        selection_hit = bool(annotated & selected) if annotated else None
        if expected is not Verdict.INSUFFICIENT_EVIDENCE:
            conclusive += 1
            retrieval_hits += bool(retrieval_hit)
            selection_hits += bool(selection_hit)

        technical_error = extraction.get("technical_error") or candidate.get("technical_error")
        stage = _stage(
            expected=expected,
            predicted=predicted,
            technical_error=technical_error,
            extraction_recall=recall,
            marker_loss=marker_loss,
            retrieval_hit=retrieval_hit,
            selection_hit=selection_hit,
        )
        stages[stage] += 1
        stage_items[stage].append(item_id)
        details.append(
            {
                "item_id": item_id,
                "claim_family": item.claim_family,
                "expected_label": expected.value,
                "candidate_label": predicted.value,
                "primary_stage": stage,
                "extraction_exact": extracted == item.claim,
                "extraction_token_recall": recall,
                "material_marker_loss": marker_loss,
                "retrieval_hit_annotated_evidence": retrieval_hit,
                "gate_selected_annotated_evidence": selection_hit,
                "candidate_source_ids": sorted(selected),
                "candidate_explanation": candidate.get("explanation"),
            }
        )

    return {
        "schema_version": 1,
        "scope": "refinement_v2_calibration_phase_a_only",
        "item_count": len(records),
        "condition": REFINEMENT_CONDITIONS[1],
        "primary_stage_counts": dict(sorted(stages.items())),
        "item_ids_by_primary_stage": dict(sorted(stage_items.items())),
        "abstention_by_expected_label": {
            label.value: {
                "abstentions": label_abstentions[label.value],
                "total": label_totals[label.value],
                "rate": label_abstentions[label.value] / label_totals[label.value],
            }
            for label in Verdict
        },
        "extraction": {
            "exact_original": exact_extractions,
            "low_token_recall_below_0_8": low_recall,
            "material_marker_loss": marker_losses,
            "mean_token_recall": statistics.fmean(recalls),
        },
        "retrieval_and_gate_on_conclusive_items": {
            "items": conclusive,
            "retrieval_hit": retrieval_hits,
            "retrieval_hit_rate": retrieval_hits / conclusive,
            "gate_selected_annotated_evidence": selection_hits,
            "gate_selection_hit_rate": selection_hits / conclusive,
        },
        "details": details,
        "interpretation_limits": [
            "Interseção de IDs mede cobertura da evidência anotada, não relevância exaustiva de todos os chunks recuperados.",
            "Atribuição por estágio é diagnóstica e não demonstra causalidade isolada.",
            "O diagnóstico não carrega teste v1 nem holdout v2 e não altera os resultados da fase A.",
        ],
    }


def render_refinement_diagnostics(report: Mapping[str, object]) -> str:
    stages = _mapping(report, "primary_stage_counts")
    abstention = _mapping(report, "abstention_by_expected_label")
    extraction = _mapping(report, "extraction")
    retrieval = _mapping(report, "retrieval_and_gate_on_conclusive_items")
    lines = [
        "# Diagnóstico pós-calibração — fase A",
        "",
        "## Resultado executivo",
        "",
        f"- Itens analisados: {int(report['item_count'])}.",
        f"- Evidência anotada apareceu no top 6 em {int(retrieval['retrieval_hit'])}/{int(retrieval['items'])} itens conclusivos ({float(retrieval['retrieval_hit_rate']):.1%}).",
        f"- O gate preservou evidência anotada em {int(retrieval['gate_selected_annotated_evidence'])}/{int(retrieval['items'])} ({float(retrieval['gate_selection_hit_rate']):.1%}).",
        f"- Extração exata: {int(extraction['exact_original'])}/{int(report['item_count'])}; perdas de marcador material: {int(extraction['material_marker_loss'])}.",
        "",
        "## Atribuição primária exclusiva",
        "",
        "| Estágio | Itens | Proporção |",
        "|---|---:|---:|",
    ]
    for stage, count in stages.items():
        lines.append(f"| `{stage}` | {int(count)} | {int(count) / int(report['item_count']):.1%} |")
    lines.extend(
        [
            "",
            "## Abstenção por classe esperada",
            "",
            "| Classe | Abstenções | Total | Taxa |",
            "|---|---:|---:|---:|",
        ]
    )
    for label, value in abstention.items():
        row = _as_mapping(value)
        lines.append(
            f"| `{label}` | {int(row['abstentions'])} | {int(row['total'])} | {float(row['rate']):.1%} |"
        )
    lines.extend(
        [
            "",
            "## Interpretação",
            "",
            "`retrieval_miss` significa que nenhum ID anotado apareceu no top 6. Quando o",
            "retrieval encontrou a evidência e a candidata se absteve, o diagnóstico separa",
            "seleção incorreta do gate de rejeição apesar de evidência anotada preservada.",
            "Extração tem precedência quando perde conteúdo material; portanto as categorias",
            "somam exatamente 48 sem contar um item duas vezes.",
            "",
            "## Limitações",
            "",
        ]
    )
    for limitation in report["interpretation_limits"]:
        lines.append(f"- {limitation}")
    return "\n".join(lines) + "\n"


def summarize_refinement_retrieval_depth(
    rankings_by_query: Mapping[str, Mapping[str, Sequence[str]]],
    items: Sequence[EndToEndItem],
    *,
    cutoffs: tuple[int, ...] = RETRIEVAL_DEPTHS,
) -> dict[str, object]:
    if not rankings_by_query or not cutoffs or tuple(sorted(set(cutoffs))) != cutoffs:
        raise ValueError("Consultas e profundidades devem ser não vazias e ordenadas.")
    conclusive = tuple(item for item in items if item.label is not Verdict.INSUFFICIENT_EVIDENCE)
    expected_ids = {item.item_id for item in conclusive}
    systems = {}
    for query_name, rankings in rankings_by_query.items():
        if set(rankings) != expected_ids:
            raise EndToEndDatasetError("Rankings não cobrem os itens conclusivos.")
        ranks: dict[str, int | None] = {}
        for item in conclusive:
            ranking = rankings[item.item_id]
            if len(ranking) < cutoffs[-1] or len(ranking) != len(set(ranking)):
                raise EndToEndDatasetError("Ranking incompleto ou duplicado.")
            relevant = set(item.evidence_chunk_ids)
            ranks[item.item_id] = next(
                (index for index, chunk_id in enumerate(ranking, start=1) if chunk_id in relevant),
                None,
            )
        systems[query_name] = {
            "items": len(conclusive),
            "hit_at_k": {
                str(cutoff): {
                    "hits": sum(rank is not None and rank <= cutoff for rank in ranks.values()),
                    "rate": sum(rank is not None and rank <= cutoff for rank in ranks.values())
                    / len(conclusive),
                }
                for cutoff in cutoffs
            },
            "per_class_hit_at_k": {
                label.value: {
                    str(cutoff): sum(
                        ranks[item.item_id] is not None and int(ranks[item.item_id]) <= cutoff
                        for item in conclusive
                        if item.label is label
                    )
                    / sum(item.label is label for item in conclusive)
                    for cutoff in cutoffs
                }
                for label in Verdict
                if label is not Verdict.INSUFFICIENT_EVIDENCE
            },
            "first_relevant_rank": {
                "median_when_found": statistics.median(
                    rank for rank in ranks.values() if rank is not None
                ),
                "missing_at_max_depth": sum(rank is None for rank in ranks.values()),
                "by_item": ranks,
            },
        }
    return {
        "schema_version": 1,
        "scope": "refinement_v2_calibration_conclusive_items_only",
        "cutoffs": list(cutoffs),
        "systems": systems,
        "v1_test_records_loaded": 0,
        "holdout_v2_records_loaded": 0,
    }


def render_refinement_retrieval_depth(report: Mapping[str, object]) -> str:
    systems = _mapping(report, "systems")
    cutoffs = report["cutoffs"]
    lines = [
        "# Diagnóstico de profundidade do retrieval — calibração v2",
        "",
        "A análise usa somente os 36 itens conclusivos da calibração e compara a mesma",
        "busca densa BGE-M3 com a alegação original e com a alegação extraída na fase A.",
        "",
        "## Cobertura de ao menos um chunk anotado",
        "",
        "| Consulta | " + " | ".join(f"Hit@{cutoff}" for cutoff in cutoffs) + " |",
        "|---|" + "---:|" * len(cutoffs),
    ]
    for name, value in systems.items():
        system = _as_mapping(value)
        hit_at_k = _mapping(system, "hit_at_k")
        lines.append(
            f"| `{name}` | "
            + " | ".join(
                f"{float(_as_mapping(hit_at_k[str(cutoff)])['rate']):.1%}" for cutoff in cutoffs
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Limites",
            "",
            "- Hit@k mede interseção com os chunks anotados, não toda evidência potencialmente válida.",
            "- A análise não chama LLM, não altera o índice e não abre teste ou holdout.",
            "- Aumentar top-k só será hipótese aceitável se houver ganho de cobertura mensurável.",
        ]
    )
    return "\n".join(lines) + "\n"


def _stage(
    *,
    expected: Verdict,
    predicted: Verdict,
    technical_error: object,
    extraction_recall: float,
    marker_loss: bool,
    retrieval_hit: bool | None,
    selection_hit: bool | None,
) -> str:
    if technical_error is not None:
        return "technical_failure"
    if extraction_recall < 0.8 or marker_loss:
        return "extraction_integrity_risk"
    if expected is Verdict.INSUFFICIENT_EVIDENCE:
        return (
            "correct_insufficient_evidence"
            if predicted is Verdict.INSUFFICIENT_EVIDENCE
            else "false_conclusion_on_insufficient_evidence"
        )
    if not retrieval_hit:
        return "retrieval_miss"
    if predicted is Verdict.INSUFFICIENT_EVIDENCE:
        return (
            "sufficiency_rejection_with_annotated_evidence"
            if selection_hit
            else "sufficiency_selection_miss"
        )
    if predicted is expected:
        return "correct_conclusive"
    return "classification_error_after_sufficient_gate"


def _extraction_integrity(original: str, extracted: str | None) -> tuple[float, bool]:
    original_tokens = _tokens(original)
    extracted_tokens = _tokens(extracted or "")
    if not original_tokens:
        return 1.0, False
    recall = len(set(original_tokens) & set(extracted_tokens)) / len(set(original_tokens))
    original_markers = set(original_tokens) & MATERIAL_MARKERS
    extracted_markers = set(extracted_tokens) & MATERIAL_MARKERS
    return recall, bool(original_markers - extracted_markers)


def _tokens(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKD", text.casefold())
    ascii_text = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    return re.findall(r"[a-z0-9]+", ascii_text)


def _condition(record: Mapping[str, object], name: str) -> Mapping[str, object]:
    conditions = _mapping(record, "conditions")
    value = conditions.get(name)
    if not isinstance(value, Mapping):
        raise EndToEndDatasetError(f"Condição ausente no diagnóstico: {name}.")
    return value


def _string_set(record: Mapping[str, object], field: str) -> set[str]:
    value = record.get(field)
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise EndToEndDatasetError(f"Lista inválida no diagnóstico: {field}.")
    return set(value)


def _text(record: Mapping[str, object], field: str) -> str:
    value = record.get(field)
    if not isinstance(value, str) or not value:
        raise EndToEndDatasetError(f"Texto ausente no diagnóstico: {field}.")
    return value


def _mapping(record: Mapping[str, object], field: str) -> Mapping[str, object]:
    value = record.get(field)
    if not isinstance(value, Mapping):
        raise EndToEndDatasetError(f"Mapa ausente no diagnóstico: {field}.")
    return value


def _as_mapping(value: object) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise EndToEndDatasetError("Linha tabular inválida no diagnóstico.")
    return value
