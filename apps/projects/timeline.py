"""Timeline grouping and display helpers for the project detail participation section."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from datetime import datetime
from typing import TYPE_CHECKING

from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from adhocracy4.modules.models import Module
    from adhocracy4.projects.models import Project

STATUS_FINISHED = "finished"
STATUS_RUNNING = "running"
STATUS_UPCOMING = "upcoming"

_STATUS_LABELS = {
    STATUS_FINISHED: _("Finished"),
    STATUS_RUNNING: _("Running"),
    STATUS_UPCOMING: _("Upcoming"),
}


@dataclass(frozen=True)
class ParticipationTimelineGroup:
    """Modules on the timeline that share a start day and schedule status."""

    group_date: date
    status: str
    status_label: str
    modules: tuple[Module, ...]


def module_participation_status(module: Module) -> tuple[str, str]:
    """Return (status key, translated label) for one module."""
    if module.module_has_finished:
        return STATUS_FINISHED, _STATUS_LABELS[STATUS_FINISHED]
    if module.module_has_started and not module.module_has_finished:
        return STATUS_RUNNING, _STATUS_LABELS[STATUS_RUNNING]
    if module.module_in_future:
        return STATUS_UPCOMING, _STATUS_LABELS[STATUS_UPCOMING]
    return STATUS_UPCOMING, _STATUS_LABELS[STATUS_UPCOMING]


participation_timeline_status = module_participation_status


def module_date_range(module: Module) -> str:
    """Formatted module schedule for timeline rows (e.g. 15.02.26 or 15.02.26-01.06.2026)."""
    start, end = _module_schedule(module)
    if start is None:
        return ""
    return _format_date_range(start, end)


def module_cta_label(module: Module) -> str:
    """Primary action label for a module on the participation timeline."""
    status, _label = module_participation_status(module)
    if status == STATUS_FINISHED:
        return _("Read results")
    if status == STATUS_RUNNING:
        return _("Participate")
    return _("Read")


def build_participation_grid_modules(project: Project) -> list[Module]:
    """Published modules for the grid view (project module ordering)."""
    return list(project.published_modules)


def build_participation_timeline_groups(
    project: Project,
) -> list[ParticipationTimelineGroup]:
    """Group published modules with phases for the timeline view."""
    participations = (
        project.module_set.filter(is_draft=False)
        .annotate_module_start()
        .annotate_module_end()
        .order_by("module_start", "weight")
    )

    grouped: dict[tuple[date, str], list[Module]] = defaultdict(list)

    for module in participations:
        start, _end = _module_schedule(module)
        if start is None:
            continue
        status, _ = module_participation_status(module)
        grouped[(timezone.localdate(start), status)].append(module)

    groups: list[ParticipationTimelineGroup] = []
    for (group_date, status), modules in sorted(
        grouped.items(), key=lambda item: (item[0][0], _status_sort_key(item[0][1]))
    ):
        groups.append(
            ParticipationTimelineGroup(
                group_date=group_date,
                status=status,
                status_label=_STATUS_LABELS[status],
                modules=tuple(modules),
            )
        )
    return groups


def _status_sort_key(status: str) -> int:
    order = {STATUS_FINISHED: 0, STATUS_RUNNING: 1, STATUS_UPCOMING: 2}
    return order.get(status, 3)


def _module_schedule(module: Module) -> tuple[datetime | None, datetime | None]:
    if not module.phase_set.exists():
        return None, None
    try:
        return module.module_start, module.module_end
    except AttributeError:
        return None, None


def _format_date(value: datetime) -> str:
    return date_format(timezone.localtime(value), "d.m.Y", use_l10n=True)


def _format_date_range(start: datetime, end: datetime | None) -> str:
    start_label = _format_date(start)
    if end is None:
        return start_label
    end_local = timezone.localtime(end)
    start_local = timezone.localtime(start)
    if start_local.date() == end_local.date():
        return start_label
    return f"{start_label}-{_format_date(end)}"
