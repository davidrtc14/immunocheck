from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import replace
from pathlib import Path

from immunocheck.evaluation.end_to_end import (
    DatasetStatus,
    load_end_to_end_items,
    serialize_end_to_end_items,
)
from immunocheck.evaluation.refinement_calibration import (
    REFINEMENT_SECOND_ANNOTATION_SEED,
    load_family_ids,
    select_refinement_second_annotation_items,
    validate_refinement_calibration,
)

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "evaluation" / "refinement_v2" / "calibration"
CANDIDATES = BASE / "candidates.jsonl"
REVIEW_TEMPLATE = BASE / "PRIMARY_REVIEW.md"
REVIEW_RETURN = BASE / "reviews" / "PRIMARY_REVIEW_2026-09-22.md"
REVIEWED = BASE / "reviewed_items.jsonl"
RECEIPT = BASE / "reviews" / "primary_review_receipt.json"
MANIFEST = BASE / "manifest.json"
SECOND_REVIEW = BASE / "independent_review"
FROZEN_FAMILIES = ROOT / "evaluation" / "refinement_v2" / "FROZEN_TEST_FAMILIES.txt"
CORPUS = ROOT / "corpus" / "processed" / "chunks.jsonl"

REVIEWER_CODE = "primary_reviewer_001"
REVIEWER_ROLE = "Professor Orientador"
REVIEW_DATE = "2026-09-22"
ALL_CALIBRATION_FAMILIES = frozenset(
    {
        "dengue_postmarketing_signal",
        "mpox_notification_severity",
        "measles_first_dose_age_response",
        "hpv_single_dose_scope",
        "meningococcal_conjugate_impact",
        "adult_pneumococcal_vaccine_type_outcomes",
        "enhanced_influenza_evidence_certainty",
        "vaccination_autoimmune_pooled_association",
        "covid_pregnancy_evidence_certainty",
        "vaccine_misinformation_scare_tactics",
        "adjuvant_mechanism_delivery",
        "acellular_pertussis_waning",
    }
)


def _normalized_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _verify_return() -> str:
    template = _normalized_text(REVIEW_TEMPLATE)
    returned = _normalized_text(REVIEW_RETURN)
    marker = "## Declaração de decisão"
    if template.split(marker, 1)[0] != returned.split(marker, 1)[0]:
        raise RuntimeError("O retorno alterou conteúdo anterior à declaração de decisão.")
    required = (
        "- [x] Examinei as 12 fontes e as 48 propostas.",
        "Revisor: Professor Orientador",
        "Data: 2026-09-22",
        "itens ref2-cal-0001 a ref2-cal-0048",
        "sem exceções",
        "as 12 fontes foram consultadas diretamente",
        "divergência entre proposta e fonte",
    )
    if any(value not in returned for value in required) or returned.count("- [x]") != 4:
        raise RuntimeError("A declaração de decisão não corresponde ao aceite esperado.")
    return returned


def _reviewed_snapshot() -> tuple[str, tuple]:
    candidates = load_end_to_end_items(CANDIDATES)
    reviewed = tuple(
        replace(
            item,
            status=DatasetStatus.REVIEWED,
            primary_label=item.label,
            rationale=(item.notes or "").removeprefix("Proposta: "),
            reviewer=REVIEWER_CODE,
            reviewed_at=REVIEW_DATE,
        )
        for item in candidates
    )
    families = load_family_ids(FROZEN_FAMILIES.read_text(encoding="utf-8").splitlines())
    validate_refinement_calibration(
        reviewed,
        frozen_test_families=families,
        expected_status=DatasetStatus.REVIEWED,
    )
    text = serialize_end_to_end_items(reviewed)
    return text, reviewed


def _source_catalog(items: tuple) -> dict[str, tuple[str, str]]:
    document_ids = {item.origin_reference for item in items if item.origin_reference}
    catalog: dict[str, tuple[str, str]] = {}
    for line in CORPUS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        chunk = json.loads(line)
        document_id = chunk["document_id"]
        if document_id in document_ids:
            catalog[document_id] = (chunk["document_title"], chunk["url"])
    if set(catalog) != document_ids:
        raise RuntimeError("O catálogo não contém todas as fontes da calibração.")
    return catalog


