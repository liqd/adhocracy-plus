"""Helpers for rendering AI project summaries on project pages."""

import json
import logging

from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext as _

from adhocracy4.modules.models import Module
from apps.contrib.models import Settings

from .export_utils.core import generate_full_export
from .models import ProjectSummary
from .models import SummaryFeedback
from .pydantic_models import ProjectSummaryResponse
from .services import AIService
from .services import SummaryRequest
from .templatetags.summarization_tags import get_project_stats

logger = logging.getLogger(__name__)


def is_ai_summarisation_enabled(project) -> bool:
    """Return True when the project's organisation has AI summarisation unlocked."""
    organisation = getattr(project, "organisation", None)
    if organisation is None:
        return False
    return bool(getattr(organisation, "enable_ai_summarisation", False))


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


def build_summary_render_context(project, response, summary_obj=None, user_feedback=None):
    """Build template context for `_summary_fragment.html`."""
    timestamp = summary_obj.created_at if summary_obj else timezone.now()
    return {
        "project": project,
        "response": response,
        "summary_modules": get_summary_modules(project),
        "summary_id": summary_obj.pk if summary_obj else None,
        "summary_timestamp": timestamp,
        "summary_date_str": date_format(timestamp, "DATE_FORMAT"),
        "summary_created_at": timestamp,
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
    return render_to_string("summarization/_summary_fragment.html", context)


def render_summary_teaser(project):
    """Render the initial teaser state before a summary is generated."""
    stats = get_project_stats(project)
    return render_to_string(
        "summarization/_summary_teaser.html",
        {
            "project": project,
            "contribution_count": stats["contributions"],
            "module_count": stats["modules"],
        },
    )


def get_summary_prompt() -> str:
    """Return the configured project summary prompt."""
    prompt = Settings.get_value("project_summary_prompt")
    if prompt:
        return prompt
    return SummaryRequest.DEFAULT_PROMPT


def generate_project_summary(project, *, allow_regeneration: bool = True):
    """
    Generate or return a cached project summary.

    Returns a tuple of (ProjectSummaryResponse, ProjectSummary).
    Raises on provider/configuration errors.
    """
    export_data = generate_full_export(project)
    export_text = json.dumps(export_data, ensure_ascii=False)
    prompt = get_summary_prompt()

    service = AIService()
    response = service.project_summarize(
        project=project,
        text=export_text,
        prompt=prompt,
        result_type=ProjectSummaryResponse,
        allow_regeneration=allow_regeneration,
    )
    summary_obj = get_latest_project_summary(project)
    return response, summary_obj


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
