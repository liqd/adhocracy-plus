import factory


class PartnerFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'liqd_product_partners.Partner'
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
