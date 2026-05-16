from django.utils.translation import gettext_lazy as _

from adhocracy4 import phases

from . import apps
from . import models
from . import views


class SuggestionPhase(phases.PhaseContent):
    app = apps.Config.label
    phase = "suggestion"
    view = views.ArpasModuleDetail

    name = _("Suggestion phase")
    description = _("Suggest ideas.")
    module_name = _("Suggest")
    icon = "lightbulb-o"

    features = {}


phases.content.register(SuggestionPhase())
