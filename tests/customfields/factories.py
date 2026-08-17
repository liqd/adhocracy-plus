import factory

from adhocracy4.test import factories as a4_factories
from apps.customfields import models as customfield_models


class CustomFieldSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = customfield_models.CustomFieldSettings

    module = factory.SubFactory(a4_factories.ModuleFactory)


class CustomFieldFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = customfield_models.CustomField

    settings = factory.SubFactory(CustomFieldSettingsFactory)
    label = factory.Faker("sentence", nb_words=4)
    type = customfield_models.CustomFieldType.OPEN
    required = False


class CustomFieldChoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = customfield_models.CustomFieldChoice

    field = factory.SubFactory(CustomFieldFactory)
    label = factory.Faker("word")
