import itertools
import logging

from allauth.account.adapter import get_adapter
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext
from django.views import View
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from rules.contrib.views import LoginRequiredMixin
from rules.contrib.views import PermissionRequiredMixin
from sentry_sdk import capture_exception

from adhocracy4.dashboard import mixins as a4dashboard_mixins
from adhocracy4.dashboard import signals as a4dashboard_signals
from adhocracy4.dashboard.components.forms.views import ProjectComponentFormView
from adhocracy4.modules import models as module_models
from adhocracy4.projects import models as project_models
from adhocracy4.projects.mixins import DisplayProjectOrModuleMixin
from adhocracy4.projects.mixins import PhaseDispatchMixin
from adhocracy4.projects.mixins import ProjectMixin
from apps.contrib.mixins import StaffRequiredMixin
from apps.projects.models import ProjectInsight
from apps.summarization.models import ProjectSummary
from apps.summarization.models import SummaryFeedback
from apps.summarization.pydantic_models import ProjectSummaryResponse

from . import dashboard
from . import forms
from . import models
from .participation_carousel import legacy_initial_slide_redirect
from .timeline import build_participation_grid_modules
from .timeline import build_participation_timeline_groups
from .utils import generate_project_summary
from .utils import get_latest_project_summary
from .utils import get_summary_modules
from .utils import get_user_feedback
from .utils import is_ai_summarisation_enabled
from .utils import project_has_result_content
from .utils import render_summary_fragment

User = get_user_model()
logger = logging.getLogger(__name__)


