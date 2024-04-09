import json
import logging

from django.db.models import Case
from django.db.models import F
from django.db.models import FloatField
from django.db.models import Q
from django.db.models import QuerySet
from django.db.models import Sum
from django.db.models import Value
from django.db.models import When

from adhocracy4.ratings.models import Rating

from .models import Choin
from .models import ChoinEvent
from .models import Idea
from .models import IdeaChoin
from .models import UserIdeaChoin

logger = logging.getLogger(__name__)

# User Choin


def get_supporters(idea: Idea) -> QuerySet:  # WRONG!!
    """
    Returns a query-set describing the users who support the given idea.
    """
    for rating in Rating.objects.filter(idea=idea):
        logger.info(rating.creator, rating.value)
    return Choin.objects.filter(
        Q(user__rating__value=1) & Q(user__rating__idea=idea), module=idea.module
    ).distinct()


# Rating


def calculate_missing_choins(idea_choins, supporters_count, goal):
    logger.info("updated supporters: ", idea_choins)
    missing_choins_per_supporter = (goal - idea_choins) / (supporters_count)
    logger.info("missing_choins_per_supporter: ", missing_choins_per_supporter)
    if missing_choins_per_supporter > 0:
        return missing_choins_per_supporter
    return 0


def update_idea_choins_after_rating(idea_id, choins):
    """
    After a user rates or updates the rating of an idea, we re-compute the total number
    of choins and the number of missing choins for this idea.
    """
    idea = Idea.objects.get(pk=idea_id)
    obj, created = IdeaChoin.objects.update_or_create(
        idea=idea, defaults={"choins": F("choins") + choins}
    )
    idea_choins = IdeaChoin.objects.values_list("choins", flat=True).get(
        pk=obj.pk
    )  # the updated idea choins
    supporters_count = get_supporters(
        idea
    ).count()  # happens after user changed their rating -> updated value
    logger.info("supporters count: ", supporters_count, "idea choins: ", idea_choins)
    if supporters_count > 0:
        obj.missing = calculate_missing_choins(idea_choins, supporters_count, obj.goal)
    else:
        obj.missing = obj.goal
    obj.save()


# Idea Choin


def accept_idea(idea_choin: IdeaChoin):
    """
    Make all required modifications once the current idea is accepted by the admin.
    """
    if idea_choin.idea.moderator_status != "ACCEPTED":
        idea_choin.idea.moderator_status = "ACCEPTED"
        calculate_user_payments_for_accepting_an_idea(idea_choin)
        idea_choin.idea.save()


def add_choin_event_for_a_supporter(
    idea_choin: IdeaChoin, supporters_count, paid, giveaway_choins, supporter
):
    """
    When accepting an idea, we add this choin-event for each user who supported this idea.
    """
    message = f"Idea accepted! <a href='{idea_choin.idea.get_absolute_url()}'>{idea_choin.idea.name}</a> cost {idea_choin.goal} choins.<br/>It was funded by {supporters_count} supporters. You supported it and paid {paid} choins."
    message_params = {
        "idea_name": idea_choin.idea.name,
        "idea_url": idea_choin.idea.get_absolute_url(),
        "supporters_count": supporters_count,
        "total_cost": idea_choin.goal,
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


def calculate_user_payments_for_accepting_an_idea(idea_choin: IdeaChoin):
    """
    Calculate how much choins should be added to each user in order to accept the current idea.
    """
    supporters = get_supporters(idea_choin.idea)
    supporters_count = supporters.count()
    supportes_by_choins = sorted(
        supporters, key=lambda s: s.choins
    )  # All supporters of this idea, sorted by increasing number of their choins.

    # choins_sum = get_choins_sum(self.idea)                    # Compute the choins_sum on the fly.
    choins_sum = IdeaChoin.objects.get(
        idea=idea_choin.idea
    ).choins  # Get the computed choins_sum from the table.

    logger.debug(
        f"{supporters_count} supporters: {supportes_by_choins}. choins_sum={choins_sum}"
    )

    idea_name = idea_choin.idea.name
    idea_url = idea_choin.idea.get_absolute_url()
    giveaway_choins = (
        (idea_choin.goal - choins_sum) / supporters_count
        if choins_sum < idea_choin.goal
        else 0
    )
    choins_per_user = idea_choin.goal / supporters_count  # most fair option

    remaining_cost = (
        idea_choin.goal
    )  # Initially, the remaining cost is the entire cost of the idea.
    last_user_index = supporters_count
    for index, supporter in enumerate(supportes_by_choins):
        if supporter.choins + giveaway_choins < choins_per_user:
            supporter.choins += giveaway_choins

            # create a "user paid" record
            UserIdeaChoin.objects.create(
                user=supporter.user, idea=idea_choin.idea, choins=supporter.choins
            )

            # update the user choins
            paid = supporter.choins
            remaining_cost -= supporter.choins
            supporter.choins = 0
            supporter.save()

            add_choin_event_for_a_supporter(
                idea_choin, supporters_count, paid, giveaway_choins, supporter
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
                user=supporter.user, idea=idea_choin.idea, choins=supporter.choins
            )

            # update user choins
            supporter.choins -= choins_per_user
            supporter.save()

            add_choin_event_for_a_supporter(
                idea_choin,
                supporters_count,
                choins_per_user,
                giveaway_choins,
                supporter,
            )

    # users who didn't support
    users_dont_support = Choin.objects.filter(
        ~Q(user__rating__value=1, user__rating__idea=idea_choin.idea)
        | Q(user__rating__isnull=True),
        module=idea_choin.idea.module,
    ).distinct()

    # create a choin-event for users don't support
    users_dont_support.update(choins=F("choins") + giveaway_choins)
    message = f"Idea accepted: <a href='{idea_url}'>{idea_name}</a> cost {idea_choin.goal} choins.<br/> It was funded by {supporters_count} supporters. You did not support it so you recived {giveaway_choins} choins."
    message_params = {
        "idea_name": idea_choin.idea.name,
        "idea_url": idea_url,
        "supporters_count": supporters_count,
        "total_cost": idea_choin.goal,
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


def update_idea_choins(idea_choin: IdeaChoin):
    """
    After an idea is accepted, we update the total number of choins and the number of missing choins for every other idea.
    """
    if idea_choin.idea.moderator_status == "ACCEPTED":
        idea_choin.choins = 0
        idea_choin.missing = 0
        idea_choin.save()
    else:
        idea_choin.choins = get_choins_sum(idea_choin.idea)
        supporters_count = Rating.objects.filter(idea=idea_choin.idea, value=1).count()
        idea_choin.missing = (
            ((idea_choin.goal - idea_choin.choins) / supporters_count)
            if supporters_count
            else idea_choin.goal
        )
        idea_choin.save()


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
