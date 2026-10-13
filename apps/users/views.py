import time
from datetime import date
from datetime import datetime

from allauth.account import views as allauth_account_views
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.translation import check_for_language
from django.views.generic import FormView
from django.views.generic.detail import DetailView
from django.views.i18n import LANGUAGE_QUERY_PARAMETER
from django.views.i18n import set_language
from guest_user.functions import is_guest_user
from guest_user.functions import maybe_create_guest_user

from adhocracy4.actions.models import Action
from apps.organisations.models import Organisation

from . import models
from .constants import GUEST_SWITCH_QUERY_PARAM
from .forms import SIGNUP_LAST_STEP
from .forms import SIGNUP_STEP_FIELDS
from .forms import GuestCreateForm
from .forms import restrict_fields_to_step
from .forms import signup_error_step

# Session key that holds the data collected during the multi step signup.
SIGNUP_WIZARD_SESSION_KEY = "signup_wizard"
SIGNUP_WIZARD_NEXT_KEY = "next"
SIGNUP_WIZARD_TIMESTAMP_KEY = "staged_at"
# Staged data expires so that a plaintext password does not linger in the
# (database backed) session when a user abandons the wizard.
SIGNUP_WIZARD_MAX_AGE = 30 * 60
# Fields collected on an earlier step are staged in the session and merged
# into the final (django-allauth) signup form. Derived from the single
# field -> step map so the two can never drift apart.
SIGNUP_WIZARD_DATA_FIELDS = tuple(
    name for name, step in SIGNUP_STEP_FIELDS.items() if step < SIGNUP_LAST_STEP
)


