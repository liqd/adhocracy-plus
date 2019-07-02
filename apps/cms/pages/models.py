from django.db import models
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel

from apps.contrib.translations import TranslatedField


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

    subtitle_de = models.CharField(
        max_length=500, blank=True, verbose_name="Subtitle")
    subtitle_en = models.CharField(
        max_length=500, blank=True, verbose_name="Subtitle")

    subpage_types = ['a4_candy_cms_pages.EmptyPage']
    body_de = RichTextField(blank=True)
    body_en = RichTextField(blank=True)

    content_panels = [
    body = TranslatedField(
        'body_de',
        'body_en'
    )

    subtitle = TranslatedField(
        'subtitle_de',
        'subtitle_en'
    )
        FieldPanel('title'),
        ImageChooserPanel('image'),
        FieldPanel('subtitle'),
        FieldPanel('body')
    ]

    promote_panels = Page.promote_panels


class EmptyPage(Page):
    subpage_types = ['a4_candy_cms_pages.SimplePage']


class SimplePage(Page):
    body_de = RichTextField()
    body_en = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname='full'),
    body = TranslatedField(
        'body_de',
        'body_en'
    )
    ]

    subpage_types = ['a4_candy_cms_pages.SimplePage']
