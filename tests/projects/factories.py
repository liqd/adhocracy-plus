import factory

from adhocracy4.test import factories as a4_factories
from apps.projects import models


class ParticipantInviteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ParticipantInvite

    creator = factory.SubFactory(a4_factories.USER_FACTORY)
    project = factory.SubFactory(a4_factories.ProjectFactory)
    email = factory.Sequence(lambda n: "user%d@liqd.net" % n)


class ModeratorInviteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ModeratorInvite

    creator = factory.SubFactory(a4_factories.USER_FACTORY)
    project = factory.SubFactory(a4_factories.ProjectFactory)
    email = factory.Sequence(lambda n: "user%d@liqd.net" % n)


class ProjectInsightFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ProjectInsight

    project = factory.SubFactory(a4_factories.ProjectFactory)
    comments = 8
    ratings = 4
    written_ideas = 3
    poll_answers = 2
    live_questions = 2
    display = True

    @factory.post_generation
    def active_participants(self, create, extracted, **kwargs):
        if not (create and extracted):
            return
        for participant in extracted:
            self.active_participants.add(participant)
