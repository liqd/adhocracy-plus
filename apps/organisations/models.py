from autoslug import AutoSlugField
from ckeditor.fields import RichTextField
from django.conf import settings
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from adhocracy4 import transforms
from adhocracy4.ckeditor.fields import RichTextCollapsibleUploadingField
from adhocracy4.images import fields as images_fields
from adhocracy4.projects.models import Project
from apps.projects import query


class Organisation(models.Model):
    slug = AutoSlugField(populate_from='name', unique=True)
    name = models.CharField(max_length=512)
    initiators = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True
    )
    title = models.CharField(
        verbose_name=_('Title of your organisation'),
        max_length=100,
        default='Organisation',
        help_text=_('The title of your organisation will be shown '
                    'on the landing page. max. 100 characters')
    )
    description = models.CharField(
        max_length=800,
        verbose_name=_('Short description of your organisation'),
        help_text=_('The description will be displayed on the '
                    'landing page. max. 800 characters')
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
    slogan = models.CharField(
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
    information = RichTextCollapsibleUploadingField(
        config_name='collapsible-image-editor',
        verbose_name=_('Information about your organisation'),
        help_text=_('You can provide general information about your '
                    'participation platform to your visitors. '
                    'It’s also helpful to name a general person '
                    'of contact for inquiries. The information '
                    'will be shown on a separate page that '
                    'can be reached via the main menu.'),
        blank=True
    )
    imprint = RichTextField(
        verbose_name=_('Imprint'),
        help_text=_('Please provide all the legally '
                    'required information of your imprint. '
                    'The imprint will be shown on a separate page.')
    )
    is_supporting = models.BooleanField(
        default=False,
        verbose_name=_('is a supporting organisation'),
        help_text=_('For supporting organisations, the banner asking '
                    'for donations is not displayed on their pages.')
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
        active_projects = []
        future_projects = []
        past_projects = []

        projects = query.filter_viewable(self.projects, user)

        for project in projects:
            if project.running_modules:
                active_projects.append(project)
            elif project.future_modules:
                future_projects.append(project)
            elif project.past_modules:
                past_projects.append(project)

        sorted_active_projects = sorted(
            active_projects,
            key=lambda p: p.running_module_ends_next.module_end)

        sorted_future_projects = sorted(
            future_projects,
            key=lambda p: p.future_modules.first().module_start)

        sorted_past_projects = sorted(
            past_projects,
            key=lambda p: project.past_modules.first().module_start,
            reverse=True)

        return sorted_active_projects, \
            sorted_future_projects, \
            sorted_past_projects

    def has_initiator(self, user):
        return (self.initiators.filter(id=user.id).exists())

    def get_absolute_url(self):
        return '/{}'.format(self.name).lower()

    def save(self, *args, **kwargs):
        self.information = transforms.clean_html_field(
            self.information, 'collapsible-image-editor')
        self.imprint = transforms.clean_html_field(self.imprint)
        super().save(*args, **kwargs)
