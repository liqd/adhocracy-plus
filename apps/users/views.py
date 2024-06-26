from django.utils.translation import check_for_language
from django.views.generic.detail import DetailView
from django.views.i18n import LANGUAGE_QUERY_PARAMETER
from django.views.i18n import set_language

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


def set_language_overwrite(request):
    """Overwrite Djangos set_language to update the user language when switching via
    the language indicator"""
    if request.method == "POST":
        lang_code = request.POST.get(LANGUAGE_QUERY_PARAMETER)
        if lang_code and check_for_language(lang_code):
            user = request.user
            if hasattr(user, "language"):
                if user.language != lang_code:
                    user.language = lang_code
                    user.save()
    return set_language(request)
