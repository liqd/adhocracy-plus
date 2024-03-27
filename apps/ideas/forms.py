import json

from django import forms

from adhocracy4.categories.forms import CategorizableFieldMixin
from adhocracy4.labels.mixins import LabelsAddableFieldMixin
from apps.contrib.mixins import ImageRightOfUseMixin
from apps.fairvote.models import DEFAULT_GOAL
from apps.fairvote.models import Choin
from apps.fairvote.models import ChoinEvent
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
        obj, created = Choin.objects.get_or_create(
            user=idea.creator, module=idea.module
        )
        if created:
            message = f"You joined module '{idea.module.name}' - project '{idea.module.project.name}'"

            message_params = {
                "module_name": idea.module.name,
                "project_name": idea.module.project.name,
            }
            message_params_json = json.dumps(message_params)
            # EREL: attempt to use parameters; currently not uesd

            ChoinEvent.objects.create(
                user=idea.creator,
                module=idea.module,
                type="NEW",
                content=message,
                content_params=message_params_json,
                balance=0,
            )
        return idea


class IdeaModerateForm(forms.ModelForm):
    """
    The form that the superuser uses to "moderate" an idea.
    In particular, the superuser can use this form to accept an idea.
    """

    class Meta:
        model = models.Idea
        fields = ["moderator_status"]

    def save(self, commit=True):
        idea = super().save(commit=commit)

        # If this is a "fairvote" module, and the superuser accepts an idea, we have to adjust the "choins" of all users in the module.
        if idea.module.blueprint_type == "FV" and idea.moderator_status == "ACCEPTED":
            IdeaChoin.objects.get(idea=idea).accept_idea()
            [other_idea.update_choins() for other_idea in IdeaChoin.objects.all()]

        return idea
