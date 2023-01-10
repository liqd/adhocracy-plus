from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.views.generic.base import RedirectView

from apps.users.models import User
from apps.users.utils import set_session_language

from . import forms


class AccountView(RedirectView):
    permanent = False
    pattern_name = "account_profile"
    # Placeholder View to be replaced if we want to use a custom account
    # dashboard function overview.


class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView):

    model = User
    template_name = "a4_candy_account/profile.html"
    form_class = forms.ProfileForm
    success_message = _("Your profile was successfully updated.")

    def get_object(self):
        return get_object_or_404(User, pk=self.request.user.id)

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        set_session_language(
            self.request.user.email, form.cleaned_data["language"], self.request
        )
        return super(ProfileUpdateView, self).form_valid(form)


class OrganisationTermsOfUseUpdateView(
    LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView
):

    model = User
    template_name = "a4_candy_account/user_agreements.html"
    form_class = forms.OrganisationTermsOfUseForm
    success_message = _("Your agreements were successfully updated.")

    def get_object(self):
        return get_object_or_404(User, pk=self.request.user.id)

    def get_success_url(self):
        return self.request.path

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["formset"] = forms.OrganisationTermsOfUseFormSet(
                self.request.POST, instance=self.get_object()
            )
        else:
            context["formset"] = forms.OrganisationTermsOfUseFormSet(
                instance=self.get_object()
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]
        with transaction.atomic():
            if formset.is_valid():
                formset.instance = self.get_object()
                formset.save()
        return super().form_valid(form)
