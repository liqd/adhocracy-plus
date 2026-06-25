"""Rich error formatting for AI summarization test playground (staff debugging)."""

from __future__ import annotations

from collections import deque
from typing import Any


def format_playground_exception(exc: BaseException, *, max_related: int = 16) -> str:
    """
    Build a multi-line, human-readable error for the summarization test UIs.

    Works for any exception type. Adds optional Pydantic validation details when present.
    """
    lines: list[str] = []

    def append_block(title: str, body: str) -> None:
        if lines:
            lines.append("")
        lines.append(f"=== {title} ===")
        lines.append(body.strip() if body else "(keine Meldung)")

    append_block("Hauptfehler", f"{type(exc).__name__}: {exc}")

    related = _collect_related_exceptions(exc, max_total=max_related)
    if related:
        parts = []
        for i, link in enumerate(related, start=1):
            parts.append(f"[{i}] {type(link).__name__}: {link}")
        append_block("Verknüpfte Fehler (Ursache / Kontext / Gruppe)", "\n".join(parts))

    pydantic_bits = _collect_pydantic_error_details(exc)
    if pydantic_bits:
        append_block("Validierungsdetails", "\n".join(pydantic_bits))

    return "\n".join(lines)


def _collect_related_exceptions(root: BaseException, *, max_total: int) -> list[BaseException]:
    """
    All exceptions reachable via __cause__, __context__, and ExceptionGroup.subexceptions.

    Excludes `root` (already shown as Hauptfehler). Order: BFS, no duplicates.
    """
    out: list[BaseException] = []
    seen: set[int] = set()
    q: deque[BaseException] = deque()
    seen.add(id(root))

    def enqueue(e: BaseException | None) -> None:
        if e is None or id(e) in seen:
            return
        seen.add(id(e))
        q.append(e)

    enqueue(getattr(root, "__cause__", None))
    enqueue(getattr(root, "__context__", None))
    _enqueue_exception_group_children(root, enqueue)

    while q and len(out) < max_total:
        cur = q.popleft()
        out.append(cur)
        enqueue(getattr(cur, "__cause__", None))
        enqueue(getattr(cur, "__context__", None))
        _enqueue_exception_group_children(cur, enqueue)

    return out


def _enqueue_exception_group_children(exc: BaseException, enqueue: Any) -> None:
    subs = getattr(exc, "exceptions", None)
    if not subs:
        return
    if type(exc).__name__ not in ("ExceptionGroup", "BaseExceptionGroup"):
        return
    for sub in subs:
        if isinstance(sub, BaseException):
            enqueue(sub)


def _collect_pydantic_error_details(exc: BaseException, *, max_errors: int = 12) -> list[str]:
    """Extract pydantic v2 ValidationError.errors() entries from an exception chain."""
    out: list[str] = []
    seen: set[int] = set()
    stack: list[BaseException] = [exc]

    while stack:
        cur = stack.pop()
        cid = id(cur)
        if cid in seen:
            continue
        seen.add(cid)

        err_fn = getattr(cur, "errors", None)
        if callable(err_fn):
            try:
                raw = err_fn()
            except Exception:
                raw = None
            if isinstance(raw, list) and raw:
                for item in raw[:max_errors]:
                    out.append(_format_one_pydantic_error(item))
                if len(raw) > max_errors:
                    out.append(f"... und {len(raw) - max_errors} weitere Fehler")
                return out

        for nxt in (getattr(cur, "__cause__", None), getattr(cur, "__context__", None)):
            if isinstance(nxt, BaseException):
                stack.append(nxt)

    return out


def _format_one_pydantic_error(item: Any) -> str:
    if not isinstance(item, dict):
        return str(item)
    loc = item.get("loc")
    loc_s = ".".join(str(x) for x in loc) if isinstance(loc, tuple) else str(loc)
    msg = item.get("msg", "")
    typ = item.get("type", "")
    parts = [f"• {loc_s or '(root)'}: {msg}"]
    if typ:
        parts.append(f"  (Typ: {typ})")
    inp = item.get("input")
    if inp is not None:
        snippet = _shorten_for_display(inp, limit=400)
        parts.append(f"  Eingabe-Ausschnitt: {snippet!r}")
    return "\n".join(parts)


def _shorten_for_display(s: Any, *, limit: int) -> str:
    text = s if isinstance(s, str) else repr(s)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."
