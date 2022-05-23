from django import forms

from apps.organisations.mixins import OrganisationTermsOfUseMixin

from . import models


class SubjectForm(OrganisationTermsOfUseMixin):

    def __init__(self, *args, **kwargs):
        self.module = kwargs.pop('module')
        super().__init__(*args, **kwargs)
        self.fields['description'].widget = forms.Textarea({'rows': 4})

    class Meta:
        model = models.Subject
        fields = ['name', 'description']
