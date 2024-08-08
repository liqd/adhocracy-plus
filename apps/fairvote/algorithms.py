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

from .models import MAX_ACCEPTED_IDEAS
from .models import Choin
from .models import ChoinEvent
from .models import Idea
from .models import IdeaChoin
from .models import ProjectChoin
from .models import UserIdeaChoin

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)
# User Choin


def get_supporters(idea: Idea) -> QuerySet:
    """
    Returns a query-set describing the users who support the given idea.
    """
    ratings = Rating.objects.filter(idea=idea).filter(value=1)
    logger.info("Ratings count: %s", ratings.count())
    for rating in ratings:
        logger.debug("Rating creator: %s, value: %s", rating.creator, rating.value)
    return Choin.objects.filter(user__rating__in=ratings, module=idea.module).distinct()


# Rating and IdeaChoin


def update_idea_goal(idea_choin: IdeaChoin, goal):
    idea_choin.goal = goal
    supporters_count = get_supporters(idea_choin.idea).count()
    idea_choin.missing = calculate_missing_choins(
        goal, idea_choin.choins, supporters_count
    )
    idea_choin.save()


def calculate_missing_choins(goal, choins, supporters_count):
    return ((goal - choins) / supporters_count) if supporters_count else goal


# Rating


def update_idea_choins_after_rating(idea_id, choins, positive_ratings=None):
    """
    After a user rates or updates the rating of an idea, we re-compute the total number
    of choins and the number of missing choins for this idea.
    """
    idea = Idea.objects.get(pk=idea_id)
    obj, created = IdeaChoin.objects.get_or_create(idea=idea)
    obj.choins += choins
    idea_choins = obj.choins
    if positive_ratings:
        supporters_count = (
            positive_ratings  # happens after user changed their rating -> updated value
        )
    else:
        supporters_count = get_supporters(idea).count()
    logger.info("supporters count: %s, idea choins: %s", supporters_count, idea_choins)
    obj.missing = calculate_missing_choins(obj.goal, idea_choins, supporters_count)
    obj.save()
    update_ideas_acceptance_order(idea.module.pk)


# Idea Choin


def user_vote_count(user):
    supported_ideas = Idea.objects.filter(rating__user=user).filter(rating__value=1)
    return supported_ideas.count()


def update_ideas_acceptance_order(module_id):
    fair_acceptance_order(module_id, top=MAX_ACCEPTED_IDEAS)


def accept_idea(idea_choin: IdeaChoin):
    """
    Make all required modifications once the current idea is accepted by the admin.
    """
    calculate_user_payments_for_accepting_an_idea(idea_choin)
    project, created = ProjectChoin.objects.get_or_create(
        project=idea_choin.idea.module.project
    )
    project.paid += idea_choin.goal
    project.save()


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


def calculate_giveaway_choins(goal, choins_sum, supporters_count):
    return (
        (goal - choins_sum) / supporters_count
        if (supporters_count and choins_sum < goal)
        else 0
    )


def get_users_dont_support(idea_choin: IdeaChoin):
    return Choin.objects.filter(
        ~Q(user__rating__value=1, user__rating__idea=idea_choin.idea)
        | Q(user__rating__isnull=True),
        module=idea_choin.idea.module,
    ).distinct()


