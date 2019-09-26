from django.db import models
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.admin.edit_handlers import PageChooserPanel
from wagtail.contrib.settings.models import BaseSetting
from wagtail.contrib.settings.models import register_setting
from wagtail.core import fields


@register_setting
class ImportantPages(BaseSetting):
    terms_of_use = models.ForeignKey(
        'wagtailcore.Page',
        related_name='important_page_terms_of_use',
        null=True,
        blank=True,
        on_delete=models.SET_NULL)
    imprint = models.ForeignKey(
        'wagtailcore.Page',
        related_name='important_page_imprint',
        null=True,
        blank=True,
        on_delete=models.SET_NULL)
    data_protection_policy = models.ForeignKey(
        'wagtailcore.Page',
        related_name='important_page_data_protection_policy',
        null=True,
        blank=True,
        on_delete=models.SET_NULL)
    contact = models.ForeignKey(
        'wagtailcore.Page',
        related_name='important_page_contact',
        null=True,
        blank=True,
        on_delete=models.SET_NULL)
    donate_link = models.URLField(blank=True)
    manual_link = models.URLField(blank=True)


    panels = [
        PageChooserPanel('terms_of_use'),
        PageChooserPanel('imprint'),
        PageChooserPanel('data_protection_policy'),
        PageChooserPanel('contact'),
        FieldPanel('donate_link'),
        FieldPanel('manual_link')
    ]


@register_setting
class OrganisationSettings(BaseSetting):
    address = fields.RichTextField()
    contacts = fields.RichTextField()

    panels = [
        FieldPanel('address'),
        FieldPanel('contacts')
    ]


@register_setting
class SocialMedia(BaseSetting):
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    github = models.URLField(blank=True)

    panels = [
        FieldPanel('facebook'),
        FieldPanel('twitter'),
        FieldPanel('github')
    ]
