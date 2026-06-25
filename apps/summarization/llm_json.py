"""Extract and parse JSON from LLM text (strip wrappers, repair, validate as Pydantic)."""

from __future__ import annotations

import re
from typing import Any

import json_repair
from pydantic import BaseModel

_FENCED_JSON = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.IGNORECASE)


def extract_llm_json_payload(text: str) -> str:
    """
    Remove surrounding prose and markdown fences so the remainder is JSON-like.

    - Strips ```json ... ``` (or ``` ... ```) blocks if present.
    - Drops any leading characters before the first ``{`` or ``[``.
    """
    s = (text or "").strip()
    if not s:
        return s

    m = _FENCED_JSON.search(s)
    if m:
        s = m.group(1).strip()

    for i, ch in enumerate(s):
        if ch in "{[":
            return s[i:].strip()

    return s


def parse_structured_llm_json(raw_text: str, result_type: type[BaseModel]) -> BaseModel:
    """Strip wrappers, repair with json_repair, validate to ``result_type``."""
    payload = extract_llm_json_payload(raw_text)
    data: Any = json_repair.loads(payload)
    return result_type.model_validate(data)
