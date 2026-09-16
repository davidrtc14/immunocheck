"""Baseline lexical agrupado por família, restrito ao desenvolvimento."""

from __future__ import annotations

import hashlib
from collections import defaultdict
from collections.abc import Sequence
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline

from immunocheck.domain.models import Verdict
from immunocheck.evaluation.benchmark_freeze import validate_freeze_manifest
from immunocheck.evaluation.end_to_end import (
    DatasetSplit,
    EndToEndDatasetError,
    EndToEndItem,
    load_end_to_end_items,
)

LEXICAL_BASELINE_SCHEMA_VERSION = 1
LEXICAL_BASELINE_SEED = 20260916
LEXICAL_BASELINE_FOLDS = 5
LEXICAL_BASELINE_BOOTSTRAP_RESAMPLES = 2000
LABELS = tuple(verdict.value for verdict in Verdict)


def load_frozen_development_items(root: Path) -> tuple[EndToEndItem, ...]:
    """Valida o congelamento e não expõe itens de teste ao experimento."""
    validate_freeze_manifest(root=root)
    items = load_end_to_end_items(root / "items.jsonl", require_reviewed=True)
    development = tuple(item for item in items if item.split is DatasetSplit.DEVELOPMENT)
    if not development:
        raise EndToEndDatasetError("O benchmark não possui itens de desenvolvimento.")
    return development


def evaluate_lexical_baseline(
    items: Sequence[EndToEndItem],
    *,
    folds: int = LEXICAL_BASELINE_FOLDS,
    seed: int = LEXICAL_BASELINE_SEED,
    bootstrap_resamples: int = LEXICAL_BASELINE_BOOTSTRAP_RESAMPLES,
) -> dict[str, object]:
    values = tuple(items)
    _validate_development_items(values, folds=folds, bootstrap_resamples=bootstrap_resamples)
    claims = np.asarray([item.claim for item in values], dtype=object)
    labels = np.asarray([item.label.value for item in values], dtype=object)
    groups = np.asarray([item.claim_family for item in values], dtype=object)
    splitter = StratifiedGroupKFold(n_splits=folds, shuffle=True, random_state=seed)
    predictions = np.empty(len(values), dtype=object)
    fold_by_index = np.full(len(values), -1, dtype=np.int32)
    fold_records: list[dict[str, object]] = []

    for fold_number, (train_indices, validation_indices) in enumerate(
        splitter.split(claims, labels, groups), start=1
    ):
        train_families = set(groups[train_indices])
        validation_families = set(groups[validation_indices])
        if train_families.intersection(validation_families):
            raise EndToEndDatasetError("Uma família vazou entre treino e validação.")
        if set(labels[train_indices]) != set(LABELS) or set(labels[validation_indices]) != set(
            LABELS
        ):
            raise EndToEndDatasetError("Cada fold precisa representar as quatro classes.")
        model = _pipeline(seed)
        model.fit(claims[train_indices].tolist(), labels[train_indices].tolist())
        fold_predictions = model.predict(claims[validation_indices].tolist())
        predictions[validation_indices] = fold_predictions
        fold_by_index[validation_indices] = fold_number
        fold_records.append(
            {
                "fold": fold_number,
                "training_items": len(train_indices),
                "validation_items": len(validation_indices),
                "training_families": sorted(str(value) for value in train_families),
                "validation_families": sorted(str(value) for value in validation_families),
                "metrics": _classification_metrics(labels[validation_indices], fold_predictions),
            }
        )
    if np.any(fold_by_index < 0):
        raise AssertionError("Existem itens sem previsão out-of-fold.")

    fitted = _pipeline(seed)
    fitted.fit(claims.tolist(), labels.tolist())
    metrics = _classification_metrics(labels, predictions)
    return {
        "schema_version": LEXICAL_BASELINE_SCHEMA_VERSION,
        "purpose": "detect_lexical_shortcuts_not_validate_immunocheck",
        "partition": DatasetSplit.DEVELOPMENT.value,
        "test_items_loaded_into_model": False,
        "seed": seed,
        "folds": folds,
        "bootstrap_unit": "claim_family",
        "bootstrap_resamples": bootstrap_resamples,
        "dataset_identity_sha256": _dataset_identity(values),
        "item_count": len(values),
        "family_count": len(set(groups)),
        "label_order": list(LABELS),
        "model": {
            "features": "word_tfidf_unigrams_bigrams",
            "classifier": "logistic_regression_balanced",
            "strip_accents": "unicode",
            "sublinear_tf": True,
        },
        "metrics": metrics,
        "bootstrap_95_percentile_interval": _cluster_bootstrap_intervals(
            labels,
            predictions,
            groups,
            resamples=bootstrap_resamples,
            seed=seed,
        ),
        "fold_records": fold_records,
        "top_weighted_terms_diagnostic_only": _top_weighted_terms(fitted),
        "predictions": [
            {
                "item_id": item.item_id,
                "claim_family": item.claim_family,
                "fold": int(fold_by_index[index]),
                "reference_label": item.label.value,
                "predicted_label": str(predictions[index]),
                "correct": bool(predictions[index] == item.label.value),
            }
            for index, item in enumerate(values)
        ],
    }


