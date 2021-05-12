import random

from django.db import models
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.admin.edit_handlers import MultiFieldPanel
from wagtail.admin.edit_handlers import ObjectList
from wagtail.admin.edit_handlers import PageChooserPanel
from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.admin.edit_handlers import TabbedInterface
from wagtail.core import blocks
from wagtail.core import fields
from wagtail.core.models import Page
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel

from apps.cms import blocks as cms_blocks
from apps.cms.news.blocks import NewsBlock
from apps.cms.use_cases.blocks import UseCaseBlock
from apps.contrib.translations import TranslatedField
from apps.contrib.translations import TranslatedFieldLegal


class HomePage(Page):

    image_1 = models.ForeignKey(
        'a4_candy_cms_images.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Header Image 1",
        help_text="The Image that is shown on top of the page"
    )

    image_2 = models.ForeignKey(
        'a4_candy_cms_images.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Header Image 2",
        help_text="The Image that is shown on top of the page"
    )

    image_3 = models.ForeignKey(
        'a4_candy_cms_images.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Header Image 3",
        help_text="The Image that is shown on top of the page"
    )

    image_4 = models.ForeignKey(
        'a4_candy_cms_images.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Header Image 4",
        help_text="The Image that is shown on top of the page"
    )

    image_5 = models.ForeignKey(
        'a4_candy_cms_images.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Header Image 5",
        help_text="The Image that is shown on top of the page"
    )

    form_page = models.ForeignKey(
        'a4_candy_cms_contacts.FormPage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    hero_title_de = models.CharField(
        max_length=80, blank=True, verbose_name="Hero title")
    hero_title_en = models.CharField(
        max_length=80, blank=True, verbose_name="Hero title")

    hero_subtitle_de = fields.RichTextField(
        max_length=150, blank=True, features=['h3', 'bold', 'italic', 'link'])
    hero_subtitle_en = fields.RichTextField(
        max_length=150, blank=True, features=['h3', 'bold', 'italic', 'link'])

    body_de = fields.RichTextField(blank=True)
    body_en = fields.RichTextField(blank=True)

    body_streamfield_de = fields.StreamField([
        ('col_list_image_cta_block', cms_blocks.ColumnsImageCTABlock()),
        ('background_cta_block', cms_blocks.ColBackgroundCTABlock()),
        ('columns_cta', cms_blocks.ColumnsCTABlock()),
        ('html', blocks.RawHTMLBlock()),
        ('paragraph', blocks.RichTextBlock()),
        ('news', NewsBlock()),
        ('use_cases', UseCaseBlock())
    ], blank=True)

    body_streamfield_en = fields.StreamField([
        ('col_list_image_cta_block', cms_blocks.ColumnsImageCTABlock()),
        ('background_cta_block', cms_blocks.ColBackgroundCTABlock()),
        ('columns_cta', cms_blocks.ColumnsCTABlock()),
        ('html', blocks.RawHTMLBlock()),
        ('paragraph', blocks.RichTextBlock()),
        ('news', NewsBlock()),
        ('use_cases', UseCaseBlock())
    ], blank=True)

    hero_title = TranslatedField(
        'hero_title_de',
        'hero_title_en'
    )

    hero_subtitle = TranslatedField(
        'hero_subtitle_de',
        'hero_subtitle_en'
    )

    body_streamfield = TranslatedField(
        'body_streamfield_de',
        'body_streamfield_en'
    )

    body = TranslatedField(
        'body_de',
        'body_en'
    )

    @property
    def form(self):
        return self.form_page.get_form()

    @property
    def random_image(self):
        image_numbers = [i for i in range(1, 6)
                         if getattr(self, 'image_{}'.format(i))]
        if image_numbers:
            return getattr(self,
                           'image_{}'.format(random.choice(image_numbers)))

    en_content_panels = [
        FieldPanel('hero_title_en'),
        FieldPanel('hero_subtitle_en'),
        FieldPanel('body_en'),
        StreamFieldPanel('body_streamfield_en')
    ]

    de_content_panels = [
        FieldPanel('hero_title_de'),
        FieldPanel('hero_subtitle_de'),
        FieldPanel('body_de'),
        StreamFieldPanel('body_streamfield_de')
    ]

    common_panels = [
        FieldPanel('title'),
        FieldPanel('slug'),
        PageChooserPanel('form_page', 'a4_candy_cms_contacts.FormPage'),
        MultiFieldPanel(
            [
                ImageChooserPanel('image_1'),
                ImageChooserPanel('image_2'),
                ImageChooserPanel('image_3'),
                ImageChooserPanel('image_4'),
                ImageChooserPanel('image_5'),
            ],
            heading="Images",
            classname="collapsible"
        )
    ]

    edit_handler = TabbedInterface([
        ObjectList(common_panels, heading='Common'),
        ObjectList(en_content_panels, heading='English'),
        ObjectList(de_content_panels, heading='German')
    ])

    subpage_types = ['a4_candy_cms_pages.EmptyPage']


