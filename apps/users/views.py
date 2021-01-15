from django.db.models import Q
from django.views.generic.detail import DetailView

from adhocracy4.actions.models import Action
from adhocracy4.projects.enums import Access
from adhocracy4.projects.models import Project
from apps.organisations.models import Organisation

from . import models


class ProfileView(DetailView):
    model = models.User
    slug_field = 'username'

    @property
    def projects(self):
        return Project.objects \
            .filter(follow__creator=self.object,
                    follow__enabled=True,
                    is_draft=False) \
            .filter(Q(access=Access.PUBLIC) |
                    Q(access=Access.SEMIPUBLIC))

    @property
    def organisations(self):
        return Organisation.objects.filter(
            project__follow__creator=self.object,
            project__follow__enabled=True
        ).distinct()

    @property
    def actions(self):
        return Action.objects.filter(
            actor=self.object,
        ).filter_public().exclude_updates()
