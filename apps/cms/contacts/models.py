from django.contrib import messages
from django.db import models
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.admin.edit_handlers import FieldRowPanel
from wagtail.admin.edit_handlers import MultiFieldPanel
from wagtail.admin.edit_handlers import ObjectList
from wagtail.admin.edit_handlers import TabbedInterface
from wagtail.contrib.forms.models import AbstractEmailForm
from wagtail.contrib.forms.models import AbstractFormField
from wagtail.core.fields import RichTextField

from apps.cms.emails import AnswerToContactFormEmail
from apps.contrib.translations import TranslatedField


class FormField(AbstractFormField):
    page = ParentalKey('FormPage',
                       on_delete=models.CASCADE,
                       related_name='form_fields')


class FormPage(AbstractEmailForm):

    header_de = models.CharField(
        max_length=500, blank=True, verbose_name="Header")
    header_en = models.CharField(
        max_length=500, blank=True, verbose_name="Header")

    intro_en = RichTextField(blank=True)
    intro_de = RichTextField(blank=True)

    thank_you_text_en = models.TextField(blank=True)
    thank_you_text_de = models.TextField(blank=True)

    header = TranslatedField(
        'header_de',
        'header_en'
    )

    intro = TranslatedField(
        'intro_de',
        'intro_en'
    )

    thank_you_text = TranslatedField(
        'thank_you_text_de',
        'thank_you_text_en'
    )



    en_content_panels = [
        FieldPanel('header_en'),
        FieldPanel('intro_en'),
        FieldPanel('thank_you_text_en'),
    ]

    de_content_panels = [
        FieldPanel('header_de'),
        FieldPanel('intro_de'),
        FieldPanel('thank_you_text_de'),
    ]

    common_panels = [
        FieldPanel('title'),
        FieldPanel('slug'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname="col6"),
                FieldPanel('to_address', classname="col6"),
            ]),
            FieldPanel('subject'),
        ], "Email"),

    ]

    edit_handler = TabbedInterface([
        ObjectList(common_panels, heading='Common'),
        ObjectList(en_content_panels, heading='English'),
        ObjectList(de_content_panels, heading='German')
    ])
