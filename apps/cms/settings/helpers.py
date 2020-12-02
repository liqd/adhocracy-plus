from django.utils.html import mark_safe
from django.utils.translation import ugettext_lazy as _
from wagtail.core.models import Site

from apps.cms.settings.models import ImportantPages

LINK_TEXT = _('Please look {}here{} for more information.')


def add_link_to_helptext(help_text, important_page_name, link_text=None):
    site = Site.objects.filter(
        is_default_site=True
    ).first()
    important_pages = ImportantPages.for_site(site)

    if getattr(important_pages, important_page_name) and \
       getattr(important_pages, important_page_name).live:
        url = getattr(important_pages, important_page_name).url
        if not link_text:
            link_text = LINK_TEXT
        link_text = link_text \
            .format('<a href="' + url + '" target="_blank">', '</a>')
        return '{} {}'.format(help_text, mark_safe(link_text))

    return help_text


def get_important_page_url(important_page_name):
    site = Site.objects.filter(is_default_site=True).first()
    important_pages = ImportantPages.for_site(site)
    if getattr(important_pages, important_page_name):
        return getattr(important_pages, important_page_name).url
    return None


