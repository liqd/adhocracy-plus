import json

from django.conf import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.views.generic import DetailView

from adhocracy4.dashboard import mixins as a4dashboard_mixins

from . import forms
from .models import Organisation


class OrganisationView(DetailView):
    template_name = 'a4_candy_organisations/organisation_landing_page.html'
    model = Organisation
    slug_url_kwarg = 'organisation_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active, future, past = \
            self.object.get_projects_list(self.request.user)

        context['active_projects'] = active
        context['future_projects'] = future
        context['past_projects'] = past

        project_headline = ''
        if active:
            project_headline = _('Participate now!')
        elif future:
            project_headline = _('Upcoming participation')
        elif past:
            project_headline = _('Ended participation')
        context['project_headline'] = project_headline

        return context


class InformationView(DetailView):
    template_name = 'a4_candy_organisations/organisation_information.html'
    model = Organisation
    slug_url_kwarg = 'organisation_slug'


class ImprintView(DetailView):
    template_name = 'a4_candy_organisations/organisation_imprint.html'
    model = Organisation
    slug_url_kwarg = 'organisation_slug'


class TermsOfUseView(DetailView):
    template_name = 'a4_candy_organisations/organisation_terms_of_use.html'
    model = Organisation
    slug_url_kwarg = 'organisation_slug'


class NetiquetteView(DetailView):
    template_name = 'a4_candy_organisations/organisation_netiquette.html'
    model = Organisation
    slug_url_kwarg = 'organisation_slug'


class DataProtectionView(DetailView):
    template_name = 'a4_candy_organisations/organisation_data_protection.html'
    model = Organisation
    slug_url_kwarg = 'organisation_slug'


class DashboardOrganisationUpdateView(a4dashboard_mixins.DashboardBaseMixin,
                                      SuccessMessageMixin,
                                      generic.UpdateView):
    model = Organisation
    form_class = forms.OrganisationForm
    slug_url_kwarg = 'organisation_slug'
    template_name = 'a4_candy_organisations/organisation_form.html'
    success_message = _('Organisation information successfully updated.')
    permission_required = 'a4_candy_organisations.change_organisation'
    menu_item = 'organisation'

    def get_permission_object(self):
        return self.organisation

    def get_success_url(self):
        return self.request.path

    def get_project_languages(self):
        languages = getattr(settings, 'LANGUAGES', None)
        if languages:
            language_dict = dict((x, str(y)) for x, y in languages)
            return json.dumps(language_dict)
        else:
            raise ImproperlyConfigured('set LANGUAGES in settings')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['language_dict'] = self.get_project_languages()
        return context


class DashboardLegalInformationUpdateView(
        a4dashboard_mixins.DashboardBaseMixin,
        SuccessMessageMixin,
        generic.UpdateView):
    model = Organisation
    form_class = forms.OrganisationLegalInformationForm
    slug_url_kwarg = 'organisation_slug'
    template_name = 'a4_candy_organisations/organisation_form_legal_info.html'
    success_message = _('Legal information successfully updated.')
    permission_required = 'a4_candy_organisations.change_organisation'
    menu_item = 'organisation'

    def get_permission_object(self):
        return self.organisation

    def get_success_url(self):
        return self.request.path
