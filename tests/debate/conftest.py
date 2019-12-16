from pytest_factoryboy import register

from . import factories as debate_factories

register(debate_factories.SubjectFactory)
