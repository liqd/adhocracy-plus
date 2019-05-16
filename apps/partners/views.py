from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.views.generic import DetailView

from adhocracy4.actions.models import Action
from adhocracy4.projects.models import Project
from adhocracy4.rules import mixins as rules_mixins
from liqd_product.apps.partners.models import Partner
from liqd_product.apps.projects import query

from . import forms


class PartnerView(DetailView):
    template_name = 'partner_landing_page.html'
    model = Partner
    slug_url_kwarg = 'partner_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project_list = Project.objects\
            .filter(organisation__partner=self.object,
                    is_archived=False,
                    is_draft=False)
        project_list = query.filter_viewable(
            project_list, self.request.user
        )
        context['project_list'] = project_list

        context['action_list'] = Action.objects\
            .filter(project__organisation__partner=self.object)\
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
    template_name = 'partner_information.html'
    model = Partner
    slug_url_kwarg = 'partner_slug'


class ImprintView(DetailView):
    template_name = 'partner_imprint.html'
    model = Partner
    slug_url_kwarg = 'partner_slug'


class PartnerUpdateView(rules_mixins.PermissionRequiredMixin,
                        SuccessMessageMixin,
                        generic.UpdateView):
    model = Partner
    form_class = forms.PartnerForm
    slug_url_kwarg = 'partner_slug'
    template_name = 'partner_form.html'
    success_message = _('Organisation successfully updated.')
    permission_required = 'liqd_product_partners.change_partner'
    menu_item = 'partner'

    def get_success_url(self):
        return self.request.path
