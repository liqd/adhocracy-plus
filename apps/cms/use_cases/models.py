from django.db import models
from django.utils.translation import ugettext_lazy as _
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.admin.edit_handlers import ObjectList
from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.admin.edit_handlers import TabbedInterface
from wagtail.core import blocks
from wagtail.core import fields
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel

from apps.contrib.translations import TranslatedField


class UseCaseIndexPage(Page):
    subtitle_de = models.CharField(
        max_length=250, blank=True, verbose_name="Title")
    subtitle_en = models.CharField(
        max_length=250, blank=True, verbose_name="Title")

    subtitle = TranslatedField(
        'subtitle_de',
        'subtitle_en'
    )

    @property
    def use_case(self):
        use_case = UseCasePage.objects.live()
        return use_case

    def get_context(self, request):
        use_case = self.use_case

        context = super(UseCasePage, self).get_context(request)
        context['use_case'] = use_case
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

    subpage_types = ['a4_candy_cms_use_cases.UseCasePage']


class UseCasePage(Page):
    MUNICIPALITIES = 'MP'
    CITIZENASSEMBLIES = 'CA'
    COOPERATIVESNGOS = 'CN'
    COMPANIES = 'CP'
    POLITICIANS = 'PO'

    CATEGORY_CHOICES = [
        ('MP', _('Municipalities')),
        ('CA', _('Citizen Assemblies')),
        ('CN', _('Co-Operatives/NGOs')),
        ('CP', _('Companies')),
        ('PO', _('Politicians')),
    ]

    category = models.CharField(
        max_length=2,
        choices=CATEGORY_CHOICES
    )

    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Use Case Header Image",
        help_text="The Image that is shown on the use case item page " +
                  "and the use case index page"
    )

    demo_link = models.URLField(blank=True, verbose_name='Demo site')

    title_de = models.CharField(
        max_length=250, blank=True, verbose_name="German Title")
    title_en = models.CharField(
        max_length=250, blank=True, verbose_name="English Title")

    teaser_de = models.TextField(
        blank=True, null=True, verbose_name="Teaser Text")
    teaser_en = models.TextField(
        blank=True, null=True, verbose_name="Teaser Text")

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
        FieldPanel('slug')
    ]

    edit_handler = TabbedInterface([
        ObjectList(common_panels, heading='Common'),
        ObjectList(en_content_panels, heading='English'),
        ObjectList(de_content_panels, heading='German')
    ])

    subpage_types = []
