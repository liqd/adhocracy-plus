from django import forms
from django.contrib.admin.helpers import ActionForm

from adhocracy4.modules.models import Module


class UpdateChoinsForm(ActionForm):
    choins_amount = forms.FloatField(required=False)
    append = forms.BooleanField(initial=True, required=False)


class IncreaseChoinIdeaForm(ActionForm):
    module = forms.ModelChoiceField(
        queryset=Module.objects.all(),
        required=False,
        label="Select a module",
        help_text="Choose a module",
    )
