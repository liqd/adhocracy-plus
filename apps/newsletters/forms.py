from django import forms
from django.apps import apps
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from adhocracy4.projects.models import Project

from . import models

Organisation = apps.get_model(settings.A4_ORGANISATIONS_MODEL)


class RestrictedNewsletterForm(forms.ModelForm):
    """Hide receiver choices - only show project follows."""

    class Meta:
        model = models.Newsletter
        fields = ['sender_name', 'sender', 'project', 'receivers',
                  'organisation', 'subject', 'body']

    def __init__(self, user=None, organisation=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['receivers'].widget = forms.HiddenInput()

        project_qs = Project.objects
        if organisation:
            project_qs = Project.objects.filter(organisation=organisation.id)

        self.fields['project'] = forms.ModelChoiceField(
            label=_('Project'),
            queryset=project_qs,
            required=False, empty_label=None)
        self.fields['project'].label = _('Receivers are all users '
                                         'which follow the following project:')

        self.fields['organisation'] = forms.ModelChoiceField(
            label=_('Organisation'),
            queryset=Organisation.objects,
            required=False, empty_label=None)
