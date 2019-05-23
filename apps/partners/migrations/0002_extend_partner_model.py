# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ckeditor_uploader.fields
import adhocracy4.images.fields


class Migration(migrations.Migration):

    replaces = [('liqd_product_partners', '0002_extend_partner_model')]

    dependencies = [
        ('a4_candy_partners', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='about',
            field=ckeditor_uploader.fields.RichTextUploadingField(verbose_name='Description of your municipality', default='about'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='partner',
            name='description',
            field=models.CharField(verbose_name='Short description of your municipality', max_length=500, default='description'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='partner',
            name='image',
            field=adhocracy4.images.fields.ConfiguredImageField('heroimage', verbose_name='Header image', upload_to='parterns/backgrounds', blank=True, help_prefix='The image will be shown as a decorative background image.'),
        ),
        migrations.AddField(
            model_name='partner',
            name='logo',
            field=adhocracy4.images.fields.ConfiguredImageField('logo', verbose_name='Logo', upload_to='partners/logos', blank=True, help_prefix='The Logo representing your municipality'),
        ),
        migrations.AddField(
            model_name='partner',
            name='slogan',
            field=models.CharField(verbose_name='Slogan', max_length=100, blank=True),
        ),
    ]
