import factory

from adhocracy4.test import factories as a4_factories
from apps.likes import models as likes_models
from apps.questions import models as question_models
from tests.factories import CategoryFactory


class QuestionFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = question_models.Question

    text = factory.Faker('text', max_nb_chars=50)
    category = factory.SubFactory(CategoryFactory)
    module = factory.SubFactory(a4_factories.ModuleFactory)


class LikeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = likes_models.Like

    question = factory.SubFactory(QuestionFactory)
