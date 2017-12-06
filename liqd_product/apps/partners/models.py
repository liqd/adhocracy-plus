from autoslug import AutoSlugField
from ckeditor_uploader.fields import RichTextUploadingField
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from adhocracy4 import transforms
from adhocracy4.images import fields as images_fields


class Partner(models.Model):
    slug = AutoSlugField(populate_from='name', unique=True)
    name = models.CharField(max_length=512)
    description = models.CharField(
        max_length=500,
        verbose_name=_('Short description of your municipality'),
    )
    logo = images_fields.ConfiguredImageField(
        'logo',
        verbose_name=_('Logo'),
        help_prefix=_('The Logo representing your municipality'),
        upload_to='partners/logos',
        blank=True
    )
    slogan = models.CharField(
        max_length=100,
        verbose_name=_('Slogan'),
        blank=True
    )
    image = images_fields.ConfiguredImageField(
        'heroimage',
        verbose_name=_('Header image'),
        help_prefix=_(
            'The image will be shown as a decorative background image.'
        ),
        upload_to='parterns/backgrounds',
        blank=True
    )
    about = RichTextUploadingField(
        config_name='image-editor',
        verbose_name=_('Description of your municipality'),
    )
    admins = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
    )

    def has_admin(self, user):
        return self.admins.filter(id=user.id).exists()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.about = transforms.clean_html_field(self.about, 'image-editor')
        super().save(*args, **kwargs)
