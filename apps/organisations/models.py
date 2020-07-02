from autoslug import AutoSlugField
from ckeditor.fields import RichTextField
from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from jsonfield.fields import JSONField
from parler.fields import TranslatedField
from parler.models import TranslatableManager
from parler.models import TranslatableModel
from parler.models import TranslatedFieldsModel

from adhocracy4 import transforms
from adhocracy4.ckeditor.fields import RichTextCollapsibleUploadingField
from adhocracy4.images import fields as images_fields
from adhocracy4.projects.models import Project
from apps.projects import query


class Organisation(TranslatableModel):
    slug = AutoSlugField(populate_from='name', unique=True)
    name = models.CharField(max_length=512)
    initiators = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True
    )
    title = models.CharField(
        verbose_name=_('Title of your organisation'),
        max_length=100,
        help_text=_('The title of your organisation will be shown '
                    'on the landing page. max. 100 characters'),
        blank=True
    )
    description_untranslated = models.CharField(
        max_length=800,
        verbose_name=_('Short description of your organisation'),
        help_text=_('The description will be displayed on the '
                    'landing page. max. 800 characters'),
        blank=True
    )
    logo = images_fields.ConfiguredImageField(
        'logo',
        verbose_name=_('Logo'),
        help_text=_('The Logo representing your organisation.'
                    ' The image must be square and it '
                    'should be min. 200 pixels wide and 200 '
                    'pixels tall. Allowed file formats are '
                    'png, jpeg, gif. The file size '
                    'should be max. 5 MB.'),
        upload_to='organisations/logos',
        blank=True
    )
    slogan_untranslated = models.CharField(
        max_length=200,
        verbose_name=_('Slogan'),
        blank=True,
        help_text=_('The slogan will be shown below '
                    'the title of your organisation on '
                    'the landing page. The slogan can '
                    'provide context or additional '
                    'information to the title. '
                    'max. 200 characters')
    )
    url = models.URLField(
        blank=True,
        verbose_name='Organisation website',
        help_text=_('Please enter '
                    'a full url which '
                    'starts with https:// '
                    'or http://')
    )
    image = images_fields.ConfiguredImageField(
        'heroimage',
        verbose_name=_('Header image'),
        help_prefix=_(
            'The image will be shown as a decorative background image.'
        ),
        upload_to='organisations/backgrounds',
        blank=True
    )
    image_copyright = models.CharField(
        max_length=200,
        verbose_name=_('Header image copyright'),
        blank=True,
        help_text=_('Author, which is displayed in the header image.')
    )
    information_untranslated = RichTextCollapsibleUploadingField(
        config_name='collapsible-image-editor',
        verbose_name=_('Information about your organisation'),
        help_text=_('You can provide general information about your '
                    'participation platform to your visitors. '
                    'It’s also helpful to name a general person '
                    'of contact for inquiries. The information '
                    'will be shown on a separate "About" page that '
                    'can be reached via the main menu.'),
        blank=True
    )
    twitter_handle = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Twitter handle',
    )
    facebook_handle = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Facebook handle',
    )
    instagram_handle = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Instagram handle',
    )

    description = TranslatedField()
    slogan = TranslatedField()
    information = TranslatedField()

    imprint = RichTextField(
        verbose_name=_('Imprint'),
        help_text=_('Please provide all the legally '
                    'required information of your imprint. '
                    'The imprint will be shown on a separate page.'),
        blank=True
    )
    terms_of_use = RichTextField(
        verbose_name=_('Terms of use'),
        help_text=_('Please provide all the legally '
                    'required information of your terms of use. '
                    'The terms of use will be shown on a separate page.'),
        blank=True
    )
    data_protection = RichTextField(
        verbose_name=_('Data protection policy'),
        help_text=_('Please provide all the legally '
                    'required information of your data protection. '
                    'The data protection policy will be shown on a '
                    'separate page.'),
        blank=True
    )
    netiquette = RichTextField(
        verbose_name=_('Netiquette'),
        help_text=_('Please provide a netiquette for the participants. '
                    'The netiquette helps improving the climate of '
                    'online discussions and supports the moderation.'),
        blank=True
    )
    is_supporting = models.BooleanField(
        default=False,
        verbose_name=_('is a supporting organisation'),
        help_text=_('For supporting organisations, the banner asking '
                    'for donations is not displayed on their pages.')
    )
    site = models.ForeignKey(
        Site,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name

    @cached_property
    def projects(self):
        return Project.objects \
            .filter(organisation=self,
                    is_archived=False,
                    is_draft=False)

    def get_projects_list(self, user):
        projects = query.filter_viewable(self.projects, user)
        now = timezone.now()

        sorted_active_projects = projects\
            .annotate(project_start=models.Min('module__phase__start_date'))\
            .annotate(project_end=models.Max('module__phase__end_date'))\
            .filter(project_start__lte=now, project_end__gt=now)\
            .order_by('project_end')

        sorted_future_projects = projects\
            .annotate(project_start=models.Min('module__phase__start_date'))\
            .filter(models.Q(project_start__gt=now)
                    | models.Q(project_start=None))\
            .order_by('project_start')

        sorted_past_projects = projects\
            .annotate(project_start=models.Min('module__phase__start_date'))\
            .annotate(project_end=models.Max('module__phase__end_date'))\
            .filter(project_end__lt=now)\
            .order_by('project_start')

        return sorted_active_projects, \
            sorted_future_projects, \
            sorted_past_projects

    def has_initiator(self, user):
        return (self.initiators.filter(id=user.id).exists())

    def has_org_member(self, user):
        return (Member.objects.filter(
            member__id=user.id,
            organisation__id=self.id).exists())

    def get_absolute_url(self):
        return reverse('organisation', kwargs={
            'organisation_slug': self.slug
        })

    def has_social_share(self):
        return (
            self.twitter_handle or self.facebook_handle
            or self.instagram_handle
        )

    def save(self, *args, **kwargs):
        self.information = transforms.clean_html_field(
            self.information, 'collapsible-image-editor')
        self.imprint = transforms.clean_html_field(self.imprint)
        super().save(*args, **kwargs)


class OrganisationTranslation(TranslatedFieldsModel):
    master = models.ForeignKey(
        Organisation,
        related_name='translations',
        null=True,
        on_delete=models.CASCADE
    )
    description=models.CharField(
        max_length=800,
        verbose_name=_('Short description of your organisation'),
        help_text=_('The description will be displayed on the '
                    'landing page. max. 800 characters'),
        blank=True
    )
    slogan=models.CharField(
        max_length=200,
        verbose_name=_('Slogan'),
        blank=True,
        help_text=_('The slogan will be shown below '
                    'the title of your organisation on '
                    'the landing page. The slogan can '
                    'provide context or additional '
                    'information to the title. '
                    'max. 200 characters')
    )
    information=RichTextCollapsibleUploadingField(
        config_name='collapsible-image-editor',
        verbose_name=_('Information about your organisation'),
        help_text=_('You can provide general information about your '
                    'participation platform to your visitors. '
                    'It’s also helpful to name a general person '
                    'of contact for inquiries. The information '
                    'will be shown on a separate "About" page that '
                    'can be reached via the main menu.'),
        blank=True
    )

    class Meta:
        unique_together = ('language_code', 'master')
        verbose_name = _("Organisation translation")


class Member(models.Model):
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    organisation = models.ForeignKey(
        settings.A4_ORGANISATIONS_MODEL,
        on_delete=models.CASCADE
    )
    member_number = models.CharField(
        max_length=50,
        blank=True,
    )
    additional_info = JSONField(blank=True)

    class Meta:
        unique_together = [('member', 'organisation')]

    def __str__(self):
        return '{}_{}'.format(self.organisation, self.member)
