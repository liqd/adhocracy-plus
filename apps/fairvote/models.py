from django.conf import settings
from django.db import models
from django.db.models import Case
from django.db.models import F
from django.db.models import FloatField
from django.db.models import Q
from django.db.models import Sum
from django.db.models import Value
from django.db.models import When
from django.utils.translation import gettext_lazy as _

from adhocracy4.modules.models import Module
from apps.ideas.models import Idea

DEFAULT_GOAL = 150


class Choin(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    choins = models.FloatField(blank=True, default=0, verbose_name=_("Choins"))

    class Meta:
        unique_together = ("user", "module")
        index_together = [("user", "module")]

    def __str__(self):
        return "{}_{}_{}".format(self.user, self.module, self.choins)

    def update_choins(self, choins_amount: float, append):
        self.choins = (
            self.choins + float(choins_amount) if append else float(choins_amount)
        )
        self.save()


class IdeaChoin(models.Model):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE)
    choins = models.FloatField(blank=True, default=0, verbose_name=_("Choins"))
    goal = models.FloatField(blank=True, default=DEFAULT_GOAL, verbose_name=_("Goal"))

    def get_remaining_choins(self):
        return self.goal - self.choins

    def get_supporters(self):
        return Choin.objects.filter(
            user__rating__value=1, user__rating__idea=self.idea
        ).distinct()

    def accept_idea(self):
        self.idea.moderator_status = "ACCEPTED"
        users_to_reset = self.get_supporters()
        users_to_reset.update(choins=0)
        self.idea.save()

    def update_choins(self):
        self.choins = (
            IdeaChoin.objects.filter(
                idea=self.idea, idea__ratings__isnull=False, idea__ratings__value=1
            )
            .annotate(
                choins_ann=Sum(
                    Case(
                        When(
                            ~Q(idea__moderator_status="ACCEPTED"),
                            idea__ratings__creator__choin__choins__isnull=False,
                            then=F("idea__ratings__creator__choin__choins"),
                        ),
                        default=Value(0),
                        output_field=FloatField(),
                        distinct=True,
                    )
                )
            )
            .values("choins_ann")
            .first()
            .get("choins_ann", 0)
        )
        self.save()

    def __str__(self):
        return "{}_{}".format(self.idea, self.choins)
