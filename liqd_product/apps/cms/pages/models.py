from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page


class HomePage(Page):
    subpage_types = ['liqd_product_cms_pages.EmptyPage']


class EmptyPage(Page):
    subpage_types = ['liqd_product_cms_pages.SimplePage']


class SimplePage(Page):
    body = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full"),
    ]

    subpage_types = ['liqd_product_cms_pages.SimplePage']
