from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from adhocracy4.dashboard import DashboardComponent
from adhocracy4.dashboard import components
from adhocracy4.dashboard.components.forms import ProjectDashboardForm
from adhocracy4.dashboard.components.forms import ProjectFormComponent

from . import views
from .models import Insight


class ParticipantsComponent(DashboardComponent):
    identifier = "participants"
    weight = 30
    label = _("Participants")

    def is_effective(self, project):
        return not project.is_draft and not project.is_public

    def get_base_url(self, project):
        return reverse(
            "a4dashboard:dashboard-participants-edit",
            kwargs={
                "organisation_slug": project.organisation.slug,
                "project_slug": project.slug,
            },
        )

    def get_urls(self):
        return [
            (
                r"^projects/(?P<project_slug>[-\w_]+)/participants/$",
                views.DashboardProjectParticipantsView.as_view(component=self),
                "dashboard-participants-edit",
            )
        ]


class ModeratorsComponent(DashboardComponent):
    identifier = "moderators"
    weight = 32
    label = _("Moderators")

    def is_effective(self, project):
        return True

    def get_base_url(self, project):
        return reverse(
            "a4dashboard:dashboard-moderators-edit",
            kwargs={
                "organisation_slug": project.organisation.slug,
                "project_slug": project.slug,
            },
        )

    def get_urls(self):
        return [
            (
                r"^projects/(?P<project_slug>[-\w_]+)/moderators/$",
                views.DashboardProjectModeratorsView.as_view(component=self),
                "dashboard-moderators-edit",
            )
        ]


class InsightForm(ProjectDashboardForm):
    class Meta:
        model = Insight
        fields = [
            "active_participants",
            "comments",
            "ratings",
            "written_ideas",
            "poll_answers",
            "live_questions",
            "display",
        ]
        required_for_project_publish = []

        help_texts = {
            "display": _(
                "Show insights with numbers "
                "of contributions and participants "
                "during the participation process"
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not name == "display":
                field.widget.attrs["readonly"] = "true"


class ProjectInsightComponent(ProjectFormComponent):
    identifier = "insight"
    weight = 12
    label = _("Insights")

    form_title = _("Insights")
    form_class = InsightForm
    form_template_name = "a4_candy_projects/includes/project_insight_form.html"


components.register_project(ProjectInsightComponent())
components.register_project(ModeratorsComponent())
components.register_project(ParticipantsComponent())