class ParticipantInviteDetailView(generic.DetailView):
    model = models.ParticipantInvite
    slug_field = "token"
    slug_url_kwarg = "invite_token"

    def dispatch(self, request, invite_token, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(
                "project-participant-invite-update",
                organisation_slug=self.get_object().project.organisation.slug,
                invite_token=invite_token,
            )
        else:
            invite = self.get_object()
            get_adapter().stash_verified_email(request, invite.email)
            return super().dispatch(request, *args, **kwargs)


class ParticipantInviteUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.ParticipantInvite
    form_class = forms.ParticipantInviteForm
    slug_field = "token"
    slug_url_kwarg = "invite_token"

    def form_valid(self, form):
        if form.is_accepted():
            form.instance.accept(self.request.user)
            return redirect(form.instance.project.get_absolute_url())
        else:
            form.instance.reject()
            return redirect("/")


class ModeratorInviteDetailView(generic.DetailView):
    model = models.ModeratorInvite
    slug_field = "token"
    slug_url_kwarg = "invite_token"

    def dispatch(self, request, invite_token, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(
                "project-moderator-invite-update",
                organisation_slug=self.get_object().project.organisation.slug,
                invite_token=invite_token,
            )
        else:
            return super().dispatch(request, *args, **kwargs)


class ModeratorInviteUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.ModeratorInvite
    form_class = forms.ModeratorInviteForm
    slug_field = "token"
    slug_url_kwarg = "invite_token"

    def form_valid(self, form):
        if form.is_accepted():
            form.instance.accept(self.request.user)
            return redirect(form.instance.project.get_absolute_url())
        else:
            form.instance.reject()
            return redirect("/")


class AbstractProjectUserInviteListView(
    ProjectMixin,
    a4dashboard_mixins.DashboardBaseMixin,
    a4dashboard_mixins.DashboardComponentMixin,
    generic.base.TemplateResponseMixin,
    generic.edit.FormMixin,
    generic.detail.SingleObjectMixin,
    generic.edit.ProcessFormView,
):
    form_class = forms.InviteUsersFromEmailForm
    invite_model = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if "submit_action" in request.POST:
            if request.POST["submit_action"] == "remove_user":
                pk = int(request.POST["user_pk"])
                user = get_object_or_404(User, pk=pk)
                related_users = getattr(self.object, self.related_users_field)
                related_users.remove(user)
                messages.success(request, self.success_message_removal)
            elif request.POST["submit_action"] == "remove_invite":
                pk = int(request.POST["invite_pk"])
                if self.invite_model.objects.filter(pk=pk).exists():
                    invite = self.invite_model.objects.get(pk=pk)
                    invite.delete()
                    messages.success(request, _("Invitation succesfully removed."))
                else:
                    messages.info(
                        request, _("Invitation was already accepted or removed.")
                    )

            response = redirect(self.get_success_url())
        else:
            response = super().post(request, *args, **kwargs)

        self._send_component_updated_signal()
        return response

    def filter_existing(self, emails):
        related_users = getattr(self.object, self.related_users_field)
        related_emails = [u.email for u in related_users.all()]
        existing = []
        filtered_emails = []
        for email in emails:
            if email in related_emails:
                existing.append(email)
            else:
                filtered_emails.append(email)
        return filtered_emails, existing

    def filter_pending(self, emails):
        pending = []
        filtered_emails = []
        for email in emails:
            if self.invite_model.objects.filter(
                email=email, project=self.project
            ).exists():
                pending.append(email)
            else:
                filtered_emails.append(email)
        return filtered_emails, pending

    def form_valid(self, form):
        emails = list(
            set(
                itertools.chain(
                    form.cleaned_data["add_users"],
                    form.cleaned_data["add_users_upload"],
                )
            )
        )

        emails, existing = self.filter_existing(emails)
        if existing:
            messages.error(
                self.request,
                _("Following users already accepted an invitation: ")
                + ", ".join(existing),
            )

        emails, pending = self.filter_pending(emails)
        if pending:
            messages.error(
                self.request,
                _("Following users are already invited: ") + ", ".join(pending),
            )

        for email in emails:
            self.invite_model.objects.invite(
                creator=self.request.user,
                project=self.project,
                email=email,
                site=get_current_site(self.request),
            )

        messages.success(
            self.request,
            ngettext(
                self.success_message[0], self.success_message[1], len(emails)
            ).format(len(emails)),
        )

        return redirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["labels"] = (self.add_user_field_label, self.add_user_upload_field_label)
        return kwargs

    def _send_component_updated_signal(self):
        a4dashboard_signals.project_component_updated.send(
            sender=self.component.__class__,
            project=self.project,
            component=self.component,
            user=self.request.user,
        )


class DashboardProjectModeratorsView(AbstractProjectUserInviteListView):
    model = project_models.Project
    slug_url_kwarg = "project_slug"
    template_name = "a4_candy_projects/project_moderators.html"
    permission_required = "a4projects.change_project"
    menu_item = "project"

    related_users_field = "moderators"
    add_user_field_label = _("Invite moderators via email")
    add_user_upload_field_label = _("Invite moderators via file upload")
    success_message = (_("{} moderator invited."), _("{} moderators invited."))
    success_message_removal = _("Moderator successfully removed.")

    invite_model = models.ModeratorInvite

    def get_permission_object(self):
        return self.project


class DashboardProjectParticipantsView(AbstractProjectUserInviteListView):
    model = project_models.Project
    slug_url_kwarg = "project_slug"
    template_name = "a4_candy_projects/project_participants.html"
    permission_required = "a4projects.change_project"
    menu_item = "project"

    related_users_field = "participants"
    add_user_field_label = _("Invite users via email")
    add_user_upload_field_label = _("Invite users via file upload")
    success_message = (_("{} participant invited."), _("{} participants invited."))
    success_message_removal = _("Participant successfully removed.")

    invite_model = models.ParticipantInvite

    def get_permission_object(self):
        return self.project


class ProjectDeleteView(PermissionRequiredMixin, generic.DeleteView):
    model = project_models.Project
    permission_required = "a4projects.delete_project"
    http_method_names = ["post"]
    success_message = _("Project '%(name)s' was deleted successfully.")

    def get_success_url(self):
        return reverse_lazy(
            "a4dashboard:project-list",
            kwargs={"organisation_slug": self.get_object().organisation.slug},
        )

    def form_valid(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super().form_valid(request, *args, **kwargs)


class ProjectInformationView(
    PermissionRequiredMixin,
    ProjectMixin,
    generic.DetailView,
):
    model = project_models.Project
    permission_required = "a4projects.view_project"
    template_name = "a4_candy_projects/project_information.html"
    slug_url_kwarg = "slug"
    project_url_kwarg = "slug"
    get_context_from_object = True

    def get_permission_object(self):
        return self.project

    @property
    def raise_exception(self):
        return self.request.user.is_authenticated


class ProjectResultsView(
    PermissionRequiredMixin,
    ProjectMixin,
    generic.DetailView,
):
    model = project_models.Project
    permission_required = "a4projects.view_project"
    template_name = "a4_candy_projects/project_results.html"
    slug_url_kwarg = "slug"
    project_url_kwarg = "slug"
    get_context_from_object = True

    def get_permission_object(self):
        return self.project

    @property
    def raise_exception(self):
        return self.request.user.is_authenticated

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        insight, _ = ProjectInsight.objects.get_or_create(project=self.object)
        if not insight.display and not project_has_result_content(self.object):
            return HttpResponseRedirect(self.object.get_absolute_url())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ProjectInsight.update_context(self.project, context)
        return context


class ProjectDetailView(
    PermissionRequiredMixin,
    DisplayProjectOrModuleMixin,
    generic.DetailView,
):
    """Project overview (intro, participation grid, events, insights)."""

    model = models.Project
    permission_required = "a4projects.view_project"
    template_name = "a4_candy_projects/project_detail.html"

    @cached_property
    def project(self):
        return self.get_object()

    def get_permission_object(self):
        return self.project

    @property
    def raise_exception(self):
        return self.request.user.is_authenticated

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        redirect_url = legacy_initial_slide_redirect(
            self.object, request.GET.get("initialSlide")
        )
        if redirect_url is not None:
            return HttpResponseRedirect(redirect_url)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["participation_grid_modules"] = build_participation_grid_modules(
            self.project
        )
        context["participation_timeline_groups"] = build_participation_timeline_groups(
            self.project
        )
        context["event"] = None
        context["modules"] = None
        context["ai_summarisation_enabled"] = is_ai_summarisation_enabled(self.project)
        context["project_summary_html"] = ""

        if context["ai_summarisation_enabled"]:
            summary_obj = get_latest_project_summary(self.project)
            if summary_obj:
                response = ProjectSummaryResponse(**summary_obj.response_data)
                user_feedback = get_user_feedback(
                    summary_obj,
                    self.request.user,
                    self.request.session.session_key,
                )
                context["project_summary_html"] = render_summary_fragment(
                    project=self.project,
                    response=response,
                    summary_obj=summary_obj,
                    user_feedback=user_feedback,
                )

        return context


class ProjectResultInsightComponentFormView(ProjectComponentFormView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ProjectInsight.update_context(
            project=self.project, context=context, dashboard=True
        )

        if self.request.POST:
            context["insight_form"] = dashboard.ProjectInsightForm(
                data=self.request.POST, instance=self.project.insight
            )
        else:
            context["insight_form"] = dashboard.ProjectInsightForm(
                instance=self.project.insight
            )

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        insight_form = context["insight_form"]
        if insight_form.is_valid():
            insight_form.save()
        return super().form_valid(form)


class ModuleDetailView(PermissionRequiredMixin, PhaseDispatchMixin):
    model = module_models.Module
    permission_required = "a4projects.view_project"
    slug_url_kwarg = "module_slug"

    @cached_property
    def project(self):
        return self.module.project

    @cached_property
    def module(self):
        return self.get_object()

    def get_permission_object(self):
        return self.project

    def get_context_data(self, **kwargs):
        """Append project and module to the template context."""
        if "project" not in kwargs:
            kwargs["project"] = self.project
        if "module" not in kwargs:
            kwargs["module"] = self.module
        context = super().get_context_data(**kwargs)
        # Future modules have no active phase, so PhaseDispatchMixin renders this
        # view directly instead of a phase view with DisplayProjectOrModuleMixin.
        context["initial_slide"] = self.module.get_timeline_index
        return context


class ProjectGenerateSummaryView(PermissionRequiredMixin, generic.DetailView):
    model = models.Project
    slug_url_kwarg = "slug"
    permission_required = "a4projects.view_project"

    def get_permission_object(self):
        return self.get_object()

    def _get_user_feedback(self, summary, request):
        return get_user_feedback(
            summary,
            request.user,
            request.session.session_key,
        )

    def _format_summary_date(self, timestamp, language_code):
        if not timestamp:
            return None

        local_ts = timezone.localtime(timestamp)

        if language_code == "de":
            return local_ts.strftime("%-d. %B %Y")
        return local_ts.strftime("%B %-d, %Y")

    def get(self, request, *args, **kwargs):
        project = self.get_object()
        if not is_ai_summarisation_enabled(project):
            return HttpResponse(
                _("AI summarisation is not enabled for this organisation."),
                status=403,
            )
        logger.info(
            "ProjectGenerateSummaryView: loading summary for project %s (%s)",
            project.id,
            project.slug,
        )
        try:
            response = generate_project_summary(
                project, request=request, allow_regeneration=False
            )
            if response is None:
                html = render_to_string(
                    "a4_candy_projects/_summary_error.html", {"project": project}
                )
                return HttpResponse(html)

            try:
                summary = ProjectSummary.objects.filter(project=project).latest(
                    "created_at"
                )
            except ProjectSummary.DoesNotExist:
                summary = None

            user_feedback = self._get_user_feedback(summary, request)
            language_code = get_language()

            summary_timestamp = None
            summary_date_str = None
            if summary:
                ts = summary.last_checked_at or summary.created_at
                summary_timestamp = timezone.localtime(ts)
                summary_date_str = self._format_summary_date(
                    summary_timestamp, language_code
                )

            html = render_to_string(
                "a4_candy_projects/_summary_fragment.html",
                {
                    "response": response,
                    "project": project,
                    "summary_modules": get_summary_modules(project),
                    "summary_id": summary.id if summary else None,
                    "summary_created_at": summary.created_at if summary else None,
                    "summary_timestamp": summary_timestamp,
                    "summary_date_str": summary_date_str,
                    "user_feedback": user_feedback,
                    "show_debug": False,
                },
            )
            return HttpResponse(html)

        except Exception as exc:
            logger.error(
                "Failed to generate summary for project %s (%s): %s",
                project.id,
                project.slug,
                exc,
                exc_info=True,
            )
            capture_exception(exc)
            html = render_to_string(
                "a4_candy_projects/_summary_error.html", {"project": project}
            )
            return HttpResponse(html)


class ProjectSummaryStaffGenerateView(StaffRequiredMixin, View):
    """
    Hidden staff-only URL to force-generate a summary for one project.

    Not linked from the UI; visit per project, e.g.
    /{organisation_slug}/projects/{slug}/summary/generate/
    """

    def get(self, request, organisation_slug, slug):
        project = get_object_or_404(
            models.Project.objects.select_related("organisation"),
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
                request=request,
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


@method_decorator(csrf_exempt, name="dispatch")
class SummaryFeedbackView(View):
    def post(self, request, organisation_slug, slug):
        project = get_object_or_404(models.Project, slug=slug)
        if not is_ai_summarisation_enabled(project):
            return HttpResponse(
                _("AI summarisation is not enabled for this organisation."),
                status=403,
            )

        summary_id = request.POST.get("summary_id")
        feedback = request.POST.get("feedback")

        if feedback not in ["positive", "negative"] or not summary_id:
            return HttpResponse("Invalid request", status=400)

        summary = get_object_or_404(ProjectSummary, id=summary_id, project=project)

        user = request.user if request.user.is_authenticated else None

        if not request.session.session_key:
            request.session.save()
        session_key = request.session.session_key

        if user:
            existing_qs = SummaryFeedback.objects.filter(summary=summary, user=user)
        elif session_key:
            existing_qs = SummaryFeedback.objects.filter(
                summary=summary, session_key=session_key
            )
        else:
            existing_qs = SummaryFeedback.objects.none()

        existing_fb = existing_qs.first()

        if existing_fb and existing_fb.feedback == feedback:
            existing_qs.delete()
            user_feedback = None
        else:
            existing_qs.delete()
            SummaryFeedback.objects.create(
                summary=summary,
                user=user,
                feedback=feedback,
                session_key=session_key,
            )
            user_feedback = feedback

        return render(
            request,
            "a4_candy_projects/_feedback_icons.html",
            {
                "user_feedback": user_feedback,
                "summary_id": summary_id,
                "project": project,
            },
        )
