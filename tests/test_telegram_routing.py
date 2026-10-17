from __future__ import annotations

from immunocheck.application.input_understanding import route_message
from immunocheck.domain.models import ContentKind
from immunocheck.telegram import TelegramUpdateHandler
from tests.test_telegram import Clock, StubClient, StubPipeline, png_bytes, update_with_text


def test_commented_link_stays_text_by_default_and_becomes_link_with_v2_router() -> None:
    message = "Recebi no grupo, é verdade? https://example.org/noticia"
    client = StubClient()
    legacy = StubPipeline(events=client.events)
    TelegramUpdateHandler(
        client=client, pipeline=legacy, clock=Clock([10.0, 10.1, 11.0])
    ).handle(update_with_text(message))
    assert legacy.submissions[0].kind is ContentKind.TEXT

    routed = StubPipeline(events=client.events)
    TelegramUpdateHandler(
        client=client,
        pipeline=routed,
        clock=Clock([10.0, 10.1, 11.0]),
        message_router=route_message,
    ).handle(update_with_text(message))
    assert routed.submissions[0].kind is ContentKind.LINK
    assert routed.submissions[0].url == "https://example.org/noticia"
    assert routed.submissions[0].text == "Recebi no grupo, é verdade?"


def test_image_caption_travels_with_the_downloaded_image() -> None:
    client = StubClient(file_content=png_bytes())
    pipeline = StubPipeline(events=client.events)
    handler = TelegramUpdateHandler(
        client=client, pipeline=pipeline, clock=Clock([10.0, 10.1, 11.0])
    )
    update = {
        "message": {
            "chat": {"id": 123},
            "caption": "  Isso é verdade?  ",
            "document": {
                "file_id": "image-id",
                "file_size": len(client.file_content),
                "mime_type": "image/png",
            },
        }
    }

    handler.handle(update)

    assert pipeline.submissions[0].kind is ContentKind.IMAGE
    assert pipeline.submissions[0].text == "Isso é verdade?"
