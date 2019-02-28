from pytest_factoryboy import register

from . import factories as ideas_factories

register(ideas_factories.IdeaFactory)
