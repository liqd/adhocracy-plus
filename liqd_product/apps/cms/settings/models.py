from django.db import models
from wagtail.contrib.settings.models import BaseSetting
from wagtail.contrib.settings.models import register_setting
from wagtail.wagtailadmin.edit_handlers import PageChooserPanel


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

    panels = [
        PageChooserPanel('terms_of_use'),
        PageChooserPanel('imprint'),
        PageChooserPanel('data_protection_policy')
    ]
