from __future__ import annotations

import re
import statistics
import unicodedata
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence

from immunocheck.domain.models import Verdict
from immunocheck.evaluation.development_end_to_end import validate_checkpoint_prefix
from immunocheck.evaluation.end_to_end import EndToEndDatasetError, EndToEndItem

MATERIAL_MARKERS = frozenset(
    {
        "apenas",
        "causa",
        "causam",
        "causar",
        "entao",
        "jamais",
        "logo",
        "nao",
        "nenhum",
        "nenhuma",
        "nunca",
        "portanto",
        "provoca",
        "provocam",
        "provocar",
        "sem",
        "sempre",
        "somente",
        "todo",
        "todos",
        "toda",
        "todas",
    }
)


def analyze_development_error_attribution(
    records: Sequence[Mapping[str, object]],
    items: Sequence[EndToEndItem],
    *,
    condition: str = "dense_with_auditor",
    draft_condition: str = "dense_no_auditor",
) -> dict[str, object]:
    """Atribui falhas observáveis sem usar nem carregar a partição de teste."""
    validate_checkpoint_prefix(records, items)
    if len(records) != len(items):
        raise EndToEndDatasetError("A auditoria exige todos os itens de desenvolvimento.")

    item_by_id = {item.item_id: item for item in items}
    stage_counts: Counter[str] = Counter()
    stage_items: defaultdict[str, list[str]] = defaultdict(list)
    label_totals: Counter[str] = Counter()
    label_errors: Counter[str] = Counter()
    audit_transitions: Counter[str] = Counter()
    evidence_rows: list[tuple[bool, bool]] = []
    extraction_recalls: list[float] = []
    extraction_exact = 0
    extraction_low_recall = 0
    extraction_marker_loss = 0
    latencies: list[float] = []
    correct = 0

    for record in records:
        item_id = _required_text(record, "item_id")
        item = item_by_id[item_id]
        expected = item.label.value
        label_totals[expected] += 1

        final = _condition(record, condition)
        draft = _condition(record, draft_condition)
        final_verdict = _required_text(final, "verdict")
        draft_verdict = _required_text(draft, "verdict")
        Verdict(final_verdict)
        Verdict(draft_verdict)
        latencies.append(_required_float(final, "latency_ms"))

        extraction = record.get("extraction")
        if not isinstance(extraction, Mapping):
            raise EndToEndDatasetError("Registro de extração ausente na auditoria.")
        extracted_claim = extraction.get("claim")
        extraction_error = extraction.get("technical_error")
        token_recall, marker_loss = _extraction_integrity(
            item.claim, extracted_claim if isinstance(extracted_claim, str) else None
        )
        extraction_recalls.append(token_recall)
        extraction_exact += extracted_claim == item.claim
        extraction_low_recall += token_recall < 0.8
        extraction_marker_loss += marker_loss

        final_error = final.get("technical_error")
        is_correct = final_verdict == expected
        if is_correct:
            correct += 1
        else:
            label_errors[expected] += 1

        draft_correct = draft_verdict == expected
        if draft_verdict == final_verdict:
            transition = "unchanged_correct" if is_correct else "unchanged_wrong"
        elif draft_correct and not is_correct:
            transition = "auditor_regression"
        elif not draft_correct and is_correct:
            transition = "auditor_recovery"
        else:
            transition = "changed_still_wrong"
        audit_transitions[transition] += 1

        evidence_hit = _evidence_hit(item, final)
        if item.label is not Verdict.INSUFFICIENT_EVIDENCE:
            evidence_rows.append((bool(evidence_hit), is_correct))

        stage = _primary_stage(
            item=item,
            final_verdict=final_verdict,
            is_correct=is_correct,
            draft_correct=draft_correct,
            extraction_error=extraction_error,
            final_error=final_error,
            token_recall=token_recall,
            marker_loss=marker_loss,
            evidence_hit=evidence_hit,
        )
        stage_counts[stage] += 1
        stage_items[stage].append(item_id)

    total = len(records)
    evidence_hits = [correct_flag for hit, correct_flag in evidence_rows if hit]
    evidence_misses = [correct_flag for hit, correct_flag in evidence_rows if not hit]
    return {
        "schema_version": 1,
        "scope": "development_outputs_only_no_test_predictions_loaded",
        "condition": condition,
        "draft_condition": draft_condition,
        "item_count": total,
        "accuracy": correct / total,
        "error_count": total - correct,
        "primary_stage_counts": dict(sorted(stage_counts.items())),
        "primary_stage_rates": {
            stage: count / total for stage, count in sorted(stage_counts.items())
        },
        "item_ids_by_primary_stage": dict(sorted(stage_items.items())),
        "errors_by_expected_label": {
            label: {
                "errors": label_errors[label],
                "total": label_totals[label],
                "error_rate": label_errors[label] / label_totals[label],
            }
            for label in sorted(label_totals)
        },
        "extraction": {
            "exact_original": extraction_exact,
            "low_token_recall_below_0_8": extraction_low_recall,
            "material_marker_loss": extraction_marker_loss,
            "mean_token_recall": statistics.fmean(extraction_recalls),
        },
        "evidence_grounding_on_conclusive_items": {
            "items": len(evidence_rows),
            "citation_hit": len(evidence_hits),
            "citation_miss": len(evidence_misses),
            "accuracy_when_hit": _safe_mean(evidence_hits),
            "accuracy_when_miss": _safe_mean(evidence_misses),
        },
        "auditor_transitions": dict(sorted(audit_transitions.items())),
        "latency_ms": _latency_summary(latencies),
        "interpretation_limits": [
            "Citação sem interseção com a evidência anotada não distingue falha de retrieval de falha de seleção ou citação do gerador.",
            "A atribuição é diagnóstica e usa somente a iteração v2 do desenvolvimento já encerrado.",
            "Nenhum resultado desta auditoria autoriza ajuste adicional nos 96 itens antigos ou reabertura do teste congelado.",
        ],
    }


