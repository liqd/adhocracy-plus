from django.utils.translation import gettext_lazy as _

from adhocracy4 import phases

from apps.ideas.models import Idea

from . import apps
from . import views


class RankPhase(phases.PhaseContent):
    """Ranking phase of the ranked-choice blueprint.

    Participants rank the ideas collected in the preceding collect phase.
    """

    app = apps.Config.label
    phase = "rank"
    view = views.RankedChoiceDetailView

    name = _("Ranking phase")
    description = _("Rank the collected ideas according to your preference.")
    module_name = _("ranked-choice")

    features = {
        "rank": (Idea,),
    }


phases.content.register(RankPhase())