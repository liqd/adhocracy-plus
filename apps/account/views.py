from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.views.generic.base import RedirectView

from apps.users.models import User
from apps.users.utils import set_session_language

from . import forms
from .emails import AccountDeletionEmail


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
        set_session_language(self.request.user.email, form.cleaned_data["language"])
        return super(ProfileUpdateView, self).form_valid(form)

    def render_to_response(self, context, **response_kwargs):
        set_session_language(self.request.user.email, self.request.user.language)
        response = super().render_to_response(context, **response_kwargs)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, self.request.user.language)
        return response


class AccountDeletionView(LoginRequiredMixin, SuccessMessageMixin, generic.DeleteView):
    template_name = "a4_candy_account/account_deletion.html"
    form_class = forms.AccountDeletionForm
    success_message = _("Your account was successfully deleted.")
    success_url = "/"

    def get_object(self):
        return get_object_or_404(User, pk=self.request.user.id)

    def form_valid(self, form):
        user = self.request.user
        password = form.cleaned_data.get("password")
        if not user.check_password(password):
            form.add_error(
                "password", ValidationError("Incorrect password.", "invalid")
            )
            return super().form_invalid(form)
        logout(self.request)
        AccountDeletionEmail.send(user)
        return super().form_valid(form)


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
