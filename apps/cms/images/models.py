from django.db import models
from wagtail.images.models import AbstractImage
from wagtail.images.models import AbstractRendition
from wagtail.images.models import Image

from apps.contrib.translations import TranslatedField


class CustomImage(AbstractImage):

    caption_en = models.CharField(max_length=255, blank=True)
    caption_de = models.CharField(max_length=255, blank=True)

    admin_form_fields = Image.admin_form_fields + (
        'caption_en', 'caption_de'
    )

    caption = TranslatedField('caption_de', 'caption_en')


class CustomRendition(AbstractRendition):
    image = models.ForeignKey(CustomImage,
                              related_name='renditions',
                              on_delete=models.CASCADE)

    class Meta:
        unique_together = (
            ('image', 'filter_spec', 'focal_point_key'),
        )
