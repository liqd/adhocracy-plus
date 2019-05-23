# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ckeditor.fields


class Migration(migrations.Migration):

    replaces = [('meinberlin_mapideas', '0006_auto_20170529_1302')]

    dependencies = [
        ('a4_candy_mapideas', '0005_update-strings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mapidea',
            name='description',
            field=ckeditor.fields.RichTextField(verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='mapidea',
            name='name',
            field=models.CharField(max_length=120, verbose_name='Name'),
        ),
    ]
