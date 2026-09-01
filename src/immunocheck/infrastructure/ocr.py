from __future__ import annotations

import csv
import io
import os
import shutil
import subprocess
import warnings
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError

from immunocheck.application.content_normalizer import ContentExtractionError
from immunocheck.domain.models import ContentKind, ContentSubmission

MEDIA_TYPE_BY_FORMAT = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
}


@dataclass(frozen=True, slots=True)
class ImageInfo:
    media_type: str
    width: int
    height: int


@dataclass(frozen=True, slots=True)
class OCRQualityPolicy:
    minimum_words: int = 3
    minimum_alphanumeric_characters: int = 12
    minimum_mean_confidence: float = 55.0
    minimum_alphanumeric_ratio: float = 0.5
    maximum_text_characters: int = 12_000


def inspect_image(
    data: bytes,
    *,
    declared_media_type: str | None = None,
    maximum_pixels: int = 12_000_000,
) -> ImageInfo:
    if not data:
        raise ContentExtractionError("A imagem recebida está vazia.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data)) as image:
                image_format = image.format
                width, height = image.size
                image.verify()
    except (UnidentifiedImageError, OSError, SyntaxError, Image.DecompressionBombWarning) as exc:
        raise ContentExtractionError("O arquivo não é uma imagem válida.") from exc

    media_type = MEDIA_TYPE_BY_FORMAT.get(image_format or "")
    if media_type is None:
        raise ContentExtractionError("O formato real da imagem não é aceito.")
    if declared_media_type is not None and declared_media_type != media_type:
        raise ContentExtractionError("O tipo declarado não corresponde ao conteúdo da imagem.")
    if width <= 0 or height <= 0 or width * height > maximum_pixels:
        raise ContentExtractionError("A imagem excede o limite de 12 megapixels.")
    return ImageInfo(media_type=media_type, width=width, height=height)


@dataclass(frozen=True, slots=True)
class TesseractOCR:
    executable: Path
    language: str = "por"
    timeout_seconds: float = 25.0
    maximum_tsv_bytes: int = 2_000_000
    quality: OCRQualityPolicy = OCRQualityPolicy()

    @classmethod
    def from_environment(cls) -> TesseractOCR:
        configured = os.getenv("TESSERACT_CMD")
        candidates = (
            configured,
            shutil.which("tesseract"),
            r"C:\Program Files\Tesseract-OCR\tesseract.exe" if os.name == "nt" else None,
        )
        for candidate in candidates:
            if candidate and Path(candidate).is_file():
                return cls(executable=Path(candidate).resolve())
        raise ValueError("Tesseract não encontrado; configure TESSERACT_CMD.")

    def extract(self, submission: ContentSubmission) -> str:
        if submission.kind is not ContentKind.IMAGE or submission.data is None:
            raise ContentExtractionError("O OCR recebeu uma entrada incompatível.")
        info = inspect_image(
            submission.data,
            declared_media_type=submission.media_type,
        )
        if submission.width != info.width or submission.height != info.height:
            raise ContentExtractionError("As dimensões declaradas da imagem são inconsistentes.")

        encoded = _preprocess_image(submission.data)
        command = [
            str(self.executable),
            "stdin",
            "stdout",
            "-l",
            self.language,
            "--psm",
            "6",
            "tsv",
        ]
        run_options: dict[str, object] = {}
        if os.name == "nt":
            run_options["creationflags"] = subprocess.CREATE_NO_WINDOW
        try:
            completed = subprocess.run(
                command,
                input=encoded,
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
        return _parse_tsv(completed.stdout, self.quality)


def _preprocess_image(data: bytes) -> bytes:
    encoded_array = np.frombuffer(data, dtype=np.uint8)
    image = cv2.imdecode(encoded_array, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ContentExtractionError("O OpenCV não conseguiu decodificar a imagem.")
    height, width = image.shape
    if max(width, height) < 1_600:
        scale = min(2.0, 1_600 / max(width, height))
        image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    blurred = cv2.GaussianBlur(image, (3, 3), 0)
    _, thresholded = cv2.threshold(
        blurred,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU,
    )
    if float(np.mean(thresholded)) < 127.0:
        thresholded = cv2.bitwise_not(thresholded)
    success, encoded = cv2.imencode(".png", thresholded)
    if not success:
        raise ContentExtractionError("Não foi possível preparar a imagem para OCR.")
    return encoded.tobytes()


def _parse_tsv(raw_tsv: bytes, policy: OCRQualityPolicy) -> str:
    try:
        decoded = raw_tsv.decode("utf-8")
        rows = csv.DictReader(io.StringIO(decoded), delimiter="\t")
        words: list[tuple[str, float]] = []
        lines: dict[tuple[str, str, str, str], list[str]] = defaultdict(list)
        for row in rows:
            text = (row.get("text") or "").strip()
            if not text:
                continue
            confidence = float(row.get("conf") or "-1")
            if confidence < 0:
                continue
            words.append((text, confidence))
            key = (
                row.get("page_num") or "",
                row.get("block_num") or "",
                row.get("par_num") or "",
                row.get("line_num") or "",
            )
            lines[key].append(text)
    except (TypeError, ValueError, UnicodeDecodeError) as exc:
        raise ContentExtractionError("O OCR local retornou dados inválidos.") from exc

    text = "\n".join(" ".join(line_words) for line_words in lines.values())
    alphanumeric_count = sum(character.isalnum() for character in text)
    visible_count = sum(not character.isspace() for character in text)
    alphanumeric_ratio = alphanumeric_count / visible_count if visible_count else 0.0
    confidence_weight = sum(max(1, len(word)) for word, _ in words)
    mean_confidence = (
        sum(confidence * max(1, len(word)) for word, confidence in words) / confidence_weight
        if confidence_weight
        else 0.0
    )
    if (
        len(words) < policy.minimum_words
        or alphanumeric_count < policy.minimum_alphanumeric_characters
        or mean_confidence < policy.minimum_mean_confidence
        or alphanumeric_ratio < policy.minimum_alphanumeric_ratio
    ):
        raise ContentExtractionError(
            "O texto da imagem está ilegível ou tem qualidade insuficiente para uma análise segura."
        )
    if len(text) > policy.maximum_text_characters:
        raise ContentExtractionError("A imagem contém texto demais; envie um recorte da alegação.")
    return text
