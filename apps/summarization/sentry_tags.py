"""Sentry tags for project-scoped summarization calls."""

from __future__ import annotations

from contextvars import ContextVar

from sentry_sdk import set_tag

_current_project: ContextVar = ContextVar("sentry_project", default=None)


def set_sentry_project_tags(project) -> None:
    """Bind project tags for the current context and Sentry scope."""
    set_tag("project_id", project.id)
    set_tag("project_slug", project.slug)
    _current_project.set(project)


def ensure_sentry_project_tags() -> None:
    """Re-apply project tags before nested SDK calls (e.g. OpenAI client)."""
    project = _current_project.get()
    if project is not None:
        set_tag("project_id", project.id)
        set_tag("project_slug", project.slug)
