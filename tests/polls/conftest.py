from pytest_factoryboy import register

from adhocracy4.test.factories import polls as factories
from tests.projects.factories import ProjectInsightFactory

register(factories.AnswerFactory)
register(factories.OpenQuestionFactory, "open_question")
register(factories.QuestionFactory)
register(factories.ChoiceFactory)
register(factories.PollFactory)
register(ProjectInsightFactory)
