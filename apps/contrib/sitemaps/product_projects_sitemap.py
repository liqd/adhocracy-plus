from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from adhocracy4.projects.models import Project
from apps.organisations.models import Organisation


class ProductProjectsSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        queryset = Project.objects.none()
        for organisation in Organisation.objects.all():
            queryset |= Project.objects.filter(
                organisation=organisation,
                is_archived=False,
                is_draft=False,
                is_public=True)
        return queryset

    def location(self, obj):
        organisation_slug = obj.organisation.slug
        return reverse('project-detail',
                       kwargs=dict(slug=obj.slug,
                                   organisation_slug=organisation_slug))
