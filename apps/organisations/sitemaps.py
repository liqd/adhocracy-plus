from django.contrib.sitemaps.views import x_robots_tag
from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404
from django.template.response import TemplateResponse
from django.urls import reverse

from adhocracy4.projects.enums import Access
from adhocracy4.projects.models import Project

from .models import Organisation


@x_robots_tag
def organisations_sitemap_index(request):

    content_type = 'application/xml'
    template_name = 'sitemap_index.xml'

    urls = []
    organisations = Organisation.objects.all().order_by('id')

    for organisation in organisations:
        if not organisation.site or \
                organisation.site is get_current_site(request):
            urls.append(
                request.build_absolute_uri(
                    reverse(
                        'organisation-sitemap-index',
                        kwargs=dict(organisation_slug=organisation.slug)
                    )
                )
            )

    return TemplateResponse(request, template_name, {'sitemaps': urls},
                            content_type=content_type)


@x_robots_tag
def organisation_sitemap_index(request, organisation_slug):

    content_type = 'application/xml'
    template_name = 'sitemap_index.xml'

    urls = []
    sitemaps = [
        'organisation-sitemap-static',
        'organisation-sitemap-projects'
    ]

    for sitemap in sitemaps:
        urls.append(
            request.build_absolute_uri(
                reverse(
                    sitemap,
                    kwargs=dict(organisation_slug=organisation_slug)
                )
            )
        )

    return TemplateResponse(request, template_name, {'sitemaps': urls},
                            content_type=content_type)


@x_robots_tag
def organisation_sitemap_static(request, organisation_slug):

    changefreq = "weekly"
    priority = 0.8
    content_type = 'application/xml'
    template_name = 'sitemap.xml'

    urls = []
    sites = [
        'organisation',
        'organisation-information',
        'organisation-imprint'
    ]

    for site in sites:
        urls.append({
            "location": request.build_absolute_uri(
                reverse(site,
                        kwargs=dict(organisation_slug=organisation_slug))),
            "changefreq": changefreq,
            "priority": priority
        })

    return TemplateResponse(request, template_name, {'urlset': urls},
                            content_type=content_type)


@x_robots_tag
def organisation_sitemap_projects(request, organisation_slug):

    changefreq = "weekly"
    priority = 0.8
    content_type = 'application/xml'
    template_name = 'sitemap.xml'
    organisation = None

    try:
        organisation = Organisation.objects.get(slug=organisation_slug)
    except Organisation.DoesNotExist:
        raise Http404("Organisation does not exist")

    projects = Project.objects.filter(
        organisation=organisation,
        is_archived=False,
        is_draft=False,
        access=Access.PUBLIC)

    urls = []
    for project in projects:
        url = {
            "location": request.build_absolute_uri(project.get_absolute_url()),
            "changefreq": changefreq,
            "priority": priority
        }
        urls.append(url)

    return TemplateResponse(request, template_name, {'urlset': urls},
                            content_type=content_type)