def _pipeline(seed: int) -> Pipeline:
    return Pipeline(
        (
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    strip_accents="unicode",
                    ngram_range=(1, 2),
                    min_df=1,
                    sublinear_tf=True,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=2000,
                    random_state=seed,
                    solver="lbfgs",
                ),
            ),
        )
    )


def _classification_metrics(reference: np.ndarray, predicted: np.ndarray) -> dict[str, object]:
    precision, recall, f1, support = precision_recall_fscore_support(
        reference,
        predicted,
        labels=LABELS,
        zero_division=0,
    )
    return {
        "accuracy": float(accuracy_score(reference, predicted)),
        "balanced_accuracy": float(balanced_accuracy_score(reference, predicted)),
        "macro_f1": float(f1_score(reference, predicted, labels=LABELS, average="macro")),
        "weighted_f1": float(f1_score(reference, predicted, labels=LABELS, average="weighted")),
        "per_class": {
            label: {
                "precision": float(precision[index]),
                "recall": float(recall[index]),
                "f1": float(f1[index]),
                "support": int(support[index]),
            }
            for index, label in enumerate(LABELS)
        },
        "confusion_matrix_reference_rows": confusion_matrix(
            reference, predicted, labels=LABELS
        ).tolist(),
    }


def _cluster_bootstrap_intervals(
    reference: np.ndarray,
    predicted: np.ndarray,
    groups: np.ndarray,
    *,
    resamples: int,
    seed: int,
) -> dict[str, dict[str, float]]:
    indices_by_group: dict[str, list[int]] = defaultdict(list)
    for index, group in enumerate(groups):
        indices_by_group[str(group)].append(index)
    group_names = tuple(sorted(indices_by_group))
    rng = np.random.default_rng(seed)
    samples: dict[str, list[float]] = {
        "accuracy": [],
        "balanced_accuracy": [],
        "macro_f1": [],
    }
    attempts = 0
    while len(samples["accuracy"]) < resamples:
        attempts += 1
        if attempts > resamples * 20:
            raise EndToEndDatasetError("Bootstrap não conseguiu representar as quatro classes.")
        selected_groups = rng.choice(group_names, size=len(group_names), replace=True)
        selected_indices = np.asarray(
            [index for group in selected_groups for index in indices_by_group[str(group)]],
            dtype=np.int32,
        )
        sampled_reference = reference[selected_indices]
        if set(sampled_reference) != set(LABELS):
            continue
        sampled_predicted = predicted[selected_indices]
        samples["accuracy"].append(float(accuracy_score(sampled_reference, sampled_predicted)))
        samples["balanced_accuracy"].append(
            float(balanced_accuracy_score(sampled_reference, sampled_predicted))
        )
        samples["macro_f1"].append(
            float(
                f1_score(
                    sampled_reference,
                    sampled_predicted,
                    labels=LABELS,
                    average="macro",
                )
            )
        )
    return {
        metric: {
            "lower": float(np.quantile(values, 0.025)),
            "median": float(np.quantile(values, 0.5)),
            "upper": float(np.quantile(values, 0.975)),
        }
        for metric, values in samples.items()
    }


def _top_weighted_terms(model: Pipeline, *, limit: int = 15) -> dict[str, list[dict[str, object]]]:
    vectorizer: TfidfVectorizer = model.named_steps["tfidf"]
    classifier: LogisticRegression = model.named_steps["classifier"]
    features = vectorizer.get_feature_names_out()
    return {
        str(label): [
            {"term": str(features[index]), "coefficient": float(coefficients[index])}
            for index in np.argsort(coefficients)[-limit:][::-1]
        ]
        for label, coefficients in zip(classifier.classes_, classifier.coef_, strict=True)
    }


def _dataset_identity(items: tuple[EndToEndItem, ...]) -> str:
    content = "".join(
        f"{item.item_id}\t{item.claim_family}\t{item.label.value}\t{item.claim}\n" for item in items
    )
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _validate_development_items(
    items: tuple[EndToEndItem, ...], *, folds: int, bootstrap_resamples: int
) -> None:
    if not items:
        raise EndToEndDatasetError("O baseline exige itens de desenvolvimento.")
    if any(item.split is not DatasetSplit.DEVELOPMENT for item in items):
        raise EndToEndDatasetError("O baseline lexical não pode receber itens de teste.")
    if any(not item.claim_family for item in items):
        raise EndToEndDatasetError("Todo item precisa de claim_family.")
    if folds < 2 or len({item.claim_family for item in items}) < folds:
        raise EndToEndDatasetError("Quantidade de folds incompatível com as famílias.")
    if bootstrap_resamples <= 0:
        raise EndToEndDatasetError("Bootstrap exige pelo menos uma reamostragem.")
    if {item.label.value for item in items} != set(LABELS):
        raise EndToEndDatasetError("O baseline exige as quatro classes.")
