"""Tests for document attachment URL handling in summarization exports."""

from apps.summarization.export_utils.attachments.handlers import _make_absolute_url
from apps.summarization.export_utils.attachments.handlers import (
    collect_document_attachments,
)


def test_make_absolute_url_keeps_existing_absolute_url_with_base_url():
    media_url = (
        "https://roots-media-prod.liqd.net/uploads/Vanita/2025/08/04/"
        "Innovationswerkstatt%201_Ablaufplanung_Stand%2001-08-2025.pdf"
    )

    assert (
        _make_absolute_url(
            media_url,
            base_url="https://beteiligung-roots.org",
        )
        == media_url
    )


def test_make_absolute_url_prefixes_relative_path_with_base_url():
    assert (
        _make_absolute_url(
            "/uploads/example.pdf",
            base_url="https://beteiligung-roots.org",
        )
        == "https://beteiligung-roots.org/uploads/example.pdf"
    )


def test_collect_document_attachments_keeps_absolute_media_urls():
    export_data = {
        "project": {
            "information_attachments": [
                "https://roots-media-prod.liqd.net/uploads/example.pdf",
            ],
            "result_attachments": [],
        }
    }

    documents_dict, handle_to_source = collect_document_attachments(
        export_data,
        base_url="https://beteiligung-roots.org",
    )

    assert documents_dict == {
        "project_information_attachment_0": (
            "https://roots-media-prod.liqd.net/uploads/example.pdf"
        )
    }
    assert handle_to_source == {
        "project_information_attachment_0": "project_information",
    }
