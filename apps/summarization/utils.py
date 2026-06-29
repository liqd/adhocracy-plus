"""Utility functions for document processing."""

import io
import json
from pathlib import Path

import fitz  # PyMuPDF
import requests
from docx import Document
from pydantic_ai.messages import BinaryContent
from pydantic_ai.messages import BinaryImage


# TODO: Deprecated ? We use only URLs now.
def read_document(doc_path: Path) -> BinaryImage | BinaryContent:
    """Read document file and return BinaryImage or BinaryContent."""
    doc_path = Path(doc_path) if not isinstance(doc_path, Path) else doc_path

    if not doc_path.exists():
        raise FileNotFoundError(f"File not found: {doc_path}")

    ext = doc_path.suffix.lower()
    media_type_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".pdf": "application/pdf",
    }
    media_type = media_type_map.get(ext, "image/jpeg")

    with open(doc_path, "rb") as f:
        file_data = f.read()

    if media_type.startswith("image/"):
        return BinaryImage(data=file_data, media_type=media_type)
    else:
        return BinaryContent(data=file_data, media_type=media_type)


def _is_image_url(url: str, image_extensions: tuple, image_keywords: tuple) -> bool:
    """Check if string is an image URL."""
    if not isinstance(url, str):
        return False
    url_lower = url.lower()
    if not (url_lower.startswith("http://") or url_lower.startswith("https://")):
        return False
    return url_lower.endswith(image_extensions) or any(
        keyword in url_lower for keyword in image_keywords
    )


# TODO: Deprecated ? Pass image_urls directly to the request ?
def _extract_from_value(
    value, urls: list, image_extensions: tuple, image_keywords: tuple
) -> None:
    """Recursively extract image URLs from JSON value."""
    if isinstance(value, str):
        if _is_image_url(value, image_extensions, image_keywords):
            urls.append(value)
    elif isinstance(value, dict):
        for key, val in value.items():
            if any(keyword in key.lower() for keyword in image_keywords):
                if isinstance(val, str) and _is_image_url(
                    val, image_extensions, image_keywords
                ):
                    urls.append(val)
            else:
                _extract_from_value(val, urls, image_extensions, image_keywords)
    elif isinstance(value, list):
        for item in value:
            _extract_from_value(item, urls, image_extensions, image_keywords)


# TODO: Deprecated ? Pass image_urls directly to the request ?
def extract_image_urls_from_json(json_data: str | dict | list) -> list[str]:
    """Extract image URLs from JSON structure."""
    urls = []
    image_extensions = (
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
        ".bmp",
        ".tiff",
        ".tif",
    )
    image_keywords = ("image", "img", "photo", "picture", "url", "src", "href")

    if isinstance(json_data, str):
        try:
            json_data = json.loads(json_data)
        except json.JSONDecodeError:
            return []

    _extract_from_value(json_data, urls, image_extensions, image_keywords)
    return list(dict.fromkeys(urls))


def download_document(url: str, timeout: int = 30) -> bytes:
    """Download document from URL and return as bytes."""
    try:
        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()
        return response.content
    except requests.Timeout:
        raise requests.RequestException(
            f"Timeout while downloading document from {url}"
        )
    except requests.RequestException as e:
        raise requests.RequestException(
            f"Failed to download document from {url}: {str(e)}"
        )


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from PDF document."""
    try:
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        text_parts = []

        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text = page.get_text()
            if text.strip():
                text_parts.append(text)

        pdf_document.close()

        if not text_parts:
            raise ValueError(
                "No text could be extracted from PDF (may be image-only or encrypted)"
            )

        return "\n\n".join(text_parts)
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")


def extract_text_from_docx(docx_bytes: bytes) -> str:
    """Extract text from DOCX document."""
    try:
        docx_file = io.BytesIO(docx_bytes)
        doc = Document(docx_file)

        text_parts = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)

        if not text_parts:
            raise ValueError("No text could be extracted from DOCX document")

        return "\n\n".join(text_parts)
    except Exception as e:
        raise ValueError(f"Failed to extract text from DOCX: {str(e)}")


def extract_text_from_document(url: str) -> str:
    """Extract text from PDF or DOCX document downloaded from URL."""
    url_lower = url.lower()
    document_bytes = download_document(url)

    if url_lower.endswith(".pdf"):
        return extract_text_from_pdf(document_bytes)
    elif url_lower.endswith(".docx"):
        return extract_text_from_docx(document_bytes)
    else:
        raise ValueError(
            "Unsupported document format. Only PDF (.pdf) and DOCX (.docx) are supported."
        )
