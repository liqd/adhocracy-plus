from django.utils.translation import ugettext_lazy as _

from adhocracy4.dashboard.blueprints import ProjectBlueprint
from apps.budgeting import phases as budgeting_phases
from apps.documents import phases as documents_phases
from apps.ideas import phases as ideas_phases
from apps.mapideas import phases as mapideas_phases
from apps.polls import phases as poll_phases
from apps.questions import phases as question_phases
from apps.topicprio import phases as topicprio_phases

blueprints = [
    ('brainstorming',
     ProjectBlueprint(
         title=_('Brainstorming'),
         description=_(
             'Collect ideas and let participants comment on them.'
         ),
         content=[
             ideas_phases.CollectPhase(),
         ],
         image='images/brainstorming.svg',
         settings_model=None,
     )),
    ('map-brainstorming',
     ProjectBlueprint(
         title=_('Spatial Brainstorming'),
         description=_(
             'Collect ideas associated with a location within a pre-defined '
             'area on a map.'
         ),
         content=[
             mapideas_phases.CollectPhase(),
         ],
         image='images/map-brainstorming.svg',
         settings_model=('a4maps', 'AreaSettings'),
     )),
    ('map-idea-collection',
     ProjectBlueprint(
         title=_('Spatial Idea Challenge'),
         description=_(
             'Collect ideas on a pre-defined area on a map and let '
             'participants rate them in a second step.'
         ),
         content=[
             mapideas_phases.CollectPhase(),
             mapideas_phases.RatingPhase()
         ],
         image='images/map-idea-collection.svg',
         settings_model=('a4maps', 'AreaSettings'),
     )),
    ('agenda-setting',
     ProjectBlueprint(
         title=_('Idea Challenge'),
         description=_(
             'Collect ideas and let participants rate and comment on them in'
             ' a second step.'
         ),
         content=[
             ideas_phases.CollectPhase(),
             ideas_phases.RatingPhase(),
         ],
         image='images/agenda-setting.svg',
         settings_model=None,
     )),
    ('text-review',
     ProjectBlueprint(
         title=_('Text Review'),
         description=_(
             'Let participants comment on paragraphs of a pre-defined text.'
         ),
         content=[
             documents_phases.CommentPhase(),
         ],
         image='images/text-review.svg',
         settings_model=None,
     )),
    ('poll',
     ProjectBlueprint(
         title=_('Poll'),
         description=_(
             'Let participants answer a poll of pre-defined multiple choice '
             'questions.'
         ),
         content=[
             poll_phases.VotingPhase(),
         ],
         image='images/poll.svg',
         settings_model=None,
     )),
    ('participatory-budgeting',
     ProjectBlueprint(
         title=_('Participatory budgeting'),
         description=_(
             'Collect ideas with a budget proposal from participants. The '
             'ideas can be located on a pre-defined map.'),
         content=[
             budgeting_phases.RequestPhase()],
         image='images/participatory-budgeting.svg',
         settings_model=('a4maps', 'AreaSettings'),
     )),
    ('speakup',
     ProjectBlueprint(
         title=_('Speak Up'),
         description=_(
             'Collect questions for your discussion.'
         ),
         content=[
             question_phases.IssuePhase(),
         ],
         image='images/brainstorming.svg',
         settings_model=None,
     )),
    ('topic-prioritization',
     ProjectBlueprint(
         title=_('Topic Priorization'),
         description=_(
             'Comment and prioritize topics.'
         ),
         content=[
             topicprio_phases.PrioritizePhase(),
         ],
         image='images/priorization.svg',
         settings_model=None,
     )),
]