def _render_second_review(reviewed: tuple, reviewed_text: str) -> dict[str, str]:
    selected = select_refinement_second_annotation_items(
        reviewed,
        target_families=ALL_CALIBRATION_FAMILIES,
    )
    tasks = [
        {
            "task_id": f"ref2-annotation-{index:03d}",
            "claim": item.claim,
            "second_label": None,
            "rationale": None,
            "source_urls": [],
            "reviewer_id": None,
            "reviewed_at": None,
        }
        for index, item in enumerate(selected, 1)
    ]
    readme = """# Segunda anotação cega — calibração v2

Esta pasta contém 16 alegações (33,3% da calibração). O participante não recebe
rótulos, justificativas, evidências pré-associadas nem saídas do ImmunoCheck. A
seleção cobre as 12 famílias da calibração para produzir uma verificação realmente
independente da primeira revisão assistida.

O segundo anotador deve ser uma pessoa distinta do primeiro. Não consulte o
repositório, a revisão primária ou respostas do sistema durante a tarefa. Use o
catálogo completo e não ranqueado de `SOURCES.md`, leia o contexto pertinente e
registre julgamento próprio. Não use LLM para substituir esse julgamento.

## Procedimento

1. Classifique cada alegação como `SUPPORTED`, `REFUTED`, `MISLEADING` ou
   `INSUFFICIENT_EVIDENCE`.
2. Registre uma justificativa e as URLs/partes consultadas. Para insuficiência,
   descreva o que falta e a busca realizada.
3. Não tente reproduzir uma distribuição de classes. Divergências são legítimas.
4. Marque as três declarações no início de `ANNOTATIONS.md`, use um código interno
   sem nome, e-mail ou outro dado pessoal e registre a data.
5. Preencha e devolva `ANNOTATIONS.md`. Os campos vazios ou uma declaração não
   marcada impedem que o arquivo conte como segunda anotação humana.

`MISLEADING` exige uma parte factual relevante, mas com contexto, alcance ou
inferência materialmente distorcidos. Ausência de menção não equivale a refutação.
O material é sintético e serve a avaliação acadêmica, não aconselhamento médico.
"""
    annotations = "# Formulário de segunda anotação cega\n\n"
    annotations += "## Declaração do segundo revisor\n\n"
    annotations += (
        "- [ ] Sou uma pessoa e realizei esta anotação por julgamento próprio.\n"
        "- [ ] Sou diferente do primeiro revisor e não consultei seus rótulos.\n"
        "- [ ] Não usei LLM ou outro sistema automático para substituir meu julgamento.\n"
        "- Código interno do revisor:\n"
        "- Data da revisão:\n\n"
    )
    for task in tasks:
        annotations += (
            f"## {task['task_id']}\n\n{task['claim']}\n\n"
            "- Rótulo:\n- Justificativa:\n- Fontes e trechos/páginas consultados:\n"
            "- Dúvidas ou ambiguidade:\n\n"
        )
    catalog = "# Catálogo completo e não ranqueado\n\n"
    catalog += "As fontes não estão associadas a tarefas específicas.\n\n"
    for document_id, (title, url) in sorted(_source_catalog(reviewed).items()):
        safe_title = title.replace("[", "(").replace("]", ")")
        catalog += f"- `{document_id}` — [{safe_title}]({url})\n"
    mapping = [
        {
            "task_id": task["task_id"],
            "item_id": item.item_id,
            "primary_label": item.primary_label.value if item.primary_label else None,
            "claim_family": item.claim_family,
        }
        for task, item in zip(tasks, selected, strict=True)
    ]
    selection_manifest = {
        "schema_version": 1,
        "purpose": "refinement_v2_blind_second_annotation",
        "prepared_at": REVIEW_DATE,
        "annotation_completed": False,
        "test_frozen": False,
        "algorithm": "target families; 16 items; 4 per class; deterministic shuffle",
        "seed": REFINEMENT_SECOND_ANNOTATION_SEED,
        "reviewed_dataset_sha256": _sha256_text(reviewed_text),
        "total_dataset": len(reviewed),
        "selected": len(selected),
        "selected_class_counts": dict(
            sorted(Counter(item.primary_label.value for item in selected).items())
        ),
        "target_family_count": len(ALL_CALIBRATION_FAMILIES),
        "selected_family_count": len({item.claim_family for item in selected}),
        "share_with_participant": "participant/ only",
        "mapping": mapping,
    }
    return {
        "participant/README.md": readme,
        "participant/ANNOTATIONS.md": annotations,
        "participant/SOURCES.md": catalog,
        "selection_manifest.json": json.dumps(
            selection_manifest, ensure_ascii=False, indent=2
        )
        + "\n",
    }


