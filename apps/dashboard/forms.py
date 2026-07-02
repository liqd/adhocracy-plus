from django import forms
from django.utils.translation import gettext_lazy as _

from adhocracy4.dashboard.forms import ProjectBasicForm as A4ProjectBasicForm
from adhocracy4.dashboard.forms import ProjectCreateForm
from adhocracy4.projects import models as project_models
from apps.contrib.image_upload_help import IMAGE_UPLOAD_HELP_TEXT
from apps.organisations.models import Organisation


class OrganisationForm(forms.ModelForm):
    class Meta:
        model = Organisation
        fields = ["name", "logo"]
        labels = {"name": _("Organisation name")}


class ProjectBasicForm(A4ProjectBasicForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].help_text = IMAGE_UPLOAD_HELP_TEXT
        self.fields["tile_image"].help_text = IMAGE_UPLOAD_HELP_TEXT


class DashboardProjectCreateForm(ProjectCreateForm):
    class Meta:
        model = project_models.Project
        fields = ["name", "description", "access"]
        widgets = {
            "access": forms.RadioSelect(
                # FIXME: these choices are currently ignored by djangos widget
                # machinery - we work around that in apps/projects/overwrites
                choices=[
                    (
                        project_models.Access.PUBLIC.value,
                        _(
                            "All users can see project tile and content and can "
                            "participate (public)."
                        ),
                    ),
                    (
                        project_models.Access.SEMIPUBLIC.value,
                        _(
                            "All users can see project tile and content, only "
                            "invited users can participate (semi-public)."
                        ),
                    ),
                    (
                        project_models.Access.PRIVATE.value,
                        _(
                            "Only invited users can see project tile and content "
                            "and can participate (private)."
                        ),
                    ),
                ]
            ),
        }
