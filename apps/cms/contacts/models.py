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

    def process_form_submission(self, form):
        submission = super().process_form_submission(form)
        if form.cleaned_data['receive_copy']:
            AnswerToContactFormEmail.send(submission)
        if self.to_address:
            self.send_mail(form)
        return submission

    def get_form_fields(self):
        fields = list(super().get_form_fields())
        fields.insert(0, FormField(
            label='receive_copy',
            field_type='checkbox',
            help_text=_('I want to receicve a copy of my message as email'),
            required=False))

        fields.insert(0, FormField(
            label='your_message',
            help_text=_('Your message'),
            field_type='multiline',
            required=True))

        fields.insert(0, FormField(
            label='email',
            help_text=_('Your email address'),
            field_type='email',
            required=True))

        fields.insert(0, FormField(
            label='phone_number',
            help_text=_('Your telephone number'),
            field_type='singleline',
            required=False))

        fields.insert(0, FormField(
            label='name',
            help_text=_('Your first and last name'),
            field_type='singleline',
            required=False))
        return fields

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
