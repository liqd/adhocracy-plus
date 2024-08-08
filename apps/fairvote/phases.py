from django.utils.translation import gettext_lazy as _

from apps.ideas import phases as idea_phases

from . import models


class FairVotePhase(idea_phases.CollectFeedbackPhase):
    phase = "fair-vote"

    name = _("Suggest ideas and vote for others' ideas")
    description = _(
        "You can add ideas, discuss them, and vote for them in a single phase."
    )

    features = {
        "crud": (models.Idea,),
        "comment": (models.Idea,),
        "rate": (models.Idea,),
        "buy": (models.Idea,),
    }


idea_phases.phases.content.register(FairVotePhase())
