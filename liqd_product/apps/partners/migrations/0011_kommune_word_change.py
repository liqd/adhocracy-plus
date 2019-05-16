# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-16 12:28
from __future__ import unicode_literals

import adhocracy4.images.fields
import ckeditor_uploader.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liqd_product_partners', '0010_update_helptexts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partner',
            name='description',
            field=models.CharField(help_text='max. 400 characters', max_length=400, verbose_name='Short description of your organisation'),
        ),
        migrations.AlterField(
            model_name='partner',
            name='information',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, verbose_name='Information about your organisation'),
        ),
        migrations.AlterField(
            model_name='partner',
            name='logo',
            field=adhocracy4.images.fields.ConfiguredImageField('logo', blank=True, help_prefix='The Logo representing your organisation', upload_to='partners/logos', verbose_name='Logo'),
        ),
    ]
