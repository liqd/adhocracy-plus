from django.contrib.sitemaps import Sitemap

from apps.organisations.models import Organisation


class ProductOrganisationsSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Organisation.objects.all()
