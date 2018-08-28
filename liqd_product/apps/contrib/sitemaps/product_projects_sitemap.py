from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from adhocracy4.projects.models import Project
from liqd_product.apps.partners.models import Partner


class ProductProjectsSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        queryset = Project.objects.none()
        for partner in Partner.objects.all():
            queryset |= Project.objects.filter(
                organisation__partner=partner,
                is_archived=False,
                is_draft=False,
                is_public=True)
        return queryset

    def location(self, obj):
        partner_slug = obj.organisation.partner.slug
        return reverse('project-detail',
                       kwargs=dict(slug=obj.slug, partner_slug=partner_slug))
