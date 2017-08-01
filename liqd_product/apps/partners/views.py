from django.views.generic import DetailView

from liqd_product.apps.partners.models import Partner


class PartnerView(DetailView):
    template_name = 'partner_landing_page.html'
    model = Partner
    slug_url_kwarg = 'partner_slug'


class AboutView(DetailView):
    template_name = 'partner_about.html'
    model = Partner
    slug_url_kwarg = 'partner_slug'
