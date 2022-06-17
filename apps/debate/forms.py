from django import forms

from . import models


class SubjectForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.module = kwargs.pop('module')
        super().__init__(*args, **kwargs)
        self.fields['description'].widget = forms.Textarea({'rows': 4})

    class Meta:
        model = models.Subject
        fields = ['name', 'description']
