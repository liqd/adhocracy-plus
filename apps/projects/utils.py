import json
import logging
import re
from datetime import datetime
from datetime import timedelta
from typing import List
from typing import Optional

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.html import strip_tags
from django.utils.translation import gettext as _
from sentry_sdk import capture_exception

from adhocracy4.modules.models import Module
from apps.contrib.models import Settings
from apps.summarization.export_utils.attachments.handlers import (
    collect_document_attachments,
)
from apps.summarization.export_utils.attachments.handlers import (
    integrate_document_summaries,
)
from apps.summarization.export_utils.core import generate_full_export
from apps.summarization.models import ProjectSummary
from apps.summarization.models import SummaryFeedback
from apps.summarization.pydantic_models import ProjectSummaryResponse
from apps.summarization.sentry_tags import set_sentry_project_tags
from apps.summarization.services import AIService
from apps.summarization.services import SummaryRequest

logger = logging.getLogger(__name__)


def html_field_has_meaningful_content(value: Optional[str]) -> bool:
    """True if a CKEditor/HTML field has non-whitespace text."""
    if not value:
        return False
    text = strip_tags(value)
    text = re.sub(r"&nbsp;|\s", "", text)
    return len(text) > 0


def project_has_result_content(project) -> bool:
    return html_field_has_meaningful_content(project.result)


def get_last_online_participation_end(project) -> Optional[datetime]:
    """
    Latest phase end among non-draft modules.
    None if there is no such module or no dated phases.
    """
    end_candidates: List[datetime] = []
    for module in project.module_set.all():
        if module.is_draft:
            continue
        phase_ends = [
            p.end_date for p in module.phase_set.all() if p.end_date is not None
        ]
        if not phase_ends:
            continue
        end_candidates.append(max(phase_ends))
    if not end_candidates:
        return None
    return max(end_candidates)


def is_ai_summarisation_enabled(project) -> bool:
    """Return True when the project's organisation has AI summarisation unlocked."""
    organisation = getattr(project, "organisation", None)
    if organisation is None:
        return False
    return bool(getattr(organisation, "enable_ai_summarisation", False))


def is_ai_image_summarisation_enabled() -> bool:
    """Return True when image attachments should be included in AI summarisation."""
    return Settings.get_value("project_summary_include_images") == "true"


def get_summary_modules(project):
    """Modules annotated with start/end dates for summary templates."""
    return (
        Module.objects.filter(project=project, is_draft=False)
        .annotate_module_start()
        .annotate_module_end()
    )


def get_latest_project_summary(project):
    """Return the most recent cached summary for a project, if any."""
    return (
        ProjectSummary.objects.filter(project=project).order_by("-created_at").first()
    )


def get_user_feedback(summary, user, session_key):
    """Return the current user's feedback value for a summary, if any."""
    if not summary:
        return None

    if user.is_authenticated:
        feedback = summary.feedback.filter(user=user).first()
    elif session_key:
        feedback = summary.feedback.filter(session_key=session_key).first()
    else:
        return None

    return feedback.feedback if feedback else None


def build_summary_render_context(
    project, response, summary_obj=None, user_feedback=None
):
    """Build template context for `_summary_fragment.html`."""
    timestamp = None
    summary_date_str = None
    if summary_obj:
        timestamp = timezone.localtime(
            summary_obj.last_checked_at or summary_obj.created_at
        )
        summary_date_str = date_format(timestamp, "DATE_FORMAT")

    return {
        "project": project,
        "response": response,
        "summary_modules": get_summary_modules(project),
        "summary_id": summary_obj.pk if summary_obj else None,
        "summary_timestamp": timestamp,
        "summary_date_str": summary_date_str,
        "summary_created_at": summary_obj.created_at if summary_obj else None,
        "user_feedback": user_feedback,
        "show_debug": False,
    }


def render_summary_fragment(project, response, summary_obj=None, user_feedback=None):
    """Render the summary accordion HTML."""
    context = build_summary_render_context(
        project=project,
        response=response,
        summary_obj=summary_obj,
        user_feedback=user_feedback,
    )
    return render_to_string("a4_candy_projects/_summary_fragment.html", context)


def get_summary_prompt() -> str:
    """Return the configured project summary prompt."""
    prompt = Settings.get_value("project_summary_prompt")
    if prompt:
        return prompt
    return SummaryRequest.DEFAULT_PROMPT


def get_auto_refresh_max_age_minutes() -> int:
    """Return max summary age before the periodic Celery job regenerates."""
    try:
        return Settings.get_int("project_summary_auto_refresh_max_age_minutes")
    except (KeyError, TypeError, ValueError):
        return getattr(settings, "PROJECT_SUMMARY_AUTO_REFRESH_MAX_AGE_MINUTES", 720)


def get_auto_refresh_max_projects_per_run() -> int:
    """Return max projects to refresh per beat run (0 = no limit)."""
    return getattr(settings, "PROJECT_SUMMARY_AUTO_REFRESH_MAX_PROJECTS_PER_RUN", 0)


def project_needs_summary_refresh(project) -> bool:
    """
    Return True when Beat should enqueue a summary task for this project.

    Only missing summary or age beyond max_age; hash comparison happens later
    inside AIService.project_summarize when the task runs.
    """
    latest = get_latest_project_summary(project)
    if not latest:
        return True

    max_age = timedelta(minutes=get_auto_refresh_max_age_minutes())
    return timezone.now() - latest.created_at > max_age


def generate_project_summary(
    project,
    request=None,
    base_url=None,
    *,
    allow_regeneration=True,
    force_regeneration=False,
):
    """
    Generate AI summary for a project. Used by views and periodic Celery tasks.

    Returns:
        ProjectSummaryResponse from the AI service, or None when regeneration is
        disabled and no cached summary exists.

    Raises:
        Exception: Re-raises provider/configuration errors.
    """
    set_sentry_project_tags(project)

    export_data = generate_full_export(project)

    if request is not None or base_url:
        documents_dict, handle_to_source = collect_document_attachments(
            export_data, request=request, base_url=base_url
        )
        if documents_dict:
            try:
                service = AIService()
                document_response = service.request_vision_dict(
                    documents_dict=documents_dict,
                    project=project,
                    include_images=is_ai_image_summarisation_enabled(),
                )
                integrate_document_summaries(
                    export_data,
                    document_response.documents,
                    handle_to_source,
                )
            except Exception as exc:
                logger.error(
                    "Failed to summarize documents for project %s: %s",
                    project.slug,
                    exc,
                    exc_info=True,
                )
                capture_exception(exc)

    json_text = json.dumps(export_data, ensure_ascii=False)
    prompt = get_summary_prompt()
    service = AIService()
    return service.project_summarize(
        project=project,
        text=json_text,
        prompt=prompt,
        result_type=ProjectSummaryResponse,
        allow_regeneration=allow_regeneration,
        is_rate_limit=not force_regeneration,
        force_regeneration=force_regeneration,
    )


def save_summary_feedback(summary, user, session_key, feedback_value):
    """Create or update feedback for a summary."""
    if user.is_authenticated:
        SummaryFeedback.objects.update_or_create(
            summary=summary,
            user=user,
            defaults={"feedback": feedback_value, "session_key": None},
        )
    elif session_key:
        SummaryFeedback.objects.update_or_create(
            summary=summary,
            session_key=session_key,
            defaults={"feedback": feedback_value, "user": None},
        )
    else:
        raise ValueError(_("Session required for anonymous feedback."))
