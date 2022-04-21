from pytest_factoryboy import register

from tests.budgeting.factories import ProposalFactory
from tests.ideas.factories import IdeaFactory
from tests.offlineevents.factories import OfflineEventFactory

register(ProposalFactory)
register(IdeaFactory)
register(OfflineEventFactory)
