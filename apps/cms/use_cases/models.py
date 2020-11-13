from django.db import models
from django.utils.translation import ugettext_lazy as _
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.admin.edit_handlers import ObjectList
from wagtail.admin.edit_handlers import PageChooserPanel
from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.admin.edit_handlers import TabbedInterface
from wagtail.core import blocks
from wagtail.core import fields
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel

from apps.contrib.translations import TranslatedField

from .blocks import ExampleBlock

MUNICIPALITIES = 'MP'
CITIZENASSEMBLIES = 'CA'
NGOS = 'NG'
COMPANIES = 'CP'
POLITICIANS = 'PO'

CATEGORY_CHOICES = [
    (MUNICIPALITIES, _('Municipalities')),
    (CITIZENASSEMBLIES, _('Citizen Assemblies')),
    (NGOS, _('Associations & NGOs')),
    (COMPANIES, _('Companies & Co-Operatives')),
    (POLITICIANS, _('Politicians')),
]


class UseCaseIndexPage(Page):
    subtitle_de = models.CharField(
        max_length=250, blank=True, verbose_name="Title")
    subtitle_en = models.CharField(
        max_length=250, blank=True, verbose_name="Title")

    demo_link = models.URLField(blank=True, verbose_name='Demo site')

    subtitle = TranslatedField(
        'subtitle_de',
        'subtitle_en'
    )

    form_page = models.ForeignKey(
        'a4_candy_cms_contacts.FormPage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    @property
    def form(self):
        return self.form_page.get_form()

    @property
    def use_cases(self):
        use_cases = UseCasePage.objects.live()
        return use_cases

    def get_context(self, request):
        use_cases = self.use_cases

        category = request.GET.get('category')

        if category:
            try:
                use_cases = use_cases.filter(category=category)
            except ValueError:
                use_cases = []

        context = super().get_context(request)
        context['use_cases'] = use_cases
        context['categories'] = CATEGORY_CHOICES
        if category:
            context['current_category'] = category
            for category_choice in CATEGORY_CHOICES:
                if category_choice[0] == category:
                    context['get_current_category_display'] = (
                        category_choice[1]
                    )
        return context

    de_content_panels = [
        FieldPanel('subtitle_de'),
    ]

    en_content_panels = [
        FieldPanel('subtitle_en'),
    ]

    common_panels = [
        FieldPanel('title'),
        FieldPanel('slug'),
        FieldPanel('demo_link'),
        PageChooserPanel('form_page', 'a4_candy_cms_contacts.FormPage'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(common_panels, heading='Common'),
        ObjectList(en_content_panels, heading='English'),
        ObjectList(de_content_panels, heading='German')
    ])

    subpage_types = ['a4_candy_cms_use_cases.UseCasePage']


class UseCasePage(Page):

    category = models.CharField(
        max_length=2,
        choices=CATEGORY_CHOICES
    )

    image = models.ForeignKey(
        'a4_candy_cms_images.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Use Case Header Image",
        help_text="The Image that is shown on the use case item page " +
                  "and the use case index page"
    )

    title_de = models.CharField(
        max_length=250, blank=True, verbose_name="German Title")
    title_en = models.CharField(
        max_length=250, blank=True, verbose_name="English Title")

    body_streamfield_de = fields.StreamField([
        ('paragraph', blocks.RichTextBlock()),
        ('html', blocks.RawHTMLBlock()),
        ('examples', ExampleBlock())
    ], blank=True)

    body_streamfield_en = fields.StreamField([
        ('paragraph', blocks.RichTextBlock()),
        ('html', blocks.RawHTMLBlock()),
        ('examples', ExampleBlock())
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

    def get_context(self, request):
        category = self.category

        if category:
            try:
                use_cases = UseCasePage.objects\
                    .filter(category=category)\
                    .exclude(id=self.id)
            except ValueError:
                use_cases = []

        context = super().get_context(request)
        context['other_use_cases'] = use_cases
        return context

    en_content_panels = [
        FieldPanel('title_en'),
        StreamFieldPanel('body_streamfield_en')
    ]

    de_content_panels = [
        FieldPanel('title_de'),
        StreamFieldPanel('body_streamfield_de')
    ]

    common_panels = [
        FieldPanel('title'),
        ImageChooserPanel('image'),
        FieldPanel('slug'),
        FieldPanel('category')
    ]

    edit_handler = TabbedInterface([
        ObjectList(common_panels, heading='Common'),
        ObjectList(en_content_panels, heading='English'),
        ObjectList(de_content_panels, heading='German')
    ])

    subpage_types = []
