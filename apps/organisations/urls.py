from django.urls import re_path
from django.views.generic import TemplateView

from . import views
from .sitemaps import organisation_sitemap_index
from .sitemaps import organisation_sitemap_projects
from .sitemaps import organisation_sitemap_static

urlpatterns = [
    re_path(r'^(?P<organisation_slug>[-\w_]+)/$',
            views.OrganisationView.as_view(),
            name='organisation'),
    re_path(r'^(?P<organisation_slug>[-\w_]+)/information/$',
            views.InformationView.as_view(),
            name='organisation-information'),
    re_path(r'^(?P<organisation_slug>[-\w_]+)/imprint/$',
            views.ImprintView.as_view(),
            name='organisation-imprint'),
    re_path(r'^(?P<organisation_slug>[-\w_]+)/sitemap.xml$',
            organisation_sitemap_index,
            name='organisation-sitemap-index'),
    re_path(r'^(?P<organisation_slug>[-\w_]+)/sitemap-static.xml$',
            organisation_sitemap_static,
            name='organisation-sitemap-static'),
    re_path(r'^(?P<organisation_slug>[-\w_]+)/sitemap-projects.xml$',
            organisation_sitemap_projects,
            name='organisation-sitemap-projects'),
    re_path(r'^(?P<organisation_slug>[-\w_]+)/robots.txt$',
            TemplateView.as_view(template_name='robots.txt',
                                 content_type="text/plain"),
            name="robots_file"),
    re_path(r'^(?P<organisation_slug>[-\w_]+)/terms-of-use/$',
            views.TermsOfUseView.as_view(),
            name='organisation-terms-of-use'),
    re_path(r'^(?P<organisation_slug>[-\w_]+)/netiquette/$',
            views.NetiquetteView.as_view(),
            name='organisation-netiquette'),
    re_path(r'^(?P<organisation_slug>[-\w_]+)/data-protection/$',
            views.DataProtectionView.as_view(),
            name='organisation-data-protection'),
]
