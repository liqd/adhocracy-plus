import factory

from adhocracy4.test import factories as a4_factories
from apps.interactiveevents import models
from tests.factories import CategoryFactory


class LiveQuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.LiveQuestion

    text = factory.Faker('text', max_nb_chars=50)
    category = factory.SubFactory(CategoryFactory)
    module = factory.SubFactory(a4_factories.ModuleFactory)


class LikeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Like

    livequestion = factory.SubFactory(LiveQuestionFactory)


class InteractiveExtraFieldsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ExtraFieldsInteractiveEvent

    module = factory.SubFactory(a4_factories.ModuleFactory)
