import json
import logging

from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View
from rules.contrib.views import PermissionRequiredMixin

from adhocracy4.projects.models import Project
from apps.contrib.mixins import StaffRequiredMixin

from .models import ProjectSummary
from .project_summary import generate_project_summary
from .project_summary import get_latest_project_summary
from .project_summary import get_user_feedback
from .project_summary import is_ai_summarisation_enabled
from .project_summary import render_summary_fragment
from .project_summary import save_summary_feedback
from .pydantic_models import ProjectSummaryResponse

logger = logging.getLogger(__name__)


class ProjectSummaryMixin(PermissionRequiredMixin, View):
    permission_required = "a4projects.view_project"

    @property
    def raise_exception(self):
        return self.request.user.is_authenticated

    def get_permission_object(self):
        return self.project

    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(
            Project,
            slug=kwargs["slug"],
            organisation__slug=kwargs["organisation_slug"],
        )
        if not is_ai_summarisation_enabled(self.project):
            return JsonResponse(
                {"error": _("AI summarisation is not enabled for this organisation.")},
                status=403,
            )
        return super().dispatch(request, *args, **kwargs)


class ProjectSummaryView(ProjectSummaryMixin, View):
    """Generate or return a cached AI summary for a project."""

    def get(self, request, *args, **kwargs):
        summary_obj = get_latest_project_summary(self.project)
        if not summary_obj:
            return JsonResponse({"has_summary": False})

        response = ProjectSummaryResponse(**summary_obj.response_data)
        user_feedback = get_user_feedback(
            summary_obj,
            request.user,
            request.session.session_key,
        )
        html = render_summary_fragment(
            project=self.project,
            response=response,
            summary_obj=summary_obj,
            user_feedback=user_feedback,
        )
        return JsonResponse(
            {
                "has_summary": True,
                "html": html,
                "summary_id": summary_obj.pk,
            }
        )

    def post(self, request, *args, **kwargs):
        """Return the cached summary only; regeneration is handled by Celery Beat."""
        try:
            response, summary_obj = generate_project_summary(
                self.project,
                allow_regeneration=False,
            )
        except Exception:
            logger.exception("Failed to load summary for project %s", self.project.pk)
            return JsonResponse(
                {"error": _("Summary could not be loaded. Please try again later.")},
                status=500,
            )

        if not summary_obj:
            return JsonResponse({"has_summary": False})

        user_feedback = get_user_feedback(
            summary_obj,
            request.user,
            request.session.session_key,
        )
        html = render_summary_fragment(
            project=self.project,
            response=response,
            summary_obj=summary_obj,
            user_feedback=user_feedback,
        )
        return JsonResponse(
            {
                "has_summary": True,
                "html": html,
                "summary_id": summary_obj.pk if summary_obj else None,
            }
        )


class ProjectSummaryFeedbackView(ProjectSummaryMixin, View):
    """Store user feedback for a project summary."""

    def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return HttpResponseBadRequest(_("Invalid request body."))

        summary_id = payload.get("summary_id")
        feedback_value = payload.get("feedback")

        if feedback_value not in ("positive", "negative"):
            return HttpResponseBadRequest(_("Invalid feedback value."))

        summary = get_object_or_404(
            ProjectSummary,
            pk=summary_id,
            project=self.project,
        )

        if not request.session.session_key:
            request.session.create()

        try:
            save_summary_feedback(
                summary=summary,
                user=request.user,
                session_key=request.session.session_key,
                feedback_value=feedback_value,
            )
        except ValueError as exc:
            return HttpResponseBadRequest(str(exc))

        return JsonResponse({"status": "ok", "feedback": feedback_value})


class ProjectSummaryGenerateView(StaffRequiredMixin, View):
    """
    Hidden staff-only URL to force-generate a summary for one project.

    Not linked from anywhere in the UI; visit per project, e.g.
    /{organisation_slug}/projects/{slug}/summary/generate/
    """

    def get(self, request, organisation_slug, slug):
        project = get_object_or_404(
            Project.objects.select_related("organisation"),
            slug=slug,
            organisation__slug=organisation_slug,
        )
        detail_url = reverse(
            "project-detail",
            kwargs={"organisation_slug": organisation_slug, "slug": slug},
        )

        if not is_ai_summarisation_enabled(project):
            messages.error(
                request,
                _("AI summarisation is not enabled for this organisation."),
            )
            return redirect(detail_url)

        try:
            generate_project_summary(
                project,
                allow_regeneration=True,
                force_regeneration=True,
            )
        except Exception:
            logger.exception(
                "Failed to force-generate summary for project %s", project.pk
            )
            messages.error(
                request,
                _("Summary generation failed. Please try again later."),
            )
            return redirect(detail_url)

        messages.success(request, _("AI summary generated successfully."))
        return redirect(detail_url)
