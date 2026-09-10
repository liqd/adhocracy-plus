from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from adhocracy4.dashboard.forms import ALLOW_GUEST_USERS_CHOICES
from adhocracy4.dashboard.forms import ProjectBasicForm as A4ProjectBasicForm
from adhocracy4.dashboard.forms import ProjectCreateForm
from adhocracy4.projects import models as project_models
from apps.contrib.image_upload_help import IMAGE_UPLOAD_HERO_HELP_TEXT
from apps.contrib.image_upload_help import IMAGE_UPLOAD_TILE_HELP_TEXT
from apps.organisations.models import Organisation


class OrganisationForm(forms.ModelForm):
    class Meta:
        model = Organisation
        fields = ["name", "logo"]
        labels = {"name": _("Organisation name")}


def _coerce_bool_choice(value):
    """Coerce radio choice values to booleans (as adhocracy4's basic form does)."""
    if value in (True, "True", "true", "1", 1):
        return True
    if value in (False, "False", "false", "0", 0):
        return False
    raise ValueError(f"Invalid boolean choice: {value!r}")


class ProjectBasicForm(A4ProjectBasicForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].help_text = IMAGE_UPLOAD_HERO_HELP_TEXT
        self.fields["tile_image"].help_text = IMAGE_UPLOAD_TILE_HELP_TEXT


class DashboardProjectCreateForm(ProjectCreateForm):
    class Meta:
        model = project_models.Project
        fields = ["name", "description", "allow_guest_users", "access"]
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if getattr(settings, "A4_ENABLE_GUEST_USERS", False):
            self.fields["allow_guest_users"] = forms.TypedChoiceField(
                label=_("Participants"),
                choices=ALLOW_GUEST_USERS_CHOICES,
                coerce=_coerce_bool_choice,
                widget=forms.RadioSelect(),
                required=True,
                initial=False,
            )
        else:
            self.fields.pop("allow_guest_users", None)
