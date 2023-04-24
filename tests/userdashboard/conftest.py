from pytest_factoryboy import register

from tests.ideas.factories import IdeaFactory
from tests.moderatorfeedback.factories import ModeratorCommentFeedbackFactory

register(IdeaFactory)
register(ModeratorCommentFeedbackFactory)
