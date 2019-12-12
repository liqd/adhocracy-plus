from django.contrib.sitemaps.views import x_robots_tag
from django.template.response import TemplateResponse
from django.urls import reverse


@x_robots_tag
def static_sitemap_index(request):

    content_type = 'application/xml'
    template_name = 'sitemap_index.xml'

    urls = []
    sitemaps = [
        'wagtail-sitemap',
        'organisations-sitemap-index'
    ]

    for sitemap in sitemaps:
        urls.append(
            request.build_absolute_uri(
                reverse(sitemap)
            )
        )

    return TemplateResponse(request, template_name, {'sitemaps': urls},
                            content_type=content_type)
