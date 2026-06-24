from django.shortcuts import redirect
from django.utils.translation import check_for_language
from django.views.generic import FormView
from django.views.generic.detail import DetailView
from django.views.i18n import LANGUAGE_QUERY_PARAMETER
from django.views.i18n import set_language
from guest_user.functions import maybe_create_guest_user

from adhocracy4.actions.models import Action
from apps.organisations.models import Organisation

from . import models
from .forms import GuestCreateForm


class GuestCreateView(FormView):
    form_class = GuestCreateForm
    template_name = "a4_candy_users/guest_create.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        next_url = self.request.POST.get("next")

        if not next_url:
            next_url = self.request.GET.get("next")
        if not next_url:
            next_url = "/"

        return next_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next"] = self.request.GET.get("next", "")
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial["next"] = self.request.GET.get("next", "")
        return initial

    def form_valid(self, form):
        maybe_create_guest_user(self.request)
        return super().form_valid(form)


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
