from django.contrib.sitemaps import Sitemap

from apps.partners.models import Partner


class ProductPartnersSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Partner.objects.all()
