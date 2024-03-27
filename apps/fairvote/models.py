import json
import logging

from django.conf import settings
from django.db import models
from django.db.models import Case
from django.db.models import F
from django.db.models import FloatField
from django.db.models import Q
from django.db.models import QuerySet
from django.db.models import Sum
from django.db.models import Value
from django.db.models import When
from django.utils.translation import gettext_lazy as _

from adhocracy4.modules.models import Module
from adhocracy4.ratings.models import Rating
from apps.ideas.models import Idea

logger = logging.getLogger(__name__)
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

    def update_choins(self, choins_amount: float, append):
        self.choins = (
            self.choins + float(choins_amount) if append else float(choins_amount)
        )
        self.save()


def get_supporters(idea) -> QuerySet:
    """
    Returns a query-set describing the users who support the given idea.
    """
    return Choin.objects.filter(
        user__rating__value=1, user__rating__idea=idea, module=idea.module
    ).distinct()


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

    def accept_idea(self):
        """
        Make all required modifications once the current idea is accepted by the admin.
        """
        if self.idea.moderator_status != "ACCEPTED":
            self.idea.moderator_status = "ACCEPTED"
            self.calculate_user_payments_for_accepting_an_idea()
            self.idea.save()

    def add_choin_event_for_a_supporter(
        self, supporters_count, paid, giveaway_choins, supporter
    ):
        """
        When accepting an idea, we add this choin-event for each user who supported this idea.
        """
        message = f"Idea accepted! <a href='{self.idea.get_absolute_url()}'>{self.idea.name}</a> cost {self.goal} choins.<br/>It was funded by {supporters_count} supporters. You supported it and paid {paid} choins."
        message_params = {
            "idea_name": self.idea.name,
            "idea_url": self.idea.get_absolute_url(),
            "supporters_count": supporters_count,
            "total_cost": self.goal,
            "paid": paid,
            "giveaway": giveaway_choins,
            "support": True,
        }
        message_params_json = json.dumps(message_params)

        ChoinEvent.objects.create(
            user=supporter.user,
            content=message,
            content_params=message_params_json,
            balance=supporter.choins,  # = 0
            module=supporter.module,
            type="ACC",
        )

    def calculate_user_payments_for_accepting_an_idea(self):
        """
        Calculate how much choins should be added to each user in order to accept the current idea.
        """
        supporters = get_supporters(self.idea)
        supporters_count = supporters.count()
        supportes_by_choins = sorted(
            supporters, key=lambda s: s.choins
        )  # All supporters of this idea, sorted by increasing number of their choins.

        # choins_sum = get_choins_sum(self.idea)                    # Compute the choins_sum on the fly.
        choins_sum = IdeaChoin.objects.get(
            idea=self.idea
        ).choins  # Get the computed choins_sum from the table.

        logger.debug(
            f"{supporters_count} supporters: {supportes_by_choins}. choins_sum={choins_sum}"
        )

        idea_name = self.idea.name
        idea_url = self.idea.get_absolute_url()
        giveaway_choins = (
            (self.goal - choins_sum) / supporters_count if choins_sum < self.goal else 0
        )
        choins_per_user = self.goal / supporters_count  # most fair option

        remaining_cost = (
            self.goal
        )  # Initially, the remaining cost is the entire cost of the idea.
        last_user_index = supporters_count
        for index, supporter in enumerate(supportes_by_choins):
            if supporter.choins + giveaway_choins < choins_per_user:
                supporter.choins += giveaway_choins

                # create a "user paid" record
                UserIdeaChoin.objects.create(
                    user=supporter.user, idea=self.idea, choins=supporter.choins
                )

                # update the user choins
                paid = supporter.choins
                remaining_cost -= supporter.choins
                supporter.choins = 0
                supporter.save()

                self.add_choin_event_for_a_supporter(
                    supporters_count, paid, giveaway_choins, supporter
                )

            else:
                # the first user that has enough choins to pay
                last_user_index = index
                break

        # if there are users that have enough choins to pay
        if last_user_index < supporters_count:
            users_count_to_divide = supporters_count - last_user_index
            choins_per_user = remaining_cost / users_count_to_divide

            for i in range(last_user_index, supporters_count):
                supporter = supportes_by_choins[i]
                supporter.choins += giveaway_choins

                # create "user paid" record
                UserIdeaChoin.objects.create(
                    user=supporter.user, idea=self.idea, choins=supporter.choins
                )

                # update user choins
                supporter.choins -= choins_per_user
                supporter.save()

                self.add_choin_event_for_a_supporter(
                    supporters_count, choins_per_user, giveaway_choins, supporter
                )

        # users who didn't support
        users_dont_support = Choin.objects.filter(
            ~Q(user__rating__value=1, user__rating__idea=self.idea)
            | Q(user__rating__isnull=True),
            module=self.idea.module,
        ).distinct()

        # create a choin-event for users don't support
        users_dont_support.update(choins=F("choins") + giveaway_choins)
        message = f"Idea accepted: <a href='{idea_url}'>{idea_name}</a> cost {self.goal} choins.<br/> It was funded by {supporters_count} supporters. You did not support it so you recived {giveaway_choins} choins."
        message_params = {
            "idea_name": self.idea.name,
            "idea_url": idea_url,
            "supporters_count": supporters_count,
            "total_cost": self.goal,
            "paid": 0,
            "giveaway": giveaway_choins,
            "support": False,
        }
        message_params_json = json.dumps(message_params)

        ChoinEvent.objects.bulk_create(
            [
                ChoinEvent(
                    user=user_choin.user,
                    content=message,
                    content_params=message_params_json,
                    balance=user_choin.choins,
                    module=user_choin.module,
                    type="ACC",
                )
                for user_choin in users_dont_support
            ]
        )

    def update_choins(self):
        """
        After an idea is accepted, we update the total number of choins and the number of missing choins for every other idea.
        """
        if self.idea.moderator_status == "ACCEPTED":
            self.choins = 0
            self.missing = 0
            self.save()
        else:
            self.choins = get_choins_sum(self.idea)
            supporters_count = Rating.objects.filter(idea=self.idea, value=1).count()
            self.missing = (
                ((self.goal - self.choins) / supporters_count)
                if supporters_count
                else self.goal
            )
            self.save()

    def __str__(self):
        return "{}_{}".format(self.idea, self.choins)


def get_choins_sum(idea) -> float:
    """
    Computes the total number of choins owned by all supporters of the given idea.
    Should be called each time the number of choins changes, in order to compute the updated sum.
    """
    # return IdeaChoin.objects.get(idea=idea).choins
    idea_choin = (
        IdeaChoin.objects.filter(  # get all rows from the `idea_choin` table that correspond to the given idea, and has at least one supporter.
            idea=idea, idea__ratings__isnull=False, idea__ratings__value=1
        )
        .annotate(  # Create a temporary field in the `idea_choin` table, for the computation.
            choins_ann=Sum(
                Case(
                    When(
                        ~Q(
                            idea__moderator_status="ACCEPTED"
                        ),  # Choose only ideas that are not accepted.
                        idea__ratings__creator__choin__choins__isnull=False,  # Choose only ideas rated by a user who has choins.
                        idea__ratings__creator__choin__module=idea.module,  # Choose only ideas rated by a user who has choins in the relevant module.
                        then=F(
                            "idea__ratings__creator__choin__choins"
                        ),  # Get the number of choins owned by each relevant supporter.
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
