import factory
from django.utils import timezone

from adhocracy4.test import factories as a4_factories
from apps.offlineevents import models


class OfflineEventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.OfflineEvent

    name = factory.Faker("sentence")
    creator = factory.SubFactory(a4_factories.USER_FACTORY)
    project = factory.SubFactory(a4_factories.ProjectFactory)
    date = factory.LazyFunction(lambda: timezone.now() + timezone.timedelta(days=1))