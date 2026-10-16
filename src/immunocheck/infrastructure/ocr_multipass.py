"""OCR em várias passadas: variantes de pré-processamento e de segmentação (ADR-050).

Cada combinação de imagem preparada e modo de segmentação do Tesseract (PSM) é lida uma vez; vence
a leitura com mais caracteres lidos com confiança. A inclinação é corrigida antes, a partir das
linhas quase horizontais da imagem. A política de qualidade é a mesma do OCR de passada única.
"""

from __future__ import annotations

import csv
import io
import os
import shutil
import subprocess
from collections import defaultdict
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np

from immunocheck.application.content_normalizer import ContentExtractionError
from immunocheck.domain.models import ContentKind, ContentSubmission
from immunocheck.infrastructure.ocr import OCRQualityPolicy, inspect_image

TARGET_LONG_SIDE = 2_000
MAX_UPSCALE = 3.0
MIN_SKEW_DEGREES = 0.4
MAX_SKEW_DEGREES = 12.0
MIN_SCORING_CONFIDENCE = 40.0


@dataclass(frozen=True, slots=True)
class OCRWord:
    text: str
    confidence: float
    line_key: tuple[str, str, str, str]


@dataclass(frozen=True, slots=True)
class OCRReading:
    variant: str
    psm: int
    words: tuple[OCRWord, ...]

    @property
    def score(self) -> float:
        """Caracteres lidos com confiança; ruído de baixa confiança não soma."""

        return sum(
            len(word.text) * word.confidence / 100
            for word in self.words
            if word.confidence >= MIN_SCORING_CONFIDENCE and _alnum_ratio(word.text) >= 0.5
        )

    @property
    def mean_confidence(self) -> float:
        weight = sum(max(1, len(word.text)) for word in self.words)
        if not weight:
            return 0.0
        return sum(word.confidence * max(1, len(word.text)) for word in self.words) / weight

    def text(self, minimum_word_confidence: float = 0.0) -> str:
        lines: dict[tuple[str, str, str, str], list[str]] = defaultdict(list)
        for word in self.words:
            if word.confidence >= minimum_word_confidence:
                lines[word.line_key].append(word.text)
        return "\n".join(" ".join(line) for line in lines.values())


@dataclass(frozen=True, slots=True)
class OCRResult:
    text: str
    mean_confidence: float
    variant: str
    psm: int


Preprocessor = Callable[[np.ndarray], np.ndarray]


@dataclass(frozen=True, slots=True)
class MultiPassTesseractOCR:
    executable: Path
    language: str = "por"
    # PSM 11 (texto esparso) foi descartado na calibração: embaralha a ordem das linhas.
    psm_modes: tuple[int, ...] = (6, 4)
    variants: tuple[str, ...] = ("otsu", "gray", "adaptive", "clahe")
    minimum_word_confidence: float = 0.0
    timeout_seconds: float = 25.0
    maximum_tsv_bytes: int = 2_000_000
    max_workers: int = 4
    correct_skew: bool = True
    quality: OCRQualityPolicy = field(default_factory=OCRQualityPolicy)

    @classmethod
    def from_environment(cls, **options: object) -> MultiPassTesseractOCR:
        configured = os.getenv("TESSERACT_CMD")
        candidates = (
            configured,
            shutil.which("tesseract"),
            r"C:\Program Files\Tesseract-OCR\tesseract.exe" if os.name == "nt" else None,
        )
        for candidate in candidates:
            if candidate and Path(candidate).is_file():
                return cls(executable=Path(candidate).resolve(), **options)
        raise ValueError("Tesseract não encontrado; configure TESSERACT_CMD.")

    def extract(self, submission: ContentSubmission) -> str:
        return self.read(submission).text

    def read(self, submission: ContentSubmission) -> OCRResult:
        if submission.kind is not ContentKind.IMAGE or submission.data is None:
            raise ContentExtractionError("O OCR recebeu uma entrada incompatível.")
        info = inspect_image(submission.data, declared_media_type=submission.media_type)
        if submission.width != info.width or submission.height != info.height:
            raise ContentExtractionError("As dimensões declaradas da imagem são inconsistentes.")
        gray = _decode_gray(submission.data)
        gray = _upscale(gray)
        if self.correct_skew:
            gray = deskew(gray)
        prepared = {name: _encode_png(PREPROCESSORS[name](gray)) for name in self.variants}
        jobs = [(name, psm) for name in self.variants for psm in self.psm_modes]
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            readings = list(
                pool.map(lambda job: self._read_variant(job[0], prepared[job[0]], job[1]), jobs)
            )
        best = max(readings, key=lambda reading: reading.score)
        text = best.text(self.minimum_word_confidence)
        _require_quality(text, best, self.quality)
        return OCRResult(text, best.mean_confidence, best.variant, best.psm)

    def _read_variant(self, variant: str, image: bytes, psm: int) -> OCRReading:
        command = [str(self.executable), "stdin", "stdout", "-l", self.language, "--psm",
                   str(psm), "tsv"]
        run_options: dict[str, object] = {}
        if os.name == "nt":
            run_options["creationflags"] = subprocess.CREATE_NO_WINDOW
        try:
            completed = subprocess.run(
                command,
                input=image,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=self.timeout_seconds,
                **run_options,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ContentExtractionError("O OCR local não conseguiu processar a imagem.") from exc
        if completed.returncode != 0:
            raise ContentExtractionError("O OCR local recusou a imagem.")
        if len(completed.stdout) > self.maximum_tsv_bytes:
            raise ContentExtractionError("A saída do OCR excedeu o limite seguro.")
        return OCRReading(variant, psm, parse_tsv_words(completed.stdout))


def parse_tsv_words(raw_tsv: bytes) -> tuple[OCRWord, ...]:
    try:
        rows = csv.DictReader(io.StringIO(raw_tsv.decode("utf-8")), delimiter="\t")
        words = []
        for row in rows:
            text = (row.get("text") or "").strip()
            confidence = float(row.get("conf") or "-1")
            if not text or confidence < 0:
                continue
            key = tuple(row.get(name) or "" for name in ("page_num", "block_num", "par_num",
                                                          "line_num"))
            words.append(OCRWord(text, confidence, key))
    except (TypeError, ValueError, UnicodeDecodeError) as exc:
        raise ContentExtractionError("O OCR local retornou dados inválidos.") from exc
    return tuple(words)


def deskew(gray: np.ndarray) -> np.ndarray:
    """Gira a imagem pela mediana dos ângulos das linhas quase horizontais."""

    angle = estimate_skew(gray)
    if angle is None or abs(angle) < MIN_SKEW_DEGREES:
        return gray
    height, width = gray.shape
    matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1.0)
    border = int(np.median(gray))
    return cv2.warpAffine(gray, matrix, (width, height), flags=cv2.INTER_CUBIC,
                          borderValue=border)


