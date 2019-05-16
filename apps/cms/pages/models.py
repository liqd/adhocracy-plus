from django.db import models
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel


class HomePage(Page):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Header Image",
        help_text="The Image that is shown on top of the page"
    )
    subtitle = models.CharField(
        max_length=500, blank=True, verbose_name="Subtitle")
    body = RichTextField(blank=True)

    subpage_types = ['liqd_product_cms_pages.EmptyPage']

    content_panels = [
        FieldPanel('title'),
        ImageChooserPanel('image'),
        FieldPanel('subtitle'),
        FieldPanel('body')
    ]

    promote_panels = Page.promote_panels


class EmptyPage(Page):
    subpage_types = ['liqd_product_cms_pages.SimplePage']


class SimplePage(Page):
    body = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('body', classname='full'),
    ]

    subpage_types = ['liqd_product_cms_pages.SimplePage']
