from dataclasses import dataclass

from immunocheck.application.content_normalizer import MultimodalNormalizer
from immunocheck.domain.models import ContentKind, ContentSubmission


@dataclass
class StubImageExtractor:
    def extract(self, submission: ContentSubmission) -> str:
        assert submission.kind is ContentKind.IMAGE
        return "texto extraído da imagem"


@dataclass
class StubLinkExtractor:
    def extract(self, url: str) -> str:
        return f"texto extraído de {url}"


def test_multimodal_normalizer_routes_all_supported_modalities() -> None:
    normalizer = MultimodalNormalizer(StubImageExtractor(), StubLinkExtractor())

    assert (
        normalizer.normalize(ContentSubmission(kind=ContentKind.TEXT, text="  texto   simples "))
        == "texto simples"
    )
    assert (
        normalizer.normalize(
            ContentSubmission(
                kind=ContentKind.IMAGE,
                data=b"image",
                media_type="image/png",
                width=10,
                height=10,
            )
        )
        == "texto extraído da imagem"
    )
    assert (
        normalizer.normalize(
            ContentSubmission(kind=ContentKind.LINK, url="https://example.org/noticia")
        )
        == "texto extraído de https://example.org/noticia"
    )
