from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.views.generic import DetailView

from adhocracy4.rules import mixins as rules_mixins

from . import forms
from .models import Organisation


class OrganisationView(DetailView):
    template_name = 'organisation_landing_page.html'
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
    template_name = 'organisation_information.html'
    model = Organisation
    slug_url_kwarg = 'organisation_slug'


class ImprintView(DetailView):
    template_name = 'organisation_imprint.html'
    model = Organisation
    slug_url_kwarg = 'organisation_slug'


class OrganisationUpdateView(rules_mixins.PermissionRequiredMixin,
                             SuccessMessageMixin,
                             generic.UpdateView):
    model = Organisation
    form_class = forms.OrganisationForm
    slug_url_kwarg = 'organisation_slug'
    template_name = 'organisation_form.html'
    success_message = _('Organisation successfully updated.')
    permission_required = 'a4_candy_organisations.change_organisation'
    menu_item = 'organisation'

    def get_success_url(self):
        return self.request.path
