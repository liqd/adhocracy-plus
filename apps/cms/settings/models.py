from django.db import models
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.admin.edit_handlers import PageChooserPanel
from wagtail.contrib.settings.models import BaseSetting
from wagtail.contrib.settings.models import register_setting
from wagtail.core import fields
from wagtail.images.edit_handlers import ImageChooserPanel

from apps.contrib.translations import TranslatedField


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
    netiquette = models.ForeignKey(
        'wagtailcore.Page',
        related_name='important_page_netiquette',
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
    github_repo_link = models.URLField(blank=True)
    open_content_link = models.URLField(blank=True)


    panels = [
        PageChooserPanel('terms_of_use',
                         ['a4_candy_cms_pages.SimplePage',
                          'a4_candy_cms_contacts.FormPage',
                          'a4_candy_cms_news.NewsIndexPage',
                          'a4_candy_cms_news.NewsPage',
                          'a4_candy_cms_use_cases.UseCaseIndexPage',
                          'a4_candy_cms_use_cases.UseCasePage']),
        PageChooserPanel('imprint',
                         ['a4_candy_cms_pages.SimplePage',
                          'a4_candy_cms_contacts.FormPage',
                          'a4_candy_cms_news.NewsIndexPage',
                          'a4_candy_cms_news.NewsPage',
                          'a4_candy_cms_use_cases.UseCaseIndexPage',
                          'a4_candy_cms_use_cases.UseCasePage']),
        PageChooserPanel('data_protection_policy',
                         ['a4_candy_cms_pages.SimplePage',
                          'a4_candy_cms_contacts.FormPage',
                          'a4_candy_cms_news.NewsIndexPage',
                          'a4_candy_cms_news.NewsPage',
                          'a4_candy_cms_use_cases.UseCaseIndexPage',
                          'a4_candy_cms_use_cases.UseCasePage']),
        PageChooserPanel('netiquette',
                         ['a4_candy_cms_pages.SimplePage',
                          'a4_candy_cms_contacts.FormPage',
                          'a4_candy_cms_news.NewsIndexPage',
                          'a4_candy_cms_news.NewsPage',
                          'a4_candy_cms_use_cases.UseCaseIndexPage',
                          'a4_candy_cms_use_cases.UseCasePage']),
        PageChooserPanel('contact',
                         ['a4_candy_cms_pages.SimplePage',
                          'a4_candy_cms_contacts.FormPage',
                          'a4_candy_cms_news.NewsIndexPage',
                          'a4_candy_cms_news.NewsPage',
                          'a4_candy_cms_use_cases.UseCaseIndexPage',
                          'a4_candy_cms_use_cases.UseCasePage']),
        FieldPanel('donate_link'),
        FieldPanel('manual_link'),
        FieldPanel('github_repo_link'),
        FieldPanel('open_content_link')
    ]


# these are settings for platform organisation
@register_setting
class OrganisationSettings(BaseSetting):
    platform_name = models.CharField(
        max_length=20,
        default="adhocracy+",
        verbose_name="Platform name",
    )
    address = fields.RichTextField()
    contacts = fields.RichTextField()

    panels = [
        FieldPanel('platform_name'),
        FieldPanel('address'),
        FieldPanel('contacts')
    ]


@register_setting
class SocialMedia(BaseSetting):
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    github = models.URLField(blank=True)
    fallback_image = models.ForeignKey(
        'a4_candy_cms_images.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Fallback Image",
        help_text="Fallback Image for social meta tags if no other image is there"
    )
    fallback_description_de = models.TextField(
        default='Mit adhocracy+ wird digitale Demokratie einfach – für alle und überall.')
    fallback_description_en = models.TextField(
        default='adhocracy+ makes digital democracy easy - for everyone no matter where.')

    fallback_description = TranslatedField(
        'fallback_description_de',
        'fallback_description_en'
    )

    panels = [
        FieldPanel('facebook'),
        FieldPanel('twitter'),
        FieldPanel('github'),
        ImageChooserPanel('fallback_image'),
        FieldPanel('fallback_description_de'),
        FieldPanel('fallback_description_en')
    ]
