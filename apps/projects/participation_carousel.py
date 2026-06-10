"""Participation timeline carousel helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.urls import reverse

if TYPE_CHECKING:
    from adhocracy4.modules.models import Module
    from adhocracy4.projects.models import Project


def participation_carousel_slide_url(project: Project, date: dict) -> str:
    """Return the detail URL for one participation carousel slide."""
    if date.get("type") == "module":
        module: Module = date["modules"][0]
        return module.get_absolute_url()
    return reverse(
        "a4_candy_offlineevents:offlineevent-detail",
        kwargs={
            "organisation_slug": project.organisation.slug,
            "slug": date["slug"],
        },
    )


def legacy_initial_slide_redirect(project: Project, initial_slide: str | None) -> str | None:
    """Map legacy ``?initialSlide=`` project URLs to module or event detail pages."""
    if initial_slide is None:
        return None
    digits = "".join(character for character in str(initial_slide) if character.isdigit())
    if not digits:
        return None
    index = int(digits)
    dates = project.participation_dates
    if index < 0 or index >= len(dates):
        return None
    return participation_carousel_slide_url(project, dates[index])
