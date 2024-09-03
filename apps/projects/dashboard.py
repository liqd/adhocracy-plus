from django.forms import ModelForm
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from adhocracy4.dashboard import DashboardComponent
from adhocracy4.dashboard import components
from adhocracy4.dashboard.components.forms import ProjectFormComponent
from adhocracy4.dashboard.forms import ProjectResultForm

from . import forms
from . import views
from .models import ProjectInsight
from .views import ProjectResultInsightComponentFormView


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


class ProjectInsightForm(ModelForm):
    class Meta:
        model = ProjectInsight
        fields = ["display"]

        labels = {
            "display": _(
                "Show insights with numbers "
                "of contributions and participants "
                "during the participation process"
            ),
        }


class ProjectResultComponent(ProjectFormComponent):
    identifier = "result"
    weight = 12
    label = _("Result")

    form_title = _("Edit project result")
    form_class = ProjectResultForm
    form_template_name = "a4dashboard/includes/project_result_form.html"

    def get_urls(self):
        view = ProjectResultInsightComponentFormView.as_view(
            component=self,
            title=self.form_title,
            form_class=self.form_class,
            form_template_name=self.form_template_name,
        )
        return [
            (
                r"^projects/(?P<project_slug>[-\w_]+)/{identifier}/$".format(
                    identifier=self.identifier
                ),
                view,
                "dashboard-{identifier}-edit".format(identifier=self.identifier),
            )
        ]


class ProjectLocationComponent(ProjectFormComponent):
    identifier = "location"
    weight = 34
    label = _("Location")

    form_title = _("Edit location")
    form_class = forms.PointForm
    form_template_name = "a4dashboard/includes/project_location_form.html"

    def get_urls(self):
        view = ProjectResultInsightComponentFormView.as_view(
            component=self,
            title=self.form_title,
            form_class=self.form_class,
            form_template_name=self.form_template_name,
        )
        return [
            (
                r"^projects/(?P<project_slug>[-\w_]+)/{identifier}/$".format(
                    identifier=self.identifier
                ),
                view,
                "dashboard-{identifier}-edit".format(identifier=self.identifier),
            )
        ]


components.register_project(ModeratorsComponent())
components.register_project(ParticipantsComponent())
components.replace_project(ProjectResultComponent())
components.replace_project(ProjectLocationComponent())