class EmptyPage(Page):
    subpage_types = ['a4_candy_cms_pages.SimplePage',
                     'a4_candy_cms_contacts.FormPage',
                     'a4_candy_cms_news.NewsIndexPage',
                     'a4_candy_cms_use_cases.UseCaseIndexPage']


class SimplePage(Page):
    body_streamfield_de = fields.StreamField([
        ('html', blocks.RawHTMLBlock()),
        ('richtext', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('faq', cms_blocks.AccordeonListBlock()),
        ('image_cta', cms_blocks.ImageCTABlock()),
        ('col_list_image_cta_block', cms_blocks.ColumnsImageCTABlock()),
        ('columns_cta', cms_blocks.ColumnsCTABlock()),
        ('downloads', cms_blocks.DownloadListBlock()),
        ('quote', cms_blocks.QuoteBlock())
    ])
    body_streamfield_en = fields.StreamField([
        ('html', blocks.RawHTMLBlock()),
        ('richtext', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('faq', cms_blocks.AccordeonListBlock()),
        ('image_cta', cms_blocks.ImageCTABlock()),
        ('col_list_image_cta_block', cms_blocks.ColumnsImageCTABlock()),
        ('columns_cta', cms_blocks.ColumnsCTABlock()),
        ('downloads', cms_blocks.DownloadListBlock()),
        ('quote', cms_blocks.QuoteBlock())
    ], blank=True)

    body_streamfield_nl = fields.StreamField([
        ('html', blocks.RawHTMLBlock()),
        ('richtext', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('faq', cms_blocks.AccordeonListBlock()),
        ('image_cta', cms_blocks.ImageCTABlock()),
        ('col_list_image_cta_block', cms_blocks.ColumnsImageCTABlock()),
        ('columns_cta', cms_blocks.ColumnsCTABlock()),
        ('downloads', cms_blocks.DownloadListBlock()),
        ('quote', cms_blocks.QuoteBlock())
    ], blank=True)

    body_streamfield_ky = fields.StreamField([
        ('html', blocks.RawHTMLBlock()),
        ('richtext', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('faq', cms_blocks.AccordeonListBlock()),
        ('image_cta', cms_blocks.ImageCTABlock()),
        ('col_list_image_cta_block', cms_blocks.ColumnsImageCTABlock()),
        ('columns_cta', cms_blocks.ColumnsCTABlock()),
        ('downloads', cms_blocks.DownloadListBlock()),
        ('quote', cms_blocks.QuoteBlock())
    ], blank=True)

    body_streamfield_ru = fields.StreamField([
        ('html', blocks.RawHTMLBlock()),
        ('richtext', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('faq', cms_blocks.AccordeonListBlock()),
        ('image_cta', cms_blocks.ImageCTABlock()),
        ('col_list_image_cta_block', cms_blocks.ColumnsImageCTABlock()),
        ('columns_cta', cms_blocks.ColumnsCTABlock()),
        ('downloads', cms_blocks.DownloadListBlock()),
        ('quote', cms_blocks.QuoteBlock())
    ], blank=True)

    body_streamfield = TranslatedFieldLegal(
        'body_streamfield_de',
        'body_streamfield_en',
        'body_streamfield_nl',
        'body_streamfield_ky',
        'body_streamfield_ru'
    )

    en_content_panels = [
        StreamFieldPanel('body_streamfield_en')
    ]

    de_content_panels = [
        StreamFieldPanel('body_streamfield_de')
    ]

    nl_content_panels = [
        StreamFieldPanel('body_streamfield_nl')
    ]

    ky_content_panels = [
        StreamFieldPanel('body_streamfield_ky')
    ]

    ru_content_panels = [
        StreamFieldPanel('body_streamfield_ru')
    ]

    common_panels = [
        FieldPanel('title'),
        FieldPanel('slug')
    ]

    edit_handler = TabbedInterface([
        ObjectList(common_panels, heading='Common'),
        ObjectList(en_content_panels, heading='English'),
        ObjectList(de_content_panels, heading='German'),
        ObjectList(nl_content_panels, heading='Dutch'),
        ObjectList(ky_content_panels, heading='Kyrgyz'),
        ObjectList(ru_content_panels, heading='Russian')
    ])

    subpage_types = ['a4_candy_cms_pages.SimplePage']
