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
        return "{}_{}".format(self.user, self.choins)

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
            user__rating__value=1, user__rating__idea=self.idea, module=self.idea.module
        ).distinct()

    def accept_idea(self):
        if self.idea.moderator_status != "ACCEPTED":
            self.idea.moderator_status = "ACCEPTED"
            self.calculate_cost_per_user()
            self.idea.save()

    def calculate_cost_per_user(self):
        supporters = self.get_supporters()
        supporters_count = supporters.count()
        choins_sum = self.get_choins_sum()
        print(choins_sum)

        if choins_sum < self.goal:
            choins_per_user = (self.goal - choins_sum) / supporters_count
            print(choins_per_user)
            Choin.objects.filter(module=self.idea.module).update(
                choins=F("choins") + choins_per_user
            )

        print(supporters)
        choins_per_user = self.goal / supporters_count  # most fair option
        supportes_by_choins = sorted(supporters, key=lambda s: s.choins)
        print(supportes_by_choins)
        current_sum = self.goal
        last_user_index = supporters_count
        for index, supporter in enumerate(supportes_by_choins):
            print(current_sum)
            print(supporter)
            if supporter.choins < choins_per_user:
                UserIdeaChoin.objects.create(
                    user=supporter.user, idea=self.idea, choins=supporter.choins
                )
                current_sum -= supporter.choins
                supporter.choins = 0
                supporter.save()
            else:
                last_user_index = index
                break

        if last_user_index < supporters_count:
            users_count_to_divide = supporters_count - last_user_index
            choins_per_user = current_sum / users_count_to_divide
            for i in range(last_user_index, supporters_count):
                supporter = supportes_by_choins[i]
                print(supporter)

                UserIdeaChoin.objects.create(
                    user=supporter.user, idea=self.idea, choins=supporter.choins
                )
                supporter.choins -= choins_per_user
                supporter.save()

    def get_choins_sum(self):
        idea_choin = (
            IdeaChoin.objects.filter(
                idea=self.idea, idea__ratings__isnull=False, idea__ratings__value=1
            )
            .annotate(
                choins_ann=Sum(
                    Case(
                        When(
                            ~Q(idea__moderator_status="ACCEPTED"),
                            idea__ratings__creator__choin__choins__isnull=False,
                            idea__ratings__creator__choin__module=self.idea.module,
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
        )

        return idea_choin.get("choins_ann", 0) if idea_choin else 0

    def update_choins(self):
        self.choins = self.get_choins_sum()
        self.save()

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