def render_error_attribution_markdown(report: Mapping[str, object]) -> str:
    stages = _required_mapping(report, "primary_stage_counts")
    labels = _required_mapping(report, "errors_by_expected_label")
    extraction = _required_mapping(report, "extraction")
    evidence = _required_mapping(report, "evidence_grounding_on_conclusive_items")
    transitions = _required_mapping(report, "auditor_transitions")
    latency = _required_mapping(report, "latency_ms")
    lines = [
        "# Auditoria de erros no desenvolvimento v2",
        "",
        "## Escopo e integridade metodológica",
        "",
        "Esta auditoria usa exclusivamente os 96 itens de desenvolvimento e as saídas já",
        "registradas da iteração v2. As previsões e métricas do teste não são carregadas nem",
        "usadas para escolher alterações. O resultado identifica gargalos observáveis e prepara uma nova",
        "linha experimental com dados independentes.",
        "",
        "## Resultado executivo",
        "",
        f"- Condição analisada: `{report['condition']}`.",
        f"- Acurácia: {float(report['accuracy']):.3f} ({int(report['item_count']) - int(report['error_count'])}/{int(report['item_count'])}).",
        f"- Erros: {int(report['error_count'])}.",
        f"- Latência mediana: {float(latency['median']):.0f} ms; P95: {float(latency['p95']):.0f} ms.",
        "",
        "## Atribuição primária",
        "",
        "Cada item recebe uma única categoria diagnóstica. `extraction_integrity_risk`",
        "pode incluir uma decisão final correta, mas cuja alegação extraída perdeu conteúdo",
        "relevante; por isso, a soma das demais categorias não equivale necessariamente ao",
        "total de erros de classificação.",
        "",
        "| Categoria | Itens | Proporção |",
        "|---|---:|---:|",
    ]
    for stage, count in stages.items():
        lines.append(
            f"| `{stage}` | {int(count)} | {int(count) / int(report['item_count']):.1%} |"
        )
    lines.extend(
        [
            "",
            "## Erros por classe de referência",
            "",
            "| Classe | Erros | Total | Taxa de erro |",
            "|---|---:|---:|---:|",
        ]
    )
    for label, values in labels.items():
        typed = _as_mapping(values)
        lines.append(
            f"| `{label}` | {int(typed['errors'])} | {int(typed['total'])} | {float(typed['error_rate']):.1%} |"
        )
    lines.extend(
        [
            "",
            "## Evidência e decisão",
            "",
            f"- Itens conclusivos: {int(evidence['items'])}.",
            f"- Citação com interseção na evidência anotada: {int(evidence['citation_hit'])}.",
            f"- Acurácia quando há interseção: {_format_optional_rate(evidence['accuracy_when_hit'])}.",
            f"- Acurácia quando não há interseção: {_format_optional_rate(evidence['accuracy_when_miss'])}.",
            "",
            "## Extração",
            "",
            f"- Extração idêntica à alegação original: {int(extraction['exact_original'])}.",
            f"- Recall lexical abaixo de 0,8: {int(extraction['low_token_recall_below_0_8'])}.",
            f"- Perda de marcador material: {int(extraction['material_marker_loss'])}.",
            f"- Recall lexical médio: {float(extraction['mean_token_recall']):.3f}.",
            "",
            "## Efeito do auditor",
            "",
        ]
    )
    for transition, count in transitions.items():
        lines.append(f"- `{transition}`: {int(count)}.")
    lines.extend(
        [
            "",
            "## Decisão para a próxima iteração",
            "",
            "A iteração seguinte não será calibrada nos 96 itens antigos. Será criado um novo",
            "conjunto de calibração com famílias inéditas, acompanhado de um holdout independente.",
            "A primeira hipótese a testar é separar suficiência da evidência, classificação do",
            "conteúdo e fidelidade da explicação, evitando que o auditor transforme discordância de",
            "rótulo em abstenção automática.",
            "",
            "## Limitações",
            "",
        ]
    )
    for limitation in report["interpretation_limits"]:
        lines.append(f"- {limitation}")
    return "\n".join(lines) + "\n"


