from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from adhocracy4.modules.models import Module
from apps.ideas.models import Idea

DEFAULT_GOAL = 150


class Choin(models.Model):
    """
    This class represents a row in the "choins" table. Each row contains:
    * User id;
    * Module id (of a fairvote module);
    * Number of choins that the user has in that module.

    The "choins" are choice-coins - virtual coins that the user can use to participate in choosing an idea to implement.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    choins = models.FloatField(blank=True, default=0, verbose_name=_("Choins"))

    class Meta:
        unique_together = ("user", "module")
        index_together = [("user", "module")]

    def __str__(self):
        return "{}_{}".format(self.user, self.choins)

    def update_user_choins(self, choins_amount: float, append: bool):
        """
        Add or change the number of choins in a user's wallet
        """
        self.choins = (
            self.choins + float(choins_amount) if append else float(choins_amount)
        )
        self.save()


class IdeaChoin(models.Model):
    """
    This class represents a row in the "idea_choin" table. Each row contains:
    * Idea id;
    * `goal` = total cost required to accept the idea.
    * `choins` - auxiliary field:  total number of choins owned by the users supporting this idea.
    * `missing` - auxiliary field: number of choins missing, per supporting user, to attain the goal (= (goal - total_choins)/(#supporters)).
    """

    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name="choin")
    goal = models.FloatField(blank=True, default=DEFAULT_GOAL, verbose_name=_("Goal"))
    choins = models.FloatField(blank=True, default=0, verbose_name=_("Choins"))
    missing = models.FloatField(
        blank=True, default=DEFAULT_GOAL, verbose_name=_("Missing Choins")
    )

    def __str__(self):
        return "{}_{}".format(self.idea, self.choins)


class UserIdeaChoin(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE)
    choins = models.FloatField(blank=True, default=0, verbose_name=_("Choins"))

    class Meta:
        unique_together = ("user", "idea")
        index_together = [("user", "idea")]

    def __str__(self):
        return "{}_{}_{}".format(self.user, self.idea, self.choins)


class ChoinEvent(models.Model):
    EVENT_TYPES = [
        ("NEW", "Welcome"),
        ("ADD", "Add Choins"),
        ("ACC", "Idea Accepted"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    type = models.CharField(choices=EVENT_TYPES, max_length=3, blank=False)
    content = models.TextField(blank=True, max_length=255)
    balance = models.FloatField(blank=True, default=0, verbose_name=_("Balance"))
    created_at = models.DateTimeField(auto_now_add=True)
    content_params = models.JSONField(null=True, blank=True)
