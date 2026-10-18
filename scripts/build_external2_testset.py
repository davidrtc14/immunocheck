"""Monta o teste externo 2 (ADR-052) a partir do feed ClaimReview do Data Commons.

O feed (`https://storage.googleapis.com/datacommons-feeds/factcheck/latest/data.json`, compilação
CC BY 4.0) traz as marcações ClaimReview das agências de checagem: alegação, rótulo, data e link.
Nenhuma marcação em português declara licença própria (`sdLicense`), então só a referência (URL,
rótulo mapeado, tema, cobertura e `claim_sha256`) é versionada; o texto é reconstruído localmente em
`output/external2_v7/items.jsonl` a partir do feed baixado, cujo sha256 fica no congelamento.

As regras de seleção e de mapeamento de rótulo são as do teste externo 1
(`scripts/build_external_testset.py`), importadas sem alteração. Nenhuma inferência do ImmunoCheck é
executada sobre estes itens.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_external_testset import (  # type: ignore[import-not-found]
    EVAL_JACCARD,
    EVAL_RATIO,
    INTERNAL_JACCARD,
    INTERNAL_RATIO,
    URL_POLITICAL_PATTERN,
    Candidate,
    claim_sha256,
    clean_claim,
    collect_evaluation_claims,
    corpus_tags,
    corpus_urls,
    exclusion_reason,
    fact_checker_hits,
    is_near_duplicate,
    is_vaccination_claim,
    load_catalog,
    make_item,
    manifest_entry,
    map_agency_label,
    normalize_text,
    to_jsonl,
)

REPOSITORY = Path(__file__).resolve().parents[1]
FEED = REPOSITORY / "output/external2_v7/download/data.json"
OUT = REPOSITORY / "evaluation/refinement_v7/external2"
LOCAL_ITEMS = REPOSITORY / "output/external2_v7/items.jsonl"
EXTERNAL1_SUPPLEMENT = REPOSITORY / "output/external_v6/items_supplement.jsonl"
CORPUS_MANIFEST = REPOSITORY / "corpus/processed/manifest.json"
SOURCE = "datacommons_claimreview"
FEED_URL = "https://storage.googleapis.com/datacommons-feeds/factcheck/latest/data.json"


def feed_candidates(feed: dict) -> list[Candidate]:
    candidates = []
    for element in feed.get("dataFeedElement", []):
        for review in element.get("item") or []:
            claim = clean_claim(review.get("claimReviewed") or "")
            url = review.get("url") or element.get("url")
            if not claim or not url:
                continue
            label = ((review.get("reviewRating") or {}).get("alternateName") or "").strip()
            author = review.get("author") or {}
            candidates.append(
                Candidate(
                    source=SOURCE,
                    source_key=url,
                    claim=claim,
                    source_label=label,
                    verdict=map_agency_label(label) if label else None,
                    agency=(author.get("name") or "").strip() or urlparse(url).netloc,
                    claim_date=(review.get("datePublished") or "")[:10] or None,
                    review_url=url,
                    redistributable=bool(review.get("sdLicense")),
                )
            )
    return candidates


def select(candidates: list[Candidate], evaluation_claims: list[str], report: Counter) -> list:
    """Mesmas regras e limiares do teste externo 1, na mesma ordem."""

    pool = []
    for candidate in candidates:
        if not is_vaccination_claim(candidate.claim):
            continue
        report["vaccine_candidates"] += 1
        reason = exclusion_reason(candidate.claim)
        slug = normalize_text(unquote(urlparse(candidate.review_url).path).replace("-", " "))
        if not reason and URL_POLITICAL_PATTERN.search(slug):
            reason = "political_actor"
        if reason:
            report[f"excluded:{reason}"] += 1
            continue
        if candidate.verdict is None:
            report["excluded:label_without_mapping"] += 1
            continue
        if any(
            is_near_duplicate(candidate.claim, other, jaccard=EVAL_JACCARD, ratio=EVAL_RATIO)
            for other in evaluation_claims
        ):
            report["excluded:near_duplicate_of_existing_evaluation"] += 1
            continue
        pool.append(candidate)
    pool.sort(key=lambda item: (item.claim_date or "", item.source_key, item.claim))
    groups: list[list[Candidate]] = []
    for candidate in pool:
        for group in groups:
            if is_near_duplicate(
                candidate.claim, group[0].claim, jaccard=INTERNAL_JACCARD, ratio=INTERNAL_RATIO
            ):
                group.append(candidate)
                break
        else:
            groups.append([candidate])
    selected = []
    for group in groups:
        if len({item.verdict for item in group}) > 1:
            report["excluded:near_duplicate_label_conflict"] += len(group)
            continue
        report["excluded:near_duplicate_internal"] += len(group) - 1
        selected.append(group[0])
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(description="Teste externo 2 (ADR-052).")
    parser.add_argument("--feed", type=Path, default=FEED)
    args = parser.parse_args()

    feed_bytes = args.feed.read_bytes()
    feed_sha = hashlib.sha256(feed_bytes).hexdigest()
    frozen = OUT / "freeze.json"
    if frozen.exists():
        expected = json.loads(frozen.read_text("utf-8"))["feed_sha256"]
        if expected != feed_sha:
            raise SystemExit("O feed não confere com o sha256 congelado.")
    feed = json.loads(feed_bytes.decode("utf-8"))

    catalog = load_catalog()
    hits = fact_checker_hits(corpus_urls(catalog, CORPUS_MANIFEST))
    if hits:
        raise SystemExit(f"O corpus contém páginas de agências de checagem: {hits}")
    evaluation_claims = collect_evaluation_claims(REPOSITORY / "evaluation", exclude=OUT)
    external1 = [
        json.loads(line)["claim"]
        for line in EXTERNAL1_SUPPLEMENT.read_text("utf-8").splitlines()
        if line
    ]
    report: Counter = Counter()
    candidates = feed_candidates(feed)
    report["feed_reviews"] = len(candidates)
    selected = select(candidates, evaluation_claims + external1, report)
    tags = corpus_tags(catalog)
    items = [
        make_item(candidate, f"ext7-{index:04d}", tags)
        for index, candidate in enumerate(selected, start=1)
    ]
    OUT.mkdir(parents=True, exist_ok=True)
    LOCAL_ITEMS.parent.mkdir(parents=True, exist_ok=True)
    manifest = to_jsonl(manifest_entry(item) for item in items)
    local = to_jsonl(items)
    (OUT / "manifest.jsonl").write_text(manifest, encoding="utf-8", newline="\n")
    LOCAL_ITEMS.write_text(local, encoding="utf-8", newline="\n")
    summary = {
        "feed_url": FEED_URL,
        "feed_sha256": feed_sha,
        "feed_date_modified": feed.get("dateModified"),
        "counts": dict(sorted(report.items())),
        "items": len(items),
        "labels": dict(Counter(item["label"] for item in items)),
        "agencies": dict(Counter(item["external_agency"] for item in items).most_common()),
        "years": dict(
            sorted(Counter((item["external_claim_date"] or "")[:4] for item in items).items())
        ),
        "corpus_topic_coverage": dict(Counter(item["corpus_topic_coverage"] for item in items)),
        "redistributable": sum(1 for c in selected if c.redistributable),
    }
    (OUT / "build_report.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    if not frozen.exists():
        frozen.write_text(
            json.dumps(
                {
                    "feed_sha256": feed_sha,
                    "manifest_sha256": hashlib.sha256(manifest.encode("utf-8")).hexdigest(),
                    "local_items_sha256": hashlib.sha256(local.encode("utf-8")).hexdigest(),
                    "builder_sha256": hashlib.sha256(
                        Path(__file__).read_bytes().replace(b"\r\n", b"\n")
                    ).hexdigest(),
                    "claims_sha256": [claim_sha256(str(item["claim"])) for item in items],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
