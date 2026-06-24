from allauth.account.utils import complete_signup
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
from guest_user.functions import is_guest_user
from guest_user.mixins import GuestUserRequiredMixin
from guest_user.mixins import RegularUserRequiredMixin
from guest_user.views import ConvertFormView

from apps.users.forms import GuestConvertForm
from apps.users.models import User
from apps.users.utils import set_session_language

from . import forms
from .emails import AccountDeletionEmail


class AccountView(RegularUserRequiredMixin, RedirectView):
    permanent = False
    pattern_name = "account_profile"


class ProfileUpdateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    RegularUserRequiredMixin,
    generic.UpdateView,
):
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


class GuestConvertView(
    SuccessMessageMixin, GuestUserRequiredMixin, ConvertFormView, generic.FormView
):
    template_name = "a4_candy_account/guest_convert.html"
    form_class = GuestConvertForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        if "instance" in kwargs:
            del kwargs["instance"]
        return kwargs

    def form_valid(self, form):
        user = form.save(self.request)
        response = complete_signup(
            self.request,
            user,
            email_verification=settings.ACCOUNT_EMAIL_VERIFICATION,
            success_url=settings.LOGIN_REDIRECT_URL,
        )
        return response


class AccountDeletionView(LoginRequiredMixin, SuccessMessageMixin, generic.DeleteView):
    template_name = "a4_candy_account/account_deletion.html"
    form_class = forms.AccountDeletionForm
    success_message = _("Your account was successfully deleted.")
    success_url = "/"

    def get_object(self):
        return get_object_or_404(User, pk=self.request.user.id)

    def get_form_class(self):
        if is_guest_user(self.request.user):
            return forms.GuestAccountDeletionForm
        return forms.AccountDeletionForm

    def form_valid(self, form):
        user = self.request.user
        password = form.cleaned_data.get("password")
        if not is_guest_user(user) and not user.check_password(password):
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
