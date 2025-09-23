from pytest_factoryboy import register

from tests.budgeting.factories import ProposalFactory
from tests.ideas.factories import IdeaFactory
from tests.offlineevents.factories import OfflineEventFactory
from tests.projects.factories import ModeratorInviteFactory
from tests.factories import CommentFactory
from adhocracy4.test import factories as a4_factories
from tests.factories import ModeratorFeedbackFactory

register(ProposalFactory)
register(IdeaFactory)
register(OfflineEventFactory)
register(a4_factories.PhaseFactory)
register(CommentFactory)
register(ModeratorFeedbackFactory)
register(ModeratorInviteFactory)

