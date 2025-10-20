from pytest_factoryboy import register

from adhocracy4.test import factories as a4_factories
from tests.budgeting.factories import ProposalFactory
from tests.factories import CommentFactory
from tests.factories import ModeratorFeedbackFactory
from tests.ideas.factories import IdeaFactory
from tests.offlineevents.factories import OfflineEventFactory
from tests.projects.factories import ModeratorInviteFactory
from tests.projects.factories import ParticipantInviteFactory

from .factories import NotificationFactory

register(ProposalFactory)
register(IdeaFactory)
register(OfflineEventFactory)
register(a4_factories.PhaseFactory)
register(CommentFactory)
register(ModeratorFeedbackFactory)
register(ParticipantInviteFactory)
register(ModeratorInviteFactory)
register(NotificationFactory)
