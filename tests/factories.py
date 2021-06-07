import factory
from django.conf import settings
from django.contrib.auth.hashers import make_password

from adhocracy4 import phases
from adhocracy4.test import factories


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = settings.AUTH_USER_MODEL

    username = factory.Sequence(lambda n: 'user%d' % n)
    email = factory.Sequence(lambda n: 'user%d@liqd.net' % n)
    password = make_password('password')
    language = 'en'


class AdminFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = settings.AUTH_USER_MODEL

    username = factory.Sequence(lambda n: 'admin%d' % n)
    email = factory.Sequence(lambda n: 'admin%d@liqd.net' % n)
    password = make_password('password')
    is_superuser = True
    language = 'en'


class OrganisationFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'a4_candy_organisations.Organisation'
        django_get_or_create = ('name',)

    name = factory.Faker('company')
    description = factory.Faker('text')
    imprint = factory.Faker('text')

    @factory.post_generation
    def initiators(self, create, extracted, **kwargs):
        if not extracted:
            user = UserFactory()
            self.initiators.add(user)
            return

        if extracted:
            for user in extracted:
                self.initiators.add(user)


class MemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'a4_candy_organisations.Member'

    member = factory.SubFactory(UserFactory)
    organisation = factory.SubFactory(OrganisationFactory)


# FIXME: move to core
class PhaseContentFactory(factory.Factory):
    class Meta:
        model = phases.PhaseContent

    app = 'phase_content_factory'
    phase = 'factory_phase'
    view = None

    name = 'Factory Phase'
    description = 'Factory Phase Description'
    module_name = 'factory phase module'

    features = {}

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        phase_content = model_class()
        for key, value in kwargs.items():
            setattr(phase_content, key, value)

        phases.content.register(phase_content)
        return phase_content


# FIXME: move to core
class PhaseFactory(factories.PhaseFactory):

    class Params:
        phase_content = PhaseContentFactory()

    type = factory.LazyAttribute(lambda f: f.phase_content.identifier)


class CategoryFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'a4categories.Category'

    name = factory.Faker('job')
    module = factory.SubFactory(factories.ModuleFactory)


class LabelFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'a4labels.Label'

    name = factory.Faker('job')
    module = factory.SubFactory(factories.ModuleFactory)


class CommentFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'a4comments.Comment'

    comment = factory.Faker('text')
    creator = factory.SubFactory(UserFactory)


class RatingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'a4ratings.Rating'

    value = 1
    creator = factory.SubFactory(UserFactory)


class ModeratorStatementFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'a4_candy_moderatorfeedback.ModeratorStatement'

    statement = factory.Faker('text')
    creator = factory.SubFactory(UserFactory)
