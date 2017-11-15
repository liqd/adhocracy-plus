import factory

from liqd_product.apps.partners import set_partner


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

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        do_set_partner = kwargs.pop('auto_set_partner', True)
        obj = super()._create(model_class, *args, **kwargs)
        if do_set_partner:
            set_partner(obj)
        return obj
