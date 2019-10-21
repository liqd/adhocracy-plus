from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.views.generic import DetailView

from adhocracy4.actions.models import Action
from adhocracy4.projects.models import Project
from adhocracy4.rules import mixins as rules_mixins
from apps.projects import query

from . import forms
from .models import Organisation


class OrganisationView(DetailView):
    template_name = 'organisation_landing_page.html'
    model = Organisation
    slug_url_kwarg = 'organisation_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project_list = Project.objects\
            .filter(organisation=self.object,
                    is_archived=False,
                    is_draft=False)
        project_list = query.filter_viewable(
            project_list, self.request.user
        )
        context['project_list'] = project_list

        context['action_list'] = Action.objects\
            .filter(project__organisation=self.object)\
            .filter(project__is_archived=False) \
            .filter_public()\
            .exclude_updates()[:4]

        context['stats'] = {
            'users': 1204,
            'items': 3425,
            'comments': 23234,
            'ratings': 134234,
        }

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