def estimate_skew(gray: np.ndarray) -> float | None:
    edges = cv2.Canny(gray, 50, 150)
    width = gray.shape[1]
    lines = cv2.HoughLinesP(edges, 1, np.pi / 720, threshold=120,
                            minLineLength=width // 4, maxLineGap=12)
    if lines is None:
        return None
    angles = []
    for x1, y1, x2, y2 in lines[:, 0]:
        angle = float(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
        if abs(angle) <= MAX_SKEW_DEGREES:
            angles.append(angle)
    if len(angles) < 3:
        return None
    return float(np.median(angles))


def _decode_gray(data: bytes) -> np.ndarray:
    image = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ContentExtractionError("O OpenCV não conseguiu decodificar a imagem.")
    return image


def _upscale(gray: np.ndarray) -> np.ndarray:
    longest = max(gray.shape)
    if longest >= TARGET_LONG_SIDE:
        return gray
    scale = min(MAX_UPSCALE, TARGET_LONG_SIDE / longest)
    return cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)


def _dark_text_on_light(image: np.ndarray) -> np.ndarray:
    return cv2.bitwise_not(image) if float(np.mean(image)) < 127.0 else image


def _otsu(gray: np.ndarray) -> np.ndarray:
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return _dark_text_on_light(binary)


def _gray(gray: np.ndarray) -> np.ndarray:
    return _dark_text_on_light(gray)


def _adaptive(gray: np.ndarray) -> np.ndarray:
    oriented = _dark_text_on_light(gray)
    return cv2.adaptiveThreshold(oriented, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 31, 15)


def _clahe(gray: np.ndarray) -> np.ndarray:
    equalized = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(gray)
    return _otsu(equalized)


PREPROCESSORS: dict[str, Preprocessor] = {
    "otsu": _otsu,
    "gray": _gray,
    "adaptive": _adaptive,
    "clahe": _clahe,
}


def _encode_png(image: np.ndarray) -> bytes:
    success, encoded = cv2.imencode(".png", image)
    if not success:
        raise ContentExtractionError("Não foi possível preparar a imagem para OCR.")
    return encoded.tobytes()


def _alnum_ratio(text: str) -> float:
    visible = [char for char in text if not char.isspace()]
    return sum(char.isalnum() for char in visible) / len(visible) if visible else 0.0


def _require_quality(text: str, reading: OCRReading, policy: OCRQualityPolicy) -> None:
    alphanumeric = sum(char.isalnum() for char in text)
    if (
        len(reading.words) < policy.minimum_words
        or alphanumeric < policy.minimum_alphanumeric_characters
        or reading.mean_confidence < policy.minimum_mean_confidence
        or _alnum_ratio(text) < policy.minimum_alphanumeric_ratio
    ):
        raise ContentExtractionError(
            "O texto da imagem está ilegível ou tem qualidade insuficiente para uma análise segura."
        )
    if len(text) > policy.maximum_text_characters:
        raise ContentExtractionError("A imagem contém texto demais; envie um recorte da alegação.")