def _primary_stage(
    *,
    item: EndToEndItem,
    final_verdict: str,
    is_correct: bool,
    draft_correct: bool,
    extraction_error: object,
    final_error: object,
    token_recall: float,
    marker_loss: bool,
    evidence_hit: bool | None,
) -> str:
    if extraction_error is not None or final_error is not None:
        return "technical_failure"
    if token_recall < 0.8 or marker_loss:
        return "extraction_integrity_risk"
    if is_correct:
        return "correct"
    if draft_correct:
        return "auditor_regression"
    if item.label is Verdict.INSUFFICIENT_EVIDENCE:
        return "false_conclusion_on_insufficient_evidence"
    if final_verdict == Verdict.INSUFFICIENT_EVIDENCE.value:
        return "over_abstention_with_evidence" if evidence_hit else "over_abstention_without_evidence"
    if evidence_hit:
        return "classification_error_with_relevant_evidence"
    return "evidence_grounding_miss"


def _evidence_hit(item: EndToEndItem, record: Mapping[str, object]) -> bool | None:
    if item.label is Verdict.INSUFFICIENT_EVIDENCE:
        return None
    source_ids = record.get("source_ids")
    if not isinstance(source_ids, list) or any(not isinstance(value, str) for value in source_ids):
        raise EndToEndDatasetError("Citações inválidas na auditoria de erros.")
    return bool(set(item.evidence_chunk_ids) & set(source_ids))


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
    ascii_text = "".join(character for character in normalized if not unicodedata.combining(character))
    return re.findall(r"[a-z0-9]+", ascii_text)


def _condition(record: Mapping[str, object], name: str) -> Mapping[str, object]:
    conditions = record.get("conditions")
    if not isinstance(conditions, Mapping):
        raise EndToEndDatasetError("Registro sem condições na auditoria.")
    condition = conditions.get(name)
    if not isinstance(condition, Mapping):
        raise EndToEndDatasetError(f"Condição ausente na auditoria: {name}.")
    return condition


def _latency_summary(values: Sequence[float]) -> dict[str, float | int]:
    ordered = sorted(values)
    p95_index = max(0, min(len(ordered) - 1, int(0.95 * len(ordered) + 0.999999) - 1))
    return {
        "median": statistics.median(ordered),
        "p95": ordered[p95_index],
        "samples": len(ordered),
    }


def _safe_mean(values: Sequence[bool]) -> float | None:
    return statistics.fmean(values) if values else None


def _format_optional_rate(value: object) -> str:
    return "não aplicável" if value is None else f"{float(value):.1%}"


def _required_text(record: Mapping[str, object], field: str) -> str:
    value = record.get(field)
    if not isinstance(value, str) or not value:
        raise EndToEndDatasetError(f"Campo textual ausente na auditoria: {field}.")
    return value


def _required_float(record: Mapping[str, object], field: str) -> float:
    value = record.get(field)
    if not isinstance(value, int | float):
        raise EndToEndDatasetError(f"Campo numérico ausente na auditoria: {field}.")
    return float(value)


def _required_mapping(record: Mapping[str, object], field: str) -> Mapping[str, object]:
    value = record.get(field)
    if not isinstance(value, Mapping):
        raise EndToEndDatasetError(f"Mapa ausente na auditoria: {field}.")
    return value


def _as_mapping(value: object) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise EndToEndDatasetError("Valor tabular inválido na auditoria.")
    return value