def calculate_user_payments_for_accepting_an_idea(idea_choin: IdeaChoin):
    """
    Calculate how much choins should be added to each user in order to accept the current idea.
    """
    supporters = get_supporters(idea_choin.idea)
    supporters_count = supporters.count()

    # choins_sum = get_choins_sum(self.idea)                    # Compute the choins_sum on the fly.
    choins_sum = IdeaChoin.objects.get(
        idea=idea_choin.idea
    ).choins  # Get the computed choins_sum from the table.

    logger.info(f"{supporters_count} supporters: {supporters}. choins_sum={choins_sum}")

    idea_name = idea_choin.idea.name
    idea_url = idea_choin.idea.get_absolute_url()
    giveaway_choins = 0
    if choins_sum <= idea_choin.goal:
        giveaway_choins = calculate_giveaway_choins(
            idea_choin.goal, choins_sum, supporters_count
        )
        for supporter in supporters:
            paid = supporter.choins + giveaway_choins
            supporter.choins = 0
            supporter.supported_ideas_paid += idea_choin.goal
            supporter.save()
            UserIdeaChoin.objects.create(
                user=supporter.user, idea=idea_choin.idea, choins=paid
            )
            add_choin_event_for_a_supporter(
                idea_choin, supporters_count, paid, giveaway_choins, supporter
            )
    else:
        choins_to_divide = idea_choin.goal / choins_sum
        for supporter in supporters:
            paid = supporter.choins * choins_to_divide
            supporter.choins -= paid
            supporter.supported_ideas_paid += idea_choin.goal
            supporter.save()
            UserIdeaChoin.objects.create(
                user=supporter.user, idea=idea_choin.idea, choins=paid
            )
            add_choin_event_for_a_supporter(
                idea_choin, supporters_count, paid, giveaway_choins, supporter
            )

    # users who didn't support
    users_dont_support = get_users_dont_support(idea_choin)

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
        idea_choin.missing = calculate_missing_choins(
            idea_choin.goal, idea_choin.choins, supporters_count
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


# Accept Order - Simulator


def simulate_calculate_user_payments_for_accepting_an_idea(
    users, idea_choin: IdeaChoin, simulated_idea_choin, user=None
):
    """
    Calculate how much choins should be added to each user in order to accept the current idea.
    """
    supporters = simulated_idea_choin["supporters"]
    supporters_count = supporters.count()

    # choins_sum = get_choins_sum(self.idea)                    # Compute the choins_sum on the fly.
    choins_sum = simulated_idea_choin[
        "choins"
    ]  # Get the computed choins_sum from the table.

    logger.info(
        "%s supporters: %s. choins_sum= %s", supporters_count, supporters, choins_sum
    )

    goal = simulated_idea_choin["goal"]
    voted = False

    if choins_sum <= goal:
        giveaway_choins = calculate_giveaway_choins(goal, choins_sum, supporters_count)
        for supporter in supporters:
            username = supporter.user.username
            user_choins = users[username]
            paid = user_choins + giveaway_choins
            users[username] = 0
            if user is not None and username == user.username:
                voted = True
        # users who didn't support
        users_dont_support = get_users_dont_support(idea_choin)

        # update choins for users don't support
        for not_support_user in users_dont_support:
            username = not_support_user.user.username
            users[username] += giveaway_choins

    else:
        choins_to_divide = goal / choins_sum
        for supporter in supporters:
            username = supporter.user.username
            user_choins = users[username]
            paid = user_choins * choins_to_divide
            users[username] -= paid
            if username == user.username:
                voted = True
    return voted


def simulate_get_choins_sum(users, simulated_idea_choin):
    """
    Calculate choins sun for the given simulated idea
    """
    choins_sum = 0
    for supporter in simulated_idea_choin["supporters"]:
        choins_sum += users[supporter.user.username]
    return choins_sum


def simulate_update_ideas_choins(ideas, users):
    """
    After an idea is accepted, we update the total number of choins and the number of missing choins for every other idea.
    """
    next_accepted_idea = None

    for id, values in ideas.items():
        values["choins"] = simulate_get_choins_sum(users, values)
        supporters_count = values["supporters"].count()
        goal = values["goal"]
        missing = calculate_missing_choins(goal, values["choins"], supporters_count)
        values["missing"] = missing
        if next_accepted_idea is None or (
            next_accepted_idea is not None and missing < next_accepted_idea[1]
        ):
            next_accepted_idea = (id, missing)

    return next_accepted_idea


def fair_acceptance_order(module_id: int, user=None, top=5):
    """
    Simulate acceptance in the most fair order - for the top `top` ideas of the given module
    """
    # ideas choins qurey set - informaiton like choins,missing choins of each idea
    ideas_qs = IdeaChoin.objects.filter(
        ~Q(idea__moderator_status="ACCEPTED"), idea__module__id=module_id
    ).order_by("missing")
    logger.info("IDEAS QS: %s", ideas_qs)
    # ideas dict - for customize the above information
    ideas = {
        idea_choin.pk: {
            "choins": idea_choin.choins,
            "missing": idea_choin.missing,
            "goal": idea_choin.goal,
            "supporters": get_supporters(idea_choin.idea),
        }
        for idea_choin in ideas_qs
    }
    # logger.info("IDEAS: %s", ideas)
    # users dict - keys: users names, values: users choins
    users = {
        user_choin.user.username: user_choin.choins
        for user_choin in Choin.objects.filter(module=module_id)
    }
    # ideas dict of the future accpeted ideas
    returned_ideas = {}
    # sort of iterator
    next_accepted_idea = ideas_qs.first()
    # count the accepted ideas
    count = 0
    voted_count = 0
    while count < top and ideas:
        if next_accepted_idea:
            count += 1
        simulated_idea_choin = ideas[
            next_accepted_idea.pk
        ]  # get the current simulated idea info
        # calculate the payment for users and update the users choins if the idea will be accepted
        voted = simulate_calculate_user_payments_for_accepting_an_idea(
            users, next_accepted_idea, simulated_idea_choin, user
        )
        if voted:
            voted_count += 1
        # remove the idea from the ideas dict - this is how we accept here the idea
        accepted_idea = ideas.pop(next_accepted_idea.pk)
        # save order in db
        next_accepted_idea.order = count
        next_accepted_idea.save()
        logger.info(
            "%s. (%s)accepted idea: %s",
            count,
            next_accepted_idea.order,
            next_accepted_idea,
        )
        # logger.info("accepted idea with the simulate data: %s", accepted_idea)
        returned_ideas[next_accepted_idea.idea.pk] = {
            "choins": next_accepted_idea.choins,
            "cost": next_accepted_idea.goal,
            "missing": next_accepted_idea.missing,
            "supporters": accepted_idea["supporters"].count(),
            "voted": voted,
        }
        # update the ideas choins by the updated users choins, and get the next most fair idea
        next_idea = simulate_update_ideas_choins(ideas, users)
        # get the idea object for returning the IdeaQureySet object
        print(next_accepted_idea, next_idea)
        if not next_idea:
            break
        next_accepted_idea = ideas_qs.get(id=next_idea[0])
        print("for count: ", next_accepted_idea)

    # get the IdeaQureySet and annotate the order
    logger.info("RETURNED: %s", returned_ideas)
    logger.info("count RETURNED: %s", len(returned_ideas))

    if ideas:
        for idea in ideas_qs.filter(pk__in=ideas.keys()).order_by("missing"):
            count += 1
            idea.order = count
            idea.save()
            print(f"idea {count} - {idea.order}", idea)

    """from django.db.models import IntegerField

    annotated_ideas = IdeaQuerySet(
        Idea.objects.filter(id__in=returned_ideas.keys())
        .annotate(
            custom_order=Case(
                *[
                    When(id=id_val, then=Value(idx))
                    for idx, id_val in enumerate(returned_ideas, start=1)
                ],
                output_field=IntegerField(),
            )
        )
        .order_by("custom_order")
    )

    # customize the attributes for using the in the template
    for idea in annotated_ideas:
        idea.url = idea.get_absolute_url()
        values = returned_ideas[idea.pk]
        idea.choins = values["choins"]
        idea.missing = values["missing"]
        idea.voted = values["voted"]
        idea.cost = values["cost"]
        idea.supporters = values["supporters"]
    annotated_ideas.voted = voted_count
    return annotated_ideas"""


"""from apps.fairvote.algorithms import order_by_accept_most_fair
from django.db.models import QuerySet, Window, F
from django.db.models.functions import RowNumber


class acceptOrderQuerySet(QuerySet):
    def annotate_accept_order(self):
        ideas_by_accept_order = order_by_accept_most_fair()

        return self.filter(id__in=ideas_by_accept_order).annotate(accept_order=Window(
            expression=RowNumber(),
            order_by=F('id').asc()))"""
