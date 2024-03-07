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
from adhocracy4.ratings.models import Rating
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
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name="choin")
    choins = models.FloatField(blank=True, default=0, verbose_name=_("Choins"))
    missing = models.FloatField(
        blank=True, default=DEFAULT_GOAL, verbose_name=_("Missing Choins")
    )
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

        if choins_sum < self.goal:
            choins_per_user = (self.goal - choins_sum) / supporters_count

            users_choins = Choin.objects.filter(module=self.idea.module)
            for user_choin in users_choins:
                user_choin.choins += choins_per_user
                user_choin.save()
                message = f"All {users_choins.count()} participants received more {choins_per_user} choins."
                ChoinEvent.objects.create(
                    user=user_choin.user,
                    content=message,
                    balance=user_choin.choins,
                    module=user_choin.module,
                    type="ADD",
                )

        choins_per_user = self.goal / supporters_count  # most fair option
        supportes_by_choins = sorted(supporters, key=lambda s: s.choins)
        current_sum = self.goal
        last_user_index = supporters_count
        for index, supporter in enumerate(supportes_by_choins):
            if supporter.choins < choins_per_user:
                UserIdeaChoin.objects.create(
                    user=supporter.user, idea=self.idea, choins=supporter.choins
                )
                paid = supporter.choins
                current_sum -= supporter.choins
                supporter.choins = 0
                supporter.save()
                message = f"The idea {self.idea.name} has been accepted. {supporters_count} participants paid {self.goal} choins. You paid {paid}"
                ChoinEvent.objects.create(
                    user=supporter,
                    content=message,
                    balance=0,
                    module=supporter.module,
                    type="ACC",
                )

            else:
                last_user_index = index
                break

        if last_user_index < supporters_count:
            users_count_to_divide = supporters_count - last_user_index
            choins_per_user = current_sum / users_count_to_divide
            for i in range(last_user_index, supporters_count):
                supporter = supportes_by_choins[i]

                UserIdeaChoin.objects.create(
                    user=supporter.user, idea=self.idea, choins=supporter.choins
                )
                supporter.choins -= choins_per_user
                supporter.save()
                message = f"The idea {self.idea.name} has been accepted. {supporters_count} participants paid {self.goal} choins. You paid {choins_per_user}"
                ChoinEvent.objects.create(
                    user=supporter.user,
                    content=message,
                    balance=supporter.choins,
                    module=supporter.module,
                    type="ACC",
                )

        users_dont_support = Choin.objects.filter(
            ~Q(user__rating__value=1, user__rating__idea=self.idea)
            | Q(user__rating__isnull=True),
            module=self.idea.module,
        ).distinct()
        message = f"The idea {self.idea.name} has been accepted. {supporters_count} participants paid {self.goal} choins. You paid 0"
        ChoinEvent.objects.bulk_create(
            [
                ChoinEvent(
                    user=user_choin.user,
                    content=message,
                    balance=user_choin.choins,
                    module=user_choin.module,
                    type="ACC",
                )
                for user_choin in users_dont_support
            ]
        )

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
        if self.idea.moderator_status == "ACCEPTED":
            self.choins = 0
            self.missing = 0
            self.save()
        else:
            self.choins = self.get_choins_sum()
            supporters_count = Rating.objects.filter(idea=self.idea, value=1).count()
            self.missing = (
                ((self.goal - self.choins) / supporters_count)
                if supporters_count
                else self.goal
            )
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
