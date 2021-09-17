from pytest_factoryboy import register

from adhocracy4.test.factories import polls as factories

register(factories.PollFactory)
register(factories.QuestionFactory)
register(factories.ChoiceFactory)
register(factories.VoteFactory)
