import factory

from apps.classifications import models as classification_models
from tests import factories


class UserClassificationFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = classification_models.UserClassification

    creator = factory.SubFactory(factories.UserFactory)
    classification = 'OFFENSIVE',
    user_message = 'This is bad.'


class AIClassificationFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = classification_models.AIClassification

    classification = 'OFFENSIVE',
