from django import forms
from django.utils.translation import gettext_lazy as _

from . import models


class ModeratorFeedbackForm(forms.ModelForm):
    class Meta:
        model = models.ModeratorFeedback
        fields = ["feedback_text"]
        help_texts = {
            "feedback_text": _(
                "The official feedback will appear below the idea, "
                "indicating your organisation. The idea provider receives "
                "a notification."
            ),
        }
