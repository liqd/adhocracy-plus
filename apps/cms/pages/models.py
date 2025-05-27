import random

from django.db import models
from django.http import HttpResponse
from wagtail import blocks
from wagtail import fields
from wagtail.admin.panels import FieldPanel
from wagtail.admin.panels import MultiFieldPanel
from wagtail.admin.panels import ObjectList
from wagtail.admin.panels import PageChooserPanel
from wagtail.admin.panels import TabbedInterface
from wagtail.admin.panels import TitleFieldPanel
from wagtail.images.blocks import ImageBlock
from wagtail.models import Page

from apps.cms import blocks as cms_blocks
from apps.cms.news.blocks import NewsBlock
from apps.cms.use_cases.blocks import UseCaseBlock
from apps.contrib.translations import TranslatedField
from apps.contrib.translations import TranslatedFieldLegal


class HomePage(Page):
    image_1 = models.ForeignKey(
        "a4_candy_cms_images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Header Image 1",
        help_text="The Image that is shown on top of the page",
    )

    image_2 = models.ForeignKey(
        "a4_candy_cms_images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Header Image 2",
        help_text="The Image that is shown on top of the page",
    )

    image_3 = models.ForeignKey(
        "a4_candy_cms_images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Header Image 3",
        help_text="The Image that is shown on top of the page",
    )

    image_4 = models.ForeignKey(
        "a4_candy_cms_images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Header Image 4",
        help_text="The Image that is shown on top of the page",
    )

    image_5 = models.ForeignKey(
        "a4_candy_cms_images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Header Image 5",
        help_text="The Image that is shown on top of the page",
    )

    form_page = models.ForeignKey(
        "a4_candy_cms_contacts.FormPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    hero_title_de = models.CharField(
        max_length=80, blank=True, verbose_name="Hero title"
    )
    hero_title_en = models.CharField(
        max_length=80, blank=True, verbose_name="Hero title"
    )

    hero_subtitle_de = fields.RichTextField(
        max_length=150, blank=True, features=["h3", "bold", "italic", "link"]
    )
    hero_subtitle_en = fields.RichTextField(
        max_length=150, blank=True, features=["h3", "bold", "italic", "link"]
    )

    body_de = fields.RichTextField(blank=True)
    body_en = fields.RichTextField(blank=True)

    body_streamfield_de = fields.StreamField(
        [
            ("col_list_image_cta_block", cms_blocks.ColumnsImageCTABlock()),
            ("background_cta_block", cms_blocks.ColBackgroundCTABlock()),
            ("columns_cta", cms_blocks.ColumnsCTABlock()),
            ("html", blocks.RawHTMLBlock()),
            ("paragraph", blocks.RichTextBlock()),
            ("news", NewsBlock()),
            ("use_cases", UseCaseBlock()),
        ],
        blank=True,
    )

    body_streamfield_en = fields.StreamField(
        [
            ("col_list_image_cta_block", cms_blocks.ColumnsImageCTABlock()),
            ("background_cta_block", cms_blocks.ColBackgroundCTABlock()),
            ("columns_cta", cms_blocks.ColumnsCTABlock()),
            ("html", blocks.RawHTMLBlock()),
            ("paragraph", blocks.RichTextBlock()),
            ("news", NewsBlock()),
            ("use_cases", UseCaseBlock()),
        ],
        blank=True,
    )

    hero_title = TranslatedField("hero_title_de", "hero_title_en")

    hero_subtitle = TranslatedField("hero_subtitle_de", "hero_subtitle_en")

    body_streamfield = TranslatedField("body_streamfield_de", "body_streamfield_en")

    body = TranslatedField("body_de", "body_en")

    @property
    def form(self):
        return self.form_page.get_form()

    @property
    def random_image(self):
        image_numbers = [i for i in range(1, 6) if getattr(self, "image_{}".format(i))]
        if image_numbers:
            return getattr(self, "image_{}".format(random.choice(image_numbers)))

    en_content_panels = [
        FieldPanel("hero_title_en"),
        FieldPanel("hero_subtitle_en"),
        FieldPanel("body_en"),
        FieldPanel("body_streamfield_en"),
    ]

    de_content_panels = [
        FieldPanel("hero_title_de"),
        FieldPanel("hero_subtitle_de"),
        FieldPanel("body_de"),
        FieldPanel("body_streamfield_de"),
    ]

    common_panels = [
        TitleFieldPanel("title"),
        FieldPanel("slug"),
        PageChooserPanel("form_page", "a4_candy_cms_contacts.FormPage"),
        MultiFieldPanel(
            [
                FieldPanel("image_1"),
                FieldPanel("image_2"),
                FieldPanel("image_3"),
                FieldPanel("image_4"),
                FieldPanel("image_5"),
            ],
            heading="Images",
            classname="collapsible",
        ),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(common_panels, heading="Common"),
            ObjectList(en_content_panels, heading="English"),
            ObjectList(de_content_panels, heading="German"),
        ]
    )

    subpage_types = ["a4_candy_cms_pages.EmptyPage"]


