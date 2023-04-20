import factory
from django.conf import settings
from django.contrib.auth.hashers import make_password

from adhocracy4.test import factories


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL

    username = factory.Sequence(lambda n: "user%d" % n)
    email = factory.Sequence(lambda n: "user%d@liqd.net" % n)
    password = make_password("password")
    language = "en"


class AdminFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL

    username = factory.Sequence(lambda n: "admin%d" % n)
    email = factory.Sequence(lambda n: "admin%d@liqd.net" % n)
    password = make_password("password")
    is_superuser = True
    language = "en"


class OrganisationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "a4_candy_organisations.Organisation"
        django_get_or_create = ("name",)

    name = factory.Faker("company")
    description = factory.Faker("text")
    imprint = factory.Faker("text")

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
        model = "a4_candy_organisations.Member"

    member = factory.SubFactory(UserFactory)
    organisation = factory.SubFactory(OrganisationFactory)


class OrganisationTermsOfUseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "a4_candy_organisations.OrganisationTermsOfUse"

    user = factory.SubFactory(UserFactory)
    organisation = factory.SubFactory(OrganisationFactory)


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "a4categories.Category"

    name = factory.Faker("job")
    module = factory.SubFactory(factories.ModuleFactory)


class LabelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "a4labels.Label"

    name = factory.Faker("job")
    module = factory.SubFactory(factories.ModuleFactory)


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "a4comments.Comment"

    comment = factory.Faker("text")
    creator = factory.SubFactory(UserFactory)


class RatingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "a4ratings.Rating"

    value = 1
    creator = factory.SubFactory(UserFactory)


class ModeratorFeedbackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "a4_candy_moderatorfeedback.ModeratorFeedback"

    feedback_text = factory.Faker("text")
    creator = factory.SubFactory(UserFactory)


class ReportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "a4reports.Report"

    description = factory.Faker("text")
    creator = factory.SubFactory(UserFactory)
    content_object = factory.SubFactory(CommentFactory)
