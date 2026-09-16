from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest

from immunocheck.domain.models import Verdict
from immunocheck.evaluation.annotation_agreement import (
    compute_annotation_agreement,
    load_annotation_responses,
)
from immunocheck.evaluation.end_to_end import EndToEndDatasetError, load_end_to_end_items

ROOT = Path(__file__).parents[1] / "evaluation/end_to_end"


def expected_tasks():
    by_id = {item.item_id: item for item in load_end_to_end_items(ROOT / "review_pool.jsonl")}
    manifest = json.loads((ROOT / "independent_review/selection_manifest.json").read_text("utf-8"))
    return {entry["task_id"]: by_id[entry["item_id"]] for entry in manifest["mapping"]}


@pytest.mark.parametrize("round_id,agreements,kappa", [(1, 31, 19 / 36), (2, 32, 5 / 9)])
def test_received_rounds_preserve_complete_pairs_before_adjudication(round_id, agreements, kappa):
    expected = expected_tasks()
    path = ROOT / f"independent_review/returns/round_{round_id:03d}.jsonl"
    responses = load_annotation_responses(path, expected_tasks=expected)
    result = compute_annotation_agreement(
        {task: item.primary_label for task, item in expected.items()}, responses
    )
    assert result["total"] == 48 and result["agreement_count"] == agreements
    assert result["cohens_kappa"] == pytest.approx(kappa)
    assert result["expected_agreement"] == 0.25
    assert result["adjudication_applied"] is False
    assert all(response.reviewer == "usr_002-independente" for response in responses)
    assert all(response.reviewed_at == "2026-09-15" for response in responses)
    assert all(item.second_label is None and item.adjudicator is None for item in expected.values())


def test_round_changes_are_preserved_and_not_counted_as_new_independent_humans():
    expected = expected_tasks()
    first = load_annotation_responses(
        ROOT / "independent_review/returns/round_001.jsonl", expected_tasks=expected
    )
    revised = load_annotation_responses(
        ROOT / "independent_review/returns/round_002.jsonl", expected_tasks=expected
    )
    assert len({response.reviewer for response in (*first, *revised)}) == 1
    assert [
        a.task_id
        for a, b in zip(first, revised, strict=True)
        if a.second_label is not b.second_label
    ] == ["annotation-004", "annotation-012", "annotation-022", "annotation-023", "annotation-043"]


@pytest.mark.parametrize(
    "problem",
    [
        "missing",
        "duplicate",
        "claim",
        "mapping",
        "date",
        "personal",
        "empty",
        "extra",
        "round",
        "reviewer",
        "same_primary",
    ],
)
def test_raw_return_loader_rejects_incomplete_or_incompatible_data(tmp_path, problem):
    expected = expected_tasks()
    values = [
        json.loads(line)
        for line in (ROOT / "independent_review/returns/round_002.jsonl")
        .read_text("utf-8")
        .splitlines()
    ]
    if problem == "missing":
        values.pop()
    elif problem == "duplicate":
        values.append(values[0])
    elif problem == "claim":
        values[0]["claim"] = "Outra alegação."
    elif problem == "mapping":
        values[0]["item_id"] = "e2e-9999"
    elif problem == "date":
        values[0]["reviewed_at"] = "15/09/2026"
    elif problem == "personal":
        values[0]["reviewer"] = "Nome Completo da Pessoa"
    elif problem == "empty":
        values[0]["rationale"] = ""
    elif problem == "extra":
        values[0]["email"] = "not-for-publication@example.org"
    elif problem == "round":
        values[0]["round_id"] = "another_round"
    elif problem == "reviewer":
        values[0]["reviewer"] = "another_reviewer"
    else:
        values[0]["reviewer"] = "project_author"
    path = tmp_path / "responses.jsonl"
    path.write_text("".join(json.dumps(value) + "\n" for value in values), encoding="utf-8")
    with pytest.raises(EndToEndDatasetError):
        load_annotation_responses(path, expected_tasks=expected)


def test_kappa_handles_perfect_agreement_and_degenerate_marginals():
    expected = expected_tasks()
    responses = load_annotation_responses(
        ROOT / "independent_review/returns/round_002.jsonl", expected_tasks=expected
    )
    primary = {response.task_id: expected[response.task_id].primary_label for response in responses}
    perfect = tuple(
        replace(response, second_label=primary[response.task_id]) for response in responses
    )
    assert compute_annotation_agreement(primary, perfect)["cohens_kappa"] == 1.0
    one_class = {response.task_id: Verdict.SUPPORTED for response in responses}
    degenerate = tuple(replace(response, second_label=Verdict.SUPPORTED) for response in responses)
    result = compute_annotation_agreement(one_class, degenerate)
    assert result["observed_agreement"] == 1.0 and result["cohens_kappa"] is None


def test_agreement_rejects_missing_or_duplicated_pairs():
    expected = expected_tasks()
    responses = load_annotation_responses(
        ROOT / "independent_review/returns/round_002.jsonl", expected_tasks=expected
    )
    primary = {task: item.primary_label for task, item in expected.items()}
    for incomplete in ((), responses[:-1], (*responses, responses[0])):
        with pytest.raises(EndToEndDatasetError):
            compute_annotation_agreement(primary, incomplete)


def test_published_receipt_reports_and_package_match_the_original_pairs():
    expected = expected_tasks()
    base = ROOT / "independent_review"
    receipt = json.loads((base / "review_receipt.json").read_text("utf-8"))
    assert receipt["test_frozen"] is receipt["adjudication_completed"] is False
    assert receipt["phase5_complete"] is False and receipt["second_reviews_applied_to_items"] == 0
    assert receipt["returned_per_round"] == 48 and receipt["selected_fraction"] == 0.30
    primary = {task: item.primary_label for task, item in expected.items()}
    for number in (1, 2):
        responses = load_annotation_responses(
            base / f"returns/round_{number:03d}.jsonl", expected_tasks=expected
        )
        published = json.loads(
            (base / f"returns/agreement_round_{number:03d}.json").read_text("utf-8")
        )
        calculated = compute_annotation_agreement(primary, responses)
        calculated["round_id"] = responses[0].round_id
        assert published == calculated
    for record in receipt["files"]:
        normalized = (base / record["path"]).read_bytes().replace(b"\r\n", b"\n")
        assert hashlib.sha256(normalized).hexdigest() == record["sha256"]
    text = (base / "adjudication/TASKS.md").read_text("utf-8")
    assert len(receipt["adjudication_task_ids"]) == 22
    assert text.count("- Rótulo final proposto (ou PENDENTE):\n") == 22
    assert text.count("- Identificador interno do responsável:\n") == 22
    assert text.count("- Data:\n") == 22
    assert all(f"## {task_id} —" in text for task_id in receipt["adjudication_task_ids"])