class EmptyPage(Page):
    subpage_types = [
        "a4_candy_cms_pages.SimplePage",
        "a4_candy_cms_contacts.FormPage",
        "a4_candy_cms_news.NewsIndexPage",
        "a4_candy_cms_use_cases.UseCaseIndexPage",
    ]

    def serve_preview(self, request, mode_name):
        return HttpResponse(status=204)


class SimplePage(Page):
    body_streamfield_de = fields.StreamField(
        [
            ("html", blocks.RawHTMLBlock()),
            ("richtext", blocks.RichTextBlock()),
            ("image", ImageBlock()),
            ("faq", cms_blocks.AccordeonListBlock()),
            ("image_cta", cms_blocks.ImageCTABlock()),
            ("col_list_image_cta_block", cms_blocks.ColumnsImageCTABlock()),
            ("columns_cta", cms_blocks.ColumnsCTABlock()),
            ("downloads", cms_blocks.DownloadListBlock()),
            ("quote", cms_blocks.QuoteBlock()),
        ],
    )
    body_streamfield_en = fields.StreamField(
        [
            ("html", blocks.RawHTMLBlock()),
            ("richtext", blocks.RichTextBlock()),
            ("image", ImageBlock()),
            ("faq", cms_blocks.AccordeonListBlock()),
            ("image_cta", cms_blocks.ImageCTABlock()),
            ("col_list_image_cta_block", cms_blocks.ColumnsImageCTABlock()),
            ("columns_cta", cms_blocks.ColumnsCTABlock()),
            ("downloads", cms_blocks.DownloadListBlock()),
            ("quote", cms_blocks.QuoteBlock()),
        ],
        blank=True,
    )

    body_streamfield_nl = fields.StreamField(
        [
            ("html", blocks.RawHTMLBlock()),
            ("richtext", blocks.RichTextBlock()),
            ("image", ImageBlock()),
            ("faq", cms_blocks.AccordeonListBlock()),
            ("image_cta", cms_blocks.ImageCTABlock()),
            ("col_list_image_cta_block", cms_blocks.ColumnsImageCTABlock()),
            ("columns_cta", cms_blocks.ColumnsCTABlock()),
            ("downloads", cms_blocks.DownloadListBlock()),
            ("quote", cms_blocks.QuoteBlock()),
        ],
        blank=True,
    )

    body_streamfield_ky = fields.StreamField(
        [
            ("html", blocks.RawHTMLBlock()),
            ("richtext", blocks.RichTextBlock()),
            ("image", ImageBlock()),
            ("faq", cms_blocks.AccordeonListBlock()),
            ("image_cta", cms_blocks.ImageCTABlock()),
            ("col_list_image_cta_block", cms_blocks.ColumnsImageCTABlock()),
            ("columns_cta", cms_blocks.ColumnsCTABlock()),
            ("downloads", cms_blocks.DownloadListBlock()),
            ("quote", cms_blocks.QuoteBlock()),
        ],
        blank=True,
    )

    body_streamfield_ru = fields.StreamField(
        [
            ("html", blocks.RawHTMLBlock()),
            ("richtext", blocks.RichTextBlock()),
            ("image", ImageBlock()),
            ("faq", cms_blocks.AccordeonListBlock()),
            ("image_cta", cms_blocks.ImageCTABlock()),
            ("col_list_image_cta_block", cms_blocks.ColumnsImageCTABlock()),
            ("columns_cta", cms_blocks.ColumnsCTABlock()),
            ("downloads", cms_blocks.DownloadListBlock()),
            ("quote", cms_blocks.QuoteBlock()),
        ],
        blank=True,
    )

    body_streamfield = TranslatedFieldLegal(
        "body_streamfield_de",
        "body_streamfield_en",
        "body_streamfield_nl",
        "body_streamfield_ky",
        "body_streamfield_ru",
    )

    en_content_panels = [FieldPanel("body_streamfield_en")]

    de_content_panels = [FieldPanel("body_streamfield_de")]

    nl_content_panels = [FieldPanel("body_streamfield_nl")]

    ky_content_panels = [FieldPanel("body_streamfield_ky")]

    ru_content_panels = [FieldPanel("body_streamfield_ru")]

    common_panels = [TitleFieldPanel("title"), FieldPanel("slug")]

    edit_handler = TabbedInterface(
        [
            ObjectList(common_panels, heading="Common"),
            ObjectList(en_content_panels, heading="English"),
            ObjectList(de_content_panels, heading="German"),
            # ObjectList(nl_content_panels, heading="Dutch"),
            # ObjectList(ky_content_panels, heading="Kyrgyz"),
            # ObjectList(ru_content_panels, heading="Russian"),
        ]
    )

    subpage_types = ["a4_candy_cms_pages.SimplePage"]
