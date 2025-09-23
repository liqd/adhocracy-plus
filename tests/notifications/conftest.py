from pytest_factoryboy import register

from tests.budgeting.factories import ProposalFactory
from tests.ideas.factories import IdeaFactory
from tests.offlineevents.factories import OfflineEventFactory
from adhocracy4.test import factories as a4_factories

register(ProposalFactory)
register(IdeaFactory)
register(OfflineEventFactory)
register(a4_factories.PhaseFactory)
