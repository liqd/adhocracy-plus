"""Tests for LLM JSON extraction (no DB)."""

from apps.summarization.llm_json import extract_llm_json_payload


def test_extract_llm_json_payload_strips_leading_prose_around_broken_json():
    """Leading prose and trailing text; inner part from first ``{`` (strict JSON may still be invalid)."""
    raw = (
        "Ich verstehe. Lassen Sie mich das JSON direkt ausgeben:\n\n"
        '{"title": "x", "broken": true,}'  # trailing comma: invalid for strict json.loads
        "\n\nDanke für Ihre Geduld."
    )
    out = extract_llm_json_payload(raw)
    assert not out.startswith("Ich verstehe")
    assert out.startswith("{")
    assert '"title"' in out
    assert "Danke" in out  # extract keeps rest of string after the object


def test_extract_llm_json_payload_fenced_json_block():
    """Markdown ```json fence: inner content is used."""
    raw = """Here you go:

```json
{"a": 1, "b": [2, 3]}
```

End.
"""
    out = extract_llm_json_payload(raw)
    assert out.startswith("{")
    assert '"a"' in out


def test_extract_llm_json_payload_empty_input():
    assert extract_llm_json_payload("") == ""
    assert extract_llm_json_payload("   ") == ""
