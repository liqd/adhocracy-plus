from django.core.paginator import InvalidPage
from django.core.paginator import Paginator
from django.db import models
from django.http import Http404
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.admin.edit_handlers import ObjectList
from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.admin.edit_handlers import TabbedInterface
from wagtail.core import blocks
from wagtail.core import fields
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel

from apps.contrib.translations import TranslatedField


class NewsIndexPage(Page):
    subtitle_de = models.CharField(
        max_length=250, blank=True, verbose_name="Title")
    subtitle_en = models.CharField(
        max_length=250, blank=True, verbose_name="Title")

    subtitle = TranslatedField(
        'subtitle_de',
        'subtitle_en'
    )

    @property
    def news(self):
        news = self.get_children().specific().live()
        news = news.order_by('-first_published_at')
        return news

    def get_context(self, request):
        news = self.news
        page = request.GET.get('page', 1)
        paginator = Paginator(news, 20)

        try:
            news = paginator.page(page)
        except InvalidPage:
            raise Http404

        context = super(NewsIndexPage, self).get_context(request)
        context['news'] = news
        return context

    de_content_panels = [
        FieldPanel('subtitle_de'),
    ]

    en_content_panels = [
        FieldPanel('subtitle_en'),
    ]

    common_panels = [
        FieldPanel('title'),
        FieldPanel('slug')
    ]

    edit_handler = TabbedInterface([
        ObjectList(common_panels, heading='Common'),
        ObjectList(en_content_panels, heading='English'),
        ObjectList(de_content_panels, heading='German')
    ])

    subpage_types = ['a4_candy_cms_news.NewsPage']


class NewsPage(Page):
    image = models.ForeignKey(
        'a4_candy_cms_images.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="News Header Image",
        help_text="The Image that is shown on the news item page " +
                  "and the news index page"
    )

    title_de = models.CharField(
        max_length=250, blank=True, verbose_name="Title")
    title_en = models.CharField(
        max_length=250, blank=True, verbose_name="Title")

    teaser_de = models.TextField(
        max_length=400, blank=True, null=True, verbose_name="Teaser Text")
    teaser_en = models.TextField(
        max_length=400, blank=True, null=True, verbose_name="Teaser Text")

    author = models.CharField(
        max_length=255, blank=True, verbose_name="Author Name")
    create_date = models.DateTimeField(auto_now_add=True, blank=True)
    update_date = models.DateTimeField(auto_now=True, blank=True)

    body_streamfield_de = fields.StreamField([
        ('paragraph', blocks.RichTextBlock()),
        ('html', blocks.RawHTMLBlock())
    ], blank=True)

    body_streamfield_en = fields.StreamField([
        ('paragraph', blocks.RichTextBlock()),
        ('html', blocks.RawHTMLBlock())
    ], blank=True)

    subtitle = TranslatedField(
        'title_de',
        'title_en'
    )

    teaser = TranslatedField(
        'teaser_de',
        'teaser_en'
    )

    body = TranslatedField(
        'body_streamfield_de',
        'body_streamfield_en'
    )

    en_content_panels = [
        FieldPanel('title_en'),
        FieldPanel('teaser_en'),
        StreamFieldPanel('body_streamfield_en')
    ]

    de_content_panels = [
        FieldPanel('title_de'),
        FieldPanel('teaser_de'),
        StreamFieldPanel('body_streamfield_de')
    ]

    common_panels = [
        FieldPanel('title'),
        ImageChooserPanel('image'),
        FieldPanel('author'),
        FieldPanel('slug')
    ]

    edit_handler = TabbedInterface([
        ObjectList(common_panels, heading='Common'),
        ObjectList(en_content_panels, heading='English'),
        ObjectList(de_content_panels, heading='German')
    ])

    subpage_types = []
