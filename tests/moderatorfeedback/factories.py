import factory

from adhocracy4.test import factories as a4_factories
from apps.moderatorfeedback.models import ModeratorCommentFeedback
from tests.factories import CommentFactory


class ModeratorCommentFeedbackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ModeratorCommentFeedback

    feedback_text = factory.Faker("text")
    comment = factory.SubFactory(CommentFactory)
    creator = factory.SubFactory(a4_factories.USER_FACTORY)