class LogoutView(allauth_account_views.LogoutView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["guest_switch_logout"] = (
            self.request.user.is_authenticated
            and is_guest_user(self.request.user)
            and self.request.GET.get(GUEST_SWITCH_QUERY_PARAM) == "1"
        )
        return context


# Bare project-wide layout used when an account view is requested via htmx
# (button click) instead of a regular navigation. The full page keeps using
# account/base.html. Both modes render the very same content template, they
# only switch layout.
AUTH_MODAL_LAYOUT = "partial.html"
# Id of the element inside the global auth modal that htmx swaps into. It is
# used to tell a modal open apart from the wizard's own step navigation (which
# targets ``#signup-wizard``).
AUTH_MODAL_TARGET = "auth-modal-body"


class AuthModalMixin:
    """Serve an account view either as a full page or as a modal fragment.

    A regular request (opening the URL directly) renders the complete page. An
    htmx request (clicking a login/registration button anywhere) renders the
    same content through the bare ``partial.html`` layout so it can be swapped
    into the global ``#auth-modal``.
    """

    def is_modal_request(self):
        return bool(self.request.headers.get("HX-Request"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.is_modal_request():
            context["layout"] = AUTH_MODAL_LAYOUT
            context["is_modal"] = True
        return context

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        return self.convert_redirect_for_modal(response)

    def convert_redirect_for_modal(self, response):
        """Turn a redirect into an htmx ``HX-Redirect`` for modal requests.

        Without this, htmx follows a 3xx transparently and swaps the redirect
        target's full page into ``#auth-modal-body``. This happens for example
        when an already authenticated user opens login/registration from a
        stale page or a second tab.
        """
        if self.is_modal_request() and getattr(response, "status_code", None) in (
            301,
            302,
        ):
            location = response.headers.get("Location")
            if location:
                hx_response = HttpResponse(status=200)
                hx_response["HX-Redirect"] = location
                return hx_response
        return response


class LoginView(AuthModalMixin, allauth_account_views.LoginView):
    template_name = "account/login.html"


class SignupWizardView(AuthModalMixin, allauth_account_views.SignupView):
    """Multi step registration on top of django-allauth.

    Steps 1 (email/username) and 2 (password) are validated on their own and
    stored in the server side session. The last step (captcha/checkboxes)
    submits the complete, merged form to the regular allauth signup flow, so
    email verification, rate limiting, newsletter opt-in and the bot trap keep
    working unchanged.
    """

    template_name = "account/signup.html"

    def get(self, request, *args, **kwargs):
        requested_step = request.GET.get("step")
        session_data = self._session_data(request)
        if requested_step in ("1", "2", "3") and session_data:
            step = int(requested_step)
            form = (
                self._complete_form()
                if step == 3
                else self._step_form(step, initial=session_data)
            )
            return self._render_wizard(request, step, form)

        # A fresh start always discards data from a previous attempt.
        request.session.pop(SIGNUP_WIZARD_SESSION_KEY, None)
        next_url = request.GET.get("next") or request.POST.get("next")
        if next_url:
            request.session[SIGNUP_WIZARD_SESSION_KEY] = {
                SIGNUP_WIZARD_NEXT_KEY: next_url
            }
        initial = self._email_initial()
        return self._render_wizard(request, 1, self._step_form(1, initial=initial))

    def post(self, request, *args, **kwargs):
        step = request.POST.get("signup_step")
        if step in ("1", "2"):
            return self._process_step(request, int(step))
        # Step 3 (or a legacy direct post) is handled by allauth.
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        form = kwargs.get("form")
        if form is not None and "email" in form.fields:
            # allauth may pre-fill a verified email; that is safe here because
            # the current step actually renders the email field.
            return super().get_context_data(**kwargs)
        # On steps without that field allauth's pre-fill would raise, so hide
        # it for the rendering and restore it afterwards.
        session = self.request.session
        verified_email = session.pop("account_verified_email", None)
        try:
            return super().get_context_data(**kwargs)
        finally:
            if verified_email:
                session["account_verified_email"] = verified_email

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method == "POST" and self.request.POST.get(
            "signup_step"
        ) not in ("1", "2"):
            session_data = self._session_data(self.request)
            if session_data:
                data = self.request.POST.copy()
                for name in SIGNUP_WIZARD_DATA_FIELDS:
                    if name in session_data and not data.get(name):
                        data[name] = session_data[name]
                if not data.get(SIGNUP_WIZARD_NEXT_KEY) and session_data.get(
                    SIGNUP_WIZARD_NEXT_KEY
                ):
                    data[SIGNUP_WIZARD_NEXT_KEY] = session_data[SIGNUP_WIZARD_NEXT_KEY]
                kwargs["data"] = data
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.session.pop(SIGNUP_WIZARD_SESSION_KEY, None)
        return response

    def form_invalid(self, form):
        step = signup_error_step(form)
        return self._render_wizard(self.request, step, form)

    def _process_step(self, request, step):
        form = self._step_form(step, data=request.POST)
        if form.is_valid():
            self._store_step_data(request, form.cleaned_data)
            if step == 1:
                return self._render_wizard(request, 2, self._step_form(2))
            return self._render_wizard(request, 3, self._complete_form())
        return self._render_wizard(request, step, form)

    def _store_step_data(self, request, cleaned_data):
        data = dict(request.session.get(SIGNUP_WIZARD_SESSION_KEY) or {})
        for name in SIGNUP_WIZARD_DATA_FIELDS:
            if name in cleaned_data:
                value = cleaned_data[name]
                # Dates are not JSON serializable (the default session
                # serializer), so keep them as ISO strings; the matching form
                # field parses them again on the final submit.
                if isinstance(value, (date, datetime)):
                    value = value.isoformat()
                data[name] = value
        next_url = request.POST.get(SIGNUP_WIZARD_NEXT_KEY)
        if next_url:
            data[SIGNUP_WIZARD_NEXT_KEY] = next_url
        data[SIGNUP_WIZARD_TIMESTAMP_KEY] = time.time()
        request.session[SIGNUP_WIZARD_SESSION_KEY] = data

    def _session_data(self, request):
        """Return the staged wizard data, dropping it once it is stale."""
        data = request.session.get(SIGNUP_WIZARD_SESSION_KEY) or {}
        staged_at = data.get(SIGNUP_WIZARD_TIMESTAMP_KEY)
        if staged_at and time.time() - staged_at > SIGNUP_WIZARD_MAX_AGE:
            request.session.pop(SIGNUP_WIZARD_SESSION_KEY, None)
            return {}
        return data

    def _email_initial(self):
        """Support allauth's ``?email=`` pre-fill on the first step."""
        email = self.request.GET.get("email")
        if not email:
            return None
        try:
            validate_email(email)
        except ValidationError:
            return None
        return {"email": email}

    def _step_form(self, step, data=None, initial=None):
        form = self.get_form_class()(data=data, initial=initial)
        return restrict_fields_to_step(form, step)

    def _complete_form(self):
        form = self.get_form_class()()
        initial = dict(self._session_data(self.request))
        for name in ("password1", "password2"):
            initial.pop(name, None)
        form.initial.update(initial)
        return form

    def _next_url(self, request):
        session_data = self._session_data(request)
        return (
            session_data.get(SIGNUP_WIZARD_NEXT_KEY)
            or request.GET.get(SIGNUP_WIZARD_NEXT_KEY)
            or request.POST.get(SIGNUP_WIZARD_NEXT_KEY)
            or ""
        )

    def _render_wizard(self, request, step, form):
        context = self.get_context_data(form=form)
        context["step_form"] = form
        context["signup_step"] = step
        context["signup_media"] = self.get_form_class()().media
        context["redirect_field_name"] = SIGNUP_WIZARD_NEXT_KEY
        context["redirect_field_value"] = self._next_url(request)
        # When the wizard is opened inside the auth modal (the button targets
        # ``#auth-modal-body``) the whole content template is needed so the
        # ``#signup-wizard`` wrapper and the captcha media are present. The
        # wizard's own step navigation targets ``#signup-wizard`` and only
        # swaps the bare fragment, so the media is not reloaded on every step.
        if self.is_modal_request() and self._is_modal_target(request):
            return render(request, self.template_name, context)
        if request.headers.get("HX-Request"):
            return render(request, "account/signup/_wizard.html", context)
        return render(request, self.template_name, context)

    @staticmethod
    def _is_modal_target(request):
        return request.headers.get("HX-Target") == AUTH_MODAL_TARGET


class GuestCreateView(AuthModalMixin, FormView):
    form_class = GuestCreateForm
    template_name = "a4_candy_users/guest_create.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return self.convert_redirect_for_modal(redirect("/"))
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
        if self.request.user.is_anonymous:
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
