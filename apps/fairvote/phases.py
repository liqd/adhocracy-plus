from django.utils.translation import gettext_lazy as _

from apps.ideas import phases as idea_phases

from . import models


class FairVotePhase(idea_phases.CollectFeedbackPhase):
    phase = "fair-vote"

    name = _("Collect ideas, get feedback and prioritize")
    description = _(
        "Create new ideas and get feedback through rates, choins and " "comments."
    )

    features = {
        "crud": (models.Idea,),
        "comment": (models.Idea,),
        "rate": (models.Idea,),
        "buy": (models.Idea,),
    }


idea_phases.phases.content.register(FairVotePhase())
