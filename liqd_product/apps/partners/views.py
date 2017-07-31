from django.views.generic import DetailView

from adhocracy4.actions.models import Action
from liqd_product.apps.partners.models import Partner


class PartnerView(DetailView):
    template_name = 'partner_landing_page.html'
    model = Partner
    slug_url_kwarg = 'partner_slug'

    def get_context_data(self, **kwargs):
        context = super(PartnerView, self).get_context_data(**kwargs)
        # FIXME: limit to current partner
        context['action_list'] = Action.objects.all()[:10]
        return context
