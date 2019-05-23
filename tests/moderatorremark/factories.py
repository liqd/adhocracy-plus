import factory

from adhocracy4.test import factories as a4_factories
from apps.moderatorremark.models import ModeratorRemark
from tests.ideas.factories import IdeaFactory


class ModeratorRemarkFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = ModeratorRemark

    remark = factory.Faker('text')
    item = factory.SubFactory(IdeaFactory)
    creator = factory.SubFactory(a4_factories.USER_FACTORY)
