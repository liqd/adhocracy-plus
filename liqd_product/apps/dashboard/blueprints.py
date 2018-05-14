from django.utils.translation import ugettext_lazy as _

from adhocracy4.dashboard.blueprints import ProjectBlueprint
from meinberlin.apps.activities import phases as activities_phases
from meinberlin.apps.budgeting import phases as budgeting_phases
from meinberlin.apps.documents import phases as documents_phases
from meinberlin.apps.ideas import phases as ideas_phases
from meinberlin.apps.mapideas import phases as mapideas_phases
from meinberlin.apps.polls import phases as poll_phases

blueprints = [
    ('brainstorming',
     ProjectBlueprint(
         title=_('Brainstorming'),
         description=_(
             'Collect first ideas for a specific topic and comment on them.'
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
             'Collect location specific ideas for a topic and comment on them.'
         ),
         content=[
             mapideas_phases.CollectPhase(),
         ],
         image='images/map-brainstorming.svg',
         settings_model=('a4maps', 'AreaSettings'),
     )),
    ('map-idea-collection',
     ProjectBlueprint(
         title=_('Spatial Idea Collection'),
         description=_(
             'Collect location specific ideas that can be rated and commented.'
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
         title=_('Agenda Setting'),
         description=_(
             'With Agenda-Setting it’s possible to identify topics and to '
             'define mission statements. Afterwards anyone can comment and '
             'rate on different topics.'
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
             'In the text-review it’s possible to structure draft texts '
             'that can be commented.'
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
             'Create a poll with multiple questions and possible answers. '
             'Anyone can cast votes and comment on the poll.'
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
             'With participatory-budgeting it’s possible to make proposals '
             'with budget specifications and locate them. Anyone can comment '
             'and rate on different proposals.'),
         content=[
             budgeting_phases.RequestPhase()],
         image='images/participatory-budgeting.svg',
         settings_model=('a4maps', 'AreaSettings'),
     )),
    ('facetoface',
     ProjectBlueprint(
         title=_('Face-to-Face Participation'),
         description=_(
             'With this module you can provide information about events or '
             'phases for face-to-face participation. No online participation '
             'is possible in this module.'
         ),
         content=[
             activities_phases.FaceToFacePhase(),
         ],
         image='images/facetoface.svg',
         settings_model=None,
     )),
]