def main() -> int:
    returned = _verify_return()
    reviewed_text, reviewed = _reviewed_snapshot()
    _write_text(REVIEWED, reviewed_text)
    package = _render_second_review(reviewed, reviewed_text)
    for relative_path, content in package.items():
        _write_text(SECOND_REVIEW / relative_path, content)

    review_sha256 = _sha256_text(returned)
    reviewed_sha256 = _sha256_text(reviewed_text)
    receipt = {
        "schema_version": 1,
        "recorded_at": REVIEW_DATE,
        "review_type": "assisted_primary_review",
        "declared_reviewer_role": REVIEWER_ROLE,
        "reviewer_code_in_dataset": REVIEWER_CODE,
        "identity_independently_verified_by_software": False,
        "decision": "approved_all_without_exceptions",
        "reviewed_item_count": len(reviewed),
        "returned_review_normalized_sha256": review_sha256,
        "reviewed_dataset_sha256": reviewed_sha256,
        "declared_direct_source_verification_families": sorted(
            ALL_CALIBRATION_FAMILIES
        ),
        "structural_coherence_only_families": [],
        "limitation": (
            "A consulta às 12 fontes e o papel do revisor são declarações documentais; "
            "o software não certifica a identidade nem a leitura realizada."
        ),
        "technical_reconciliation": [
            "Família 10: 'adesão' é interpretada como crença ou endosso da desinformação, não como cobertura vacinal.",
            "Família 12: a fonte é um artigo com revisão sistemática e modelagem.",
            "A correspondência direta às fontes refere-se aos 36 rótulos conclusivos; os 12 itens insuficientes decorrem da falta de contexto individual para causalidade.",
        ],
        "next_gate": "blind_second_annotation_of_16_items",
    }
    _write_text(RECEIPT, json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["status"] = "primary_review_complete_second_review_pending"
    manifest["reviewed_dataset_sha256"] = reviewed_sha256
    manifest["primary_review"] = {
        "reviewed_at": REVIEW_DATE,
        "reviewer_code": REVIEWER_CODE,
        "declared_role": REVIEWER_ROLE,
        "decision": "approved_all_without_exceptions",
        "item_count": len(reviewed),
        "return_normalized_sha256": review_sha256,
        "declared_direct_source_verification_family_count": len(
            ALL_CALIBRATION_FAMILIES
        ),
        "structural_only_family_count": 0,
    }
    previous_second_review = manifest.get("second_review", {})
    attempts = previous_second_review.get("attempts", [])
    manifest["second_review"] = {
        "status": (
            "package_regenerated_pending_distinct_human_annotation"
            if attempts
            else "package_prepared_pending_human_annotation"
        ),
        "selected_items": len(json.loads(package["selection_manifest.json"])["mapping"]),
        "selected_class_counts": json.loads(package["selection_manifest.json"])[
            "selected_class_counts"
        ],
        "selected_family_count": json.loads(package["selection_manifest.json"])[
            "selected_family_count"
        ],
    }
    if attempts:
        manifest["second_review"]["attempts"] = attempts
    manifest["limitations"] = [
        "A identidade declarada do revisor não é certificada pelo software.",
        "A consulta direta às 12 fontes e o papel do revisor são declarações documentais, não certificações do software.",
        "A segunda anotação cega foi preparada, mas ainda não foi realizada.",
        "A matriz sintética por família pode criar atalhos de redação.",
        "O pacote de holdout v2 ainda não existe por desenho.",
    ]
    _write_text(MANIFEST, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

    print(f"Revisão primária incorporada: {len(reviewed)} itens.")
    print("Segunda anotação cega preparada: 16 itens, 4 por classe.")
    print("Famílias cobertas pela seleção cega: 12 de 12.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
