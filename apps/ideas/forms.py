import json

from django import forms

from adhocracy4.categories.forms import CategorizableFieldMixin
from adhocracy4.labels.mixins import LabelsAddableFieldMixin
from apps.contrib.mixins import ImageRightOfUseMixin
from apps.fairvote.algorithms import accept_idea
from apps.fairvote.algorithms import update_idea_choins
from apps.fairvote.algorithms import update_idea_goal
from apps.fairvote.algorithms import update_ideas_acceptance_order
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
    goal = forms.FloatField(min_value=0, required=False)

    class Meta:
        model = models.Idea
        fields = ["name", "description", "image", "category", "labels"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optionally populate initial data for goal field
        instance = kwargs.get("instance")
        user = kwargs.get("user")
        if instance:
            try:
                idea_choin_instance = instance.choin.first()
                if idea_choin_instance:
                    self.initial["goal"] = idea_choin_instance.goal
            except IdeaChoin.DoesNotExist:
                pass
        if user.has_perm("a4_candy_modules.is_context_moderator", instance):
            self.fields["goal"].required = True
        print("initial:", self.initial, self.is_valid())

    def save(self, commit=True):
        print("valid:", self.is_valid())
        idea = super().save(commit=commit)
        if commit and idea.module.blueprint_type == "FV":
            idea_choin, created = IdeaChoin.objects.get_or_create(
                idea=idea, defaults={"choins": 0, "goal": DEFAULT_GOAL}
            )
            print(idea_choin)
            goal = self.cleaned_data.get("goal")
            if goal:
                update_idea_goal(idea_choin, goal)
            # function
            obj, created = Choin.objects.get_or_create(
                user=idea.creator, module=idea.module
            )
            update_ideas_acceptance_order(idea.module)
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
        prev_status = models.Idea.objects.get(pk=self.instance.pk).moderator_status
        idea = super().save(commit=commit)
        # If this is a "fairvote" module, and the superuser accepts an idea, we have to adjust the "choins" of all users in the module.
        if (
            idea.module.blueprint_type == "FV"
            and prev_status != "ACCEPTED"
            and self.instance.moderator_status == "ACCEPTED"
        ):
            accept_idea(IdeaChoin.objects.get(idea=idea))
            [update_idea_choins(other_idea) for other_idea in IdeaChoin.objects.all()]
            update_ideas_acceptance_order(idea.module.pk)
        return idea
