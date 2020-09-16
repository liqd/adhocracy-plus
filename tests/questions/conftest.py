from pytest_factoryboy import register

from . import factories as question_factories

register(question_factories.QuestionFactory)
register(question_factories.LikeFactory)
