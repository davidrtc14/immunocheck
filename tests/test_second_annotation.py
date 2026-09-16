from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import replace
from pathlib import Path

import pytest

from immunocheck.domain.models import Verdict
from immunocheck.evaluation.end_to_end import (
    DatasetStatus,
    EndToEndDatasetError,
    load_end_to_end_items,
)
from immunocheck.evaluation.second_annotation import (
    render_second_annotation_package,
    select_second_annotation_items,
)

ROOT = Path(__file__).parents[1] / "evaluation/end_to_end"


def test_selection_is_reproducible_stratified_and_order_independent() -> None:
    items = load_end_to_end_items(ROOT / "review_pool.jsonl", require_reviewed=True)
    selected = select_second_annotation_items(items)
    assert selected == select_second_annotation_items(tuple(reversed(items)))
    assert len(selected) == len({item.item_id for item in selected}) == 48
    assert Counter(item.primary_label for item in selected) == {label: 12 for label in Verdict}
    assert Counter((item.primary_label.value, item.split.value) for item in selected) == {
        (label.value, split): count
        for label in Verdict
        for split, count in (("development", 7), ("test", 5))
    }
    assert selected != select_second_annotation_items(items, seed=123)
    assert all(item.second_reviewer is None for item in selected)


@pytest.mark.parametrize("problem", ["small", "draft", "primary", "duplicate", "second", "strata"])
def test_selection_rejects_invalid_or_previously_second_reviewed_input(problem: str) -> None:
    items = load_end_to_end_items(ROOT / "review_pool.jsonl")
    if problem == "small":
        items = items[:12]
    elif problem == "draft":
        items = (replace(items[0], status=DatasetStatus.DRAFT), *items[1:])
    elif problem == "primary":
        items = (replace(items[0], primary_label=None), *items[1:])
    elif problem == "duplicate":
        items = (*items, items[0])
    elif problem == "second":
        items = (replace(items[0], second_reviewer="another_human"), *items[1:])
    else:
        items = tuple(replace(item, primary_label=Verdict.SUPPORTED) for item in items)
    with pytest.raises(EndToEndDatasetError):
        select_second_annotation_items(items)


def test_rendered_participant_tasks_hide_labels_mapping_evidence_and_splits() -> None:
    items = load_end_to_end_items(ROOT / "review_pool.jsonl")
    package = render_second_annotation_package(
        items,
        dataset_text=(ROOT / "review_pool.jsonl").read_text(encoding="utf-8"),
        corpus_version="test-snapshot",
        source_catalog={"source-a": ("Example document", "https://example.org/document")},
    )
    tasks = [json.loads(line) for line in package["participant/tasks.jsonl"].splitlines()]
    assert len(tasks) == 48
    for task in tasks:
        assert set(task) == {
            "task_id",
            "claim",
            "second_label",
            "rationale",
            "source_urls",
            "reviewer_id",
            "reviewed_at",
        }
        assert task["second_label"] is task["rationale"] is task["reviewer_id"] is None
        assert task["reviewed_at"] is None and task["source_urls"] == []
    for name, content in package.items():
        if name.startswith("participant/"):
            assert "e2e-" not in content
            assert "primary_label" not in content
            assert "evidence_chunk_ids" not in content
    assert "https://example.org/document" in package["participant/SOURCES.md"]
    assert "não prova cegamento" in package["participant/README.md"]


def test_published_package_matches_selection_and_unannotated_snapshot() -> None:
    items = load_end_to_end_items(ROOT / "review_pool.jsonl")
    base = ROOT / "independent_review"
    manifest = json.loads((base / "selection_manifest.json").read_text(encoding="utf-8"))
    assert manifest["selected"] == 48 and manifest["total_dataset"] == 160
    assert manifest["test_frozen"] is manifest["annotation_completed"] is False
    normalized = (ROOT / "review_pool.jsonl").read_bytes().replace(b"\r\n", b"\n")
    assert manifest["dataset_sha256"] == hashlib.sha256(normalized).hexdigest()
    selected = select_second_annotation_items(items, seed=manifest["seed"])
    tasks = [
        json.loads(line)
        for line in (base / "participant/tasks.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    annotations = (base / "participant/ANNOTATIONS.md").read_text(encoding="utf-8")
    for entry, mapping, task in zip(selected, manifest["mapping"], tasks, strict=True):
        assert entry.item_id == mapping["item_id"]
        assert entry.primary_label.value == mapping["primary_label"]
        assert entry.split.value == mapping["split"]
        assert mapping["task_id"] == task["task_id"]
        assert task["claim"] == entry.claim and task["second_label"] is None
        assert task["rationale"] is None and not task["source_urls"]
        assert f"## {task['task_id']}" in annotations and entry.claim in annotations
    assert annotations.count("- Rótulo:\n") == 48
