from django.conf import settings
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _
from wagtail.models import Site

from apps.cms.settings.models import ImportantPages

LINK_TEXT = _("Please look {}here{} for more information.")


def add_link_to_helptext(help_text, important_page_name, link_text=None):
    site = Site.objects.filter(is_default_site=True).first()
    important_pages = ImportantPages.for_site(site)

    if (
        getattr(important_pages, important_page_name)
        and getattr(important_pages, important_page_name).live
    ):
        url = getattr(important_pages, important_page_name).url
        if not link_text:
            link_text = LINK_TEXT
        link_text = link_text.format('<a href="' + url + '" target="_blank">', "</a>")
        return "{} {}".format(help_text, mark_safe(link_text))

    return help_text


def add_email_link_to_helptext(help_text, link_text=None):
    url = settings.CONTACT_EMAIL

    if not link_text:
        link_text = LINK_TEXT
    link_text = link_text.format('<a href="mailto:' + url + '">', "</a>")
    return mark_safe("{} {}".format(help_text, link_text))

    return help_text


def get_important_page_url(important_page_name):
    site = Site.objects.filter(is_default_site=True).first()
    important_pages = ImportantPages.for_site(site)
    if getattr(important_pages, important_page_name):
        return getattr(important_pages, important_page_name).url
    return None
