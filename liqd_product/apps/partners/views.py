from django.views.generic import DetailView

from adhocracy4.actions.models import Action
from adhocracy4.projects.models import Project
from liqd_product.apps.partners.models import Partner


class PartnerView(DetailView):
    template_name = 'partner_landing_page.html'
    model = Partner
    slug_url_kwarg = 'partner_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['project_list'] = Project.objects.all()[:3]

        context['action_list'] = Action.objects.all()\
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


class AboutView(DetailView):
    template_name = 'partner_about.html'
    model = Partner
    slug_url_kwarg = 'partner_slug'
