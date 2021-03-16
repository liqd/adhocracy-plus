from django.utils.translation import ugettext_lazy as _

from adhocracy4.dashboard.blueprints import ProjectBlueprint
from apps.budgeting import phases as budgeting_phases
from apps.debate import phases as debate_phases
from apps.documents import phases as documents_phases
from apps.ideas import phases as ideas_phases
from apps.interactiveevents import phases as interactiveevent_phases
from apps.mapideas import phases as mapideas_phases
from apps.polls import phases as poll_phases
from apps.topicprio import phases as topicprio_phases

blueprints = [
    ('brainstorming',
     ProjectBlueprint(
         title=_('Brainstorming'),
         description=_(
             'Participants can submit their own ideas and discuss the '
             'ideas of others.'
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
             'Participants can submit their own ideas and locate them on a '
             'map. They can also discuss the ideas of others.'
         ),
         content=[
             mapideas_phases.CollectPhase(),
         ],
         image='images/map-brainstorming.svg',
         settings_model=('a4maps', 'AreaSettings'),
     )),
    ('agenda-setting',
     ProjectBlueprint(
         title=_('Idea Challenge'),
         description=_(
             'In a first phase, participants can submit their own ideas '
             'and discuss the ideas of others. In a second phase, the '
             'ideas can be rated (pro/contra).'
         ),
         content=[
             ideas_phases.CollectPhase(),
             ideas_phases.RatingPhase(),
         ],
         image='images/agenda-setting.svg',
         settings_model=None,
     )),
    ('map-idea-collection',
     ProjectBlueprint(
         title=_('Spatial Idea Challenge'),
         description=_(
             'In a first phase, participants can submit their own ideas, '
             'mark them on a map, and discuss the ideas of others. In a '
             'second phase, the ideas can be rated (pro/contra).'
         ),
         content=[
             mapideas_phases.CollectPhase(),
             mapideas_phases.RatingPhase()
         ],
         image='images/map-idea-collection.svg',
         settings_model=('a4maps', 'AreaSettings'),
     )),
    ('text-review',
     ProjectBlueprint(
         title=_('Text Review'),
         description=_(
             'Participants can discuss the paragraphs of a text that you '
             'added beforehand.'
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
             'Participants can answer one or more questions with '
             'predefined choices.'
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
             'Participants can submit their own suggestions, mark them on '
             'a map, and add a budget. The ideas of others can be '
             'discussed and rated (pro/contra).'
         ),
         content=[
             budgeting_phases.RequestPhase()],
         image='images/participatory-budgeting.svg',
         settings_model=('a4maps', 'AreaSettings'),
     )),
    ('interactive-event',
     ProjectBlueprint(
         title=_('Interactive Event'),
         description=_(
             'The participants of an event can ask their questions online. '
             'Other participants can support the question. You as the '
             'moderator can sort the questions by support or '
             'affiliation.'
         ),
         content=[
             interactiveevent_phases.IssuePhase(),
         ],
         image='images/live-discussion.svg',
         settings_model=None,
     )),
    ('topic-prioritization',
     ProjectBlueprint(
         title=_('Prioritization'),
         description=_(
             'Participants can discuss and rate (pro/contra) previously '
             'added ideas and topics. Participants cannot add ideas or '
             'topics.'
         ),
         content=[
             topicprio_phases.PrioritizePhase(),
         ],
         image='images/priorization.svg',
         settings_model=None,
     )),
    ('debate',
     ProjectBlueprint(
         title=_('Debate'),
         description=_(
             'Participants can discuss posted topics or questions. '
             'To do this, the participants comment on posted '
             'topics / questions as well as on contributions from other '
             'users.'

         ),
         content=[
             debate_phases.DebatePhase(),
         ],
         image='images/debate.svg',
         settings_model=None,
     )),
]
