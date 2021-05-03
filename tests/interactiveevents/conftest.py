from pytest_factoryboy import register

from . import factories

register(factories.LiveQuestionFactory)
register(factories.LikeFactory)
register(factories.InteractiveExtraFieldsFactory)
