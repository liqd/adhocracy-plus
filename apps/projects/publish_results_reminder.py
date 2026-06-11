from datetime import datetime
from datetime import timedelta
from typing import Optional
from typing import Tuple

from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from . import emails as project_emails
from .models import ProjectInsight
from .utils import get_last_online_participation_end
from .utils import html_field_has_meaningful_content

SKIP_WRONG_PROJECT_TYPE = "wrong_project_type"
SKIP_IS_DRAFT = "is_draft"
SKIP_IS_ARCHIVED = "is_archived"
SKIP_ALREADY_SENT = "already_sent"
SKIP_HAS_RESULTS = "has_results"
SKIP_NO_PARTICIPATION_END = "no_participation_end"
SKIP_PARTICIPATION_NOT_ENDED = "participation_not_ended"
SKIP_BEFORE_MIN_CUTOFF = "before_min_cutoff"
SKIP_DELAY_NOT_REACHED = "delay_not_reached"

SKIP_REASON_LABELS = {
    SKIP_WRONG_PROJECT_TYPE: _("not a standard project"),
    SKIP_IS_DRAFT: _("project is still a draft"),
    SKIP_IS_ARCHIVED: _("project is archived"),
    SKIP_ALREADY_SENT: _("reminder was already sent"),
    SKIP_HAS_RESULTS: _("project results are already filled in"),
    SKIP_NO_PARTICIPATION_END: _("no ended online participation module"),
    SKIP_PARTICIPATION_NOT_ENDED: _("online participation has not ended yet"),
    SKIP_BEFORE_MIN_CUTOFF: _("last participation ended before the minimum cutoff"),
    SKIP_DELAY_NOT_REACHED: _("waiting period after participation end has not passed"),
}


def _get_project_state_skip_reason(project) -> Optional[str]:
    if project.project_type != "a4projects.Project":
        return SKIP_WRONG_PROJECT_TYPE
    if project.is_draft:
        return SKIP_IS_DRAFT
    if project.is_archived:
        return SKIP_IS_ARCHIVED

    try:
        insight = project.insight
    except ProjectInsight.DoesNotExist:
        insight = None
    if insight and insight.results_reminder_sent_at is not None:
        return SKIP_ALREADY_SENT

    if html_field_has_meaningful_content(project.result):
        return SKIP_HAS_RESULTS

    return None


def _get_reminder_settings(
    delay_hours: Optional[int],
    min_last_participation_end: Optional[datetime],
    use_settings_defaults: bool,
) -> Tuple[int, Optional[datetime]]:
    if delay_hours is None and use_settings_defaults:
        delay_hours = settings.RESULTS_PUBLISH_REMINDER_DELAY_HOURS
    if min_last_participation_end is None and use_settings_defaults:
        min_last_participation_end = getattr(
            settings,
            "RESULTS_PUBLISH_REMINDER_MIN_LAST_PARTICIPATION_END",
            None,
        )
    return delay_hours, min_last_participation_end


def _get_participation_timing_skip_reason(
    project,
    *,
    now: datetime,
    delay_hours: int,
    min_last_participation_end: Optional[datetime],
) -> Optional[str]:
    last_end = get_last_online_participation_end(project)
    if last_end is None:
        return SKIP_NO_PARTICIPATION_END
    if last_end > now:
        return SKIP_PARTICIPATION_NOT_ENDED
    if min_last_participation_end is not None and last_end < min_last_participation_end:
        return SKIP_BEFORE_MIN_CUTOFF

    threshold = last_end + timedelta(hours=delay_hours)
    if now < threshold:
        return SKIP_DELAY_NOT_REACHED

    return None


def get_publish_results_reminder_skip_reason(
    project,
    *,
    now: Optional[datetime] = None,
    delay_hours: Optional[int] = None,
    min_last_participation_end: Optional[datetime] = None,
    use_settings_defaults: bool = True,
) -> Optional[str]:
    """
    Return a skip-reason code when the project must not receive a reminder,
    or None when it is eligible under the automatic sending rules.
    """
    state_skip_reason = _get_project_state_skip_reason(project)
    if state_skip_reason is not None:
        return state_skip_reason

    now = now or timezone.now()
    delay_hours, min_last_participation_end = _get_reminder_settings(
        delay_hours,
        min_last_participation_end,
        use_settings_defaults,
    )
    return _get_participation_timing_skip_reason(
        project,
        now=now,
        delay_hours=delay_hours,
        min_last_participation_end=min_last_participation_end,
    )


def send_publish_results_reminder(
    project,
    *,
    now: Optional[datetime] = None,
    force: bool = False,
) -> Optional[str]:
    """
    Send the publish-results reminder when eligible.

    With force=True, skip all eligibility checks and do not update
    results_reminder_sent_at (for manual testing only).

    Returns a skip-reason code, or None when the e-mail was sent.
    """
    if not force:
        skip_reason = get_publish_results_reminder_skip_reason(project, now=now)
        if skip_reason:
            return skip_reason

    project_emails.NotifyInitiatorsPublishResultsEmail.send(project)

    if not force:
        now = now or timezone.now()
        insight, _ = ProjectInsight.objects.get_or_create(project=project)
        insight.results_reminder_sent_at = now
        insight.save(update_fields=["results_reminder_sent_at"])

    return None
