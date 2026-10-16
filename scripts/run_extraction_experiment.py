"""Executa o benchmark sintético de extração multimodal (ADR-050).

Etapa `extract`: só a conversão da entrada em texto (OCR, página, mensagem), sem LLM; é barata
e determinística, e pode ser repetida à vontade na fase `dev`.
Etapa `verdict`: pipeline completo (v3 por padrão) sobre a entrada multimodal e sobre a alegação
limpa em texto (`reference`), para medir a concordância do veredito.
Fase `dev`: só itens e modelos de desenvolvimento (e o controle limpo).
Fase `final`: execução única, exige `evaluation/extraction_v1/freeze.json` válido.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import time
from collections.abc import Callable
from pathlib import Path

from immunocheck.application.content_normalizer import ContentExtractionError, MultimodalNormalizer
from immunocheck.application.input_understanding import UnderstandingNormalizer, route_message
from immunocheck.domain.models import ContentKind, ContentSubmission
from immunocheck.evaluation import extraction_benchmark as bench
from immunocheck.evaluation.end_to_end import load_end_to_end_items
from immunocheck.infrastructure.main_content import MainContentLinkExtractor
from immunocheck.infrastructure.ocr import TesseractOCR
from immunocheck.infrastructure.ocr_multipass import MultiPassTesseractOCR
from immunocheck.infrastructure.ollama_vision import OllamaVisionTranscriber
from immunocheck.infrastructure.web_content import FetchedResource, SafeLinkTextExtractor

REPOSITORY = Path(__file__).resolve().parents[1]
ITEMS = REPOSITORY / "evaluation/refinement_v4/items.jsonl"
ROOT = REPOSITORY / "evaluation/extraction_v1"
RESULTS = ROOT / "results"
FREEZE = ROOT / "freeze.json"
CONDITIONS = ("baseline", "improved", "improved_vision")
FROZEN_FILES = (
    "src/immunocheck/evaluation/extraction_benchmark.py",
    "scripts/run_extraction_experiment.py",
    # Linha de base (extração atual), reexecutada na fase final.
    "src/immunocheck/application/content_normalizer.py",
    "src/immunocheck/infrastructure/ocr.py",
    "src/immunocheck/infrastructure/web_content.py",
    # Extração v2.
    "src/immunocheck/application/input_cleaning.py",
    "src/immunocheck/application/input_understanding.py",
    "src/immunocheck/application/passage_selection.py",
    "src/immunocheck/infrastructure/main_content.py",
    "src/immunocheck/infrastructure/ocr_multipass.py",
    "src/immunocheck/infrastructure/ollama_vision.py",
)


@dataclasses.dataclass(frozen=True, slots=True)
class MappingFetcher:
    """Serve as páginas geradas em memória; URL desconhecida falha como um link inacessível."""

    resources: dict[str, FetchedResource]

    def fetch(self, url: str) -> FetchedResource:
        try:
            return self.resources[url]
        except KeyError as exc:
            raise ContentExtractionError("Não foi possível acessar o link informado.") from exc


@dataclasses.dataclass(slots=True)
class RecordingNormalizer:
    delegate: object
    last_text: str | None = None

    def normalize(self, submission: ContentSubmission) -> str:
        self.last_text = None
        self.last_text = self.delegate.normalize(submission)
        return self.last_text


def legacy_route(message: str) -> ContentSubmission:
    """Roteamento atual do Telegram: só uma URL isolada vira link."""

    text = message.strip()
    if " " not in text and text.lower().startswith(("http://", "https://")):
        return ContentSubmission(kind=ContentKind.LINK, url=text)
    return ContentSubmission(kind=ContentKind.TEXT, text=text)


def build_condition(
    condition: str, fetcher: MappingFetcher
) -> tuple[object, Callable[[str], ContentSubmission]]:
    if condition == "baseline":
        normalizer = MultimodalNormalizer(
            image_extractor=TesseractOCR.from_environment(),
            link_extractor=SafeLinkTextExtractor(fetcher=fetcher),
        )
        return normalizer, legacy_route
    if condition in {"improved", "improved_vision"}:
        normalizer = UnderstandingNormalizer(
            image_reader=MultiPassTesseractOCR.from_environment(),
            link_extractor=MainContentLinkExtractor(fetcher=fetcher),
            vision=OllamaVisionTranscriber() if condition == "improved_vision" else None,
        )
        return normalizer, route_message
    raise ValueError(f"Condição desconhecida: {condition}")


def submission_for(
    case: bench.ExtractionCase, route: Callable[[str], ContentSubmission]
) -> ContentSubmission:
    if case.modality == "image":
        image = bench.render_image(case)
        return ContentSubmission(
            kind=ContentKind.IMAGE,
            data=image.data,
            media_type=image.media_type,
            width=image.width,
            height=image.height,
        )
    if case.modality == "link":
        return ContentSubmission(kind=ContentKind.LINK, url=bench.page_url(case))
    if case.modality == "message":
        return route(bench.render_message(case))
    if case.modality == "text":
        # Como no bot, toda mensagem digitada passa pelo roteamento da condição.
        return route(bench.render_text(case))
    raise ValueError(f"Modalidade desconhecida: {case.modality}")


def page_resources(cases: list[bench.ExtractionCase]) -> dict[str, FetchedResource]:
    resources: dict[str, FetchedResource] = {}
    for case in cases:
        if case.modality in {"link", "message"}:
            page = bench.render_page(case)
            resources[page.url] = FetchedResource(page.url, page.content_type, page.body)
    return resources


def select_cases(phase: str, modalities: tuple[str, ...]) -> list[bench.ExtractionCase]:
    items = load_end_to_end_items(ITEMS, require_reviewed=True)
    cases = [case for case in bench.build_cases(items) if case.modality in modalities]
    if phase == "dev":
        return [
            case
            for case in cases
            if case.item_split == "development" and case.template_split != "reserved"
        ]
    return [case for case in cases if case.item_split == "test"]


def file_hashes() -> dict[str, str]:
    return {
        name: hashlib.sha256((REPOSITORY / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        for name in FROZEN_FILES
    }


def verify_freeze() -> None:
    if not FREEZE.is_file():
        raise SystemExit("A fase final exige evaluation/extraction_v1/freeze.json registrado antes.")
    frozen = json.loads(FREEZE.read_text(encoding="utf-8"))
    changed = [name for name, digest in file_hashes().items() if frozen["sha256"].get(name) != digest]
    changed += [
        f"fonte {name}"
        for name, digest in bench.font_hashes().items()
        if frozen["fonts"].get(name) != digest
    ]
    if changed:
        raise SystemExit("Congelamento violado: " + ", ".join(changed))


def extraction_metrics(case: bench.ExtractionCase, extracted: str | None) -> dict[str, object]:
    if extracted is None:
        return {"cer": 1.0, "cer_no_accents": 1.0, "markers_preserved": False}
    return {
        "cer": round(bench.substring_cer(case.target_claim, extracted), 4),
        "cer_no_accents": round(
            bench.substring_cer(case.target_claim, extracted, strip_accents=True), 4
        ),
        "markers_preserved": bench.markers_preserved(case.target_claim, extracted),
    }


def case_record(case: bench.ExtractionCase) -> dict[str, object]:
    return {
        "case_id": case.case_id,
        "parent_item_id": case.parent_item_id,
        "item_split": case.item_split,
        "modality": case.modality,
        "template": case.template,
        "template_split": case.template_split,
        "claim_family": case.claim_family,
        "expected_label": case.expected_label,
    }


def run_extract(cases, normalizer, route, handle, done: set[str]) -> None:
    for case in cases:
        if case.case_id in done:
            continue
        submission = submission_for(case, route)
        started = time.perf_counter()
        extracted, rejection = None, None
        try:
            extracted = normalizer.normalize(submission)
        except ContentExtractionError as exc:
            rejection = str(exc)
        record = case_record(case)
        record.update(
            submission_kind=submission.kind.value,
            extracted=extracted,
            rejection=rejection,
            latency_ms=round((time.perf_counter() - started) * 1000, 1),
            **extraction_metrics(case, extracted),
        )
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        handle.flush()
        print(case.case_id, f"cer={record['cer']}", rejection or "", flush=True)


def run_verdict(cases, normalizer, route, handle, done: set[str]) -> None:
    from immunocheck.bootstrap import build_routed_multimodal_pipeline

    recorder = RecordingNormalizer(normalizer)
    pipeline = dataclasses.replace(build_routed_multimodal_pipeline(), normalizer=recorder)
    references = {}
    for case in cases:
        references.setdefault(case.parent_item_id, case)
    jobs = [("reference", case) for case in references.values()] + [
        ("case", case) for case in cases
    ]
    for kind, case in jobs:
        case_id = f"{case.parent_item_id}-reference" if kind == "reference" else case.case_id
        if case_id in done:
            continue
        submission = (
            ContentSubmission(kind=ContentKind.TEXT, text=case.target_claim)
            if kind == "reference"
            else submission_for(case, route)
        )
        started = time.perf_counter()
        verdict = rejection = failure = None
        try:
            verdict = pipeline.run(submission).verdict.value
        except ContentExtractionError as exc:
            rejection = str(exc)
        except Exception as exc:  # noqa: BLE001 - falha técnica é dado do experimento
            failure = type(exc).__name__
        record = case_record(case)
        if kind == "reference":
            record.update(case_id=case_id, modality="reference", template="clean_text",
                          template_split="control")
        record.update(
            submission_kind=submission.kind.value,
            extracted=recorder.last_text,
            verdict=verdict,
            rejection=rejection,
            failure=failure,
            latency_ms=round((time.perf_counter() - started) * 1000, 1),
        )
        if kind == "case":
            record.update(extraction_metrics(case, recorder.last_text if not rejection else None))
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        handle.flush()
        print(case_id, "->", verdict, rejection or failure or "", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark de extração multimodal (ADR-050).")
    parser.add_argument("--condition", choices=CONDITIONS, required=True)
    parser.add_argument("--phase", choices=("dev", "final"), required=True)
    parser.add_argument("--stage", choices=("extract", "verdict"), required=True)
    parser.add_argument(
        "--modalities", nargs="+", choices=tuple(bench.MODALITY_TEMPLATES),
        default=list(bench.MODALITY_TEMPLATES),
    )
    parser.add_argument("--tag", default="run1")
    args = parser.parse_args()
    if args.phase == "final":
        verify_freeze()

    cases = select_cases(args.phase, tuple(args.modalities))
    fetcher = MappingFetcher(page_resources(cases))
    normalizer, route = build_condition(args.condition, fetcher)
    output_dir = RESULTS / args.phase
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint = output_dir / f"{args.condition}_{args.stage}_{args.tag}.jsonl"
    done: set[str] = set()
    if checkpoint.exists():
        done = {
            json.loads(line)["case_id"] for line in checkpoint.read_text("utf-8").splitlines() if line
        }
        if args.phase == "final" and args.stage == "verdict" and done:
            print(f"Retomando execução final ({len(done)} registros já gravados).")
    runner = run_extract if args.stage == "extract" else run_verdict
    with checkpoint.open("a", encoding="utf-8", newline="\n") as handle:
        runner(cases, normalizer, route, handle, done)


if __name__ == "__main__":
    main()
