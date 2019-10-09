from django.utils.translation import ugettext_lazy as _

from adhocracy4 import phases

from . import apps
from . import models
from . import views


class IssuePhase(phases.PhaseContent):
    app = apps.Config.label
    phase = 'issue'
    view = views.QuestionModuleDetail

    name = _('Issue phase')
    description = _('Add question.')
    module_name = _('Speak Up')
    icon = 'lightbulb-o'

    features = {
        'crud': (models.Question,),
        'like': (models.Question,)
    }


phases.content.register(IssuePhase())
