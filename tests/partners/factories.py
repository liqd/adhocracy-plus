import factory

from apps.partners import set_partner


class PartnerFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'a4_candy_partners.Partner'
        django_get_or_create = ('name',)

    name = factory.Faker('company')

    @factory.post_generation
    def admins(self, create, extracted, **kwargs):
        from ..factories import UserFactory

        if not extracted:
            user = UserFactory()
            self.admins.add(user)
            return

        if extracted:
            for user in extracted:
                self.admins.add(user)

    @factory.post_generation
    def auto_set_partner(self, create, extracted, **kwargs):
        if extracted is None or extracted:
            set_partner(self)
