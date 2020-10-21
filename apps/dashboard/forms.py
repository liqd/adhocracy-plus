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
        fields = ['name', 'description', 'access']
        widgets = {
            'access': forms.RadioSelect(
                choices=[
                    (project_models.Access.PUBLIC.value,
                     _('All users can participate (public).')),
                    (project_models.Access.SEMIPUBLIC.value,
                     _('All users can view the content but only invited users '
                       'can participate (semipublic).')),
                    (project_models.Access.PRIVATE.value,
                     _('Only invited users can participate (private).'))
                ]
            ),
        }
