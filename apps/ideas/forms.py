from django import forms

from adhocracy4.categories.forms import CategorizableFieldMixin
from adhocracy4.labels.mixins import LabelsAddableFieldMixin
from apps.contrib.mixins import ImageRightOfUseMixin
from apps.fairvote.models import DEFAULT_GOAL
from apps.fairvote.models import Choin
from apps.fairvote.models import IdeaChoin
from apps.organisations.mixins import OrganisationTermsOfUseMixin

from . import models


class IdeaForm(
    CategorizableFieldMixin,
    LabelsAddableFieldMixin,
    ImageRightOfUseMixin,
    OrganisationTermsOfUseMixin,
):
    class Meta:
        model = models.Idea
        fields = ["name", "description", "image", "category", "labels"]

    def save(self, commit=True):
        idea = super().save(commit=commit)
        if idea.module.blueprint_type == "FV" and commit:
            IdeaChoin.objects.get_or_create(idea=idea, choins=0, goal=DEFAULT_GOAL)
        Choin.objects.get_or_create(user=idea.creator, module=idea.module)
        return idea


class IdeaModerateForm(forms.ModelForm):
    class Meta:
        model = models.Idea
        fields = ["moderator_status"]

    def save(self, commit=True):
        idea = super().save(commit=commit)
        if idea.moderator_status == "ACCEPTED":
            IdeaChoin.objects.get(idea=idea).accept_idea()
            [idea.update_choins() for idea in IdeaChoin.objects.all()]
        return idea
