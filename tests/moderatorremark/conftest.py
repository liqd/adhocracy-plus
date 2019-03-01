from pytest_factoryboy import register

from tests.ideas import factories as ideas_factories

from . import factories as moderatorremarks_factories

register(ideas_factories.IdeaFactory)
register(moderatorremarks_factories.ModeratorRemarkFactory)
