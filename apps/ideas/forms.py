from django import forms

from adhocracy4.categories.forms import CategorizableFieldMixin
from adhocracy4.forms.fields import CreatorContactFieldMixin
from adhocracy4.labels.mixins import LabelsAddableFieldMixin
from apps.contrib.image_upload_help import IMAGE_UPLOAD_IDEA_HELP_TEXT
from apps.contrib.mixins import ImageRightOfUseMixin
from apps.organisations.mixins import OrganisationTermsOfUseMixin

from . import models


class IdeaForm(
    CategorizableFieldMixin,
    LabelsAddableFieldMixin,
    ImageRightOfUseMixin,
    CreatorContactFieldMixin,
    OrganisationTermsOfUseMixin,
):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].help_text = IMAGE_UPLOAD_IDEA_HELP_TEXT

    class Meta:
        model = models.Idea
        fields = ["name", "description", "image", "category", "labels"]


class IdeaModerateForm(forms.ModelForm):
    class Meta:
        model = models.Idea
        fields = ["moderator_status"]
