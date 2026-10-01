import pytest

from apps.cms.pages.templatetags.block_tags import file_type
from apps.cms.pages.templatetags.block_tags import is_audio
from apps.cms.pages.templatetags.block_tags import is_video

FALLBACK = "application/octet-stream"


class _Document:
    def __init__(self, url):
        self.url = url


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://example.org/media/clip.mp4", "video/mp4"),
        ("https://example.org/media/clip.webm", "video/webm"),
        ("https://example.org/media/sound.mp3", "audio/mpeg"),
        ("https://example.org/media/sound.ogg", "audio/ogg"),
        ("https://example.org/media/sound.wav", "audio/wav"),
        ("/media/file", FALLBACK),
    ],
)
def test_file_type(url, expected):
    assert file_type(url) == expected


def test_file_type_accepts_document_objects():
    assert file_type(_Document("https://example.org/media/clip.mp4")) == "video/mp4"


def test_file_type_fallback_for_unknown_or_empty():
    assert file_type("https://example.org/media/unknown.unknownext") == FALLBACK
    assert file_type(None) == FALLBACK


def test_audio_and_video_helpers():
    assert is_audio("sound.mp3")
    assert not is_video("sound.mp3")
    assert is_video("clip.webm")
    assert not is_audio("clip.webm")
