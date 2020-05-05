from django import forms
from django.utils.translation import ugettext_lazy as _

from adhocracy4.dashboard.forms import ProjectCreateForm
from adhocracy4.projects import models as project_models
from apps.organisations.models import Organisation


class OrganisationForm(forms.ModelForm):

    class Meta:
        model = Organisation
        fields = ['name', 'logo']
        labels = {
            'name': _('Organisation name')
        }


class DashboardProjectCreateForm(ProjectCreateForm):

    class Meta:
        model = project_models.Project
        fields = ['name', 'description', 'is_public']
        widgets = {
            'is_public': forms.RadioSelect(
                choices=[
                    (True, _('All users can participate (public).')),
                    (False, _('Only invited users can participate (private).'))
                ]
            )
        }
