from django.views.generic.detail import DetailView

from adhocracy4.actions.models import Action
from apps.organisations.models import Organisation

from . import models


class ProfileView(DetailView):
    model = models.User
    slug_field = "username"

    @property
    def projects_carousel(self):
        (
            sorted_active_projects,
            sorted_future_projects,
            sorted_past_projects,
        ) = self.object.get_projects_follow_list(exclude_private_projects=True)
        return (
            list(sorted_active_projects)
            + list(sorted_future_projects)
            + list(sorted_past_projects)
        )[:6]

    @property
    def organisations(self):
        return Organisation.objects.filter(
            project__follow__creator=self.object, project__follow__enabled=True
        ).distinct()

    @property
    def actions(self):
        return (
            Action.objects.filter(
                actor=self.object,
            )
            .filter_public()
            .exclude_updates()[:25]
        )
