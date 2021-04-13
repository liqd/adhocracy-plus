from pytest_factoryboy import register

from tests.ideas import factories as idea_factories

register(idea_factories.IdeaFactory)
