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
    from apps.offlineevents.models import OfflineEvent

STATUS_FINISHED = "finished"
STATUS_RUNNING = "running"
STATUS_UPCOMING = "upcoming"

_STATUS_LABELS = {
    STATUS_FINISHED: _("Finished"),
    STATUS_RUNNING: _("Running"),
    STATUS_UPCOMING: _("Upcoming"),
}


@dataclass(frozen=True)
class ParticipationTimelineItem:
    """One row on the participation timeline (module or offline event)."""

    module: Module | None = None
    offline_event: OfflineEvent | None = None

    def sort_datetime(self) -> datetime:
        if self.module is not None:
            start, _end = _module_schedule(self.module)
            if start is not None:
                return start
        if self.offline_event is not None:
            return self.offline_event.date
        return timezone.now()


@dataclass(frozen=True)
class ParticipationTimelineGroup:
    """Timeline items that share a schedule status (one header per status)."""

    group_date: date
    status: str
    status_label: str
    items: tuple[ParticipationTimelineItem, ...]


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


def offline_event_participation_status(event: OfflineEvent) -> tuple[str, str]:
    """Return (status key, translated label) for one offline event."""
    if event.date <= timezone.now():
        return STATUS_FINISHED, _STATUS_LABELS[STATUS_FINISHED]
    return STATUS_UPCOMING, _STATUS_LABELS[STATUS_UPCOMING]


def module_date_range(module: Module) -> str:
    """Formatted module schedule for timeline rows (e.g. 15.02.26 or 15.02.26-01.06.2026)."""
    start, end = _module_schedule(module)
    if start is None:
        return ""
    return _format_date_range(start, end)


def offline_event_date_label(event: OfflineEvent) -> str:
    """Formatted event date for timeline rows."""
    return _format_date(event.date)


def module_cta_label(module: Module) -> str:
    """Primary action label for a module on the participation timeline."""
    status, _label = module_participation_status(module)
    if status == STATUS_FINISHED:
        return _("See contributions")
    if status == STATUS_RUNNING:
        return _("Participate")
    return _("Read")


def offline_event_cta_label(event: OfflineEvent) -> str:
    """Primary action label for an offline event on the participation timeline."""
    status, _label = offline_event_participation_status(event)
    if status == STATUS_FINISHED:
        return _("Read")
    return _("Read")


def build_participation_grid_modules(project: Project) -> list[Module]:
    """Published modules for the grid view, ordered like the timeline."""
    ordered: list[Module] = []
    scheduled: set[Module] = set()
    for group in build_participation_timeline_groups(project):
        for item in group.items:
            if item.module is not None:
                ordered.append(item.module)
                scheduled.add(item.module)
    for module in project.published_modules:
        if module not in scheduled:
            ordered.append(module)
    return ordered


def build_participation_timeline_groups(
    project: Project,
) -> list[ParticipationTimelineGroup]:
    """Group published modules and offline events by status for the timeline view."""
    participations = (
        project.module_set.filter(is_draft=False)
        .annotate_module_start()
        .annotate_module_end()
        .order_by("module_start", "weight")
    )

    grouped: dict[str, list[ParticipationTimelineItem]] = defaultdict(list)

    for module in participations:
        start, _end = _module_schedule(module)
        if start is None:
            continue
        status, _ = module_participation_status(module)
        grouped[status].append(
            ParticipationTimelineItem(module=module, offline_event=None)
        )

    for event in project.events.all():
        status, _ = offline_event_participation_status(event)
        grouped[status].append(
            ParticipationTimelineItem(module=None, offline_event=event)
        )

    groups: list[ParticipationTimelineGroup] = []
    for status in (STATUS_FINISHED, STATUS_RUNNING, STATUS_UPCOMING):
        items = grouped.get(status)
        if not items:
            continue
        items = sorted(items, key=lambda item: item.sort_datetime())
        first_date = timezone.localdate(items[0].sort_datetime())
        groups.append(
            ParticipationTimelineGroup(
                group_date=first_date,
                status=status,
                status_label=_STATUS_LABELS[status],
                items=tuple(items),
            )
        )
    return groups


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
