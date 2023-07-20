from pytest_factoryboy import register

from adhocracy4.test.factories import polls as polls_factory
from tests.ideas.factories import IdeaFactory
from tests.interactiveevents import factories as event_factories
from tests.topicprio.factories import TopicFactory

from . import factories as invites

register(IdeaFactory)
register(polls_factory.PollFactory)
register(polls_factory.QuestionFactory)
register(polls_factory.AnswerFactory)
register(polls_factory.ChoiceFactory)
register(polls_factory.VoteFactory)
register(TopicFactory)
register(event_factories.LiveQuestionFactory)
register(event_factories.LikeFactory)

register(invites.ModeratorInviteFactory)
register(invites.ParticipantInviteFactory)
register(invites.ProjectInsightFactory)
