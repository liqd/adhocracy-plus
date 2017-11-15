import factory
from django.conf import settings
from django.contrib.auth.hashers import make_password

from .partners import factories as partner_factories


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = settings.AUTH_USER_MODEL

    username = factory.Faker('name')
    password = make_password('password')
    email = factory.Faker('email')


class AdminFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = settings.AUTH_USER_MODEL

    username = factory.Faker('name')
    password = make_password('password')
    is_superuser = True


class OrganisationFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'liqd_product_organisations.Organisation'
        django_get_or_create = ('name',)

    name = factory.Faker('company')

    partner = factory.SubFactory(partner_factories.PartnerFactory)

    @factory.post_generation
    def initiators(self, create, extracted, **kwargs):
        if not extracted:
            user = UserFactory()
            self.initiators.add(user)
            return

        if extracted:
            for user in extracted:
                self.initiators.add(user)
