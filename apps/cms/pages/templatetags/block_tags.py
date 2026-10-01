import mimetypes
from urllib.parse import urlparse

from django import template

register = template.Library()

FALLBACK_MIME_TYPE = "application/octet-stream"

# Make the detection independent of the host's mimetypes database.
_KNOWN_MEDIA_TYPES = {
    "video/webm": ".webm",
    "video/mp4": ".mp4",
    "audio/mpeg": ".mp3",
    "audio/ogg": ".ogg",
    "audio/wav": ".wav",
}
for _mime_type, _extension in _KNOWN_MEDIA_TYPES.items():
    mimetypes.add_type(_mime_type, _extension)


@register.filter
def file_type(value):
    """Return a valid MIME type for a file/document or URL.

    Unknown extensions fall back to ``application/octet-stream`` so the emitted
    ``<source type>`` attribute always stays a valid MIME type.
    """
    if not value:
        return FALLBACK_MIME_TYPE

    url = getattr(value, "url", value)
    path = urlparse(str(url)).path
    mime_type, _ = mimetypes.guess_type(path)
    return mime_type or FALLBACK_MIME_TYPE


@register.filter
def is_audio(value):
    return file_type(value).startswith("audio/")


@register.filter
def is_video(value):
    return file_type(value).startswith("video/")
